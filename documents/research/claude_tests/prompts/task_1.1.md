You are an expert software engineer completing an implementation challenge.
Please provide:
1. Complete, runnable code with proper type hints and docstrings
2. Explanation of design decisions and tradeoffs
3. Edge case handling

## Task 1.1: Correct Sliding Window Rate Limiter

Implement a rate limiter that allows at most N requests per time window. Must use a *sliding window* approach, not fixed time buckets.

**Concurrent correctness requirement:** Multiple threads must not exceed the limit, even when calling allow() simultaneously.

**Interface:**

from typing import Optional
import threading
import time


class SlidingWindowRateLimiter:
    """Rate limiter using sliding window algorithm."""
    
    def __init__(self, max_requests: int, window_seconds: float):
        """
        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Window size in seconds
        """
        ...
    
    def allow(self) -> bool:
        """
        Check if a request is allowed.
        
        Returns:
            True if request is within rate limit, False otherwise
        """
        ...
    
    def remaining(self) -> int:
        """Return approximate number of requests remaining in current window."""
        ...
    
    def reset_time(self) -> float:
        """Return time (seconds) until at least one request slot opens."""
        ...

**What to evaluate:**
- Correct sliding window implementation (timestamp-based, not fixed buckets)
- Thread safety with minimal contention
- O(1) or O(log n) amortized time per allow() call
- Memory management: old timestamps are cleaned up
- Correct remaining() and reset_time() calculations

**Common wrong approaches:**
- Fixed time buckets (precompute, flush at boundaries)
- Not thread-safe
- O(n) linear scan per call
- Memory leak from never cleaning old entries
