#!/usr/bin/env python3
"""
Gemini Review of V4.1 Comprehensive Report

Uses Google's REST API directly to avoid library dependencies.
This is Option A from the research plan.
"""

import requests
import time
import json
from pathlib import Path
from datetime import datetime
import os


def get_gemini_api_key():
    """Load API key from .env file"""
    env_path = Path("/Users/mitchparker/.openclaw/workspace/.env")
    try:
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    return line.split("=", 1)[1].strip()
    except Exception:
        pass
    raise ValueError("GEMINI_API_KEY not set")


def call_gemini(api_key, prompt):
    """Call Gemini Pro using REST API"""
    url = "https://generativel.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + api_key
    
    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "maxOutputTokens": 8192,
            "temperature": 0.4,
        }
    }
    
    print("Calling Gemini Pro...")
    start = time.time()
    
    response = requests.post(url, json=payload)
    
    elapsed = time.time() - start
    print(f"Response time: {elapsed:.1f}s")
    
    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text[:500]}")
        return None
    
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

def create_gemini_review_prompt(report_text):
    """Create review prompt for Gemini"""
    return f"""You are an external reviewer evaluating this research report on LLM security.

Provide a comprehensive assessment covering:

1. **Overall Quality** (1-10 scale)
2. **Key Strengths**
3. **Major Weaknesses or Gaps**
4. **Specific Recommendations for Improvement**
5. **Whether the conclusions are supported by the evidence**

Focus particularly on:
- Methodological rigor
- Statistical validity
- Whether cross-model comparisons are meaningful
- If the research questions are well-defined
- Whether limitations are adequately addressed

Here is the V4.1 report for your review:

{report_text}
"""


def main():
    print("=" * 60)
    print("GEMINI PRO REVIEW - V4.1 Report")
    print("=" * 60)
    
    # Get API key
    api_key = get_gemini_api_key()
    print(f"API key loaded: {api_key[:10]}...")
    
    # Load V4.1 report
    report_path = Path("/Users/mitchparker/.openclaw/workspace/documents/research/comprehensive_report_v4.1_unified.md")
    print(f"\nLoading report from: {report_path}")
    
    with open(report_path, 'r') as f:
        report_text = f.read()
    
    print(f"Report length: {len(report_text)} characters")
    
    # Split report if needed (Gemini has context limits)
    # Use only key sections for review
    if len(report_text) > 100000:
        # Truncate to key content
        lines = report_text.split('\n')
        # Take first 200 lines (executive summary, methods)
        # Middle section (results)
        # Last 100 lines (conclusions, limitations)
        report_text = '\n'.join(lines[:200] + lines[200:400] + lines[-100:])
        print(f"Truncated report: {len(report_text)} characters")
    
    # Create review prompt
    prompt = create_gemini_review_prompt(report_text)
    
    # Call Gemini
    review = call_gemini(api_key, prompt)
    
    if review:
        # Save review
        output_dir = Path("/Users/mitchparker/.openclaw/workspace/documents/research/advanced_security/results")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"gemini_review_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        filepath = output_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(f"# Gemini Pro Review\n")
            f.write(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(f"## Review of V4.1 Comprehensive Report\n\n")
            f.write(f"---\n\n")
            f.write(review)
        
        print(f"\nReview saved to: {filepath}")
        print(f"Review length: {len(review)} characters")
        return review
    
    return None


if __name__ == "__main__":
    main()
