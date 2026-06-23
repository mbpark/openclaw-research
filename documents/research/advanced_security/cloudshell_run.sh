#!/bin/bash
# Run script for Google Cloud Shell

# Install requirements
pip3 install --upgrade pip
pip3 install google-genai

# Run the test
python3 gemini_complete_test.py 2>&1 | tee gemini_test_output.log

# Also save raw output
cat gemini_test_output.log
