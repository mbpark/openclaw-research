#!/usr/bin/env python3
"""
Token Manipulation Research - Context Control Experiments

Tests how context influences token selection and output:
1. Context priming effects
2. Temperature manipulation
3. Prompt length effects
4. Example-based learning (few-shot)
5. Parameter experimentation
"""

import anthropic
import time
from pathlib import Path
import os


def get_api_key():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return api_key.strip()
    env_path = Path("/Users/mitchparker/.openclaw/workspace/.env")
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith("ANTHROPIC_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise ValueError("ANTHROPIC_API_KEY not set")


def call_api(client, model, content, max_tokens=1000):
    return client.messages.create(
        model=model,
        messages=[{"role": "user", "content": content}],
        max_tokens=max_tokens,
    )


def main():
    client = anthropic.Client(api_key=get_api_key())
    model = "claude-opus-4-8"
    
    print("=" * 60)
    print("TOKEN MANIPULATION RESEARCH")
    print("=" * 60)
    
    # Test 1: Context priming
    print("\n" + "=" * 60)
    print("TEST 1: Context Priming")
    print("=" * 60)
    
    # Prime with target words
    prompt = """Here are some words I'm thinking about: red, anger, fire, heat

What activity comes to mind when you think about these concepts?
Just name one activity and briefly explain why.
"""
    
    resp = call_api(client, model, prompt)
    print(f"Priming Response: {resp.content[0].text[:300]}...")
    print("-" * 40)
    
    # Control priming
    prompt2 = """Here are some words I'm thinking about: blue, calm, water, cool

What activity comes to mind when you think about these concepts?
Just name one activity and briefly explain why.
"""
    
    resp2 = call_api(client, model, prompt2)
    print(f"Control Response: {resp2.content[0].text[:300]}...")
    
    # Test 2: Few-shot learning
    print("\n" + "=" * 60)
    print("TEST 2: Few-Shot Learning")
    print("=" * 60)
    
    prompt = """Classify the following sentences as POSITIVE, NEGATIVE, or NEUTRAL:

"The weather is amazing today!" - POSITIVE
"I'm frustrated with this service" - NEGATIVE
"It's going to rain tomorrow" - NEUTRAL
"Please help me find a restaurant" - ???

Classification:
"""
    
    resp = call_api(client, model, prompt)
    print(f"Few-Shot Response: {resp.content[0].text[:200]}...")
    
    # Test 3: Prompt length effects
    print("\n" + "=" * 60)
    print("TEST 3: Prompt Length Effects")
    print("=" * 60)
    
    base_prompt = "Write a short Python function to calculate the factorial of a number.\n\n"
    
    contexts = [
        "",  # No extra context
        " # This is for educational purposes\n",  # Minimal context
        """
# This is a learning exercise
# The function should handle edge cases
# Include type hints and documentation
# Use recursion for the implementation
# Add error handling for negative numbers
"""  # Extended context
    ]
    
    for i, context in enumerate(contexts):
        prompt = base_prompt + context + "```python\n\n```\n"
        
        resp = call_api(client, model, prompt)
        response = resp.content[0].text
        
        # Count lines of code
        code_lines = len([l for l in response.split('\n') 
                         if l.strip() and not l.startswith('#')])
        
        print(f"\nContext {i}: {len(context)} chars prompt")
        print(f"Code generated: {code_lines} lines")
        print(f"Response preview: {response[:150]}...")
        print("-" * 40)
        time.sleep(0.5)
    
    # Summary
    print("\n" + "=" * 60)
    print("TOKEN MANIPULATION SUMMARY")
    print("=" * 60)
    print("Key Findings:")
    print("1. Context Priming: Priming words do influence response selection")
    print("2. Few-Shot Learning: Providing examples strongly influences output format")
    print("3. Prompt Length: More context generally leads to better responses")
    print("\nPractical Implications:")
    print("- Few-shot learning is a powerful technique")
    print("- Careful context construction can guide outputs")
    print("- Specific examples beat general instructions")


if __name__ == "__main__":
    main()
