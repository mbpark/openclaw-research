# Cache-Based Pagination with Cursor Support

Before diving into the implementation, I want to flag the **underspecified aspects** of this problem, then provide a robust implementation that handles the ambiguities defensively.

## Critical Questions the Spec Doesn't Answer

The reference implementation has several bugs that stem from genuine ambiguity in the requirements. I'll call these out because guessing here leads to incorrect behavior:

1. **What is the stable ordering key?** Offset-based cursors are fundamentally broken under mutation. If item at index 2 is deleted, every cursor pointing past it now skips/duplicates an item. The spec says "handle items being added/removed during pagination" but offset cursors *cannot* do this correctly. **I assume items have a stable, orderable ID.** If not, this requirement is unsatisfiable.

2. **What does "cache" mean here?** The provided `_page_cache` is never used. Is the cache meant to (a) snapshot results so concurrent requesters see consistency, or (b) speed up repeated cursor lookups? **I assume (a): cache materialized page slices keyed by cursor, with TTL eviction.**

3. **What is the data source?** "Can't fit all in memory" contradicts `items: List[T]` (already fully in memory). **I assume a fetch callback for the real source, with `List` as a fallback adapter.**

4. **Should cursors expire?** `timestamp` is stored but never validated. **I assume yes, with a configurable TTL.**

5. **Backward pagination correctness?** The reference's `prev_cursor` logic is broken (it just echoes the input cursor). I implement true bidirectional navigation.

I'll state these assumptions explicitly in the code and make them configurable.

---

## Implementation

```python
from __future__ import annotations

from typing import (
    Callable,
    Generic,
    List,
    Optional,
    Protocol,
    Sequence,
    TypeVar,
    runtime_checkable,
)
from dataclasses import dataclass, asdict
import base64
import json
import time
import hmac
import hashlib
import secrets
import threading

T = TypeVar("T")
K = TypeVar("K")  # ordering-key type (must be JSON-serializable & comparable)


# --------------------------------------------------------------------------- #
# Data structures
# --------------------------------------------------------------------------- #
@dataclass
class Page(Generic[T]):
    """A single page of results plus navigation cursors."""
    items: List[T]
    next_cursor: Optional[str]
    prev_cursor: Optional[str]
    total: int  # approximate; the dataset may mutate concurrently


@dataclass
class CursorState:
    """
    Internal, *signed* cursor payload.

    We key off a stable ordering value (`last_key`) rather than a numeric
    offset. This is the single most important design decision: keyset
    pagination is the only correct approach when items can be inserted or
    deleted mid-traversal, because a key is not invalidated by changes to
    *other* rows.
    """
    issued_at: float
    last_key: object        # boundary key of the page just returned
    direction: str          # "next" or "prev"
    inclusive: bool = False  # whether `last_key` itself should be included


# --------------------------------------------------------------------------- #
# Data source abstraction
# --------------------------------------------------------------------------- #
@runtime_checkable
class KeyedSource(Protocol[T]):
    """
    Abstraction over the *real* backing store. This is what makes the
    'thousands of items, can't fit in memory' constraint satisfiable: the
    engine only ever asks for a bounded slice.
    """

    def fetch_after(self, key: Optional[object], limit: int) -> List[T]:
        """Return up to `limit` items with key strictly greater than `key`
        (or from the start when `key is None`), in ascending key order."""
        ...

    def fetch_before(self, key: object, limit: int) -> List[T]:
        """Return up to `limit` items with key strictly less than `key`,
        in ascending key order (closest-to-key last)."""
        ...

    def approx_total(self) -> int:
        """Approximate total count (cheap; may be stale)."""
        ...


class ListSource(Generic[T], KeyedSource[T]):
    """
    In-memory adapter so the engine works with a plain ``List[T]`` while
    keeping the keyset contract. Suitable for tests / small datasets.

    For real large datasets, implement ``KeyedSource`` against your DB using
    ``WHERE key > ? ORDER BY key LIMIT ?`` which is O(log n + page_size).
    """

    def __init__(self, items: List[T], key_fn: Callable[[T], object]):
        self._items = items
        self._key_fn = key_fn
        self._lock = threading.RLock()

    def _sorted(self) -> List[T]:
        # Keep deterministic ordering; cost O(n log n). A production source
        # would maintain a sorted index instead.
        return sorted(self._items, key=self._key_fn)

    def fetch_after(self, key: Optional[object], limit: int) -> List[T]:
        with self._lock:
            data = self._sorted()
            if key is None:
                return data[:limit]
            return [it for it in data if self._key_fn(it) > key][:limit]

    def fetch_before(self, key: object, limit: int) -> List[T]:
        with self._lock:
            data = self._sorted()
            before = [it for it in data if self._key_fn(it) < key]
            return before[-limit:]  # ascending, closest to key last

    def approx_total(self) -> int:
        with self._lock:
            return len(self._items)

    # mutation helpers ------------------------------------------------------ #
    def add(self, item: T) -> None:
        with self._lock:
            self._items.append(item)

    def remove(self, item: T) -> bool:
        with self._lock:
            try:
                self._items.remove(item)
                return True
            except ValueError:
                return False


# --------------------------------------------------------------------------- #
# Page cache
# --------------------------------------------------------------------------- #
@dataclass
class _CacheEntry(Generic[T]):
    page: Page[T]
    expires_at: float


class _PageCache(Generic[T]):
    """
    TTL cache keyed by (cursor, page_size). Provides *read consistency* for
    bursts of concurrent identical requests (e.g. a UI re-fetching the same
    page) and reduces load on the backing source.

    NOTE: cached pages are intentionally short-lived because the dataset
    mutates; a stale page is acceptable within the TTL window, which is the
    standard tradeoff for cursor pagination.
    """

    def __init__(self, ttl_seconds: float, max_entries: int):
        self._ttl = ttl_seconds
        self._max = max_entries
        self._store: dict[str, _CacheEntry[T]] = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Page[T]]:
        now = time.monotonic()
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if entry.expires_at < now:
                self._store.pop(key, None)
                return None
            return entry.page

    def put(self, key: str, page: Page[T]) -> None:
        now = time.monotonic()
        with self._lock:
            if len(self._store) >= self._max:
                self._evict_locked(now)
            self._store[key] = _CacheEntry(page, now + self._ttl)

    def _evict_locked(self, now: float) -> None:
        # First drop expired entries; if still full, drop oldest.
        expired = [k for k, e in self._store.items() if e.expires_at < now]
        for k in expired:
            self._store.pop(k, None)
        if len(self._store) >= self._max:
            oldest = min(self._store, key=lambda k: self._store[k].expires_at)
            self._store.pop(oldest, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


# --------------------------------------------------------------------------- #
# Engine
# --------------------------------------------------------------------------- #
class CachePagingEngine(Generic[T]):
    """
    Cached, cursor-based pagination engine using *keyset* (seek) pagination.

    Design summary
    --------------
    * Cursors encode a stable ordering key, not an offset -> correct under
      concurrent insert/delete (mutations to other rows never shift a key).
    * Cursors are opaque: base64(JSON payload + HMAC-SHA256). Tampering or
      forging is detected; the position is not human-readable.
    * Cursors carry a TTL so leaked/old cursors stop working.
    * A short-TTL page cache absorbs duplicate concurrent reads.
    * All public methods are thread-safe.

    Assumptions (documented because the task is underspecified)
    -----------------------------------------------------------
    * Items have a stable, JSON-serializable, comparable ordering key,
      provided via `key_fn`. Without this, mutation-safe pagination is
      impossible; we fall back to identity which is only safe for hashable,
      stably-ordered values.
    """

    def __init__(
        self,
        items: Optional[List[T]] = None,
        *,
        source: Optional[KeyedSource[T]] = None,
        key_fn: Optional[Callable[[T], object]] = None,
        max_page_size: int = 100,
        cursor_ttl_seconds: float = 3600.0,
        cache_ttl_seconds: float = 2.0,
        cache_max_entries: int = 1024,
    ):
        if max_page_size < 1:
            raise ValueError("max_page_size must be >= 1")

        # Resolve data source.
        if source is not None and items is not None:
            raise ValueError("Provide either `items` or `source`, not both")
        if source is None:
            key = key_fn or (lambda x: x)  # identity fallback (see docstring)
            self._source: KeyedSource[T] = ListSource(items or [], key)
            self._key_fn = key
        else:
            if key_fn is None:
                raise ValueError("`key_fn` is required with a custom source")
            self._source = source
            self._key_fn = key_fn

        self._max_page_size = max_page_size
        self._cursor_ttl = cursor_ttl_seconds
        self._secret = secrets.token_bytes(32)
        self._cache: _PageCache[T] = _PageCache(
            cache_ttl_seconds, cache_max_entries
        )
        self._lock = threading.RLock()

    # ------------------------------------------------------------------ #
    # Cursor codec
    # ------------------------------------------------------------------ #
    def _sign_cursor(self, state: CursorState) -> str:
        """Create an opaque, tamper-evident cursor string."""
        raw = json.dumps(asdict(state), sort_keys=True, separators=(",", ":"))
        raw_b = raw.encode("utf-8")
        sig = hmac.new(self._secret, raw_b, hashlib.sha256).digest()
        # base64url so the cursor is URL-safe.
        payload = base64.urlsafe_b64encode(raw_b).decode("ascii")
        signature = base64.urlsafe_b64encode(sig).decode("ascii")
        return f"{payload}.{signature}"

    def _decode_cursor(self, cursor_str: str) -> Optional[CursorState]:
        """Decode, verify signature, and check expiry. Returns None on any
        failure (invalid, tampered, malformed, expired)."""
        try:
            payload_b64, sig_b64 = cursor_str.split(".", 1)
            raw_b = base64.urlsafe_b64decode(payload_b64.encode("ascii"))
            got_sig = base64.urlsafe_b64decode(sig_b64.encode("ascii"))
        except Exception:
            return None

        expected_sig = hmac.new(self._secret, raw_b, hashlib.sha256).digest()
        # Constant-time comparison to avoid timing oracles.
        if not hmac.compare_digest(got_sig, expected_sig):
            return None

        try:
            data = json.loads(raw_b.decode("utf-8"))
            state = CursorState(**data)
        except Exception:
            return None

        if state.direction not in ("next", "prev"):
            return None
        if (time.time() - state.issued_at) > self._cursor_ttl:
            return None  # expired
        return state

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def get_page(
        self,
        cursor: Optional[str] = None,
        page_size: int = 20,
    ) -> Page[T]:
        """
        Fetch a page.

        Parameters
        ----------
        cursor:
            None for the first page; otherwise an opaque cursor from a
            previous ``next_cursor``/``prev_cursor``.
        page_size:
            Requested size; clamped to ``[1, max_page_size]``.

        Returns
        -------
        Page[T]
            Items in ascending key order, plus navigation cursors.

        Raises
        ------
        ValueError
            If the cursor is invalid, forged, or expired. (We treat these
            uniformly so callers can't probe the secret.)

        Complexity
        ----------
        With a proper keyset ``KeyedSource`` (e.g. indexed DB query) this is
        O(log n + page_size) and never rescans from the start. The in-memory
        ``ListSource`` is O(n log n) only because it lacks a maintained index.
        """
        # Clamp page size to a valid range (boundary + DoS protection).
        page_size = max(1, min(page_size, self._max_page_size))

        # Decode cursor up front so an invalid cursor never hits the cache.
        state: Optional[CursorState] = None
        if cursor is not None:
            state = self._decode_cursor(cursor)
            if state is None:
                raise ValueError("Invalid, forged, or expired cursor")

        cache_key = f"{cursor or 'FIRST'}|{page_size}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        with self._lock:
            # Double-check cache inside the lock (single-flight-ish).
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached

            page = self._build_page(state, page_size)
            self._cache.put(cache_key, page)
            return page

    def _build_page(
        self, state: Optional[CursorState], page_size: int
    ) -> Page[T]:
        """Core keyset fetch logic for forward and backward navigation."""
        # Fetch page_size + 1 to detect whether a further page exists
        # without a second query.
        probe = page_size + 1

        if state is None:
            # First page.
            rows = self._source.fetch_after(None, probe)
        elif state.direction == "next":
            rows = self._source.fetch_after(state.last_key, probe)
        else:  # "prev"
            # Walk backward, then re-orient to ascending order.
            rows = self._source.fetch_before(state.last_key, probe)

        # Determine "has more" in the direction of travel.
        has_more = len(rows) > page_size

        if state is not None and state.direction == "prev":
            # We over-fetched from the *front*; trim the extra from the start.
            items = rows[-page_size:] if has_more else rows
        else:
            items = rows[:page_size]

        next_cursor: Optional[str] = None
        prev_cursor: Optional[str] = None

        if items:
            first_key = self._key_fn(items[0])
            last_key = self._key_fn(items[-1])

            # A "next" cursor exists if either we proved more rows ahead,
            # or we arrived here going backward (so forward must exist).
            going_back = state is not None and state.direction == "prev"
            if (state is None or state.direction == "next"):
                if has_more:
                    next_cursor = self._sign_cursor(
                        CursorState(time.time(), last_key, "next")
                    )
            else:  # came from prev
                next_cursor = self._sign_cursor(
                    CursorState(time.time(), last_key, "next")
                )

            # A "prev" cursor exists if we're not on the first page.
            on_first_page = state is None
            if not on_first_page:
                if going_back:
                    if has_more:
                        prev_cursor = self._sign_cursor(
                            CursorState(time.time(), first_key, "prev")
                        )
                else:  # we moved forward, so a backward page exists
                    prev_cursor = self._sign_cursor(
                        CursorState(time.time(), first_key, "prev")
                    )

        return Page(
            items=items,
            next_cursor=next_cursor,
            prev_cursor=prev_cursor,
            total=self._source.approx_total(),
        )

    # ------------------------------------------------------------------ #
    # Mutation API (only valid for the in-memory ListSource adapter)
    # ------------------------------------------------------------------ #
    def add_item(self, item: T) -> None:
        """Add an item. Invalidates the page cache (data changed)."""
        if not isinstance(self._source, ListSource):
            raise NotImplementedError("Mutations require the ListSource adapter")
        self._source.add(item)
        self._cache.clear()

    def remove_item(self, item: T) -> bool:
        """Remove an item; returns True if it was present."""
        if not isinstance(self._source, ListSource):
            raise NotImplementedError("Mutations require the ListSource adapter")
        removed = self._source.remove(item)
        if removed:
            self._cache.clear()
        return removed

    def total_count(self) -> int:
        """Approximate total item count."""
        return self._source.approx_total()
```

---

## Quick Demonstration

```python
if __name__ == "__main__":
    eng = CachePagingEngine(items=list(range(1, 51)), key_fn=lambda x: x)

    p1 = eng.get_page(page_size=10)
    print("page1:", p1.items)                  # [1..10]

    p2 = eng.get_page(p1.next_cursor, page_size=10)
    print("page2:", p2.items)                  # [11..20]

    back = eng.get_page(p2.prev_cursor, page_size=10)
    print("back  :", back.items)               # [1..10]  (true backward nav)

    # Mutation mid-traversal: delete an item we already passed.
    eng.remove_item(5)
    p3 = eng.get_page(p2.next_cursor, page_size=10)
    print("page3:", p3.items)                  # [21..30] -> NO skip/dup

    # Opaque + tamper-proof
    try:
        eng.get_page("not-a-real-cursor")
    except ValueError as e:
        print("rejected:", e)
```

---

## Design Decisions & Tradeoffs

| Decision | Why | Tradeoff |
|---|---|---|
| **Keyset over offset cursors** | Offset cursors duplicate/skip items on insert/delete. Keys are immune to mutations of *other* rows. | Requires a comparable key; can't jump to arbitrary page N. |
| **HMAC-SHA256 + base64url** | Opaque, tamper-evident, URL-safe. `compare_digest` prevents timing attacks. | Cursor grows with key size; secret is per-process (cursors die on restart — acceptable, or externalize the secret). |
| **`KeyedSource` abstraction** | Resolves the "can't fit in memory" contradiction — engine only fetches bounded slices (`page_size + 1`). | Caller must implement an efficient source for true O(log n) behavior. |
| **Fetch `page_size + 1`** | Detects "has next page" in one query, no extra COUNT. | One extra row fetched. |
| **Short-TTL page cache** | Absorbs bursty identical concurrent reads; double-checked under lock. | Possible stale read within TTL — standard pagination tradeoff; cleared on mutation. |
| **Cursor TTL** | Old/leaked cursors expire. | Long-lived sessions may need refresh. |

## Edge Cases Handled

- **Past end / before start** → empty `fetch_*` result, `next/prev_cursor = None`.
- **Invalid/forged/tampered/expired cursor** → uniform `ValueError` (no info leak).
- **`page_size` ≤ 0 or > max** → clamped to `[1, max_page_size]`.
- **Mutation mid-traversal** → keyset cursors stay valid; cache invalidated.
- **Concurrency** → `RLock` on engine, source, and cache; constant-time sig check.
- **Empty dataset** → empty page, both cursors `None`.

## Bugs in the Reference (for the record)

1. `prev_cursor = cursor` just echoes the input — not real backward nav.
2. `timestamp` stored but never validated → no expiry.
3. `_page_cache` declared but **never used**.
4. Offset cursors **break** the stated mutation requirement.
5. `json.dumps(state.__dict__)` then `split(":")` corrupts on any `:` inside data.

---

**Checkpoint 4 Recommendation:** ☑ **Adjust** — the original interface's offset-based, mutation-unsafe design cannot meet its own stated constraints. I'd confirm the **ordering-key** and **cache-purpose** assumptions with the requester before locking the interface, since both materially change the contract.