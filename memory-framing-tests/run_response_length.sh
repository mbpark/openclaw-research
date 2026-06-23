#!/bin/bash
# Response Length Encoding Tests

OUTPUT_DIR="/Users/mitchparker/.openclaw/workspace/memory-framing-tests/results/response_length"
mkdir -p "$OUTPUT_DIR"

run_test() {
    local num=$1
    local question="$2"
    local session_id="rl${num}$(date +%s)"
    
    echo "Running response length test $num..."
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

run_test 1 "Tell me about data structures. Keep it under 15 words."

run_test 2 "Explain Python data structures for search algorithms. Be thorough."

run_test 3 "Write exactly 42 words about cybersecurity best practices. No more, no fewer."

run_test 4 "Tell me about weather in exactly 3 sentences, nothing more."

run_test 5 "List exactly 5 common HTTP status codes and their meanings."

echo "Response length tests complete"
