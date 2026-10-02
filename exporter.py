import csv
from typing import List

from .exceptions import StorageError
from .models import Expense

FIELDS = ["id", "date", "category", "amount", "description"]


def export_csv(expenses: List[Expense], path: str) -> int:
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            for e in expenses:
                writer.writerow({k: getattr(e, k) for k in FIELDS})
    except OSError as e:
        raise StorageError(f"Cannot write {path}: {e}")
    return len(expenses)
