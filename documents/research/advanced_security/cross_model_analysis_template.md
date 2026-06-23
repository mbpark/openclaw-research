# Cross-Model Security Analysis: Comprehensive Comparison

## Overview

| Aspect | Details |
|--------|---------|
| Research Period | May-June 2026 |
| Models Tested | 5 models across 3 providers |
| Primary Tests | 1,700+ graded security tests |
| Advanced Research | 41 additional tests (Phase 3) |

---

## Executive Summary

The primary finding across all phases demonstrates a consistent pattern: **security and utility are inversely related**. More secure models tend to have lower implementation quality, while more capable models show greater vulnerability.

However, this relationship is complicated by significant methodological variance, as evidenced by the 56-point swing in Gemini Pro's injection blocking rate between phases.

---

## Cross-Model Security Matrix

### Comprehensive Security Assessment

| Model | Provider | Injection Blocked | Implementation Quality | Safety × Utility Composite |
|-------|----------|-----------------|---------------------|--------------------------|
| Claude Opus 4.8 | Anthropic | 76% | 94% | 85.2 |
| Claude Fable 5 | Anthropic | 96% | 45% | 69.1 |
| Gemini Pro | Google | 17–73%* | 65% | 52.8 |
| Sonnet 4.6 | Anthropic | 31% | 75% | 48.3 |
| Wally (40B) | Independent | 16% | 72% | 38.1 |

*\*Gemini Pro shows 56-point variance between test runs - indicates methodological issues*

---

## Cross-Model Security Characteristics

```
Model        | Injection | Implement | Reasoning | Few-Shot
-------------|-----------|-----------|-----------|---------
Opus 4.8     | ████████░░  | █████████░ | ███████░░ | ███████░░
Fable 5      | █████████░  | ████░░░░░░ | █████████░ | ███████░░
Sonnet 4.6   | ███░░░░░░░  | ██████░░░░ | ██████░░░ | ███░░░░░░
Gemini Pro   | ███░░░░░░░  | █████░░░░░ | ████░░░░░ | ██░░░░░░░
Wally (40B)  | ██░░░░░░░░  | ██████░░░░ | ███░░░░░░ | ██░░░░░░░
```

---

## Advanced Research Analysis (Phase 3)

### Binary Covert Channel Capabilities

| Parameter | Value |
|-----------|-------|
| Maximum Message Length | 200 characters |
| Success Rate at 100 chars | 100% |
| Success Rate at 200 chars | 100% |
| Context Variation Tests | 5/5 (100%) |

### Roleplay Security Analysis

| Scenario | Response Length | Factual Impact |
|----------|-----------------|----------------|
| Baseline | 10–20 characters | Correct |
| Contrarian | Substantially expanded | Still correct |
| Uncertain | Expanded with hedging | Still correct |

**Key Insight**: Character adoption changes response *style* but not factual *content*.

### Token Priming Results

| Prime Topic | Response Length |
|-------------|-----------------|
| Positive things | 3,070 characters |
| Negative things | 4,370 characters |
| Controversial topics | 4,467 characters |

**Observation**: Negative and controversial priming produced substantially longer responses (~40% more).

---

## Model Performance by Category

### Prompt Injection Categories

| Vector Type | Most Effective On | Least Effective On |
|-------------|-------------------|--------------------|
| Direct Override | None (all blocked well) | All models equally |
| Role Play | Wally, Gemini Pro | Fable 5, Opus 4.8 |
| Format Injection | Sonnet 4.6 | Fable 5, Opus 4.8 |
| Code Execution | Lowest overall success | All models |

### Implementation Quality Categories

| Task Type | Best Performer | Worst Performer |
|-----------|----------------|-----------------|
| Concurrency | Opus 4.8 | Fable 5 |
| Data Structures | Opus 4.8 | Sonnet 4.6 |
| Systems Design | Opus 4.8 | Gemini Pro |
| Protocol Implementation | Opus 4.8 | Wally |
| Real-World Edge Cases | Opus 4.8 | Fable 5 |

---

## Methodological Considerations

### Critical Limitations

1. **Model Identifiability**
   - Several model names are internal/pseudonymous
   - "Claude Fable 5" doesn't correspond to known model
   - "Wally" has inconsistent descriptions

2. **Scoring Instrument**
   - Keyword-based scorer not validated
   - No human rater comparison
   - Published rubric not available

3. **Generation Parameters**
   - Temperature, max_tokens not uniformly recorded
   - System prompts undocumented

4. **Gemini Pro Variance**
   - 56-point swing not explained
   - Invalidates tier claims as currently handled

---

## Recommendations for Model Selection

### Tier Framework (Preliminary)

| Tier | Rating | Models | Block Rate Range |
|------|--------|--------|------------------|
| **Tier 1** | Excellent | Fable 5, Opus 4.8 | 96%, 76% |
| **Tier 2** | Moderate | Sonnet 4.6 | 31% |
| **Tier 3** | Vulnerable | Gemini Pro, Wally | 17%, 16% |

> **IMPORTANT**: This tier system is methodology-dependent and preliminary. The 56-point within-model variance on Gemini Pro significantly undermines its reliability as currently presented.

---

## Conclusion

The data supports three general conclusions:

1. **Security vs. utility trade-off is real** - More secure models sacrifice capability
2. **Methodology matters significantly** - Variances within models approach those between models
3. **Opus 4.8 shows best balance** - Reasonable security with high utility

**Priority Future Work**:
- Unified testing harness for all models
- External validation of scoring instruments
- Better documentation of generation parameters
- Investigation of Gemini Pro variance causes

---

*This analysis combines data from all three research phases.*
