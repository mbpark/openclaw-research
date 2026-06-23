# Event Sourcing for Bank Account

Here's a complete, runnable implementation of the event sourcing pattern.

```python
from __future__ import annotations

from typing import List, Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Event:
    """
    Base immutable event.

    Immutability is enforced via ``frozen=True`` so that once an event is
    created it can never be mutated. ``aggregate_version`` provides the
    sequential ordering within a single aggregate's stream (1-based).
    """
    id: str
    created_at: datetime
    aggregate_id: str
    aggregate_version: int


@dataclass(frozen=True)
class AccountCreated(Event):
    """Emitted exactly once as the first event in an account stream."""
    initial_balance: float


@dataclass(frozen=True)
class Deposit(Event):
    """Funds added to an account."""
    amount: float


@dataclass(frozen=True)
class Withdrawal(Event):
    """Funds removed from an account."""
    amount: float


# ---------------------------------------------------------------------------
# State + Exceptions
# ---------------------------------------------------------------------------

class AccountState:
    """Current materialized state of a bank account."""

    def __init__(self, account_id: str, balance: float = 0.0,
                 version: int = 0):
        self.account_id = account_id
        self.balance = balance
        # Track which event version produced this state. Useful for
        # optimistic concurrency and projection bookkeeping.
        self.version = version

    def __repr__(self) -> str:
        return (f"AccountState(account_id={self.account_id!r}, "
                f"balance={self.balance}, version={self.version})")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AccountState):
            return NotImplemented
        return (self.account_id == other.account_id
                and self.balance == other.balance
                and self.version == other.version)


class AccountException(Exception):
    """Domain exceptions for invalid account operations."""
    pass


# ---------------------------------------------------------------------------
# Repository (event store)
# ---------------------------------------------------------------------------

class AccountRepository:
    """
    In-memory append-only event store.

    Events are grouped by aggregate id and stored in arrival order, which
    (because we assign sequential versions on append) is also version order.
    An optional observer list lets projections subscribe to new events.
    """

    def __init__(self) -> None:
        self._store: Dict[str, List[Event]] = {}
        self._observers: List["CachedAccountProjection"] = []

    def subscribe(self, observer: "CachedAccountProjection") -> None:
        """Register a projection to receive events as they are appended."""
        self._observers.append(observer)

    def apply(self, event: Event) -> None:
        """
        Persist event to store.

        Enforces optimistic concurrency: an appended event must have a
        version exactly one greater than the current last version for its
        aggregate. This guarantees a gap-free, sequential stream.
        """
        stream = self._store.setdefault(event.aggregate_id, [])
        expected_version = len(stream) + 1
        if event.aggregate_version != expected_version:
            raise AccountException(
                f"Concurrency/version error: expected version "
                f"{expected_version}, got {event.aggregate_version}"
            )
        stream.append(event)

        # Notify projections so they can update incrementally.
        for observer in self._observers:
            observer.handle_event(event)

    def get_events(self, aggregate_id: str) -> List[Event]:
        """Retrieve all events for aggregate, in version order."""
        # Return a copy to prevent external mutation of the stored stream.
        return list(self._store.get(aggregate_id, []))


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------

class BankAccount:
    """
    Bank account aggregate root.

    Commands (create/deposit/withdraw) validate against current state, then
    emit an event that is persisted via the repository. State is always
    derivable by replaying the event stream.
    """

    def __init__(self, account_id: str, repository: AccountRepository):
        self._account_id = account_id
        self._repository = repository
        # Local cache of this aggregate's events (loaded lazily).
        self._events: List[Event] = []
        self._state: Optional[AccountState] = None

    # ---- internal helpers -------------------------------------------------

    def _load(self) -> None:
        """Load events from the store into the local cache."""
        self._events = self._repository.get_events(self._account_id)

    def _next_version(self) -> int:
        """Compute the next sequential version for a new event."""
        if not self._events:
            self._load()
        return len(self._events) + 1

    def _make_event_id(self) -> str:
        return str(uuid.uuid4())

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _record(self, event: Event) -> AccountState:
        """Persist an event and refresh the cached state."""
        self._repository.apply(event)
        self._events.append(event)
        # Invalidate the cached state; recompute fresh.
        self._state = None
        return self.get_state()

    @staticmethod
    def _validate_positive(amount: float, op: str) -> None:
        if amount <= 0:
            raise AccountException(f"{op} amount must be positive, got {amount}")

    # ---- commands ---------------------------------------------------------

    def create(self, initial_balance: float) -> AccountState:
        """
        Create a new account (must be the first event in the stream).

        Raises:
            AccountException: if the account already exists or the initial
                balance is negative.
        """
        self._load()
        if self._events:
            raise AccountException(
                f"Account {self._account_id} already exists"
            )
        if initial_balance < 0:
            raise AccountException(
                f"Initial balance cannot be negative, got {initial_balance}"
            )
        event = AccountCreated(
            id=self._make_event_id(),
            created_at=self._now(),
            aggregate_id=self._account_id,
            aggregate_version=self._next_version(),
            initial_balance=initial_balance,
        )
        return self._record(event)

    def deposit(self, amount: float) -> AccountState:
        """
        Deposit funds. Returns the new state.

        Raises:
            AccountException: if the account does not exist or amount <= 0.
        """
        self._ensure_exists()
        self._validate_positive(amount, "Deposit")
        event = Deposit(
            id=self._make_event_id(),
            created_at=self._now(),
            aggregate_id=self._account_id,
            aggregate_version=self._next_version(),
            amount=amount,
        )
        return self._record(event)

    def withdraw(self, amount: float) -> AccountState:
        """
        Withdraw funds. Returns the new state.

        Raises:
            AccountException: if the account does not exist, amount <= 0, or
                there are insufficient funds (the aggregate rejects events
                that would put the balance below zero).
        """
        self._ensure_exists()
        self._validate_positive(amount, "Withdrawal")
        current = self.get_state()
        if amount > current.balance:
            raise AccountException(
                f"Insufficient funds: balance={current.balance}, "
                f"requested={amount}"
            )
        event = Withdrawal(
            id=self._make_event_id(),
            created_at=self._now(),
            aggregate_id=self._account_id,
            aggregate_version=self._next_version(),
            amount=amount,
        )
        return self._record(event)

    def _ensure_exists(self) -> None:
        self._load()
        if not self._events:
            raise AccountException(
                f"Account {self._account_id} does not exist"
            )

    # ---- queries ----------------------------------------------------------

    def get_state(self) -> AccountState:
        """
        Rebuild current state from events (full replay).

        Returns a fresh ``AccountState`` reflecting every persisted event.
        """
        self._load()
        return self._fold(self._events)

    def get_history(self) -> List[Event]:
        """Return the event history in version order."""
        self._load()
        return list(self._events)

    @staticmethod
    def _fold(events: List[Event]) -> AccountState:
        """
        Pure left-fold of events into a state.

        This is the single source of truth for how events mutate state and
        is reused by the projection's incremental updater.
        """
        if not events:
            raise AccountException("No events to build state from")

        state: Optional[AccountState] = None
        for event in events:
            state = BankAccount._apply_event(state, event)
        assert state is not None
        return state

    @staticmethod
    def _apply_event(state: Optional[AccountState], event: Event) -> AccountState:
        """Apply a single event to a state (the reducer)."""
        if isinstance(event, AccountCreated):
            if state is not None:
                raise AccountException("AccountCreated must be the first event")
            return AccountState(
                account_id=event.aggregate_id,
                balance=event.initial_balance,
                version=event.aggregate_version,
            )
        if state is None:
            raise AccountException(
                "First event must be AccountCreated, "
                f"got {type(event).__name__}"
            )
        if isinstance(event, Deposit):
            return AccountState(state.account_id,
                                state.balance + event.amount,
                                event.aggregate_version)
        if isinstance(event, Withdrawal):
            new_balance = state.balance - event.amount
            if new_balance < 0:
                # Defensive: stored streams should never contain such events.
                raise AccountException("Withdrawal would overdraw the account")
            return AccountState(state.account_id, new_balance,
                                event.aggregate_version)
        raise AccountException(f"Unknown event type: {type(event).__name__}")


# ---------------------------------------------------------------------------
# Projection
# ---------------------------------------------------------------------------

class CachedAccountProjection:
    """
    Read-model that maintains up-to-date account states without full replay.

    Each new event is applied incrementally to the cached state (O(1) per
    event) rather than replaying the whole stream (O(n)). Reads are O(1).

    It can be wired up live (via ``repository.subscribe``) so it stays in
    sync as events are appended, and can also rebuild itself from the store.
    """

    def __init__(self, repository: AccountRepository):
        self._repository = repository
        self._cache: Dict[str, AccountState] = {}
        # Track last applied version per aggregate to make handling idempotent
        # and to detect gaps.
        self._versions: Dict[str, int] = {}

    def handle_event(self, event: Event) -> None:
        """
        Update projection when a new event arrives.

        Idempotent: events whose version is <= the last applied version are
        ignored, so replaying or double-delivery does not corrupt state.
        """
        last = self._versions.get(event.aggregate_id, 0)

        # Ignore already-applied events (idempotency / replay safety).
        if event.aggregate_version <= last:
            return

        # Detect gaps: if an event is missing, fall back to a full rebuild
        # from the store so the projection self-heals.
        if event.aggregate_version != last + 1:
            self.rebuild(event.aggregate_id)
            return

        current = self._cache.get(event.aggregate_id)
        new_state = BankAccount._apply_event(current, event)
        self._cache[event.aggregate_id] = new_state
        self._versions[event.aggregate_id] = event.aggregate_version

    def rebuild(self, aggregate_id: str) -> None:
        """Recompute one aggregate's projection from the full event stream."""
        events = self._repository.get_events(aggregate_id)
        if not events:
            self._cache.pop(aggregate_id, None)
            self._versions.pop(aggregate_id, None)
            return
        state = BankAccount._fold(events)
        self._cache[aggregate_id] = state
        self._versions[aggregate_id] = events[-1].aggregate_version

    def get_state(self, aggregate_id: str) -> Optional[AccountState]:
        """Get current state from the projection cache (O(1), no replay)."""
        return self._cache.get(aggregate_id)


# ---------------------------------------------------------------------------
# Demo / sanity checks
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    repo = AccountRepository()
    projection = CachedAccountProjection(repo)
    repo.subscribe(projection)

    acct_id = "acct-1"
    account = BankAccount(acct_id, repo)

    account.create(initial_balance=100.0)
    account.deposit(50.0)
    state = account.withdraw(30.0)

    print("Aggregate state:", state)                  # balance 120
    print("Projection state:", projection.get_state(acct_id))
    assert state == projection.get_state(acct_id)

    # Insufficient funds
    try:
        account.withdraw(1000.0)
    except AccountException as e:
        print("Rejected:", e)

    # Double create
    try:
        BankAccount(acct_id, repo).create(10.0)
    except AccountException as e:
        print("Rejected:", e)

    print("History length:", len(account.get_history()))  # 3
```

## Design Decisions and Tradeoffs

**1. Immutable events (`frozen=True`)**
Events represent facts that have already happened, so they must never change. `frozen=True` enforces this at runtime. The base `Event` carries an `aggregate_version` providing **sequential, gap-free ordering** within each stream.

**2. Single reducer (`_apply_event`)**
Both the aggregate's full replay (`_fold`) and the projection's incremental update reuse the *same* pure function. This guarantees the read model and the aggregate can never diverge in how they interpret events — a common source of bugs in event-sourced systems.

**3. Optimistic concurrency in the repository**
`apply` requires `aggregate_version == len(stream) + 1`. This rejects out-of-order or duplicate writes and keeps the stream contiguous, which the projection relies on.

**4. Validation in commands, not in events**
Business rules (positive amounts, sufficient funds, single creation) are checked *before* emitting an event. This means **invalid events are never persisted** — the aggregate rejects events that would cause invalid state. The reducer also has a defensive check against overdrafts in case of a corrupted stream.

**5. Projection efficiency**
`get_state` on the projection is **O(1)** (cache lookup) versus the aggregate's **O(n)** full replay. The projection subscribes to the repository for live updates and applies events incrementally.

| Approach | Read cost | Memory |
|----------|-----------|--------|
| Aggregate `get_state` | O(n) replay | low |
| Projection `get_state` | O(1) | one state per aggregate |

## Edge Case Handling

- **Account already exists / doesn't exist** → `AccountException` on create/deposit/withdraw.
- **Non-positive deposit/withdraw amounts** → rejected.
- **Negative initial balance** → rejected.
- **Insufficient funds** → withdrawal rejected before emitting an event.
- **Empty stream** → `get_state` raises (no account to materialize).
- **Out-of-order / duplicate version** → repository rejects; projection is **idempotent** (ignores `version <= last`).
- **Gap in projection delivery** → projection **self-heals** via `rebuild` from the store.
- **First event not `AccountCreated`** → reducer raises, protecting against corrupted streams.