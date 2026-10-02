from .base import Storage
from .json_storage import JSONStorage
from .sqlite_storage import SQLiteStorage


def get_storage(backend: str = "sqlite", path: str = None) -> Storage:
    if backend == "json":
        return JSONStorage(path or "data/expenses.json")
    if backend == "sqlite":
        return SQLiteStorage(path or "data/expenses.db")
    raise ValueError(f"Unknown backend '{backend}'")


__all__ = ["Storage", "JSONStorage", "SQLiteStorage", "get_storage"]
