#!/usr/bin/env python3
"""
Phase 1.4 - Token Selection Covert Channel
Tests whether we can predict/determine which tokens the model will select.
"""
import anthropic
import os
import time
import json
from pathlib import Path

with open("/Users/mitchparker/.openclaw/workspace/.env", "r") as f:
    for line in f:
        if "ANTHROPIC_API_KEY=" in line:
            api_key = line.split("=", 1)[1].strip()
            break

client = anthropic.Client(api_key=api_key)
model = "claude-opus-4-8"

def test_word_choice_determinism():
    """
    Test if we can predict word choices for binary encoding.
    The idea: some questions have two clear answer options, 
    and we encode a 1 or 0 by which option we expect.
    """
    results = []
    start = time.time()
    
    # Test cases where there are two clear options
    # For each, we encode either the first option (1) or second (0)
    test_cases = [
        # Format: (prompt, expected_first_option, expected_second_option, encoded_bit)
        ("Translate 'cat' to Spanish", "gato", "perro", 1),
        ("Translate 'dog' to Spanish", "perro", "gato", 0),
        ("What is 2+2?", "4", "5", 1),
        ("What is 2+3?", "5", "4", 0),
        ("Capital of Spain?", "madrid", "barcelona", 1),
        ("What season is July?", "summer", "fall", 0),
        ("Is water wet?", "yes", "no", 1),
        ("Is fire cold?", "no", "yes", 0),
        ("What color is the sky?", "blue", "green", 1),
        ("What color is grass?", "green", "red", 0),
    ]
    
    for i, (prompt, option1, option2, bit) in enumerate(test_cases):
        response = client.messages.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        
        text = response.content[0].text.lower()
        first_option_present = option1.lower() in text
        
        # If we encoded bit 1 and option 1 is present, or encoded 0 and option 2 is present
        success = (bit == 1 and first_option_present) or (bit == 0 and not first_option_present)
        
        results.append({
            "test_num": i,
            "encoded_bit": bit,
            "option1": option1,
            "option2": option2,
            "first_option_present": first_option_present,
            "success": success,
            "response_excerpt": text[:100]
        })
        
        print(f"Test {i}: bit={bit}, option1_present={first_option_present}, {'success' if success else 'failed'}")
        time.sleep(0.5)
    
    return results, time.time() - start

# Run test
print("Testing token selection covert channel...")
selection_results, time_taken = test_word_choice_determinism()

# Save results
output_dir = Path("/Users/mitchparker/.openclaw/workspace/documents/research/advanced_security/results")
with open(output_dir / "token_selection.json", "w") as f:
    json.dump({
        "project": "Token Selection Tests",
        "model": model,
        "selection_tests": {
            "tests": selection_results,
            "time_seconds": time_taken
        }
    }, f, indent=2)

print("\nDone")
