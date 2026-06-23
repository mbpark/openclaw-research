## Task 3.2: Event Sourcing for Bank Account

**Description:**
Implement event sourcing pattern for bank account domain.

**Interface:**
```python
from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Event:
    id: str
    created_at: datetime
    aggregate_id: str
    aggregate_version: int


@dataclass
class AccountCreated(Event):
    initial_balance: float


@dataclass
class Deposit(Event):
    amount: float


@dataclass
class Withdrawal(Event):
    amount: float


class AccountState:
    def __init__(self, account_id: str, balance: float = 0.0):
        self.account_id = account_id
        self.balance = balance


class AccountException(Exception):
    """Domain exceptions for invalid account operations."""
    pass


class AccountRepository:
    def apply(self, event: Event) -> None:
        """Persist event to store."""
        ...
    
    def get_events(self, aggregate_id: str) -> List[Event]:
        """Retrieve all events for aggregate."""
        ...


class BankAccount:
    def __init__(
        self,
        account_id: str,
        repository: AccountRepository
    ):
        self._account_id = account_id
        self._repository = repository
        self._events: List[Event] = []
        self._state = None

    def create(self, initial_balance: float) -> AccountState:
        """Create new account (first event only)."""
        ...

    def deposit(self, amount: float) -> AccountState:
        """Deposit funds. Returns new state."""
        ...

    def withdraw(self, amount: float) -> AccountState:
        """Withdraw funds. Raises if insufficient."""
        ...
