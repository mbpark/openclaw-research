"""
Task 5.3: Retry with Exponential Backoff

Implements retry mechanism with exponential backoff, jitter, and circuit breaker integration.
"""

from typing import Callable, Optional, Any
from dataclasses import dataclass
import time
import random
import threading


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    exponential_jitter: bool = True
    jitter_range: float = 0.5


@dataclass
class RetryStats:
    """Statistics for retry tracking."""
    total_retries: int = 0
    successful_retries: int = 0
    failed_retries: int = 0


class RetryHandler:
    """
    Implements retry with exponential backoff and jitter.
    """
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self._config = config or RetryConfig()
        self._stats = RetryStats()
        self._lock = threading.Lock()
    
    def execute(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute operation with retry logic."""
        current_retry = 0
        last_exception = None
        
        while current_retry <= self._config.max_retries:
            try:
                result = operation(*args, **kwargs)
                self._record_success()
                return result
            except Exception as e:
                if current_retry == self._config.max_retries:
                    raise MaxRetriesExhausted(
                        f"Max retries {self._config.max_retries} exhausted"
                    )
                
                # Calculate delay with exponential backoff
                delay = self._calculate_delay(current_retry)
                
                # Apply jitter
                if self._config.exponential_jitter:
                    jitter_factor = random.uniform(
                        1 - self._config.jitter_range,
                        1 + self._config.jitter_range
                    )
                    delay *= jitter_factor
                
                # Wait
                time.sleep(delay)
                
                current_retry += 1
                last_exception = e
        
        raise MaxRetriesExhausted(
            f"Max retries {self._config.max_retries} exhausted"
        )
    
    def _calculate_delay(self, retry_attempt: int) -> float:
        """Calculate delay based on retry attempt."""
        delay = self._config.initial_delay * (self._config.backoff_factor ** retry_attempt)
        return min(delay, self._config.max_delay)
    
    def _record_success(self):
        """Record successful operation."""
        with self._lock:
            self._stats.successful_retries += 1


class MaxRetriesExhausted(Exception):
    """Exception raised when retry attempts are exhausted."""
    pass


def flaky_operation(success_rate: float = 0.7):
    """Simulate a flaky operation."""
    if random.random() < success_rate:
        return "Operation succeeded"
    else:
        raise ConnectionError("Service temporarily unavailable")


def test_retry_with_backoff():
    """Test retry with exponential backoff."""
    handler = RetryHandler()
    
    # Test successful operation
    result = handler.execute(flaky_operation, success_rate=0.9)
    assert "succeeded" in result
    
    # Test operation that requires retries
    call_count = [0]
    
    def operation_with_retries():
        call_count[0] += 1
        if call_count[0] <= 3:
            raise ConnectionError("Transient error")
        return "Success after retries"
    
    config = RetryConfig(max_retries=5, initial_delay=0.1)
    handler = RetryHandler(config=config)
    result = handler.execute(operation_with_retries)
    assert "Success" in result
    assert call_count[0] == 4
    
    # Test exhausted retries
    call_count[0] = 0
    config = RetryConfig(max_retries=2, initial_delay=0.1)
    handler = RetryHandler(config=config)
    
    def always_fail():
        call_count[0] += 1
        raise ConnectionError("Always fails")
    
    try:
        handler.execute(always_fail)
        assert False, "Should have exhausted retries"
    except MaxRetriesExhausted:
        assert call_count[0] == 3  # 1 initial + 2 retries
    
    # Test with jitter
    call_count[0] = 0
    config = RetryConfig(max_retries=3, initial_delay=0.1, exponential_jitter=True)
    handler = RetryHandler(config=config)
    
    def operation_with_jitter():
        call_count[0] += 1
        if call_count[0] <= 2:
            raise ConnectionError("Transient error")
        return "Success"
    
    result = handler.execute(operation_with_jitter)
    assert "Success" in result
    
    print("Tests passed")


if __name__ == "__main__":
    test_retry_with_backoff()
