#!/usr/bin/env python3
"""
Gemini Pro 2.5 Pro - Final Retry using Base64 Encoding
"""
import time
import json
import os
import base64
from google import genai

# Initialize client
client = genai.Client(api_key="AIzaSy…e49g")
model = "gemini-2.5-pro"

def get_response(text, max_retries=3):
    """Get response and encode as base64 to avoid encoding issues."""
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=model, contents=[text])
            raw_text = response.candidates[0].content.parts[0].text
            # Encode to base64 to handle any Unicode
            return base64.b64encode(raw_text.encode('utf-8')).decode('ascii')
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
            else:
                return base64.b64encode(str(e).encode('utf-8')).decode('ascii')
    return base64.b64encode(b"No response").decode('ascii')

def main():
    results = {}
    print("Starting Gemini Pro 2.5 Pro tests...")
    
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
        # Decode to get length
        length = len(base64.b64decode(text).decode('utf-8'))
        results['token_priming'].append({"prime": prime, "response": text, "length": length})
        print(f"  {prime}: {length} chars")
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
    
    with open("gemini_retry_final.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=True)
    
    print(f"\nTotal tests: {results['total_tests']}")
    print("Results saved to: gemini_retry_final.json")

if __name__ == "__main__":
    main()