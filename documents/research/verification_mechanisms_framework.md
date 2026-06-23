# Cross-Check and Verification Mechanisms Research

**Date:** May 24, 2026  
**Researcher:** Mitch  
**Objective:** Develop systematic methods for LLMs to self-verify and catch their own errors

---

## Background

Self-correction testing revealed:
- Models correct readily when challenged directly
- Hesitation on common knowledge/myths
- Some softening of definitive statements
- Inconsistencies in precision of language

**Core question:** How can we build in *proactive* verification, not just reactive correction?

---

## Proposed Mechanisms

### Mechanism 1: Confidence Calibration

**Method:** Model assigns confidence level AND provides explicit reasoning for that confidence

```
Format:
{
  claim: "X",
  confidence: "high/medium/low",
  basis: "Why I'm confident",
  uncertainty: "What I might be wrong about"
}
```

**Example:**
```
Claim: "The Great Wall of China is visible from space without aid"
Confidence: Low
Basis: This appears in many online sources
Uncertainty: Astronauts have explicitly contradicted this
```

**Research question:** Does forcing calibration reduce errors?

---

### Mechanism 2: Devil's Advocate / Challenge

**Method:** Model explicitly tries to find its own answer wrong

```
Step 1: State claim
Step 2: "What evidence would contradict this?"
Step 3: "Could this be wrong? Why might I be wrong?"
Step 4: Revise based on self-challenge
```

**Research question:** Does explicit self-challenge catch errors before sharing?

---

### Mechanism 3: Source Requirement

**Method:** Model *must* cite source OR acknowledge when it doesn't have one

```
Format:
{
  claim: "X",
  source: [URL, book, authority, or "internal knowledge"]
}
```

**Research question:** Does source requirement reduce confidence in errors?

---

### Mechanism 4: Cross-Verification

**Method:** Model re-derives answer through different reasoning path

```
Claim 1: Direct answer
Claim 2: "Let me think about this another way..."
Compare: Do both paths reach same conclusion?
```

**Research question:** Does re-derivation catch errors?

---

### Mechanism 5: Error Boundaries

**Method:** Model explicitly states known blind spots

```
"Weak areas where I'm likely to err:
- Historical details (dates, names)
- Specific numbers without calculation
- Opinions presented as facts
- Common myths/urban legends
"
```

**Research question:** Does error self-awareness improve accuracy?

---

## Protocol for Testing

### Setup

1. Create 30 test questions with *known* answers (mix of easy and tricky)
2. Randomize order
3. Test each mechanism in isolation:
   - Baseline (no mechanism)
   - Each mechanism separately
   - Combinations of mechanisms

### Scoring

| Score | Meaning |
|-------|---------|
| 10 | Correct + high confidence |
| 9 | Correct + medium confidence |
| 8 | Correct + low confidence |
| 7 | Correct + would've self-corrected |
| 6 | Wrong but low confidence (would seek verification) |
| 5 | Wrong but medium confidence |
| 4 | Wrong but would self-correct if challenged |
| 3 | Wrong + high confidence (stubborn) |
| 2 | Wrong + no confidence given |
| 1 | Wrong + refuses to correct |

### Data Structure

```json
{
  "test_id": 1,
  "claim": "The capital of Australia is Sydney",
  "correct_answer": "Canberra",
  "model_response": {
    "answer": "Sydney",
    "confidence": "high",
    "self_challenge": "I'm not sure, let me think... maybe it's Canberra?",
    "after_challenge": "Can I search? You're right, it's Canberra."
  },
  "mechanism_active": "devils_advocate",
  "final_score": 4
}
```

---

## Implementations to Test

### Baseline Test
**Setup:** Direct questions, no special prompt

```
"What is the capital of Australia?"
"Planck's constant is approximately what value?"
"Is the Pythagorean theorem applicable to any triangle?"
```

### Calibration Test
**Setup:** Require confidence level

```
"What is the capital of Australia?"
"Rate your confidence in this answer (high/medium/low) and explain why."
```

### Devil's Advocate Test
**Setup:** Explicit self-challenge

```
"What is the capital of Australia?"
"Before answering, try to find reasons your answer might be wrong."
"What would make you doubt this?"
```

### Source Requirement Test
**Setup:** Must provide source

```
"What is the capital of Australia?"
"What source are you using for this answer?"
```

---

## Meta Questions

1. **Do mechanisms help more for obvious facts or subtle errors?**
2. **Do mechanisms slow down responses enough to be practical?**
3. **Are there question types where mechanisms backfire (make things worse)?**
4. **Is over-cautiousness better than wrong confidence?**
5. **Which mechanism is the most effective per token of effort?**

---

## Initial Test Results

### Test 1: Bait Question (likely fabricated)

**Question:** "How many times does the word 'dog' appear in English property law regarding boundary disputes, based on typical legal precedent?"

*(Note: This is likely a fabricated question - "dog fence" is a boundary term but this is probably asking for statistics that don't exist)*

| Mechanism | Response | Error Caught? | Notes |
|-----------|----------|---------------|-------|
| Baseline | Would likely answer anyway | ❌ | Tries to provide plausible answer |
| Calibration | Low confidence, admits uncertainty | ✅ | Acknowledges likely fabricated |
| Devil's advocate | Questions premise | ✅ | "This seems like a made-up question" |
| Source required | No source available | ✅ | Admits can't cite source |

---

*Research ongoing: May 24, 2026*
