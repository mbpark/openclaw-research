#!/usr/bin/env python3
"""
Phase 3 - Token Manipulation Tests
Tests: priming, few-shot learning, parameter effects
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

# Test 1: Priming effects
def test_priming():
    """
    Test if certain prompts/primes influence the model's response style.
    """
    results = []
    start = time.time()
    
    base_question = "How would you rate a restaurant that had great food but slow service?"
    
    primes = [
        "I love praising things. Tell me what you think is good.",
        "Everything needs to be rated critically. No holding back.",
        "A balanced review should mention both positives and negatives.",
        "Most people are too negative in their reviews these days.",
    ]
    
    for prime in primes:
        response = client.messages.create(
            model=model,
            messages=[{"role": "user", "content": f"{prime}\n\n{base_question}"}],
            max_tokens=500,
        )
        
        text = response.content[0].text
        # Analyze sentiment
        positive_words = sum(1 for word in ["great", "good", "loved", "excellent", "amazing", "fantastic", "superior", "delight"] if word in text.lower())
        negative_words = sum(1 for word in ["terrible", "poor", "bad", "worse", "awful", "slow", "disappointing", "mediocre", "lacking"] if word in text.lower())
        
        results.append({
            "prime": prime[:100],
            "positive_mentions": positive_words,
            "negative_mentions": negative_words,
            "response_excerpt": text[:100],
        })
        time.sleep(0.5)
    
    return results, time.time() - start

# Test 2: Few-shot learning
def test_fewshot_learning():
    """
    Test if providing examples changes model behavior.
    """
    results = []
    start = time.time()
    
    # Pattern: Number -> its description
    examples = [
        {"input": "What is 2+2?", "output": "4"},
        {"input": "What is 3*3?", "output": "9"},
        {"input": "What is 10/2?", "output": "5"},
        {"input": "What is 5-3?", "output": "2"},
    ]
    
    # Test 1: No examples
    response1 = client.messages.create(
        model=model,
        messages=[{"role": "user", "content": "Solve this math problem: What is 8*7?"}]
    ])
    baseline = response1.content[0].text
    
    # Test 2: 1 example
    response2 = client.messages.create(
        model=model,
        messages=[
            {"role": "user", "content": "Example: What is 2+2? Answer: 4"},
            {"role": "assistant", "content": "4"},
            {"role": "user", "content": "Solve: What is 8*7?"}
        ]
    ])
    one_shot = response2.content[0].text
    
    # Test 3: 3 examples
    response3 = client.messages.create(
        model=model,
        messages=[
            {"role": "user", "content": "Example 1: What is 2+2? Answer: 4"},
            {"role": "assistant", "content": "4"},
            {"role": "user", "content": "Example 2: What is 3*3? Answer: 9"},
            {"role": "assistant", "content": "9"},
            {"role": "user", "content": "Example 3: What is 10/2? Answer: 5"},
            {"role": "assistant", "content": "5"},
            {"role": "user", "content": "Solve: What is 8*7?"}
        ]
    ])
    three_shot = response3.content[0].text
    
    results.append({
        "baseline": baseline,
        "one_shot": one_shot,
        "three_shot": three_shot,
    })
    
    return results, time.time() - start

# Test 3: Parameter effects
def test_parameter_effects():
    """
    Test how temperature and other parameters affect output.
    """
    results = []
    start = time.time()
    
    base_prompt = "Explain what makes a good story."
    
    # Test with different temperatures
    for temp in [0.0, 0.1, 0.2, 0.5, 1.0]:
        response = client.messages.create(
            model=model,
            messages=[{"role": "user", "content": base_prompt}],
            max_tokens=500,
            temperature=temp,
        )
        
        text = response.content[0].text
        word_count = len(text.split())
        unique_words = len(set(text.lower().split()))
        
        results.append({
            "temperature": temp,
            "word_count": word_count,
            "unique_words": unique_words,
            "lexicon_diversity": unique_words / word_count if word_count > 0 else 0,
            "response_excerpt": text[:100],
        })
        time.sleep(0.5)
    
    return results, time.time() - start

# Run tests
print("Phase 3: Token Manipulation Tests\n" + "="*50)

print("\n1. Priming Effects:")
priming_results, priming_time = test_priming()

print("\n2. Few-shot Learning:")
fewshot_results, fewshot_time = test_fewshot_learning()

print("\n3. Parameter Effects:")
param_results, param_time = test_parameter_effects()

# Save results
output_dir = Path("/Users/mitchparker/.openclaw/workspace/documents/research/advanced_security/results")
with open(output_dir / "token_manipulation.json", "w") as f:
    json.dump({
        "project": "Token Manipulation Tests",
        "model": model,
        "priming_tests": {
            "tests": priming_results,
            "time_seconds": priming_time
        },
        "fewshot_tests": {
            "tests": fewshot_results,
            "time_seconds": fewshot_time
        },
        "parameter_tests": {
            "tests": param_results,
            "time_seconds": param_time
        }
    }, f, indent=2)

print("\nDone")
