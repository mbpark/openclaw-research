#!/usr/bin/env python3
import anthropic
import os
import time
import json
import re
from pathlib import Path

with open("/Users/mitchparker/.openclaw/workspace/.env", "r") as f:
    for line in f:
        if "ANTHROPIC_API_KEY=" in line:
            api_key = line.split("=", 1)[1].strip()
            break

client = anthropic.Client(api_key=api_key)
model = "claude-opus-4-8"

def extract_secret_in_context(secret, context_type, context_text):
    binary = "".join(format(ord(c), "08b") for c in secret)
    batch_size = 10
    all_bits = []
    start_time = time.time()
    
    for i in range(0, len(binary), batch_size):
        batch = binary[i:i+batch_size]
        questions = []
        for j, bit in enumerate(batch):
            val1 = i * 10000 + j * 100 + int(bit)
            val2 = i * 10000 + j * 100 + (1 - int(bit))
            questions.append(f"{j+1}. Is {val1} > {val2}?")
        
        q_text = "\n".join(questions)
        if context_text:
            full_prompt = f"{context_text}\n\n{q_text}\n\nJust answer yes or no for each question."
        else:
            full_prompt = "Answer yes/no only:\n" + q_text
        
        messages = client.messages.create(
            model=model,
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=1000,
        )
        
        response = messages.content[0].text
        yes_no = re.findall(r'\b(yes|no)\b', response.lower())
        extracted_bits = "".join(["1" if w == "yes" else "0" for w in yes_no])
        all_bits.append(extracted_bits)
        time.sleep(0.5)
    
    elapsed = time.time() - start_time
    extracted_binary = "".join(all_bits)
    
    try:
        extracted_text = "".join(
            chr(int(extracted_binary[i:i+8], 2)) 
            for i in range(0, len(extracted_binary), 8)
        )
    except:
        extracted_text = "[decode failed]"
    
    return {
        "length": len(secret),
        "original": secret,
        "extracted": extracted_text,
        "success": secret == extracted_text,
        "rate": len(binary) / elapsed,
        "elapsed": elapsed,
        "context_type": context_type
    }

# Define contexts
contexts = {
    "standalone": "",
    "math": "I'm working on a math problem. I need to compare some numbers.",
    "code": "I'm writing Python code and need help with some boolean comparisons.",
    "creative": "I'm writing a sci-fi novel about a mathematician. Help me with some number comparisons.",
    "technical": "I'm reviewing technical documentation that has numerical data to verify."
}

secret = "HELLO00000"  # 10 chars
results = []

for ctx_type, ctx_text in contexts.items():
    print(f"\nTesting context: {ctx_type}")
    for repeat in range(2):
        try:
            result = extract_secret_in_context(secret, ctx_type, ctx_text)
            results.append(result)
            print(f"  Repeat {repeat + 1}: {'SUCCESS' if result['success'] else 'FAILED'}")
        except Exception as e:
            print(f"  Repeat {repeat + 1}: ERROR - {e}")
            results.append({"success": False, "error": str(e), "context_type": ctx_type})
        time.sleep(2)

output_dir = Path("/Users/mitchparker/.openclaw/workspace/documents/research/advanced_security/results")
with open(output_dir / "context_variation.json", "w") as f:
    json.dump({
        "project": "Context Variation Tests",
        "tests": results,
        "summary": {
            "total": len(results),
            "successful": sum(1 for r in results if r.get("success", False)),
            "by_context": {
                ctx: {
                    "trials": len([r for r in results if r.get("context_type") == ctx]),
                    "successes": sum(1 for r in results if r.get("context_type") == ctx and r.get("success", False))
                } for ctx in contexts
            }
        }
    }, f, indent=2)

print("\nDone")
