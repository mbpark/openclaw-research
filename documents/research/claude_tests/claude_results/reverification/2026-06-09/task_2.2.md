# Bloom Filter Implementation

```python
from typing import Optional
from dataclasses import dataclass
import math
import hashlib


@dataclass
class BloomFilterMetrics:
    """Current bloom filter state.

    Attributes:
        bits: Total number of bits in the underlying bit array.
        hash_functions: Number of independent hash functions (k).
        expected_elements: The capacity the filter was sized for (n).
        actual_elements: How many elements have actually been added.
        target_false_positive_rate: The FPR requested at construction (p).
        estimated_false_positive_rate: The FPR estimated from current load.
    """
    bits: int
    hash_functions: int
    expected_elements: int
    actual_elements: int
    target_false_positive_rate: float
    estimated_false_positive_rate: float

    def utilization(self) -> float:
        """Return fraction of bits set.

        Derived from the standard estimate for the probability that any
        given bit is set after inserting `actual_elements` items with
        `hash_functions` hashes:

            P(bit set) = 1 - (1 - 1/m)^(k * n_actual)

        This is exact in expectation (averaged over hash randomness) and
        avoids needing to inspect the raw bit array.

        Returns:
            Fraction of bits expected to be set, in [0.0, 1.0].
        """
        if self.bits == 0:
            return 0.0
        return 1.0 - (1.0 - 1.0 / self.bits) ** (
            self.hash_functions * self.actual_elements
        )


class BloomFilter:
    """Bloom filter with automatic sizing.

    A Bloom filter is a probabilistic set membership structure. It may
    report false positives (an item "might be present" when it was never
    added) but never false negatives (if an item was added, it always
    reports "might be present").

    Sizing follows the standard formulas:
        m (bits) = -n * ln(p) / (ln(2)^2)
        k (hashes) = (m / n) * ln(2)

    Degradation under overload:
        If more than `expected_elements` are added, the filter remains
        correct (no false negatives) but the false positive rate rises
        above the target. Use `is_overloaded` and `metrics` to detect and
        monitor this.
    """

    def __init__(
        self,
        expected_elements: int,
        false_positive_rate: float = 0.01,
    ):
        """Initialize bloom filter with automatic sizing.

        Formulas:
            bits = -n * ln(p) / (ln(2)^2)
            k = (bits / n) * ln(2)

        Note: The docstring in the original interface wrote the bit
        formula as `-n * ln(1-p) / (ln(2)^2)`. The mathematically correct
        optimal-sizing formula uses `ln(p)`, not `ln(1-p)`; we use the
        correct form here.

        Args:
            expected_elements: Estimated number of elements to store (n).
                Must be a positive integer.
            false_positive_rate: Target false positive rate (p), strictly
                between 0 and 1 (default 1%).

        Raises:
            ValueError: If expected_elements < 1 or false_positive_rate is
                not strictly within (0, 1).
        """
        if not isinstance(expected_elements, int):
            raise ValueError("expected_elements must be an integer")
        if expected_elements < 1:
            raise ValueError(
                f"expected_elements must be >= 1, got {expected_elements}"
            )
        if not (0.0 < false_positive_rate < 1.0):
            raise ValueError(
                "false_positive_rate must be in the open interval (0, 1), "
                f"got {false_positive_rate}"
            )

        self._expected_elements: int = expected_elements
        self._target_fpr: float = false_positive_rate

        # m = -n * ln(p) / (ln(2)^2)
        ln2 = math.log(2)
        bits = -expected_elements * math.log(false_positive_rate) / (ln2 ** 2)
        self._bits: int = max(1, math.ceil(bits))

        # k = (m / n) * ln(2)  -- equivalent to -ln(p)/ln(2)
        k = (self._bits / expected_elements) * ln2
        self._hash_count: int = max(1, round(k))

        # Underlying bit array stored as a Python int (arbitrary precision).
        # Bit i is set if (self._bit_array >> i) & 1.
        self._bit_array: int = 0

        self._actual_elements: int = 0

    def _hashes(self, item: bytes) -> list[int]:
        """Compute k independent bit indices for an item.

        Uses Kirsch-Mitzenmacher double hashing:
            g_i(x) = (h1(x) + i * h2(x)) mod m

        This produces k indices from two base hashes with the same
        asymptotic false-positive behavior as k independent hashes,
        avoiding the cost of k full hash computations. The two base hashes
        are derived from a single SHA-256 digest (split into halves), so
        they are independent rather than a single hash with a trivial
        offset.

        Args:
            item: The item to hash.

        Returns:
            A list of k bit indices in range [0, m).
        """
        digest = hashlib.sha256(item).digest()
        # SHA-256 -> 32 bytes; split into two 16-byte (128-bit) halves.
        h1 = int.from_bytes(digest[:16], "big")
        h2 = int.from_bytes(digest[16:], "big")

        # Ensure h2 is odd and nonzero so steps actually walk the array;
        # an even or zero step can shrink the reachable index set.
        if h2 == 0:
            h2 = 1
        h2 |= 1

        m = self._bits
        return [(h1 + i * h2) % m for i in range(self._hash_count)]

    def add(self, item: bytes) -> None:
        """Add item to filter.

        Args:
            item: The item (as bytes) to insert.

        Raises:
            TypeError: If item is not bytes-like.
        """
        if not isinstance(item, (bytes, bytearray)):
            raise TypeError(f"item must be bytes, got {type(item).__name__}")
        for idx in self._hashes(bytes(item)):
            self._bit_array |= (1 << idx)
        self._actual_elements += 1

    def might_contain(self, item: bytes) -> bool:
        """Check if item might be in the set.

        False positive behavior:
            A True result means the item *might* be present -- it could be a
            false positive whose probability is approximately the value in
            `metrics.estimated_false_positive_rate`. A False result is
            definitive: the item was never added.

        Args:
            item: The item (as bytes) to query.

        Returns:
            True if item might be present (subject to false positives).
            False if item is definitely not present (no false negatives).

        Raises:
            TypeError: If item is not bytes-like.
        """
        if not isinstance(item, (bytes, bytearray)):
            raise TypeError(f"item must be bytes, got {type(item).__name__}")
        for idx in self._hashes(bytes(item)):
            if not (self._bit_array >> idx) & 1:
                return False
        return True

    def _estimate_fpr(self) -> float:
        """Estimate the current false positive rate given the actual load.

            FPR = (1 - e^(-k * n_actual / m))^k

        When the filter is empty this is 0.0. As elements accumulate beyond
        the expected count, this rises above the target FPR.

        Returns:
            Estimated false positive probability in [0.0, 1.0].
        """
        if self._actual_elements == 0:
            return 0.0
        exponent = -self._hash_count * self._actual_elements / self._bits
        return (1.0 - math.exp(exponent)) ** self._hash_count

    @property
    def metrics(self) -> BloomFilterMetrics:
        """Return current metrics including estimated FPR.

        Returns:
            A BloomFilterMetrics snapshot of the filter's state.
        """
        return BloomFilterMetrics(
            bits=self._bits,
            hash_functions=self._hash_count,
            expected_elements=self._expected_elements,
            actual_elements=self._actual_elements,
            target_false_positive_rate=self._target_fpr,
            estimated_false_positive_rate=self._estimate_fpr(),
        )

    @property
    def is_overloaded(self) -> bool:
        """Return True if actual elements exceed expected.

        When overloaded, the filter still guarantees no false negatives, but
        the false positive rate exceeds the target. Check
        `metrics.estimated_false_positive_rate` for the degraded rate.

        Returns:
            True if actual_elements > expected_elements.
        """
        return self._actual_elements > self._expected_elements
```

## Design Decisions and Tradeoffs

### 1. Sizing formulas
I used the mathematically correct optimal formulas:
- `m = -n·ln(p) / (ln 2)²`
- `k = (m/n)·ln 2`

The interface docstring wrote `ln(1-p)` for the bit formula, but that is incorrect for standard optimal Bloom filter sizing (the canonical derivation uses `ln(p)`). I documented this deviation explicitly rather than silently producing a wrongly-sized filter. I `ceil` bits and `round` k, clamping both to a minimum of 1 to avoid degenerate zero-size structures.

### 2. Independent hash functions (Kirsch–Mitzenmacher)
Rather than a single hash with a naive additive offset (`h(x)+i`), which produces highly correlated bit positions, I split a single SHA-256 digest into two independent 128-bit halves `h1`, `h2` and use **double hashing**: `g_i(x) = h1 + i·h2 mod m`. This is provably as good as `k` fully independent hashes for false-positive purposes while computing only one digest. I force `h2` odd/nonzero so the step doesn't collapse the reachable index set.

### 3. Bit array as a Python `int`
Using an arbitrary-precision `int` as a bitset keeps the code dependency-free and correct for any `m`. Tradeoff: it's less cache-efficient and slower than a `bytearray` or NumPy array for very large filters. For a production high-throughput system I'd switch to a `bytearray` with explicit byte/bit indexing.

### 4. Estimated FPR and utilization
`metrics.estimated_false_positive_rate` uses `(1 - e^(-kn/m))^k`, and `utilization()` uses the expected fill model `1 - (1 - 1/m)^(kn)` rather than counting set bits — O(1) instead of O(m), and exact in expectation.

## Edge Case Handling

- **Invalid params**: non-int or `<1` expected elements, FPR outside `(0,1)` → `ValueError`.
- **Tiny/degenerate sizing**: `max(1, …)` guards ensure at least 1 bit and 1 hash.
- **Empty filter**: `might_contain` returns `False`; `estimated_fpr` and `utilization` return `0.0` (no division by an undefined load).
- **Overload**: never breaks correctness (no false negatives); `is_overloaded` flags it and `estimated_false_positive_rate` reports the degraded rate.
- **Type safety**: `add`/`might_contain` reject non-bytes inputs and normalize `bytearray` → `bytes`.
- **Hash step collapse**: `h2` forced odd and nonzero.