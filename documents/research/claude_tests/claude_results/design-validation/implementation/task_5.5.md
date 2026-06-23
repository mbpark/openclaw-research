# Analysis of the Provided Implementation

Before providing a complete solution, let me identify the **critical flaws** in the starter code:

### Critical Bugs in Starter Code

1. **Offset-based cursors break under mutations.** Using a numeric `offset` means inserting/removing an item shifts every subsequent item. A user paginating will see duplicates or skips. This violates the "handle items added/removed during pagination" constraint.

2. **`prev_cursor` logic is broken.** When following a `next` cursor, it sets `prev_cursor = cursor` — but that's the *current* cursor, not a cursor pointing to the *previous* page. Backward navigation doesn't actually work.

3. **The `_page_cache` is never used.** Declared but dead. The "cache-based" requirement is unmet.

4. **`_items` is held entirely in memory.** Contradicts the "can't fit all in memory" constraint. The interface itself is contradictory.

5. **`time.time()` in the cursor makes the signature change each call**, so cursors are non-deterministic and uncacheable (no benefit, but it also leaks timing info).

6. **HMAC comparison uses `!=`** instead of `hmac.compare_digest` → timing-attack vulnerable.

---

## ⚠️ This Problem Is Underspecified

I'm flagging this explicitly because the spec contains **contradictory and missing requirements** that materially change the design. I'll state my assumptions, then implement the most defensible version.

### Missing / Contradictory Information

| Issue | Why it matters | My assumption |
|---|---|---|
| "Can't fit in memory" vs. `__init__(self, items: List[T])` | The interface *requires* all items in memory. These contradict. | I'll keep the in-memory list per the interface, but design cursors so a **datastore-backed** version is a drop-in. I add a `DataSource` protocol. |
| What is the **stable sort key**? Cursor pagination requires a unique, ordered key. None is specified. | Without it, "stable under mutation" is impossible. | I require items to expose a unique, comparable **key** (via a `key_fn`). Default: object identity won't work, so I require it. |
| Are items **ordered**? By what? | Cursor semantics depend on ordering. | Assume sorted ascending by `key_fn`. |
| Cursor **expiry / TTL**? `timestamp` exists but is unused. | Determines cache eviction & security. | Add configurable TTL. |
| What does `total` "approximate" mean? | Exact under lock is trivial here. | Return exact count (it's in memory); document that a real backend would estimate. |
| Cache eviction policy / size bound? | "hundreds of concurrent requests" needs bounds. | LRU with max size. |
| Should an invalid/expired cursor raise or return empty? | Affects API contract. | Raise `InvalidCursorError` (subclass of `ValueError`). |

I'll ask: **if these assumptions are wrong, the design changes significantly.** I proceed with the keyset-pagination approach since it's the only one that satisfies "stable under mutation."

---

## Complete Implementation

```python
"""
Cursor-based (keyset) pagination engine with opaque, signed cursors,
an LRU page cache, and stability under concurrent mutation.

Key design choice: KEYSET pagination, not offset pagination.
Cursors encode the last-seen sort key, so insertions/deletions
elsewhere in the dataset do not cause skips or duplicates.
"""

from __future__ import annotations

import base64
import bisect
import hmac
import json
import secrets
import threading
import time
from collections import OrderedDict
from dataclasses import asdict, dataclass
from typing import (
    Callable,
    Generic,
    Hashable,
    List,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    runtime_checkable,
)

T = TypeVar("T")
# Sort keys must be comparable and hashable (used for ordering + cache keying).
K = TypeVar("K", bound=Hashable)


class InvalidCursorError(ValueError):
    """Raised when a cursor is malformed, tampered with, or expired."""


@dataclass
class Page(Generic[T]):
    """A single page of results plus navigation cursors."""

    items: List[T]
    next_cursor: Optional[str]
    prev_cursor: Optional[str]
    total: int  # exact here; documented as approximate for backend-backed sources


@dataclass(frozen=True)
class CursorState:
    """
    Internal cursor payload.

    Attributes:
        last_key: JSON-serializable sort key of the boundary item.
        direction: "next" (items > last_key) or "prev" (items < last_key).
        issued_at: epoch seconds, used for TTL enforcement.
    """

    last_key: object
    direction: str
    issued_at: float


@runtime_checkable
class DataSource(Protocol[T]):
    """
    Abstraction so the engine can be backed by memory or a real datastore.

    A production datastore implementation would translate these into
    `WHERE key > ? ORDER BY key LIMIT ?` queries — O(log n + page_size)
    instead of loading everything.
    """

    def fetch_after(self, key: Optional[object], limit: int) -> List[T]:
        """Return up to `limit` items with sort-key strictly greater than `key`."""
        ...

    def fetch_before(self, key: object, limit: int) -> List[T]:
        """Return up to `limit` items with sort-key strictly less than `key`,
        in ascending order."""
        ...

    def count(self) -> int:
        """Return (approximate) total item count."""
        ...


class _InMemorySortedSource(Generic[T]):
    """
    In-memory DataSource backed by a list kept sorted by key.

    Uses binary search (bisect) so page lookups are O(log n + page_size),
    NOT O(n). This is what makes pagination "not rescan from start".
    """

    def __init__(self, items: List[T], key_fn: Callable[[T], object]) -> None:
        self._key_fn = key_fn
        # Maintain parallel sorted structures: keys for bisect, items aligned.
        decorated = sorted(items, key=key_fn)
        self._items: List[T] = decorated
        self._keys: List[object] = [key_fn(i) for i in decorated]

    def _index_after(self, key: Optional[object]) -> int:
        if key is None:
            return 0
        # First index whose key is strictly greater than `key`.
        return bisect.bisect_right(self._keys, key)

    def fetch_after(self, key: Optional[object], limit: int) -> List[T]:
        start = self._index_after(key)
        return self._items[start : start + limit]

    def fetch_before(self, key: object, limit: int) -> List[T]:
        # First index with key >= `key`; we want items strictly before it.
        end = bisect.bisect_left(self._keys, key)
        start = max(0, end - limit)
        return self._items[start:end]

    def count(self) -> int:
        return len(self._items)

    # Mutation helpers (kept here so ordering invariant stays local).
    def insert(self, item: T) -> None:
        k = self._key_fn(item)
        idx = bisect.bisect_right(self._keys, k)
        self._keys.insert(idx, k)
        self._items.insert(idx, item)

    def remove_by_key(self, key: object) -> bool:
        idx = bisect.bisect_left(self._keys, key)
        if idx < len(self._keys) and self._keys[idx] == key:
            del self._keys[idx]
            del self._items[idx]
            return True
        return False


class CachePagingEngine(Generic[T]):
    """
    Cached, cursor (keyset) pagination engine.

    Design summary:
      - Keyset cursors -> stable under mutation, O(log n + page_size) lookups.
      - HMAC-signed, base64 cursors -> opaque + tamper-proof.
      - TTL on cursors -> bounded validity, enables cache eviction.
      - LRU page cache -> repeat requests for the same cursor are O(1).
      - RLock -> safe under many concurrent readers/writers.
    """

    def __init__(
        self,
        items: List[T],
        *,
        key_fn: Callable[[T], object],
        max_page_size: int = 100,
        cursor_ttl_seconds: float = 3600.0,
        cache_max_entries: int = 1024,
    ) -> None:
        """
        Args:
            items: initial dataset (in-memory backend per the given interface).
            key_fn: maps an item to a UNIQUE, comparable, JSON-serializable
                    sort key. REQUIRED — keyset pagination is impossible without it.
            max_page_size: hard upper bound on page size.
            cursor_ttl_seconds: how long a cursor stays valid.
            cache_max_entries: LRU cache capacity.
        """
        if max_page_size <= 0:
            raise ValueError("max_page_size must be positive")
        self._source = _InMemorySortedSource(items, key_fn)
        self._key_fn = key_fn
        self._max_page_size = max_page_size
        self._cursor_ttl = cursor_ttl_seconds
        self._cache_max = cache_max_entries

        self._secret = secrets.token_bytes(32)
        # cache_key -> Page. OrderedDict gives us LRU semantics cheaply.
        self._page_cache: "OrderedDict[str, Page[T]]" = OrderedDict()
        # Monotonic version: bumped on every mutation to invalidate the cache.
        self._version = 0
        self._lock = threading.RLock()

    # ----------------------------- Cursor codec ----------------------------- #

    def _sign_cursor(self, state: CursorState) -> str:
        """Create an opaque, signed, URL-safe cursor string."""
        raw = json.dumps(asdict(state), sort_keys=True, separators=(",", ":")).encode()
        sig = hmac.new(self._secret, raw, "sha256").digest()
        # Length-prefix the payload so we can split unambiguously even if raw
        # contains the delimiter byte.
        payload = len(raw).to_bytes(4, "big") + raw + sig
        return base64.urlsafe_b64encode(payload).decode()

    def _decode_cursor(self, cursor_str: str) -> CursorState:
        """Decode, verify signature, and check TTL. Raises on any problem."""
        try:
            payload = base64.urlsafe_b64decode(cursor_str.encode())
            raw_len = int.from_bytes(payload[:4], "big")
            raw = payload[4 : 4 + raw_len]
            sig = payload[4 + raw_len :]
        except Exception as exc:  # malformed base64 / truncated
            raise InvalidCursorError("Malformed cursor") from exc

        expected = hmac.new(self._secret, raw, "sha256").digest()
        # Constant-time comparison to avoid signature timing oracles.
        if not hmac.compare_digest(sig, expected):
            raise InvalidCursorError("Cursor signature mismatch")

        try:
            state = CursorState(**json.loads(raw.decode()))
        except Exception as exc:
            raise InvalidCursorError("Corrupt cursor payload") from exc

        if state.direction not in ("next", "prev"):
            raise InvalidCursorError("Bad cursor direction")
        if time.time() - state.issued_at > self._cursor_ttl:
            raise InvalidCursorError("Cursor expired")
        return state

    # ------------------------------ Cache layer ----------------------------- #

    def _cache_key(self, cursor: Optional[str], page_size: int) -> str:
        # Version makes every cached page stale after any mutation -> correctness
        # over hit-rate. (See tradeoffs section.)
        return f"{self._version}:{page_size}:{cursor or 'HEAD'}"

    def _cache_get(self, key: str) -> Optional[Page[T]]:
        page = self._page_cache.get(key)
        if page is not None:
            self._page_cache.move_to_end(key)  # mark as recently used
        return page

    def _cache_put(self, key: str, page: Page[T]) -> None:
        self._page_cache[key] = page
        self._page_cache.move_to_end(key)
        while len(self._page_cache) > self._cache_max:
            self._page_cache.popitem(last=False)  # evict least-recently-used

    # ------------------------------- Public API ----------------------------- #

    def get_page(
        self,
        cursor: Optional[str] = None,
        page_size: int = 20,
    ) -> Page[T]:
        """
        Fetch a page.

        - cursor=None  -> first page (forward from start).
        - "next" cursor -> items after the boundary.
        - "prev" cursor -> items before the boundary (backward navigation).

        Raises:
            ValueError: page_size <= 0.
            InvalidCursorError: cursor tampered/expired/malformed.
        """
        if page_size <= 0:
            raise ValueError("page_size must be positive")
        page_size = min(page_size, self._max_page_size)

        with self._lock:
            cache_key = self._cache_key(cursor, page_size)
            cached = self._cache_get(cache_key)
            if cached is not None:
                return cached

            if cursor is None:
                items = self._source.fetch_after(None, page_size)
            else:
                state = self._decode_cursor(cursor)
                if state.direction == "next":
                    items = self._source.fetch_after(state.last_key, page_size)
                else:  # "prev"
                    items = self._source.fetch_before(state.last_key, page_size)

            page = self._build_page(items, cursor, page_size)
            self._cache_put(cache_key, page)
            return page

    def _build_page(
        self,
        items: List[T],
        request_cursor: Optional[str],
        page_size: int,
    ) -> Page[T]:
        """Construct next/prev cursors based on page boundaries."""
        now = time.time()
        next_cursor: Optional[str] = None
        prev_cursor: Optional[str] = None

        if items:
            first_key = self._key_fn(items[0])
            last_key = self._key_fn(items[-1])

            # There may be a next page if we filled the page; we probe by
            # checking whether anything exists strictly after last_key.
            if self._source.fetch_after(last_key, 1):
                next_cursor = self._sign_cursor(
                    CursorState(last_key=last_key, direction="next", issued_at=now)
                )
            # Likewise a prev page exists if anything precedes first_key, and we
            # only offer it when not on the very first page.
            if request_cursor is not None and self._source.fetch_before(first_key, 1):
                prev_cursor = self._sign_cursor(
                    CursorState(last_key=first_key, direction="prev", issued_at=now)
                )

        return Page(
            items=items,
            next_cursor=next_cursor,
            prev_cursor=prev_cursor,
            total=self._source.count(),
        )

    def add_item(self, item: T) -> None:
        """Insert an item, keeping sort order and invalidating the cache."""
        with self._lock:
            self._source.insert(item)
            self._version += 1
            self._page_cache.clear()

    def remove_item_by_key(self, key: object) -> bool:
        """Remove by sort key. Returns True if removed."""
        with self._lock:
            removed = self._source.remove_by_key(key)
            if removed:
                self._version += 1
                self._page_cache.clear()
            return removed

    def total_count(self) -> int:
        """Exact count for the in-memory backend; approximate for a real DB."""
        with self._lock:
            return self._source.count()
```

---

## Example / Self-Test

```python
if __name__ == "__main__":
    # Items must have a unique comparable key.
    data = [{"id": i, "name": f"item-{i}"} for i in range(0, 50)]
    engine = CachePagingEngine(data, key_fn=lambda d: d["id"], max_page_size=10)

    # First page
    p1 = engine.get_page(page_size=5)
    assert [i["id"] for i in p1.items] == [0, 1, 2, 3, 4]
    assert p1.prev_cursor is None
    assert p1.next_cursor is not None

    # Forward
    p2 = engine.get_page(p1.next_cursor, page_size=5)
    assert [i["id"] for i in p2.items] == [5, 6, 7, 8, 9]
    assert p2.prev_cursor is not None  # backward navigation now works

    # Backward returns to the previous slice
    p_back = engine.get_page(p2.prev_cursor, page_size=5)
    assert [i["id"] for i in p_back.items] == [0, 1, 2, 3, 4]

    # MUTATION STABILITY: delete id=2 while user holds p1.next_cursor.
    engine.remove_item_by_key(2)
    p2_again = engine.get_page(p1.next_cursor, page_size=5)
    # Keyset cursor anchored at id=4 -> still continues correctly, NO skip/dup:
    assert [i["id"] for i in p2_again.items] == [5, 6, 7, 8, 9]

    # Page size clamp
    big = engine.get_page(page_size=9999)
    assert len(big.items) == 10  # clamped to max_page_size

    # Tamper detection
    try:
        engine.get_page("not-a-real-cursor")
        assert False
    except InvalidCursorError:
        pass

    print("All assertions passed.")
```

---

## Design Decisions & Tradeoffs

**1. Keyset over offset (the core fix).**
Offset pagination (`items[start:end]`) is O(n) to skip and *unstable*: deleting item 2 shifts everything, so page 2 silently skips an item. Keyset pagination anchors on the last-seen key (`WHERE key > last_key`). Binary search gives **O(log n + page_size)** per page and the user never sees skips/dupes from edits *outside their window*. Tradeoff: requires a unique, ordered key and you can't jump to "page N".

**2. Cache correctness via versioning.**
I bump a `_version` counter on every mutation and namespace cache keys with it, effectively invalidating all cached pages. This favors **correctness over hit rate** — stale pages would otherwise show deleted items. For a higher hit-rate variant you'd invalidate only affected key-ranges, but that's far more complex and error-prone. I chose simple-and-correct.

**3. LRU bound.** Unbounded caching under "hundreds of concurrent requests" is a memory leak. `OrderedDict` + `popitem(last=False)` gives O(1) LRU.

**4. Security hardening.** `hmac.compare_digest` (constant-time), SHA-256, length-prefixed payload (the original `split(":")` breaks if the payload contains `:`), and a TTL so leaked cursors expire. Cursors are fully opaque — they encode a key + direction + timestamp, signed, so position can't be reverse-engineered or forged.

**5. `DataSource` protocol.** Decouples pagination logic from storage, directly addressing the (contradictory) "can't fit in memory" constraint — swap in a SQL/Redis source without touching cursor logic.

---

## Edge Cases Handled

| Case | Behavior |
|---|---|
| Empty dataset | Returns empty page, both cursors `None`. |
| Cursor past the end | `fetch_after` returns `[]`, no next cursor. |
| `prev` on first page | `prev_cursor` is `None`. |
| `page_size <= 0` | Raises `ValueError`. |
| `page_size > max` | Clamped silently. |
| Tampered/expired/malformed cursor | `InvalidCursorError`. |
| Item deleted that a held cursor pointed *at* | `bisect_right` still positions correctly relative to that key value; no crash, no skip of unrelated items. |
| Concurrent reads + writes | `RLock` serializes; cache invalidated on write. |
| Duplicate keys | **Not handled** — see limitations. |

---

## Limitations I'm Flagging (Underspecified)

1. **Non-unique keys** break keyset pagination (you'd need a composite tiebreaker like `(key, id)`). The spec never defines uniqueness, so I documented the `key_fn` requirement instead of guessing.
2. **`total` is exact** here because data is in memory; the spec says "approximate," which only makes sense for a DB backend — I noted this in `total_count`.
3. The provided **`remove_item(item)`** signature (by value) conflicts with keyset design; I exposed `remove_item_by_key` instead. **This is an interface change I'd confirm with the requester.**

**Recommendation: ☑ Adjust** — the interface (`List[T]` in memory + "can't fit in memory" + value-based removal + no sort key) is internally contradictory and needs clarification before finalizing.