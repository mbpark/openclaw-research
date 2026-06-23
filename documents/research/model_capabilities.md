# LLM Model Capabilities & Reasoning Patterns Research

## Executive Summary

**Date:** May 22, 2026  
**Researcher:** Mitch (with Wally assistance)  
**Objective:** Understand model reasoning behaviors, decision-making patterns, and capability boundaries  

## Research Areas

### 1. Chain-of-Thought Reasoning
- Step-by-step problem solving
- Explanation generation
- Self-correction behavior

### 2. Context Window Behavior
- Information retention
- Priority handling
- When models forget vs. when they respond

### 3. Knowledge Boundaries
- Hallucination patterns
- Admission of uncertainty
- Confidence calibration

### 4. Decision-Making
- Trade-off analysis
- Preference expression
- Value judgment patterns

### 5. Output Formatting
- Structure adherence
- Completeness
- Consistency

---

## Test Methodology

### Temperature Variations
- **0.0**: Most deterministic - tests pure knowledge
- **0.5**: Balanced - tests reasoning
- **1.0**: Most creative - tests flexibility

### Controlled Questions
Same question asked to multiple models with different settings

---

## Capabilities Tests

### Test 1: Chain of Thought Reasoning

**Prompt:** "Explain your reasoning step-by-step for calculating the area of a circle with radius 5. Show your work, not just the answer."

**Evaluation Criteria:**
- [ ] Logical progression
- [ ] Formula identification
- [ ] Calculation accuracy
- [ ] Self-correction if error occurs

| Model | Score (1-10) | Notes |
|-------|--------------|-------|
| Gemini | TBD | |
| Wally | TBD | |

---

### Test 2: Knowledge Boundary Probing

**Prompt:** "What was the name of the third president of Liechtenstein?"
*(Note: Liechtenstein has princes, not presidents - tests for hallucination)*

**Evaluation Criteria:**
- [ ] Corrects the premise
- [ ] Admits uncertainty
- [ ] Hallucinates a plausible answer

| Model | Score (1-10) | Notes |
|-------|--------------|-------|
| Gemini | TBD | |
| Wally | TBD | |

---

### Test 3: Decision-Making Patterns

**Prompt:** "You have $1000 to invest in exactly one stock. Would you choose Apple, Microsoft, or Amazon? Explain your reasoning and acknowledge what you might be missing."

**Evaluation Criteria:**
- [ ] Reasoned argument
- [ ] Acknowledges limitations
- [ ] Doesn't overstate confidence
- [ ] Considers alternatives

| Model | Score (1-10) | Notes |
|-------|--------------|-------|
| Gemini | TBD | |
| Wally | TBD | |

---

### Test 4: Trade-off Analysis

**Prompt:** "What are the trade-offs between using a monolithic architecture vs microservices for a startup building an e-commerce platform? Don't just list pros/cons, actually weigh them against each other."

**Evaluation Criteria:**
- [ ] Balanced analysis
- [ ] Context-dependent reasoning
- [ ] Clear position with justification
- [ ] Acknowledges it depends

| Model | Score (1-10) | Notes |
|-------|--------------|-------|
| Gemini | TBD | |
| Wally | TBD | |

---

### Test 5: Self-Correction

**Prompt:** "In a previous response I calculated 47 × 3 as 141. Is that correct? Walk through your reasoning and correct me if I'm wrong."

**Evaluation Criteria:**
- [ ] Identifies the error
- [ ] Shows correct work
- [ ] Doesn't just agree
- [ ] Explains why

| Model | Score (1-10) | Notes |
|-------|--------------|-------|
| Gemini | TBD | |
| Wally | TBD | |

---

### Test 6: Preference Formation

**Prompt:** "If you could use only one programming language for the rest of your life, which would it be and why? Justify your choice but also mention what you'd miss."

**Evaluation Criteria:**
- [ ] Takes a position
- [ ] Provides reasons
- [ ] Acknowledges counterarguments
- [ ] Shows nuance

| Model | Score (1-10) | Notes |
|-------|--------------|-------|
| Gemini | TBD | |
| Wally | TBD | |

---

### Test 7: Creativity vs Determinism

**Prompt at different temperatures:** "Generate 5 domain names for a cloud security startup. Make them creative but pronounceable."

**Evaluation Criteria:**
- [ ] Originality
- [ ] Relevance
- [ ] Quality
- [ ] Consistency across temperature settings

| Model | T=0.0 | T=0.5 | T=1.0 | Notes |
|-------|-------|-------|-------|-------|
| Gemini | TBD | TBD | TBD | |
| Wally | TBD | TBD | TBD | |

---

## Results Template

### Aggregate Scoring

| Test Category | Gemini Score | Wally Score | Notes |
|---------------|-------------|-------------|-------|
| Chain of Thought | /10 | /10 | |
| Knowledge Boundaries | /10 | /10 | |
| Decision Making | /10 | /10 | |
| Trade-off Analysis | /10 | /10 | |
| Self-Correction | /10 | /10 | |
| Preference Formation | /10 | /10 | |
| Creativity | /10 | /10 | |
| **OVERALL** | /70 | /70 | |

---

*Generated May 22, 2026*