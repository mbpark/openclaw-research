#!/usr/bin/env python3
"""
Step 5 (V4): Fix report based on Claude review.
"""
import anthropic
from pathlib import Path
from datetime import datetime
import os


REVIEW_DIR = Path("review")
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
log = open(LOG_DIR / f"step5v4_{datetime.now().strftime('%H%M')}.log", "w")


def logf(msg, *args):
    msg = msg % args if args else msg
    print(msg)
    log.write(msg + "\n")
    log.flush()


def get_api_key():
    """Load API key from .env file."""
    env_path = Path("/Users/mitchparker/.openclaw/workspace/.env")
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return api_key
    try:
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith("ANTHROPIC_API_KEY="):
                    return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return None


def main():
    logf("Starting v4 remediation based on review...")

    api_key = get_api_key()
    if not api_key:
        logf("Error: ANTHROPIC_API_KEY not set")
        return False

    client = anthropic.Client(api_key=api_key)

    # Read report and review
    report = Path("../comprehensive_report_v4_unified.md").read_text()
    review = (REVIEW_DIR / "v4_claude_review_comprehensive.md").read_text()

    # Ask Claude for specific changes
    changes_request = """You previously reviewed this research report and provided detailed feedback.

# Report

[REPORT START]
{report}
[REPORT END]

# Review Feedback

[REVIEW START]
{review}
[REVIEW END]

# Task

Based on the review feedback, provide specific improvements:

1. List each issue identified and proposed fix
2. Show the original text that needs changing
3. Show the corrected/revised text

Be selective - only make improvements that genuinely address review concerns.
Don't change things for style preference.

Format response as a change list that can be applied to the report.
"""

    messages = client.messages.create(
        model="claude-opus-4-8",
        messages=[{
            "role": "user",
            "content": changes_request.format(
                report=report[:40000],
                review=review[:30000]
            )
        }],
        max_tokens=10000
    )

    # Save proposed changes
    changes_path = REVIEW_DIR / "v4_proposed_changes.md"
    with open(changes_path, "w") as f:
        f.write(messages.content[0].text)

    logf("Proposed changes saved to: %s", changes_path)
    logf("Changes length: %d characters", len(messages.content[0].text))

    return True


if __name__ == "__main__":
    main()
