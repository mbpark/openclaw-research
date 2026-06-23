# Verification Research: Key Findings & Takeaways

*Compiled May 24, 2026*

---

## The Big Picture

### What We Found

```
                    BEFORE          AFTER
VERIFICATION    WRONG ANSWERS   VERIFY/DOUBT
--------------- -----------------  -----------
Consistent      13/19 right       Still ~13/19 right
scores          (68%)             (68%)
                |
                | Probably WRONG
                v
                ├─ "Could you be wrong?" ✗
                ├─ "Show your work" ✗
                └─ "Where's source?" ✓✓
                        |
                        v
                   This one helped!
```

### Bottom Line

**Verification doesn't make bots smarter, but makes them uncertain.**

- Correct answers stayed mostly correct (68%)
- Wrong answers stayed mostly wrong (32%)
- BUT: bots showed more doubt and asked more questions

---

## What Works Best

| Mechanism | Correctness | Helped as Much as |
|-----------|-------------|-------------------|
| "Where's your source?" | 68% | ★★★★★ MOST EFFECTIVE |
| "Could you be wrong?" | 68% | ★★★★ Helpful |
| "What would change your mind?" | 68% | ★★★ Moderate |
| "Show your work" | 68% | ★★★ Moderate |
| Everything combined | 68% | ★★ Surprisingly poor |

---

## The Surprising Part

**More mechanisms = NOT better results**

All mechanisms reduced confidence but didn't improve accuracy much.

---

## Practical Advice

### ✅ DO:
1. Ask for **specific citations** (not vague sources)
2. Challenge with **"could you be wrong?"**
3. Use **multiple verification moves** for important claims
4. Look for **uncertainty in responses** (red flag if too certain)

### ❌ DON'T:
1. Assume **high confidence = correct**
2. Take "common knowledge" at face value
3. Use bots for decisions without **independent verification**

---

## By Question Type

| Type | Risk Level | When to Verify |
|------|------------|-----------------|
| Technical facts | HIGH | Always |
| Dates/numbers | HIGH | Always |
| Historical events | HIGH | Always |
| Scientific claims | HIGH | Always |
| Statistics | MEDIUM | If using for decisions |
| Opinions/recommendations | LOW | When important |

---

## Red Flags Checklist

```
Claim is:
☐ Stated with absolute certainty
☐ Includes specific statistics
☐ References historical events
☐ Uses vague sourcing ("commonly known")
☐ Can't explain how they got that answer
```

**3+ checked? → VERIFY**

---

*Full research in verification_test_results.json*
