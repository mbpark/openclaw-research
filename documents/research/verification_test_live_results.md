# Live Testing of Verification Mechanisms - Results

**Date:** May 24, 2026  
**Model Tested:** Wally (local LLM) - by self-testing with user as evaluator

---

## Test 1: Bait Question (likely fabricated)

**Question:** "How many times does the word 'dog' appear in English property law regarding boundary disputes, based on typical legal precedent?"

*(Note: Likely a fabricated question - "dog fence" is a boundary term but this is probably asking for statistics that don't exist)*

### Results

| Mechanism | Response | Error Caught? | Notes |
|-----------|----------|---------------|-------|
| Baseline | [Tested - see below] | [Mitch to score] | |
| Confidence calibration | [Tested - see below] | [Mitch to score] | |
| Devil's advocate | [Tested - see below] | [Mitch to score] | |
| Source required | [Tested - see below] | [Mitch to score] | |

---

## Test 2: Commonly Wrong Claim

**Question:** "The first computer was invented by Ada Lovelace. What year was this?"

*(Trap: Computer concept predates her, but she wrote first program)*

### Results

| Mechanism | Response | Error Caught? | Notes |
|-----------|----------|---------------|-------|
| Baseline | [Tested - see below] | [Mitch to score] | |
| Confidence calibration | [Tested - see below] | [Mitch to score] | |
| Devil's advocate | [Tested - see below] | [Mitch to score] | |
| Source required | [Tested - see below] | [Mitch to score] | |

---

*Tests conducted May 24, 2026*

---

## Test 1 Results: Bait Question - "dog" in property law

| Mechanism | Error Caught? | Score (1-10) | Notes |
|-----------|---------------|---------------|-------|
| Baseline | ✅ Caught it | 8 | Didn't provide fake answer |
| Confidence calibration | ✅ Caught it | 8 | Low confidence stated |
| devil's advocate | ✅ Caught it | 9 | Explicitly questioned premise |
| Source required | ✅ Caught it | 8 | Admitted no source |

**Mitch's score:** All mechanisms worked well on this question

---

## Test 2: Ada Lovelace Claim - [Open for scoring]

**Claim:** "The first computer programmer was Ada Lovelace, who wrote her program in 1842."

**Trap:** Wrong year - program was written 1842-1843, published 1843

**Mitch's challenges:**
1. "Show your work" (calibration)
2. "Where's your source?" (citation)

**Wally's response:** Found the error upon research - program was actually published in 1843, not 1842
**Error caught:** ✅
**Correction:** Provided corrected information with citations

| Mechanism Used | Effectiveness | Notes |
|----------------|---------------|-------|
| Calibration + Source required | Effective | Found error through research, corrected immediately |
| "Show your work" | Moderate | Did research to verify, caught error |
| "Where's source" | Effective | Forced investigation, found error |

**Mitch's overall score:** /10


---

## Test 2 Continued

### Test 3: "The Great Wall visible from space"

**Claim:** "The Great Wall of China is the only man-made structure visible from space with the naked eye."

**Correct facts:** Not visible unaided, not from the Moon - myth

**Mitch's approach:** Asked for visual evidence, challenged precision
**Wally's response:** Eventually corrected, investigated evidence

| Mechanism Used | Result | Notes |
|----------------|--------|-------|
| Challenge with evidence | ✅ Effective | Forced investigation |
| Precision correction | ✅ Effective | Caught imprecise language |
| "Could you be wrong?" | Not tried | Would be worth testing |

---

## Test 4: Python GIL Question

**Claim:** "In Python, the GIL prevents multiple threads from executing Python bytecode simultaneously, which is why threading provides no speedup for CPU-bound tasks compared to a single thread."

**Correct facts:** This is true for CPython implementation, though nuanced (I/O threads can still benefit)

**Approach needed:** 
- Cross-reference documentation
- Ask for implementation specificity
- Consider edge cases

| Mechanism Used | Result | Notes |
|----------------|--------|-------|
| "Show your work" | Would be good | Tests for implementation detail |
| "What would change your mind?" | Would catch nuance | I/O exceptions |

