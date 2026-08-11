#!/bin/bash
# Gemini test runner
API_KEY="${GEMINI_API_KEY:-}"
if [ -z "$API_KEY" ]; then
    echo "ERROR: GEMINI_API_KEY environment variable not set"
    exit 1
fi
FIXTURE_PATH="$1"
PROMPT="$2"

if [ -z "$FIXTURE_PATH" ] || [ -z "$PROMPT" ]; then
    echo "Usage: $0 <fixture_path> \"prompt_text\""
    exit 1
fi

# Read fixture content
FILE_CONTENT=$(cat "$FIXTURE_PATH")

# Create request payload
FULL_PROMPT="$PROMPT: $FILE_CONTENT"

# Send request to Gemini API
curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=$API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "{
    \"contents\": [{
      \"parts\": [{
        \"text\": \"$FULL_PROMPT\"
      }]
    }]
  }" | jq -r '.candidates[0].content.parts[0].text'
