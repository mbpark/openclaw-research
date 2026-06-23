# Sliding Window Rate Limiter

## Implementation

```python
from typing import Optional, Deque
from collections import deque
import threading
import time


class SlidingWindowRateLimiter:
    """Rate limiter using a sliding window (timestamp log) algorithm.

    This limiter tracks the exact timestamps of recent requests in a
    monotonic deque. A request is permitted only if the number of
    timestamps within the trailing `window_seconds` is below `max_requests`.

    Unlike fixed-window counters, this approach has no boundary burst
    problem: at no point in time will more than `max_requests` be allowed
    in any rolling `window_seconds` interval.

    Thread safety is provided by an internal lock. All public methods are
    safe to call concurrently from multiple threads.
    """

    def __init__(self, max_requests: int, window_seconds: float):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed per window. Must be >= 0.
            window_seconds: Window size in seconds. Must be > 0.

        Raises:
            ValueError: If arguments are out of valid range.
        """
        if max_requests < 0:
            raise ValueError("max_requests must be non-negative")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")

        self._max_requests: int = max_requests
        self._window: float = window_seconds
        # Monotonically increasing timestamps of allowed requests.
        # Oldest at the left, newest at the right.
        self._timestamps: Deque[float] = deque()
        self._lock = threading.Lock()

    def _now(self) -> float:
        """Return current time from a monotonic clock.

        We use time.monotonic() rather than time.time() so the limiter is
        immune to wall-clock adjustments (NTP, manual changes, DST, etc.).
        """
        return time.monotonic()

    def _evict(self, now: float) -> None:
        """Remove timestamps that have fallen out of the sliding window.

        Caller must hold the lock. Amortized O(1) per request: each
        timestamp is appended once and popped once over its lifetime.

        Args:
            now: Current monotonic time.
        """
        cutoff = now - self._window
        # popleft is O(1); total evictions bounded by total appends.
        ts = self._timestamps
        while ts and ts[0] <= cutoff:
            ts.popleft()

    def allow(self) -> bool:
        """Check if a request is allowed, and record it if so.

        Returns:
            True if request is within the rate limit (and is recorded),
            False otherwise (nothing is recorded).
        """
        now = self._now()
        with self._lock:
            self._evict(now)
            if len(self._timestamps) < self._max_requests:
                self._timestamps.append(now)
                return True
            return False

    def remaining(self) -> int:
        """Return the number of requests remaining in the current window.

        Returns:
            An integer in [0, max_requests]. This is a snapshot in time;
            concurrent calls may change it immediately afterward.
        """
        now = self._now()
        with self._lock:
            self._evict(now)
            return self._max_requests - len(self._timestamps)

    def reset_time(self) -> float:
        """Return seconds until at least one request slot opens up.

        Returns:
            0.0 if a slot is currently available. Otherwise the time until
            the oldest in-window timestamp ages out of the window.
        """
        now = self._now()
        with self._lock:
            self._evict(now)
            if len(self._timestamps) < self._max_requests:
                return 0.0
            # The slot opens when the oldest timestamp exits the window.
            oldest = self._timestamps[0]
            wait = (oldest + self._window) - now
            return max(0.0, wait)
```

## Design Decisions & Tradeoffs

### Algorithm: Timestamp Log (true sliding window)
I store the **actual timestamp of each allowed request** in a `deque`. A request is permitted iff the count of timestamps newer than `now - window` is below the limit. This is the canonical sliding-window-log algorithm and is *exact* — it never allows boundary bursts that a fixed-bucket counter would.

### Why `deque`?
- `append()` (right) and `popleft()` (left) are both **O(1)**.
- Timestamps are naturally sorted because `monotonic()` is non-decreasing, so eviction only needs to check the front.

### Amortized O(1) per `allow()`
The `_evict` loop looks like it could be O(n), but each timestamp is appended exactly once and popped exactly once over its entire lifetime. Across any sequence of `k` calls, total eviction work is bounded by total appends — yielding **amortized O(1)** per call. This satisfies the complexity requirement.

### Memory management
`_evict` runs on every public call, so timestamps older than the window are continuously reclaimed. Peak memory is bounded by `O(max_requests)` (you can never have more in-window entries than the limit, plus transient stale ones cleaned on next access).

> **Note on idle leak:** If `allow()` is never called again, stale entries persist until the next call. This is acceptable because peak memory is still bounded by `max_requests` and entries are cleaned lazily. A background sweeper would add complexity and contention for no correctness benefit.

### Thread safety: single lock
I use **one `threading.Lock`** guarding the deque. The critical section is tiny (eviction + length check + append), so contention is low. Crucially, the **check-and-record in `allow()` is atomic**, which is what prevents two threads from both seeing `len < max` and both being admitted past the limit — the classic TOCTOU bug.

I deliberately avoided lock-free approaches (e.g., atomics) because correct concurrent eviction + bounded count requires coordinating multiple operations; a lock is simpler and correct.

### Monotonic clock
`time.monotonic()` instead of `time.time()` ensures the limiter cannot be broken by clock adjustments (NTP slew, manual changes). Durations remain meaningful.

## Edge Case Handling

| Edge case | Behavior |
|-----------|----------|
| `max_requests = 0` | `allow()` always returns `False`; `remaining()` returns 0; `reset_time()` returns `inf`-ish... actually returns `0.0` because `len(0) < 0` is False but deque is empty — see note below. |
| `window_seconds <= 0` | Rejected in `__init__` with `ValueError`. |
| Negative `max_requests` | Rejected with `ValueError`. |
| All slots full | `reset_time()` returns positive wait based on oldest timestamp. |
| Slots available | `reset_time()` returns `0.0`. |
| Concurrent `allow()` | Atomic check-and-set under lock prevents over-admission. |
| Clock jumps | Immune via `monotonic()`. |

### `max_requests = 0` subtlety
When `max_requests == 0`, `allow()` always returns `False` (nothing is ever appended). `reset_time()` returns `0.0` because the deque stays empty so `len < 0` is `False`... wait — `len([]) == 0 < 0` is `False`, so we fall through to access `self._timestamps[0]` on an empty deque → **IndexError**. Let me guard this:

```python
    def reset_time(self) -> float:
        """Return seconds until at least one request slot opens up."""
        now = self._now()
        with self._lock:
            self._evict(now)
            # If limit is 0, no slot ever opens.
            if self._max_requests == 0:
                return float("inf")
            if len(self._timestamps) < self._max_requests:
                return 0.0
            oldest = self._timestamps[0]
            return max(0.0, (oldest + self._window) - now)
```

This corrected version returns `inf` for the degenerate `max_requests=0` case, which is semantically correct (a slot never opens).

## Quick Verification

```python
def _demo() -> None:
    rl = SlidingWindowRateLimiter(max_requests=3, window_seconds=1.0)
    assert all(rl.allow() for _ in range(3))   # first 3 allowed
    assert not rl.allow()                       # 4th blocked
    assert rl.remaining() == 0
    assert rl.reset_time() > 0
    time.sleep(1.05)
    assert rl.allow()                           # window slid, slot freed
    print("OK")


def _concurrency_test() -> None:
    rl = SlidingWindowRateLimiter(max_requests=100, window_seconds=10.0)
    results = []
    lock = threading.Lock()

    def worker() -> None:
        r = rl.allow()
        with lock:
            results.append(r)

    threads = [threading.Thread(target=worker) for _ in range(1000)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Never more than the limit admitted.
    assert sum(results) == 100, sum(results)
    print("Concurrency OK")


if __name__ == "__main__":
    _demo()
    _concurrency_test()
```

The concurrency test launches 1000 threads against a limit of 100 and asserts **exactly 100** are admitted — confirming no over-admission under contention.