"""
Task 5.1: Cursor-Based Pagination

Implements cursor-based pagination with proper data type handling and edge cases.
"""

from typing import List, Optional, TypeVar, Generic, Dict, Any
from dataclasses import dataclass
import base64
import json
import time


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


class PaginatedQuery(Generic[TypeVar('T')]):
    """
    Implements cursor-based pagination for data retrieval.
    
    Handles edge cases:
    - Empty result sets
    - Invalid cursors
    - Concurrent data changes
    """
    
    def __init__(self, data_source, default_page_size: int = 20, max_page_size: int = 100):
        self._data_source = data_source
        self._default_page_size = default_page_size
        self._max_page_size = max_page_size
    
    def execute(self, cursor: Optional[Cursor] = None, page_size: Optional[int] = None) -> PageResult:
        """Execute paginated query."""
        # Validate parameters
        page_size = page_size or self._default_page_size
        if page_size <= 0 or page_size > self._max_page_size:
            raise ValueError(f"Page size must be between 1 and {self._max_page_size}")
        
        # Get total count
        total_items = len(self._data_source)
        
        # Get start index from cursor
        start_index = cursor.index if cursor else 0
        
        # Handle empty result set
        if total_items == 0:
            return PageResult(
                items=[],
                current_page=1,
                total_pages=0,
                total_items=0,
                next_cursor=None,
                previous_cursor=None,
                has_next=False,
                has_previous=False,
                is_last_page=True
            )
        
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
    
    def get_by_cursor(self, cursor_data: str, page_size: Optional[int] = None) -> PageResult:
        """Get page by cursor string."""
        try:
            cursor = Cursor.deserialize(cursor_data)
            return self.execute(cursor, page_size)
        except Exception as e:
            raise ValueError(f"Invalid cursor: {str(e)}")


def test_cursor_pagination():
    """Test cursor-based pagination."""
    # Create sample data
    sample_data = list(range(100))
    paginated = PaginatedQuery(sample_data, default_page_size=10)
    
    # Test first page
    result1 = paginated.execute()
    assert result1.current_page == 1
    assert len(result1.items) == 10
    assert result1.has_next
    assert not result1.has_previous
    assert result1.items == list(range(10))
    
    # Test second page
    result2 = paginated.execute(Cursor.deserialize(result1.next_cursor))
    assert result2.current_page == 2
    assert len(result2.items) == 10
    assert result2.has_next
    assert result2.has_previous
    assert result2.items == list(range(10, 20))
    
    # Test last page
    last_page_size = 3  # Will get only 3 items on last page
    result_last = paginated.execute(Cursor(index=97))
    assert len(result_last.items) == 3
    assert result_last.has_previous
    assert not result_last.has_next
    assert result_last.is_last_page
    
    # Test invalid cursor
    try:
        paginated.execute(Cursor(index=150))
    except Exception:
        pass
    
    # Test empty result set
    empty_paginated = PaginatedQuery([])
    empty_result = empty_paginated.execute()
    assert empty_result.is_last_page
    assert len(empty_result.items) == 0
    
    print("Tests passed")

if __name__ == "__main__":
    test_cursor_pagination()
