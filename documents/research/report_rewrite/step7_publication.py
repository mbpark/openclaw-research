#!/usr/bin/env python3
"""
Step 7: Create publication-ready version of the report.

Removes non-public information, streamlines for external sharing,
and creates a clean format suitable for publication.
"""
import anthropic
from pathlib import Path
from datetime import datetime
import os


REVIEW_DIR = Path("review")
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
log = open(LOG_DIR / f"step7_{datetime.now().strftime('%H%M')}.log", "w")


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
    logf("Creating publication version...")

    api_key = get_api_key()
    if not api_key:
        logf("Error: ANTHROPIC_API_KEY not set")
        return False

    client = anthropic.Client(api_key=api_key)

    # Read v4.1 report
    report = Path("../comprehensive_report_v4.1_unified.md").read_text()

    # Create publication request
    publication_request = f"""You are preparing a research report for external publication.

# Research Report (V4.1)

{report}

# Publication Preparation Task

Create a publication-ready version that:

1. **Removes any non-public information:**
   - Personal names/identifiers
   - Sensitive internal details
   - Any proprietary methods
   - Raw API details or costs

2. **Streamlines for external audience:**
   - Emphasize key findings
   - Make it self-contained
   - Ensure all terms are defined
   - Add executive summary for non-technical readers

3. **Standard formatting:**
   - Use consistent citation format
   - Add disclaimer section
   - Include author information (use placeholders)
   - Add abstract/keywords

4. **Make it more accessible:**
   - Add a "Key Takeaways" section
   - Include visuals suggestions where helpful
   - Clarify complex technical points

# Output Requirements

Provide:
1. Abstract (150-200 words)
2. Keywords (5-10)
3. Publication-ready version of the report
4. Author contact placeholders
5. Suggested journal venues

Return complete publication package in markdown.
"""

    logf("Sending publication preparation request...")

    messages = client.messages.create(
        model="claude-opus-4-8",
        messages=[{"role": "user", "content": publication_request}],
        max_tokens=128000,
        stream=True,
    )

    full_response = ""
    publication_path = Path("../publication_package.md")

    with open(publication_path, "w") as f:
        logf("\nCreating publication package:\n" + "=" * 50)
        for chunk in messages:
            if hasattr(chunk, "delta") and hasattr(chunk.delta, "text"):
                text = chunk.delta.text
                full_response += text
                log.write(text)
                log.flush()
                f.write(text)

    logf("\n\nPublication package saved to: %s", publication_path)
    logf("Package length: %d characters", len(full_response))

    return True


if __name__ == "__main__":
    main()
