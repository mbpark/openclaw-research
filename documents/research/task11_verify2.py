"""
Comprehensive verification tests for Task 1.1 Rate Limiter
(Minimal dependencies version)
"""

import threading
import time
import os


def test_sliding_vs_fixed():
    """Verify true sliding window behavior."""
    import task11_wally
    limiter = task11_wally.SlidingWindowRateLimiter(3, 1.0)
    
    limiter.allow()
    limiter.allow()
    limiter.allow()
    assert not limiter.allow()
    
    time.sleep(0.99)
    assert not limiter.allow()
    
    time.sleep(0.02)
    assert limiter.allow()
    
    print("✓ Sliding window test passed")


def test_performance():
    """Measure per-operation performance."""
    import task11_wally
    import statistics
    
    limiter = task11_wally.SlidingWindowRateLimiter(10000, 10.0)
    
    for _ in range(100):
        limiter.allow()
    
    times = []
    
    for _ in range(10000):
        start = time.perf_counter()
        limiter.allow()
        end = time.perf_counter()
        times.append(end - start)
    
    times.sort()
    
    print(f"\nPerformance test (n=10000):")
    print(f"  Mean: {statistics.mean(times) * 1e6:.2f}μs")
    print(f"  Median: {statistics.median(times) * 1e6:.2f}μs")
    print(f"  99th percentile: {times[int(len(times)*0.99)] * 1e6:.2f}μs")
    
    assert statistics.mean(times) < 0.0001, "Performance too slow"
    print("✓ Performance test passed")


def test_concurrent_correctness():
    """Stress test for concurrent correctness."""
    import task11_wally
    
    max_requests = 1000
    limiter = task11_wally.SlidingWindowRateLimiter(max_requests, 2.0)
    
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
    
    assert allowed_count[0] <= max_requests + 5, \
        f"Allowed {allowed_count[0]} but limit is {max_requests}"
    
    print("✓ Concurrency test passed")


def test_limits():
    """Test various limit configurations."""
    import task11_wally
    
    # Test with limit of 1
    limiter = task11_wally.SlidingWindowRateLimiter(1, 1.0)
    assert limiter.allow()
    assert not limiter.allow()
    time.sleep(1.1)
    assert limiter.allow()
    
    # Test with small window
    limiter = task11_wally.SlidingWindowRateLimiter(5, 0.01)
    for _ in range(5):
        assert limiter.allow()
    assert not limiter.allow()
    
    # Test invalid inputs
    try:
        task11_wally.SlidingWindowRateLimiter(0, 1.0)
        assert False, "Should have raised"
    except ValueError:
        pass
    
    try:
        task11_wally.SlidingWindowRateLimiter(1, 0)
        assert False, "Should have raised"
    except ValueError:
        pass
    
    print("✓ Edge case tests passed")


def run_all_tests():
    print("=== Task 1.1 Rate Limiter Comprehensive Tests ===\n")
    
    print("1. Sliding vs Fixed Window Test:")
    test_sliding_vs_fixed()
    
    print("\n2. Performance Test:")
    test_performance()
    
    print("\n3. Edge Case Tests:")
    test_limits()
    
    print("\n4. Concurrency Correctness Test:")
    test_concurrent_correctness()
    
    print("\n=== All comprehensive tests passed ===")


if __name__ == "__main__":
    run_all_tests()
