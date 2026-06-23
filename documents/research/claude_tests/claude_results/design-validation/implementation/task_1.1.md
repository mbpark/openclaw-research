# Sliding Window Rate Limiter

## Implementation

```python
from typing import Optional
from collections import deque
import threading
import time


class SlidingWindowRateLimiter:
    """Rate limiter using a sliding window log algorithm.

    This implementation keeps a log of request timestamps and evicts any
    timestamp that has fallen outside the current window. A request is allowed
    only if the number of timestamps within the window is below ``max_requests``.

    Unlike a fixed-bucket approach (which can allow up to ``2 * max_requests``
    requests around a bucket boundary), this sliding window enforces the limit
    over *any* contiguous ``window_seconds`` interval.

    Thread safety:
        All mutating operations are guarded by a single lock. The critical
        section is kept minimal (only deque eviction + append), so contention
        is low. Amortized work per call is O(1): although eviction can pop
        multiple expired entries, each timestamp is appended once and popped
        once over its lifetime.
    """

    def __init__(self, max_requests: int, window_seconds: float):
        """Initialize the rate limiter.

        Args:
            max_requests: Maximum number of requests allowed within any
                window of ``window_seconds``. Must be a positive integer.
            window_seconds: Size of the sliding window in seconds. Must be
                a positive number.

        Raises:
            ValueError: If ``max_requests`` < 1 or ``window_seconds`` <= 0.
        """
        if max_requests < 1:
            raise ValueError("max_requests must be >= 1")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be > 0")

        self._max_requests: int = max_requests
        self._window: float = float(window_seconds)
        # Stores monotonic timestamps of allowed requests, oldest at left.
        self._timestamps: deque[float] = deque()
        self._lock = threading.Lock()

    def _now(self) -> float:
        """Return a monotonic clock reading.

        We use ``time.monotonic`` rather than ``time.time`` so the limiter is
        immune to wall-clock adjustments (NTP corrections, DST, manual changes).
        """
        return time.monotonic()

    def _evict(self, now: float) -> None:
        """Remove timestamps older than the current window.

        Must be called while holding ``self._lock``.

        Args:
            now: The current monotonic time.
        """
        cutoff = now - self._window
        ts = self._timestamps
        # Each timestamp is popped at most once across its lifetime,
        # making the amortized cost O(1) per allow() call.
        while ts and ts[0] <= cutoff:
            ts.popleft()

    def allow(self) -> bool:
        """Check if a request is allowed and, if so, record it.

        Returns:
            True if the request is within the rate limit (and has been
            recorded), False otherwise. When False, no timestamp is recorded.
        """
        now = self._now()
        with self._lock:
            self._evict(now)
            if len(self._timestamps) < self._max_requests:
                self._timestamps.append(now)
                return True
            return False

    def remaining(self) -> int:
        """Return the number of requests still allowed in the current window.

        This is a point-in-time snapshot; in a concurrent setting the value
        may be stale by the time the caller acts on it.

        Returns:
            An integer in the range ``[0, max_requests]``.
        """
        now = self._now()
        with self._lock:
            self._evict(now)
            return self._max_requests - len(self._timestamps)

    def reset_time(self) -> float:
        """Return seconds until at least one request slot opens up.

        If a slot is currently available, returns ``0.0``. Otherwise returns
        the time until the oldest in-window timestamp expires (i.e. when it
        slides out of the window).

        Returns:
            Non-negative number of seconds.
        """
        now = self._now()
        with self._lock:
            self._evict(now)
            if len(self._timestamps) < self._max_requests:
                return 0.0
            # The oldest timestamp expires at oldest + window.
            oldest = self._timestamps[0]
            wait = (oldest + self._window) - now
            return max(0.0, wait)
```

## Design Decisions & Tradeoffs

### 1. Algorithm: Sliding Window Log
I store an explicit **deque of timestamps**. A request is allowed iff fewer than `max_requests` timestamps lie within `[now - window, now]`.

- **Correctness**: Enforces the limit over *any* sliding interval. A fixed-bucket counter can let `2 * max_requests` through at a boundary (e.g., `max` requests at end of bucket 1, `max` at start of bucket 2 — only milliseconds apart).
- **Tradeoff**: Memory is O(max_requests) — we keep one timestamp per live request. The popular alternative (sliding window *counter*, blending two fixed buckets) uses O(1) memory but is only an approximation. Given the task explicitly forbids fixed buckets and demands true sliding behavior, the log is the right choice.

### 2. Complexity: Amortized O(1)
`_evict` uses `deque.popleft()` in a loop. While a single call can pop many entries, **each timestamp is appended exactly once and popped exactly once** over its lifetime. Total work across `k` calls is O(k), so amortized cost per call is O(1). (No `O(log n)` structure or binary search is needed because eviction is always from the front.)

### 3. Thread Safety: Single Lock, Minimal Critical Section
- A single `threading.Lock` guards all reads/writes of the deque.
- The check-and-record (`evict → compare → append`) happens **atomically** inside the lock. This is what prevents the classic race where two threads both read `count < max` and both append, exceeding the limit.
- The critical section is tiny (deque ops only — no I/O, no sleeping), keeping contention low.

### 4. Clock: `time.monotonic()`
Using a monotonic clock avoids bugs from wall-clock jumps (NTP sync, manual time changes) that could either wrongly expire or wrongly retain timestamps.

## Edge Case Handling

| Case | Behavior |
|------|----------|
| `max_requests < 1` or `window_seconds <= 0` | Raises `ValueError` at construction. |
| Burst at window boundary | True sliding behavior — old timestamps must fully exit the window before new slots open. |
| `remaining()` / `reset_time()` are racy | Documented as point-in-time snapshots; only `allow()` is authoritative. |
| All slots full | `reset_time()` returns time until the *oldest* entry slides out (`oldest + window - now`), clamped to `≥ 0`. |
| Rejected request | When `allow()` returns `False`, **no timestamp is recorded**, so rejected attempts don't extend the busy period. |
| `reset_time` slightly negative due to timing | Clamped with `max(0.0, ...)`. |

## Quick Verification

```python
def test_basic():
    rl = SlidingWindowRateLimiter(max_requests=3, window_seconds=1.0)
    assert [rl.allow() for _ in range(5)] == [True, True, True, False, False]
    assert rl.remaining() == 0
    assert 0 < rl.reset_time() <= 1.0
    time.sleep(1.05)
    assert rl.allow() is True  # window slid, slot freed


def test_concurrency():
    rl = SlidingWindowRateLimiter(max_requests=100, window_seconds=10.0)
    allowed = []
    lock = threading.Lock()

    def worker():
        if rl.allow():
            with lock:
                allowed.append(1)

    threads = [threading.Thread(target=worker) for _ in range(1000)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert sum(allowed) == 100  # never exceeds limit, even under contention


test_basic()
test_concurrency()
print("All tests passed.")
```

**Note on the GIL:** While CPython's GIL serializes bytecode, it does *not* make compound check-then-act operations atomic across threads — the interpreter can switch threads between the length check and the append. The explicit lock is genuinely required for correctness (and ensures correctness under free-threaded / no-GIL Python too).