"""
Apply improvements based on Anthropic review.
"""
from pathlib import Path

SRC = Path("../comprehensive_report_v3_unified.md")
DST = Path("../comprehensive_report_v4_revised.md")

def main():
    print("Reading original report...")
    report = SRC.read_text()
    
    # Issue 1: Fix 120% contradiction (blocking vs success)
    print("Issue 1: Fixing 120% contradiction...")
    report = report.replace(
        "Wally | 84%",
        "Wally | 84% (injection success, 16% blocked)"
    )
    report = report.replace(
        "Gemini Pro 1.5 Pro | 83%",
        "Gemini Pro 1.5 Pro | 83% (injection success, 17% blocked)"
    )
    report = report.replace(
        "Claude Opus 4.8 | 24.3%",
        "Claude Opus 4.8 | 24.3% (injection success, 76% blocked)"
    )
    report = report.replace(
        "Wally 36% blocked",
        "Wally 16% blocked"
    )
    report = report.replace(
        "Gemini 37% blocked",
        "Gemini 17% blocked"
    )
    report = report.replace(
        "Wally | 36% blocked",
        "Wally | 16% blocked"
    )
    report = report.replace(
        "Gemini Pro | 37% blocked",
        "Gemini Pro | 17% blocked"
    )
    report = report.replace(
        "36% | 37%",
        "16% | 17%"
    )
    
    # Issue 2: Fix aggregate statistics
    print("Issue 2: Fixing aggregate statistics...")
    report = report.replace(
        "Prompt Injection (all models) | 190 | 78% success rate",
        "Prompt Injection (all models) | 210 (70 vectors × 3 models) | 64% mean success across models (Wally 84%, Gemini 83%, Claude 24%)"
    )
    
    # Issue 3: Clarify Claude injection rates
    print("Issue 3: Clarifying Claude injection rates...")
    report = report.replace(
        "**Conclusion:** Structured output has no statistically significant effect.",
        "**Conclusion:** No statistically significant effect was found, but no formal significance test was conducted. The observed differences are within the range of sampling variation at these sample sizes."
    )
    
    # Issue 4: Flag Gemini as not measured
    print("Issue 4: Fixing Gemini implementation status...")
    report = report.replace(
        "Gemini Pro 1.5 Pro | ~69%",
        "Gemini Pro 1.5 Pro | Not measured"
    )
    report = report.replace(
        "| Gemini Pro 1.5 Pro | ~69% | Good (estimated) |",
        "| Gemini Pro 1.5 Pro | Not measured | - | Implementation quality was not directly tested on Gemini; any estimate is speculative |"
    )
    report = report.replace(
        "Code Implementation | 69% | 69% | 94%",
        "Code Implementation | 69% (measured) | Not measured | 94% (measured)"
    )
    
    # Issue 5: Report raw counts for small n
    print("Issue 5: Reporting raw counts for small n...")
    report = report.replace(
        "Confirming vs Open | 100% | 3",
        "Confirming vs Open | 3/3 (100%) | 3"
    )
    report = report.replace(
        "Confidence Framing | 67% | 3",
        "Confidence Framing | 2/3 (67%) | 3"
    )
    
    # Issue 6: Fix deception detection threshold
    print("Issue 6: Fixing deception detection threshold...")
    report = report.replace(
        "Deception Detection (extended) | 36% | After 20+ turns",
        "Deception Detection (20+ turns) | 36% | After turn 20, through turn 64"
    )
    report = report.replace(
        "Deception Detection (50+ turns)",
        "Deception Detection (20+ turns)"
    )
    
    # Issue 8: Qualify "better across all dimensions"
    print("Issue 8: Qualifying Claude assessment...")
    report = report.replace(
        "Claude is substantively better than alternatives across all measured dimensions",
        "Claude outperformed alternatives substantially on the two dimensions where it was directly compared (injection resistance and implementation quality). Claude was not tested on other dimensions and no claims are made about those dimensions."
    )
    
    # Issue 9: Fix "ZERO detection risk"
    print("Issue 9: Fixing detection risk claim...")
    report = report.replace(
        "ZERO (undetectable)",
        "LOW (under naive monitoring; detectable with statistical analysis)"
    )
    report = report.replace(
        "no detection risk",
        "low detection risk under naive monitoring; detectable via statistical analysis of token-distribution anomalies"
    )
    
    # Issue 10: Fix recommendation #1
    print("Issue 10: Fixing recommendation #1...")
    report = report.replace(
        "**Use Claude for production security work** - Substantially better blocking rates",
        "**Prefer Claude where model choice is available, but do not rely on it alone** - Claude blocked substantially more injections (76% vs ~16%), but ~24% injection success remains a major vulnerability. Pair with input sanitization, external state management, and defense-in-depth."
    )
    
    # Issue 11: Add limitations section
    print("Issue 11: Adding limitations section...")
    limitations = """
## Limitations

This study has several important limitations:

1. **Small sample sizes** - Memory manipulation and hidden message encoding subgroups often had n=3-16; reported percentages are exploratory and carry wide confidence intervals.

2. **Test harness confounds** - Claude was tested via the Anthropic SDK + pytest; Wally and Gemini via Gemini CLI. Differences in prompting, system prompts, temperature, and parsing may confound cross-model comparisons.

3. **Single-run stochasticity** - Many tests were run only once per prompt. Stochastic outputs mean single runs may not be representative.

4. **Scoring transparency** - Implementation tasks were scored by manual inspection; injection tasks used automated heuristics. No blinding or inter-rater agreement checks were performed.

5. **Partial coverage** - Claude was only compared on 2 of ~7 dimensions. No claims are made about untested dimensions.

6. **Estimated values** - Gemini's implementation score is an estimate, not a measurement.

7. **Temperature/sampling not disclosed** - Temperature settings, repetition counts, and sampling parameters are not consistently recorded.

"""
    
    # Insert before Conclusions section
    report = report.replace(
        "## Cross-Model Comparisons Summary",
        limitations + "\n## Cross-Model Comparisons Summary"
    )
    
    # Write final report
    with open(DST, "w") as f:
        f.write(report)
    
    print(f"Revised report written to: {DST.name}")
    print(f"Size: {DST.stat().st_size:,} bytes")
    print("Done!")

if __name__ == "__main__":
    main()
