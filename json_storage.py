import json
import os
import tempfile
from pathlib import Path
from typing import List

from ..exceptions import ExpenseNotFoundError, StorageError
from ..models import Expense
from .base import Storage


class JSONStorage(Storage):
    def __init__(self, path: str = "data/expenses.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    # ---- file helpers ----
    def _load(self) -> dict:
        if not self.path.exists():
            return {"next_id": 1, "expenses": []}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise StorageError(f"{self.path} is corrupted: {e}")
        except OSError as e:
            raise StorageError(f"Cannot read {self.path}: {e}")

    def _save(self, data: dict) -> None:
        # Write to a temp file then rename, so a crash never leaves half a file.
        try:
            fd, tmp = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp, self.path)
        except OSError as e:
            raise StorageError(f"Cannot write {self.path}: {e}")

    # ---- Storage API ----
    def add(self, expense: Expense) -> Expense:
        data = self._load()
        expense.id = data["next_id"]
        data["next_id"] += 1
        data["expenses"].append(expense.to_dict())
        self._save(data)
        return expense

    def get(self, expense_id: int) -> Expense:
        for item in self._load()["expenses"]:
            if item["id"] == expense_id:
                return Expense.from_dict(item)
        raise ExpenseNotFoundError(f"Expense #{expense_id} not found.")

    def update(self, expense: Expense) -> Expense:
        data = self._load()
        for i, item in enumerate(data["expenses"]):
            if item["id"] == expense.id:
                data["expenses"][i] = expense.to_dict()
                self._save(data)
                return expense
        raise ExpenseNotFoundError(f"Expense #{expense.id} not found.")

    def delete(self, expense_id: int) -> None:
        data = self._load()
        remaining = [e for e in data["expenses"] if e["id"] != expense_id]
        if len(remaining) == len(data["expenses"]):
            raise ExpenseNotFoundError(f"Expense #{expense_id} not found.")
        data["expenses"] = remaining
        self._save(data)

    def list_all(self) -> List[Expense]:
        return [Expense.from_dict(e) for e in self._load()["expenses"]]
