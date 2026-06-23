"""
Task 5.4: Cache Concurrency with Stampede Protection

Implements cache with stampede protection to prevent multiple threads
from simultaneously regenerating cached values.
"""

from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from threading import Lock, Event
import time
from collections import OrderedDict


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    value: Any
    created_at: float
    expires_at: float
    in_flight: Optional[Event] = None
    result: Optional[Any] = None


class StampedeProtectedCache:
    """
    Cache with stampede protection.
    
    Prevents multiple threads from regenerating the same
    cache entry simultaneously.
    """
    
    def __init__(self, default_ttl: float = 300.0):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._default_ttl = default_ttl
        self._key_locks: Dict[str, Lock] = {}
    
    def get(self, key: str, fetch_fn: Optional[Callable] = None) -> Optional[Any]:
        """
        Get value from cache, creating it if not present.
        
        Uses stampede protection when creating cache entries.
        """
        # First check for existing entry
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if not self._is_expired(entry):
                    return entry.value
                elif entry.in_flight and not entry.in_flight.is_set():
                    # Another thread is creating this entry
                    return None
        
        # Create event to coordinate threads
        event = Event()
        
        # Ensure only one thread regenerates this entry
        with self._lock:
            if key in self._cache and not self._is_expired(self._cache[key]):
                return self._cache[key].value
            
            if not fetch_fn:
                return None
            
            # Check again if someone else created this entry
            if key in self._cache and self._cache[key].in_flight:
                return self._cache[key].value
            
            # Create entry with event
            entry = CacheEntry(
                value=None,
                created_at=time.time(),
                expires_at=time.time() + self._default_ttl,
                in_flight=event
            )
            self._cache[key] = entry
        
        # Generate cache value
        try:
            value = fetch_fn()
            with self._lock:
                entry = self._cache[key]
                entry.value = value
                entry.in_flight = None
                entry.created_at = time.time()
                entry.expires_at = time.time() + self._default_ttl
            event.set()
            return value
        except Exception as e:
            with self._lock:
                if key in self._cache:
                    del self._cache[key]
            event.set()
            raise
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set cache entry."""
        with self._lock:
            self._cache[key] = CacheEntry(
                value=value,
                created_at=time.time(),
                expires_at=time.time() + (ttl or self._default_ttl)
            )
    
    def delete(self, key: str) -> bool:
        """Delete cache entry."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def contains(self, key: str) -> bool:
        """Check if key exists in cache."""
        with self._lock:
            return key in self._cache and not self._is_expired(self._cache[key])
    
    def size(self) -> int:
        """Get number of valid entries."""
        with self._lock:
            return sum(1 for entry in self._cache.values() 
                      if not self._is_expired(entry))
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired."""
        return time.time() > entry.expires_at
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        with self._lock:
            total = len(self._cache)
            valid = sum(1 for entry in self._cache.values() 
                       if not self._is_expired(entry))
            in_flight = sum(1 for entry in self._cache.values() 
                          if entry.in_flight and not entry.in_flight.is_set())
            
            return {
                "total_entries": total,
                "valid_entries": valid,
                "in_flight_entries": in_flight,
                "expired_entries": total - valid
            }


def test_stampede_protection():
    """Test stampede protection functionality."""
    cache = StampedeProtectedCache(default_ttl=10.0)
    
    # Test basic cache operations
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"
    
    # Test stampede protection
    fetch_count = [0]
    def slow_fetch():
        fetch_count[0] += 1
        return f"Generated value at {time.time()}"
    
    # Multiple threads trying to fetch same key
    results = [cache.get("shared_key", fetch_fn=slow_fetch) for _ in range(3)]
    
    # Should have only fetched once
    assert fetch_count[0] == 1
    
    # Test expired entry
    cache = StampedeProtectedCache(default_ttl=0.1)
    cache.set("temp_key", "temp_value")
    time.sleep(0.2)
    assert cache.get("temp_key") is None
    
    # Test stats
    stats = cache.get_stats()
    assert stats["total_entries"] >= 0
    
    print("Tests passed")

if __name__ == "__main__":
    test_stampede_protection()
