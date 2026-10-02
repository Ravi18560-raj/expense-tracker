from abc import ABC, abstractmethod
from typing import List

from ..models import Expense


class Storage(ABC):
    """Interface every backend implements. The rest of the app only knows this."""

    @abstractmethod
    def add(self, expense: Expense) -> Expense: ...

    @abstractmethod
    def get(self, expense_id: int) -> Expense: ...

    @abstractmethod
    def update(self, expense: Expense) -> Expense: ...

    @abstractmethod
    def delete(self, expense_id: int) -> None: ...

    @abstractmethod
    def list_all(self) -> List[Expense]: ...
