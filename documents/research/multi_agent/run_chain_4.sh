#!/bin/bash
# Run chain length 4 with Claude → Gemini Flash → Claude → Gemini Flash
# Usage: bash run_chain_4.sh

cd "$(dirname "$0")"

echo "Starting heterogeneous chain test..."
echo "Models: Claude → Gemini Flash → Claude → Gemini Flash"
echo "Chain length: 4"
echo "Vectors: 50"
echo "Injection points: 3 (start, middle, end)"
echo "Total tests: 150"
echo ""

python3 chain_tests/run_heterogeneous_v2.py \
  --chain-length 4 \
  --model-sequence claude-gemini-claude-gemini \
  --anthropic-key api_key.txt \
  --gemini-key gemini_api_key.txt \
  --vectors-file chain_tests/vectors/expanded_vectors.json \
  --results-dir chain_tests/comprehensive_results
