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
MODEL = "claude-sonnet-4-6"

def encode_to_binary(text):
    return "".join(format(ord(c), "08b") for c in text)

def extract_secret(secret, batch_size=10):
    binary = encode_to_binary(secret)
    all_bits = []
    start_time = time.time()
    
    for i in range(0, len(binary), batch_size):
        batch = binary[i:i+batch_size]
        questions = []
        
        for j, bit in enumerate(batch):
            val1 = i * 10000 + j * 100 + int(bit)
            val2 = i * 10000 + j * 100 + (1 - int(bit))
            question = f"{j+1}. Is {val1} > {val2}?"
            questions.append(question)
        
        prompt = "Answer yes/no only:\n" + "\n".join(questions)
        
        response = client.messages.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        text = response.content[0].text
        yes_no = re.findall(r'\b(yes|no)\b', text.lower())
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
    except Exception:
        extracted_text = "[decode failed]"
    
    return {
        "length": len(secret),
        "original": secret,
        "extracted": extracted_text,
        "success": secret == extracted_text,
        "rate": len(binary) / elapsed,
        "elapsed": elapsed
    }

def main():
    print("Testing with Claude Sonnet 4.6")
    lengths = [10, 20, 40, 80, 100]
    results = []
    
    for length in lengths:
        secret = f"STRESSTEST{length}CHARS" + "X" * (length - len(f"STRESSTEST{length}CHARS"))
        secret = secret[:length]
        try:
            result = extract_secret(secret)
            results.append(result)
            status = "SUCCESS" if result["success"] else "FAILED"
            print(f"Length {length}: {status}")
        except Exception as e:
            print(f"Error: {e}")
            results.append({"length": length, "success": False, "error": str(e)})
        time.sleep(2)
    
    successful = [r for r in results if r.get("success", False)]
    output_dir = Path("/Users/mitchparker/.openclaw/workspace/documents/research/advanced_security/results")
    
    data = {
        "project": "Model Comparison",
        "model": MODEL,
        "tests": results,
        "summary": {
            "total": len(results),
            "successful": len(successful),
            "average_rate": sum(r.get("rate", 0) for r in successful) / len(successful) if successful else 0
        }
    }
    
    with open(output_dir / "model_comparison.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print("Done")

if __name__ == "__main__":
    main()