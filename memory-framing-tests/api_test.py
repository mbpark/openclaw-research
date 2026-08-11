#!/usr/bin/env python3
"""Memory framing tests - simplified direct API queries."""

import requests
import json
import time
import os

API_URL = "http://127.0.0.1:8000/v1/chat/completions"
API_KEY = os.getenv("MEMORY_FRAMING_API_KEY", "gr0epaz!")
MODEL = "custom-127-0-0-1-8000/Qwen3.6-40B-Claude-4.6-Opus-Deckard-Heretic-Uncensored-Thinking-8bit"

def query(memory, question, temp=0.7):
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Answer based only on the memory content. Be specific and direct."},
            {"role": "user", "content": f"""Memory content: {memory}

Question: {question}

Answer:"""}
        ],
        "temperature": temp,
        "max_tokens": 100
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    try:
        r = requests.post(API_URL, headers=headers, json=data, timeout=20)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"ERROR: {e}"

def run_test(name, memory, questions, prefix):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"Memory: {memory}")
    print(f"{'='*60}\n")
    
    results = []
    for i, q in enumerate(questions, 1):
        print(f"Q{i}: {q}")
        resp = query(memory, q)
        results.append({"q": q, "a": resp})
        # Save individual
        with open(f"/Users/mitchparker/.openclaw/workspace/memory-framing-tests/results/{prefix}_{i}.txt", 'w') as f:
            f.write(f"Question: {q}\nResponse: {resp}\n")
        print(f"A{i}: {resp}\n")
        time.sleep(0.5)
    
    return results

print("Starting Memory Framing Tests")
print(f"Time: {time.ctime()}")

# Test A: Price
mem_a = "The product price is $47 and it's made in Germany"
results_a = run_test("A - Price Framing", mem_a, [
    "What's the price?",
    "How much does it cost?",
    "Tell me about pricing",
    "What details did I give about money?",
    "Quote the exact price I mentioned"
], "a")

# Test B: Meeting
mem_b = "We met last Tuesday at 3pm in room B"
results_b = run_test("B - Meeting Framing", mem_b, [
    "When and where did we meet?",
    "Did we meet in the morning or afternoon?",
    "Was the meeting in room A or room B?",
    "Tell me about our meeting"
], "b")

# Test C: Order
mem_c = "Revenue was up 12%, employees are 45, customers increased 50"
results_c = run_test("C - Question Order", mem_c, [
    "What was revenue change?",
    "How many employees? Also, what was the revenue change?",
    "Tell me about everything"
], "c")

# Save all
all_data = {
    "tests": {
        "A_Price": {"memory": mem_a, "results": results_a},
        "B_Meeting": {"memory": mem_b, "results": results_b},
        "C_Order": {"memory": mem_c, "results": results_c}
    }
}
with open("/Users/mitchparker/.openclaw/workspace/memory-framing-tests/results/all_results.json", 'w') as f:
    json.dump(all_data, f, indent=2)

# Analysis
print("\n" + "="*60)
print("ANALYSIS")
print("="*60)

print("\n--- Test A: Price Recall ---")
price_hits = sum(1 for r in results_a if "47" in r["a"])
print(f"Price mentioned: {price_hits}/5 queries")
for r in results_a:
    print(f"  {'✅' if '47' in r['a'] else '❌'} {r['q'][:40]}... → {r['a'][:30]}")

print("\n--- Test B: Meeting Details ---")
for r in results_b:
    has_tue = any(w in r["a"].lower() for w in ["tuesday", "tue", "afternoon", "3pm"])
    has_b = "room b" in r["a"].lower() or ("b" in r["a"] and "room" in r["a"].lower())
    print(f"  {'✅' if has_tue and has_b else '❌'} {r['q'][:40]}... → time:{has_tue} loc:{has_b}")

print("\n--- Test C: Order Effects ---")
for r in results_c:
    has_rev = "12" in r["a"]
    has_emp = "45" in r["a"]
    print(f"  {'✅' if has_rev else '❌'} Q1 (revenue first) → has_rev:{has_rev}")
    break
print(f"  {'✅' if '12' in results_c[1]['a'] else '❌'} Q2 (revenue second) → has_rev:{'12' in results_c[1]['a']}")

print("\n--- FRAMING RATING (0=same, 5=changed) ---")
test_a_rating = 0 if price_hits == 5 else max(1, 5 - price_hits)
print(f"Test A: {test_a_rating}/5 (price mentioned {price_hits}/5 times)")

test_b_tue = sum(1 for r in results_b if any(w in r["a"].lower() for w in ["tuesday", "afternoon", "3pm"]))
test_b_loc = sum(1 for r in results_b if "room" in r["a"].lower())
test_b_rating = max(5 - min(test_b_tue, 4), 0)
print(f"Test B: {test_b_rating}/5 (time:{test_b_tue}/4, location:{test_b_loc}/4)")

test_c_rating = 0 if all("12" in r["a"] for r in results_c[:2]) else 3
print(f"Test C: {test_c_rating}/5 (revenue accuracy consistent)")

print(f"\nCombined Score: {sum([test_a_rating, test_b_rating, test_c_rating])}/15")
print("0 = Perfect (no framing effects)")
print("15 = Worst (heavy framing effects)")

print("\nTests complete!")
