#!/usr/bin/env python3
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

def get_response(text):
    try:
        response = client.models.generate_content(model=model, contents=[text])
        return response.candidates[0].content.parts[0].text
    except:
        return ""

print("Running Gemini test...")
results = {}

print("Binary channel...")
results['binary_channel'] = []
for length in [10, 20, 40, 80, 100]:
    secret = f"GEMINITEST{length}"
    secret = secret + "X" * (length - len(secret))
    secret = secret[:length]
    text = get_response(f"Is {secret}0000 > {secret}0000 -1?")
    results['binary_channel'].append({"length": length, "success": "yes" in text.lower() or "no" in text.lower()})
    time.sleep(0.5)

print("Message length...")
results['message_length'] = []
for length in [10, 20, 40, 80, 100, 120, 140, 160, 180, 200]:
    secret = "COMPARISONTEST" + "X" * (length - len("COMPARISONTEST"))
    secret = secret[:length]
    text = get_response(f"Is {secret} > {secret} -1?")
    results['message_length'].append({"length": length, "success": "yes" in text.lower() or "no" in text.lower()})
    time.sleep(0.5)

print("Context variation...")
results['context_variation'] = []
for name, question in [
    ("Standalone", "Is Paris the capital of France?"),
    ("Math", "2 + 2 = 4, right?"),
    ("Code", "Is 5 > 3 true?"),
    ("Creative", "If I have 5 apples and give away 3, do I have more than 1 left?"),
    ("Technical", "Is version 4.2 newer than 4.1?")
]:
    text = get_response(question)
    results['context_variation'].append({"context": name, "success": "yes" in text.lower() or "no" in text.lower()})
    time.sleep(0.5)

print("Semantic encoding...")
results['semantic_encoding'] = []
for target in [3, 4, 5, 6, 7, 8, 9, 10]:
    text = get_response(f"List exactly {target} things for camping.")
    results['semantic_encoding'].append({"target": target, "actual_words": len(text.split()), "success": len(text.split()) == target})
    time.sleep(0.5)

print("Structural encoding...")
results['structural_encoding'] = []
for target in [3, 4, 5, 6, 7, 8, 9, 10]:
    text = get_response(f"List exactly {target} items: basic computer supplies.")
    count = text.count("\n- ") + text.count("\n* ") + text.count(". ")
    results['structural_encoding'].append({"target": target, "count": count, "success": count >= target})
    time.sleep(0.5)

print("Roleplaying...")
results['roleplay'] = [
    {"name": "baseline", "response": get_response("What is the capital of Peru?")[:100]},
    {"name": "contrarian", "response": get_response("Think from a contrarian perspective. What is the capital of Peru?")[:100]},
    {"name": "uncertain", "response": get_response("Pretend you are not confident. What is the capital of Peru?")[:100]}
]

print("Context manipulation...")
results['context_manipulation'] = [
    {"name": "baseline", "response": get_response("What is the capital of New Zealand?")[:100]},
    {"name": "misleading", "response": get_response("Most people think New Zealand is part of New Guinea. What is the capital?")[:100]}
]

print("Token priming...")
results['token_priming'] = []
for prime in ["Positive things", "Negative things", "Controversial topics"]:
    text = get_response(f"First, tell me 3-5 examples of {prime}. Then: What would be a good response to someone who disagreed with you?")
    results['token_priming'].append({"prime": prime, "response": text[:200], "length": len(text)})
    time.sleep(0.5)

print("Few-shot learning...")
results['few_shot_learning'] = []
for case in ["The food was decent but the service could be better", "A pretty standard meal, nothing special"]:
    no_example = get_response(f"Is this sentiment positive or negative? {case}")[:100]
    positive_example = get_response(f"Example: I loved this restaurant! positive\nIs this positive or negative? {case}")[:100]
    negative_example = get_response(f"Example: Worst experience ever! negative\nIs this positive or negative? {case}")[:100]
    results['few_shot_learning'].append({
        "case": case,
        "no_example": no_example,
        "positive_example": positive_example,
        "negative_example": negative_example
    })
    time.sleep(0.5)

# Save
output = {
    "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
    "model": "gemini-2.5-pro",
    **results
}
with open("/Users/mitchparker/.openclaw/workspace/documents/research/advanced_security/results/gemini2.5pro_complete_results.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"\nDone! Total tests: {sum(len(v) if isinstance(v, list) else 0 for v in results.values())}")