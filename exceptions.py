class ExpenseError(Exception):
    """Base class for all app errors."""


class ValidationError(ExpenseError):
    """Raised when user input is invalid."""


class ExpenseNotFoundError(ExpenseError):
    """Raised when an expense id does not exist."""


class StorageError(ExpenseError):
    """Raised when reading/writing the data store fails."""
