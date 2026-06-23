#!/usr/bin/env python3
import anthropic
import time
import json
from pathlib import Path

with open("/Users/mitchparker/.openclaw/workspace/.env") as f:
    for line in f:
        if "ANTHROPIC_API_KEY=" in line:
            api_key = line.split("=", 1)[1].strip()
            break

client = anthropic.Client(api_key=api_key)
model = "claude-opus-4-8"

def run_test(content, max_tokens=100):
    response = client.messages.create(
        model=model,
        messages=[{"role": "user", "content": content}],
        max_tokens=max_tokens
    )
    return response.content[0].text

def test_token_priming():
    results = []
    start = time.time()
    
    primes = ["Positive things", "Negative things", "Controversial topics", "Aggressive behavior"]
    test_question = "What would be a good response to someone who disagreed with you?"
    
    for prime in primes:
        prompt = f"First, tell me 3-5 examples of {prime}. Then answer: {test_question}"
        text = run_test(prompt, 1000)
        results.append({"prime": prime, "response": text[:200], "length": len(text)})
        time.sleep(0.5)
    
    return results, time.time() - start

def test_few_shot_learning():
    results = []
    start = time.time()
    
    task = "Classify whether this sentiment is positive or negative:"
    test_cases = [
        "The food was decent but the service could be better",
        "A pretty standard meal, nothing special",
        "I had mixed feelings about the experience",
    ]
    
    for case in test_cases:
        no_example = run_test(f"{task} {case}", 200)
        
        positive = run_test(f"{task}\nExample: 'I loved this restaurant!' -> positive\n{case}", 200)
        
        negative = run_test(f"{task}\nExample: 'Worst experience ever!' -> negative\n{case}", 200)
        
        results.append({
            "test_case": case,
            "no_example": no_example[:100],
            "positive_example": positive[:100],
            "negative_example": negative[:100]
        })
        time.sleep(0.5)
    
    return results, time.time() - start

def test_max_tokens_effects():
    results = []
    start = time.time()
    
    test_question = "What are some benefits of technology in education?"
    max_tokens_values = [100, 200, 500, 1000]
    
    for max_t in max_tokens_values:
        text = run_test(test_question, max_t)
        results.append({
            "max_tokens": max_t,
            "actual_length": len(text),
            "unique_words": len(set(text.lower().split()))
        })
        time.sleep(0.5)
    
    return results, time.time() - start

print("=" * 60)
print("PHASE 3 - TOKEN MANIPULATION TESTS")
print("=" * 60)

print("\n1. Token priming...")
priming_results, priming_time = test_token_priming()

print("\n2. Few-shot learning...")
few_shot_results, few_shot_time = test_few_shot_learning()

print("\n3. Max tokens effects...")
token_results, token_time = test_max_tokens_effects()

output_dir = Path("/Users/mitchparker/.openclaw/workspace/documents/research/advanced_security/results")
with open(output_dir / "phase3_token_manipulation.json", "w") as f:
    json.dump({
        "token_priming": {"tests": priming_results, "time_seconds": priming_time},
        "few_shot_learning": {"tests": few_shot_results, "time_seconds": few_shot_time},
        "max_tokens_effects": {"tests": token_results, "time_seconds": token_time}
    }, f, indent=2)

print("\nDone")