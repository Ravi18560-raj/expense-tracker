import pytest

from expense_tracker.exceptions import ExpenseNotFoundError, ValidationError
from expense_tracker.manager import ExpenseManager
from expense_tracker.storage import JSONStorage, SQLiteStorage


@pytest.fixture(params=["json", "sqlite"])
def mgr(request, tmp_path):
    if request.param == "json":
        return ExpenseManager(JSONStorage(str(tmp_path / "e.json")))
    return ExpenseManager(SQLiteStorage(str(tmp_path / "e.db")))


def test_add_edit_delete(mgr):
    e = mgr.add_expense(10, "food", "lunch", "2026-09-05")
    assert e.id == 1 and e.category == "Food"
    mgr.edit_expense(1, amount=12.5)
    assert mgr.storage.get(1).amount == 12.5
    mgr.delete_expense(1)
    with pytest.raises(ExpenseNotFoundError):
        mgr.storage.get(1)


def test_validation(mgr):
    with pytest.raises(ValidationError):
        mgr.add_expense(-5, "food")
    with pytest.raises(ValidationError):
        mgr.add_expense(5, "food", date="05/09/2026")


def test_search_and_monthly(mgr):
    mgr.add_expense(100, "Food", "pizza night", "2026-09-05")
    mgr.add_expense(50, "Transport", "metro", "2026-09-10")
    mgr.add_expense(30, "Food", "coffee", "2026-10-01")
    assert mgr.monthly_total(2026, 9) == 150
    assert len(mgr.search("pizza")) == 1
    assert len(mgr.search(category="food")) == 2
    assert len(mgr.search(min_amount=40)) == 2
    assert mgr.category_totals(mgr.expenses_for_month(2026, 9))["Food"] == 100
