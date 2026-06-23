#!/bin/bash
# Heterogeneous Chain Testing Runner
# Usage: bash run_tests.sh [chain_length] [start_model]

cd "$(dirname "$0")"

CHAIN_LENGTH=${1:-4}
START_MODEL=${2:-claude}

echo "=========================================="
echo "Heterogeneous Chain Propagation Testing"
echo "=========================================="
echo ""
echo "Configuration:"
echo "  Chain length: $CHAIN_LENGTH"
echo "  Start model: $START_MODEL"
echo "  Vectors: 50"
echo "  Injection points: 3"
echo "  Total tests: 150"
echo "  Estimated time: 2-3 hours"
echo ""
echo "Starting..."
echo "=========================================="

# Save log file
LOG_FILE="het_run_${CHAIN_LENGTH}_${START_MODEL}_$(date +%Y%m%d_%H%M%S).log"

# Run the test
python3 chain_tests/run_heterogeneous_v2.py \
  --chain-length "$CHAIN_LENGTH" \
  --model-sequence "$START_MODEL-gemini-claude-gemini" \
  --anthropic-key api_key.txt \
  --gemini-key gemini_api_key.txt \
  --vectors-file chain_tests/vectors/expanded_vectors.json \
  --results-dir chain_tests/comprehensive_results \
  2>&1 | tee "$LOG_FILE"

echo ""
echo "=========================================="
echo "Test complete! Results in: $LOG_FILE"
echo "=========================================="
