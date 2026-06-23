"""
Comprehensive verification tests for Task 1.1 Rate Limiter
"""

import threading
import time
from collections import deque
from collections import defaultdict


def test_sliding_vs_fixed():
    """
    Verify true sliding window behavior.
    
    In a fixed bucket system with 3 requests/1s window:
    - 3 requests at t=0 pass
    - 3 requests at t=0.99 pass (same bucket, not allowed)
    - At t=1.0 exactly, bucket resets
    - 3 more requests pass
    
    In a true sliding window:
    - 3 requests at t=0 pass
    - At t=0.99, still 0 remaining (all 3 still in window)
    - At t=1.001, requests from t=0 have expired
    - 3 more requests pass
    
    The key difference: sliding window spreads out usage, fixed buckets
    allow bursts.
    """
    import task11_wally
    limiter = task11_wally.SlidingWindowRateLimiter(3, 1.0)
    
    # Consume all requests
    limiter.allow()
    limiter.allow()
    limiter.allow()
    
    # Should be rejected
    start = time.time()
    assert not limiter.allow()
    
    # Wait just short of window
    time.sleep(0.99)
    # Should still be rejected
    assert not limiter.allow()
    
    # Wait for window to expire
    time.sleep(0.02)
    # Should be allowed now
    assert limiter.allow()
    
    end = time.time()
    print(f"Sliding window test passed (took {end-start:.2f}s)")


def test_performance():
    """Measure per-operation performance."""
    import task11_wally
    import statistics
    
    # Create limiter with large limit to avoid rejection affecting timing
    limiter = task11_wally.SlidingWindowRateLimiter(10000, 10.0)
    
    # Warmup
    for _ in range(100):
        limiter.allow()
    
    # Measure allow() performance
    times = []
    iterations = 10000
    
    for _ in range(iterations):
        start = time.perf_counter()
        limiter.allow()
        end = time.perf_counter()
        times.append(end - start)
    
    print(f"\nPerformance test (n={iterations}):")
    print(f"  Mean: {statistics.mean(times) * 1e6:.2f}μs")
    print(f"  Median: {statistics.median(times) * 1e6:.2f}μs")
    print(f"  99th percentile: {sorted(times)[int(len(times)*0.99)] * 1e6:.2f}μs")
    
    # Should be microseconds, not milliseconds
    assert statistics.mean(times) < 0.0001, "Performance too slow"


def test_memory_bounded():
    """Verify memory usage stays bounded."""
    import task11_wally
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    
    # Create small window limiter
    limiter = task11_wally.SlidingWindowRateLimiter(100, 0.1)
    
    initial_mem = process.memory_info().rss
    
    # Rapidly call for a while
    for _ in range(100000):
        limiter.allow()
        time.sleep(0.00001)  # Small delay to let timestamps differ
    
    final_mem = process.memory_info().rss
    mem_growth = (final_mem - initial_mem) / 1024
    
    print(f"\nMemory test:")
    print(f"  Initial: {initial_mem / 1024:.1f} KB")
    print(f"  Final: {final_mem / 1024:.1f} KB")
    print(f"  Growth: {mem_growth:.1f} KB")
    
    # Should be very small (just a few KB for the deque)
    assert mem_growth < 100, f"Memory grew too much: {mem_growth:.1f} KB"


def test_concurrent_correctness():
    """
    Stress test for concurrent correctness.
    """
    import task11_wally
    
    # Create limiter with known limit
    max_requests = 1000
    limiter = task11_wally.SlidingWindowRateLimiter(max_requests, 2.0)
    
    # Track results with thread safety
    allowed_count = [0]
    denied_count = [0]
    count_lock = threading.Lock()
    
    def worker():
        local_allowed = 0
        local_denied = 0
        
        for _ in range(1000):
            if limiter.allow():
                local_allowed += 1
            else:
                local_denied += 1
        
        with count_lock:
            allowed_count[0] += local_allowed
            denied_count[0] += local_denied
    
    # Create many threads
    threads = [threading.Thread(target=worker) for _ in range(20)]
    
    start = time.time()
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    elapsed = time.time() - start
    
    print(f"\nConcurrency stress test:")
    print(f"  Threads: 20")
    print(f"  Duration: {elapsed:.2f}s")
    print(f"  Allowed: {allowed_count[0]} (limit: {max_requests})")
    print(f"  Denied: {denied_count[0]}")
    
    # With true thread safety, allowed should be <= max_requests
    # Allow small tolerance for timing edge cases
    assert allowed_count[0] <= max_requests + 5, \
        f"Allowed {allowed_count[0]} but limit is {max_requests}"


def run_all_tests():
    print("=== Task 1.1 Rate Limiter Comprehensive Tests ===\n")
    
    print("1. Sliding vs Fixed Window Test:")
    test_sliding_vs_fixed()
    
    print("\n2. Performance Test:")
    test_performance()
    
    print("\n3. Memory Bounded Test:")
    test_memory_bounded()
    
    print("\n4. Concurrency Correctness Test:")
    test_concurrent_correctness()
    
    print("\n=== All comprehensive tests passed ===")


if __name__ == "__main__":
    run_all_tests()
