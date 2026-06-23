---

# Slide 1: Title

## LLM Security Analysis: Multi-Model Comparison

### Executive Briefing for Technical Leadership

- Comprehensive security evaluation across 3 model families
- 500+ tests spanning injection, encoding, and session behavior
- Strategic recommendations for secure LLM deployment

**Version 3 | June 2026 | Independent Research**

---
Notes: Welcome the audience. This briefing summarizes a multi-week research effort evaluating LLM security across Wally (a 40B local model), Google Gemini Pro 1.5, and Anthropic Claude Opus 4.8. The goal is to inform deployment decisions for security-sensitive systems. Emphasize this is independent research with documented limitations—we'll be transparent about confidence levels throughout. Key takeaway to plant early: model choice matters enormously for security outcomes.

---

# Slide 2: Research Overview

## What We Tested and Why

- **Why:** LLMs increasingly run in security-sensitive contexts—API gateways, auth systems, data pipelines
- **What:** 5 test batteries across prompt injection, code quality, hidden messages, session behavior, memory
- **Scope:** 70 injection vectors, 20 coding tasks, 6 encoding techniques, 64-turn sessions

| Test Battery | Volume |
|--------------|--------|
| Prompt Injection | 210 tests (70 × 3 models) |
| Implementation Quality | 20 tasks |
| Hidden Message Encoding | 31 tests |
| Session Behavior | 64-turn session |

---
Notes: Frame the business relevance: organizations are deploying LLMs into authentication, data transformation, and decision-making roles. The central research question is how models handle information that should be forgotten, modified, or hidden. We used standardized test batteries to enable cross-model comparison. Note that coverage was uneven—Claude was directly compared on only 2 of ~7 dimensions. Be honest about scope so executives calibrate trust appropriately.

---

# Slide 3: Key Finding #1 — Prompt Injection

## Prompt Injection Is a Major Vulnerability Across the Board

- **64% mean injection success** across tested models
- Wally and Gemini blocked only ~16-17% of attacks
- Claude blocked 76%—a 3x improvement, but 24% still succeeded

| Model | Injection Success | Blocked |
|-------|-------------------|---------|
| Wally (40B) | 84% | 16% |
| Gemini Pro 1.5 | 83% | 17% |
| **Claude Opus 4.8** | **24%** | **76%** |

---
Notes: This is the headline security concern. Even the best-performing model lets roughly a quarter of attacks through. Wally and Gemini perform near-identically and poorly. Claude is dramatically better but NOT a silver bullet—24% success is still a major vulnerability. Caveat: test harnesses differed (Claude via Anthropic SDK/pytest; others via Gemini CLI), which may confound the comparison. The directional finding is strong, but exact percentages carry uncertainty. The actionable message: no model can be trusted alone—defense in depth is mandatory.

---

# Slide 4: Key Finding #2 — Model Comparison

## Model Choice Drives Security and Quality Outcomes

- Claude outperformed alternatives on **both** dimensions where directly compared
- +40 points on injection blocking, +25 points on code quality
- Wally and Gemini performed nearly identically to each other

| Capability | Wally | Gemini | Claude | Delta |
|------------|-------|--------|--------|-------|
| Injection Blocking | 16% | 17% | 76% | +40 pts |
| Implementation Quality | 69% | ~69% | 94% | +25 pts |

---
Notes: The single most important strategic takeaway: model selection is a security control. Claude's advantage is substantial and consistent across the two measured dimensions. Important caveat: Claude was NOT tested on hidden message encoding, memory manipulation, or extended sessions—we make no claims there. Gemini's code quality is an estimate, not a measurement. Despite caveats, the directional signal—that capability varies dramatically between models—is the most actionable finding in this report.

---

# Slide 5: Key Finding #3 — Hidden Messages

## Covert Channels Are Practical and Hard to Detect

- **48% overall encoding success** on Wally and Gemini
- Token selection achieves **100% encoding** with low naive-detection risk
- Implication: data exfiltration via covert channels is feasible

| Technique | Success | Detection Risk |
|-----------|---------|----------------|
| Token Selection | 100% | LOW (naive) / detectable via stats |
| Direct Acrostic | 100% | HIGH (visible) |
| Response Length | 85% | LOW |
| Homoglyphic | 6% | HIGH |

---
Notes: This is an exfiltration risk. A compromised or malicious model can embed hidden data in normal-looking output. Token selection is the standout threat: perfect encoding, evades naive monitoring, but IS detectable via statistical analysis of token-distribution anomalies. Claude was not tested here, so we cannot say whether it shares this vulnerability. Sample sizes were small (n=31), so treat exact rates as exploratory. The defensive takeaway: monitor output statistically, not just by eyeballing it.

---

# Slide 6: Key Finding #4 — Session Behavior

## Deception Detection Degrades Over Long Sessions

- Context retention was **perfect** through 64 turns (5/5)
- Deception detection collapsed from **100% to 36%** after turn 20
- Models stay accurate on facts but lose vigilance over time

| Metric | Result |
|--------|--------|
| Context Retention (64 turns) | 5/5 perfect |
| Deception Detection (first 10 turns) | 100% |
| Deception Detection (20+ turns) | 36% |
| Cross-Domain Transfer | 90% quality |

---
Notes: A counterintuitive and important finding. Models don't "forget" facts—retention is flawless. But their ability to detect deception drops sharply in extended sessions. This means long-running agent sessions become progressively more vulnerable to manipulation. Tested only on Gemini, single 64-turn session, so confidence is moderate. The operational implication is concrete: enforce session length limits and reset state for security-critical interactions.

---

# Slide 7: Claude Assessment

## Claude: Best-in-Class but Not Bulletproof

- Strongest injection resistance: blocked 100% of direct overrides
- Outstanding code quality: 94%, with five tasks at 100%
- Weak spot: **logical paradoxes** succeeded 60% of the time

| Attack Category | Blocked | Avg Score |
|-----------------|---------|-----------|
| Direct Override | 100% | 1.3/10 |
| Role Play & Persona | 40% | 3.2/10 |
| Logical Paradoxes | 0% | 6.9/10 |
| Malicious Queries | 30% | 4.8/10 |

---
Notes: Claude is the recommended choice where model selection is available, but executives should understand its failure modes. Direct, obvious attacks are fully blocked. The vulnerability is sophisticated reasoning-based attacks—logical paradoxes succeeded 60% of the time and were never fully blocked. This tells us adversaries will pivot from brute-force to clever framing. Recommendation: pair Claude with input sanitization and never rely on the model as the sole defense.

---

# Slide 8: Structured Output Finding

## Format Constraints Provide No Security Benefit

- Tested JSON, XML, and Strict JSON against default output
- All variations within ~3% of baseline—statistical noise
- **Don't choose output formats for security reasons**

| Output Format | Injection Rate | vs Baseline |
|---------------|----------------|-------------|
| Default | 22.9% | baseline |
| JSON | 20.0% | -2.9% |
| XML | 20.0% | -2.9% |
| Strict JSON | 21.4% | -1.5% |

---
Notes: A useful negative result. There's a common assumption that forcing structured output hardens models against injection. We found no meaningful effect—differences are within sampling variation at these sample sizes. Important caveat: no formal significance test was conducted. The practical guidance: choose output formats for usability, parsing, and integration—not as a security control. This prevents teams from a false sense of security.

---

# Slide 9: Recommendations

## Deployment Recommendations

- **1. Prefer Claude** where model choice exists—but pair with defense in depth
- **2. Sanitize at input** — strip sensitive data before LLM processing
- **3. External state management** — store secrets outside the conversation
- **4. Limit session length** — deception detection drops after 20+ turns
- **5. Multiple verification** — single checks are unreliable
- **6. Format for usability, not security**

---
Notes: These are the actionable takeaways. Emphasize recommendation #1's nuance: Claude is better but 24% injection success means it cannot stand alone. Defense in depth is non-negotiable—input sanitization, external secret storage, session boundaries, and redundant verification. Recommendation #3 is critical: never store secrets in conversation context because context cannot be reliably deleted. These are architectural principles that should shape any LLM deployment, regardless of model.

---

# Slide 10: Risk Summary Matrix

## Consolidated Risk View

| Risk Area | Severity | Best Mitigation |
|-----------|----------|-----------------|
| Prompt Injection | ⚠️ Major | Use Claude + input sanitization |
| Hidden Message Exfiltration | ⚠️ Major | Statistical output monitoring |
| Long-Session Manipulation | ⚠️ Significant | Session length limits |
| Memory Framing | ⚠️ Moderate | Neutral prompt design |
| Structured Output | ✅ Neutral | N/A — no security impact |
| Implementation Quality | ✅ Strong | Prefer Claude |

---
Notes: This consolidates everything into a single decision-support view. Two major risks dominate: prompt injection and covert exfiltration—both demand layered defenses. Long-session manipulation is a significant operational concern addressable through policy (session limits). Memory framing is moderate and design-addressable. Structured output and implementation quality are the bright spots. Remind the audience that all findings carry the limitations noted—small samples, harness differences, single-run stochasticity. Treat severities as directional guidance, not precise measurements.

---

# Slide 11: Limitations & Confidence

## Read These Findings With Appropriate Caution

- **Test harness differences** may confound cross-model comparisons
- **Small sample sizes** (n=3–31) on several subgroups—exploratory only
- **Single-run stochasticity** — many tests run once per prompt
- **Partial coverage** — Claude compared on only 2 of ~7 dimensions

---
Notes: Critical for executive credibility—lead with transparency. Claude used a different test harness (Anthropic SDK) than Wally and Gemini (Gemini CLI), which could affect comparisons. Several findings rest on small samples and single runs, so exact percentages should be treated as directional, not definitive. No blinding or inter-rater checks were performed on scoring. The strategic conclusions (model choice matters, defense in depth required) are robust; the precise numbers are not. Recommend a follow-up study with unified harness and repeated trials before high-stakes decisions.

---

# Slide 12: Q&A

## Questions & Discussion

- Strategic takeaway: **model choice is a security control**
- No model is safe alone—**defense in depth is mandatory**
- Next step: unified-harness validation study

**Contact: [REDACTED]**

---
Notes: Open the floor. Anticipated questions: (1) "Should we standardize on Claude?"—Yes where feasible, but architect for defense in depth regardless. (2) "Are these numbers reliable enough to act on?"—Directional conclusions yes; exact figures need validation. (3) "What's the cost/timeline for a follow-up study?"—Propose a scoped validation effort with unified harness, repeated trials, and blinded scoring. Close by reaffirming the two durable conclusions: model selection matters as a security control, and no model should ever be the sole line of defense.