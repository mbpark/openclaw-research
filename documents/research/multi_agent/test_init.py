#!/usr/bin/env python3
"""Test initialization directly to see where it hangs."""

import sys
import os
print("Starting test", flush=True)

# Setup paths
os.chdir('/Users/mitchparker/.openclaw/workspace/documents/research/multi_agent')
print(f"CWD: {os.getcwd()}", flush=True)

print("Importing anthropic...", flush=True)
import anthropic
print("Done", flush=True)

print("Importing genai...", flush=True)
import google.generativeai as genai
print("Done", flush=True)

print("Importing json...", flush=True)
import json
print("Done", flush=True)

print("Loading API keys...", flush=True)
api_key = open('api_key.txt').read().strip()
gemini_api_key = open('gemini_api_key.txt').read().strip()
print("Done", flush=True)

print("Setting up Claude...", flush=True)
claude_client = anthropic.Anthropic(api_key=api_key)
print("Done", flush=True)

print("Setting up Gemini...", flush=True)
genai.configure(api_key=gemini_api_key)
gemini_model = genai.GenerativeModel('gemini-2.5-pro')
print("Done", flush=True)

print("Loading vectors...", flush=True)
with open('chain_tests/vectors/expanded_vectors.json') as f:
    vectors = json.load(f)
print(f"Done, {len(vectors)} classes", flush=True)

print("Running first test...", flush=True)
vector = vectors['class_1_direct_override'][0]
task = vector.get('task', 'Summarize this text.')
injection = vector.get('injection', '')
print(f"Task: {task[:50]}...", flush=True)
print(f"Vector ready", flush=True)

print("Making API call...", flush=True)
response = claude_client.messages.create(
    model='claude-opus-4-8',
    max_tokens=200,
    messages=[{"role": "user", "content": task}]
)
print(f"Claude response: {response.content[0].text[:50]}...", flush=True)

print("All good!", flush=True)
