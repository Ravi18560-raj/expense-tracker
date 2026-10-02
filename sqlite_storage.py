import sqlite3
from pathlib import Path
from typing import List

from ..exceptions import ExpenseNotFoundError, StorageError
from ..models import Expense
from .base import Storage

SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    amount      REAL NOT NULL CHECK (amount > 0),
    category    TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    date        TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category);
"""


class SQLiteStorage(Storage):
    def __init__(self, path: str = "data/expenses.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self._connect() as conn:
                conn.executescript(SCHEMA)
        except sqlite3.Error as e:
            raise StorageError(f"Cannot open database {self.path}: {e}")

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _row_to_expense(row: sqlite3.Row) -> Expense:
        return Expense(id=row["id"], amount=row["amount"], category=row["category"],
                       description=row["description"], date=row["date"])

    def _run(self, sql: str, params=()):
        try:
            conn = self._connect()
            try:
                with conn:  # commits or rolls back
                    return conn.execute(sql, params)
            finally:
                conn.close()
        except sqlite3.Error as e:
            raise StorageError(f"Database error: {e}")

    def add(self, expense: Expense) -> Expense:
        cur = self._run(
            "INSERT INTO expenses (amount, category, description, date) VALUES (?,?,?,?)",
            (expense.amount, expense.category, expense.description, expense.date))
        expense.id = cur.lastrowid
        return expense

    def get(self, expense_id: int) -> Expense:
        try:
            conn = self._connect()
            try:
                row = conn.execute("SELECT * FROM expenses WHERE id = ?",
                                   (expense_id,)).fetchone()
            finally:
                conn.close()
        except sqlite3.Error as e:
            raise StorageError(f"Database error: {e}")
        if row is None:
            raise ExpenseNotFoundError(f"Expense #{expense_id} not found.")
        return self._row_to_expense(row)

    def update(self, expense: Expense) -> Expense:
        cur = self._run(
            "UPDATE expenses SET amount=?, category=?, description=?, date=? WHERE id=?",
            (expense.amount, expense.category, expense.description,
             expense.date, expense.id))
        if cur.rowcount == 0:
            raise ExpenseNotFoundError(f"Expense #{expense.id} not found.")
        return expense

    def delete(self, expense_id: int) -> None:
        cur = self._run("DELETE FROM expenses WHERE id = ?", (expense_id,))
        if cur.rowcount == 0:
            raise ExpenseNotFoundError(f"Expense #{expense_id} not found.")

    def list_all(self) -> List[Expense]:
        try:
            conn = self._connect()
            try:
                rows = conn.execute("SELECT * FROM expenses ORDER BY date, id").fetchall()
            finally:
                conn.close()
        except sqlite3.Error as e:
            raise StorageError(f"Database error: {e}")
        return [self._row_to_expense(r) for r in rows]
