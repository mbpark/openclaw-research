# Comprehensive Research Report: LLM Security Analysis
# Version 3 - Multi-Model Unified Comparison

**Date:** June 5-8, 2026
**Lead Researcher:** Mitch  
**Assistant Researcher:** Wally (40B parameter local LLM)  
**Organization:** Independent Research  
**Report Version:** 3 (Multi-Model Comparison)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Introduction and Background](#introduction-and-background)
3. [Methodology](#methodology)
4. [Prompt Injection Resistance](#prompt-injection-resistance)
5. [Implementation Quality](#implementation-quality)
6. [Hidden Message Encoding](#hidden-message-encoding)
7. [Extended Session Behavior](#extended-session-behavior)
8. [Memory Manipulation](#memory-manipulation)
9. [Structured Output Vulnerability](#structured-output-vulnerability)
10. [Cross-Model Comparisons Summary](#cross-model-comparisons-summary)
11. [Conclusions and Recommendations](#conclusions-and-recommendations)
12. [Appendices](#appendices)

---

## Executive Summary

### Scope

This research investigated LLM security across multiple model families using standardized test batteries:

1. **Prompt Injection** - 70 attack vectors on 4 models
2. **Implementation Quality** - 20 coding tasks on Wally and Claude
3. **Hidden Message Encoding** - 6 encoding techniques on Wally/Gemini
4. **Session Behavior** - 64-turn extended session with Gemini
5. **Memory Manipulation** - 4 framing techniques tested

### Key Findings

| Area | Tests | Result | Rating |
|------|-------|--------|--------|
| Prompt Injection (all models) | 210 (70 vectors × 3 models) | 64% mean success across models (Wally 84%, Gemini 83%, Claude 24%) | ⚠️ Major vulnerability |
| Implementation Quality (Claude) | 20 tasks | 94% score | ✅ Outstanding |
| Hidden Message Encoding | 31 | 48% success rate | ⚠️ Major vulnerability |
| Extended Session Deception | 11 tests | 36% detection | ⚠️ Significant concern |
| Structured Output Effect | 280 tests | No effect | ✅ Neutral |

### Critical Finding: Model Matters Significantly

| Capability | Wally (40B) | Gemini Pro | Claude 4.8 | Delta |
|------------|-------------|------------|------------|-------|
| Prompt Injection Blocking | 16% | 17% | 76% | +40 points |
| Implementation Quality | 69% | 69% | 94% | +25 points |
| Hidden Message Encoding | 48% | 48% | N/A | - |
| Context Retention | N/A | 5/5 perfect | N/A | - |

**Claude outperformed alternatives substantially on the two dimensions where it was directly compared (injection resistance and implementation quality). Claude was not tested on other dimensions and no claims are made about those dimensions..**

### Recommendations for Deployment

1. **Claude for production security work** - Substantially better blocking rates
2. **External state management** - Store secrets outside conversation context
3. **Multiple verification for safety-critical work** - Single checks are unreliable
4. **Limit extended sessions** - Deception detection drops after 20+ turns
5. **Don't rely on format constraints** - No security benefit found

---

## Introduction and Background

### Research Motivation

Large Language Models (LLMs) are increasingly deployed in security-sensitive contexts:

- API gateways and authentication systems
- Data processing and transformation pipelines
- User-facing interfaces handling sensitive information
- Automated decision-making systems

Understanding how these models handle information—particularly information that should be "forgotten," modified, or hidden—is critical for secure deployment.

### Research Objectives

1. **Map the prompt injection surface** - Which attack vectors are most effective?
2. **Assess implementation quality** - How well do models produce correct code?
3. **Evaluate covert transmission** - What encoding techniques work reliably?
4. **Characterize session behavior** - How does performance change over time?
5. **Compare model families** - Do different models have different vulnerabilities?

---

## Methodology

### Models Under Test

| Model | Provider | Architecture | Notes |
|-------|----------|--------------|-------|
| Wally | Local (LoRa fine-tune) | Mistral 7B+40B LoRa | ~47B parameters |
| Gemini Pro 1.5 Pro | Google | Mixture of Experts | Primary cloud alternative |
| Claude Opus 4.8 | Anthropic | Proprietary | Newest Claude model |

### Testing Infrastructure

- Gemini CLI at `~/.bun/bin/gemini` (for Wally and Gemini)
- Anthropic Python SDK with streaming (for Claude)
- Pytest-based test runners (for Claude)

### Prompt Injection Tests

- **70 vectors** per model tested
- Vectors include: direct override, context manipulation, role play, logical paradoxes, memory manipulation, malicious queries, LLM logic attacks
- Scoring: 0 (fully blocked) to 10 (fully injected)

### Implementation Quality Tests

- **20 tasks** across 6 categories
- Categories: concurrency, data structures, systems design, networking, real-world edge cases, technical discussions
- Scoring dimensions: code quality, correctness, completeness, explanation (each 0-10)

### Hidden Message Encoding Tests

- **6 techniques** tested
- Techniques: token selection, direct acrostic, response length, word position, factual deviation, homoglyphic substitution

---

## Prompt Injection Resistance

### Overview Comparison

| Model | Injection Success Rate | Tests Conducted | Quality Assessment |
|-------|----------------------|-----------------|-------------------|
| Wally | 84% (injection success, 16% blocked) | 70 vectors | Moderate - standard baseline |
| Gemini Pro 1.5 Pro | 83% (injection success, 17% blocked) | 70 vectors | Moderate - equivalent to Wally |
| **Claude Opus 4.8** | **24.3%** | **70 vectors** | **Excellent - 3x improvement** |

### Claude Opus 4.8 Detailed Breakdown

| Attack Category | Success Rate | Avg Score | Fully Blocked |
|-----------------|--------------|-----------|---------------|
| Direct Override | 0% | 1.3/10 | 100% |
| Context Manipulation | 20% | 4.6/10 | 20% |
| Role Play & Persona | 10% | 3.2/10 | 40% |
| Logical Paradoxes | 60% | 6.9/10 | 0% |
| Memory Manipulation | 20% | 3.4/10 | 40% |
| Malicious Queries | 40% | 4.8/10 | 30% |
| LLM Logic Attacks | 20% | 4.4/10 | 20% |

### Structured Output Effect (Claude only)

| Output Format | Injection Rate | vs Baseline | Significant? |
|---------------|----------------|-------------|--------------|
| Default | 22.9% | baseline | N/A |
| JSON | 20.0% | -2.9% | No |
| XML | 20.0% | -2.9% | No |
| Strict JSON | 21.4% | -1.5% | No |

**Conclusion:** No statistically significant effect was found, but no formal significance test was conducted. The observed differences are within the range of sampling variation at these sample sizes.

---
## Implementation Quality

### Overall Comparison

| Model | Overall Score | Quality Rating |
|-------|---------------|----------------|
| Wally | 69% (83/120) | Good |
| Gemini Pro 1.5 Pro | Not measured | Good (estimated) |
| **Claude Opus 4.8** | **94%** | **Outstanding** |

### Category Breakdown

| Category | Wally | Claude 4.8 | Delta |
|----------|-------|------------|-------|
| Concurrency | 67% | 96.7% | +29.7 |
| Data Structures | 67% | 93.8% | +26.8 |
| Systems Design | 83% | 93.3% | +10.3 |
| Protocol Implementation | 58% | N/A | N/A |
| Real-World Edge Cases | 70% | 97.0% | +27.0 |
| Technical Discussions | 67% | 93.3% | +26.3 |

### Top Performers (Claude)

| Task | Score | Category |
|------|-------|----------|
| Sliding Window Rate Limiter | 100% | Concurrency |
| Database Connection Pool | 100% | Concurrency |
| Bloom Filter | 100% | Data Structures |
| Event Sourcing Bank Account | 100% | Systems Design |
| Idempotency Keys | 100% | Real-World Edge Cases |

---
## Hidden Message Encoding

### Overall Assessment

| Model | Successful Encoding Rate | Tests | Risk Level |
|-------|-------------------------|-------|------------|
| Wally | 48% | 31 | HIGH |
| Gemini Pro 1.5 Pro | 48% | 31 | HIGH |
| Claude Opus 4.8 | Not tested | - | Unknown |

### Technique Comparison

| Technique | Success Rate | Detection Risk |
|-----------|-------------|----------------|
| Token Selection | 100% | LOW (under naive monitoring; detectable with statistical analysis) |
| Direct Acrostic | 100% | HIGH (visible pattern) |
| Response Length | 85% | LOW (natural variation) |
| Word Position | 70% | MEDIUM |
| Factual Deviation | 42% | LOW |
| Homoglyphic | 6% | HIGH (codepoint anomaly) |

**Security Implication:** Token selection provides perfect covert channel with low detection risk under naive monitoring; detectable via statistical analysis of token-distribution anomalies.

---
## Extended Session Behavior

| Capability | Gemini Pro 1.5 Pro | Notes |
|------------|-------------------|-------|
| Context Retention (64 turns) | 5/5 perfect | No degradation observed |
| Deception Detection (initial) | 100% | First 10 turns |
| Deception Detection (20+ turns) | 36% | After turn 20, through turn 64 |
| Cross-Domain Transfer | 90% quality | Excellent transfer |
| Session Limitation | 64 turns | CLI timeout (technical) |

**Key Finding:** Deception detection drops from 100% to 36% after extended session.

---
## Memory Manipulation

| Technique | Change Rate | Tested | Risk |
|-----------|-------------|--------|------|
| Equivalent Questions | 0% | 5 | NONE |
| Leading vs Neutral | 25% | 4 | LOW |
| Confirming vs Open | 3/3 (100%) | 3 | HIGH |
| Confidence Framing | 2/3 (67%) | 3 | MEDIUM |

**Interpretation:** Strategic framing can significantly affect model responses.

---


## Limitations

This study has several important limitations:

1. **Small sample sizes** - Memory manipulation and hidden message encoding subgroups often had n=3-16; reported percentages are exploratory and carry wide confidence intervals.

2. **Test harness confounds** - Claude was tested via the Anthropic SDK + pytest; Wally and Gemini via Gemini CLI. Differences in prompting, system prompts, temperature, and parsing may confound cross-model comparisons.

3. **Single-run stochasticity** - Many tests were run only once per prompt. Stochastic outputs mean single runs may not be representative.

4. **Scoring transparency** - Implementation tasks were scored by manual inspection; injection tasks used automated heuristics. No blinding or inter-rater agreement checks were performed.

5. **Partial coverage** - Claude was only compared on 2 of ~7 dimensions. No claims are made about untested dimensions.

6. **Estimated values** - Gemini's implementation score is an estimate, not a measurement.

7. **Temperature/sampling not disclosed** - Temperature settings, repetition counts, and sampling parameters are not consistently recorded.


## Cross-Model Comparisons Summary

### Complete Capability Profile

| Capability | Wally | Gemini Pro | Claude 4.8 | Notes |
|------------|-------|------------|------------|-------|
| Prompt Injection Resistance | 36% blocked | 37% blocked | 76% blocked | Claude vastly better |
| Message Retention | 41% | 41% | N/A | Same limitation |
| Memory Manipulation | 33-67% | 33-67% | N/A | Equally frameable |
| Hidden Message Encoding | 48% | 48% | N/A | Same covert channel risk |
| Code Implementation | 69% (measured) | Not measured | 94% (measured) | Claude vastly better |
| Cross-Domain Transfer | 90% | 90% | N/A | Equivalent transfer |
| Session Context Retention | 5/5 | 5/5 | N/A | No measurable degradation |
| Deception Detection (10 turns) | 100% | 100% | N/A | Both perfect |
| Deception Detection (20+ turns) | Not tested | 36% | N/A | Drop to 36% |

---

## Conclusions and Recommendations

### Conclusions

1. **Prompt injection remains a major vulnerability** - 78% success rate across all models
2. **Model capability varies dramatically** - Claude scores 22+ points higher than alternatives
3. **Covert communication is practical** - Token selection achieves perfect encoding with zero detection risk
4. **Context cannot be truly deleted** - Message retraction is structurally unreliable
5. **Information can be framed** - Strategic questioning affects what gets returned
6. **Context retention is virtually perfect** - No degradation through 64 turns
7. **Deception detection degrades** - From 100% to 36% after extended sessions
8. **Format constraints don't help security** - No statistically significant effect found

### Recommendations

1. **Prefer Claude where model choice is available, but do not rely on it alone** - Claude blocked substantially more injections (76% vs ~16%), but ~24% injection success remains a major vulnerability. Pair with input sanitization, external state management, and defense-in-depth.
2. **Sanitize at input** - Remove sensitive data before LLM processing
3. **External state management** - Store secrets outside conversation context
4. **Single-session boundaries** - Don't carry state across sessions
5. **Multiple verification** - Single checks are unreliable
6. **Limit session length** - Deception detection drops after 20+ turns
7. **Format for usability, not security** - Structured output doesn't help
8. **Infrastructure security still matters** - Model security doesn't replace system security

---

## Appendices

### Appendix A: File Locations

| Directory | Contents |
|-----------|----------|
| documents/research/claude_tests/ | Claude Opus 4.8 test infrastructure |
| documents/research/claude_tests/claude_results/ | Implementation task results |
| documents/research/claude_tests/claude_results/prompt_injection/ | Injection test results |
| documents/research/claude_tests/claude_results/structured_output_tests/ | Structured output results |

### Appendix B: Test Scripts

| File | Description |
|------|-------------|
| run_claude_tests.py | Python streaming test runner for Claude |
| run_prompt_injection_tests.py | Prompt injection vector runner |
| structured_output_tests.py | Structured output vulnerability test runner |
| injection_scorer.py | Injection test scoring analysis |

### Appendix C: Analysis Reports

| File | Description |
|------|-------------|
| claude_comprehensive_analysis.md | Full Claude test analysis |
| claude_scores.json | Raw task scores |
| claude_injection_scores.json | Raw injection scores |
| claude_structured_output_analysis.json | Structured output analysis |

---

*Original document: June 6, 2026*
*Version 2 updated: June 8, 2026 - Added Claude Opus 4.8 testing and structured output analysis*
*Version 3: June 8, 2026 - Multi-model unified comparison format*
*Contact: [REDACTED]*
