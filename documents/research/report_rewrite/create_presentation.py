"""
Create executive presentation from research report.
"""
import subprocess
import anthropic
import sys
from pathlib import Path

# Load API key from environment
api_key = sys.argv[1] if len(sys.argv) > 1 else ""

if not api_key:
    print("Error: API key not provided")
    sys.exit(1)

client = anthropic.Client(api_key=api_key)

# Read report
report = Path("../comprehensive_report_v4_revised.md").read_text()

# Create presentation
print("Creating executive presentation...")
print(f"Report length: {len(report)} characters")

try:
    messages = client.messages.create(
        model="claude-opus-4-8",
        messages=[{
            "role": "user",
            "content": """You are a technical communications expert creating executive presentations.

# Task

Create an executive presentation deck based on this research report.

# Requirements

- Target audience: Technical executives (CTO-level)
- Format: Markdown with speaker notes
- Length: 12-15 slides maximum
- Focus: Key findings, implications, recommendations

# Slide Format

```
---

# Slide 1: Title

## Main Title Here

- Key point 1
- Key point 2

---
Notes: Extended speaker notes here. Include data points, caveats, and talking points.
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
        }],
        max_tokens=10000
    )
    
    # Save presentation
    with open(Path("slides") / "executive_presentation.md", "w") as f:
        f.write(messages.content[0].text)
    
    print("Presentation created successfully!")
    print(f"Length: {len(messages.content[0].text)} characters")
    
except Exception as e:
    print(f"Error: {e}")
    raise
