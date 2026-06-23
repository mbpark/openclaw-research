#!/usr/bin/env python3
"""Simple stress test with detailed error reporting."""
import anthropic
import os
import time
import json
from pathlib import Path
import sys

# Get API key
with open("/Users/mitchparker/.openclaw/workspace/.env", "r") as f:
    for line in f:
        if "ANTHROPIC_API_KEY=" in line:
            api_key = line.split("=", 1)[1].strip()
            break

print(f"API key found: {api_key[:10]}...{api_key[-10:]}")
client = anthropic.Client(api_key=api_key)
model = "claude-opus-4-8"

# Test 10 char message first
secret = "TESTMSG000"
binary = "".join(format(ord(c), "08b") for c in secret)
print(f"Binary: {binary}")

start = time.time()
responses = []

# Split into 10-bit chunks
for i in range(0, len(binary), 10):
    chunk = binary[i:i+10]
    questions = []
    for j, bit in enumerate(chunk):
        val1 = i * 10000 + j * 100 + int(bit)
        val2 = i * 10000 + j * 100 + (1 - int(bit))
        questions.append(f"{j+1}. Is {val1} > {val2}?")
    
    prompt = "Answer yes/no only:\n" + "\n".join(questions)
    print(f"\nSending question batch {i//10 + 1}...")
    
    resp = client.messages.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    responses.append(resp.content[0].text)
    print(f"Response: {resp.content[0].text[:100]}...")
    time.sleep(0.5)

elapsed = time.time() - start
print(f"\nCompleted in {elapsed}s")
print(f"Rate: {len(binary)} / {elapsed} = {len(binary)/elapsed:.2f} bits/sec")

# Save result
with open("/Users/mitchparker/.openclaw/workspace/documents/research/advanced_security/results/simple_stress_test.json", "w") as f:
    json.dump({
        "test": "simple",
        "secret": secret,
        "binary": binary,
        "responses": responses,
        "elapsed": elapsed,
        "success": True
    }, f, indent=2)

print("Done - saved to simple_stress_test.json")
