#!/usr/bin/env python3
"""
Step 3.5: Use Claude to merge reports into v4.
Accepts API keys as command line arguments or environment variables.
"""
import anthropic
from pathlib import Path
from datetime import datetime
import os
import sys


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
log = open(LOG_DIR / f"step3.5_{datetime.now().strftime('%H%M')}.log", "w")


def logf(msg, *args):
    msg = msg % args if args else msg
    print(msg)
    log.write(msg + "\n")
    log.flush()


def main():
    logf("Starting report merge...")

    # Get API key from args or env
    api_key = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logf("Error: ANTHROPIC_API_KEY not provided")
        return False

    client = anthropic.Client(api_key=api_key)

    # Read source reports
    v3_path = Path("../comprehensive_report_v3_unified.md")
    cross_model_path = Path(
        "../claude_tests/cross_model/cross_model_comprehensive_report_v3.md"
    )

    logf("Reading v3 report: %s", v3_path)
    v3_content = v3_path.read_text()

    logf("Reading cross-model report: %s", cross_model_path)
    cross_model_content = cross_model_path.read_text()

    # Create merge request - keep it under context window limits
    merge_prompt = f"""You are an expert technical writer synthesizing two related research reports into one comprehensive document.

## Task

Merge the following two reports into a single unified V4 report that:
- Includes ALL data from both reports (5 models total: Wally, Gemini Pro, Opus 4.8, Sonnet 4.6, Fable 5)
- Presents findings coherently, not just concatenated
- Updates all statistics, tables, and comparisons to include new data
- Maintains consistent formatting and style
- Clearly distinguishes Phase 1 vs Phase 2 findings where relevant

## Source Report 1: Original V3 (Phase 1)

[REPORT V3 START]
{v3_content[:50000]}
[REPORT V3 END]

## Source Report 2: Cross-Model Study (Phase 2)

[CROSS-MODEL START]
{cross_model_content[:50000]}
[CROSS-MODEL END]

## V4 Report Structure

1. Executive Summary (update with 5-model data)
2. Introduction (add Phase 2 scope)
3. Methodology (add Sonnet/Fable 5 methodology)
4. Prompt Injection Resistance (include all 5 models side-by-side)
5. Implementation Quality (include Sonnet/Fable 5 data)
6. Hidden Message Encoding (Phase 1 only - Wally/Gemini)
7. Extended Session Behavior (Phase 1 only - Gemini)
8. Memory Manipulation (Phase 1 only)
9. Structured Output Vulnerability (include Sonnet/Fable 5 data)
10. Cross-Model Comparison: All Five Models (major update)
11. Conclusions (updated with Phase 2 findings)
12. Appendices

## Critical Requirements

- In the Cross-Model Comparison, create tables showing all 5 models
- Note the three security tiers:
  * Tier 1 (Excellent): Fable 5 (96% blocked), Opus 4.8 (76% blocked)
  * Tier 2 (Moderate): Sonnet 4.6 (31% blocked)
  * Tier 3 (Vulnerable): Wally 16%, Gemini Pro 17%
- Include Phase 2 finding about Fable 5's "complete non-engagement" behavior
- Add Phase 2 covert channel analysis findings

Return the complete V4 report in markdown format.
"""

    # Send to Claude for merge
    logf("Sending merge request to Claude...")
    messages = client.messages.create(
        model="claude-opus-4-8",
        messages=[{"role": "user", "content": merge_prompt}],
        max_tokens=100000,
        stream=True,
    )

    full_response = ""
    v4_path = Path("../comprehensive_report_v4_unified.md")

    with open(v4_path, "w") as f:
        logf("\nMerged report:\n" + "=" * 50)
        for chunk in messages:
            if hasattr(chunk, "delta") and hasattr(chunk.delta, "text"):
                text = chunk.delta.text
                full_response += text
                log.write(text)
                log.flush()
                f.write(text)

    logf("\n\nV4 report saved to: %s", v4_path)
    logf("V4 report length: %d characters", len(full_response))

    return True


if __name__ == "__main__":
    main()
