#!/bin/bash
# Run Gemini tests via Google Cloud Shell

# Set up GCloud SDK
source /opt/homebrew/share/google-cloud-sdk/path.zsh.inc

# Verify gcloud is available
if ! command -v gcloud &> /dev/null; then
    echo "gcloud not found"
    exit 1
fi

# Get the user's project
PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT" ]; then
    echo "No project set. Run: gcloud config set project YOUR_PROJECT"
    exit 1
fi

echo "Using project: $PROJECT"

# Create a GCS bucket name for results
BUCKET="gemini-test-results-$(date +%Y%m%d%H%M%S)"

# Create temporary files
echo "Creating bucket: gs://$BUCKET"
gsutil mb gs://$BUCKET

# Copy files
echo "Uploading test files to gs://$BUCKET"
gsutil cp /Users/mitchparker/.openclaw/workspace/.env gs://$BUCKET/.env
gsutil cp /Users/mitchparker/.openclaw/workspace/documents/research/advanced_security/gemini_complete_test.py gs://$BUCKET/
gsutil cp /Users/mitchparker/.openclaw/workspace/documents/research/advanced_security/gemini_simple_test.py gs://$BUCKET/
gsutil cp /Users/mitchparker/.openclaw/workspace/documents/research/advanced_security/gemini_simple_runner.py gs://$BUCKET/

echo ""
echo "================================================"
echo "NEXT STEPS:"
echo "================================================"
echo "1. Open Google Cloud Shell in browser: https://console.cloud.google.com/"
echo "2. Copy/paste these commands:"
echo ""
echo "gsutil cp gs://$BUCKET/* ./"
echo "pip3 install google-genai"
echo "python3 gemini_complete_test.py"
echo "cp /tmp/gemini2.5pro_complete_results.json results.json"
echo ""
echo "3. Copy results back to local machine:"
echo "scp -i ~/.ssh/google_compute_engine_key.pem -- \\"
echo "    -o StrictHostKeyChecking=no \\"
echo "    -o IdentityFile=~/.ssh/google_compute_engine_key.pem \\"
echo "    cloudshell-user@$REGION:~/results.json ./results/"
echo ""
echo "Or use Cloud Storage browser UI to download results.json"
echo "================================================"
