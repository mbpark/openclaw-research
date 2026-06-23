## Task 5.3: Retry with Exponential Backoff

**Description:**
Implement retry logic with exponential backoff and error classification.

**Interface:**
```python
from typing import Callable, TypeVar, Type
from dataclasses import dataclass
import time
import random
import asyncio


class RetryConfig:
    """Configuration for retry behavior."""
    
    max_attempts: int = 3
    base_delay: float = 0.1
    max_delay: float = 30.0
    jitter: float = 0.5
    retryable_exceptions: tuple = (ConnectionError, TimeoutError)
    non_retryable_exceptions: tuple = (ValueError, KeyError)


class RetryExecutor:
    """Executes operations with retry logic."""
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    def execute(self, func: Callable, *args, **kwargs) -> any:
        """Execute with retries, raise after max attempts."""
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                return func(*args, **kwargs)
            except self.config.non_retryable_exceptions:
                # Don't retry these
                raise
            except self.config.retryable_exceptions as e:
                last_exception = e
                if attempt < self.config.max_attempts - 1:
                    delay = self._calculate_delay(attempt)
                    time.sleep(delay)
                continue
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter."""
        exponential = self.config.base_delay * (2 ** attempt)
        capped = min(exponential, self.config.max_delay)
        # Add jitter
        jitter_range = self.config.jitter * capped
        return capped + random.uniform(-jitter_range / 2, jitter_range / 2)


def retry(config: RetryConfig) -> Callable:
    """Decorator version of retry."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            executor = RetryExecutor(config)
            return executor.execute(func, *args, **kwargs)
        return wrapper
```

**What to evaluate:**
- Exponential backoff formula correct
- Jitter adds variance without exceeding max
- Distinguishes retryable vs non-retryable errors
- Doesn't retry forever (respects max_attempts)
- Doesn't retry on errors retry won't help (400, 404, AuthError)

**Scoring:** __ / 6
