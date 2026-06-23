"""
Send report to Anthropic for review.
"""
import sys
import anthropic
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
LOG_DIR = Path("logs")
REVIEW_DIR = Path("review")
LOG_DIR.mkdir(exist_ok=True)
REVIEW_DIR.mkdir(exist_ok=True)

SRC = Path("../comprehensive_report_v3_unified.md")

log = open(LOG_DIR / f"step4_{datetime.now().strftime('%H%M')}.log", "w")

def logf(msg, *args):
    msg = msg % args if args else msg
    print(msg)
    log.write(msg + "\n")
    log.flush()

def main():
    logf("Starting Anthropic review...")
    
    if len(sys.argv) < 2:
        logf("Error: API key not provided")
        return
    
    api_key = sys.argv[1]
    client = anthropic.Client(api_key=api_key)
    
    # Read report
    report = SRC.read_text()
    
    # Create review prompt
    review_prompt = """You are an expert technical reviewer evaluating a security research report.

# Report to Review

The following is a comprehensive research report on LLM security:

[REPORT START]
{report}
[REPORT END]

# Review Task

Please conduct a critical review addressing:

## 1. Internal Consistency
- Are statistics/numbers consistent throughout?
- Do claims match the data presented?
- Are findings properly supported by evidence?

## 2. Methodology Soundness
- Are test methodologies adequately described?
- Are there obvious biases or confounders?
- Is sample size sufficient for conclusions?

## 3. Logical Flow
- Do conclusions follow from findings?
- Are alternative explanations considered?
- Is the argument structure coherent?

## 4. Technical Accuracy
- Are technical descriptions correct?
- Are limitations properly acknowledged?
- Is the math/statistics used correctly?

## 5. Executive Summary Alignment
- Does the summary accurately represent the full report?
- Are key findings properly highlighted?
- Are conclusions appropriately qualified?

## 6. Improvements Needed

List specific, actionable improvements:
- Sections to strengthen
- Missing information to add
- Overstated conclusions to qualify
- Additional data that would help
- Clarifications needed

## 7. Overall Assessment
- Overall quality rating (1-10)
- Major strengths
- Major weaknesses
- Should this be shared with executives as-is or revised first?

Be thorough, honest, and constructive. Flag genuine issues but don't nitpick.
"""

    review_request = review_prompt.format(report=report)
    
    # Send to Claude
    logf("Sending review request ({:,} characters)...".format(len(review_request)))
    
    try:
        messages = client.messages.create(
            model="claude-opus-4-8",
            messages=[{
                "role": "user", 
                "content": review_request[:90000]
            }],
            max_tokens=10000,
            stream=True
        )
        
        full_response = ""
        logf("\nReview response:\n" + "="*50)
        
        with open(REVIEW_DIR / "anthropic_review.md", "w") as f:
            for chunk in messages:
                if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                    text = chunk.delta.text
                    full_response += text
                    log.write(text)
                    log.flush()
                    f.write(text)
        
        logf("\n\nReview saved to: %s", REVIEW_DIR / "anthropic_review.md")
        logf("Review length: %d characters", len(full_response))
        
        return True
    except Exception as e:
        logf("Error during review: %s", e)
        return False

if __name__ == "__main__":
    main()
