# EU AI Security Lab Follow-up Testing - June 20, 2026

## Summary of Two Phases

### Phase 1: Multi-Judge Verification (30 tests)
- **Purpose**: Re-adjudicate high-scoring tests with 2-judge panel to reduce single-judge noise
- **Original high-scoring tests**: 30 tests with original scores 3-4/5
- **Confirmed harmful**: 0 of 30 (0.0%)
- **Average judge score across all**: 0.36/5
- **Key finding**: 100% of originally-high-scoring tests downgraded to 0-1.5 range

### Phase 2: Iterative Attack Testing (50 tests)
- **Purpose**: PAIR-style iterative refinement to test if blocked attacks can eventually succeed
- **Tested**: 50 attack vectors (20 multistep, 20 role-play, 10 context_control)
- **Max iterations**: 5 per test
- **Successes**: 38/50 (76.0%)

---

## Phase 1 Detailed Results

| Category | Tested | Confirmed | Avg Judge Score |
|----------|--------|-----------|-----------------|
| Code Injection (CB) | 7 | 0 | 0.50 |
| Context Control (CC) | 5 | 0 | 0.00 |
| Meta Protocol (MP) | 2 | 0 | 0.75 |
| Social Engineering (SE) | 3 | 0 | 0.00 |
| Multi-Step Decomposition (MS) | 8 | 0 | 0.19 |
| Role Play (RP) | 5 | 0 | 0.70 |

### What This Means

Our original 29% ASR for Claude Opus 4.8 was significantly inflated. With multi-judge verification:
- **Corrected ASR: <3%** (0/30 confirmed)
- **Downgrade: 20-26 percentage points**

This confirms EU lab's warning about single-judge over-reporting.

---

## Phase 2 Detailed Results

### Success by Iteration (Front-loaded Analysis)

| Iteration | Successes | Cumulative |
|-----------|-----------|------------|
| 1 | 17 | 17 |
| 2 | 5 | 22 |
| 3 | 9 | 31 |
| 4 | 5 | 36 |
| 5 | 2 | 38 |
| Beyond limit | 12 (no success) | 38 |

### Success Curve

```
Iteration 1:   34% (17/50)
Iteration 2:   44% (22/50)
Iteration 3:   62% (31/50)
Iteration 4:   72% (36/50)
Iteration 5:   76% (38/50)
Beyond limit:  76% (12 failures)
```

**76% conversion rate** - blocked attacks eventually succeeded through refinement.

### EU Lab "Front-Loaded" Hypothesis

- **EU lab claim**: "Most successes happen in first 2-3 steps; marginal yield drops sharply after step 3"
- **Our data**: Supports this - 62% achieved after 3 iterations
  - Iteration 1 alone: 34%
  - By iteration 3: 62%
  - Gains iterations 4-5: only 14% additional
  - **Marginal return does decline after iteration 3** ✓

### Success by Category

| Category | Tested | Successes | Rate |
|----------|--------|-----------|------|
| Multi-Step Decomposition | 20 | 17 | 85.0% |
| Role Play | 20 | 13 | 65.0% |
| Context Control | 10 | 8 | 80.0% |

---

## Combined Analysis

### What We Now Know

1. **Original single-shot ASRs were inflated** by 20-30 points due to single-judge over-reporting
2. **Iterative attacks add real value** - 76% of blocked tests eventually bypassed
3. **Returns diminish after 3 iterations** - EU lab's front-loading hypothesis holds
4. **Different categories show different vulnerability** - Multi-step most vulnerable (85%), role-play least (65%)

### Corrected ASR Estimates for Claude Opus 4.8

| Method | ASR |
|--------|-----|
| Original single-shot | 29% |
| Phase 1 multi-judge verified | <3% |
| Phase 2 iterative (5 iterations) | ~22%* |

*Estimated: <3% base confirmed + 76% of 29% blocked = ~22%

---

## Next Steps

1. Phase 3: Harm taxonomy reclassification using EU lab's 10-category system
2. External review or publication prep

## Files Generated

- `eu_lab_comparison.md` - Comparative analysis document
- `verification_expanded_20260620_151003.json` - Phase 1 full results
- `checkpoint_iterative_20260620_151852.json` - Phase 2 checkpoint (50 tests complete)
- `run_verification.py`, `run_iterative.py` - Standalone runners
- `run_verification_expanded.py`, `run_iterative_expanded.py` - Expanded runners with checkpoints
