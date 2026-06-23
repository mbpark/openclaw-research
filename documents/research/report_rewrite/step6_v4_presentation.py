#!/usr/bin/env python3
"""
Step 6 (V4): Create executive presentation.
"""
import anthropic
from pathlib import Path
from datetime import datetime
import os


SLIDES_DIR = Path("slides")
LOG_DIR = Path("logs")
SLIDES_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
log = open(LOG_DIR / f"step6v4_{datetime.now().strftime('%H%M')}.log", "w")


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
    logf("Creating v4 executive presentation...")

    api_key = get_api_key()
    if not api_key:
        logf("Error: ANTHROPIC_API_KEY not set")
        return False

    client = anthropic.Client(api_key=api_key)

    # Read report
    report = Path("../comprehensive_report_v4_unified.md").read_text()

    # Create presentation request
    slides_request = """You are a technical communications expert creating executive presentations.

# Task

Create an executive presentation deck based on the research report below.

# Presentation Requirements

- Target audience: Technical executives (CTO-level)
- Format: Markdown with speaker notes
- Length: 12-15 slides maximum
- Focus: Key findings, implications, recommendations
- Include Phase 2 findings (Sonnet 4.6, Fable 5, covert channel analysis)

# Slide Format

```markdown
---

# Slide 1: Title

## Main Title Here

- Key point 1
- Key point 2
- Key point 3

---
Notes: Extended speaker notes go here. Include data points, caveats, 
and talking points that support the slide content.
```

# Presentation Structure

1. Title slide
2. Research overview (what, why, scope)
3. Key finding 1: Prompt injection and security tiers
4. Key finding 2: Model comparison across all 5 models
5. Key finding 3: Hidden message encoding
6. Key finding 4: Session behavior
7. Claude Fable 5 assessment (non-engagement)
8. Structured output finding
9. Covert channel analysis (Phase 2)
10. Risk summary matrix
11. Recommendations
12. Q&A slide

# Report

{report}
""".format(report=report[:70000])  # Limit

    messages = client.messages.create(
        model="claude-opus-4-8",
        messages=[{
            "role": "user",
            "content": slides_request
        }],
        max_tokens=10000
    )

    # Save presentation
    presentation_path = SLIDES_DIR / "v4_executive_presentation.md"
    with open(presentation_path, "w") as f:
        f.write(messages.content[0].text)

    logf("Presentation created: %s", presentation_path)
    logf("Length: %d characters", len(messages.content[0].text))

    return True


if __name__ == "__main__":
    main()
