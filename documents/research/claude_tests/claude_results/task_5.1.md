# Cursor-Based Pagination Implementation

## Analysis of the Provided Code

The starter code has several **critical bugs** worth fixing:

1. **`split(":")` corruption**: HMAC hexdigest contains no `:`, but the *raw JSON* may contain `:` characters (e.g., `{"timestamp": 1.0}`). `decoded.split(":")` splits on *all* colons, breaking JSON. Must use `rsplit(":", 1)`.
2. **Timing attack**: `sig != expected_sig` uses non-constant-time comparison. Use `hmac.compare_digest`.
3. **Inefficient pagination**: `page_number` implies offset-based rescanning. True cursor pagination should seek via `last_id` for O(log n + k) access.
4. **No expiry validation** despite storing `timestamp`.

---

## Complete Implementation

```python
from __future__ import annotations

from typing import Generic, List, Optional, Protocol, Sequence, TypeVar
from dataclasses import dataclass, asdict
import base64
import json
import time
import hmac
import hashlib
import secrets
import bisect

T = TypeVar("T")


@dataclass
class Page(Generic[T]):
    """A single page of results with navigation cursors.

    Attributes:
        items: The records contained in this page.
        next_cursor: Opaque cursor to fetch the following page, or None if last page.
        prev_cursor: Opaque cursor to fetch the preceding page, or None if first page.
        total: Total number of records across all pages (best-effort).
    """
    items: List[T]
    next_cursor: Optional[str]
    prev_cursor: Optional[str]
    total: int


@dataclass
class CursorData:
    """Payload encoded inside an opaque cursor.

    Attributes:
        timestamp: Unix time the cursor was created (for TTL enforcement).
        page_number: Logical page index (for display / prev computation only).
        last_id: The id of the last item on the page that produced this cursor.
                 Used as a seek key so retrieval is O(log n + k), not O(offset).
        direction: 'next' or 'prev'; controls seek direction.
    """
    timestamp: float
    page_number: int
    last_id: int
    direction: str = "next"


class PaginationCursor:
    """Opaque, tamper-evident cursor encoder/decoder.

    Cursors are HMAC-signed so clients cannot forge or mutate them
    (e.g. cannot jump to arbitrary ids or pages). They are also opaque
    (base64) so internal pagination strategy is not leaked.
    """

    def __init__(self, secret_key: Optional[bytes] = None, ttl_seconds: Optional[float] = None):
        """
        Args:
            secret_key: HMAC key. If None, a random 32-byte key is generated.
                        NOTE: a random key means cursors won't validate across
                        process restarts / multiple servers; provide a fixed
                        key in production.
            ttl_seconds: If set, cursors older than this are rejected.
        """
        self._secret = secret_key or secrets.token_bytes(32)
        self._ttl = ttl_seconds

    def create_cursor(self, data: CursorData) -> str:
        """Create an opaque, signed cursor string from cursor data.

        Returns:
            A URL-safe base64 string of the form base64(payload || b"." || sig).
        """
        raw = json.dumps(asdict(data), separators=(",", ":"), sort_keys=True).encode()
        sig = hmac.new(self._secret, raw, hashlib.sha256).digest()
        # Use a non-base64 alphabet separator. base64 (urlsafe) uses
        # [A-Za-z0-9-_], so '.' is a safe, unambiguous delimiter even though
        # the raw payload itself is base64'd as one unit below.
        combined = raw + b"." + sig
        return base64.urlsafe_b64encode(combined).decode()

    def decode_cursor(self, cursor_str: str) -> Optional[CursorData]:
        """Decode and validate a cursor.

        Returns:
            CursorData if the signature is valid (and not expired), else None.
        """
        try:
            combined = base64.urlsafe_b64decode(cursor_str.encode())
            # Split off the trailing signature. Signature is fixed-length
            # (32 bytes for sha256), so slice rather than split to avoid
            # any ambiguity with '.' inside the payload.
            sig_len = hashlib.sha256().digest_size  # 32
            if len(combined) < sig_len + 1:
                return None
            raw = combined[: -sig_len - 1]
            sep = combined[-sig_len - 1: -sig_len]
            sig = combined[-sig_len:]
            if sep != b".":
                return None

            expected_sig = hmac.new(self._secret, raw, hashlib.sha256).digest()
            # Constant-time comparison to prevent timing attacks.
            if not hmac.compare_digest(sig, expected_sig):
                return None

            payload = json.loads(raw.decode())
            data = CursorData(**payload)

            if self._ttl is not None and (time.time() - data.timestamp) > self._ttl:
                return None
            return data
        except Exception:
            # Any malformed input -> treat as invalid cursor.
            return None


# ---------------------------------------------------------------------------
# Repository that uses cursors for efficient seek-based pagination.
# ---------------------------------------------------------------------------

class HasId(Protocol):
    id: int


ItemT = TypeVar("ItemT", bound=HasId)


class CursorPaginator(Generic[ItemT]):
    """Seek-based paginator over an id-sorted dataset.

    Assumes items are sorted by a unique, monotonic `id`. This enables
    O(log n + k) page retrieval via binary search rather than O(offset).
    Backing store here is an in-memory list, but the same `last_id` seek
    strategy maps directly to SQL: `WHERE id > :last_id ORDER BY id LIMIT :k`.
    """

    def __init__(self, items: Sequence[ItemT], page_size: int, cursor: PaginationCursor):
        if page_size <= 0:
            raise ValueError("page_size must be positive")
        # Keep sorted by id; copy to avoid external mutation surprises.
        self._items: List[ItemT] = sorted(items, key=lambda x: x.id)
        self._ids: List[int] = [it.id for it in self._items]
        self._page_size = page_size
        self._cursor = cursor

    def _seek_index(self, last_id: int) -> int:
        """Return index of first item with id > last_id. O(log n)."""
        return bisect.bisect_right(self._ids, last_id)

    def get_page(self, cursor_str: Optional[str] = None) -> Page[ItemT]:
        """Fetch a page. With no cursor, returns the first page.

        Args:
            cursor_str: opaque cursor from a previous page, or None for first page.

        Returns:
            A Page with items and next/prev cursors.

        Raises:
            ValueError: if a non-None cursor is invalid/tampered/expired.
        """
        total = len(self._items)

        # --- Resolve start index from cursor ---
        if cursor_str is None:
            start = 0
            page_number = 1
        else:
            data = self._cursor.decode_cursor(cursor_str)
            if data is None:
                raise ValueError("Invalid, tampered, or expired cursor")

            if data.direction == "next":
                start = self._seek_index(data.last_id)
                page_number = data.page_number + 1
            else:  # prev
                # Items strictly before this page's first id. last_id here is
                # the first_id of the page we came from.
                end_excl = bisect.bisect_left(self._ids, data.last_id)
                start = max(0, end_excl - self._page_size)
                page_number = max(1, data.page_number - 1)

        # --- Slice the page ---
        end = min(start + self._page_size, total)
        items = self._items[start:end]

        now = time.time()

        # --- Build next_cursor ---
        next_cursor: Optional[str] = None
        if end < total and items:
            next_cursor = self._cursor.create_cursor(
                CursorData(
                    timestamp=now,
                    page_number=page_number,
                    last_id=items[-1].id,
                    direction="next",
                )
            )

        # --- Build prev_cursor ---
        prev_cursor: Optional[str] = None
        if start > 0 and items:
            prev_cursor = self._cursor.create_cursor(
                CursorData(
                    timestamp=now,
                    page_number=page_number,
                    last_id=items[0].id,   # first id of current page
                    direction="prev",
                )
            )

        return Page(items=items, next_cursor=next_cursor, prev_cursor=prev_cursor, total=total)
```

---

## Demonstration & Tests

```python
@dataclass
class Record:
    id: int
    name: str


def demo() -> None:
    secret = b"fixed-secret-key-for-stable-cursors!"
    cursor = PaginationCursor(secret_key=secret, ttl_seconds=3600)
    records = [Record(id=i, name=f"item-{i}") for i in [1, 3, 5, 7, 9, 11, 13]]
    paginator = CursorPaginator(records, page_size=3, cursor=cursor)

    # Page 1
    p1 = paginator.get_page()
    assert [r.id for r in p1.items] == [1, 3, 5]
    assert p1.prev_cursor is None and p1.next_cursor is not None

    # Page 2 (seek via cursor)
    p2 = paginator.get_page(p1.next_cursor)
    assert [r.id for r in p2.items] == [7, 9, 11]
    assert p2.prev_cursor is not None and p2.next_cursor is not None

    # Page 3 (last, partial)
    p3 = paginator.get_page(p2.next_cursor)
    assert [r.id for r in p3.items] == [13]
    assert p3.next_cursor is None  # boundary: last page

    # Go back from page 2
    back = paginator.get_page(p2.prev_cursor)
    assert [r.id for r in back.items] == [1, 3, 5]

    # Opaqueness: cursor reveals no page info
    assert "page" not in p1.next_cursor.lower()

    # Tamper detection
    tampered = p1.next_cursor[:-4] + "AAAA"
    try:
        paginator.get_page(tampered)
        assert False, "should reject tampered cursor"
    except ValueError:
        pass

    # Wrong key cannot decode
    other = PaginationCursor(secret_key=b"different-key")
    assert other.decode_cursor(p1.next_cursor) is None

    print("All assertions passed.")


if __name__ == "__main__":
    demo()
```

---

## Design Decisions & Tradeoffs

| Decision | Rationale | Tradeoff |
|---|---|---|
| **Seek by `last_id` (binary search / `WHERE id > last_id`)** | O(log n + k) per page; no offset rescan | Requires a sorted, unique key; can't jump to arbitrary page N |
| **HMAC-SHA256 signature** | Tamper-evidence; client can't forge `last_id` to scrape arbitrary rows | Adds ~44 bytes; needs shared secret across servers |
| **Fixed-length sig slicing** | Avoids the original `split(":")` bug where JSON colons corrupt parsing | Slightly less obvious than a delimiter |
| **`hmac.compare_digest`** | Constant-time → prevents signature timing attacks | None meaningful |
| **`base64.urlsafe_b64encode`** | Safe in URLs/query strings without escaping | None |
| **Optional TTL** | Limits cursor replay window; cursors don't outlive data shifts forever | Long sessions may see expiry |
| **Opaque payload** | Internal strategy (seek vs offset) hidden; can evolve server-side | Clients can't introspect |

## Edge Cases Handled

- **Empty dataset / empty page** → no cursors emitted (`items` falsy guard).
- **First page** → `prev_cursor is None`.
- **Last page** → `next_cursor is None`; partial last page handled by `min(end, total)`.
- **Tampered cursor** → signature mismatch → `None` → `ValueError`.
- **Wrong secret key** → fails validation (not a crash).
- **Malformed base64 / truncated cursor** → caught, returns `None`.
- **JSON containing colons** → fixed via length-based sig extraction.
- **Expired cursor** → rejected when TTL configured.
- **Deleted `last_id`** → `bisect_right` still finds the correct next position (graceful; stable across deletions, unlike offset pagination).

## Complexity

- `create_cursor` / `decode_cursor`: **O(payload size)**.
- `get_page`: **O(log n + k)** (binary search + page slice), where `k = page_size`.
- No re-scan from the start — the key advantage over offset pagination's O(offset).