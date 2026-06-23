# Sliding Window Rate Limiter

## Implementation

```python
from typing import Optional, Deque
from collections import deque
import threading
import time


class SlidingWindowRateLimiter:
    """Rate limiter using a true sliding window (log) algorithm.

    Tracks individual request timestamps in a monotonic-time-ordered deque.
    A request is allowed if the number of timestamps within the trailing
    `window_seconds` window is strictly less than `max_requests`.

    Thread-safe: all mutations and reads of shared state happen under a lock.
    """

    def __init__(self, max_requests: int, window_seconds: float):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed per window (must be >= 0).
            window_seconds: Window size in seconds (must be > 0).

        Raises:
            ValueError: If max_requests < 0 or window_seconds <= 0.
        """
        if max_requests < 0:
            raise ValueError("max_requests must be >= 0")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be > 0")

        self._max_requests: int = max_requests
        self._window: float = window_seconds
        # Timestamps (monotonic clock) of accepted requests, oldest at left.
        self._timestamps: Deque[float] = deque()
        self._lock = threading.Lock()

    def _now(self) -> float:
        """Return current monotonic time (immune to wall-clock adjustments)."""
        return time.monotonic()

    def _evict(self, now: float) -> None:
        """Remove timestamps older than the sliding window.

        Must be called while holding the lock. Amortized O(1) per request:
        each timestamp is appended once and popped at most once.

        Args:
            now: Current monotonic time.
        """
        cutoff = now - self._window
        ts = self._timestamps
        # popleft of expired entries; total pops bounded by total appends.
        while ts and ts[0] <= cutoff:
            ts.popleft()

    def allow(self) -> bool:
        """
        Check if a request is allowed and, if so, record it.

        Returns:
            True if request is within rate limit (and is recorded),
            False otherwise (nothing is recorded).
        """
        if self._max_requests == 0:
            return False

        with self._lock:
            now = self._now()
            self._evict(now)
            if len(self._timestamps) < self._max_requests:
                self._timestamps.append(now)
                return True
            return False

    def remaining(self) -> int:
        """Return approximate number of requests remaining in current window.

        Returns:
            Number of additional requests that would currently be accepted.
            Always in range [0, max_requests].
        """
        with self._lock:
            now = self._now()
            self._evict(now)
            return max(0, self._max_requests - len(self._timestamps))

    def reset_time(self) -> float:
        """Return time (seconds) until at least one request slot opens.

        Returns:
            0.0 if a slot is currently available; otherwise the number of
            seconds until the oldest in-window request expires.
        """
        with self._lock:
            now = self._now()
            self._evict(now)
            if len(self._timestamps) < self._max_requests:
                return 0.0
            # The oldest timestamp expires at oldest + window.
            oldest = self._timestamps[0]
            wait = (oldest + self._window) - now
            return max(0.0, wait)
```

---

## Design Decisions and Tradeoffs

### 1. Algorithm: Sliding Window Log (not fixed buckets)

I store the **exact timestamp of every accepted request** in a `deque`. A request is allowed iff the count of timestamps within `(now - window, now]` is below `max_requests`. This is a *true* sliding window — the window moves continuously with each call, unlike fixed buckets that flush at boundaries and permit up to 2× the limit at boundary edges.

**Tradeoff:** Memory is O(max_requests) — we store one timestamp per active request. The alternative "sliding window counter" approximation (weighting the previous fixed bucket) uses O(1) memory but is *approximate*. Since the task emphasizes correctness over the boundary-burst problem, the log approach is the right exact solution.

### 2. Monotonic clock

I use `time.monotonic()` instead of `time.time()`. Wall-clock time can jump backward (NTP corrections, manual changes), which would corrupt eviction logic and produce negative `reset_time`. Monotonic time only ever increases.

### 3. Thread safety with a single lock

All state access goes through one `threading.Lock`. The critical section is tiny (a deque eviction + append/length check), so contention is minimal in practice.

- I considered lock-free / striped approaches, but with a shared global counter limit, any correct implementation must serialize the *check-then-record* step. Splitting it would create a TOCTOU race allowing the limit to be exceeded.
- The `allow()` check and the `append()` happen atomically under the lock — this is the key to the concurrent-correctness requirement.

### 4. Amortized O(1) eviction

The `while` loop in `_evict` looks like O(n), but it's **amortized O(1)**: each timestamp is `append`ed exactly once and `popleft`'d at most once over its lifetime. `deque` gives O(1) at both ends. (A log-structured exact window is inherently O(active requests) memory; with the sorted-by-insertion invariant we avoid any per-call sort or scan beyond eviction.)

### 5. `remaining()` and `reset_time()` semantics

- `remaining()` evicts first, then returns `max_requests - active_count`, clamped to `[0, max_requests]`.
- `reset_time()` returns `0.0` when a slot is free; otherwise it computes when the **oldest** request expires (`oldest + window - now`), since freeing that slot is the soonest a new request becomes possible.

---

## Edge Case Handling

| Case | Behavior |
|------|----------|
| `max_requests == 0` | `allow()` always returns `False`; short-circuits before locking. `remaining()` returns 0; `reset_time()` returns `inf`-free path returns... see note below. |
| `max_requests < 0` | Raises `ValueError` in constructor. |
| `window_seconds <= 0` | Raises `ValueError` (a zero/negative window is meaningless). |
| Clock going backward | Avoided entirely via `time.monotonic()`. |
| Memory growth | Bounded by `max_requests`; eviction runs on every public call. No unbounded leak. |
| Rejected request | Not recorded — only accepted requests consume a slot, so rejected bursts don't extend the window. |
| `reset_time` when slot free | Returns `0.0`. |
| Floating-point near-zero wait | `max(0.0, ...)` clamps tiny negatives from float arithmetic. |

> **Note on `max_requests == 0` + `reset_time()`:** With zero capacity, no slot ever opens. The current code would return `0.0` (since `len(timestamps) < 0` is `False`... actually `0 < 0` is `False`, so it falls through to `self._timestamps[0]` which is empty → `IndexError`).

Let me fix that edge case explicitly:

```python
    def reset_time(self) -> float:
        """Return time (seconds) until at least one request slot opens."""
        with self._lock:
            now = self._now()
            self._evict(now)
            if self._max_requests == 0:
                return float("inf")  # no slot will ever open
            if len(self._timestamps) < self._max_requests:
                return 0.0
            oldest = self._timestamps[0]
            return max(0.0, (oldest + self._window) - now)
```

---

## Quick Verification

```python
import time

def demo() -> None:
    rl = SlidingWindowRateLimiter(max_requests=3, window_seconds=1.0)
    assert rl.allow() and rl.allow() and rl.allow()  # 3 ok
    assert not rl.allow()                              # 4th blocked
    assert rl.remaining() == 0
    assert 0 < rl.reset_time() <= 1.0
    time.sleep(1.05)                                   # window slides
    assert rl.remaining() == 3
    assert rl.allow()

    # Concurrency check
    import threading
    rl2 = SlidingWindowRateLimiter(100, 10.0)
    accepted = []
    lock = threading.Lock()
    def worker():
        if rl2.allow():
            with lock:
                accepted.append(1)
    threads = [threading.Thread(target=worker) for _ in range(1000)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert sum(accepted) == 100, sum(accepted)  # never exceeds limit
    print("All checks passed.")

demo()
```

This guarantees the limit is never exceeded under heavy concurrency, uses a genuine sliding window, evicts old entries in amortized O(1), and bounds memory to `max_requests`.