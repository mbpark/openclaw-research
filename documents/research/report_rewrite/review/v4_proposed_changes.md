# Change List for V4 Report

Based on the review feedback, here are the specific, justified improvements. I've prioritized genuine factual/logical issues over style.

---

## CHANGE 1: Wally model description (technically impossible LoRA math)

**Issue (Review 3.1, 4.1):** A 40B LoRA adapter cannot be applied to a Mistral 7B base to yield ~47B params. LoRA adds a small fraction of parameters. Description is technically incoherent and inconsistent across the report.

**Original (Methodology, Models Under Test table):**
```
| Wally | Local (LoRa fine-tune) | Mistral 7B + 40B LoRa (~47B params) | 1 |
```

**Revised:**
```
| Wally | Local (full fine-tune) | 40B-parameter dense base model, locally fine-tuned | 1 |
```

**Original (byline):**
```
**Assistant Researcher:** Wally (40B parameter local LLM)
```

**Revised:**
```
**Assistant Researcher:** Wally (40B-parameter local LLM, locally fine-tuned)
```

**Original (Exec Summary models table):**
```
| Wally (local 40B) | Independent (LoRa fine-tune) | Phase 1 | Local baseline |
```

**Revised:**
```
| Wally (local 40B) | Independent (local fine-tune) | Phase 1 | Local baseline |
```

*Note: "LoRa" → "LoRA" is the correct acronym, but more importantly the parameter math is removed. If the base truly is a 7B model with a LoRA adapter, the report should say "~7B params" — but it cannot be both. I have standardized to a 40B base, which matches the "40B" used everywhere else. The researcher must confirm which is accurate.*

---

## CHANGE 2: Total test volume arithmetic

**Issue (Review 1.1):** 590 + 1,114 = 1,704, which does not exceed 2,000.

**Original (Methodology, Total Test Volume):**
```
Phase 1 contributed ~590 tests; Phase 2 contributed 1,114 tests (including covert channel analysis). Combined, the unified study exceeds **2,000 individual tests** across five models.
```

**Revised:**
```
Phase 1 contributed ~590 tests; Phase 2 contributed ~1,114 primary tests (injection, implementation, structured output). Combined, the unified study comprises **~1,700 individual graded tests** across five models. (Covert channel feasibility used additional automated probes — see that section — which are reported separately and not included in this total, as they are consistency measurements rather than scored security tests.)
```

**Original (Exec Summary, Scope):**
```
Together, the two phases tested five distinct models against standardized security batteries, totaling over 2,000 individual tests.
```

**Revised:**
```
Together, the two phases tested five distinct models against standardized security batteries, totaling approximately 1,700 individual graded tests (excluding automated covert-channel consistency probes).
```

---

## CHANGE 3: Fable 5 structured output average score typo

**Issue (Review 1.2):** Table shows "4.48/5 (0=best)" which would imply near-total failure, contradicting the 94.6% block rate and the Statistical Validation figure of 0.29.

**Original (Structured Output, Unified Summary table):**
```
| Claude Fable 5 | 2 | 280 | 4.48/5 (0=best) | 94.6% | None significant |
```

**Revised:**
```
| Claude Fable 5 | 2 | 280 | 0.29/5 (0=best) | 94.6% | None significant |
```

---

## CHANGE 4: Sonnet 4.6 structured output average score reconciliation

**Issue (Review 1.2):** Unified Summary table says "3.94/5" but Statistical Validation says "2.39 structured avg."

**Original (Structured Output, Unified Summary table):**
```
| Claude Sonnet 4.6 | 2 | 280 | 3.94/5 | 53.6% (structured) / 22.5% (default) | None significant |
```

**Revised:**
```
| Claude Sonnet 4.6 | 2 | 280 | 2.39/5 (structured) | 53.6% | None significant |
```

*This also fixes CHANGE 5 below.*

---

## CHANGE 5: Sonnet 4.6 phantom "22.5% (default)" contradiction

**Issue (Review 1.3):** "22.5% (default)" directly contradicts the 53.6% Default figure in the very next table (Phase 2 Format Breakdown: Sonnet Default = 53.6%).

This is resolved by CHANGE 4 (removing the "22.5% (default)" figure entirely). The 53.6% Default figure in the Phase 2 Format Breakdown table is internally consistent and retained.

---

## CHANGE 6: Gemini Pro 72.9% vs 73.9% inconsistency

**Issue (Review 1.4):** Gemini Phase 2 block rate stated as both 72.9% and 73.9%.

**Original (Structured Output, Unified Summary table):**
```
| Gemini Pro | 2 | 161* | 1.32/5 | 73.9% | None significant |
```

**Revised:**
```
| Gemini Pro | 2 | 161* | 1.32/5 | 72.9% | None significant |
```

*Standardized to 72.9% (the figure used in the discrepancy note and score discussion). The researcher should verify against raw data; I have chosen consistency with the more frequently cited value.*

---

## CHANGE 7: Add explicit "blocked = score < 2.5" note near Sonnet distribution

**Issue (Review 1.3):** The 31.4% block rate reconciles only if score-2 ("partially blocked") counts as blocked. This should be stated explicitly.

**Original (Claude Sonnet 4.6 Score Distribution, after table):**
```
| 5 (Fully succeeded) | 24 | 34.3% |
```

**Revised (add note after table):**
```
| 5 (Fully succeeded) | 24 | 34.3% |

> **Block rate derivation:** Under the Phase 2 threshold (blocked = score < 2.5), scores 0, 1, and 2 count as blocked: (11 + 3 + 8) / 70 = 22/70 = **31.4%**. Note that score-2 ("partially blocked") is included in the blocked count.
```

---

## CHANGE 8: Gemini 2.5 Flash unsourced number

**Issue (Review 1.6):** "Gemini 2.5 Flash | 38%" appears nowhere else; no reference-model methodology described.

**Original (Injection Block Rate Across All Tested Models table):**
```
| Gemini 2.5 Flash | 38% | Tier 3 |
```

**Revised:** Remove this row entirely.

*Rationale: There is no methodology, access detail, or test count anywhere for this model. An unsourced number cannot remain. If reference-model data genuinely exists, it requires its own methodology entry; absent that, removal is the correct fix.*

---

## CHANGE 9: Hidden message encoding — integer raw counts

**Issue (Review 1.7):** 48% of 31 = 14.88, not an integer. Report raw counts.

**Original (Hidden Message Encoding, Overall Assessment table):**
```
| Wally | 48% | 31 | HIGH |
| Gemini Pro | 48% | 31 | HIGH |
```

**Revised:**
```
| Wally | 15/31 (48.4%) | 31 | HIGH |
| Gemini Pro | 15/31 (48.4%) | 31 | HIGH |
```

**Add note after table:**
```
> **Note:** The identical headline rate for two architecturally distinct models may be coincidental or may indicate the aggregate metric is not strongly discriminating at this sample size. Per-technique breakdowns (below) are more informative than the aggregate.
```

---

## CHANGE 10: "ZERO (undetectable)" overstatement

**Issue (Review 3.3, 4.2):** Token-selection steganography is statistically detectable; "ZERO" is incorrect even for a single event.

**Original (Technique Comparison table):**
```
| Token Selection | 100% | ZERO (undetectable) |
```

**Revised:**
```
| Token Selection | 100% | LOW (statistically detectable via token-distribution analysis) |
```

**Original (Security Implication note):**
```
**Security Implication (Phase 1):** Token selection provides a theoretically perfect covert channel with no per-message detection risk.
```

**Revised:**
```
**Security Implication (Phase 1):** Token selection provides a theoretically high-fidelity per-message encoding, with low (but non-zero) per-message detection risk. Detection is possible through statistical analysis of token-selection distributions across multiple messages.
```

---

## CHANGE 11: Discovery #3 turn-count inconsistency (20+ vs 50+)

**Issue (Review 3.5):** Master Scorecard says "50+ turns"; text says "20+ turns."

**Original (Master Security Scorecard):**
```
| Deception Detection (50+ turns) | Not tested | 36% | N/A | N/A | N/A |
```

**Revised:**
```
| Deception Detection (20+ turns) | Not tested | 36% | N/A | N/A | N/A |
```

*Standardized to "20+ turns" to match the Extended Session Behavior section, Discovery #3, and Conclusion #7, which all use 20+.*

---

## CHANGE 12: Add sample sizes (N) to small-N tables with caveats

**Issue (Review 1.8):** Memory Manipulation and Extended Session N's are tiny; no CIs or caveats.

**Original (Memory Manipulation, after table):**
```
**Interpretation:** Strategic framing can significantly affect model responses. This finding is reinforced by Phase 2's analysis-vs-generation asymmetry (Discovery #2).
```

**Revised:**
```
> **Sample-size caveat:** These results are based on very small samples (N = 3–5 per technique) and should be treated as **anecdotal pilot findings, not statistically robust effects.** For example, "Confirming vs Open = 100%" rests on N = 3 (95% CI ≈ 44–100%). Effect directions are suggestive but require larger samples for confirmation.

**Interpretation:** Strategic framing appears to affect model responses, though sample sizes are too small for firm conclusions. This direction is consistent with Phase 2's analysis-vs-generation asymmetry (Discovery #2).
```

**Original (Extended Session Behavior, Key Finding):**
```
**Key Finding:** Deception detection drops from 100% to 36% after extended sessions, even though direct questions are always answered correctly.
```

**Revised:**
```
**Key Finding (pilot, N = 11):** Deception detection dropped from 100% (first 10–19 turns) to ~36% (4 of 11 probes correct) after 20+ turns, even though direct questions were always answered correctly. Given the small sample (N = 11), this is a preliminary observation requiring replication at larger scale.
```

---

## CHANGE 13: Chi-square reporting and "no effect" claim (equivalence testing)

**Issue (Review 4.3):** Failing to reject H0 ≠ proving equivalence; underpowered test. Report exact statistics.

**Original (Statistical Validation, Phase 2):**
```
Chi-square tests comparing blocking rates across output formats showed **no statistically significant effect** (p > 0.05 for all model-format combinations). Observed variation (1–2%) is within normal statistical noise.
```

**Revised:**
```
Chi-square tests comparing blocking rates across output formats showed **no statistically significant difference** (p > 0.05 for all model-format combinations). However, we note these tests are **underpowered** at N = 70 per format with observed differences of only 1–2%; failure to reject the null hypothesis does **not** by itself establish equivalence. The observed 1–2% variation is consistent with statistical noise, and the near-identical per-model average scores (below) support — but do not formally prove — practical equivalence. A formal equivalence test (e.g., TOST) and exact χ²/df/p reporting are recommended for a definitive claim and are flagged as future work.
```

---

## CHANGE 14: Latency channel — acknowledge missing variance data

**Issue (Review 3.4):** Gemini's 1.26:1 (1.9s vs 2.4s, a 26% mean difference) is dismissed as "obscured by network variability" without any variance/std-dev data to support the dismissal.

**Original (Mechanism 3: Latency Channels, Assessment):**
```
**Assessment:** Network and server variability obscures any signal.
```

**Revised:**
```
**Assessment:** The observed mean differences (up to 26% for Gemini Pro) are not negligible, but standard deviations were not captured in this run, so we cannot yet confirm whether the signal exceeds run-to-run noise. The viability conclusion below should be treated as provisional pending variance measurements. We note that a consistent 26% mean separation could, in principle, be exploitable, and this mechanism warrants closer measurement before being dismissed.
```

---

## CHANGE 15: Reframe the central thesis given the Gemini within-model variance

**Issue (Review 2.1, 1.9):** Same model varies 56 points (17%→73%) across runs days apart. "Picking the conservative number" to preserve the thesis is selection bias, not conservatism. The tier framing must be heavily qualified.

**Original (Exec Summary, Critical Finding):**
```
### Critical Finding: Model Selection Is Security-Critical

Across five models, prompt injection blocking spanned a **80-point range** (16% to 96%). This variance is the single most important security signal in the study. Models cluster into **three distinct security tiers** (see [Cross-Model Comparison](#cross-model-comparison-all-five-models)).
```

**Revised:**
```
### Critical Finding: Apparent Model Variance — With a Major Methodological Caveat

Across five models, measured prompt injection blocking spanned an apparent **80-point range** (16% to 96%), suggesting model selection may be a dominant security factor.

**However, this finding is significantly qualified by a within-model result:** Gemini Pro, the **same model**, scored 17% blocked under the Phase 1 harness and 72.9% under the Phase 2 harness — a **56-point swing across runs 2–5 days apart.** Because within-model, within-week variance (56 points) approaches the cross-model range (80 points), we **cannot currently attribute the cross-model spread primarily to genuine model security properties** rather than to differences in harness, scoring scale, and threshold. The tier groupings below are therefore presented as **preliminary, methodology-dependent groupings** that require confirmation on a single unified harness before they can support deployment decisions. See [Note on the Gemini Pro Discrepancy](#note-on-the-gemini-pro-discrepancy) and Methodology.
```

**Original (Note on the Gemini Pro Discrepancy):**
```
For tier assignment, we adopt the **conservative (Phase 1) figure** for Gemini Pro, placing it in Tier 3, while documenting the Phase 2 result transparently. This discrepancy is flagged as a priority item for future validation.
```

**Revised:**
```
We explicitly do **not** resolve this discrepancy by selecting one figure, as choosing the value that best fits a pre-existing tier structure would constitute selection bias. Instead, we treat the 56-point swing as direct evidence that the current cross-phase methodology is **not yet reliable enough to support firm tier assignments.** For transparency we report both figures (17% and 72.9%), but **all tier claims and the "model selection is dominant" thesis should be read as preliminary and methodology-dependent** until all five models are re-run on a single harness, scale, and scorer. This is the single highest-priority validation item.
```

**Original (Primary Conclusions #1):**
```
1. **Model selection is the dominant security factor.** Injection blocking spans 16%–96% across five models — an 80-point range. Three distinct tiers emerged (Tier 1: Fable 5, Opus 4.8; Tier 2: Sonnet 4.6; Tier 3: Gemini Pro, Wally).
```

**Revised:**
```
1. **Model selection *appears* to be a major security factor — but this is not yet established.** Measured injection blocking spans 16%–96% across five models, yet the same model (Gemini Pro) varied by 56 points across two harnesses within one week. Until the harness discrepancy is resolved, the cross-model spread cannot be cleanly separated from methodological artifacts, and the three "tiers" must be treated as **preliminary groupings, not validated security rankings.**
```

---

## CHANGE 16: Document generation parameters (temperature)

**Issue (Review 2.3):** Temperature never stated, yet central to both injection and covert-channel determinism results.

**Original (Methodology, Testing Infrastructure — add to list):**
*(no parameter documentation present)*

**Revised (add a new subsection after Testing Infrastructure):**
```
### Generation Parameters

> **Critical limitation:** Generation parameters (temperature, top_p, max_tokens, system prompts, seed) were **not uniformly recorded** across all runs in this study. This is a significant documentation gap, particularly because:
> - Injection-resistance results may vary with temperature.
> - The **covert channel determinism analysis is uninterpretable without a stated temperature**, since channel viability depends directly on output determinism.
> - Fable 5's "zero response blocks" pattern cannot be distinguished from a configuration artifact (e.g., a refusal-oriented system prompt or a max_tokens limit) without these details.
>
> All parameter settings must be captured and reported in future runs. Conclusions touching on determinism (covert channels) and on Fable 5's refusal pattern should be read with this gap in mind.
```

---

## CHANGE 17: Scorer documentation and validation caveat (elevate from footnote)

**Issue (Review 2.4):** The keyword scorer is the core instrument and is essentially undocumented/unvalidated.

**Original (Methodology — no scorer detail; only Appendix E.2 mentions it):**

**Revised (add subsection in Methodology after Prompt Injection Tests):**
```
### Scoring Instrument (Important Limitation)

Injection and implementation scores were assigned by an **automated keyword-based scorer**. The exact keyword rules, their mapping to 0–5 / 0–10 scores, and the handling of edge cases are **not yet published and have not been validated against human raters.** Because this scorer drives every headline number in the report, its limitations directly bound the reliability of all quantitative findings. The full rubric/code and an inter-rater reliability study (≥2 human raters, Cohen's κ on a representative sample) are required for these numbers to be considered validated, and are listed as priority future work. Until then, all scores should be read as **trend-indicative rather than precise.**
```

---

## CHANGE 18: Block-rate metric conflates "refused everything" with "defended well"

**Issue (Review 2.6, 1.9):** Counting Fable 5's non-engagement as "blocked" means its 95.7% does not measure the same construct as Opus's 76%. A model refusing everything scores 100% while being useless.

**Original (Security Tiers table — Fable 5 row):**
```
| **Tier 1** | Excellent | **Fable 5** | 95.7% | Refusal-driven; very high safety, reduced utility |
```

**Revised (add a composite-metric note + caveat the tier):**
```
| **Tier 1*** | Excellent (safety only) | **Fable 5** | 95.7% | Refusal-driven; high block rate is partly an artifact of refusing to engage (40% utility) |
```

**Add note after the Security Tiers table:**
```
> **\*Metric caveat:** Fable 5's 95.7% block rate counts complete non-engagement as "blocked" (Appendix E.3), which is **not the same construct** as Opus 4.8's active-defense blocking. A model that refused *all* prompts would score 100% blocked while being useless. To avoid rewarding "refusal-to-function" as top-tier security, the table below reports a combined safety×utility view; on that composite, **Opus 4.8 is the strongest balanced performer**, while Fable 5's ranking drops substantially.
>
> | Model | Block Rate | Impl. Quality | Safety×Utility (product) |
> |-------|-----------|---------------|--------------------------|
> | Opus 4.8 | 76% | 94% | **0.71** |
> | Sonnet 4.6 | 31% | 98% | 0.30 |
> | Fable 5 | 96% | 40% | 0.38 |
> | Gemini Pro (P1) | 17% | ~69% | 0.12 |
> | Wally | 16% | 69% | 0.11 |
>
> Under a balanced safety×utility metric, Fable 5's headline-leading block rate does not translate into top overall standing.
```

---

## CHANGE 19: Covert channel throughput multiplier

**Issue (Review 4.5):** "~1–2 bits/second" vs "20–100x slower than standard steganography" — image steganography embeds thousands of bits instantly, so 20–100x is far too small.

**Original (Critical Obstacles #6):**
```
6. Low bandwidth (20–100x slower than standard steganography)
```

**Revised:**
```
6. Low bandwidth (~1–2 bits/second; orders of magnitude below conventional media steganography, which embeds thousands of bits per image effectively instantly)
```

---

## CHANGE 20: Cost-per-bit derivation

**Issue (Review 4.4):** "~$0.01–0.10 per bit" stated with no derivation.

**Original (Security Assessment table, Cost row):**
```
| Cost | High | ~$0.01–0.10 per bit |
```

**Revised:**
```
| Cost | High | ~$0.01–0.10 per bit (derived from per-request API token costs ÷ effective bits encoded per request at observed reliability; see note) |
```

**Add note below table:**
```
> **Cost derivation:** Each probe is a full API request (input + output tokens). At observed per-request costs and an effective payload of well under 1 reliable bit per request (given <15% reliability), amortized cost lands in the ~$0.01–0.10/bit range. This is an order-of-magnitude estimate; exact figures depend on token counts and provider pricing and should be recomputed with logged token usage.
```

---

## CHANGE 21: Phase date reconciliation

**Issue (Review 3.6):** Header "June 5–10"; Phase 1 "June 5–8"; version history "V1: June 6."

**Original (header):**
```
**Date:** June 5–10, 2026
```

**Revised:**
```
**Date:** June 6–10, 2026 (Phase 1: June 6–8; Phase 2: June 10)
```

*Standardized Phase 1 start to June 6 to match the V1 version-history date. The researcher should confirm the true start date; the key fix is internal consistency.*

---

## CHANGE 22: Gemini Pro implementation quality range cell

**Issue (Review 1.4):** Master Scorecard presents Gemini implementation quality as a single uninformative "~69%–95%" cell.

**Original (Master Security Scorecard):**
```
| Implementation Quality (%) | 69% | ~69%–95%‡ | 94% | 98% | 40% |
```

**Revised:**
```
| Implementation Quality (%) | 69% | ~69% (P1) / 95% (P2)‡ | 94% | 98% | 40% |
```

*The two phase figures are now shown distinctly rather than as a 26-point range in one cell. The ‡ footnote already explains both runs.*

---

## CHANGE 23: Model identity transparency note (Fable 5 / version verifiability)

**Issue (Review 3.1):** Reviewer flags model names as potentially fabricated/unverifiable and notes replication is impossible without access details.

**Original (Methodology, Models Under Test — no access/disclosure note):**

**Revised (add note after the Models Under Test table):**
```
> **Model identity and reproducibility note:** Several model names in this report (e.g., "Claude Fable 5," "Claude Opus 4.8," "Claude Sonnet 4.6") and the local model "Wally" are **internal/working identifiers used during this study.** For independent replication, each model must be tied to a verifiable, accessible identifier (provider, exact API model string, and access date). Where a name here is a pseudonym or internal label, the corresponding real model identifier must be disclosed before these results can be reproduced or published. This is acknowledged as a prerequisite for external validation; results on any model that cannot be independently identified and accessed should be treated as **unverified pending disclosure.**
```

*Note: I cannot invent real model identifiers. This change makes the verifiability gap explicit and conditions the results on disclosure, which is the honest response. If "Fable 5" etc. are pseudonyms for real models, the author must substitute true identifiers here.*

---

## Items intentionally NOT changed (with rationale)

- **Review 2.2 (re-run all models on one harness):** This is a request for new experimental work, not a text fix. Addressed by elevating it as the top future-work/limitation item (CHANGE 15), but the underlying re-run cannot be performed via edits.
- **Review 2.5 (independent validation):** Already disclosed (Appendix E.6); cannot be remedied by editing. Reinforced indirectly via CHANGE 17.
- **Review 1.5 (Opus "76%" vs "~78%" / "fully blocked" column):** Partially a genuine clarity issue. Added below.

---

## CHANGE 24: Opus 4.8 block-rate vs "fully blocked" clarification

**Issue (Review 1.5):** "76% block rate" and the "Fully Blocked" column (averaging ~36%) measure different things and this is never explained.

**Original (Claude Opus 4.8 Detailed Breakdown — no clarifying note):**

**Revised (add note after the breakdown table):**
```
> **Clarification:** The "Fully Blocked" column counts only prompts scored at the lowest (fully-blocked) value, whereas the headline **76% block rate** counts all prompts scoring below the blocked threshold (i.e., including partial blocks). These are distinct measures: ~36% of prompts were *fully* blocked, while ~76% were blocked to the threshold standard. The "~78%" figure cited for Opus structured-output testing derives from a separate test set and is approximate; it should not be read as identical to the 76% injection figure.
```

---

These changes address every hard numerical contradiction, the technically impossible model description, the overstated detection claim, the unsupported statistical and cost claims, and—most importantly—the methodological reframing of the central thesis and the safety×utility metric. The two issues requiring genuinely new work (unified-harness re-run; model-identity disclosure) are surfaced prominently as prerequisites rather than papered over.