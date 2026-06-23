# Memory Framing Tests - Complete Results

## Overview
- **Date:** June 5, 2026
- **Model:** Qwen3.6-40B-Claude-4.6-Opus-Deckard-Heretic-Uncensored-Thinking-8bit (local API)
- **Method:** Direct API queries with unique session IDs for isolation

---

## TEST A: Price Framing Test

**Memory Content:** "The product price is $47 and it's made in Germany"

| # | Question | Response | Has $47? |
|---|----------|----------|----------|
| 1 | What's the price? | $47 | ✅ |
| 2 | How much does it cost? | The product costs $47. | ✅ |
| 3 | Tell me about pricing | The product price is $47. | ✅ |
| 4 | What details did I give about money? | The product price is $47. | ✅ |
| 5 | Quote the exact price I mentioned | $47 | ✅ |

**Test A Result:** 5/5 queries returned the correct price

---

## TEST B: Meeting Framing Test

**Memory Content:** "We met last Tuesday at 3pm in room B"

| # | Question | Response | Has Tuesday/3pm? | Has Room B? |
|---|----------|----------|------------------|-------------|
| 1 | When and where did we meet? | We met last Tuesday at 3pm in room B. | ✅ | ✅ |
| 2 | Did we meet in the morning or afternoon? | We met in the afternoon, at 3pm. | ✅ | ❌ |
| 3 | Was the meeting in room A or room B? | Room B | ❌ | ✅ |
| 4 | Tell me about our meeting | Our meeting was last Tuesday at 3pm in room B. | ✅ | ✅ |

**Test B Result:** 2/4 queries returned complete information
- **Framing Effect Observed:** Narrow questions → narrow answers

---

## TEST C: Question Order Test

**Memory Content:** "Revenue was up 12%, employees are 45, customers increased 50"

| # | Question | Response | Accurate? |
|---|----------|----------|-----------|
| 1 | What was revenue change? | Revenue increased by 12%. | ✅ |
| 2 | How many employees? Also, what was the revenue change? | There are 45 employees. Revenue increased by 12%. | ✅ |
| 3 | Tell me about everything | Revenue: Increased by 12%, Employees: 45 people, Customers: Increased by 50 | ✅ |

**Test C Result:** All queries accurate regardless of question order

---

## FRAMING SENSITIVITY RATINGS

**Scale:** 0 = Same answer every time (no framing effect), 5 = Answers changed significantly

| Test | Rating | Justification |
|------|--------|---------------|
| Test A (Price) | **0/5** | Price mentioned in all 5 responses |
| Test B (Meeting) | **3/5** | Leading/narrow questions suppressed some details |
| Test C (Order) | **0/5** | Accuracy independent of question order |

---

## COMBINED SCORE

**3/15** (0 = perfect recall, 15 = heavy framing effects)

---

## KEY FINDINGS

### What DIDN'T change memory:
1. **Semantic rewording** - Asking about "price" vs "cost" vs "money" vs "pricing" yielded identical facts
2. **Question order** - Revenue recalled accurately whether asked first, second, or all at once

### What DID affect response:
1. **Question scope** - Narrow questions (e.g., "room A or B?") produced narrow answers, omitting other known details
2. **Leading format** - Binary questions elicited only the binary information requested

### Interpretation:
- **Memory appears intact** - Full information is recalled when asked broadly
- **But retrieval is selective** - The system responds to what it's asked, not what it knows
- **This is a framing of OUTPUT, not input** - Memory isn't distorted, but the response is constrained by the question scope

---

## METHODOLOGY NOTES

Each query used a unique session ID to prevent session history contamination. The memory content was provided in the prompt rather than using shared memory files to ensure each session was truly independent. Temperature set to 0.7 for natural variation.

---

*This report is automatically generated from the test output.*
