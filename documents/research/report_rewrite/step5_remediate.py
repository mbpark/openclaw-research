#!/usr/bin/env python3
"""
Step 5: Fix report based on Anthropic review.
"""
import anthropic
from pathlib import Path
from datetime import datetime
import os

REVIEW_DIR = Path("review")
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
log = open(LOG_DIR / f"step5_{datetime.now().strftime('%H%M')}.log", "w")

def logf(msg, *args):
    msg = msg % args if args else msg
    print(msg)
    log.write(msg + "\n")
    log.flush()

def main():
    logf("Starting remediation based on review...")
    
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        logf("Error: ANTHROPIC_API_KEY not set")
        return False
    
    client = anthropic.Client(api_key=api_key)
    
    # Read report and review
    report = Path("../comprehensive_report_v3_unified.md").read_text()
    review = (REVIEW_DIR / "anthropic_review.md").read_text()
    
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
                report=report[:40000],  # Limit
                review=review[:30000]   # Limit
            )
        }],
        max_tokens=10000
    )
    
    # Save proposed changes
    with open(REVIEW_DIR / "proposed_changes.md", "w") as f:
        f.write(messages.content[0].text)
    
    logf("Proposed changes saved to: {}", REVIEW_DIR / "proposed_changes.md")
    logf("Changes length: {} characters".format(len(messages.content[0].text)))
    
    return True

if __name__ == "__main__":
    main()
