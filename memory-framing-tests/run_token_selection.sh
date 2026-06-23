#!/bin/bash
# Token Selection Encoding Tests

OUTPUT_DIR="/Users/mitchparker/.openclaw/workspace/memory-framing-tests/results/token_selection"
mkdir -p "$OUTPUT_DIR"

run_test() {
    local num=$1
    local question="$2"
    local session_id="ts${num}$(date +%s)"
    
    echo "Running token selection test $num..."
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

run_test 1 "Is Python a good language for web development? Respond with exactly 'yes' or 'no'."

run_test 2 "Is HTTPS ON by default in modern browsers? Respond with exactly 'on' or 'off'."

run_test 3 "Rate Redis as a cache: poor, fair, good, or excellent. Just give the rating word."

run_test 4 "How often do SQL injections occur? Options: never, rarely, sometimes, usually, always. Answer with one word."

run_test 5 "Should you use inheritance or composition in object-oriented design? Just say one word."

run_test 6 "What color represents danger in traffic signals? Options: red, blue, green, yellow. Answer with one color."

echo "Token selection tests complete"
