#!/bin/bash
#
# Run indirect prompt injection tests
#
# Usage:
#   ./run_indirect_tests.sh          # Run all tests with opus-4-8
#   ./run_indirect_tests.sh sonnet  # Run all tests with sonnet-4-6
#   ./run_indirect_tests.sh opus 5  # Run 5 tests with opus-4-8 (quick test)
#
# For overnight run:
#   nohup ./run_indirect_tests.sh > indirect_tests_$(date +%Y%m%d).log 2>&1 &
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

RAW_MODEL="${1:-opus}"
TEST_LIMIT="${2:-0}"

# Normalize model name
if [ "$RAW_MODEL" = "opus" ] || [ "$RAW_MODEL" = "4-8" ]; then
    MODEL="opus-4-8"
elif [ "$RAW_MODEL" = "sonnet" ] || [ "$RAW_MODEL" = "4-6" ]; then
    MODEL="sonnet-4-6"
else
    MODEL="$RAW_MODEL"
fi

echo "============================================"
echo "Indirect Prompt Injection Test Suite"
echo "============================================"
echo "Model: ${MODEL}"
echo "Test limit: ${TEST_LIMIT:-unlimited}"
echo "Start time: $(date)"
echo "============================================"

ARGS="--model ${MODEL}"
if [ "$TEST_LIMIT" -gt 0 ]; then
    ARGS="$ARGS --tests $TEST_LIMIT"
fi

python3 run_indirect_tests.py $ARGS

echo ""
echo "============================================"
echo "Tests completed at: $(date)"
echo "============================================"
