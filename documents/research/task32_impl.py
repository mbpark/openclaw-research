"""
Task 3.2: Event Sourcing for Bank Account

Implements event sourcing pattern for bank account domain.
"""

from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


@dataclass
class Event:
    """Base event class."""
    event_id: str
    created_at: datetime
    aggregate_id: str
    aggregate_version: int
    
    def __init__(self, aggregate_id: str, aggregate_version: int):
        self.event_id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.aggregate_id = aggregate_id
        self.aggregate_version = aggregate_version


@dataclass
class AccountCreated(Event):
    """Account creation event."""
    initial_balance: float
    
    def __init__(self, aggregate_id: str, aggregate_version: int, initial_balance: float):
        super().__init__(aggregate_id, aggregate_version)
        self.initial_balance = initial_balance


@dataclass
class Deposit(Event):
    """Deposit event."""
    amount: float
    
    def __init__(self, aggregate_id: str, aggregate_version: int, amount: float):
        super().__init__(aggregate_id, aggregate_version)
        self.amount = amount


@dataclass
class Withdrawal(Event):
    """Withdrawal event."""
    amount: float
    
    def __init__(self, aggregate_id: str, aggregate_version: int, amount: float):
        super().__init__(aggregate_id, aggregate_version)
        self.amount = amount


@dataclass
class AccountState:
    """Bank account state."""
    account_id: str
    balance: float
    version: int
    
    def __init__(self, account_id: str, balance: float = 0.0, version: int = 0):
        self.account_id = account_id
        self.balance = balance
        self.version = version


class AccountException(Exception):
    """Domain exceptions for account operations."""
    pass


class InsufficientFundsError(AccountException):
    """Insufficient funds."""
    pass


class AccountAlreadyExistsError(AccountException):
    """Account already exists."""
    pass


class AccountNotFoundError(AccountException):
    """Account not found."""
    pass


class InMemoryEventStore:
    """In-memory event store."""
    
    def __init__(self):
        self._events: Dict[str, List[Event]] = {}
    
    def persist(self, event: Event) -> Event:
        """Persist event."""
        if event.aggregate_id not in self._events:
            self._events[event.aggregate_id] = []
        self._events[event.aggregate_id].append(event)
        return event
    
    def get_events(self, aggregate_id: str) -> List[Event]:
        """Get all events for aggregate."""
        return self._events.get(aggregate_id, [])
    
    def clear(self):
        """Clear all events."""
        self._events = {}


class BankAccount:
    """
    Bank account aggregate root with event sourcing.
    """
    
    def __init__(self, account_id: str, event_store: InMemoryEventStore):
        self._account_id = account_id
        self._event_store = event_store
        self._events = event_store.get_events(account_id)
        self._state = self._apply_all_events()
    
    def create(self, initial_balance: float) -> AccountState:
        """Create new account."""
        if self._state is not None:
            raise AccountAlreadyExistsError("Account already exists")
        
        event = AccountCreated(
            aggregate_id=self._account_id,
            aggregate_version=1,
            initial_balance=initial_balance
        )
        self._event_store.persist(event)
        self._events.append(event)
        
        self._state = AccountState(
            account_id=self._account_id,
            balance=initial_balance,
            version=1
        )
        
        return self._state
    
    def deposit(self, amount: float) -> AccountState:
        """Deposit funds."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        if self._state is None:
            raise AccountNotFoundError("Account not found")
        
        event = Deposit(
            aggregate_id=self._account_id,
            aggregate_version=self._state.version + 1,
            amount=amount
        )
        self._event_store.persist(event)
        self._events.append(event)
        
        self._state.balance += amount
        self._state.version += 1
        
        return self._state
    
    def withdraw(self, amount: float) -> AccountState:
        """Withdraw funds."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        if self._state is None:
            raise AccountNotFoundError("Account not found")
        
        if self._state.balance < amount:
            raise InsufficientFundsError(
                f"Insufficient funds: {self._state.balance} < {amount}"
            )
        
        event = Withdrawal(
            aggregate_id=self._account_id,
            aggregate_version=self._state.version + 1,
            amount=amount
        )
        self._event_store.persist(event)
        self._events.append(event)
        
        self._state.balance -= amount
        self._state.version += 1
        
        return self._state
    
    def get_state(self) -> AccountState:
        """Rebuild current state from events."""
        return AccountState(
            account_id=self._account_id,
            balance=self._state.balance if self._state else 0.0,
            version=self._state.version if self._state else 0
        )
    
    def get_history(self) -> List[Event]:
        """Return event history."""
        return self._events.copy()
    
    def _apply_all_events(self) -> Optional[AccountState]:
        """Rebuild state from all events."""
        state = None
        for event in self._events:
            if isinstance(event, AccountCreated):
                state = AccountState(
                    account_id=self._account_id,
                    balance=event.initial_balance,
                    version=1
                )
            elif isinstance(event, Deposit):
                if state:
                    state.balance += event.amount
                    state.version += 1
            elif isinstance(event, Withdrawal):
                if state:
                    state.balance -= event.amount
                    state.version += 1
        return state


class CachedAccountProjection:
    """Maintains up-to-date state without full replay."""
    
    def __init__(self):
        self._cache: Dict[str, AccountState] = {}
    
    def handle_event(self, event: Event):
        """Update projection when new event arrives."""
        account_id = event.aggregate_id
        
        if account_id not in self._cache:
            return
        
        state = self._cache[account_id]
        
        if isinstance(event, AccountCreated):
            state.balance = event.initial_balance
        elif isinstance(event, Deposit):
            state.balance += event.amount
        elif isinstance(event, Withdrawal):
            state.balance -= event.amount
        
        state.version = event.aggregate_version
        self._cache[account_id] = state
    
    def get_state(self, account_id: str) -> Optional[AccountState]:
        """Get current state from projection."""
        return self._cache.get(account_id)


def test_event_sourcing():
    """Test event sourcing implementation."""
    event_store = InMemoryEventStore()
    account_id = "account-001"
    
    # Create account
    account = BankAccount(account_id, event_store)
    state = account.create(1000.0)
    
    assert state.balance == 1000.0
    assert state.version == 1
    
    # Deposit
    state = account.deposit(500.0)
    assert state.balance == 1500.0
    assert state.version == 2
    
    # Withdraw
    state = account.withdraw(200.0)
    assert state.balance == 1300.0
    assert state.version == 3
    
    # Test insufficient funds
    try:
        account.withdraw(5000.0)
        assert False, "Should have raised InsufficientFundsError"
    except InsufficientFundsError:
        pass
    
    # Test event history
    history = account.get_history()
    assert len(history) == 3
    
    # Test aggregate rebuild
    new_account = BankAccount(account_id, event_store)
    assert new_account.get_state().balance == 1300.0
    
    print("Tests passed")


if __name__ == "__main__":
    test_event_sourcing()
