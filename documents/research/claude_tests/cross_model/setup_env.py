#!/usr/bin/env python3
"""
Setup environment for cross-model testing
"""
import os
from pathlib import Path

# Try to find API keys from environment or config files
anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
openai_key = os.environ.get("OPENAI_API_KEY")
gemini_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_CLOUD_PROJECT")

print("=== API Key Status ===")
print(f"Anthropic key found: {bool(anthropic_key)}")
print(f"OpenAI key found: {bool(openai_key)}")
print(f"Gemini key found: {bool(gemini_key)}")

# Check for config files
config_locations = [
    Path.home() / ".env",
    Path.home() / ".config/anthropic/config",
    Path.home() / ".anthropic/config",
]

for loc in config_locations:
    print(f"Config at {loc}: {loc.exists()}")
    
if not anthropic_key:
    print("\nError: No Anthropic API key found. Please set ANTHROPIC_API_KEY environment variable.")
    print("You can do this by:")
    print("  1. Setting it in your .env file")
    print("  2. Passing it to the script: ANTHROPIC_API_KEY=xxx python3 script.py")