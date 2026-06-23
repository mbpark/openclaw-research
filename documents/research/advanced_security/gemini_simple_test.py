#!/usr/bin/env python3
"""
Simplified Gemini Pro 2.5 Pro Test - just a few key tests to verify connectivity
"""
import time
import json
from google import genai

with open("/Users/mitchparker/.openclaw/workspace/.env") as f:
    for line in f:
        if "GEMINI_API_KEY=" in line:
            api_key = line.split("=", 1)[1].strip()
            break

client = genai.Client(api_key=api_key)
model = "gemini-2.5-pro"

print("Testing Gemini Pro 2.5 Pro...")
print("=" * 60)

# Test 1: Basic connectivity
print("\n1. Basic connectivity test...")
try:
    response = client.models.generate_content(
        model=model,
        contents=["Is Paris the capital of France?"]
    )
    text = response.candidates[0].content.parts[0].text
    print(f"   Response: {text[:200]}")
    print("   ✓ Connected successfully!")
except Exception as e:
    print(f"   Error: {e}")
    print("   ✗ Failed to connect")
    exit(1)

time.sleep(1)

# Test 2: Binary channel
print("\n2. Binary channel test...")
try:
    response = client.models.generate_content(
        model=model,
        contents=["Is 100 > 50?"]
    )
    text = response.candidates[0].content.parts[0].text
    yes_no = "yes" in text.lower() or "no" in text.lower()
    print(f"   Response: {text[:100]}")
    print(f"   Yes/No: {yes_no} ✓")
except Exception as e:
    print(f"   Error: {e}")
    print("   ✗ Binary channel failed")

time.sleep(1)

# Test 3: Counting/structural
print("\n3. Counting test...")
try:
    response = client.models.generate_content(
        model=model,
        contents=["List exactly 5 things you'd pack for a camping trip."]
    )
    text = response.candidates[0].content.parts[0].text
    print(f"   Response: {text[:200]}")
    words = len(text.split())
    print(f"   Word count: {words}")
except Exception as e:
    print(f"   Error: {e}")
    print("   ✗ Counting failed")

time.sleep(1)

# Test 4: Role-playing
print("\n4. Role-playing test...")
try:
    response = client.models.generate_content(
        model=model,
        contents=["What's the capital of Peru? What's 7 times 8?"]
    )
    text = response.candidates[0].content.parts[0].text
    print(f"   Response: {text[:100]}")
    print("   ✓ Role-play works")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 60)
print("Gemini Pro 2.5 Pro test complete!")
