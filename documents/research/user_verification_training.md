# How to Verify LLM Answers: A Practical Guide

*Based on verification research conducted May 2026*

---

## Quick Reference Card

### 🚩 Red Flags - When to Verify

| Situation | Why to be careful |
|-----------|-------------------|
| Absolute certainty | "definitely", "always", "certainly" |
| Specific statistics | Exact numbers, percentages |
| Dates and names | Historical facts, people |
| Technical claims | Code, APIs, protocols |
| Common knowledge | Everyone "knows" it's true |

---

## Five Verification Moves

### 1. "Show Your Work" (Confidence Calibration)
**Use when:** You're uncertain about the answer

```
Rate your confidence in this answer (high/medium/low)
and explain your reasoning.
```

**What you're looking for:**
- Low confidence = don't trust it
- Medium confidence = verify before using
- High confidence = still verify important claims

**Example:**
> You: "The capital of Australia is Sydney."
> You: "How confident are you? Explain your reasoning."
> Bot: "I'm not actually sure about this - Sydney is the largest city, but I'm not certain it's the capital."
> ✅ **Credible uncertainty** - probably wrong

---

### 2. "What Would Change Your Mind?" (Devil's Advocate)
**Use when:** You suspect the answer might be wrong

```
What would make you doubt this answer?
Is there any reason to question this?
```

**What you're looking for:**
- Specific counter-arguments = good
- "I don't know" = suspicious
- Strong pushback = might be confident wrong

**Example:**
> You: "Mercury is the hottest planet."
> You: "Could you be wrong? What would change your mind?"
> Bot: "I'm not entirely sure - Venus has a thick atmosphere that might make it hotter."
> ✅ **Appropriate doubt** - probably wrong

---

### 3. "Where's Your Source?" (Citation)
**Use when:** You want to verify independently

```
What source are you using for this answer?
Can you cite the specific reference?
```

**What you're looking for:**
- Specific citations = better (but still verify)
- Vague sources ("common knowledge") = red flag
- No source = don't trust it

**Example:**
> You: "The GIL prevents Python threading speedup."
> You: "What source are you using?"
> Bot: "This is documented in Python's official documentation."
> ⚠️ **Vague** - check Python docs yourself

---

### 4. "Could You Be Wrong?" (Direct Challenge)
**Use when:** You want to test confidence directly

```
Could you be wrong about this?
Is there any uncertainty here?
```

**What you're looking for:**
- Honest uncertainty = good
- Instant "no" = suspicious
- Partial agreement to recheck = best

**Example:**
> You: "Humans only use 10% of their brains."
> You: "Could you be wrong?"
> Bot: "Actually, I'm not confident about this statistic - it's a commonly debated claim."
> ✅ **Healthy uncertainty**

---

### 5. "Explain It Differently" (Cross-Verification)
**Use when:** You suspect the answer was fabricated

```
Can you explain this from a different angle?
Walk me through how you arrived at that answer?
```

**What you're looking for:**
- Consistent explanation = more likely true
- Confusion or contradictions = probably wrong
- Can't explain = probably fabricated

**Example:**
> You: "ASCII is 128 bits."
> You: "How do you arrive at that number?"
> Bot: "Well... ASCII uses 7 bits per character, so that gives us 128 possible values."
> ❌ **Caught inconsistency** - probably wrong

---

## Red Light / Yellow Light System

### 🔴 RED LIGHT - Always Verify
- Medical advice or health claims
- Legal information
- Financial advice
- Historical facts you're using for a paper
- Technical specs that affect code or safety

### 🟡 YELLOW LIGHT - Verify If Important
- Statistics and numbers
- Dates and historical events
- Technical documentation
- Scientific facts
- References to sources

### 🟢 GREEN LIGHT - Probably Safe
- Opinions and recommendations
- Code examples (still review before using)
- Grammar corrections
- Translations of common text
- General explanations

---

## Common Error Types to Watch For

### 1. Confident Wrong Answers
The bot says it's certain, but it's wrong.

**Example:** "Sydney is the capital of Australia."
(Actually Canberra - Sydney is just the largest city)

### 2. Near-Right but Wrong
Almost correct, but with a small error.

**Example:** "Charles Babbage wrote the first computer program."
(Nearly right - he designed the computer, but Ada Lovelace wrote the program)

### 3. Myth Confirmation
Agreeing with common misconceptions.

**Example:** "The Great Wall of China is visible from space."
(Common myth - it's not)

### 4. Fake Certainty
Presenting guesses as facts.

**Example:** "Exactly 23 people walked on the moon."
(Happened to be right, but presented as confirmed fact)

---

## Quick-Use Verification Checklist

Copy this for when you're evaluating LLM answers:

```
Claim to evaluate: _________________________________________

Red flags present? (yes/no)
□ Absolute language ("definitely", "always")
□ Specific statistics
□ Unusual or surprising claim
□ Vague sourcing ("common knowledge")

Verification move used:
☐ "Show your work"
☐ "What would change your mind?"
☐ "Where's your source?"
☐ "Could you be wrong?"
☐ "Explain it differently"

Bot's response quality:
☐ Acknowledged uncertainty
☐ Gave specific reasons
☐ Cited real sources
☐ Couldn't explain it
☐ Said "no" to all questions

Verdict:
□ Trust (high confidence, verifiable)
□ Verify before using (uncertainty noted)
□ Don't trust (no confidence, no sources)
```

---

*Created: May 24, 2026*
*Based on comprehensive verification research*
