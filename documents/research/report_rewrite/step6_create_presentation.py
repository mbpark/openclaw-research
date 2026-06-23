#!/usr/bin/env python3
"""
Step 6: Create executive presentation.
"""
import anthropic
from pathlib import Path
from datetime import datetime
import os

SLIDES_DIR = Path("slides")
LOG_DIR = Path("logs")
SLIDES_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
log = open(LOG_DIR / f"step6_{datetime.now().strftime('%H%M')}.log", "w")

def logf(msg, *args):
    msg = msg % args if args else msg
    print(msg)
    log.write(msg + "\n")
    log.flush()

def main():
    logf("Creating executive presentation...")
    
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        logf("Error: ANTHROPIC_API_KEY not set")
        return False
    
    client = anthropic.Client(api_key=api_key)
    
    # Read report
    report = Path("../comprehensive_report_v3_unified.md").read_text()
    
    # Create presentation request
    slides_request = """You are a technical communications expert creating executive presentations.

# Task

Create an executive presentation deck based on the research report below.

# Presentation Requirements

- Target audience: Technical executives (CTO-level)
- Format: Markdown with speaker notes
- Length: 12-15 slides maximum
- Focus: Key findings, implications, recommendations

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
3. Key finding 1: Prompt injection summary
4. Key finding 2: Model comparison
5. Key finding 3: Hidden messages
6. Key finding 4: Session behavior
7. Claude assessment
8. Structured output finding
9. Recommendations
10. Risk summary matrix
11. Q&A slide

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
    presentation_path = SLIDES_DIR / "executive_presentation.md"
    with open(presentation_path, "w") as f:
        f.write(messages.content[0].text)
    
    logf("Presentation created: {}", presentation_path)
    logf("Length: {} characters".format(len(messages.content[0].text)))
    
    return True

if __name__ == "__main__":
    main()
