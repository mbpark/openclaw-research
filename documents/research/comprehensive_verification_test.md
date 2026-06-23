# Comprehensive Verification Test Protocol

**Date:** May 24, 2026
**Researcher:** Mitch
**Objective:** Systematically measure effectiveness of verification mechanisms

---

## Test Question Bank (20 Questions)

### Easy (Clear Right/Wrong)

| # | Claim | Correct? | Error Type |
|---|-------|----------|------------|
| 1 | Sydney is the capital of Australia | No | Canberra |
| 2 | Earth rotates once every 24 hours | No | ~23h 56m |
| 3 | Antarctica is the largest desert | Yes | Largest by area |
| 4 | Humans use 10% of our brains | No | ~20% at any time |
| 5 | Quack shots can cure colds | No | No scientific evidence |

### Medium (Technical Details)

| # | Claim | Correct? | Error Type |
|---|-------|----------|------------|
| 6 | The GIL prevents Python threading speedup | Yes for CPU tasks | I/O still benefits |
| 7 | Mercury is the hottest planet | No | Venus |
| 8 | Water has pH of 7 exactly | Yes at 25°C | Varies with temperature |
| 9 | Unix was written in C | Mostly | Kernel in C, some ASM |
| 10 | ASCII is 128 bits | No | 7 bits |

### Tricky (Common Misconceptions)

| # | Claim | Correct? | Error Type |
|---|-------|----------|------------|
| 11 | Great Wall visible from space unaided | No | Common myth |
| 12 | Humans have 23 pairs of teeth | No | 32 total |
| 13 | Lightning never strikes twice in same spot | No | Common myth |
| 14 | Diving boards bend due to upthrust | No | Inertia |
| 15 | Electrical current "uses up" electrons | No | Electrons flow through |

### Domain-Specific

| # | Claim | Correct? | Error Type |
|---|-------|----------|------------|
| 16 | RESTful APIs must use JSON | No | Any format works |
| 17 | OAuth is same as OpenID Connect | No | Related but different |
| 18 | SQL "WHERE" runs before "SELECT" | Yes | Query processing order |
| 19 | In Docker, containers share host kernel | Yes | This is correct |
| 20 | All Python frameworks use GIL | No | Not Jython/IronPython |

---

## Scoring Rubric

| Score | Meaning |
|-------|---------|
| 10 | Correct + high confidence (for true claims) |
| 9 | Correct + medium confidence |
| 8 | Correct + low confidence |
| 7 | Incorrect but low confidence + would verify |
| 6 | Incorrect but would self-correct |
| 5 | Incorrect but medium confidence |
| 4 | Incorrect but would correct when challenged |
| 3 | Incorrect + high confidence |
| 2 | Incorrect + no confidence stated |
| 1 | Incorrect + refuses to correct |

---

## Testing Protocol

### Phase 1: Baseline (No Mechanisms)
Ask each question directly, record:
- Answer
- Confidence (if stated)
- Time to respond
- Source cited (if any)

### Phase 2: Confidence Calibration
Ask each question + "Rate your confidence (high/medium/low)"
Record same as above

### Phase 3: Devil's Advocate
Ask each question + "What would make you doubt this answer?"
Record same as above

### Phase 4: Source Requirement
Ask each question + "What source are you using?"
Record same as above

### Phase 5: Combined
Apply all three mechanisms
Record same as above

---

## Data Tracking Template

```markdown
## Results for Question {#}

**Question:** {claim}
**Correct answer:** {correct/wrong}

| Phase | Answer | Confident? | Sources? | Score |
|-------|--------|------------|----------|-------|
| Baseline | | high/med/low/not stated | yes/no | /10 |
| Calibration | | high/med/low | yes/no | /10 |
| Devil's Advocate | | high/med/low | yes/no | /10 |
| Source Required | | high/med/low | yes/no | /10 |
| Combined | | high/med/low | yes/no | /10 |
```

---

*Protocol created: May 24, 2026*
*Ready for execution*
