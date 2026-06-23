# Re-verification and Small Sample Testing Infrastructure

Chunked test runner system to avoid LLM timeouts by breaking large test suites into small batches.

## Quick Start

```bash
cd documents/research/claude_tests

# Re-verification with small sample (20 tests)
python3 reverification/run_chunked_injection_tests.py --sample 20

# Full re-verification (70 tests)
python3 reverification/run_chunked_injection_tests.py

# Implementation tests
python3 reverification/run_chunked_implementation_tests.py --sample 5

# Structured output tests (small)
python3 reverification/run_chunked_structured_output.py --sample 20

# Scoring
python3 reverification/run_batched_scoring.py --input claude_results/injection_reverification_20260609/
```

## Design Principles

1. **Small batches** (3-10 tests each) - Completes before timeout
2. **Resume capability** - Pick up where interrupted
3. **Progress tracking** - File-based state persistence
4. **Sampling options** - Run 10-20 test subsets
5. **Category filtering** - Target specific test groups

## File Structure

```
reverification/
├── common.py                  # Shared utilities, progress tracking
├── test_vectors.py            # All 70 injection vectors + sampling
├── run_chunked_injection_tests.py   # Injection test runner
├── run_chunked_implementation_tests.py  # Implementation test runner  
├── run_chunked_structured_output.py   # Structured output tests
├── run_batched_scoring.py       # Scoring and analysis
└── README.md                  # This file
```

## Usage Examples

### Run targeted category verification
```bash
python3 run_chunked_injection_tests.py --category "Logical Paradoxes"
```

### Small sample implementation test
```bash
python3 run_chunked_implementation_tests.py --sample 5 --batch 2
```

### Score with randomization
```bash
python3 run_batched_scoring.py --input results/ --method randomized --sample 20
```

## Advantages Over Original Scripts

| Feature | Original | Chunked |
|---------|----------|---------|
| Batch size | 70 tests (one shot) | 3-10 per batch |
| Timeout handling | All lost | Resume from checkpoint |
| Progress tracking | None | JSON state file |
| Sample sizes | Only full suite | 10-70 test samples |
| Category filtering | No | Yes |
