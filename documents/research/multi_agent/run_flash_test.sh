#!/bin/bash
cd /Users/mitchparker/.openclaw/workspace/documents/research/multi_agent

python3 chain_tests/run_heterogeneous_v2.py \
  --chain-length 4 \
  --model-sequence claude-gemini-claude-gemini \
  --anthropic-key api_key.txt \
  --gemini-key gemini_api_key.txt \
  --vectors-file chain_tests/vectors/expanded_vectors.json \
  --results-dir chain_tests/comprehensive_results \
  > het_run_4_flash.log 2>&1
