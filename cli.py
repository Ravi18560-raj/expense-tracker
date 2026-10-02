import argparse
import sys
from datetime import date

from .exceptions import ExpenseError
from .exporter import export_csv
from .manager import ExpenseManager
from .models import DEFAULT_CATEGORIES
from .reports import format_table, monthly_report, yearly_report
from .storage import get_storage


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="expense", description="Personal Expense Tracker")
    p.add_argument("--backend", choices=["json", "sqlite"], default="sqlite",
                   help="storage backend (default: sqlite)")
    p.add_argument("--db", help="path to data file (default: data/expenses.<ext>)")
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("add", help="add an expense")
    a.add_argument("amount", type=float)
    a.add_argument("category", help=f"e.g. {', '.join(DEFAULT_CATEGORIES[:4])}...")
    a.add_argument("-d", "--description", default="")
    a.add_argument("--date", help="YYYY-MM-DD (default: today)")

    e = sub.add_parser("edit", help="edit an expense")
    e.add_argument("id", type=int)
    e.add_argument("--amount", type=float)
    e.add_argument("--category")
    e.add_argument("-d", "--description")
    e.add_argument("--date")

    d = sub.add_parser("delete", help="delete an expense")
    d.add_argument("id", type=int)

    l = sub.add_parser("list", help="list expenses")
    l.add_argument("--category")

    s = sub.add_parser("search", help="search expenses")
    s.add_argument("keyword", nargs="?")
    s.add_argument("--category")
    s.add_argument("--from", dest="date_from")
    s.add_argument("--to", dest="date_to")
    s.add_argument("--min", type=float, dest="min_amount")
    s.add_argument("--max", type=float, dest="max_amount")

    today = date.today()
    m = sub.add_parser("month", help="total for a month")
    m.add_argument("--year", type=int, default=today.year)
    m.add_argument("--month", type=int, default=today.month)

    r = sub.add_parser("report", help="detailed report")
    r.add_argument("--year", type=int, default=today.year)
    r.add_argument("--month", type=int, help="omit for a yearly report")

    x = sub.add_parser("export", help="export to CSV")
    x.add_argument("path", nargs="?", default="expenses.csv")
    x.add_argument("--category")

    mg = sub.add_parser("migrate", help="copy JSON data into SQLite")
    mg.add_argument("--json-path", default="data/expenses.json")
    mg.add_argument("--sqlite-path", default="data/expenses.db")
    return p


def run(args) -> None:
    if args.command == "migrate":
        src = get_storage("json", args.json_path).list_all()
        dst = get_storage("sqlite", args.sqlite_path)
        if dst.list_all():
            raise ExpenseError("Target SQLite database is not empty; aborting.")
        for exp in src:
            exp.id = None
            dst.add(exp)
        print(f"Migrated {len(src)} expenses to {args.sqlite_path}")
        return

    mgr = ExpenseManager(get_storage(args.backend, args.db))
    cmd = args.command

    if cmd == "add":
        exp = mgr.add_expense(args.amount, args.category, args.description, args.date)
        print(f"Added #{exp.id}: {exp.amount:.2f} {exp.category} on {exp.date}")
    elif cmd == "edit":
        exp = mgr.edit_expense(args.id, args.amount, args.category,
                               args.description, args.date)
        print(f"Updated #{exp.id}: {exp.amount:.2f} {exp.category} on {exp.date}")
    elif cmd == "delete":
        mgr.delete_expense(args.id)
        print(f"Deleted #{args.id}")
    elif cmd == "list":
        print(format_table(mgr.list_expenses(args.category)))
    elif cmd == "search":
        print(format_table(mgr.search(args.keyword, args.category, args.date_from,
                                      args.date_to, args.min_amount, args.max_amount)))
    elif cmd == "month":
        total = mgr.monthly_total(args.year, args.month)
        print(f"Total for {args.year}-{args.month:02d}: {total:.2f}")
    elif cmd == "report":
        print(monthly_report(mgr, args.year, args.month) if args.month
              else yearly_report(mgr, args.year))
    elif cmd == "export":
        n = export_csv(mgr.list_expenses(args.category), args.path)
        print(f"Exported {n} expenses to {args.path}")


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        run(args)
    except ExpenseError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
