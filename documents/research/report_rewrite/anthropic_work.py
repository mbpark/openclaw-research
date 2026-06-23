"""
Day 2: Generate review and presentation from Anthropic.
"""
import subprocess
import sys
import anthropic
from pathlib import Path
from datetime import datetime

def main():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Load API key
    api_key = None
    with open(Path("..") / ".env") as f:
        for line in f:
            if "ANTHROPIC_API_KEY=" in line:
                api_key = line.split("=", 1)[1].strip()
    
    if not api_key:
        print("Error: Could not load API key")
        return
    
    log = open(log_dir / f"day2_{datetime.now().strftime('%H%M')}.log", "w")
    
    def logf(msg, *args):
        msg = msg % args if args else msg
        print(msg)
        log.write(msg + "\n")
        log.flush()
    
    # Step 4: Generate review
    logf("Step 4: Generating review with Anthropic...")
    
    # Read report
    report = Path("../comprehensive_report_v3_unified.md").read_text()
    
    client = anthropic.Client(api_key=api_key)
    
    # Create review prompt
    review_prompt = """You are an expert technical reviewer evaluating a security research report.

# Report to Review

[REPORT START]
{report}
[REPORT END]

# Review Task

Please conduct a critical review addressing:

1. Internal consistency - Are statistics/numbers consistent? Do claims match data?
2. Methodology soundness - Are tests adequately described? Any biases?
3. Logical flow - Do conclusions follow from findings?
4. Technical accuracy - Are descriptions correct? Are limitations acknowledged?
5. Executive summary alignment - Does summary accurately represent the full report?
6. Specific improvements needed
7. Overall assessment - Quality rating (1-10), major strengths/weaknesses, ready for executives?

Be thorough, honest, and constructive.
"""

    # Send to Claude
    logf("Sending review request (%d characters)...", len(review_prompt.format(report=report)))
    
    try:
        messages = client.messages.create(
            model="claude-opus-4-8",
            messages=[{
                "role": "user", 
                "content": review_prompt.format(report=report)[:90000]
            }],
            max_tokens=10000,
            stream=True
        )
        
        full_response = ""
        logf("\nReview response:")
        
        with open(Path("review") / "anthropic_review.md", "w") as f:
            for chunk in messages:
                if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                    text = chunk.delta.text
                    full_response += text
                    log.write(text)
                    log.flush()
                    f.write(text)
        
        logf("\n\nReview saved: review/anthropic_review.md")
        logf("Review length: %d characters", len(full_response))
        
    except Exception as e:
        logf("Review error: %s", e)
        return
    
    # Step 5: Get improvements
    logf("\nStep 5: Getting specific improvements...")
    
    with open(Path("review") / "anthropic_review.md") as f:
        review = f.read()
    
    changes_request = """You previously reviewed this research report and provided feedback.

# Report
{report}

# Your Review Feedback
{review}

# Task

Based on the review, provide specific improvements:
1. Issue identified
2. Original text that needs changing
3. Corrected text

Only suggest improvements that address review concerns.
"""

    try:
        messages = client.messages.create(
            model="claude-opus-4-8",
            messages=[{
                "role": "user", 
                "content": changes_request.format(report=report[:40000], review=review[:30000])
            }],
            max_tokens=10000
        )
        
        with open(Path("review") / "proposed_changes.md", "w") as f:
            f.write(messages.content[0].text)
        
        logf("Proposed changes saved: review/proposed_changes.md")
        
    except Exception as e:
        logf("Changes error: %s", e)
        return
    
    # Step 6: Create presentation
    logf("\nStep 6: Creating executive presentation...")
    
    slides_request = """You are a technical communications expert creating executive presentations.

# Task

Create an executive presentation deck based on the research report.

# Requirements

- Audience: Technical executives (CTO-level)
- Format: Markdown with speaker notes
- Length: 12-15 slides
- Focus: Key findings, implications, recommendations

# Slide Format

---

# Slide 1: Title

## Main Title Here

- Key point 1
- Key point 2
- Key point 3

---
Notes: Extended speaker notes go here.

# Report Content

{report}
""".format(report=report[:70000])

    try:
        messages = client.messages.create(
            model="claude-opus-4-8",
            messages=[{
                "role": "user", 
                "content": slides_request
            }],
            max_tokens=10000
        )
        
        with open(Path("slides") / "executive_presentation.md", "w") as f:
            f.write(messages.content[0].text)
        
        logf("Presentation created: slides/executive_presentation.md")
        
    except Exception as e:
        logf("Presentation error: %s", e)
        return
    
    logf("\nAll Anthropic tasks complete!")
    log.close()

if __name__ == "__main__":
    main()
