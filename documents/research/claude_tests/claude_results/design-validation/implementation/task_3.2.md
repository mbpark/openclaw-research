# Event Sourcing for Bank Account

## Complete Implementation

```python
from __future__ import annotations

from typing import List, Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------
# Events are immutable facts that have already happened. We enforce
# immutability with `frozen=True`. Each event carries the aggregate version
# it produced, giving us a strict sequential ordering per aggregate and
# enabling optimistic concurrency checks.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Event:
    """Base immutable domain event.

    Attributes:
        id: Globally unique identifier for this event.
        created_at: UTC timestamp the event was recorded.
        aggregate_id: Identifier of the aggregate the event belongs to.
        aggregate_version: Monotonically increasing version (1-based) of the
            aggregate *after* this event is applied. Used for ordering and
            optimistic concurrency control.
    """
    id: str
    created_at: datetime
    aggregate_id: str
    aggregate_version: int


@dataclass(frozen=True)
class AccountCreated(Event):
    """Emitted exactly once as the first event of an account's lifecycle."""
    initial_balance: float


@dataclass(frozen=True)
class Deposit(Event):
    """Funds added to the account."""
    amount: float


@dataclass(frozen=True)
class Withdrawal(Event):
    """Funds removed from the account."""
    amount: float


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class AccountState:
    """Mutable read-model representing the current state of an account.

    State is *derived* from events; it is never persisted as the source of
    truth. Two states are equal when their account id and balance match.
    """

    def __init__(self, account_id: str, balance: float = 0.0) -> None:
        self.account_id = account_id
        self.balance = balance

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AccountState):
            return NotImplemented
        return (
            self.account_id == other.account_id
            and self.balance == other.balance
        )

    def __repr__(self) -> str:
        return f"AccountState(account_id={self.account_id!r}, balance={self.balance})"


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class AccountException(Exception):
    """Domain exceptions for invalid account operations."""
    pass


# ---------------------------------------------------------------------------
# Repository
# ---------------------------------------------------------------------------

class AccountRepository:
    """In-memory append-only event store.

    Events are grouped by aggregate id and stored in append order. The store
    rejects out-of-order or duplicate versions to guarantee a clean,
    gap-free, sequential event stream per aggregate.

    A list of observers (e.g. projections) can be registered to be notified
    of every newly appended event.
    """

    def __init__(self) -> None:
        self._store: Dict[str, List[Event]] = {}
        self._observers: List["CachedAccountProjection"] = []

    def register_observer(self, observer: "CachedAccountProjection") -> None:
        """Register a projection to receive events as they are appended."""
        self._observers.append(observer)

    def apply(self, event: Event) -> None:
        """Persist an event to the store.

        Enforces that versions are strictly sequential (1, 2, 3, ...) per
        aggregate. This protects against duplicate appends and lost updates
        (optimistic concurrency).

        Args:
            event: The immutable event to persist.

        Raises:
            AccountException: If the event version is not exactly one greater
                than the current latest version for the aggregate.
        """
        stream = self._store.setdefault(event.aggregate_id, [])
        expected_version = len(stream) + 1
        if event.aggregate_version != expected_version:
            raise AccountException(
                f"Concurrency/ordering violation for {event.aggregate_id}: "
                f"expected version {expected_version}, got "
                f"{event.aggregate_version}."
            )
        stream.append(event)

        # Notify projections so they can incrementally update.
        for observer in self._observers:
            observer.handle_event(event)

    def get_events(self, aggregate_id: str) -> List[Event]:
        """Retrieve all events for an aggregate in version order.

        Returns a copy so callers cannot mutate the underlying store.
        """
        return list(self._store.get(aggregate_id, []))


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------

class BankAccount:
    """Bank account aggregate root.

    Commands (`create`, `deposit`, `withdraw`) validate business rules
    against the current rebuilt state, emit a new event, and persist it.
    State is always derived by folding (replaying) the event stream.
    """

    def __init__(self, account_id: str, repository: AccountRepository) -> None:
        self._account_id = account_id
        self._repository = repository
        self._events: List[Event] = []
        self._state: Optional[AccountState] = None

    # -- internal helpers --------------------------------------------------

    def _next_version(self) -> int:
        """Compute the next sequential aggregate version."""
        return len(self._repository.get_events(self._account_id)) + 1

    def _new_event_meta(self) -> dict:
        """Build common event metadata for a new event."""
        return {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc),
            "aggregate_id": self._account_id,
            "aggregate_version": self._next_version(),
        }

    @staticmethod
    def _apply_event(state: Optional[AccountState], event: Event) -> AccountState:
        """Pure reducer: produce next state from (state, event).

        This is the heart of event sourcing — a deterministic fold over the
        event stream. Kept static and pure so it can be reused by anyone
        rebuilding state (aggregate, projection, tests).
        """
        if isinstance(event, AccountCreated):
            return AccountState(event.aggregate_id, event.initial_balance)
        if state is None:
            # Any non-creation event without prior state is a corrupt stream.
            raise AccountException(
                f"Cannot apply {type(event).__name__} before AccountCreated."
            )
        if isinstance(event, Deposit):
            return AccountState(state.account_id, state.balance + event.amount)
        if isinstance(event, Withdrawal):
            return AccountState(state.account_id, state.balance - event.amount)
        raise AccountException(f"Unknown event type: {type(event).__name__}")

    def _rebuild(self) -> Optional[AccountState]:
        """Fold the full persisted event stream into current state."""
        state: Optional[AccountState] = None
        for event in self._repository.get_events(self._account_id):
            state = self._apply_event(state, event)
        return state

    # -- commands ----------------------------------------------------------

    def create(self, initial_balance: float) -> AccountState:
        """Create a new account.

        Args:
            initial_balance: Opening balance, must be non-negative.

        Returns:
            The freshly created account state.

        Raises:
            AccountException: If the account already exists or the initial
                balance is negative.
        """
        if self._repository.get_events(self._account_id):
            raise AccountException(
                f"Account {self._account_id} already exists."
            )
        if initial_balance < 0:
            raise AccountException("Initial balance cannot be negative.")

        event = AccountCreated(initial_balance=initial_balance,
                               **self._new_event_meta())
        self._repository.apply(event)
        self._events.append(event)
        self._state = self._apply_event(None, event)
        return self.get_state()

    def deposit(self, amount: float) -> AccountState:
        """Deposit funds.

        Args:
            amount: Positive amount to add.

        Returns:
            The new state after the deposit.

        Raises:
            AccountException: If the account does not exist or amount <= 0.
        """
        state = self._require_existing_state()
        if amount <= 0:
            raise AccountException("Deposit amount must be positive.")

        event = Deposit(amount=amount, **self._new_event_meta())
        self._repository.apply(event)
        self._events.append(event)
        self._state = self._apply_event(state, event)
        return self.get_state()

    def withdraw(self, amount: float) -> AccountState:
        """Withdraw funds.

        Args:
            amount: Positive amount to remove.

        Returns:
            The new state after the withdrawal.

        Raises:
            AccountException: If the account does not exist, amount <= 0, or
                there are insufficient funds.
        """
        state = self._require_existing_state()
        if amount <= 0:
            raise AccountException("Withdrawal amount must be positive.")
        if amount > state.balance:
            raise AccountException(
                f"Insufficient funds: balance={state.balance}, "
                f"requested={amount}."
            )

        event = Withdrawal(amount=amount, **self._new_event_meta())
        self._repository.apply(event)
        self._events.append(event)
        self._state = self._apply_event(state, event)
        return self.get_state()

    def _require_existing_state(self) -> AccountState:
        """Return current state, raising if the account was never created."""
        state = self.get_state()
        if state is None:
            raise AccountException(
                f"Account {self._account_id} does not exist."
            )
        return state

    # -- queries -----------------------------------------------------------

    def get_state(self) -> Optional[AccountState]:
        """Return current state, rebuilding from events when not cached."""
        if self._state is None:
            self._state = self._rebuild()
        return self._state

    def get_history(self) -> List[Event]:
        """Return the ordered event history for this account."""
        return self._repository.get_events(self._account_id)


# ---------------------------------------------------------------------------
# Projection (read model)
# ---------------------------------------------------------------------------

class CachedAccountProjection:
    """Maintains an up-to-date materialized view without full replay.

    The projection reacts to each new event incrementally (O(1) per event)
    and caches the latest state per aggregate so reads are O(1) and never
    require replaying the stream. If asked about an aggregate it has not seen
    (e.g. it was created before this projection registered), it lazily
    backfills by replaying that single stream once.
    """

    def __init__(self, repository: AccountRepository) -> None:
        self._repository = repository
        self._cache: Dict[str, AccountState] = {}

    def handle_event(self, event: Event) -> None:
        """Incrementally update the projection from a single new event."""
        current = self._cache.get(event.aggregate_id)
        self._cache[event.aggregate_id] = BankAccount._apply_event(current, event)

    def get_state(self, aggregate_id: str) -> Optional[AccountState]:
        """Return cached state, lazily backfilling on a cache miss."""
        if aggregate_id in self._cache:
            return self._cache[aggregate_id]

        # Cache miss: backfill by replaying the stream once.
        state: Optional[AccountState] = None
        for event in self._repository.get_events(aggregate_id):
            state = BankAccount._apply_event(state, event)
        if state is not None:
            self._cache[aggregate_id] = state
        return state
```

## Usage Example

```python
repo = AccountRepository()
projection = CachedAccountProjection(repo)
repo.register_observer(projection)

acct = BankAccount("acc-1", repo)
acct.create(100.0)
acct.deposit(50.0)
acct.withdraw(30.0)

print(acct.get_state())                  # AccountState(account_id='acc-1', balance=120.0)
print(projection.get_state("acc-1"))     # AccountState(account_id='acc-1', balance=120.0) - no replay

for e in acct.get_history():
    print(e.aggregate_version, type(e).__name__)
```

## Design Decisions & Tradeoffs

**Immutable events (`frozen=True`).** Events are historical facts; freezing them prevents accidental mutation and makes the audit log trustworthy. Tradeoff: requires creating new objects rather than editing, which is exactly what we want for an append-only log.

**Pure reducer `_apply_event`.** State transitions live in one static, side-effect-free function reused by the aggregate's rebuild, the projection, and tests. This eliminates the "two places that compute balance disagree" bug class. Tradeoff: `static` access from the projection couples them slightly; in a larger system I'd extract this into a shared `apply` function or an `Aggregate.replay` module.

**Sequential version enforcement in the repository.** `apply` requires `version == current_count + 1`, giving optimistic concurrency control and a gap-free stream. Two writers racing on the same aggregate will cause one to fail rather than silently lose an update.

**Repository as the source of versioning truth.** `_next_version` reads stream length rather than trusting in-memory `_events`, so a freshly loaded aggregate (empty `_events`) still computes correct versions.

**Projection incremental updates + lazy backfill.** Registered projections update in O(1) per event (the whole point — avoid full replay on every query). The lazy backfill handles aggregates created before the projection subscribed, trading a one-time replay for correctness.

## Edge Cases Handled

| Case | Behavior |
|------|----------|
| Double `create` | `AccountException` (events already exist) |
| Negative initial balance | `AccountException` |
| Deposit/withdraw before create | `AccountException` (no state) |
| Non-positive deposit/withdraw | `AccountException` |
| Overdraft | `AccountException`, no event emitted |
| Out-of-order / duplicate version | `AccountException` in `apply` |
| Corrupt stream (non-create first event) | `AccountException` in reducer |
| Query unknown aggregate | Returns `None` |
| Projection cache miss | Lazy single replay, then cached |
| `get_events` mutation | Returns a copy, store protected |

**Note on floats:** real money should use `Decimal` to avoid rounding errors. I kept `float` to match the provided interface, but in production I'd change the type signatures to `Decimal`.