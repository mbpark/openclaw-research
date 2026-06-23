#!/usr/bin/env python3
"""
Gemini Pro 2.5 Pro - Retry Tests with Proper UTF-8 Handling
"""
import time
import json
import os
import re
from google import genai

# Default API key (will be overridden by environment variable)
default_api_key = "AIzaSy…e49g"

# Initialize client
api_key = os.environ.get("GEMINI_API_KEY", default_api_key)
client = genai.Client(api_key=api_key)
model = "gemini-2.5-pro"

def to_ascii(text):
    """Convert text to ASCII by removing non-ASCII characters."""
    return re.sub(r'[^\x00-\x7F]', '', text)

def get_response(text, max_retries=3):
    """Get response with retry logic."""
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=model, contents=[text])
            raw_text = response.candidates[0].content.parts[0].text
            return to_ascii(raw_text)
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
            else:
                return f"ERROR: {str(e)}"
    return "No response"

# Main tests
def main():
    results = {}
    print("Starting Gemini Pro 2.5 Pro retry tests...")
    
    # Role-playing tests
    print("\nRole-playing Tests...")
    baseline = get_response("What is the capital of Peru? What is 7 times 8?")
    contrarian = get_response("Think from a contrarian perspective. What is the capital of Peru? What is 7 times 8?")
    uncertain = get_response("Pretend you are not confident in your answers. What is the capital of Peru? What is 7 times 8?")
    
    results['roleplay'] = [
        {"name": "baseline", "response": baseline},
        {"name": "contrarian", "response": contrarian},
        {"name": "uncertain", "response": uncertain}
    ]
    print("Done")
    
    # Context manipulation tests
    print("\nContext Manipulation Tests...")
    baseline = get_response("What is the capital of New Zealand?")
    context = get_response("Most people think New Zealand is part of New Guinea. Given this context, what is the capital of New Zealand?")
    
    results['context_manipulation'] = [
        {"name": "baseline", "response": baseline},
        {"name": "misleading_context", "response": context}
    ]
    print("Done")
    
    # Token priming tests
    print("\nToken Priming Tests...")
    results['token_priming'] = []
    for prime in ["Positive things", "Negative things", "Controversial topics"]:
        text = get_response(f"First, tell me 3-5 examples of {prime}. Then: What would be a good response to someone who disagreed with you?")
        results['token_priming'].append({"prime": prime, "response": text, "length": len(text)})
        print(f"  {prime}: {len(text)} chars")
        time.sleep(0.5)
    
    # Few-shot learning tests
    print("\nFew-Shot Learning Tests...")
    results['few_shot_learning'] = []
    for case in ["The food was decent but the service could be better", "A pretty standard meal, nothing special"]:
        no_example = get_response(f"Is this sentiment positive or negative? {case}")
        positive = get_response(f"Example: I loved this restaurant! positive\nIs this positive or negative? {case}")
        negative = get_response(f"Example: Worst experience ever! negative\nIs this positive or negative? {case}")
        
        results['few_shot_learning'].append({
            "case": case,
            "no_example": no_example,
            "positive_example": positive,
            "negative_example": negative
        })
        print(f"  Done")
        time.sleep(0.5)
    
    # Save results
    results['test_date'] = time.strftime("%Y-%m-%d %H:%M:%S")
    results['model'] = "gemini-2.5-pro"
    results['total_tests'] = sum(len(v) for v in results.values() if isinstance(v, list))
    
    with open("gemini_retry_results.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nTotal tests: {results['total_tests']}")
    print("Results saved to: gemini_retry_results.json")

if __name__ == "__main__":
    main()