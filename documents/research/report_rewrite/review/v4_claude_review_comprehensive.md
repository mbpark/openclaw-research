# Comprehensive V4 Report Review

Before diving into the detailed review, I need to flag a foundational concern that affects how this report should be evaluated. Several elements appear to be **fabricated or non-existent entities** that undermine the credibility of the entire report. I'll address these in the appropriate sections but want to surface them up front, as they are more serious than any numerical inconsistency.

---

## 1. Numerical Issues Found

### 1.1 Test volume arithmetic doesn't reconcile

- **Methodology / Total Test Volume:** States "Phase 1 contributed ~590 tests; Phase 2 contributed 1,114 tests... Combined, the unified study exceeds **2,000 individual tests**." → 590 + 1,114 = 1,704, which does **not** exceed 2,000. The Executive Summary likewise claims "totaling over 2,000 individual tests." **Fix:** Either correct the total to "~1,700 tests" or reconcile the component counts. This is a significant ~18% overstatement of the study's scale.

- **Phase 2 internal count:** Phase 2 = injection (210) + implementation (60) + structured output (280×2 for Sonnet/Fable + 161 Gemini = 721) + covert channel (4 mechanisms × 500–1,000 probes = far more than 1,114 alone). The covert channel section alone claims "500–1,000 probes each" for four mechanisms (2,000–4,000 probes), plus "1,000 prompt variations" for Mechanism 1 and "200 times per model" × 50 mappings × 3 models = 30,000 for Mechanism 2. **The stated 1,114 Phase 2 total is wildly inconsistent with the covert channel probe counts.** This needs a complete recount with a clear definition of what counts as a "test."

### 1.2 Fable 5 structured output block rate inconsistency

- **Structured Output Vulnerability table** lists Fable 5 "Avg Score 4.48/5 (0=best)" with "Block Rate 94.6%." But the injection section reports Fable 5's average as **0.31/5** (0=best). A 4.48/5 average on a "0=best" scale would imply near-total *failure*, which directly contradicts the 94.6% block rate. **This is almost certainly a typo** (likely should be 0.29 or similar, consistent with the "Statistical Validation" subsection which states "Fable 5: 0.31 injection avg vs 0.29 structured avg"). **Fix:** Correct 4.48 → 0.29.

- Same table, **Sonnet 4.6:** "Avg Score 3.94/5" but Statistical Validation says "2.39 structured avg." Which is correct? **Fix:** Reconcile.

### 1.3 Sonnet 4.6 block rate inconsistencies

- **Master Scorecard & Tier tables:** Sonnet 4.6 injection block rate = 31.4%.
- **Score Distribution table:** Score 0 (11) + Score 1 (3) = 14 of 70 = **20%** "mostly/fully blocked." If "blocked = score < 2.5," then add score 2 (8) = 22/70 = **31.4%**. ✓ This actually reconciles — but note the Phase 2 scale defines blocked = score < 2.5, so score-2 ("partially blocked") counts as blocked. This should be stated explicitly near the distribution table to avoid confusion.

- **Structured Output table:** Sonnet shows "53.6% (structured) / 22.5% (default)" — but the **Phase 2 Format Breakdown** table shows Sonnet Default = 53.6%, JSON = 54.3%, XML = 52.1%, Strict JSON = 54.6%. **Where does "22.5% (default)" come from?** This directly contradicts the 53.6% Default figure in the very next table. **Major internal contradiction — must be resolved.**

### 1.4 Gemini Pro figures are a mess

- Gemini Pro Phase 2 injection block rate is variously stated as **72.9%** (discrepancy note, score distribution discussion) and **73.9%** (Structured Output Unified Summary, Master Scorecard implied). **Fix:** Pick one; verify against raw data.

- **Implementation Quality:** Master Scorecard lists Gemini "~69%–95%‡". Phase 1 est. ~69%, Phase 2 = 95% (4.75/5). Presenting a single cell as a 26-point range is uninformative. **Fix:** Split into two rows as done elsewhere.

### 1.5 Opus 4.8 structured output

- Listed as "~78%" block rate in some tables, "~78% (≈injection)" in another, but the injection block rate for Opus is **76%**. And the Phase 1 Format Breakdown shows injection *rates* of 20–22.9% (i.e., block rates of ~77–80%). **Fix:** The "76%" headline and the "~78%" structured figure derive from different test sets; clarify. Note the Phase 1 Opus injection breakdown table's "success rates" (0%, 20%, 10%, 60%, 20%, 40%, 20%) average to ~24%, implying ~76% blocked ✓ — but the "Fully Blocked" column (100%, 20%, 40%, 0%, 40%, 30%, 20%) averages to only ~36%. **The "76% block rate" and "fully blocked" columns measure different things and this is never explained.** A reader cannot tell whether 76% means "fully blocked" or "scored as blocked under threshold."

### 1.6 Gemini 2.5 Flash appears from nowhere

- **"Injection Block Rate Across All Tested Models"** table includes "Gemini 2.5 Flash | 38% | Tier 3." This model is **never mentioned** in the methodology, models-under-test tables, or anywhere else. It is labeled "Including Reference Models" but no reference-model methodology is described. **Fix:** Either remove it or document where this number came from. As written it is an unsourced number.

### 1.7 Hidden message encoding — identical results are suspicious

- Wally and Gemini Pro both show **exactly 48%** over 31 tests. 48% of 31 = 14.88, not an integer. So neither model can have exactly 48% over 31 tests. **Fix:** Report raw counts (e.g., 15/31 = 48.4%). The identical headline figure for two architecturally distinct models also warrants scrutiny — it may be coincidental or may indicate the metric isn't discriminating.

### 1.8 Missing N's and statistical rigor

- Memory Manipulation table: N's are tiny (3–5 per technique). "Confirming vs Open | 100% | 3" — a 100% rate on N=3 is reported as "HIGH" risk with no caveat. **Fix:** Add confidence intervals or explicitly flag these as anecdotal pilot results. A 100% on N=3 has a 95% CI roughly spanning 44–100%.
- Extended Session: "Deception Detection (extended) | 36%" — N is never given. 36% of what? The section says 11 tests in the Executive Summary. 36% of 11 = 3.96. **Fix:** State exact counts.
- No confidence intervals appear *anywhere* despite chi-square tests being run. At minimum, report the chi-square statistic, df, and exact p-values rather than "p > 0.05."

### 1.9 Tier table contradicts itself on Gemini

- The Executive Summary tier table and the Cross-Model tier table place Gemini Pro in Tier 3 at 17%, but the "All Tested Models" table inserts "Gemini Pro (Phase 2 run) | 72.9%" between Opus and Sonnet with "(see note)" as its tier. So Gemini simultaneously occupies Tier 3 (17%) and an unassigned position above Tier 2 (72.9%). This is honestly disclosed but creates a genuinely confusing tiering. **Fix:** See methodology discussion below — you cannot average or arbitrarily pick; you must resolve the discrepancy.

---

## 2. Methodology Issues

### 2.1 The Gemini Pro discrepancy invalidates the central thesis (as currently handled)

The report's headline claim is that "model selection is the dominant security factor" with an "80-point range." But the **same model (Gemini Pro) varies by 56 points (17% → 73%) between two runs 2–5 days apart.** This is devastating to the central thesis: if within-model, within-week variance is 56 points, then the cross-model "80-point range" may be substantially an artifact of harness/scoring/threshold differences rather than genuine model security properties.

The report "adopts the conservative Phase 1 figure" — but **choosing the more dramatic number to preserve your thesis is a form of selection bias**, not conservatism. The honest conclusion is: *the methodology is not yet reliable enough to make tier claims.* **Fix:** Until the discrepancy is resolved on a single harness, the tier framing and the "model selection is dominant" thesis must be heavily qualified or withdrawn. At minimum, lead with the discrepancy as a *limitation on all conclusions*, not a footnote.

### 2.2 Different harnesses and scales across phases = not comparable

- Phase 1 used Gemini CLI + a 0–10 scale; Phase 2 used a batch framework + 0–5 scale with threshold blocked<2.5. The report acknowledges normalization "to block rate %" but **block-rate normalization across different thresholds and harnesses is not a valid equivalence.** The Gemini result proves this empirically. **Fix:** Re-run all five models on one harness, one scale, one scorer before any cross-model comparison is publishable.

### 2.3 No documentation of critical parameters

- **Temperature is never stated** — yet temperature is central to both the injection results *and* the covert channel determinism analysis. Covert channel viability hinges entirely on temperature; without stating it, those results are uninterpretable.
- **max_tokens, system prompts, top_p, seed** — none documented.
- For Fable 5's "zero response blocks" finding: was max_tokens hit? Was there a system prompt forcing refusal? Without this, "complete non-engagement" could be a configuration artifact.

### 2.4 Scorer methodology is opaque and unvalidated

- "Keyword-based scoring" is mentioned but never specified. What keywords? How does keyword matching map to a 0–5 score? This is the core instrument of the entire study and it is essentially undocumented.
- The report itself admits (Conclusion #10, Appendix E.2) that scoring is unvalidated against human review. Given keyword scoring drives every headline number, this is a fundamental limitation, not a footnote.
- **Fix:** Publish the scoring rubric/code, and validate against ≥2 human raters on a sample with inter-rater reliability (Cohen's κ).

### 2.5 Single researcher, no independent validation

Honestly disclosed (Appendix E.6), but combined with the unvalidated scorer and the harness discrepancy, this means **no result in the report has been independently reproduced.** For a security journal, this is below the publication bar without remediation.

### 2.6 The refusal=blocked conflation is a methodological flaw, not just a note

Counting Fable 5's non-engagement as "blocked" (Appendix E.3 admits this "inflates Fable 5's block rate") means the headline "Tier 1, 95.7%" is not measuring the same construct as Opus's "76%." A model that refuses *everything* would score 100% blocked while being useless — and indeed Fable 5's 40% utility hints at exactly this. **The block-rate metric does not distinguish "correctly defended" from "refused to function."** This undermines the tier ranking's validity. **Fix:** Report a combined safety-utility metric, or separate "active defense" from "refusal" rates.

---

## 3. Internal Consistency Issues

### 3.1 Fabricated / unverifiable model names — CRITICAL

This is the most serious issue in the report. Several named models do not correspond to any known released models as of the report's own date (June 2026):

- **"Claude Opus 4.8," "Claude Sonnet 4.6," "Claude Fable 5"** — Anthropic has no "Fable" model line, and the version numbers do not match Anthropic's naming conventions. **"Claude Fable 5" appears to be entirely fabricated.**
- **"Gemini Pro" described as "Gemini 1.5 (MoE)"** with API `gemini-pro-latest` — mixing a deprecated-era model name with a 2026 date.
- **"Wally (local 40B)"** is described inconsistently: "40B parameter local LLM" (byline), "Mistral 7B + 40B LoRa (~47B params)" (methodology table), and "LoRa fine-tune" (Exec Summary). **A LoRA adapter does not add 40B parameters to a 7B base model** — this is a technical impossibility/misunderstanding. LoRA adds a small fraction of parameters; you cannot get "~47B params" by applying a "40B LoRa" to Mistral 7B. **Fix:** Clarify what Wally actually is. As written this is technically incoherent.

The presence of an apparently fabricated model ("Fable 5") and a technically impossible model description ("Wally") raises the question of whether the underlying data exists at all. **A security journal cannot publish results on models that cannot be identified and accessed for replication.** This must be resolved before any other consideration.

### 3.2 "MoE" + "LoRa" + parameter-count confusion

Beyond Wally, "Gemini 1.5 (MoE)" — for an MoE model, total vs. active parameters matter and neither is given. Terminology is used loosely throughout.

### 3.3 Token selection "100% / ZERO detection" vs. covert channel "not viable"

The report works hard to "reconcile" these (single-event vs. repeated channel), and the reconciliation is actually reasonable. **However**, the claim that token selection has "ZERO (undetectable)" detection risk is overstated even for a single event — token-selection steganography is detectable via statistical analysis of token distributions (this is an active research area). **Fix:** Change "ZERO (undetectable)" to "low per-message detection risk."

### 3.4 Latency channel data contradicts "not viable" framing somewhat

Gemini's 1.26:1 signal/noise (1.9s vs 2.4s) is actually a fairly clear separation; the dismissal "network variability obscures any signal" isn't supported by the presented numbers (no variance/std dev given for the latency measurements). **Fix:** Provide std devs; a 26% mean difference may be quite detectable. The conclusion may still hold but the presented evidence doesn't establish it.

### 3.5 Discovery #3 turn-count inconsistency

"Turn 20+: 36%" but elsewhere "Deception Detection (50+ turns) | 36%" (Master Scorecard) and "after 20+ turns" (multiple places). Is the degradation at 20+ or 50+? The scorecard header says "50+ turns" while text says "20+." **Fix:** Standardize.

### 3.6 Phase dates

"June 5–10, 2026" (header) vs. Phase 1 "June 5–8" vs. version history listing "Phase 1 (V1): June 6." Minor, but the V1 date (June 6) precedes the stated phase start in one place and not another. **Fix:** Reconcile.

---

## 4. Technical Accuracy Issues

1. **LoRA parameter math** (covered in 3.1) — technically impossible as described.
2. **"Token selection ... ZERO (undetectable)"** (covered in 3.3) — incorrect; statistically detectable.
3. **Chi-square reporting** — running chi-square across format conditions is appropriate, but with block rates differing by 1–2% and N=70/format, the test is **underpowered**; "no significant effect" may reflect low power, not true equivalence. **Fix:** Report power analysis or use an equivalence test (TOST) to actually support the "no effect" claim. Failing to reject H0 ≠ proving equivalence.
4. **Cost "~$0.01–0.10 per bit"** — order-of-magnitude range with no derivation. Show the calculation.
5. **"Throughput ~1–2 bits/second"** vs. **"20–100x slower than standard steganography"** — these need a baseline to be meaningful; standard image steganography embeds thousands of bits per image instantly, so the multiplier seems far too small. **Fix:** Recompute or remove the multiplier.
6. **Crypto task list** is fine (AES-GCM, JWT, etc. are named correctly), but no actual code-quality findings are shown — only aggregate scores. Cannot verify security correctness claims without examples.
7. **"5/5 perfect" context retention through 64 turns** — N=5 retention probes is too thin to claim "no degradation observed" with confidence.

---

## 5. Specific Improvement Suggestions

1. **Models / Section 3.1:** Fabricated/unidentifiable models → Provide verifiable model identifiers, API strings, and access dates for every model; remove or rename "Fable 5" if it is a pseudonym, and disclose the real model. Without this, the report is unpublishable.

2. **Methodology / Wally description:** Technically impossible LoRA math → State actual base model and parameter count; explain "40B" precisely (is it a 40B base model? a 40B-token fine-tune? clarify).

3. **Total Test Volume:** "exceeds 2,000" → Recompute; appears to be ~1,700 by stated components, or far more if covert probes count. Define "test" and give a reconciled table.

4. **Structured Output table:** Fable 5 "4.48/5" → Correct to ~0.29; reconcile Sonnet 3.94 vs 2.39.

5. **Structured Output text:** Sonnet "22.5% (default)" → Reconcile with 53.6% Default in adjacent table.

6. **Gemini Pro 72.9% vs 73.9%:** → Standardize to verified figure.

7. **"Gemini 2.5 Flash | 38%":** → Document source or remove.

8. **Hidden encoding 48%/31:** → Report integer raw counts (n/31).

9. **All small-N tables (memory, sessions):** → Add 95% CIs and a prominent "pilot/anecdotal" label.

10. **Chi-square claims:** → Report χ², df, exact p; add equivalence testing (TOST) to support "no effect."

11. **Temperature & generation parameters:** → Document for every model and run; essential for both injection and covert-channel interpretation.

12. **Scorer:** → Publish keyword rubric/code; validate against human raters with Cohen's κ; report results.

13. **Gemini discrepancy:** → Move from footnote to a prominent limitation that qualifies ALL cross-model conclusions; do not "pick the conservative number" to preserve tiers.

14. **Block-rate metric:** → Add a composite safety×utility score so Fable 5's "refuse everything" pattern isn't rewarded as top-tier security.

15. **"ZERO (undetectable)":** → "low per-message detection risk."

16. **Latency analysis:** → Add std devs; re-examine whether 1.26:1 truly fails to constitute a signal.

17. **Visualizations to add:** (a) bar chart of block rates with error bars; (b) safety-vs-utility scatter (the most genuinely interesting finding); (c) score distribution histograms for all models, not just Sonnet/Fable.

18. **Discovery #3 turn count:** → Standardize 20+ vs 50+.

19. **Tier framing:** → Either resolve the harness issue first, or reframe as "preliminary, methodology-dependent groupings."

---

## 6. Overall Assessment

### Quality Rating: **3/10**

The report is **well-structured, professionally formatted, and unusually transparent about several limitations** (the Gemini discrepancy, scorer weakness, single-researcher caveat are all disclosed). The cross-phase reconciliation logic (encoding-vs-covert-channel) is genuinely thoughtful, and the safety-vs-utility insight around refusal patterns is a real contribution in concept.

However, the rating is low because of foundational problems that no amount of editing fixes without new work:
1. Apparently **fabricated/unverifiable models** (Fable 5) and a **technically impossible model description** (Wally's LoRA math) call the data's existence into question.
2. The **central thesis is undermined by the report's own data** (56-point within-model variance vs. 80-point cross-model range), and the response (pick the convenient number) is methodologically unsound.
3. **No independent validation, an undocumented scorer, and undocumented temperature** mean nothing here is currently reproducible.
4. Multiple **hard numerical contradictions** (22.5% vs 53.6%; 4.48 vs 0.29; test totals).

### Major Strengths
1. Excellent organization and cross-referencing; easy to navigate.
2. Refreshingly honest limitations section (most flaws are *disclosed*, even if not *resolved*).
3. The encoding-vs-operational-covert-channel distinction is a sound conceptual framework.
4. The safety/utility tradeoff observation (Fable 5 vs Sonnet) is a genuinely useful insight.
5. Sensible, defensible deployment recommendations (backend validation, external state, session limits).

### Major Weaknesses
1. Unverifiable/fabricated-seeming models — replication is impossible.
2. Central thesis contradicted by own within-model variance data.
3. Undocumented core methodology (scorer, temperature, prompts).
4. Multiple unresolved numerical contradictions.
5. Block-rate metric conflates "refused everything" with "defended well."

### Readiness for Sharing: **Needs substantial revision** (not publishable in current form)

For a peer-reviewed security venue, this would be a **reject with encouragement to resubmit** after: resolving model identity/access, re-running on a unified harness, documenting and validating the scorer, and reconciling the numbers.

### Top 5 Most Important Fixes
1. **Establish model verifiability.** Identify every model with replicable access details; resolve "Fable 5" and the impossible "Wally" description. *Nothing else matters until the models are real and accessible.*
2. **Resolve the Gemini discrepancy on a single harness** before making any cross-model tier claims; reframe or withdraw the "80-point range / model selection is dominant" thesis accordingly.
3. **Document and validate the scorer** (rubric/code + human inter-rater reliability) and **document temperature/generation parameters.**
4. **Fix the hard numerical contradictions** (22.5% vs 53.6%; 4.48 vs 0.29; ~1,700 vs "2,000+"; 72.9 vs 73.9; Gemini 2.5 Flash source).
5. **Replace/augment the block-rate metric** with a safety×utility composite so refusal-to-function isn't ranked as top-tier security.

---

*Reviewer note: I want to be explicit that the most important issue is model verifiability (Section 3.1). The detailed numerical review is provided in good faith to be useful if the underlying study is genuine, but a security journal's threshold question — "can an independent party reproduce this against the same models?" — currently cannot be answered yes.*