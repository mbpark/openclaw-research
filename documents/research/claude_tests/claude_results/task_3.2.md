# Event Sourcing for Bank Account

Here's a complete, runnable implementation of the event sourcing pattern.

```python
from typing import List, Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from collections import defaultdict
import uuid


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------
# Events are immutable facts about something that has already happened.
# We use frozen dataclasses to enforce immutability at runtime.

@dataclass(frozen=True)
class Event:
    """
    Base immutable event.

    Attributes:
        id: Globally unique event identifier.
        created_at: UTC timestamp when the event was created.
        aggregate_id: Identifier of the aggregate this event belongs to.
        aggregate_version: Sequential, 1-based version of the aggregate
            *after* this event is applied. Used for ordering and optimistic
            concurrency control.
    """
    id: str
    created_at: datetime
    aggregate_id: str
    aggregate_version: int


@dataclass(frozen=True)
class AccountCreated(Event):
    """Emitted when an account is first created."""
    initial_balance: float


@dataclass(frozen=True)
class Deposit(Event):
    """Emitted when funds are deposited."""
    amount: float


@dataclass(frozen=True)
class Withdrawal(Event):
    """Emitted when funds are withdrawn."""
    amount: float


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class AccountState:
    """
    Read-model representing the current state of an account.

    This is a *derived* value: it is always reconstructed by folding events,
    never mutated directly by callers.
    """

    def __init__(
        self,
        account_id: str,
        balance: float = 0.0,
        version: int = 0,
        created: bool = False,
    ):
        self.account_id = account_id
        self.balance = balance
        self.version = version
        self.created = created

    def __repr__(self) -> str:
        return (
            f"AccountState(account_id={self.account_id!r}, "
            f"balance={self.balance}, version={self.version}, "
            f"created={self.created})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AccountState):
            return NotImplemented
        return (
            self.account_id == other.account_id
            and self.balance == other.balance
            and self.version == other.version
            and self.created == other.created
        )


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class AccountException(Exception):
    """Domain exceptions for invalid account operations."""
    pass


# ---------------------------------------------------------------------------
# Repository (Event Store)
# ---------------------------------------------------------------------------

class AccountRepository:
    """
    In-memory append-only event store.

    Events are stored per-aggregate in insertion order. The store enforces
    optimistic concurrency: an appended event's version must be exactly one
    greater than the last stored version for that aggregate.
    """

    def __init__(self) -> None:
        self._store: Dict[str, List[Event]] = defaultdict(list)
        # Optional subscribers (e.g. projections) notified on every append.
        self._subscribers: List["CachedAccountProjection"] = []

    def subscribe(self, projection: "CachedAccountProjection") -> None:
        """Register a projection to receive events as they are appended."""
        self._subscribers.append(projection)

    def apply(self, event: Event) -> None:
        """
        Persist an event to the store.

        Raises:
            AccountException: If the event version is not strictly sequential
                (gap or duplicate), which would corrupt the stream ordering.
        """
        stream = self._store[event.aggregate_id]
        expected_version = len(stream) + 1
        if event.aggregate_version != expected_version:
            raise AccountException(
                f"Concurrency/version error: expected version "
                f"{expected_version}, got {event.aggregate_version} "
                f"for aggregate {event.aggregate_id!r}"
            )
        stream.append(event)

        # Notify projections so they can update incrementally.
        for subscriber in self._subscribers:
            subscriber.handle_event(event)

    def get_events(self, aggregate_id: str) -> List[Event]:
        """Retrieve all events for an aggregate in version order (a copy)."""
        return list(self._store.get(aggregate_id, []))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


def _apply_event(state: AccountState, event: Event) -> AccountState:
    """
    Pure fold function: given a state and an event, produce the next state.

    This is the single source of truth for how events mutate state and is
    shared between the aggregate's replay logic and the projection, so they
    can never drift apart.

    Raises:
        AccountException: If an event is invalid for the current state
            (e.g. duplicate creation, operating on a non-created account).
    """
    if isinstance(event, AccountCreated):
        if state.created:
            raise AccountException(
                f"Account {state.account_id!r} already created"
            )
        return AccountState(
            account_id=event.aggregate_id,
            balance=event.initial_balance,
            version=event.aggregate_version,
            created=True,
        )

    # All non-creation events require an existing account.
    if not state.created:
        raise AccountException(
            f"Cannot apply {type(event).__name__} to non-existent account "
            f"{state.account_id!r}"
        )

    if isinstance(event, Deposit):
        new_balance = state.balance + event.amount
    elif isinstance(event, Withdrawal):
        new_balance = state.balance - event.amount
    else:
        raise AccountException(f"Unknown event type: {type(event).__name__}")

    return AccountState(
        account_id=state.account_id,
        balance=new_balance,
        version=event.aggregate_version,
        created=True,
    )


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------

class BankAccount:
    """
    The BankAccount aggregate root.

    Commands (create/deposit/withdraw) validate business rules against the
    current state, then emit and persist events. State is always derived by
    replaying the event stream, guaranteeing that the in-memory model and the
    persisted history agree.
    """

    def __init__(self, account_id: str, repository: AccountRepository):
        self._account_id = account_id
        self._repository = repository

    # -- Command handlers ---------------------------------------------------

    def create(self, initial_balance: float) -> AccountState:
        """
        Create a new account.

        Args:
            initial_balance: Opening balance; must be non-negative.

        Returns:
            The new account state.

        Raises:
            AccountException: If the account already exists or the initial
                balance is negative.
        """
        if initial_balance < 0:
            raise AccountException("Initial balance cannot be negative")

        state = self.get_state()
        if state.created:
            raise AccountException(
                f"Account {self._account_id!r} already exists"
            )

        event = AccountCreated(
            id=str(uuid.uuid4()),
            created_at=_now(),
            aggregate_id=self._account_id,
            aggregate_version=state.version + 1,
            initial_balance=initial_balance,
        )
        return self._commit(event)

    def deposit(self, amount: float) -> AccountState:
        """
        Deposit funds into the account.

        Args:
            amount: Positive amount to deposit.

        Returns:
            The updated account state.

        Raises:
            AccountException: If the account does not exist or amount <= 0.
        """
        state = self._require_existing()
        if amount <= 0:
            raise AccountException("Deposit amount must be positive")

        event = Deposit(
            id=str(uuid.uuid4()),
            created_at=_now(),
            aggregate_id=self._account_id,
            aggregate_version=state.version + 1,
            amount=amount,
        )
        return self._commit(event)

    def withdraw(self, amount: float) -> AccountState:
        """
        Withdraw funds from the account.

        Args:
            amount: Positive amount to withdraw.

        Returns:
            The updated account state.

        Raises:
            AccountException: If the account does not exist, amount <= 0,
                or there are insufficient funds.
        """
        state = self._require_existing()
        if amount <= 0:
            raise AccountException("Withdrawal amount must be positive")
        if amount > state.balance:
            raise AccountException(
                f"Insufficient funds: balance={state.balance}, "
                f"requested={amount}"
            )

        event = Withdrawal(
            id=str(uuid.uuid4()),
            created_at=_now(),
            aggregate_id=self._account_id,
            aggregate_version=state.version + 1,
            amount=amount,
        )
        return self._commit(event)

    # -- Queries ------------------------------------------------------------

    def get_state(self) -> AccountState:
        """Rebuild the current state by replaying the full event stream."""
        state = AccountState(account_id=self._account_id)
        for event in self._repository.get_events(self._account_id):
            state = _apply_event(state, event)
        return state

    def get_history(self) -> List[Event]:
        """Return the ordered event history for this account."""
        return self._repository.get_events(self._account_id)

    # -- Internals ----------------------------------------------------------

    def _require_existing(self) -> AccountState:
        """Return current state, raising if the account does not exist."""
        state = self.get_state()
        if not state.created:
            raise AccountException(
                f"Account {self._account_id!r} does not exist"
            )
        return state

    def _commit(self, event: Event) -> AccountState:
        """Persist an event and return the resulting state."""
        self._repository.apply(event)
        return self.get_state()


# ---------------------------------------------------------------------------
# Projection
# ---------------------------------------------------------------------------

class CachedAccountProjection:
    """
    A read-model projection maintaining up-to-date account states without
    replaying full event streams on every query.

    The projection updates incrementally as events arrive via `handle_event`
    (typically driven by the repository's subscription mechanism). It uses the
    same `_apply_event` fold as the aggregate, so it cannot diverge from the
    canonical state logic.
    """

    def __init__(self, repository: AccountRepository):
        self._repository = repository
        self._cache: Dict[str, AccountState] = {}

    def handle_event(self, event: Event) -> None:
        """
        Update the projection incrementally when a new event arrives.

        Idempotency / ordering guard: events older than or equal to the
        cached version are ignored to protect against duplicate delivery.
        """
        current = self._cache.get(event.aggregate_id)

        if current is None:
            current = AccountState(account_id=event.aggregate_id)

        # Skip already-applied or out-of-order-old events.
        if event.aggregate_version <= current.version:
            return

        # If we somehow missed events (gap), rebuild from the store to stay
        # consistent rather than silently producing wrong balances.
        if event.aggregate_version != current.version + 1:
            self._rebuild(event.aggregate_id)
            return

        self._cache[event.aggregate_id] = _apply_event(current, event)

    def get_state(self, aggregate_id: str) -> Optional[AccountState]:
        """Get the current state from the projection cache, if known."""
        return self._cache.get(aggregate_id)

    def _rebuild(self, aggregate_id: str) -> None:
        """Recover the projection for an aggregate from the event store."""
        state = AccountState(account_id=aggregate_id)
        for event in self._repository.get_events(aggregate_id):
            state = _apply_event(state, event)
        self._cache[aggregate_id] = state


# ---------------------------------------------------------------------------
# Demonstration
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    repo = AccountRepository()
    projection = CachedAccountProjection(repo)
    repo.subscribe(projection)

    account = BankAccount("acc-1", repo)

    print(account.create(100.0))      # balance=100, version=1
    print(account.deposit(50.0))      # balance=150, version=2
    print(account.withdraw(30.0))     # balance=120, version=3

    # Projection serves reads without replaying the full stream.
    print("Projection:", projection.get_state("acc-1"))

    # Replayed aggregate state matches projection.
    print("Replayed:  ", account.get_state())

    # Event history
    for e in account.get_history():
        print(f"  v{e.aggregate_version} {type(e).__name__}")

    # Edge cases
    try:
        account.withdraw(10_000)
    except AccountException as exc:
        print("Rejected:", exc)

    try:
        account.create(10)  # already exists
    except AccountException as exc:
        print("Rejected:", exc)
```

---

## Design Decisions & Tradeoffs

### 1. Immutable events (`frozen=True`)
Events represent facts that already happened, so I made all event dataclasses `frozen`. This prevents accidental mutation of history at runtime — a core event-sourcing invariant.

### 2. A single shared fold function (`_apply_event`)
The most important design choice: **both the aggregate's `get_state()` replay and the projection's `handle_event()` use the exact same pure function**. This eliminates the classic event-sourcing bug where the write-side and read-side state-derivation logic drift apart. State derivation lives in one place.

### 3. Sequential versioning + optimistic concurrency
`aggregate_version` is 1-based and strictly sequential. The repository's `apply()` rejects any event whose version isn't exactly `last + 1`, catching gaps, duplicates, and concurrent-write races (optimistic concurrency control).

### 4. Validation lives in the aggregate, not the fold
Command-level rules (positive amounts, sufficient funds) are checked in `create/deposit/withdraw` *before* emitting events. The fold (`_apply_event`) only enforces structural invariants (account must exist, no double-create). This separation reflects reality: once an event is recorded, it must always replay successfully — we never want a stored event that the fold rejects.

### 5. Projection: incremental with self-healing
`CachedAccountProjection` updates O(1) per event instead of replaying. It guards against:
- **Duplicates / stale events** (`version <= cached version` → ignore, idempotent).
- **Gaps** (`version != cached + 1` → rebuild from store).

This trades a little complexity for robustness against unreliable event delivery.

## Edge Cases Handled

| Case | Behavior |
|------|----------|
| Negative initial balance | `AccountException` |
| Double account creation | `AccountException` (both aggregate & fold) |
| Deposit/withdraw on non-existent account | `AccountException` |
| Non-positive deposit/withdraw amounts | `AccountException` |
| Overdraft | `AccountException`, no event emitted |
| Out-of-order / duplicate event versions | Repository rejects; projection ignores/rebuilds |
| Querying unknown aggregate in projection | Returns `None` |
| Timezone-naive timestamps | Always UTC-aware (`datetime.now(timezone.utc)`) |
| History/event-list mutation by callers | Returns copies, not internal lists |

## Notes / Possible Extensions
- **Snapshots:** For long event streams, persist periodic `AccountState` snapshots and replay only events after the snapshot.
- **Persistence:** The repository is in-memory; the `apply`/`get_events` interface maps cleanly onto a real append-only store (e.g. EventStoreDB, a SQL events table).
- **Floats:** I kept `float` per the interface, but production money code should use `Decimal` to avoid rounding errors.