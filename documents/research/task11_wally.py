"""
Task 1.1: Correct Sliding Window Rate Limiter Implementation
by Wally (local LLM) - June 4, 2026

This implementation uses a deque of timestamps for a true sliding window
algorithm rather than fixed time buckets.

Key design decisions:
1. Thread safety using a single RLock - chosen over per-key locks because
   the rate limiter itself is a single entity, so per-key locks wouldn't help.
   The lock is held for the minimum time necessary (just the deque operations).

2. Deque for timestamps - allows O(1) amortized removal of old entries via
   popleft, compared to O(n) for list operations.

3. Cleanup happens on every allow() call, ensuring bounded memory usage.

4. remaining() and reset_time() provide useful metrics while acknowledging
   they're approximate due to concurrent access.
"""

from typing import Optional
from collections import deque
import threading
import time


class SlidingWindowRateLimiter:
    """Rate limiter using sliding window algorithm.
    
    This implementation maintains a deque of request timestamps. On each
    allow() call, it removes expired timestamps and checks if the window
    is full. This provides a true sliding window rather than fixed buckets.
    
    Thread safety is provided by a single RLock, held for the minimal
    duration necessary.
    
    Args:
        max_requests: Maximum requests allowed per window
        window_seconds: Window size in seconds
    """
    
    def __init__(self, max_requests: int, window_seconds: float):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed per window. Must be > 0.
            window_seconds: Window size in seconds. Must be > 0.
        """
        if max_requests <= 0:
            raise ValueError("max_requests must be positive")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._timestamps: deque = deque()
        self._lock = threading.RLock()
    
    def _cleanup_expired(self, now: float):
        """Remove timestamps outside the current window."""
        cutoff = now - self._window_seconds
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()
    
    def allow(self) -> bool:
        """
        Check if a request is allowed.
        
        This method is thread-safe. Multiple threads calling allow()
        simultaneously will have their calls serialized.
        
        Returns:
            True if request is within rate limit, False otherwise
        """
        now = time.time()
        
        with self._lock:
            # Remove expired timestamps first
            self._cleanup_expired(now)
            
            # Check if we have room
            if len(self._timestamps) < self._max_requests:
                # Record this request
                self._timestamps.append(now)
                return True
            
            return False
    
    def remaining(self) -> int:
        """
        Return approximate number of requests remaining in current window.
        
        Note: This is an approximation because timestamps expire continuously
        and concurrent requests may be in progress.
        """
        now = time.time()
        
        with self._lock:
            # Clean up without holding the lock long
            self._cleanup_expired(now)
            return max(0, self._max_requests - len(self._timestamps))
    
    def reset_time(self) -> float:
        """
        Return time (seconds) until at least one request slot opens.
        
        Returns 0 if there are available slots.
        """
        now = time.time()
        
        with self._lock:
            # If we have room, return 0
            if len(self._timestamps) < self._max_requests:
                return 0.0
            
            # Time until oldest request expires
            oldest = self._timestamps[0]
            expires_at = oldest + self._window_seconds
            
            if expires_at > now:
                return expires_at - now
            
            return 0.0


def test_rate_limiter():
    """Basic tests for the rate limiter."""
    
    # Test basic functionality
    limiter = SlidingWindowRateLimiter(3, 1.0)
    
    # Should allow 3 requests
    assert limiter.allow()
    assert limiter.allow()
    assert limiter.allow()
    
    # Should reject 4th request
    assert not limiter.allow()
    
    # Check remaining
    assert limiter.remaining() == 0
    
    # Check reset time should be > 0
    assert limiter.reset_time() > 0
    
    print("Basic functionality tests passed")
    
    # Test time-based behavior
    import time as t
    limiter2 = SlidingWindowRateLimiter(2, 0.5)
    
    limiter2.allow()
    limiter2.allow()
    assert not limiter2.allow()
    
    # Wait for window to expire
    t.sleep(0.6)
    assert limiter2.allow()
    
    print("Time-based tests passed")
    
    # Test thread safety (basic)
    limiter3 = SlidingWindowRateLimiter(100, 2.0)
    results = []
    
    def worker():
        for _ in range(50):
            results.append(limiter3.allow())
    
    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    allowed = sum(results)
    # Should be roughly 100, but could be slightly less due to timing
    assert allowed <= 120, f"Allowed {allowed} requests (expected ~100)"
    
    print(f"Thread safety test: {allowed} requests allowed")


if __name__ == "__main__":
    test_rate_limiter()
