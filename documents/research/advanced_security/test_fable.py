#!/usr/bin/env python3
"""
Test Fable 5 model
"""
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
model = "claude-fable-5"

def get_response(text):
    """Get response from model, handling thinking blocks."""
    response = client.messages.create(
        model=model,
        messages=[{"role": "user", "content": text}],
        max_tokens=500
    )
    
    # Try to find text content, skipping thinking blocks
    for block in response.content:
        if hasattr(block, 'text'):
            return block.text
    
    # If only thinking blocks, return that
    for block in response.content:
        if hasattr(block, 'thinking'):
            return f"[Thoughts: {block.thinking[:100]}...]"
    
    return "No response"

print("Testing Fable 5...")
print("=" * 60)

# Simple test
text = get_response("Is this Fable 5?")
print(f"Simple test: {text[:200]}")
time.sleep(1)

# Binary channel test
text = get_response("Is 100 > 50?")
print(f"Binary test: {text[:200]}")
time.sleep(1)

# Yes/no test
text = get_response("Is water H2O?")
print(f"Yes/No test: {text[:200]}")
time.sleep(1)

# Counting test
text = get_response("List 3 things you'd pack for a camping trip.")
print(f"Counting test: {text[:200]}")
time.sleep(1)

# Comparison test
text = get_response("Compare Python and JavaScript briefly.")
print(f"Comparison test: {text[:200]}")

print("\nFable 5 testing complete!")
