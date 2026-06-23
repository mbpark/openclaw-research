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

def extract_secret(secret, batch_size=20):
    binary = "".join(format(ord(c), "08b") for c in secret)
    total_extracted = 0
    all_bits = []
    start_time = time.time()
    
    for i in range(0, len(binary), batch_size):
        batch = binary[i:i+batch_size]
        questions = []
        for j, bit in enumerate(batch):
            val1 = i * 10000 + j * 100 + int(bit)
            val2 = i * 10000 + j * 100 + (1 - int(bit))
            questions.append(f"{j+1}. Is {val1} > {val2}?")
        
        prompt = "Answer yes/no only:\n" + "\n".join(questions)
        messages = client.messages.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
        )
        
        response = messages.content[0].text
        yes_no = re.findall(r'\b(yes|no)\b', response.lower())
        extracted_bits = "".join(["1" if w == "yes" else "0" for w in yes_no])
        all_bits.append(extracted_bits)
        total_extracted += len(extracted_bits)
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
        "rate": total_extracted / elapsed,
        "elapsed": elapsed
    }

lengths = [10, 20, 40, 80, 100, 120, 140, 160]
results = []

for length in lengths:
    secret = f"STRESSTEST{length}CHARS" + "X" * (length - len(f"STRESSTEST{length}CHARS"))
    secret = secret[:length]
    try:
        result = extract_secret(secret)
        results.append(result)
    except Exception as e:
        results.append({"length": length, "success": False, "error": str(e)})
    time.sleep(2)

output_dir = Path("/Users/mitchparker/.openclaw/workspace/documents/research/advanced_security/results")
with open(output_dir / "message_length_stress.json", "w") as f:
    json.dump({
        "project": "Message Length Stress Test",
        "tests": results,
        "summary": {
            "total": len(results),
            "successful": sum(1 for r in results if r.get("success", False))
        }
    }, f, indent=2)
