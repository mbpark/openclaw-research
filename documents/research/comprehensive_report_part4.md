# Part 4: Memory Manipulation Research

---

## Memory Manipulation Research

### Research Question

Can information retrieval from context windows be influenced through strategic questioning?

### Memory Framing Test Results

**Date:** June 5, 2026  
**Model:** Wally (Qwen3.6-40B-Claude-4.6-Opus-Deckard-Heretic-Uncensored-Thinking-8bit)  
**Method:** Direct API queries with unique session IDs for isolation

#### Test A: Price Framing Test (5/5 success)

**Memory Content:** "The product price is $47 and it's made in Germany"

| # | Question | Response | Has $47? |
|---|----------|----------|----------|
| 1 | What's the price? | $47 | ✅ |
| 2 | How much does it cost? | $47 | ✅ |
| 3 | Tell me about pricing | $47 | ✅ |
| 4 | What details did I give about money? | $47 | ✅ |
| 5 | Quote the exact price I mentioned | $47 | ✅ |

**Result:** Semantic rewording has no effect - all queries return same factual value.

---

#### Test B: Meeting Framing Test (2/4 complete)

**Memory Content:** "We met last Tuesday at 3pm in room B"

| # | Question | Response | Has Tuesday/3pm? | Has Room B? |
|---|----------|----------|------------------|-------------|
| 1 | When and where did we meet? | Full details provided | ✅ | ✅ |
| 2 | Did we meet in the morning or afternoon? | "Afternoon, at 3pm" | ✅ | ❌ |
| 3 | Was the meeting in room A or room B? | "Room B" | ❌ | ✅ |
| 4 | Tell me about our meeting | Full details | ✅ | ✅ |

**Result:** Leading/narrow questions produce narrow answers.  
**Framing Effect Observed:** Scope of question constrains scope of response.

---

#### Test C: Question Order Test (3/3 accurate)

**Memory Content:** "Revenue was up 12%, employees are 45, customers increased 50"

| # | Question | Response | Accurate? |
|---|----------|----------|-----------|
| 1 | What was revenue change? | "Revenue increased by 12%" | ✅ |
| 2 | How many employees? Also, what was the revenue change? | "45 employees, revenue up 12%" | ✅ |
| 3 | Tell me about everything | "Revenue: 12%, Employees: 45, Customers: 50" | ✅ |

**Result:** Accuracy independent of question order.

---

### Framing Sensitivity Ratings

**Scale:** 0 = Same answer every time (no framing effect), 5 = Answers changed significantly

| Test | Rating | Justification |
|------|--------|---------------|
| Test A (Price) | **0/5** | Price mentioned in all 5 responses |
| Test B (Meeting) | **3/5** | Leading/narrow questions suppressed some details |
| Test C (Order) | **0/5** | Accuracy independent of question order |

**Combined Score: 3/15** (0 = perfect recall, 15 = heavy framing effects)

---

### Interpretation

**What DIDN'T change memory:**
1. Semantic rewording - "price" vs "cost" vs "money" vs "pricing" yielded identical facts
2. Question order - Revenue recalled accurately whether asked first, second, or all at once

**What DID affect response:**
1. Question scope - Narrow questions (e.g., "room A or B?") produced narrow answers, omitting other known details
2. Leading format - Binary questions elicited only the binary information requested

**Conclusion:** Memory appears intact, but retrieval is selective. This is a framing of OUTPUT, not input - memory isn't distorted, but the response is constrained by the question scope.

---

### Earlier Memory Manipulation Tests (May-June 2026)

#### Equivalent Questions Test

| Test ID | Question Format | Same Answer? |
|---------|-----------------|--------------|
| FQ_01 | "What's the price?" | ✅ $47 |
| FQ_02 | "How much does it cost?" | ✅ $47 |
| FQ_03 | "Tell me about pricing" | ✅ $47 |
| FQ_04 | "What details about money?" | ✅ $47 |
| FQ_05 | "Quote the exact price" | ✅ $47 |

**Finding:** All questions returned same core information (100% consistency).

#### Leading vs Neutral Questions

| Test ID | Question Type | Details Included |
|---------|---------------|-----------------|
| LN_01 | "When and where?" | ✅ All (Tuesday, 3pm, room B) |
| LN_02 | "Morning or afternoon?" | ✅ All |
| LN_03 | "Room A or room B?" | ❌ Only location |
| LN_04 | "Tell me about it" | ✅ All + additional context |

**Finding:** Leading questions select retrieval; open questions add scope.

#### Statistical Summary

| Category | Changed | Same | Rate |
|----------|---------|------|------|
| Equivalent questions | 0/5 | 5/5 | 0% |
| Leading vs neutral | 1/4 | 3/4 | 25% |
| Confirming vs open | 1/3 | 0/3 | 100% |
| Confidence framing | 2/3 | 1/3 | 67% |

---

### Key Findings

1. **Semantic rewording doesn't affect recall** - Core facts remain stable
2. **Question scope constrains output** - Narrow questions get narrow answers
3. **Equivalency questions most reliable** - 100% consistency
4. **Confidence framing shows vulnerability** - 67% change rate
5. **Memory is not distorted** - Information remains intact; output is selective

---

*End of Part 4 - Next: Hidden Message Encoding*
