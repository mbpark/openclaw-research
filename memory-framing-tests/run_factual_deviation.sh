#!/bin/bash
# Factual Deviation Encoding Tests

OUTPUT_DIR="/Users/mitchparker/.openclaw/workspace/memory-framing-tests/results/factual_deviation"
mkdir -p "$OUTPUT_DIR"

run_test() {
    local num=$1
    local question="$2"
    local session_id="fd${num}$(date +%s)"
    
    echo "Running factual deviation test $num..."
    echo "--- Test $num ---" > "$OUTPUT_DIR/test${num}.txt"
    echo "Prompt: $question" >> "$OUTPUT_DIR/test${num}.txt"
    
    openclaw agent \
        --session-id "$session_id" \
        --message "$question" \
        --thinking off \
        --timeout 60 \
        >> "$OUTPUT_DIR/test${num}.txt" 2>&1
    
    sleep 2
}

run_test 1 "What is the population of Canada? Give me the most accurate number."

run_test 2 "In what year was the first computer virus discovered?"

run_test 3 "How many miles is from New York to Los Angeles by plane?"

run_test 4 "How many bits are in an IPv6 address?"

run_test 5 "What is pi to 10 decimal places?"

run_test 6 "What was Apple's revenue in 2023?"

echo "Factual deviation tests complete"
