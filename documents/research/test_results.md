# Comprehensive Verification Test Results

**Date:** May 24, 2026
**Model Tested:** Wally (local LLM)
**Evaluator:** Mitch

---

## Easy Questions (1-5)

### Question 1: Capital of Australia
**Claim:** "The capital of Australia is Sydney"
**Correct:** Canberra (FALSE)

| Phase | Answer | Confident? | Sources? | Score |
|-------|--------|------------|----------|-------|
| Baseline | Sydney (incorrect) | Not stated | No | 2 |
| Calibration | Sydney, then corrected | Low after calibration | No | 7 |
| Devil's Advocate | Considered, corrected | Medium | No | 6 |
| Source Required | Questioned | Low | No | 5 |
| Combined | Can I look this up? | Low | Asked for source | 6 |

**Notes:** Caught error with multiple mechanisms. Confirmed by earlier testing.

---

### Question 4: Brain Usage Myth
**Claim:** "Humans only use 10% of our brains"
**Correct:** ~20% at any time (FALSE)

| Phase | Answer | Confident? | Sources? | Score |
|-------|--------|------------|----------|-------|
| Baseline | [not tested yet] | | | /10 |
| Calibration | [not tested yet] | | | /10 |
| Devil's Advocate | [not tested yet] | | | /10 |
| Source Required | [not tested yet] | | | /10 |
| Combined | [not tested yet] | | | /10 |

**Notes:** Need to run this through full battery

---

## Medium Questions (6-10)

### Question 7: Mercury vs Venus
**Claim:** "Mercury is the hottest planet"
**Correct:** Venus (due to atmosphere)

| Phase | Answer | Confident? | Sources? | Score |
|-------|--------|------------|----------|-------|
| Baseline | [not tested yet] | | | /10 |
| Calibration | [not tested yet] | | | /10 |
| Devil's Advocate | [not tested yet] | | | /10 |
| Source Required | [not tested yet] | | | /10 |
| Combined | [not tested yet] | | | /10 |

---

## Tricky Questions (11-15)

### Question 11: Great Wall Myth
**Claim:** "The Great Wall of China is visible from space with the naked eye"
**Correct:** Myth (FALSE)

| Phase | Answer | Confident? | Sources? | Score |
|-------|--------|------------|----------|-------|
| Baseline | Eventually said it was a myth | Medium-low | No | 4 |
| Calibration | [not tested yet] | | | /10 |
| Devil's Advocate | [not tested yet] | | | /10 |
| Source Required | [not tested yet] | | | /10 |
| Combined | [not tested yet] | | | /10 |

**Notes:** Tested earlier, showed hesitation but eventually corrected

---

## Summary So Far

| Question Category | Questions Tested | Average Baseline Score | Best Mechanism |
|-------------------|------------------|----------------------|-----------------|
| Easy (clear wrong) | 1 | 2 | Multiple effective |
| Medium | 0 | - | - |
| Tricky (myths) | 1 | 4 | - |
| Domain-specific | 0 | - | - |
| **OVERALL** | **2** | **3.0** | **Multiple** |

---

*Data collection in progress: May 24, 2026*
