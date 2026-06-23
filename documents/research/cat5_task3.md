## Task 5.4: Cache Concurrency with Stampede Protection

**Description:**
Implement a thread-safe cache with:
- Cache stampede protection (one thread recomputes, others wait)
- Read-while-recompute (serve old value during recomputation)
- Conditional update (don't overwrite fresh data with stale recompute)

**Interface:**
```python
from typing import TypeVar, Callable, Optional
from dataclasses import dataclass
import threading
import time


@dataclass
class CacheEntry:
    value: any
    expire_at: float
    compute_lock: Optional[threading.Event] = None


class ConcurrentCache:
    """
    Thread-safe cache with stampede protection.
    """
    
    def __init__(self, ttl: float = 60.0):
        self.ttl = ttl
        self._cache: dict = {}
        self._locks: dict = {}
        self._lock = threading.Lock()
    
    def _get_or_create_lock(self, key) -> threading.RLock:
        """Get or create per-key lock."""
        if key not in self._locks:
            self._locks[key] = threading.RLock()
        return self._locks[key]

    def get(
        self,
        key,
        compute_fn: Optional[Callable[[], any]] = None
    ) -> Optional[any]:
        """
        Get value, recomputing if missing/expired.
        Returns old value during recomputation.
        """
        lock = self._get_or_create_lock(key)
        
        with lock:
            entry = self._cache.get(key)
            
            if entry and time.time() < entry.expire_at:
                return entry.value
            
            if not compute_fn:
                return None
            
            # Check if already recomputing
            if entry and entry.compute_lock:
                # Another thread is recomputing
                return entry.value
            
            # Start recomputation
            old_value = entry.value if entry else None
            new_event = threading.Event()
            self._cache[key] = CacheEntry(
                old_value,
                time.time() + self.ttl + 30,  # grace period
                compute_lock=new_event
            )
        
        # Compute outside lock
        try:
            new_value = compute_fn()
            with lock:
                # Conditional update - only if still same compute_lock
                entry = self._cache.get(key)
                if entry and entry.compute_lock == new_event:
                    self._cache[key] = CacheEntry(
                        new_value,
                        time.time() + self.ttl,
                        compute_lock=None
                    )
                new_event.set()
                return new_value
        except Exception:
            new_event.set()
            raise

    def put(self, key, value) -> None:
        """Put value, overwriting existing."""
        with self._get_or_create_lock(key):
            self._cache[key] = CacheEntry(
                value,
                time.time() + self.ttl,
                compute_lock=None
            )

    def invalidate(self, key) -> None:
        """Remove entry."""
        with self._get_or_create_lock(key):
            self._cache.pop(key, None)

    def size(self) -> int:
        """Number of non-expired entries."""
        now = time.time()
        return sum(
            1 for entry in self._cache.values()
            if now < entry.expire_at
        )
```

**What to evaluate:**
- Proper stampede protection
- Returns old value while recomputing
- Conditional update rejects stale recomputes
- Thread safety throughout
- Doesn't hold locks during compute_fn
- Per-key lock granularity

**Scoring:** __ / 6
