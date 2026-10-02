from dataclasses import dataclass, asdict
from datetime import date, datetime
from typing import Optional

from .exceptions import ValidationError

DEFAULT_CATEGORIES = ["Food", "Transport", "Rent", "Utilities",
                      "Entertainment", "Health", "Shopping", "Other"]


def parse_date(value: Optional[str]) -> str:
    """Return an ISO date string (YYYY-MM-DD). None/'' means today."""
    if not value:
        return date.today().isoformat()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date().isoformat()
    except ValueError:
        raise ValidationError(f"Invalid date '{value}'. Use YYYY-MM-DD.")


def parse_amount(value) -> float:
    try:
        amount = round(float(value), 2)
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid amount '{value}'.")
    if amount <= 0:
        raise ValidationError("Amount must be greater than 0.")
    return amount


def clean_category(value: Optional[str]) -> str:
    value = (value or "Other").strip()
    if not value:
        raise ValidationError("Category cannot be empty.")
    return value.title()


@dataclass
class Expense:
    amount: float
    category: str
    description: str = ""
    date: str = ""
    id: Optional[int] = None

    def __post_init__(self):
        self.amount = parse_amount(self.amount)
        self.category = clean_category(self.category)
        self.date = parse_date(self.date)
        self.description = (self.description or "").strip()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Expense":
        return cls(
            id=data.get("id"),
            amount=data["amount"],
            category=data["category"],
            description=data.get("description", ""),
            date=data.get("date", ""),
        )
