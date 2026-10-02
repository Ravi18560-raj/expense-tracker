"""Business logic. Talks only to the Storage interface."""
from typing import Dict, List, Optional

from .exceptions import ValidationError
from .models import Expense, clean_category, parse_amount, parse_date
from .storage import Storage


class ExpenseManager:
    def __init__(self, storage: Storage):
        self.storage = storage

    def add_expense(self, amount, category, description="", date=None) -> Expense:
        return self.storage.add(Expense(amount, category, description, date or ""))

    def edit_expense(self, expense_id: int, amount=None, category=None,
                     description=None, date=None) -> Expense:
        exp = self.storage.get(expense_id)
        if amount is not None:
            exp.amount = parse_amount(amount)
        if category is not None:
            exp.category = clean_category(category)
        if description is not None:
            exp.description = description.strip()
        if date is not None:
            exp.date = parse_date(date)
        return self.storage.update(exp)

    def delete_expense(self, expense_id: int) -> None:
        self.storage.delete(expense_id)

    def list_expenses(self, category: Optional[str] = None) -> List[Expense]:
        items = self.storage.list_all()
        if category:
            items = [e for e in items if e.category.lower() == category.lower()]
        return sorted(items, key=lambda e: (e.date, e.id or 0))

    def search(self, keyword: str = None, category: str = None,
               date_from: str = None, date_to: str = None,
               min_amount: float = None, max_amount: float = None) -> List[Expense]:
        results = self.list_expenses(category)
        if keyword:
            k = keyword.lower()
            results = [e for e in results
                       if k in e.description.lower() or k in e.category.lower()]
        if date_from:
            d = parse_date(date_from)
            results = [e for e in results if e.date >= d]
        if date_to:
            d = parse_date(date_to)
            results = [e for e in results if e.date <= d]
        if min_amount is not None:
            results = [e for e in results if e.amount >= min_amount]
        if max_amount is not None:
            results = [e for e in results if e.amount <= max_amount]
        return results

    @staticmethod
    def _check_month(year: int, month: int) -> None:
        if not 1 <= month <= 12:
            raise ValidationError("Month must be between 1 and 12.")

    def expenses_for_month(self, year: int, month: int) -> List[Expense]:
        self._check_month(year, month)
        prefix = f"{year:04d}-{month:02d}"
        return [e for e in self.list_expenses() if e.date.startswith(prefix)]

    def monthly_total(self, year: int, month: int) -> float:
        return round(sum(e.amount for e in self.expenses_for_month(year, month)), 2)

    def category_totals(self, expenses: List[Expense]) -> Dict[str, float]:
        totals: Dict[str, float] = {}
        for e in expenses:
            totals[e.category] = round(totals.get(e.category, 0) + e.amount, 2)
        return dict(sorted(totals.items(), key=lambda kv: kv[1], reverse=True))
