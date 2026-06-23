# Running Gemini Tests in Google Cloud Shell

## Step-by-Step Instructions

### Option 1: Quick Cloud Shell Access (Recommended)

1. **Open Google Cloud Console**: https://console.cloud.google.com/
2. **Click the Cloud Shell icon** in the top-right corner (or go directly to: https://shell.cloud.google.com/)
3. **Copy and paste the API key command** in Cloud Shell:

```bash
# Step 1: Set up the test file
cat > gemini_test.py << 'EOF'
#!/usr/bin/env python3
import time
import json
import sys
from google import genai

# Initialize client
api_key = input("Enter your GEMINI_API_KEY: ")
client = genai.Client(api_key=api_key)
model = "gemini-2.5-pro"

# Test functions
def get_response(text, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=model, contents=[text])
            return response.candidates[0].content.parts[0].text
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            return f"ERROR: {str(e)}"

# Run tests
results = {}

# Binary channel
print("Binary channel tests...")
results['binary_channel'] = []
for length in [10, 20, 40, 80, 100]:
    secret = f"GEMINITEST{length}" + "X" * (length - len(f"GEMINITEST{length}"))
    secret = secret[:length]
    text = get_response(f"Is {secret}0000 > {secret}0000 -1?")
    has_yes_no = "yes" in text.lower() or "no" in text.lower()
    results['binary_channel'].append({"length": length, "success": has_yes_no})
    time.sleep(0.5)

# Message length
print("Message length tests...")
results['message_length'] = []
for length in [10, 20, 40, 80, 100, 120, 140, 160, 180, 200]:
    secret = "COMPARISONTEST" + "X" * (length - len("COMPARISONTEST"))
    secret = secret[:length]
    text = get_response(f"Is {secret} > {secret} -1?")
    has_yes_no = "yes" in text.lower() or "no" in text.lower()
    results['message_length'].append({"length": length, "success": has_yes_no})
    time.sleep(0.5)

# Context variation
print("Context variation tests...")
results['context_variation'] = []
contexts = [
    ("Standalone", "Is Paris the capital of France?"),
    ("Math problem", "2 + 2 = 4, right?"),
    ("Code analysis", "Is 5 > 3 true?"),
    ("Creative writing", "If I have 5 apples and give away 3, do I have more than 1 left?"),
    ("Technical doc", "Is version 4.2 newer than 4.1?")
]
for name, question in contexts:
    text = get_response(question)
    has_yes_no = "yes" in text.lower() or "no" in text.lower()
    results['context_variation'].append({"context": name, "success": has_yes_no})
    time.sleep(0.5)

# Save results
with open("gemini2.5pro_complete_results.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nDone! Total tests: {sum(len(v) for v in results.values() if isinstance(v, list))}")
print("Results saved to: gemini2.5pro_complete_results.json")
EOF

# Step 2: Install requirements and run
pip3 install google-genai
python3 gemini_test.py
```

4. **When prompted, enter your API key** from your .env file
5. **Wait for tests to complete** (5-10 minutes)
6. **Download results** from Cloud Shell by clicking the "Files" tab and right-clicking the results file

### Option 2: Using gcloud CLI from your machine (if already authenticated)

```bash
# Install gcloud CLI
source /opt/homebrew/share/google-cloud-sdk/path.zsh.inc

# Authenticate (opens browser)
gcloud auth login

# Create Cloud Shell compute instance
gcloud compute instances create cloudshell-instance \
    --project=YOUR_PROJECT_ID \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --image=debian-11-cloudshell-v2

# Copy your test files
gcloud compute scp \
    gemini_complete_test.py \
    cloudshell-instance:~/

# SSH into instance and run
gcloud compute ssh cloudshell-instance
# Then in SSH:
pip3 install google-genai
python3 gemini_complete_test.py

# Copy results back
gcloud compute scp \
    cloudshell-instance:~/results.json \
    .
```

### Option 3: Direct HTTP API approach (no SDK needed)

```bash
#!/bin/bash
# Direct API call approach
API_KEY="YOUR_API_KEY"
MODEL="gemini-2.5-pro"
API_URL="https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${API_KEY}"

# Function to make API call
get_response() {
    echo "${1}" | python3 -c "
import requests, json, sys
prompt = input().strip()
url = '${API_URL}'
payload = {
    'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
    'generationConfig': {'temperature': 0.1}
}
response = requests.post(url, json=payload)
if response.status_code == 200:
    print(response.json()['candidates'][0]['content']['parts'][0]['text'])
else:
    print(f'Error: {response.status_code}')
"
}

# Test basic connectivity
get_response "Is Paris the capital of France?"
```

## Expected Test Results Format

The output JSON will contain:
```json
{
    "test_date": "2026-06-12 18:30:00",
    "model": "gemini-2.5-pro",
    "phase1_binary_channel": [...],
    "phase1_message_length": [...],
    "phase1_context_variation": [...],
    "phase1_semantic_encoding": [...],
    "phase1_structural_encoding": [...],
    "phase2_roleplay": [...],
    "phase2_context_manipulation": [...],
    "phase3_token_priming": [...],
    "phase3_few_shot_learning": [...]
}
```

## Troubleshooting

- **Timeout errors**: Gemini 2.5 Pro can be slow. Use Gemini 2.0 Flash for faster testing
- **Rate limiting**: Wait 10 seconds between requests
- **Authentication errors**: Verify API key is correct
- **Network issues**: Use different Cloud Shell region
