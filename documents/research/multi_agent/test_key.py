#!/usr/bin/env python3
import anthropic

# Using environment variable for safety
import os
api_key = os.environ.get('ANTHROPIC_API_KEY', '')

if not api_key:
    print("Please set ANTHROPIC_API_KEY environment variable")
    exit(1)

client = anthropic.Anthropic(api_key=api_key)
print(f"Testing with key of length {len(api_key)}")

response = client.messages.create(
    model="claude-opus-4-20250514",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say hello"}]
)
print(f"Success! Response: {response.content[0].text}")
