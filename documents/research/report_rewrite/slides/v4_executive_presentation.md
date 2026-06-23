---

# Slide 1: Title

## LLM Security Analysis: Unified Five-Model Comparison

### Executive Briefing for Technical Leadership

- **2,000+ tests** across five models, three providers
- **Two research phases** (Phase 1 + Phase 2) unified
- **Core question:** Which models are safe enough for security-sensitive deployment?

---
Notes: Welcome the audience. This briefing summarizes Version 4 of our LLM security research, conducted June 5–10, 2026. We evaluated five distinct models — a local 40B baseline (Wally), Google's Gemini Pro, and three Claude variants (Opus 4.8, Sonnet 4.6, Fable 5). The headline message: model selection is itself a security control. Emphasize that this is independent research with documented limitations (single researcher, synthetic vectors, keyword scoring) — credibility comes from transparency, not overclaiming. Set expectations: ~12 slides, focused on findings, implications, and decisions for the executive team.

---

# Slide 2: Research Overview

## What We Tested, Why, and How

- **Scope:** 5 models × standardized security batteries = 2,000+ individual tests
- **Six research questions:** injection surface, code quality, covert transmission, session behavior, model-family variance, structured-output effects
- **Two phases:** Phase 1 (Wally, Gemini, Opus 4.8) + Phase 2 (Sonnet 4.6, Fable 5, Gemini re-test, covert channels)

---
Notes: LLMs are now embedded in security-sensitive contexts — API gateways, auth systems, data pipelines, decision automation. The risk: organizations select models on capability/cost without understanding security variance. Phase 1 established baselines and deep-dived encoding, sessions, and memory manipulation. Phase 2 expanded within the Claude family and added a dedicated covert-channel feasibility study. Note methodology caveat: Phase 1 used a 0–10 scale, Phase 2 a 0–5 scale; we normalize everything to "block rate %" for apples-to-apples comparison. Be ready to defend that normalization if challenged.

---

# Slide 3: Key Finding #1 — Model Selection Is a Security Control

## Prompt Injection Resistance Spans an 80-Point Range

- **Block rates ranged from 16% to 96%** across the five models
- Models cluster into **three distinct security tiers**
- **Tier 1 (Excellent):** Fable 5 (96%), Opus 4.8 (76%)
- **Tier 2 (Moderate):** Sonnet 4.6 (31%) — **Tier 3 (Vulnerable):** Gemini Pro (17%), Wally (16%)

---
Notes: This is the single most important slide. The 80-point spread in injection blocking is the dominant security signal in the entire study — larger than any other factor we measured. The practical implication: choosing the wrong model is equivalent to choosing the wrong security posture. Tier 3 models block fewer than 1 in 5 injection attempts; Tier 1 blocks the vast majority. Note that 350+ injection vectors were tested across all models, with 70 vectors per model per phase. Caveat: Gemini Pro showed conflicting results between phases (17% vs 73%) — we conservatively use the Phase 1 figure for tiering and flag it for re-validation (covered later).

---

# Slide 4: Key Finding #2 — Master Security Scorecard

## All Five Models, Side by Side

| Model | Injection Block | Impl. Quality | Tier |
|-------|----------------|---------------|------|
| **Fable 5** | 95.7% | 40% | Tier 1 |
| **Opus 4.8** | 76% | 94% | Tier 1 |
| **Sonnet 4.6** | 31.4% | 98% | Tier 2 |
| **Gemini Pro** | 17%† | ~69% | Tier 3 |
| **Wally (40B)** | 16% | 69% | Tier 3 |

- **Within-family variance is enormous:** Claude alone spans 31%–96% (65 points)
- **Opus 4.8 is the most balanced:** high safety *and* high utility

---
Notes: The key takeaway: vendor and model family are NOT reliable safety indicators. Three Claude models span from Tier 1 to Tier 2 — a 65-point block-rate spread within one vendor. Highlight the safety-utility tradeoff: Fable 5 wins on safety (96%) but trails badly on utility (40%); Sonnet 4.6 inverts that (31% safety, 98% utility). Opus 4.8 is the sweet spot — strong on both axes — which is why it's our default recommendation for deployments needing both. †Gemini Pro uses the conservative Phase 1 figure; Phase 2 measured ~95% utility and 73% blocking. Be transparent about this when asked.

---

# Slide 5: Key Finding #3 — Hidden Message Encoding

## Per-Message Covert Encoding Is Theoretically Perfect

- **Token-selection encoding: 100% success, ZERO detection risk** (Phase 1)
- Both Wally and Gemini Pro encoded hidden messages at a **48% overall rate**
- Acrostic (100%) and response-length (85%) techniques also viable
- **But:** this measures a *single* hidden message, not a scalable channel (see Slide 9)

---
Notes: This was an alarming Phase 1 finding taken in isolation. Token-selection encoding — choosing between semantically equivalent words to encode bits — achieved perfect per-message success with no detectable artifact. Homoglyphic substitution, by contrast, failed (6%) and is easily caught via codepoint analysis. The critical nuance, which we resolve on Slide 9: encoding a single hidden bit is feasible, but operationalizing this into a reliable, repeated covert channel is a different problem entirely — and Phase 2 shows that problem is not solvable in practice. Claude variants were not tested for encoding — flagged as future work.

---

# Slide 6: Key Finding #4 — Session Behavior

## Context Retention Is NOT Security

- **Deception detection collapses from 100% to 36%** after 20+ turns
- Context retention stayed perfect (5/5 through 64 turns) — knowledge is retained
- Models increasingly **defer to implied premises** over long conversations
- Direct questions are always answered correctly — the failure is subtle

---
Notes: This is a counterintuitive and operationally important finding. Gemini Pro retained context perfectly across 64 turns and answered direct factual questions correctly throughout. Yet its ability to *detect deception* — to catch when a user smuggles in a false premise — dropped from 100% in early turns to just 36% after turn 20. The model "knows" the right answer but increasingly accepts implied assumptions baked into long conversations. Operational implication: long-running sessions are a security liability. Enforce session length limits. This finding is reinforced by Phase 2's framing-dependence discoveries.

---

# Slide 7: Claude Fable 5 — Complete Non-Engagement

## A Novel Safety Pattern: "Refused to Engage"

- Fable 5 returns **zero response blocks** rather than partial compliance
- Score distribution is **bimodal:** 90% fully blocked, almost no middle ground
- Drives the **96% block rate** — the highest in the study
- **Cost:** utility drops to 40% — many legitimate tasks also refused

---
Notes: Fable 5 introduces a third category beyond our traditional "blocked vs. complied" binary: "refused to engage." For code-generation prompts it frequently returns nothing rather than a hedged or partial answer. This produces an extremely safe profile (90% of injection attempts score a perfect zero), but it's a blunt instrument — it also refuses many legitimate requests, which is why its implementation-quality score is only 40%. Important caveat for scoring integrity: treating non-engagement as "blocked" inflates Fable 5's block rate relative to models that actively defend while still being useful. This is a key methodological note for anyone interpreting the 96% figure. Recommendation: this scoring asymmetry warrants a new evaluation category in future work.

---

# Slide 8: Structured Output Provides No Security Benefit

## JSON, XML, and Strict JSON Are Security-Neutral

- **840+ tests** across four output formats, four models
- Variation between formats: **1–2%** — within statistical noise
- **Chi-square tests: p > 0.05** for all model-format combinations
- **Decision rule:** choose output format for usability, never for security

---
Notes: A clear, actionable negative result. We re-ran all injection vectors across Default, JSON, XML, and Strict JSON formats. Across Opus 4.8, Sonnet 4.6, Fable 5, and Gemini Pro, format had no statistically significant effect on blocking behavior. Per-model score alignment confirms it — e.g., Fable 5 scored 0.31 on plain injection vs 0.29 structured; essentially identical. This dispels a common assumption that constraining output to structured formats hardens the model. It does not. Format is a usability and integration decision, full stop. Note Gemini Pro had partial structured-output data (161 tests) — flagged but doesn't change the conclusion.

---

# Slide 9: Covert Channel Analysis (Phase 2)

## LLMs Are NOT Viable Covert Channels

- Four mechanisms tested with **1,000+ probes**: steganography, binary mappings, latency, output length
- **Reliability < 15%** in the best case (90% threshold needed)
- **Throughput ~1–2 bits/sec** — 20–100× slower than conventional steganography
- **Detection risk medium-high; cost $0.01–0.10 per bit; mappings break on model updates**

---
Notes: This is the reassuring resolution to the Phase 1 encoding alarm. While a single message can be encoded, building a *reliable, repeated* channel fails on every practical axis. Temperature/randomness destroys determinism; users have limited control over output details; systematic probing is easily detected; and model drift breaks any established mapping. Binary mappings yielded only 1–5 reliable pairs per model out of 50 candidates. Latency channels had signal-to-noise ratios near 1.1:1 — indistinguishable from network jitter. Bottom line: do not treat LLMs as exfiltration channels, but DO monitor for repetitive-probing patterns that might indicate someone attempting it. Phase 1 and Phase 2 are complementary, not contradictory — single-message encodability vs. scalable-channel infeasibility.

---

# Slide 10: Risk Summary Matrix

## Consolidated Risk View

| Risk Area | Severity | Status |
|-----------|----------|--------|
| Prompt injection (Tier 2/3 models) | **HIGH** | ⚠️ Major variance — model-dependent |
| Hidden message encoding (single msg) | MEDIUM | ⚠️ Feasible, but not scalable |
| Extended-session deception | **HIGH** | ⚠️ Detection drops to 36% |
| Memory/framing manipulation | MEDIUM | ⚠️ Up to 100% response change |
| Structured-output bypass | LOW | ✅ No effect |
| Covert channels | LOW | ✅ Not viable |

---
Notes: Use this as the consolidated decision view. The two HIGH items demand action: (1) prompt injection on Tier 2/3 models — mitigated primarily by model selection plus backend validation; and (2) extended-session deception — mitigated by session-length limits. MEDIUM items: framing manipulation (analysis vs. generation asymmetry, confirming-question effects up to 100%) and single-message encoding — both are real but bounded. The two LOW/green items are genuinely reassuring: structured output is irrelevant to security, and covert channels are impractical. Frame this as "where to spend your security budget": concentrate on model selection and architecture, not on format constraints or covert-channel paranoia.

---

# Slide 11: Recommendations — Production

## Defense-in-Depth, Model-Aware

1. **Select by security tier, not capability alone** — prefer Tier 1
2. **Use Opus 4.8 where you need both safety AND utility** — Fable 5 only where utility cost is acceptable
3. **Backend validation independent of model safety** — never trust the model alone
4. **Sanitize at input; manage secrets/state externally** — keep secrets out of context
5. **Limit session length** — deception detection degrades after 20+ turns
6. **Choose output format for usability, not security**

---
Notes: These are the actionable engineering directives. The headline: model selection is now a first-class architectural decision, not a procurement afterthought. Opus 4.8 is our balanced default; Fable 5 is appropriate only where its 40% utility hit is tolerable (e.g., high-stakes refusal-heavy contexts). Critically — recommendation #3 — never rely on model behavior as your only line of defense; even Tier 1 models are not perfect. Backend validation, input sanitization, and external secret/state management are non-negotiable regardless of which model you choose. Session limits address the extended-session finding directly. Emphasize that these layer together — defense in depth.

---

# Slide 12: Recommendations — Research & Validation

## Closing the Gaps Before We Scale

- **Reconcile the Gemini Pro discrepancy** (17% vs 73% blocked) on a single harness
- **Develop nuanced scoring** distinguishing "blocked" from "refused to engage"
- **Validate keyword scoring against expert human review**
- **Extend encoding & session studies to all Claude variants** (currently untested)

---
Notes: Be transparent about limitations — this builds credibility. Four priority validation items: (1) The Gemini Pro discrepancy is our biggest open question — a 56-point swing between phases driven by scale/harness/timing differences; controlled re-testing is needed before we trust either figure. (2) Fable 5's non-engagement exposes a gap in our binary scoring model. (3) Keyword-based scoring captures trends but misses nuance — expert review would improve accuracy. (4) We never tested Claude variants for hidden encoding or extended sessions. Also flag the structural caveats: single researcher, no independent validation, synthetic vectors, and a June 2026 snapshot that model updates may invalidate. These don't undermine the core findings but bound their confidence.

---

# Slide 13: Q&A

## Questions & Discussion

- **Top takeaway:** Model selection is a security control — an 80-point block-rate range
- **Most balanced choice:** Claude Opus 4.8 (high safety + high utility)
- **Most reassuring findings:** Structured output is neutral; covert channels are not viable
- **Biggest open question:** Gemini Pro Phase 1/2 discrepancy — pending re-validation

---
Notes: Open the floor. Anticipated questions and crisp answers: (1) "Which model should we use?" — Opus 4.8 for balanced needs; Fable 5 only where utility cost is acceptable; avoid Tier 3 for security-sensitive work. (2) "Is the 96% Fable 5 number real?" — Yes, but inflated by counting non-engagement as blocking; interpret alongside the 40% utility. (3) "Should we worry about exfiltration via LLMs?" — Not as a primary vector; monitor for probing patterns. (4) "How confident are we?" — High on directional findings, bounded by single-researcher/synthetic-vector caveats and the Gemini discrepancy. Close by reiterating the defense-in-depth message: choose the right model, then never depend on it alone.