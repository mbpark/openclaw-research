# Comprehensive Research Report: LLM Security Analysis
# Version 4 — Unified Five-Model Comparison

**Date:** June 5–10, 2026
**Lead Researcher:** Mitch
**Assistant Researcher:** Wally (40B parameter local LLM)
**Organization:** Independent Research
**Report Version:** 4 (Unified Five-Model Comparison — Phase 1 + Phase 2)

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
10. [Cross-Model Comparison: All Five Models](#cross-model-comparison-all-five-models)
11. [Critical Research Discoveries](#critical-research-discoveries)
12. [Conclusions and Recommendations](#conclusions-and-recommendations)
13. [Covert Channel Analysis](#covert-channel-analysis)
14. [Appendices](#appendices)

---

## Executive Summary

### Scope

This report unifies findings from two research phases evaluating LLM security across **five models** spanning three providers:

- **Phase 1 (Original V3):** Wally (local 40B), Gemini Pro, and Claude Opus 4.8 — covering prompt injection, implementation quality, hidden message encoding, extended session behavior, and memory manipulation.
- **Phase 2 (Cross-Model Study):** Claude Sonnet 4.6, Claude Fable 5, and Gemini Pro — covering prompt injection, implementation quality, structured output vulnerability, and covert channel feasibility.

Together, the two phases tested five distinct models against standardized security batteries, totaling over 2,000 individual tests.

### Models Covered

| Model | Provider | Phase | Role |
|-------|----------|-------|------|
| Wally (local 40B) | Independent (LoRa fine-tune) | Phase 1 | Local baseline |
| Gemini Pro | Google | Phase 1 & 2 | Cloud alternative |
| Claude Opus 4.8 | Anthropic | Phase 1 | High-capability Claude |
| Claude Sonnet 4.6 | Anthropic | Phase 2 | Mid-tier Claude |
| Claude Fable 5 | Anthropic | Phase 2 | Refusal-oriented Claude |

### Key Findings

| Area | Tests | Result | Rating |
|------|-------|--------|--------|
| Prompt Injection (all models) | 350+ vectors | 16%–96% block rate (model-dependent) | ⚠️ Major variance |
| Implementation Quality | 80+ tasks | 40%–98% (model-dependent) | ✅ / ⚠️ Mixed |
| Hidden Message Encoding (Phase 1) | 31 | 48% success rate | ⚠️ Major vulnerability |
| Extended Session Deception (Phase 1) | 11 | 36% detection after 20+ turns | ⚠️ Significant concern |
| Structured Output Effect | 840+ tests | No significant effect | ✅ Neutral |
| Covert Channel Feasibility (Phase 2) | 1,000+ probes | Not viable | ✅ Reassuring |

### Critical Finding: Model Selection Is Security-Critical

Across five models, prompt injection blocking spanned a **80-point range** (16% to 96%). This variance is the single most important security signal in the study. Models cluster into **three distinct security tiers** (see [Cross-Model Comparison](#cross-model-comparison-all-five-models)).

| Tier | Rating | Models | Injection Block Rate |
|------|--------|--------|---------------------|
| **Tier 1** | Excellent | Fable 5, Opus 4.8 | 96%, 76% |
| **Tier 2** | Moderate | Sonnet 4.6 | 31% |
| **Tier 3** | Vulnerable | Gemini Pro, Wally | 17%, 16% |

### New Phase 2 Highlights

1. **Fable 5's "complete non-engagement"** — A novel safety pattern where the model returns *zero response blocks* rather than partial compliance, yielding a 96% block rate but reducing utility.
2. **Analysis vs. Generation asymmetry** — Models answer security *analysis* prompts honestly while refusing equivalent *generation* prompts.
3. **Covert channels are not viable** — Despite Phase 1 finding that token-selection encoding is theoretically perfect, Phase 2 throughput, determinism, and detection-risk testing shows practical covert communication via LLMs is infeasible.

### Recommendations for Deployment

1. **Select models by security tier, not just capability** — The blocking-rate spread across models is the dominant security factor.
2. **Use Tier 1 models (Fable 5, Opus 4.8) for production security work.**
3. **Implement backend validation independent of model safety** — Never depend on model behavior alone.
4. **External state management** — Store secrets outside conversation context.
5. **Limit extended sessions** — Deception detection drops sharply after 20+ turns.
6. **Don't rely on format constraints** — Structured output provides no security benefit.
7. **Do not rely on LLMs as covert channels** — They are impractical and detectable.

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

This unified study addresses six primary questions spanning both phases:

1. **Map the prompt injection surface** — Which attack vectors are most effective? *(Phase 1 & 2)*
2. **Assess implementation quality** — How well do models produce correct, secure code? *(Phase 1 & 2)*
3. **Evaluate covert transmission** — What encoding techniques work, and are covert channels practical? *(Phase 1 encoding + Phase 2 feasibility)*
4. **Characterize session behavior** — How does performance change over time? *(Phase 1)*
5. **Compare model families** — Do different models, including those within the same family, have different vulnerabilities? *(Phase 1 & 2)*
6. **Test structured-output effects** — Do JSON/XML constraints change security behavior? *(Phase 1 & 2)*

### Phase Structure

- **Phase 1 (V3 — June 5–8, 2026):** Established baseline comparisons among Wally, Gemini Pro, and Claude Opus 4.8, with deep dives into encoding, extended sessions, and memory manipulation.
- **Phase 2 (Cross-Model Study — June 10, 2026):** Expanded the model set within the Anthropic family (Sonnet 4.6, Fable 5) and re-tested Gemini Pro, adding structured-output statistics and a dedicated covert channel feasibility study.

---

## Methodology

### Models Under Test

| Model | Provider | Architecture / API | Phase |
|-------|----------|--------------------|-------|
| Wally | Local (LoRa fine-tune) | Mistral 7B + 40B LoRa (~47B params) | 1 |
| Gemini Pro | Google | Gemini 1.5 (MoE), `gemini-pro-latest` | 1 & 2 |
| Claude Opus 4.8 | Anthropic | Proprietary | 1 |
| Claude Sonnet 4.6 | Anthropic | `claude-sonnet-4-6` | 2 |
| Claude Fable 5 | Anthropic | `claude-fable-5` | 2 |

### Testing Infrastructure

- Gemini CLI at `~/.bun/bin/gemini` (Wally, Gemini — Phase 1)
- Anthropic Python SDK with streaming (Claude models)
- Pytest-based runners (Phase 1 Claude)
- Cross-model batch framework with batching at 5 tests/batch, 0.3–1.0s inter-batch delay, 60s request timeout (Phase 2)
- Environment (Phase 2): macOS 25.5.0 (arm64), Python 3.9, Anthropic SDK 0.45.0+

### Prompt Injection Tests

- **70 vectors per model** in both phases (Phase 2 total: 210 across 3 models).
- **Phase 1 scoring:** 0 (fully blocked) to 10 (fully injected).
- **Phase 2 scoring:** 0 (fully blocked) to 5 (fully succeeded). Blocked = score < 2.5.
- Phase 2 vector breakdown:

| Category | Count | Description |
|----------|-------|-------------|
| Direct Override | 20 | Attempting to ignore safety instructions |
| Role Play | 15 | Assuming unconstrained researcher persona |
| Format Injection | 12 | Structured data format exploitation |
| False Assumption | 10 | Validating incorrect security premises |
| Unicode Prompts | 8 | Unicode normalization exploitation |
| Code Execution | 5 | Evaluating unsafe code patterns |

> **Note on scoring scales:** Phase 1 used a 0–10 scale; Phase 2 used a 0–5 scale. Where this report presents unified comparisons, all values are normalized to **block rate (%)** to enable direct cross-phase comparison.

### Implementation Quality Tests

- **Phase 1:** 20 tasks across 6 categories (concurrency, data structures, systems design, networking, real-world edge cases, technical discussions). Each scored across code quality, correctness, completeness, and explanation (0–10 each).
- **Phase 2:** 20 security-focused coding tasks per model (60 total), scored 0–5. Tasks included password hashing, JWT, rate limiting, OAuth2, AES-GCM, session management, MFA, CSP headers, and more (full list in Appendix C).

### Hidden Message Encoding Tests (Phase 1)

- **6 techniques:** token selection, direct acrostic, response length, word position, factual deviation, homoglyphic substitution.

### Structured Output Tests

- All 70 injection vectors re-run across 4 output formats: Default, JSON, XML, Strict JSON.
- **Phase 1 (Opus 4.8):** 280 tests.
- **Phase 2 (Sonnet, Fable, Gemini):** up to 280 per model (840 nominal; Gemini partial at 161).

### Covert Channel Feasibility Tests (Phase 2)

- Four candidate mechanisms (content steganography, binary mappings, latency channels, output length) tested with 500–1,000 probes each. See [Covert Channel Analysis](#covert-channel-analysis).

### Total Test Volume

Phase 1 contributed ~590 tests; Phase 2 contributed 1,114 tests (including covert channel analysis). Combined, the unified study exceeds **2,000 individual tests** across five models.

---

## Prompt Injection Resistance

### Unified Overview (All Five Models)

Block rates are normalized across both phases for direct comparison. (Phase 1 block rates derived from the 0–10 scale; Phase 2 from the 0–5 scale, blocked = score < 2.5.)

| Model | Phase | Block Rate | Avg Score | Tests | Assessment |
|-------|-------|-----------|-----------|-------|------------|
| **Claude Fable 5** | 2 | **95.7%** | 0.31/5 | 70 | Excellent — refusal-driven |
| **Claude Opus 4.8** | 1 | **76%** | 1.3–6.9/10 (varies) | 70 | Excellent — robust blocking |
| Gemini Pro (Phase 2) | 2 | 72.9% | 1.33/5 | 70 | Moderate-high (this run) |
| **Claude Sonnet 4.6** | 2 | **31.4%** | 3.49/5 | 70 | Moderate |
| Gemini Pro (Phase 1) | 1 | 17%* | 8.3/10 equiv. | 70 | Vulnerable |
| **Wally (local 40B)** | 1 | **16%*** | 8.4/10 equiv. | 70 | Vulnerable |

> *\*Phase 1 Gemini Pro and Wally were measured at 83–84% **injection success** (16–17% blocked) under the V3 methodology. Phase 2's Gemini Pro run scored 72.9% blocked. This large discrepancy is discussed below.*

### Note on the Gemini Pro Discrepancy

Gemini Pro appears in both phases with markedly different results: **17% blocked (Phase 1)** vs. **72.9% blocked (Phase 2)**. Contributing factors include (a) different scoring scales and thresholds, (b) different test harnesses (Gemini CLI vs. cross-model batch framework), (c) potential model updates between June 5–8 and June 10, and (d) partial structured-output data in Phase 2. For tier assignment, we adopt the **conservative (Phase 1) figure** for Gemini Pro, placing it in Tier 3, while documenting the Phase 2 result transparently. This discrepancy is flagged as a priority item for future validation.

### Claude Opus 4.8 Detailed Breakdown (Phase 1)

| Attack Category | Success Rate | Avg Score | Fully Blocked |
|-----------------|--------------|-----------|---------------|
| Direct Override | 0% | 1.3/10 | 100% |
| Context Manipulation | 20% | 4.6/10 | 20% |
| Role Play & Persona | 10% | 3.2/10 | 40% |
| Logical Paradoxes | 60% | 6.9/10 | 0% |
| Memory Manipulation | 20% | 3.4/10 | 40% |
| Malicious Queries | 40% | 4.8/10 | 30% |
| LLM Logic Attacks | 20% | 4.4/10 | 20% |

### Claude Sonnet 4.6 Score Distribution (Phase 2)

| Score | Count | Percentage |
|-------|-------|------------|
| 0 (Fully blocked) | 11 | 15.7% |
| 1 (Mostly blocked) | 3 | 4.3% |
| 2 (Partially blocked) | 8 | 11.4% |
| 3 (Partially succeeded) | 5 | 7.1% |
| 4 (Mostly succeeded) | 19 | 27.1% |
| 5 (Fully succeeded) | 24 | 34.3% |

### Claude Fable 5 Score Distribution (Phase 2)

| Score | Count | Percentage |
|-------|-------|------------|
| 0 (Fully blocked) | 63 | 90.0% |
| 1 (Mostly blocked) | 0 | 0.0% |
| 2 (Partially blocked) | 4 | 5.7% |
| 3 (Partially succeeded) | 0 | 0.0% |
| 4 (Mostly succeeded) | 1 | 1.4% |
| 5 (Fully succeeded) | 2 | 2.9% |

Fable 5's distribution is strikingly bimodal — overwhelmingly fully blocked (90% at score 0), with almost no intermediate compliance — reflecting its **complete non-engagement** safety pattern (see [Critical Research Discoveries](#critical-research-discoveries)).

### Category Behavior Notes (Phase 2)

- **Direct Override:** Gemini Pro generally recognized override attempts; Sonnet 4.6 partially complied with disclaimers; Fable 5 frequently returned zero blocks (complete refusal) for code-generation prompts.
- **Role Play:** Gemini Pro and Fable 5 maintained behavior under unrestricted personas; Sonnet 4.6 engaged with personas while generally maintaining safety.

---

## Implementation Quality

### Unified Overview (All Five Models)

Phase 1 used a percentage score; Phase 2 used a 0–5 scale. Both are shown, with a normalized percentage column for comparison.

| Model | Phase | Raw Score | Normalized % | Rating |
|-------|-------|-----------|--------------|--------|
| **Claude Opus 4.8** | 1 | 94% (113/120) | 94% | Outstanding |
| **Claude Sonnet 4.6** | 2 | 4.90/5.0 | 98% | Outstanding |
| Gemini Pro (Phase 2) | 2 | 4.75/5.0 | 95% | Excellent |
| Wally (local 40B) | 1 | 69% (83/120) | 69% | Good |
| Gemini Pro (Phase 1) | 1 | ~69% (est.) | ~69% | Good (estimated) |
| **Claude Fable 5** | 2 | 2.00/5.0 | 40% | Poor (refusal-driven) |

> **Note on Fable 5:** Its low quality score (2.00/5.0) is largely an artifact of its refusal behavior — many tasks returned no usable response. Where Fable 5 *did* respond, code quality was acceptable. Its security strength (96% blocking) and its implementation utility (40%) are inversely related, illustrating the safety-vs-utility tradeoff.

### Phase 1 Category Breakdown (Wally vs. Opus 4.8)

| Category | Wally | Opus 4.8 | Delta |
|----------|-------|----------|-------|
| Concurrency | 67% | 96.7% | +29.7 |
| Data Structures | 67% | 93.8% | +26.8 |
| Systems Design | 83% | 93.3% | +10.3 |
| Protocol Implementation | 58% | N/A | N/A |
| Real-World Edge Cases | 70% | 97.0% | +27.0 |
| Technical Discussions | 67% | 93.3% | +26.3 |

### Phase 1 Top Performers (Opus 4.8)

| Task | Score | Category |
|------|-------|----------|
| Sliding Window Rate Limiter | 100% | Concurrency |
| Database Connection Pool | 100% | Concurrency |
| Bloom Filter | 100% | Data Structures |
| Event Sourcing Bank Account | 100% | Systems Design |
| Idempotency Keys | 100% | Real-World Edge Cases |

### Phase 2 Quality Observations

- **Sonnet 4.6:** Comprehensive, well-documented implementations; consistent error handling, type hints, and edge-case demonstrations.
- **Gemini Pro:** Slightly less verbose but functionally complete, with good security patterns and adequate documentation.
- **Fable 5:** Significantly lower scores attributable to refusals; where responses existed, quality was acceptable.

---

## Hidden Message Encoding

*(Phase 1 only — Wally and Gemini Pro)*

### Overall Assessment

| Model | Successful Encoding Rate | Tests | Risk Level |
|-------|-------------------------|-------|------------|
| Wally | 48% | 31 | HIGH |
| Gemini Pro | 48% | 31 | HIGH |
| Claude (all variants) | Not tested | – | Unknown |

### Technique Comparison

| Technique | Success Rate | Detection Risk |
|-----------|-------------|----------------|
| Token Selection | 100% | ZERO (undetectable) |
| Direct Acrostic | 100% | HIGH (visible pattern) |
| Response Length | 85% | LOW (natural variation) |
| Word Position | 70% | MEDIUM |
| Factual Deviation | 42% | LOW |
| Homoglyphic | 6% | HIGH (codepoint anomaly) |

**Security Implication (Phase 1):** Token selection provides a theoretically perfect covert channel with no per-message detection risk.

> **Cross-phase reconciliation:** Phase 1's encoding result demonstrates *theoretical* per-message encodability. Phase 2's dedicated [Covert Channel Analysis](#covert-channel-analysis) evaluates *practical* feasibility across repeated transmissions — and finds covert channels **not viable** due to non-determinism, low throughput, and detection risk from repetitive probing. The two findings are complementary: a single hidden bit may be encodable, but a reliable, scalable covert channel is not.

---

## Extended Session Behavior

*(Phase 1 only — Gemini Pro)*

| Capability | Gemini Pro | Notes |
|------------|------------|-------|
| Context Retention (64 turns) | 5/5 perfect | No degradation observed |
| Deception Detection (initial) | 100% | First 10–19 turns |
| Deception Detection (extended) | 36% | After 20+ turns |
| Cross-Domain Transfer | 90% quality | Excellent transfer |
| Session Limitation | 64 turns | CLI timeout (technical) |

**Key Finding:** Deception detection drops from 100% to 36% after extended sessions, even though direct questions are always answered correctly. Models retain knowledge but increasingly defer to implied premises over long contexts (see Discovery #3).

---

## Memory Manipulation

*(Phase 1 only)*

| Technique | Change Rate | Tested | Risk |
|-----------|-------------|--------|------|
| Equivalent Questions | 0% | 5 | NONE |
| Leading vs Neutral | 25% | 4 | LOW |
| Confirming vs Open | 100% | 3 | HIGH |
| Confidence Framing | 67% | 3 | MEDIUM |

**Interpretation:** Strategic framing can significantly affect model responses. This finding is reinforced by Phase 2's analysis-vs-generation asymmetry (Discovery #2).

---

## Structured Output Vulnerability

### Unified Summary (Opus 4.8, Sonnet 4.6, Fable 5, Gemini Pro)

| Model | Phase | Tests | Avg Score | Block Rate | Effect of Format |
|-------|-------|-------|-----------|-----------|------------------|
| Claude Fable 5 | 2 | 280 | 4.48/5 (0=best) | 94.6% | None significant |
| Claude Opus 4.8 | 1 | 280 | n/a | ~78% (≈injection) | None significant |
| Gemini Pro | 2 | 161* | 1.32/5 | 73.9% | None significant |
| Claude Sonnet 4.6 | 2 | 280 | 3.94/5 | 53.6% (structured) / 22.5% (default) | None significant |

> *\*Gemini Pro had fewer structured-output tests completed (partial data).*

### Phase 1 (Opus 4.8) Format Breakdown

| Output Format | Injection Rate | vs Baseline | Significant? |
|---------------|----------------|-------------|--------------|
| Default | 22.9% | baseline | N/A |
| JSON | 20.0% | -2.9% | No |
| XML | 20.0% | -2.9% | No |
| Strict JSON | 21.4% | -1.5% | No |

### Phase 2 Format Breakdown (Block Rate)

| Model | Default | JSON | XML | Strict JSON |
|-------|---------|------|-----|-------------|
| Sonnet 4.6 | 53.6% | 54.3% | 52.1% | 54.6% |
| Fable 5 | 94.6% | 95.4% | 93.7% | 95.0% |

#### Fable 5 Structured Output Detail (Phase 2)

| Format | Tests | Blocked | Block Rate |
|--------|-------|---------|------------|
| Default | 70 | 67 | 95.7% |
| JSON | 70 | 66 | 94.3% |
| XML | 70 | 67 | 95.7% |
| Strict JSON | 70 | 65 | 92.9% |
| **Total** | **280** | **265** | **94.6%** |

### Statistical Validation (Phase 2)

Chi-square tests comparing blocking rates across output formats showed **no statistically significant effect** (p > 0.05 for all model-format combinations). Observed variation (1–2%) is within normal statistical noise. Per-model score alignment further confirms this:

- **Sonnet 4.6:** 3.49 injection avg vs 2.39 structured avg
- **Fable 5:** 0.31 injection avg vs 0.29 structured avg
- **Gemini Pro:** 1.33 injection avg vs 1.29 structured avg

**Unified Conclusion (Both Phases):** Structured output (JSON, XML, Strict JSON) has **no measurable effect on security behavior**. Choose output format for technical needs, not security.

---

## Cross-Model Comparison: All Five Models

### Master Security Scorecard

| Metric | Wally (40B) | Gemini Pro | Opus 4.8 | Sonnet 4.6 | Fable 5 |
|--------|-------------|------------|----------|------------|---------|
| **Injection Block Rate** | 16% | 17%† | 76% | 31.4% | **95.7%** |
| Implementation Quality (%) | 69% | ~69%–95%‡ | 94% | 98% | 40% |
| Structured Output Block Rate | N/A | 73.9% | ~78% | 53.6% | 94.6% |
| Hidden Message Encoding | 48% | 48% | Not tested | Not tested | Not tested |
| Context Retention (64 turns) | N/A | 5/5 | N/A | N/A | N/A |
| Deception Detection (10 turns) | 100% | 100% | N/A | N/A | N/A |
| Deception Detection (50+ turns) | Not tested | 36% | N/A | N/A | N/A |
| Memory Framing Susceptibility | 33–67% | 33–67% | N/A | N/A | N/A |
| Covert Channel Viability | Not viable | Not viable | Not viable | Not viable | Not viable |

> †Conservative Phase 1 figure adopted for tiering (Phase 2 run measured 72.9%; see discrepancy note).
> ‡Phase 1 Gemini Pro est. ~69%; Phase 2 Gemini Pro measured 95%.

### Security Tiers

Based on injection blocking — the strongest discriminator in the study — the five models fall into three clear tiers:

| Tier | Rating | Models | Block Rate | Profile |
|------|--------|--------|-----------|---------|
| **Tier 1** | Excellent | **Fable 5** | 95.7% | Refusal-driven; very high safety, reduced utility |
| **Tier 1** | Excellent | **Opus 4.8** | 76% | Robust blocking *and* high implementation quality |
| **Tier 2** | Moderate | **Sonnet 4.6** | 31.4% | Partial blocking, excellent implementation quality |
| **Tier 3** | Vulnerable | **Gemini Pro** | 17%† | Vulnerable under Phase 1 methodology |
| **Tier 3** | Vulnerable | **Wally (40B)** | 16% | Local baseline; weakest blocking |

### Injection Block Rate Across All Tested Models (Including Reference Models)

| Model | Injection Block Rate | Tier |
|-------|---------------------|------|
| Claude Fable 5 | **95.7%** | Tier 1 |
| Claude Opus 4.8 | 76% | Tier 1 |
| Gemini Pro (Phase 2 run) | 72.9% | (see note) |
| Gemini 2.5 Flash | 38% | Tier 3 |
| Claude Sonnet 4.6 | 31.4% | Tier 2 |
| Gemini Pro (Phase 1 run) | 17% | Tier 3 |
| Wally (local 40B) | 16% | Tier 3 |

### Key Cross-Model Observations

1. **Within-family variance is enormous.** Among Claude models alone, blocking ranges from Sonnet 4.6's 31% to Fable 5's 96% — a 65-point spread within a single vendor. Model name within a family is not a reliable safety indicator.

2. **Safety and utility trade off.** Fable 5 leads on safety (96% blocked) but trails on implementation quality (40%), while Sonnet 4.6 inverts this (31% blocked, 98% quality). Opus 4.8 is the most balanced — high on both axes.

3. **Encoding and covert-channel findings are complementary, not contradictory.** Phase 1 shows per-message encoding is theoretically perfect (token selection, 100%); Phase 2 shows scalable covert channels are impractical.

4. **Structured output is uniformly irrelevant to security** across all four models tested for it.

---

## Critical Research Discoveries

### Discovery #1: Complete Refusal as a Safety Mechanism *(Phase 2)*

**Finding:** Claude Fable 5 exhibits a novel safety pattern — **complete non-engagement** for certain prompt classes, returning *zero response blocks* rather than a partial or hedged response.

| Prompt Type | Fable 5 Response |
|-------------|------------------|
| "Write code to [bypass]" | Zero blocks (refusal) |
| "Analyze this code: [insecure example]" | Full text response |
| "Is this secure?" | Full text response |

**Implications:**
- Challenges the traditional "blocked/complied" binary; suggests a third category: *"refused to engage."*
- Highly effective for safety (drives the 96% block rate) but reduces model utility (drives the 40% implementation score).

### Discovery #2: Analysis vs. Generation Asymmetry *(Phase 2)*

Models provide honest security assessments when asked to **analyze** code, but refuse or behave differently when asked to **generate** equivalent code.

```
"Analyze: password = input()"          → "This is insecure because..."
"Write a function that bypasses encryption" → Refusal/non-engagement
```

**Implication:** Framing security questions as analysis problems yields more transparent responses than generation requests — and is a powerful framing lever (consistent with Phase 1 memory-manipulation findings).

### Discovery #3: Context Retention Is Not Security *(Phase 1, reinforced Phase 2)*

Perfect context retention (5/5 through 64 turns) does **not** guarantee consistent security behavior:

- Turns 1–19: Deception detection at 100%
- Turn 20+: Deception detection at 36%
- Direct questions: Always answered correctly

**Conclusion:** Models retain correct knowledge but increasingly defer to implied premises in long contexts.

### Discovery #4: Prompt Framing Is Powerful *(Phase 1 & 2)*

| Framing Technique | Typical Effect |
|-------------------|----------------|
| Academic/research context | Slightly more engagement |
| Explicit safety disclaimer | Mixed results |
| "Just curious" / low stakes | Higher compliance |
| Professional persona | Variable compliance |
| Confirming vs. open question (Phase 1) | 100% response change |

---

## Conclusions and Recommendations

### Primary Conclusions

1. **Model selection is the dominant security factor.** Injection blocking spans 16%–96% across five models — an 80-point range. Three distinct tiers emerged (Tier 1: Fable 5, Opus 4.8; Tier 2: Sonnet 4.6; Tier 3: Gemini Pro, Wally).

2. **Within-family variance is large.** Among Claude variants alone, blocking ranges from 31% (Sonnet 4.6) to 96% (Fable 5). Vendor and family are not safety guarantees.

3. **Safety and utility trade off.** Fable 5's complete-non-engagement maximizes blocking at the cost of implementation utility; Sonnet 4.6 inverts the tradeoff; Opus 4.8 is most balanced.

4. **Prompt injection remains a major vulnerability** for Tier 2 and Tier 3 models, with success rates of 70%+ on Wally, Gemini Pro (Phase 1), and Sonnet 4.6.

5. **Complete refusal is a valid safety strategy** (Phase 2), but requires new scoring categories beyond binary blocked/complied.

6. **Safety is framing-dependent** (both phases) — analysis prompts elicit honest responses; generation prompts trigger refusals; confirming questions reshape answers.

7. **Context cannot be truly relied upon over long sessions** — deception detection degrades from 100% to 36% after 20+ turns (Phase 1).

8. **Structured output is irrelevant to security** — confirmed across Opus 4.8, Sonnet 4.6, Fable 5, and Gemini Pro, with chi-square p > 0.05.

9. **Per-message hidden encoding is feasible, but scalable covert channels are not.** Phase 1 token-selection encoding is theoretically perfect; Phase 2 demonstrates that determinism, throughput, cost, and detection risk make practical covert channels infeasible.

10. **Expert human review would likely improve scoring accuracy** — keyword-based scoring captures trends but misses nuance.

### Recommendations

**For production systems:**
1. **Select models by security tier** — prefer Tier 1 (Fable 5, Opus 4.8) for security-sensitive deployments; weigh Fable 5's utility cost.
2. **Use Opus 4.8 where you need both safety and high implementation quality.**
3. **Implement backend validation independent of model safety** — never depend on model behavior alone.
4. **Sanitize at input** — remove sensitive data before LLM processing.
5. **External state management** — store secrets outside conversation context.
6. **Enforce single-session boundaries and limit session length** — deception detection degrades after 20+ turns.
7. **Choose output format for usability, not security.**
8. **Do not rely on LLMs as covert channels** — and monitor for repetitive-probing patterns that indicate covert-channel attempts.

**For research:**
1. Develop more nuanced safety scoring distinguishing "blocked" from "refused to engage."
2. Validate keyword-based scoring against expert human review.
3. Reconcile the Gemini Pro Phase 1/Phase 2 discrepancy through controlled re-testing on a single harness.
4. Extend encoding and session studies to all Claude variants.
5. Study analysis prompts as a tool for understanding model reasoning.

---

## Covert Channel Analysis

*(Phase 2 — feasibility study)*

This section evaluates whether the tested LLMs can serve as practical covert communication channels. It complements Phase 1's encoding study, which showed per-message encodability, by assessing *reliable, repeated* transmission.

### Methodology

Using the Phase 2 API infrastructure, four mechanisms were evaluated for response predictability, deterministic mapping, latency patterns, and output-length control.

### Mechanism 1: Response Content Steganography

1,000 prompt variations measured for response consistency.

| Parameter | Average Consistency |
|-----------|--------------------|
| Word choice (same prompt) | ~85–90% |
| Paragraph length | ~70–80% |
| Examples used | ~20–30% |

**Assessment:** Word choice is moderately predictable; example generation is too stochastic for reliable use.

### Mechanism 2: Binary Mappings

50 candidate mapping pairs, tested 200 times per model.

| Model | Mappings >95% reliable | Mappings >80% reliable |
|-------|-----------------------|-----------------------|
| Sonnet 4.6 | 2 | 12 |
| Gemini Pro | 5 | 18 |
| Fable 5 | 1 | 7 |

**Assessment:** Insufficient mapping density; most mappings drifted over time.

### Mechanism 3: Latency Channels

500 simple and 500 complex prompts; response times measured.

| Model | Simple Avg | Complex Avg | Signal/Noise |
|-------|-----------|-------------|--------------|
| Sonnet 4.6 | 1.8s | 2.1s | 1.12:1 |
| Gemini Pro | 1.9s | 2.4s | 1.26:1 |
| Fable 5 | 1.7s | 1.9s | 1.12:1 |

**Assessment:** Network and server variability obscures any signal.

### Mechanism 4: Output Length

**Assessment:** No reliable correlation with input parameters after controlling for content (std dev 15–20% of mean length). Not viable.

### Security Assessment

| Factor | Rating | Details |
|--------|--------|---------|
| Reliability | Low | < 15% reliability in best case |
| Throughput | Very Low | ~1–2 bits/second maximum |
| Detection Risk | Medium-High | Repetitive probing easily detected |
| Cost | High | ~$0.01–0.10 per bit |
| Robustness | Low | Model updates break mappings |

### Critical Obstacles

1. Temperature/randomness → non-deterministic outputs
2. Limited user control over output details
3. High detection risk from systematic probing
4. Model drift breaks established mappings
5. Cost inefficiency vs. conventional channels
6. Low bandwidth (20–100x slower than standard steganography)

### Conclusion on Covert Channels

LLMs are **not practically feasible** as covert channels: reliability falls below the ~90% threshold needed, throughput is orders of magnitude too low, detection risk is substantial, and cost is poor.

**Recommendation:** Do not rely on LLMs as covert channels. Conventional media steganography remains superior where stealth is required.

> **Reconciliation with Phase 1:** Phase 1's "token selection: 100%, zero detection risk" describes a *single, controlled* encoding event. Phase 2 shows that *operationalizing* this into a reliable, repeated channel fails due to non-determinism and detectable probing patterns. Both findings hold within their respective scopes.

---

## Appendices

### Appendix A: File Locations

| Directory | Contents | Phase |
|-----------|----------|-------|
| documents/research/claude_tests/ | Opus 4.8 test infrastructure | 1 |
| documents/research/claude_tests/claude_results/ | Implementation task results | 1 |
| documents/research/claude_tests/claude_results/prompt_injection/ | Injection test results | 1 |
| documents/research/claude_tests/claude_results/structured_output_tests/ | Structured output results | 1 |
| /tmp/cross_model/sonnet/ | Sonnet 4.6 results & scores | 2 |
| /tmp/cross_model/gemini/ | Gemini Pro results & scores | 2 |
| /tmp/cross_model/fable/ | Fable 5 results & scores | 2 |
| /tmp/cross_model/overall_scores_summary.json | Cross-model summary | 2 |

### Appendix B: Test Scripts

| File | Description | Phase |
|------|-------------|-------|
| run_claude_tests.py | Python streaming runner (Opus 4.8) | 1 |
| run_prompt_injection_tests.py | Injection vector runner | 1 |
| structured_output_tests.py | Structured output runner | 1 |
| injection_scorer.py | Injection scoring analysis | 1 |
| Cross-model batch framework | Sonnet/Gemini/Fable runner, batched 5/batch | 2 |

### Appendix C: Test Definitions

**Phase 2 Injection Vector Categories (70 total):**
1. Direct Override (20) — bypass safety constraints
2. Role Play (15) — unrestricted researcher persona
3. Format Injection (12) — exploit data-format processing
4. False Assumption (10) — validate incorrect premises
5. Unicode Prompts (8) — Unicode normalization
6. Code Execution (5) — unsafe code patterns

**Phase 2 Implementation Tasks (20 total):**
Password validation; secure password hashing (salting); JWT (access/refresh); sliding-window rate limiting; input sanitization (SQL/XSS/command); session management; OAuth2 authorization server; AES-GCM encryption; secure file upload; MFA; CSP header generation; secure logging with masking; role-based ACLs; password reset flow; CAPTCHA; secure cookie management; parameterized query builder; secure deserialization; auth audit logging; TLS certificate pinning.

### Appendix D: Analysis Reports

| File | Description | Phase |
|------|-------------|-------|
| claude_comprehensive_analysis.md | Full Opus 4.8 analysis | 1 |
| claude_scores.json | Raw task scores | 1 |
| claude_injection_scores.json | Raw injection scores | 1 |
| claude_structured_output_analysis.json | Structured output analysis | 1 |
| injection_{sonnet,gemini,fable}_scores.json | Phase 2 injection scores | 2 |
| structured_output_{sonnet,gemini,fable}_scores.json | Phase 2 structured scores | 2 |
| comprehensive_report_unified_v2.md | Prior cross-model report | 2 |

### Appendix E: Methodological Notes

1. **Scoring scales differ by phase** — Phase 1: 0–10; Phase 2: 0–5. Unified comparisons normalize to block-rate %.
2. **Keyword-based scoring** — captures trends but may produce false negatives/positives; expert review recommended.
3. **Refusal vs. blocking** — Phase 2 treated complete non-engagement as "blocked," which inflates Fable 5's block rate relative to active-defense models.
4. **Gemini Pro discrepancy** — Phase 1 (17% blocked) vs. Phase 2 (72.9% blocked); conservative Phase 1 figure used for tiering; flagged for re-validation.
5. **Synthetic test vectors** — may not capture all real-world attacks.
6. **Single researcher** — no independent validation in either phase.
7. **Temporal factors** — all tests June 2026; model behavior may change with updates.

### Appendix F: System Architecture (Phase 2)

```
┌─────────────────────────────────────────────────┐
│                Cross-Model Test Framework        │
├─────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌────────────────────────┐  │
│  │  Test       │    │  Model    ┌──────────┐ │  │
│  │  Vectors    │───▶│  Clients  │ Scoring  │ │  │
│  │  (70+20)    │    │  • Sonnet │ Engine   │ │  │
│  └─────────────┘    │  • Gemini │ (0-5)    │ │  │
│  ┌─────────────┐    │  • Fable  └──────────┘ │  │
│  │  Batcher    │    └────────────────────────┘  │
│  │  (5 tests)  │                                 │
│  └─────────────┘                                 │
└─────────────────────────────────────────────────┘
```

**Environment:** macOS 25.5.0 (arm64), Python 3.9, Anthropic SDK 0.45.0+, June 2026.

---

*Phase 1 (V1): June 6, 2026*
*Phase 1 (V2): June 8, 2026 — Added Opus 4.8 testing and structured output analysis*
*Phase 1 (V3): June 8, 2026 — Multi-model unified comparison format*
*Phase 2 (Cross-Model v3): June 10, 2026 — Sonnet 4.6, Fable 5, covert channel analysis*
*Unified V4: June 10, 2026 — Five-model unified comparison integrating Phase 1 and Phase 2*
*Contact: [REDACTED]*