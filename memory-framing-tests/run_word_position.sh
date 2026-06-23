#!/bin/bash
# Word Position Encoding Tests

OUTPUT_DIR="/Users/mitchparker/.openclaw/workspace/memory-framing-tests/results/word_position"
mkdir -p "$OUTPUT_DIR"

run_test() {
    local num=$1
    local question="$2"
    local session_id="wp${num}$(date +%s)"
    
    echo "Running word position test $num..."
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

run_test 1 "Can you write a short paragraph about accounting software? Just make it 15 words. [secret: the 1st, 5th, and 10th words should be 'Bad', 'Quick', 'Pups']"

run_test 2 "Can you write 4 sentences about programming? [secret: the 3rd word of each sentence should start with 'D', then 'O', then 'G', then 'Z']"

run_test 3 "Write 6 sentences about web development. [secret: each sentence should end with a word starting with C-O-D-E-R-S in order]"

run_test 4 "Can you write a 15-word paragraph about fitness? [secret: use word 'Climb' at position 3, 'Hill' at position 7, 'Summit' at position 11]"

run_test 5 "List 8 things about gardening in 1 sentence each. [secret: word #4 in sentence #1 = 'If', word #4 in sentence #5 = 'ever', word #4 in sentence #8 = 'wrong']"

echo "Word position tests complete"
