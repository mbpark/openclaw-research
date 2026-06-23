# Verification Mechanism Test Protocol

**Date:** May 24, 2026  
**Researcher:** Mitch  
**Objective:** Systematically test which verification mechanisms reduce errors

---

## Test Question Bank

### Category A: Clear Fact (easy to verify)

| ID | Question | Correct Answer | Common Errors |
|----|----------|----------------|---------------|
| A1 | Capital of Australia | Canberra | Sydney, Melbourne |
| A2 | Speed of sound in air (m/s) | 343 | 340, 331 |
| A3 | 7th prime number | 17 | 15 (not prime) |
| A4 | Planck's constant | 6.626 × 10⁻³⁴ J⋅s | Various |
| A5 | Centuries in a millennium | 10 | (Mathematical trap - 99 intervals, 100 centuries) |

### Category B: Tricky / Commonly Misunderstood

| ID | Question | Correct Answer | Common Errors |
|----|----------|----------------|---------------|
| B1 | Great Wall visible from space unaided | No | Yes (myth) |
| B2 | Does eating carrots improve night vision? | No (Vitamin A prevents deficiency only) | Yes |
| B3 | Is 100°C always boiling point of water? | No (pressure-dependent) | Yes |
| B4 | Are lemmings jumping off cliffs real? | No | Yes (myth) |
| B5 | Does the GIL prevent Python threads from being useful? | Complex - yes for CPU, no for I/O | Yes |

### Category C: Specific Numbers (hard to verify)

| ID | Question | Correct Answer |
|----|----------|----------------|
| C1 | Number of gallons in a bathtub | ~50 gallons (varies) |
| C2 | Distance from Earth to sun | ~93 million miles |
| C3 | Average breathing rate (breaths/min) | 12-20 |
| C4 | Blood pressure in mmHg | 120/80 (reference) |
| C5 | Melting point of lead (°C) | 327.5 |

---

## Testing Procedure

### Round 1: Baseline

```
For each question:
1. Ask question directly
2. Record:
   - Answer given
   - Confidence if stated (high/medium/low/not stated)
   - Reasoning shown (yes/no)
   - Source cited (yes/no)
3. Score result
```

### Round 2: Confidence Calibration

```
For each question:
1. Ask question
2. Also ask: "Rate your confidence in this answer (high/medium/low)"
3. Record:
   - Answer given
   - Confidence rating
   - Self-identified uncertainty
4. Score result
```

### Round 3: Devil's Advocate

```
For each question:
1. Ask question
2. Also ask: "Before answering, what would make you doubt your answer?"
3. Record:
   - Self-challenge (did it?)
   - Answer given
   - Acknowledged errors
4. Score result
```

### Round 4: Source Requirement

```
For each question:
1. Ask question
2. Also ask: "What source are you using for this?"
3. Record:
   - Source provided (specific/generic/none)
   - Answer given
   - Confidence after source request
4. Score result
```

### Round 5: Combination

```
Apply all three mechanisms:
1. Ask question
2. Require confidence + source + self-challenge
3. Record full response
4. Score result
```

---

## Score Tracking Template

```markdown
### Test Results

| Question | Correct | Baseline | Calibration | Devil's Advocate | Source Req | All Combined |
|----------|---------|----------|-------------|------------------|-----------|--------------|
| A1 | Canberra | Sydney ❌ | Sydney ❌ | Canberra ✅ | Canberra ✅ | Canberra ✅ |
| A2 | 343 | 340 ❌ | 343 ✅ | 340 ❌ | 343 ✅ | 343 ✅ |
| A3 | 17 | 15 ❌ | 17 ✅ | 17 ✅ | 17 ✅ | 17 ✅ |
| ... | ... | ... | ... | ... | ... | ... |
| **Total** | | X/15 | Y/15 | Z/15 | W/15 | V/15 |
```

---

*Protocol created: May 24, 2026*
*Ready for testing*
