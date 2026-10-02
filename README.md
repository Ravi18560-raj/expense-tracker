# Personal Expense Tracker CLI

Pure-Python (standard library only) CLI to track expenses.
Storage is pluggable: start with **JSON**, upgrade to **SQLite**.

## Structure
```
main.py                     entry point
expense_tracker/
  models.py                 Expense class + validation
  exceptions.py             custom exceptions
  manager.py                add/edit/delete/search/totals
  reports.py                text reports
  exporter.py               CSV export
  cli.py                    argparse commands
  storage/
    base.py                 Storage interface
    json_storage.py         Phase 1
    sqlite_storage.py       Phase 2
tests/test_manager.py       runs against both backends
```

## Usage
```
python main.py --backend json add 250 food -d "Lunch" --date 2026-10-01
python main.py --backend json list
python main.py --backend json edit 1 --amount 275
python main.py --backend json delete 1
python main.py --backend json search lunch --min 100
python main.py --backend json month --year 2026 --month 10
python main.py --backend json report --year 2026 --month 10
python main.py --backend json report --year 2026        # yearly
python main.py --backend json export out.csv

# upgrade: copy JSON data into SQLite, then drop --backend json
python main.py migrate
python main.py list
```
Run tests: `pytest`
# expense-tracker
