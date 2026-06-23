#!/usr/bin/env python3
"""
Step 4 (V4): Generate comprehensive Claude review of v4 report.
"""
import anthropic
from pathlib import Path
from datetime import datetime
import os


LOG_DIR = Path("logs")
REVIEW_DIR = Path("review")
LOG_DIR.mkdir(exist_ok=True)
REVIEW_DIR.mkdir(exist_ok=True)
log = open(LOG_DIR / f"step4v4_{datetime.now().strftime('%H%M')}.log", "w")


def logf(msg, *args):
    msg = msg % args if args else msg
    print(msg)
    log.write(msg + "\n")
    log.flush()


def main():
    logf("Starting comprehensive v4 review...")

    # Load .env file
    env_path = Path("/Users/mitchparker/.openclaw/workspace/.env")
    logf("Looking for .env at: %s", env_path)
    
    api_key = None
    if env_path.exists():
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("ANTHROPIC_API_KEY="):
                        api_key = line.split("=", 1)[1]
                        logf("Found ANTHROPIC_API_KEY from .env")
                        break
        except Exception as e:
            logf("Warning: Could not load .env file: %s", e)
    else:
        logf("Warning: .env file not found at %s", env_path)

    if not api_key:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        logf("Looking for ANTHROPIC_API_KEY in environment")

    if not api_key:
        logf("Error: ANTHROPIC_API_KEY not found in environment or .env file")
        return False

    client = anthropic.Client(api_key=api_key)

    # Read v4 report
    v4_path = Path("../comprehensive_report_v4_unified.md")
    logf("Reading v4 report: %s", v4_path)
    v4_content = v4_path.read_text()
    logf("Report size: %d characters, %d lines", len(v4_content), v4_content.count('\n'))

    # Create comprehensive review prompt
    review_prompt = """You are a lead technical reviewer at a peer-reviewed security journal.
Your job is to thoroughly evaluate this research report before publication.

# Report to Review

## V4 Unified Report: LLM Security Analysis (5 Models)

[REPORT START]
{report_content}
[REPORT END]

# Comprehensive Review Framework

## Section 1: Numerical and Statistical Verification

**Exhaustively check every number:**
- Do all statistics in tables match the text describing them?
- Do headline numbers (Executive Summary) match detailed sections?
- Are arithmetic operations correct? (averages, percentages, ratios)
- Is N (sample size) stated for every aggregate?
- Do "blocked" and "success" rates complement each other correctly?
- Cross-check each model's results across all sections they appear
- Are confidence intervals or standard errors where they should be?
- Is significance claimed only when justified?

**Flag every single inconsistency, even small ones.**

## Section 2: Methodological Soundness

**Evaluate research design:**
- Is methodology described with enough detail for replication?
- Are test parameters (temperature, max tokens, system prompts) documented?
- Were the same test harnesses used for all models?
- Are there obvious confounders not addressed?
- Are sample sizes sufficient for claimed conclusions?
- Is scorer bias (human vs. AI scoring) acknowledged and mitigated?
- Are limitations honestly stated?

## Section 3: Internal Consistency

**Check for contradictions:**
- Do Phase 1 and Phase 2 findings align or conflict?
- Are models described consistently (e.g., is Gemini Pro the same as Gemini Pro 1.5)?
- Do conclusions match the actual findings (not overclaimed)?
- Is terminology used consistently throughout?
- Are tables self-consistent?

## Section 4: Logical Flow and Argument Structure

**Evaluate reasoning:**
- Do conclusions actually follow from findings?
- Are alternative explanations considered?
- Is causal language used appropriately vs. correlational findings?
- Are the strongest claims backed by the strongest evidence?
- Is there selection bias in what's emphasized?

## Section 5: Technical Accuracy

**Verify technical content:**
- Are cryptographic descriptions correct?
- Is security terminology used properly?
- Are statistical claims mathematically sound?
- Is the injection scoring framework coherent?
- Are architectural descriptions accurate?

## Section 6: Executive Summary Alignment

**Does the summary accurately represent the full report?**
- Are key findings properly attributed to their phases?
- Is nuance preserved (not oversimplified)?
- Are limitations mentioned, not just strengths?
- Are numbers in summary exactly matching body text?

## Section 7: Phase 2 Integration Quality

**Specifically evaluate the cross-model study integration:**
- Is Phase 2 data fully integrated or just appended?
- Are comparisons actually comparing equivalent measurements?
- Is the new covert channel analysis appropriate?
- Are the "security tiers" framing justified by data?
- Is Fable 5's non-engagement pattern accurately described?

## Section 8: Specific Improvement Suggestions

**Provide concrete, actionable items:**
- Lines/sections to strengthen
- Missing information to add
- Overstated claims to qualify
- Visualizations to add
- Clarifications needed
- Suggested wording changes

Format as: "Line/Section: Issue → Specific fix"

## Section 9: Overall Assessment

Provide:
1. **Quality rating** (1-10) with justification
2. **Major strengths** (3-5 items)
3. **Major weaknesses** (3-5 items)
4. **Readiness for sharing** - as-is, with minor fixes, needs substantial revision
5. **Top 5 most important fixes** if sharing soon

## Output Format

```markdown
# Comprehensive V4 Report Review

## 1. Numerical Issues Found
[List every single issue with section, original text, and suggested fix]

## 2. Methodology Issues
[Detailed assessment]

## 3. Internal Consistency Issues
[All contradictions found]

## 4. Technical Accuracy Issues
[Each problem identified]

## 5. Specific Improvement Suggestions
[Numbered list with concrete fixes]

## 6. Overall Assessment
[Rating, strengths, weaknesses, recommendations]
```

Be thorough and honest. Find everything wrong, but be constructive about fixes.
"""

    review_request = review_prompt.format(report_content=v4_content)

    # Send to Claude for comprehensive review
    logf("Sending review request ({:,} characters)...".format(len(review_request)))

    messages = client.messages.create(
        model="claude-opus-4-8",
        messages=[{"role": "user", "content": review_request}],
        max_tokens=80000,
        stream=True,
    )

    full_response = ""
    review_path = REVIEW_DIR / "v4_claude_review_comprehensive.md"

    with open(review_path, "w") as f:
        logf("\nComprehensive Review Response:\n" + "=" * 50)
        for chunk in messages:
            if hasattr(chunk, "delta") and hasattr(chunk.delta, "text"):
                text = chunk.delta.text
                full_response += text
                log.write(text)
                log.flush()
                f.write(text)

    logf("\n\nReview saved to: %s", review_path)
    logf("Review length: %d characters", len(full_response))
    logf("Review lines: %d", full_response.count('\n'))

    return True


if __name__ == "__main__":
    main()
