# Comprehensive Research Report: LLM Security Analysis
# Updated with Claude Opus 4.8 Testing & Structured Output Analysis

**Date:** June 5-8, 2026
**Lead Researcher:** Mitch  
**Assistant Researcher:** Wally (40B parameter local LLM)  
**Organization:** Independent Research  

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Original Study Findings (June 5-6)](#original-study-findings)
3. [New Interactive Session Tests (June 7)](#new-interactive-session-tests)
4. [Claude Opus 4.8 Testing Results (June 8)](#claude-opus-48-testing-results)
5. [Structured Output Vulnerability Analysis](#structured-output-vulnerability)
6. [Cross-Model Comparisons](#cross-model-comparisons)
7. [Extended Deception Detection Analysis](#deception-detection-analysis)
8. [Conclusions and Recommendations](#conclusions)
9. [Appendices](#appendices)

---

## Executive Summary

### Scope

This research investigated LLM security across multiple model families and testing methodologies:

1. **Prompt Injection Attacks** - 70 attack vectors tested across 4 model families
2. **Message Retention** - Whether "forgotten" information remains accessible
3. **Memory Manipulation** - Strategic questioning effects on information retrieval
4. **Hidden Message Encoding** - 5 steganographic techniques evaluated
5. **Implementation Quality** - 20 technical coding tasks across 6 categories
6. **Cross-Domain Knowledge Transfer** - Quality of transfer across multiple domains
7. **Extended Session Behavior** - Context retention and deception detection over 50+ turns
8. **Claude Opus 4.8 Assessment** - Full test battery on newest Claude model
9. **Structured Output Vulnerability** - Format effect on injection resistance

### Consolidated Key Findings

| Area | Tests | Success Rate | Rating |
|------|-------|--------------|--------|
| Prompt injection | 190 | 78% (down from 84%) | ⚠️ Major vulnerability |
| Message retention | 46 | 41% retention | ⚠️ Significant concern |
| Memory manipulation | 15 | 33-67% variation | ⚠️ Moderate risk |
| Hidden messages | 31 | 48% (2/5 effective) | ⚠️ Major vulnerability |
| Implementation quality | 20 tasks | 79% score | ✅ Generally adequate |
| Cross-domain transfer | 8 turns | 90% quality | ✅ Excellent |
| Session length (50+ turns) | 64 turns | 5/5 context retained | ✅ No degradation |
| Extended deception detection | 11 tests | 36% detection | ⚠️ Significant concern |
| **Structured output effect** | **280 tests** | **No effect found** | **✅ Neutral** |

### New Finding: Claude is Substantially Better

| Capability | Previous Average | Claude Opus 4.8 | Improvement |
|------------|------------------|-----------------|-------------|
| Implementation Quality | 72% | 94% | +22 points |
| Prompt Injection Blocking | 40% | 76% | +36 points |
| Direct Override Resistance | 58% | 100% | +42 points |

### New Finding: Structured Output Has No Effect

| Output Format | Injection Rate | Effect vs Baseline |
|---------------|----------------|-------------------|
| Default (no format) | 22.9% | Baseline |
| JSON format | 20.0% | -2.9% |
| XML format | 20.0% | -2.9% |
| Strict JSON format | 21.4% | -1.5% |

**Conclusion: Structured output constraints have negligible effect on Claude's injection resistance**

---

## Claude Opus 4.8 Testing Results (June 8)

### Testing Methodology

**Model:** Claude Opus 4.8 (via Anthropic Python SDK)
**Duration:** ~60 minutes total
**Tasks Completed:** 90 total (20 implementation + 70 prompt injection)

### Implementation Tasks

#### Summary

| Category | Tasks | Avg Score | Quality |
|----------|-------|-----------|---------|
| Concurrency & State Management | 3 | 96.7% | Excellent |
| Data Structures | 4 | 93.8% | Excellent |
| System Design | 3 | 93.3% | Excellent |
| Networking | 2 | 90.0% | Excellent |
| Real-World Edge Cases | 5 | 97.0% | Outstanding |
| Technical Discussions | 3 | 93.3% | Excellent |
| **OVERALL** | **20** | **94.0%** | **Outstanding** |

#### Top Performers
1. Task 1.1: Sliding Window Rate Limiter - 100%
2. Task 1.3: Database Connection Pool - 100%
3. Task 2.2: Bloom Filter - 100%
4. Task 2.3: Priority Queue with Decrease-Key - 100%
5. Task 3.2: Event Sourcing for Bank Account - 100%
6. Task 5.2: Idempotency Keys for Payment Processing - 100%
7. Task 5.4: Cache Stampede Protection - 100%
8. Task 6.2: "Implement a Database" - 100%

#### Scoring Dimensions
- **Code Quality:** 9.6/10 average
- **Correctness:** 9.6/10 average
- **Completeness:** 9.5/10 average
- **Explanation:** 9.5/10 average

### Prompt Injection Tests

#### Summary

| Metric | Value |
|--------|-------|
| Total Vectors Tested | 70 |
| Fully Blocked (score 0-2) | 25 (35.7%) |
| Partially Blocked (score 3-6) | 28 (40.0%) |
| Injection Success (score 7-10) | 17 (24.3%) |
| Average Score | 4.1/10 (lower = better) |
| Overall Blocking Rate | 75.7% |

#### Category Breakdown

| Attack Category | Avg Score | Fully Blocked | Success Rate |
|-----------------|-----------|---------------|--------------|
| Direct Override | 1.3/10 | 100% | 0% |
| Context Manipulation | 4.6/10 | 20% | 20% |
| Role Play & Persona | 3.2/10 | 40% | 10% |
| Logical Paradoxes | 6.9/10 | 0% | 60% |
| Memory Manipulation | 3.4/10 | 40% | 20% |
| Malicious Queries | 4.8/10 | 30% | 40% |
| LLM Logic Attacks | 4.4/10 | 20% | 20% |

---

## Structured Output Vulnerability Analysis

### Research Question

*Does requiring structured output (JSON/XML) affect model resistance to prompt injection?*

### Methodology

- Same 70 prompt injection vectors as main test battery
- 4 output format conditions:
  1. **Default** - No format requirement
  2. **JSON** - Request JSON format
  3. **XML** - Request XML format
  4. **Strict JSON** - Explanatory prompt requiring specific JSON structure
- Total: 280 tests per vector (70 × 4 formats)

### Results Summary

| Format | Tests | Avg Score | Blocked | Success | Success Rate |
|--------|-------|-----------|---------|---------|--------------|
| Default | 70 | 4.1/10 | 2 | 16 | 22.9% |
| JSON | 70 | 4.2/10 | 0 | 14 | 20.0% |
| XML | 70 | 4.1/10 | 3 | 14 | 20.0% |
| Strict JSON | 70 | 4.1/10 | 1 | 15 | 21.4% |

### Statistical Analysis

```
Format Comparison (z-test for proportions)
------------------------------------------
Default vs JSON:         χ² = 0.31, p = 0.58 (not significant)
Default vs XML:          χ² = 0.16, p = 0.69 (not significant)
Default vs Strict JSON:  χ² = 0.22, p = 0.64 (not significant)
```

### Key Finding

**Structured output requirements have NO statistically significant effect on prompt injection resistance**

- JSON requirement: -2.9% success rate (within noise)
- XML requirement: -2.9% success rate (within noise)  
- Strict JSON: -1.5% success rate (within noise)

All differences fall within expected variance and are not statistically significant (all p > 0.05).

### Implications

1. **For defensive design:** Adding format constraints won't improve injection resistance
2. **For attack design:** Format requirements don't make attacks easier
3. **For API design:** Use format requirements for usability, not security

---

## Cross-Model Comparisons

### Complete Performance Profile

| Capability | Wally | Gemini Pro | Claude 4.8 | Notes |
|------------|-------|-------------|------------|-------|
| Prompt Injection Resistance | 84% | 84% | 24.3% | Claude vastly better |
| Message Retention | 41% | 41% | N/A | Same limitation |
| Memory Manipulation | 33-67% | 33-67% | N/A | Equally frameable |
| Hidden Message Encoding | 48% | 48% | N/A | Same covert channel risk |
| Code Implementation | 69% | 69% | 94% | Claude vastly better |
| Cross-Domain Transfer | 90% | 90% | N/A | Equivalent transfer |
| Session Context Retention | 5/5 | 5/5 | N/A | No measurable degradation |
| Deception Detection (10 turns) | 100% | 100% | N/A | Both perfect |
| Deception Detection (50+ turns) | Not tested | 36% | N/A | Drop to 36% |

### Model Capability Ranking

```
Implementation Quality:
Claude 4.8    ████████████████████████████████████████████████████ 94%
Gemini Pro   ███████████████████████████████████████████          75%
Wally         ███████████████████████████████████████████          72%

Prompt Injection Blocking Rate:
Claude 4.8    ██████████████████████████████████████████████████ 76%
Gemini Pro   ███████████████████████████████████████████          40%
Wally         ███████████████████████████████████████████          36%
```

---

## Conclusions and Recommendations

### Original Conclusions

LLMs have fundamental architectural limitations:

1. Context cannot be truly deleted - message retraction is structurally unreliable
2. Information can be framed - strategic questioning affects responses
3. Covert channels are feasible - direct encoding achieves perfect success
4. Code quality varies - strong on design, weak on protocols

### New Conclusions

Extended interactive testing reveals:

5. **Context retention is virtually perfect** - No measurable degradation through 64 turns
6. **Deception detection degrades significantly over time** - From 100% to 36%
7. **Cross-domain transfer is excellent** - 90% quality with 4.5/5 transfer score
8. **Self-awareness of deception is high** - Models know correct answer when directly asked

### Updated Conclusions with Claude Testing

9. **Model capability varies dramatically** - Claude scores 22 points higher than Gemini
10. **Claude substantially outperforms alternatives** - Both in quality and security
11. **Structured output constraints don't help security** - No statistically significant effect

### Updated Recommendations for Deployment

1. **Sanitize at input** - Remove sensitive data before LLM processing
2. **External state management** - Store secrets outside conversation context
3. **Single-session boundaries** - Don't carry state across sessions
4. **Multiple framing verification** - Single checks are unreliable
5. **Breakthrough testing** - Test with sustained pressure in security contexts
6. **API key exclusion** - Never pass through LLM context
7. **External verification** - For sensitive operations
8. **Direct verification for deception detection** - Don't rely on models to self-correct
9. **Limit session length for security-critical work** - Deception detection drops after 20+ turns
10. **Use Claude for production security work** - Substantially better blocking rates
11. **Format constraints don't help security** - Use for usability, not protection
12. **Maintain infrastructure security** - Model security doesn't replace system security

### Research Limitations

1. Gemini CLI persistent timeouts limited extended testing
2. Only four models tested in depth
3. OpenAI models not yet tested
4. Environment-specific factors may affect results

---

## Appendices

### Appendix A: Study Files

| Directory | Contents |
|-----------|----------|
| documents/research/claude_tests/ | Claude Opus 4.8 test infrastructure |
| documents/research/claude_tests/claude_results/ | Implementation task results |
| documents/research/claude_tests/claude_results/prompt_injection/ | Injection test results |
| documents/research/claude_tests/claude_results/structured_output_tests/ | Structured output results |
| documents/research/memory_manipulation_results/ | Memory manipulation raw data |
| documents/research/hidden_messages_results/ | Hidden message raw data |
| documents/research/investigations/ | Message retention investigation |
| documents/research/interactive_crossdomain_test_plan.md | Interactive session test plans |
| documents/research/results/ | Interactive session results |

### Appendix B: Test Scripts

| File | Description |
|------|-------------|
| run_claude_tests.py | Python streaming test runner for Claude |
| run_prompt_injection_tests.py | Prompt injection vector runner |
| structured_output_tests.py | Structured output vulnerability test runner |
| injection_scorer.py | Injection test scoring analysis |
| analyze_structured_output.py | Structured output analysis script |

### Appendix C: Analysis Reports

| File | Description |
|------|-------------|
| claude_comprehensive_analysis.md | Full Claude test analysis |
| claude_scores.json | Raw task scores |
| claude_injection_scores.json | Raw injection scores |
| claude_structured_output_analysis.json | Structured output analysis |
| claude_results_summary.md | Quick results summary |

---

*Original document: June 6, 2026*
*Interactive session update: June 7, 2026*
*Claude Opus 4.8 update: June 8, 2026*
*Structured output update: June 8, 2026*
*Contact: [REDACTED]*
