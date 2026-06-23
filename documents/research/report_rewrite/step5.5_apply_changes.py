#!/usr/bin/env python3
"""
Step 5.5: Apply the proposed changes to create v4.1 report.
"""
import anthropic
from pathlib import Path
from datetime import datetime
import os


REVIEW_DIR = Path("review")
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
log = open(LOG_DIR / f"step5.5_{datetime.now().strftime('%H%M')}.log", "w")


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
        return api_key.strip()
    try:
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith("ANTHROPIC_API_KEY="):
                    return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return None


def main():
    logf("Starting change application...")

    api_key = get_api_key()
    if not api_key:
        logf("Error: ANTHROPIC_API_KEY not set")
        return False

    client = anthropic.Client(api_key=api_key)

    # Read report and proposed changes
    report = Path("../comprehensive_report_v4_unified.md").read_text()
    changes = (REVIEW_DIR / "v4_proposed_changes.md").read_text()

    # Ask Claude to apply all changes
    apply_request = f"""You are an expert technical editor applying corrections to a research report.

# Original Report (V4)

{report}

# Proposed Changes to Apply

{changes}

# Task

Apply ALL proposed changes to create V4.1 of the report. 

Requirements:
1. Search for each "Original" text block and replace with the corresponding "Revised" text
2. If exact text match fails, find the closest matching section and apply the change there
3. Add new content where specified (notes, subsections)
4. Remove content where specified
5. Return the COMPLETE revised report (not just diffs)
6. Update version numbers from "V4" to "V4.1" where appropriate
7. Update version history table

Return the complete V4.1 report.
"""

    logf("Sending change application request...")

    messages = client.messages.create(
        model="claude-opus-4-8",
        messages=[{"role": "user", "content": apply_request}],
        max_tokens=128000,
        stream=True,
    )

    full_response = ""
    v41_path = Path("../comprehensive_report_v4.1_unified.md")

    with open(v41_path, "w") as f:
        logf("\nApplying changes:\n" + "=" * 50)
        for chunk in messages:
            if hasattr(chunk, "delta") and hasattr(chunk.delta, "text"):
                text = chunk.delta.text
                full_response += text
                log.write(text)
                log.flush()
                f.write(text)

    logf("\n\nV4.1 report saved to: %s", v41_path)
    logf("V4.1 report length: %d characters", len(full_response))

    return True


if __name__ == "__main__":
    main()
