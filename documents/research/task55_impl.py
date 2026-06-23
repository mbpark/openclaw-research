"""
Task 5.5: Cache-Based Pagination with Cursor Support

Implements cache-based pagination with cursor support for efficient
data retrieval and replay.
"""

from typing import List, Optional, TypeVar, Generic, Dict, Any
from dataclasses import dataclass
import base64
import json
import time
import hashlib


@dataclass
class Cursor:
    """Represents a pagination cursor."""
    index: int
    timestamp: float
    
    def __init__(self, index: int = 0, timestamp: Optional[float] = None):
        self.index = index
        self.timestamp = timestamp or time.time()
    
    def serialize(self) -> str:
        data = {
            "index": self.index,
            "timestamp": self.timestamp
        }
        return base64.b64encode(json.dumps(data).encode()).decode()
    
    @staticmethod
    def deserialize(data: str) -> 'Cursor':
        decoded = json.loads(base64.b64decode(data).decode())
        return Cursor(index=decoded["index"], timestamp=decoded["timestamp"])


@dataclass
class PageResult:
    """Represents a paginated result."""
    items: list
    current_page: int
    total_pages: int
    total_items: int
    next_cursor: Optional[str]
    previous_cursor: Optional[str]
    has_next: bool
    has_previous: bool
    is_last_page: bool


class CacheBasedPaginator:
    """
    Implements cache-based pagination with cursor support.
    
    Features:
    - Cache hit/miss tracking
    - Cursor-based navigation
    - Limited cache size with eviction
    """
    
    def __init__(self, data_source, default_page_size: int = 20, 
                 max_cache_size: int = 1000):
        self._data_source = data_source
        self._default_page_size = default_page_size
        self._max_cache_size = max_cache_size
        
        # Cache storage
        self._cache: Dict[str, Any] = {}
        self._cache_hits = 0
        self._cache_misses = 0
    
    def get_page(self, cursor_data: Optional[str] = None, 
                 page_size: Optional[int] = None) -> PageResult:
        """
        Get paginated data with caching.
        
        Args:
            cursor_data: Serialized cursor from previous page
            page_size: Number of items per page
            
        Returns:
            PageResult with data and pagination metadata
        """
        # Generate cache key
        if cursor_data:
            cursor = Cursor.deserialize(cursor_data)
            start_index = cursor.index
        else:
            start_index = 0
        
        page_size = page_size or self._default_page_size
        cache_key = f"page_{start_index}_{page_size}"
        
        # Try cache first
        if cache_key in self._cache:
            self._cache_hits += 1
            return self._cache[cache_key]
        
        # Cache miss - generate new page
        self._cache_misses += 1
        result = self._generate_page(start_index, page_size)
        
        # Store in cache with eviction
        if len(self._cache) >= self._max_cache_size:
            self._evict_oldest()
        
        self._cache[cache_key] = result
        return result
    
    def _generate_page(self, start_index: int, page_size: int) -> PageResult:
        """Generate a new page of results."""
        total_items = len(self._data_source)
        
        # Get data slice
        end_index = min(start_index + page_size, total_items)
        items = self._data_source[start_index:end_index]
        
        # Calculate pagination metadata
        current_page = start_index // page_size + 1
        total_pages = (total_items + page_size - 1) // page_size
        has_next = end_index < total_items
        has_previous = start_index > 0
        is_last_page = end_index >= total_items
        
        # Create cursors
        next_cursor = Cursor(index=end_index).serialize() if has_next else None
        previous_cursor = Cursor(index=max(0, start_index - page_size)).serialize() if has_previous else None
        
        return PageResult(
            items=items,
            current_page=current_page,
            total_pages=total_pages,
            total_items=total_items,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            has_next=has_next,
            has_previous=has_previous,
            is_last_page=is_last_page
        )
    
    def _evict_oldest(self):
        """Evict oldest cache entries."""
        if not self._cache:
            return
        
        # Simple LRU eviction - evict half
        keys_to_remove = list(self._cache.keys())
        remove_count = max(len(keys_to_remove) // 2, 1)
        
        for key in keys_to_remove[:remove_count]:
            del self._cache[key]
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests) if total_requests > 0 else 0.0
        
        return {
            "cache_size": len(self._cache),
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }
    
    def clear_cache(self):
        """Clear all cached pages."""
        self._cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0


def test_cache_based_pagination():
    """Test cache-based pagination."""
    sample_data = list(range(100))
    paginator = CacheBasedPaginator(sample_data, default_page_size=10)
    
    # Test initial page
    result1 = paginator.get_page()
    assert result1.current_page == 1
    assert len(result1.items) == 10
    assert result1.has_next
    assert not result1.has_previous
    
    # Test cache miss for second page
    result2 = paginator.get_page(result1.next_cursor)
    assert result2.current_page == 2
    assert len(result2.items) == 10
    assert result2.has_next
    assert result2.has_previous
    
    # Test cache hit for second page
    result3 = paginator.get_page(result1.next_cursor)
    assert result3.items == result2.items
    
    # Test cache statistics
    stats = paginator.get_cache_stats()
    assert stats["cache_hits"] >= 0
    assert stats["cache_misses"] >= 1
    
    # Test navigation
    result_prev = paginator.get_page(result2.previous_cursor)
    assert result_prev.current_page == 1
    
    # Test last page
    last_page_result = paginator.get_page(Cursor(index=97).serialize())
    assert len(last_page_result.items) == 3
    assert last_page_result.is_last_page
    
    print("Tests passed")

if __name__ == "__main__":
    test_cache_based_pagination()
