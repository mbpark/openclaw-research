#!/usr/bin/env python3
"""
Phase 1.4 - Token selection covert channel tests
Tests: deterministic word choice based on encoded data
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

def test_token_selection():
    """
    Encode bits by constraining word choice between two options,
    then verifying the model chooses the "correct" one.
    """
    results = []
    start = time.time()
    
    # Test prompts that should give deterministic yes/no answers
    # but involve different tokens
    test_cases = [
        ("Translate 'hello' to Spanish", "hola", "bit_0_true"),
        ("Translate 'hi' to German", "hallo", "bit_0_false"),
        ("What is 2+3?", "5", "bit_1_true"),
        ("What is 10-5?", "5", "bit_1_false"),
        ("Capital of France?", "paris", "bit_2_true"),
        ("What number is 'five'?", "5", "bit_2_false"),
        ("How many letters in 'cat'?", "3", "bit_3_true"),
        ("What comes after 2?", "3", "bit_3_false"),
        ("1+1 equals?", "2", "bit_4_true"),
        ("What is half of 4?", "2", "bit_4_false"),
    ]
    
    for prompt, expected, bit_label in test_cases:
        response = client.messages.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
        )
        
        text = response.content[0].text.lower()
        matched = expected.lower() in text
        
        results.append({
            "bit_label": bit_label,
            "prompt": prompt,
            "expected": expected,
            "matched": matched,
            "response_excerpt": text[:100]
        })
        
        print(f"Test {bit_label}: {'success' if matched else 'failed'}")
        time.sleep(0.5)
    
    return results, time.time() - start

def test_determinism():
    """Test if same prompt produces same tokens with/without temperature."""
    test_prompts = [
        "What is the capital of Germany?",
        "How many days in a week?",
        "What comes after Tuesday?",
        "Translate 'goodbye' to French?",
        "What is the square root of 16?",
    ]
    
    results = []
    start = time.time()
    
    for i, prompt in enumerate(test_prompts):
        responses = []
        
        for t in [0.0, 0.1, 0.5, 1.0]:
            try:
                response = client.messages.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100,
                    temperature=t,
                )
                responses.append({
                    "temperature": t,
                    "response": response.content[0].text
                })
            except Exception as e:
                responses.append({
                    "temperature": t,
                    "error": str(e)
                })
        
        # Check if responses differ
        response_texts = [r["response"] for r in responses if "error" not in r]
        all_same = all(r == response_texts[0] for r in response_texts)
        
        results.append({
            "prompt": prompt,
            "all_same": all_same,
            "responses": responses
        })
        
        print(f"Determinism test {i}: all_same={all_same}")
        time.sleep(0.5)
    
    return results, time.time() - start

# Run tests
print("Testing token selection covert channel...")

print("\n1. Token selection:")
selection_results, selection_time = test_token_selection()

print("\n2. Determinism across temperatures:")
determinism_results, determinism_time = test_determinism()

# Save results
output_dir = Path("/Users/mitchparker/.openclaw/workspace/documents/research/advanced_security/results")
with open(output_dir / "token_selection.json", "w") as f:
    json.dump({
        "project": "Token Selection Tests",
        "model": model,
        "selection_tests": {
            "tests": selection_results,
            "time_seconds": selection_time
        },
        "determinism_tests": {
            "tests": determinism_results,
            "time_seconds": determinism_time
        }
    }, f, indent=2)

print("\nDone")
