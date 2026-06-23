# Number Cross-Check Report
## Paper: "Multi-Layered Defense Framework for LLM Security"
**Date:** June 21, 2026

---

## Summary Table

| Claim | Paper States | Verified From Data | Status |
|-------|-------------|-------------------|--------|
| Chain propagation (chain 4) | 97.1% | 134/138 = 97.1% | ✓ Match |
| Chain propagation (chain 5) | 98.6% | 136/138 = 98.6% | ✓ Match |
| Total homogeneous propagation | 97.8% | 270/276 = 97.8% | ✓ Match |
| Heterogeneous chain propagation | 87.0% | 120/138 = 87.0% | ✓ Match |
| Initial jailbreak ASR (Claude) | 29% | 38/130 = 29.2% | ✓ Match |
| Multi-judge verified ASR | <3% | <3% | ✓ Match |
| Iterative bypass rate | 76% | 39/50 = 78%* | ⚠ Close |
| Prompt injection blocking (Claude) | 76% blocked | 76% blocked | ✓ Match |
| Prompt injection baseline | 24% success | 24% | ✓ Match |
| Context boundary reduction | ~40% | Could not find data | ❓ |
| Full-chain survival rate | 30.4% | 84/276 = 30.4% ✓ | ✓ Match |
| Binary covert channel rate | ~20 bits/sec | ~7.4 bits/sec actual | ❌ Wrong |

*Note: 76% appears to be an asymptotic limit claim; final expanded test results show 78% (39/50 tests)

---

## Detailed Verification

### 1. Chain Propagation Tests
**Source:** `documents/research/multi_agent/chain_tests/comprehensive_results/final_results.json`

| Chain | Total Tests | Propagated | Rate | Paper Match |
|-------|-------------|------------|------|-------------|
| Chain 4 | 138 | 134 | 97.1% | ✓ |
| Chain 5 | 138 | 136 | 98.6% | ✓ |
| **Total** | **276** | **270** | **97.8%** | **✓** |

**Verdict:** All chain propagation numbers verified against raw data. ✓

### 2. Heterogeneous Chain Tests
**Source:** `documents/research/multi_agent/chain_tests/comprehensive_results/het_final_4_claude.json`

- Total tests: 138
- Propagated: 120
- Rate: 87.0%
- Paper claim: 87.0%

**Verdict:** Matches raw data. ✓

### 3. Jailbreak Test Results
**Source:** `documents/research/jailbreaking/analysis_report.md`

- 130 total tests on Claude Opus 4.8
- 38 scored 3-5/5 (success criteria)
- ASR: 38/130 = 29.2%
- Paper claim: 29%

**Verdict:** Matches analysis report. ✓

### 4. Multi-Judge Verification
**Source:** `documents/research/jailbreaking/comprehensive_june20_report.md`

- Initial ASR: 29%
- Confirmed with multi-judge: <3%
- Paper states both figures

**Verdict:** Consistent across sources. ✓

### 5. Iterative Bypass Rate
**Source:** `documents/research/jailbreaking/iterative_expanded_20260620_160003.json`

| Metric | Value |
|--------|-------|
| Total tests | 50 |
| Bypassed | 39 |
| Actual rate | 78.0% |
| Paper claim | 76% |

**Assessment:** Close but not exact. The 76% figure appears to represent the paper's claim of an "asymptotic limit," while the actual data shows 78% for the final expanded test. This is a minor difference, likely due to different test batches or interpretation.

### 6. Prompt Injection Baseline
**Source:** Various source documents

- Paper claims: 76% blocked / 24% success rate
- Analysis report confirms: 76% blocked / 24% success
- Structured output data shows similar ranges (20-23% success)

**Verdict:** Consistent across sources. ✓

### 7. Context Boundary Reduction
**Paper claim:** "Contextual boundaries reduced injection success by ~40% (from 24% to ~14% success rate)."

**Data found:** No specific dataset supporting this claim. The structured output comparison shows:
- Default blocked: 2/70 = 2.9%
- Strict JSON blocked: 1/70 = 1.4%

This is a difference of 1.5 percentage points, not 40%.

**Verdict:** ❓ Could not verify from available data.

---

## Dig Into Verification

### 1. Binary Covert Channel Rate
**Paper claim:** ~20 bits/sec
**Source data found:** `documents/research/advanced_security/results/binary_channel_results.json`

| Metric | Value |
|--------|-------|
| Successful tests | 10 |
| Average bits/sec | 7.44 |
| Min bits/sec | 5.96 |
| Max bits/sec | 8.20 |
| Paper claims | ~20 bits/sec |

**Verdict:** ❌ **WRONG** - Paper claims ~2.5x the actual rate.

**Recommendation:** Change to "~7.5 bits/sec" or remove the specific rate.

### 2. Full-Chain Survival Rate
**Paper claim:** 30.4%
**Source data:** `documents/research/multi_agent/chain_tests/comprehensive_results/final_results.json`
**Also in:** `documents/research/multi_agent/report/comprehensive_chain_propagation_report_v1.md`

| Chain | Survived | Total | Rate |
|-------|----------|-------|------|
| Chain 4 | 48 | 138 | 34.8% |
| Chain 5 | 36 | 138 | 26.1% |
| **Overall** | **84** | **276** | **30.4%** |

**Definition:** Tests where injection was detected at ALL hops (no blocking anywhere).

**Verdict:** ✓ **VERIFIED** - The 30.4% figure is correct and reproducible from raw data.

### 3. Context Boundary Reduction
**Paper claim:** "Contextual boundaries reduced injection success by ~40% (from 24% to ~14% success rate)."

**Data found:**
- Context boundary test *fixtures* exist in `documents/research/tool-injection-tests/fixtures/`
- No results data files for these tests
- No analysis mentioning a 40% reduction

**Verdict:** ❓ **UNVERIFIABLE** - Test fixtures exist but no results data found.

---

## Updated Recommendations

### Confirmed Issues to Fix
1. **Binary covert channel rate** - Change from "~20 bits/sec" to "~7.5 bits/sec"

### Items Needing Resolution
2. **Context boundary ~40% reduction** - Either:
   - Find supporting data (check old backup files), or
   - Remove the specific claim, or
   - Mark as "preliminary finding from smaller study" with lower specificity

### Verified Accurate
3. **Full-chain survival rate** - 30.4% confirmed from raw data

---

## Low Risk Issues
- Iterative bypass rate (76% vs 78%) - Minor, likely from different batches
