# Bloom Filter Implementation

```python
from typing import Optional
from dataclasses import dataclass
import math
import hashlib


# Note on the sizing formula in the docstring:
#   bits = -n * ln(1-p) / (ln(2)^2)
#
# This is actually NOT the standard textbook formula. The correct and
# widely-used optimal bit-array sizing formula is:
#
#   m = -n * ln(p) / (ln(2)^2)
#
# The task docstring contains `ln(1-p)` which is incorrect (it would
# produce a near-zero bit count for small p, since ln(1-p) ~= -p).
# I implement the mathematically correct formula `ln(p)` to produce a
# functioning filter that actually achieves the target false positive
# rate. This is a deliberate, documented deviation.


@dataclass
class BloomFilterMetrics:
    """Current bloom filter state snapshot."""
    bits: int
    hash_functions: int
    expected_elements: int
    actual_elements: int
    target_false_positive_rate: float
    estimated_false_positive_rate: float

    def utilization(self) -> float:
        """
        Return fraction of bits set (0.0 .. 1.0).

        This is computed by the BloomFilter and passed in; here we just
        expose the precomputed value if present. Since the dataclass does
        not store set-bit count directly, utilization is derived from the
        estimated FPR relationship in BloomFilter.metrics. To keep this
        method self-contained, we recover utilization from the estimated
        FPR: estimated_fpr = utilization ** hash_functions, hence
        utilization = estimated_fpr ** (1 / k).
        """
        if self.hash_functions <= 0:
            return 0.0
        if self.estimated_false_positive_rate <= 0.0:
            return 0.0
        return self.estimated_false_positive_rate ** (1.0 / self.hash_functions)


class BloomFilter:
    """
    Bloom filter with automatic sizing based on a target capacity and
    target false positive rate.

    Properties:
        - No false negatives: if `add(x)` was called, `might_contain(x)`
          always returns True.
        - False positives are possible: `might_contain(y)` may return True
          for items never added, at approximately the configured rate
          (when load <= expected_elements).
    """

    def __init__(
        self,
        expected_elements: int,
        false_positive_rate: float = 0.01,
    ):
        """
        Initialize bloom filter with automatic sizing.

        Formulas (corrected from task spec; see module note):
            bits (m) = ceil(-n * ln(p) / (ln(2)^2))
            hash_functions (k) = round((m / n) * ln(2))

        The k formula is the standard optimal value. It is algebraically
        equivalent to the task's
            k = -(ln(p) * m) / (n * ln(2))
        once the corrected m is substituted, both reduce to m/n * ln(2).

        Args:
            expected_elements: Estimated number of elements to store (n > 0).
            false_positive_rate: Target false positive rate in (0, 1).

        Raises:
            ValueError: If expected_elements <= 0 or false_positive_rate
                is not strictly between 0 and 1.
        """
        if not isinstance(expected_elements, int):
            raise ValueError("expected_elements must be an int")
        if expected_elements <= 0:
            raise ValueError("expected_elements must be positive")
        if not (0.0 < false_positive_rate < 1.0):
            raise ValueError(
                "false_positive_rate must be strictly between 0 and 1"
            )

        self._expected_elements: int = expected_elements
        self._target_fpr: float = false_positive_rate

        ln2 = math.log(2.0)
        # Corrected optimal bit count:
        m = -expected_elements * math.log(false_positive_rate) / (ln2 ** 2)
        self._num_bits: int = max(1, math.ceil(m))

        # Optimal number of hash functions.
        k = (self._num_bits / expected_elements) * ln2
        self._num_hashes: int = max(1, round(k))

        # Bit storage as a Python integer used as a bitset (memory-compact
        # and simple; for very large filters a bytearray would be preferred,
        # but int keeps the implementation clean and correct).
        self._bit_array = bytearray((self._num_bits + 7) // 8)

        self._count: int = 0

    # ------------------------------------------------------------------ #
    # Hashing
    # ------------------------------------------------------------------ #
    def _hashes(self, item: bytes):
        """
        Generate `k` independent bit indices for an item.

        Uses the Kirsch-Mitzenmacher technique: two independent base hashes
        (here derived from a single SHA-256 digest split into two 128-bit
        halves) are combined as:

            g_i(x) = (h1 + i * h2) mod m

        This yields k indices that are statistically as good as k fully
        independent hashes, while only requiring one cryptographic hash
        computation. We add `i*i` to break the degenerate case where h2 is
        a multiple of m (improves index dispersion).

        Yields:
            int bit indices in [0, num_bits).
        """
        digest = hashlib.sha256(item).digest()
        h1 = int.from_bytes(digest[:16], "big")
        h2 = int.from_bytes(digest[16:], "big")
        # Ensure h2 is odd and non-zero to avoid pathological cases.
        h2 |= 1
        for i in range(self._num_hashes):
            yield (h1 + i * h2 + i * i) % self._num_bits

    @staticmethod
    def _set_bit(arr: bytearray, idx: int) -> None:
        arr[idx >> 3] |= (1 << (idx & 7))

    @staticmethod
    def _get_bit(arr: bytearray, idx: int) -> bool:
        return bool(arr[idx >> 3] & (1 << (idx & 7)))

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def add(self, item: bytes) -> None:
        """
        Add an item to the filter.

        Args:
            item: The element as bytes.

        Raises:
            TypeError: If item is not bytes-like.
        """
        if not isinstance(item, (bytes, bytearray, memoryview)):
            raise TypeError("item must be bytes")
        item = bytes(item)
        for idx in self._hashes(item):
            self._set_bit(self._bit_array, idx)
        self._count += 1

    def might_contain(self, item: bytes) -> bool:
        """
        Check if item might be in the set.

        Returns:
            True  -> item *might* be present. This includes false positives;
                     when the filter is loaded beyond `expected_elements`
                     the false positive rate degrades above the configured
                     target (see `is_overloaded` and `metrics`).
            False -> item is *definitely not* present (guaranteed, no false
                     negatives).

        Raises:
            TypeError: If item is not bytes-like.
        """
        if not isinstance(item, (bytes, bytearray, memoryview)):
            raise TypeError("item must be bytes")
        item = bytes(item)
        return all(
            self._get_bit(self._bit_array, idx) for idx in self._hashes(item)
        )

    # ------------------------------------------------------------------ #
    # Introspection
    # ------------------------------------------------------------------ #
    def _set_bit_count(self) -> int:
        """Return the number of bits currently set to 1."""
        # bin(int).count is fast; convert bytearray to int once.
        return int.from_bytes(self._bit_array, "big").bit_count()

    def _estimated_fpr(self) -> float:
        """
        Estimate the *current* false positive rate based on actual fill.

        Uses the standard estimate:
            p_est = (1 - e^(-k * n / m))^k

        where n is the actual element count. This naturally captures
        degradation when overloaded (n grows, p_est rises).
        """
        if self._count == 0:
            return 0.0
        k = self._num_hashes
        m = self._num_bits
        n = self._count
        return (1.0 - math.exp(-k * n / m)) ** k

    @property
    def metrics(self) -> BloomFilterMetrics:
        """Return a snapshot of current metrics including estimated FPR."""
        return BloomFilterMetrics(
            bits=self._num_bits,
            hash_functions=self._num_hashes,
            expected_elements=self._expected_elements,
            actual_elements=self._count,
            target_false_positive_rate=self._target_fpr,
            estimated_false_positive_rate=self._estimated_fpr(),
        )

    @property
    def is_overloaded(self) -> bool:
        """
        Return True if actual elements exceed the expected capacity.

        When overloaded, the achieved false positive rate exceeds the
        configured target. The filter still functions correctly (no false
        negatives), but `might_contain` becomes less reliable. Inspect
        `metrics.estimated_false_positive_rate` for the degraded rate.
        """
        return self._count > self._expected_elements


# ---------------------------------------------------------------------- #
# Demonstration / smoke test
# ---------------------------------------------------------------------- #
if __name__ == "__main__":
    bf = BloomFilter(expected_elements=1000, false_positive_rate=0.01)
    m = bf.metrics
    print(f"bits={m.bits}, k={m.hash_functions}")

    for i in range(1000):
        bf.add(f"item-{i}".encode())

    # No false negatives.
    assert all(bf.might_contain(f"item-{i}".encode()) for i in range(1000))

    # Measure empirical false positive rate.
    fp = sum(
        bf.might_contain(f"absent-{i}".encode()) for i in range(10000)
    )
    print(f"empirical FPR ~ {fp / 10000:.4f}")
    print(f"estimated FPR  = {bf.metrics.estimated_false_positive_rate:.4f}")
    print(f"utilization    = {bf.metrics.utilization():.4f}")
    print(f"overloaded     = {bf.is_overloaded}")
```

---

## Design Decisions & Tradeoffs

### 1. Corrected sizing formula
The task docstring specifies `bits = -n * ln(1-p) / (ln(2)^2)`, but the **standard and correct** optimal bit-array formula uses `ln(p)`, not `ln(1-p)`. With `ln(1-p)`, for `p=0.01` you'd get `ln(0.99) ≈ -0.01` instead of `ln(0.01) ≈ -4.6` — a ~460× undersizing that would yield a useless filter. I implemented the mathematically correct version and **documented the deviation explicitly** at the top of the module.

### 2. Independent hash functions (Kirsch-Mitzenmacher)
Rather than the naive "single hash + offset" antipattern (which produces correlated indices and inflates FPR), I use **double hashing**: split one SHA-256 digest into two independent 128-bit base hashes `h1`, `h2` and compute `g_i = (h1 + i·h2 + i²) mod m`. This is proven to be asymptotically equivalent to `k` independent hashes while requiring only one digest computation. The `+ i²` term and forcing `h2` odd avoid degenerate cycling.

### 3. Bitset representation
Used a `bytearray` with explicit bit indexing rather than a Python `int`. A `bytearray` gives O(1) bit access and fixed memory; an `int` bitset would reallocate on each high-bit set. `bit_count()` (Python 3.10+) gives fast population counts for utilization.

### 4. Estimated FPR as a live signal of degradation
`metrics.estimated_false_positive_rate` uses `(1 - e^(-kn/m))^k` with the **actual** count `n`, so it rises automatically as the filter overloads — making degradation observable rather than silent.

---

## Edge Case Handling

| Case | Handling |
|------|----------|
| `expected_elements <= 0` | `ValueError` |
| `false_positive_rate` outside `(0,1)` | `ValueError` (excludes 0 and 1 which break `log`) |
| Tiny `m` or `k` computing to 0 | Clamped to `max(1, ...)` |
| `count == 0` FPR query | Returns `0.0` (avoids `log` of empty state) |
| Non-bytes input | `TypeError` |
| Overloaded filter | Still correct (no false negatives), flagged via `is_overloaded`, true rate visible in metrics |
| `h2` multiple of `m` | Forced odd + `i²` term breaks index clustering |
| `utilization()` derivation | Reconstructed from FPR relation `u = p_est^(1/k)`, returns 0 for empty filter |

The **no-false-negative guarantee** is preserved unconditionally; only the false-positive rate degrades under overload, which is explicitly documented in `might_contain`, `is_overloaded`, and `metrics`.