from typing import List

from .manager import ExpenseManager
from .models import Expense

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def format_table(expenses: List[Expense]) -> str:
    if not expenses:
        return "No expenses found."
    lines = [f"{'ID':>4}  {'Date':<10}  {'Category':<14}  {'Amount':>10}  Description",
             "-" * 60]
    for e in expenses:
        lines.append(f"{e.id:>4}  {e.date:<10}  {e.category:<14}  "
                     f"{e.amount:>10.2f}  {e.description}")
    lines.append("-" * 60)
    lines.append(f"{'Total':>31}  {sum(e.amount for e in expenses):>10.2f}")
    return "\n".join(lines)


def _bar(value: float, maximum: float, width: int = 25) -> str:
    return "█" * int(width * value / maximum) if maximum else ""


def monthly_report(mgr: ExpenseManager, year: int, month: int) -> str:
    expenses = mgr.expenses_for_month(year, month)
    title = f"Report for {MONTHS[month - 1]} {year}"
    if not expenses:
        return f"{title}\nNo expenses recorded."
    totals = mgr.category_totals(expenses)
    total = sum(totals.values())
    top = max(expenses, key=lambda e: e.amount)
    lines = [title, "=" * len(title),
             f"Total spent   : {total:.2f}",
             f"Transactions  : {len(expenses)}",
             f"Average       : {total / len(expenses):.2f}",
             f"Largest       : {top.amount:.2f} ({top.category}"
             f"{': ' + top.description if top.description else ''})",
             "", "By category:"]
    biggest = max(totals.values())
    for cat, amt in totals.items():
        lines.append(f"  {cat:<14} {amt:>10.2f}  {amt / total * 100:5.1f}%  "
                     f"{_bar(amt, biggest)}")
    return "\n".join(lines)


def yearly_report(mgr: ExpenseManager, year: int) -> str:
    monthly = [mgr.monthly_total(year, m) for m in range(1, 13)]
    title = f"Yearly report {year}"
    lines = [title, "=" * len(title)]
    biggest = max(monthly) if any(monthly) else 0
    for name, amt in zip(MONTHS, monthly):
        lines.append(f"  {name}  {amt:>10.2f}  {_bar(amt, biggest)}")
    lines.append(f"\nYear total: {sum(monthly):.2f}")
    return "\n".join(lines)
