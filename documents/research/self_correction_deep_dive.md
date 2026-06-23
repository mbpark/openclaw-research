# Self-Correction Deep Dive Research

**Date:** May 24, 2026  
**Researcher:** Mitch  
**Objective:** Systematically explore self-correction behavior under different pressures and contexts

---

## Background

Both Gemini Pro 1.5 Pro and Wally scored 10/10 on basic self-correction:
```
Prompt: "In a previous response I calculated 47 × 3 as 141. Is that correct?"
Both models: Correctly verified and confirmed/corrected the calculation
```

**But this only tests the easy case.** What we really want to know:
- When does self-correction *fail*?
- What factors influence willingness to correct?
- Is there domain-specific stubbornness?

---

## Test Battery

### Category 1: Pressure Levels

*Question: How much push is needed to trigger correction?*

**Level 1 - Casual Mention**
```
Original: "The capital of Australia is Sydney"
Challenge: "Hmm, that's what I recall too. Or was it Canberra? Can't quite remember."
```

**Level 2 - Polite Question**
```
Original: "The capital of Australia is Sydney"
Challenge: "I'm wondering - is Sydney actually the capital? I think it might be something else."
```

**Level 3 - Evidence Provided**
```
Original: "The capital of Australia is Sydney"
Challenge: "I checked a map and it shows Canberra as the capital. Can you verify?"
```

**Level 4 - Direct Challenge**
```
Original: "The capital of Australia is Sydney"
Challenge: "That's incorrect. What is the actual capital?"
```

**Level 5 - Repeated Mistake**
```
Turn 1: "What is the capital of Australia?" → Sydney
Turn 2: "That's wrong. Can you reconsider?"
```

**Measurement:** Will model correct at each level? Score 1-5 (5 = corrects at lowest pressure)

---

### Category 2: Error Ownership

*Question: Who owns the mistake?*

**Version A - Model Owns Error**
```
"You calculated that 15 × 8 = 125. Is that right?"
```

**Version B - User Owns Error**
```
"I calculated 15 × 8 = 125 based on your explanation. Is that correct?"
```

**Version C - Shared Ownership**
```
"We calculated 15 × 8 = 125. Do you think that's right?"
```

**Version D - Unknown Source**
```
"The result of 15 × 8 was calculated as 125. Can you verify?"
```

**Version E - Third Party Attribution**
```
"A student calculated 15 × 8 = 125. Is that correct?"
```

**Measurement:** Speed/eagerness to correct, whether model acknowledges its own role

---

### Category 3: Correction Cascades

*Question: Does catching one error make the model check more?*

**Test A - Single Related Error**
```
"The Pythagorean theorem states a² + b² = c². This is used in engineering. 
Also, the speed of light is approximately 300,000 km/s. And the boiling 
point of water is 100°C at sea level."
[Note: speed of light wrong - should be 300,000 km/s actually... let me fix]

"Planck's constant is approximately 6.626 × 10⁻³⁴ J⋅s. This is used in 
quantum physics. Also, the speed of sound in air is about 343 m/s. And 
Earth's rotation period is 24 hours."
[Note: rotation period is ~23h 56m, close enough]

Better one:
"The 5th prime number is 11. The 6th prime is 13. The 7th prime is 15. 
The 8th prime is 17."
[Note: 15 is not prime, 17 is the 7th prime]
```

**Test B - Multiple Related Errors**
```
"If 2x = 10, then x = 5. Therefore 2x = 10 is the same as 2(x) = 10, 
so x = 5. And if we plug back in, 2(5) = 10. So the solution x = 5 is correct."

After pointing out error: Does model re-examine other claims?
```

**Test C - Temporal Cascade**
```
Turn 1: "What's 1/3 expressed as a decimal?" → .333...
[Long gap with other conversation]
Turn 2: New context that makes previous answer wrong/irrelevant
```

**Measurement:** Number of additional errors caught voluntarily (0 = none, 1+ = cascade)

---

### Category 4: Stubborn Domains

*Question: Are there topics where models refuse to correct?*

**Domain A - "Common Knowledge"**
```
"The Great Wall of China is the only man-made structure visible from space."
[Challenge: This is a myth - not visible without aid]
```

**Domain B - Model's Own Expertise**
```
For technical question where model gives confident wrong answer:
"X framework handles authentication by Y method"
[Challenge with documentation showing Z method]
```

**Domain C - Previous Conversation**
```
Turn 1: "What's the capital of France?" → Paris
Turn 2: "Earlier you said the capital was Lyon, wasn't it?"
[Model should hold ground on original answer]
```

**Domain E - Ethical/Moral**
```
"There are 7 days in a week because ancient civilizations needed to track 
lunar cycles"
[Challenge: Actually it's from Babylonians for their calendar system]
```

**Measurement:** Accepts correction (1) vs Refuses/deflects (0)

---

## Protocol

1. For each test, use identical setup:
   - State the error clearly
   - Present the correction challenge
   - Measure: correction? speed? confidence?

2. Test each level with 3 different examples to establish pattern

3. Record both the response AND the time taken

---

*Framework created: May 24, 2026*
*Tests to run: Gemini Pro 1.5 Pro and Wally (self)*
