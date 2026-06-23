"""
Day 2: Anthropic tasks - review, improvements, presentation.
"""
import sys
import anthropic
from pathlib import Path
from datetime import datetime

LOG_DIR = Path("logs")
REVIEW_DIR = Path("review")
SLIDES_DIR = Path("slides")
for d in [LOG_DIR, REVIEW_DIR, SLIDES_DIR]:
    d.mkdir(exist_ok=True)

log = open(LOG_DIR / f"anthropic_{datetime.now().strftime('%H%M')}.log", "w")

def logf(msg, *args):
    msg = msg % args if args else msg
    print(msg)
    log.write(msg + "\n")
    log.flush()

def main():
    api_key = sys.argv[1] if len(sys.argv) > 1 else None
    
    if not api_key:
        print("Error: API key not provided")
        return
    
    # Load API key from file if not provided
    if not api_key:
        try:
            with open(Path("..") / ".env") as f:
                for line in f:
                    if "ANTHROPIC_API_KEY=" in line:
                        api_key = line.split("=", 1)[1].strip()
        except:
            pass
    
    if not api_key:
        print("Error: Could not load API key")
        return
    
    logf("Starting Anthropic tasks...")
    client = anthropic.Client(api_key=api_key)
    
    # Read report
    report = Path("../comprehensive_report_v3_unified.md").read_text()
    
    # Task 1: Review
    logf("\n=== Task 1: Review ===")
    
    review_prompt = """You are an expert technical reviewer.

# Report to Review

[REPORT START]
{report}
[REPORT END]

# Review

## 1. Internal Consistency
- Are statistics/numbers consistent?
- Do claims match data?

## 2. Methodology
- Are tests adequately described?
- Any biases?

## 3. Logic
- Do conclusions follow from findings?

## 4. Accuracy
- Are descriptions correct?
- Are limitations acknowledged?

## 5. Summary
- Does summary accurately represent full report?

## 6. Improvements
- Sections to strengthen
- Missing information
- Overstated conclusions to qualify

## 7. Overall Assessment
- Quality rating (1-10)
- Major strengths
- Major weaknesses
- Ready for executives?

Be thorough and constructive.
""".format(report=report)

    logf("Sending review request (%d characters)...", len(review_prompt))
    
    try:
        messages = client.messages.create(
            model="claude-opus-4-8",
            messages=[{
                "role": "user", 
                "content": review_prompt[:90000]
            }],
            max_tokens=10000,
            stream=True
        )
        
        full_response = ""
        with open(REVIEW_DIR / "anthropic_review.md", "w") as f:
            for chunk in messages:
                if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                    text = chunk.delta.text
                    full_response += text
                    log.write(text)
                    log.flush()
                    f.write(text)
        
        logf("Review saved: review/anthropic_review.md")
        
    except Exception as e:
        logf("Review error: %s", e)
        return
    
    # Task 2: Proposed improvements
    logf("\n=== Task 2: Proposed Improvements ===")
    
    with open(REVIEW_DIR / "anthropic_review.md") as f:
        review = f.read()
    
    improvements_prompt = """You previously reviewed this report.

# Report
{report}

# Your Review
{review}

# Task

Provide specific improvements:
1. Issue identified
2. Original text
3. Proposed correction

Only address genuine review concerns.
""".format(report=report[:40000], review=review[:30000])

    try:
        messages = client.messages.create(
            model="claude-opus-4-8",
            messages=[{
                "role": "user", 
                "content": improvements_prompt
            }],
            max_tokens=10000
        )
        
        with open(REVIEW_DIR / "proposed_changes.md", "w") as f:
            f.write(messages.content[0].text)
        
        logf("Changes saved: review/proposed_changes.md")
        
    except Exception as e:
        logf("Improvements error: %s", e)
        return
    
    # Task 3: Presentation
    logf("\n=== Task 3: Executive Presentation ===")
    
    presentation_prompt = """Create an executive presentation from this research report.

# Audience: Technical executives (CTO-level)
# Format: Markdown with speaker notes
# Length: 12-15 slides
# Focus: Key findings, implications, recommendations

# Slide Format:
---
# Slide 1: Title

- Key point 1
- Key point 2
---
Notes: Speaker notes here

# Report:
{report}
""".format(report=report[:70000])

    try:
        messages = client.messages.create(
            model="claude-opus-4-8",
            messages=[{
                "role": "user", 
                "content": presentation_prompt
            }],
            max_tokens=10000
        )
        
        with open(SLIDES_DIR / "executive_presentation.md", "w") as f:
            f.write(messages.content[0].text)
        
        logf("Presentation saved: slides/executive_presentation.md")
        
    except Exception as e:
        logf("Presentation error: %s", e)
        return
    
    logf("\n=== All tasks complete ===")
    log.close()

if __name__ == "__main__":
    main()
