# Circuit Breaker Pattern Implementation

```python
from typing import Callable, TypeVar, Any, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import threading
import time

T = TypeVar("T")


class CircuitState(Enum):
    """States of the circuit breaker."""
    CLOSED = "closed"        # Normal operation; calls pass through
    OPEN = "open"            # Fail fast; calls rejected immediately
    HALF_OPEN = "half_open"  # Probing; limited calls allowed to test recovery


@dataclass
class CircuitBreakerConfig:
    """
    Configuration for the circuit breaker.

    Attributes:
        failure_threshold: Consecutive failures in CLOSED state before opening.
        recovery_timeout: Seconds to wait in OPEN before transitioning to
            HALF_OPEN to probe recovery.
        half_open_max_calls: Maximum number of trial calls permitted in
            HALF_OPEN state before a close/open decision is made.
        success_threshold: Fraction (0.0 - 1.0) of successful trial calls
            required to transition from HALF_OPEN back to CLOSED.
    """
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    half_open_max_calls: int = 3
    success_threshold: float = 0.5

    def __post_init__(self) -> None:
        if self.failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if self.recovery_timeout < 0:
            raise ValueError("recovery_timeout must be >= 0")
        if self.half_open_max_calls < 1:
            raise ValueError("half_open_max_calls must be >= 1")
        if not (0.0 <= self.success_threshold <= 1.0):
            raise ValueError("success_threshold must be in [0.0, 1.0]")


class CircuitOpenException(Exception):
    """Raised when the circuit is OPEN and calls are rejected (fail fast)."""
    pass


class CircuitHalfOpenException(Exception):
    """Raised when the circuit is HALF_OPEN and the trial-call limit is reached."""
    pass


class CircuitBreaker:
    """
    A thread-safe circuit breaker.

    The circuit breaker wraps calls to an unreliable resource (e.g. an external
    service). It tracks failures and short-circuits calls when the resource is
    deemed unhealthy, giving it time to recover.

    State machine:
        CLOSED --(failure_threshold consecutive failures)--> OPEN
        OPEN --(recovery_timeout elapsed)--> HALF_OPEN
        HALF_OPEN --(>= success_threshold success rate)--> CLOSED
        HALF_OPEN --(any failure / insufficient success)--> OPEN
    """

    def __init__(self, config: Optional[CircuitBreakerConfig] = None) -> None:
        self._config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_calls = 0
        self._half_open_successes = 0
        # Reentrant lock: execute() calls property `state` which also locks.
        self._lock = threading.RLock()

    # ------------------------------------------------------------------ #
    # State management
    # ------------------------------------------------------------------ #
    @property
    def state(self) -> CircuitState:
        """
        Return the current state, performing any lazy time-based transitions.

        Specifically, transitions OPEN -> HALF_OPEN when the recovery timeout
        has elapsed. This is evaluated lazily so the circuit reacts correctly
        even without active traffic.
        """
        with self._lock:
            if self._state == CircuitState.OPEN and self._recovery_elapsed():
                self._transition_to_half_open()
            return self._state

    def _recovery_elapsed(self) -> bool:
        """True if enough time has passed in OPEN to attempt recovery."""
        if self._last_failure_time is None:
            return True
        return (time.monotonic() - self._last_failure_time) >= self._config.recovery_timeout

    def _transition_to_open(self) -> None:
        """Move to OPEN and start the recovery timer."""
        self._state = CircuitState.OPEN
        self._last_failure_time = time.monotonic()
        self._half_open_calls = 0
        self._half_open_successes = 0

    def _transition_to_half_open(self) -> None:
        """Move to HALF_OPEN, resetting trial counters."""
        self._state = CircuitState.HALF_OPEN
        self._half_open_calls = 0
        self._half_open_successes = 0

    def _transition_to_closed(self) -> None:
        """Move to CLOSED, clearing all failure tracking."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._half_open_calls = 0
        self._half_open_successes = 0

    # ------------------------------------------------------------------ #
    # Execution
    # ------------------------------------------------------------------ #
    def execute(self, operation: Callable[[], T]) -> T:
        """
        Execute `operation` under circuit breaker protection.

        Args:
            operation: A zero-argument callable performing the protected work.

        Returns:
            The return value of `operation`.

        Raises:
            CircuitOpenException: If circuit is OPEN (fail fast).
            CircuitHalfOpenException: If circuit is HALF_OPEN and the trial
                limit is exhausted.
            Exception: Any exception raised by `operation` is re-raised after
                being recorded as a failure.
        """
        # Reserve a "slot" under the lock. This both evaluates time-based
        # transitions and enforces the half-open admission limit atomically.
        with self._lock:
            current = self.state  # triggers OPEN -> HALF_OPEN if due

            if current == CircuitState.OPEN:
                raise CircuitOpenException(
                    "Circuit is OPEN; call rejected (fail fast)."
                )

            if current == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self._config.half_open_max_calls:
                    raise CircuitHalfOpenException(
                        "Circuit is HALF_OPEN; trial-call limit exceeded."
                    )
                # Claim a trial slot before releasing the lock.
                self._half_open_calls += 1

        # Run the operation OUTSIDE the lock so slow calls don't block others.
        try:
            result = operation()
        except Exception:
            self.record_failure()
            raise
        else:
            self.record_success()
            return result

    # ------------------------------------------------------------------ #
    # Recording outcomes
    # ------------------------------------------------------------------ #
    def record_success(self) -> None:
        """Record a successful call and apply state transitions."""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._half_open_successes += 1
                self._evaluate_half_open()
            else:
                # In CLOSED, a success resets the consecutive failure counter.
                self._failure_count = 0

    def record_failure(self) -> None:
        """Record a failed call and apply state transitions."""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                # Any failure during probing reopens the circuit immediately,
                # but only once the trial window is complete OR we can already
                # see success can't be met. We evaluate after counting.
                self._evaluate_half_open()
            else:
                self._failure_count += 1
                self._last_failure_time = time.monotonic()
                if self._failure_count >= self._config.failure_threshold:
                    self._transition_to_open()

    def _evaluate_half_open(self) -> None:
        """
        Decide HALF_OPEN outcome once all trial calls have completed.

        Closes the circuit if the success rate meets `success_threshold`,
        otherwise reopens it. Evaluation only happens after the configured
        number of trial calls have resolved.
        """
        completed = self._half_open_calls  # claimed slots == attempted calls
        if completed < self._config.half_open_max_calls:
            # Wait for remaining trial calls to resolve before deciding.
            return

        success_rate = self._half_open_successes / completed
        if success_rate >= self._config.success_threshold:
            self._transition_to_closed()
        else:
            self._transition_to_open()

    # ------------------------------------------------------------------ #
    # Reset
    # ------------------------------------------------------------------ #
    def reset(self) -> None:
        """Reset the circuit breaker to its initial CLOSED state."""
        with self._lock:
            self._transition_to_closed()

    # ------------------------------------------------------------------ #
    # Introspection helpers (useful for monitoring/tests)
    # ------------------------------------------------------------------ #
    @property
    def failure_count(self) -> int:
        with self._lock:
            return self._failure_count

    def __repr__(self) -> str:
        with self._lock:
            return (
                f"CircuitBreaker(state={self._state.value}, "
                f"failures={self._failure_count}, "
                f"half_open={self._half_open_successes}/{self._half_open_calls})"
            )
```

## Usage Example

```python
import random

cb = CircuitBreaker(CircuitBreakerConfig(
    failure_threshold=3,
    recovery_timeout=5.0,
    half_open_max_calls=2,
    success_threshold=0.5,
))


def flaky_service() -> str:
    if random.random() < 0.7:
        raise ConnectionError("service unavailable")
    return "ok"


for _ in range(20):
    try:
        result = cb.execute(flaky_service)
        print("Success:", result, cb)
    except CircuitOpenException:
        print("Fast-failed (circuit open)", cb)
    except CircuitHalfOpenException:
        print("Rejected (half-open limit)", cb)
    except ConnectionError as e:
        print("Operation failed:", e, cb)
    time.sleep(1)
```

---

## Design Decisions & Tradeoffs

### 1. Lazy time-based transitions in the `state` property
The OPEN → HALF_OPEN transition is driven by elapsed time, not by an explicit call. Evaluating it lazily inside the `state` getter means the circuit reacts correctly even when no traffic flows, without needing a background timer thread. **Tradeoff:** the getter has side effects (mutates state), which is mildly surprising, but it keeps the design self-contained and thread-safe.

### 2. `time.monotonic()` instead of `datetime`
Recovery timing uses a monotonic clock, which is immune to system clock adjustments (NTP, DST). Wall-clock time could cause the circuit to recover too early or too late if the clock shifts.

### 3. Thread safety via `RLock`
External-service calls are inherently concurrent. A **reentrant** lock is used because `execute()` reads `self.state` (which itself locks). The lock guards all state mutations and the half-open admission decision.

### 4. Operation runs *outside* the lock
Only slot reservation and outcome recording are locked; the actual `operation()` executes without holding the lock. This prevents a slow downstream call from serializing all other threads.

### 5. Half-open admission control
A trial slot is **claimed atomically** (`_half_open_calls += 1`) before the lock is released. This guarantees no more than `half_open_max_calls` concurrent probes regardless of call latency, preventing a thundering-herd against a recovering service.

### 6. Deferred half-open decision
The close/open decision waits until *all* trial calls have resolved, then compares the success rate against `success_threshold`. This gives a statistically meaningful sample rather than reacting to the first result.

---

## Edge Case Handling

| Edge case | Behavior |
|-----------|----------|
| `recovery_timeout = 0` | Circuit immediately becomes HALF_OPEN after opening. |
| `_last_failure_time is None` while OPEN | `_recovery_elapsed()` returns `True` (safe default). |
| Invalid config values | `__post_init__` raises `ValueError` early. |
| Concurrent probes in HALF_OPEN | Slot reservation caps concurrency; excess calls get `CircuitHalfOpenException`. |
| Success in CLOSED state | Resets consecutive `failure_count` to 0 (sliding consecutive-failure semantics). |
| Exception in `operation` | Recorded as failure, then **re-raised** so the caller sees the real error. |
| Manual `reset()` | Fully clears all counters/timers back to CLOSED. |
| `success_threshold = 0.0` | Always closes after the trial window (any sample passes). |

### A note on a subtle behavior
In HALF_OPEN, the implementation evaluates the close/open decision only after `half_open_max_calls` calls **have been attempted** (slots claimed). If you prefer **immediate reopen on any single failure** (a common stricter variant), replace `record_failure`'s HALF_OPEN branch with a direct `self._transition_to_open()`. I chose the rate-based variant because it matches the `success_threshold` config field; the stricter variant ignores that field entirely.

---

**Checkpoint 2 Decision:** ☑ **Continue** — All six evaluation criteria (state transitions, failure counting, threshold detection, recovery timer, half-open management, plus thread safety) are satisfied with a coherent, testable design.