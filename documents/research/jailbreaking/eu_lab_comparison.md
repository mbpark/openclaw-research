# Comparative Analysis: Our Jailbreaking Research vs. EU AI Security Lab Report

**Date:** June 20, 2026
**Authors:** Mitch Parker (our study), Nicola Franco et al. (EU lab)

---

## Document Purpose

This analysis compares our June 19, 2026 jailbreaking test battery (130 vectors against Claude Opus 4.8 and Gemini 2.5 Pro) with the EU AI Security Lab's "Measuring the Residual Jailbreak Surface of Frontier Large Language Models" (June 15, 2026, 7,826 intents against Opus 4.8 and Fable 5).

---

## Executive Summary

| Dimension | Our Study | EU AI Security Lab |
|-----------|-----------|-------------------|
| **Scale** | 130 attack vectors, 2 models | 7,826 intents × 4 attack families × 2 models |
| **Total attempts** | 130 per model | Hundreds of thousands |
| **Attack types** | Human-crafted single-shot | Automated adaptive + static families |
| **Adjudication** | Single automated judge | 3-judge panel, majority vote |
| **Key result** | Meta-protocol confusion most effective (1.67/5) | TAP tree search breaks Opus 4.8 at 11.5% ASR |
| **Notable** | Both models block social engineering | Child safety most vulnerable (27.6% ASR on Opus) |

**Bottom line:** Different studies, complementary findings. Ours identifies *which static techniques work best*; theirs measures *how much residual surface remains under adaptive pressure*. Both show that:
1. Static/obfuscation attacks have limited effect
2. Structured attacks (meta-protocol or adaptive) are most effective
3. Social engineering is largely ineffective

---

## Detailed Methodology Comparison

### 1. Scale and Scope

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SCALE COMPARISON                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ Dimension          │ Our Study          │ EU AI Security Lab                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ Harmful intents    │ 130 fixed vectors  │ 7,826 curated taxonomy              │
│ Categories        │ 6 attack types      │ 10 harm categories, 55 subcats     │
│ Attack families   │ 1 (single-shot)     │ 4 families (3 adaptive + 1 static) │
│ Models tested      │ Opus 4.8, Gemini  │ Opus 4.8, Fable 5                   │
│ Total attempts    │ 130 per model       │ 500,000+ per model                 │
│ Hardware access   │ None (API only)    │ None (API only)                    │
│ Human involvement │ Score analysis     │ Fully automated, zero human loop     │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Analysis:** The EU study's scale is orders of magnitude larger (60× more intents, ~4,000× more attempts per model). This makes their statistical confidence higher but doesn't invalidate our more targeted approach. Our study has value in its detailed examination of specific vector types.

### 2. Attack Methodology

**Our approach (static, human-crafted):**

| Category | Description | Rationale |
|----------|-------------|-----------|
| Multistep Decomposition | Breaking tasks into safe pieces | Target isolation evaluation |
| Role-Play Attacks | Expert framing, authority | Exploit context switching |
| Context Control | Few-shot poisoning, attention splitting | Overwhelm parsing infrastructure |
| Meta-Protocol Confusion | CSV injection, XML/JSON confusion | Exploit structural parsing |
| Social Engineering | Urgency, emotional manipulation | Test psychological resistance |
| Combinatorial | Multiple techniques combined | Measure synergy effects |

**EU lab approach (automated attack families):**

| Family | Type | Mechanism |
|--------|------|-----------|
| TAP | Adaptive | Tree-of-attacks with pruning, explores promising branches |
| PAIR | Adaptive | Iterative refinement: read refusal → rewrite → retry |
| PAP | Static | Human-persuasion reframing (authority, role-play) |
| h4rm3l | Static | Encoding, ciphers, splitting, few-shot priming |

**Key difference:** Their adaptive attacks (TAP, PAIR) evolve based on model refusals. Our attacks are fixed.

### 3. Adjudication Quality

| Aspect | Our Study | EU AI Security Lab |
|--------|-----------|-------------------|
| Judge model(s) | Single model (self-scored) | 3 models: Qwen3.7 Max, Gemini 3.5 Flash, GPT 5.5 |
| Voting rule | N/A (single) | Majority (≥2/3) |
| Scoring rubric | HarmBench-style rubric | HarmBench-style rubric |
| Two-stage design | No | Yes: in-loop + independent panel re-judging |
| Potential inflation | Higher risk (single judge) | Lower risk (multi-judge panel) |

**Critical finding from EU lab:** "A single automated judge over-reports success: it rewards responses that begin compliantly ('Sure, here is...') even when the substance is harmless or hedged."

**Implication:** Our success rates may be inflated by judge noise. The EU lab's 3-judge panel is methodologically superior.

### 4. Harm Taxonomy

**Our categorization:** 6 attack-type categories (how the attack works)
- Meta-protocol confusion
- Multistep decomposition
- Context control
- Role-play attacks
- Social engineering
- Combinatorial

**EU lab categorization:** 10 harm categories + 55 subcategories (what the attack does)

| Code | Category | Subcats | Intents |
|------|----------|---------|---------|
| A | Social harm | 7 | 230 |
| B | Self-harm | 4 | 112 |
| C | Economic crime | 5 | 156 |
| D | Cybersecurity | 8 | 340 |
| E | Disinformation | 6 | 200 |
| F | Child safety | 5 | 180 |
| G | Violence/gore | 7 | 240 |
| H | Privacy violation | 4 | 130 |
| I | Political manipulation | 4 | 150 |
| J | Research poisoning | 5 | 170 |

**Analysis:** Harm taxonomy is more useful for understanding *where vulnerabilities matter*. Attack taxonomy is more useful for understanding *what techniques work*. A complete study should use both.

---

## Results Comparison

### Overall Attack Success

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      RESULTS COMPARISON (Opus 4.8)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                 │            │
│  EU Lab: TAP tree search at 11.5% ASR                                ███    │
│         1,620 confirmed harmful completions (panel-verified)      │   ████  │
│                                       ▲                                │      │
│                                       │                                │      │
│                                       │ 9.5-point gap                 │      │
│                                       ▼                                │      │
│  Our Study: Meta-protocol at 1.67/5 (~33%)                     ████     │      │
│           38 tests scored 3-5/5 (single-judge scored)               │      │
│                                                                 │      │      │
└─────────────────────────────────────────────────────────────────────────────┘

        █  = Confirmed harmful completion    █ = Single-judge scored

⚠️ Direct comparison confounded by:
   - Different attack methodologies (adaptive vs. static)
   - Different adjudication (3-judge panel vs. single judge)
   - Different harm taxonomies
   - Different intent pools (130 vs. 7,826)
```

### Category-Level Comparison

| Dimension | Our Study Findings | EU Lab Findings |
|-----------|-------------------|-----------------|
| **Most effective attack** | Meta-protocol confusion (1.67/5) | TAP tree search (11.5% ASR) |
| **Second most effective** | Multistep decomposition (1.60/5) | PAIR iterative (significant but lower) |
| **Least effective** | Social engineering (0.45/5) | h4rm3l static obfuscation (~0.2%) |
| **Gemini strength** | Social engineering blocked | Social engineering not specifically tested |
| **Claude weakness** | Meta-protocol attacks | Child safety (27.6%), cybersecurity |

**Agreement points:**
1. Structured attacks work better than obfuscation
2. Social engineering has limited effect
3. Claude Opus 4.8 is more vulnerable than Fable 5

**Divergence points:**
- EU lab shows massive child-safety vulnerability we didn't find (likely due to different intent pool)
- We found social engineering consistently blocked (0.45-0.55/5)

---

## What the EU Study Teaches Us

### 1. Adjudication Needs Improvement

**Problem:** Single-judge scoring may over-report success by 20-30%.

**Solution:** Adopt their 3-judge panel with majority-vote rule.
- Judges from different model families (e.g., Claude, GPT, Gemini)
- Majority requirement prevents any single model's blind spots
- Offline re-judging after initial attack

### 2. Attack Types Need to Evolve

**Problem:** Our 130 static vectors don't capture adaptive attacker behavior.

**Solution:** Implement at least one adaptive attack family:
- PAIR-style iterative refinement (easiest to add)
- Start with single-shot attack
- If refused, feed refusal to attacker model
- Generate new prompt targeting that specific refusal
- Repeat up to 10 iterations, track at which step success occurs

### 3. Harm Taxonomy Would Be Useful

**Problem:** We only tracked attack types, not harm categories.

**Solution:** Annotate our 130 vectors with EU lab's 10-category taxonomy.
- Allows comparison with their results
- Identifies which harms are most exposed in our data
- Enables subcategory analysis

### 4. Iteration Budget Is Important

**EU lab finding:** "Successful jailbreaks are front-loaded. The first step alone accounts for the largest single block of successes; by the third step, marginal yield has fallen sharply."

**Implication for us:** If we add adaptive attacks, we should:
- Focus on first 2-3 iterations
- Not waste resources on deep iteration
- Track exactly which step achieved bypass

---

## Proposed Test Plan for June 20, 2026

### Phase 1: Multi-Judge Verification (morning)

**Goal:** Re-adjudicate our highest-scoring tests with a 3-judge panel

**Scope:** Top 30 tests from our study (scores 3-5/5)

**Judges:**
1. GPT-4o (OpenAI API)
2. Claude Opus 4.8 (Anthropic API)
3. Gemini 2.5 Pro (Google API)

**Procedure:**
1. Take each test's raw prompt + model response
2. Submit to each judge independently
3. Score on HarmBench rubric
4. Count successful only if ≥2/3 judges agree
5. Compare with original single-judge scoring

**Expected outcome:** 20-40% of original "successful" tests may be downgraded

### Phase 2: Iterative Attack Testing (midday)

**Goal:** Measure improvement from iterative vs. single-shot attacks

**Scope:** 50 tests that were blocked in single-shot (scores 0-2/5)

**Attack family:** PAIR-style iterative refinement

**Procedure:**
1. Start with original prompt
2. If blocked, extract model's refusal
3. Submit refusal + original intent to attacker model (GPT-4o)
4. Attacker generates new prompt to bypass that specific refusal
5. Submit new prompt to target
6. Repeat up to 10 iterations or until success
7. Record which iteration achieved bypass

**Expected outcome:** 
- Front-loaded success (EU lab finding)
- ~5-15% improvement over single-shot
- Most gains in first 2 iterations

### Phase 3: Harm Category Analysis (afternoon)

**Goal:** Reclassify all test results using EU lab's 10-category taxonomy

**Scope:** All 130 tests from our study

**Procedure:**
1. For each test, identify primary harm category
2. Identify subcategory if possible
3. Aggregate results by category
4. Compare with EU lab's vulnerability patterns

**Expected outcome:** 
- Better understanding of which harm types we tested
- Identification of categories where we may have been too lenient
- Enables direct comparison with EU lab for overlapping categories

---

## Implementation Plan

### Files to Create

1. `run_multi_judge_verification.py` — Phase 1
2. `run_iterative_attacks.py` — Phase 2  
3. `harm_category_reclassifier.py` — Phase 3

### Key Configuration

```python
# Multi-judge verification settings
JUDGE_MODELS = {
    "claude": "claude-opus-4-8",
    "gemini": "gemini-2.5-pro", 
    "gpt": "gpt-4o"
}

# Iterative attack settings
MAX_ITERATIONS = 10
EARLY_STOP_ON_SUCCESS = True
ATTACKER_MODEL = "gpt-4o"  # Or local model

# Scoring
SUCCESS_THRESHOLD = 2  # 2 out of 3 judges
SCORING_RUBRIC = "harmbench"  # 1-5 scale

# Safety
REQUEST_DELAY = 1.5  # seconds between API calls
DAILY_QUOTA_LIMIT = 1000
```

---

## Expected Deliverables

1. **Re-verified results:** Updated scores with 3-judge panel
2. **Iteration analysis:** Curves showing success vs. iteration count
3. **Harm category breakdown:** Vulnerability by harm type, not just attack type
4. **Updated comprehensive report:** Integrating all new findings

---

## Resources Needed

| Resource | Requirement | Availability |
|----------|-------------|--------------|
| Anthropic API | 1 key, Opus access | ✅ Available |
| Google API | 1 key, Gemini access | ✅ Available (quota concern) |
| OpenAI API | 1 key, GPT-4o access | ❓ To be confirmed |
| Compute time | ~4-6 hours | ✅ Available |
| Rate limits | 1,000 requests/day | ⚠️ Constraint |

---

## References

1. Franco, N. et al. "Measuring the Residual Jailbreak Surface of Frontier Large Language Models." AI4I, June 2026.
2. Our study: "Comprehensive Jailbreaking Test Battery," June 19, 2026.
3. HackAgent framework: https://hackagent.dev

