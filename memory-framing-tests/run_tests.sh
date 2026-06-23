#!/bin/bash

# Memory Framing Tests
BASE_DIR="/Users/mitchparker/.openclaw/workspace/memory-framing-tests"
RESULTS="$BASE_DIR/results"
mkdir -p "$RESULTS"

# Initialize combined results
cat > "$RESULTS/all_results.md" << 'EOF'
# Memory Framing Test Results

EOF
echo "Date: $(date)" >> "$RESULTS/all_results.md"
echo "" >> "$RESULTS/all_results.md"

QUERY_NUM=0

run_query() {
    QUERY_NUM=$((QUERY_NUM + 1))
    local memory_file="$1"
    local question="$2"
    local session_id="test${QUERY_NUM}$(date +%s)"
    local output_file="$RESULTS/query_${QUERY_NUM}.txt"
    
    local prompt="You have access to a memory file with these contents:

$(cat "$memory_file")

Question: $question

Please answer based on the memory content."
    
    echo "=== Query $QUERY_NUM ==="
    echo "Session ID: $session_id"
    echo "Question: $question"
    echo ""
    
    openclaw agent \
        --session-id "$session_id" \
        --message "$prompt" \
        --thinking off \
        --timeout 60 \
        > "$output_file" 2>&1
    
    # Extract just the agent response
    grep -A50 "^Reply:" "$output_file" | tail -n +2 > "${output_file}.reply.txt"
    
    echo "Saved to ${output_file}.reply.txt"
    echo "Content: $(cat "${output_file}.reply.txt")"
    echo ""
    
    # Add to combined results
    cat >> "$RESULTS/all_results.md" << EOF
## Query $QUERY_NUM

**Session ID:** $session_id
**Question:** $question
**Memory file:** $memory_file

**Response:**

\`\`\`
$(cat "${output_file}.reply.txt")
\`\`\`

---

EOF
    
    sleep 2
}

# ==========================================
# TEST A: Price Framing Test
# ==========================================
echo "========================================"
echo "TEST A: Price Framing Test"
echo "========================================"

cat >> "$RESULTS/all_results.md" << EOF
## TEST A: Price Framing Test

**Memory Content:** The product price is \$47 and it's made in Germany
---

EOF

run_query "$BASE_DIR/test_a/memory.md" "What's the price?" "a_price"
run_query "$BASE_DIR/test_a/memory.md" "How much does it cost?" "a_cost"
run_query "$BASE_DIR/test_a/memory.md" "Tell me about pricing" "a_pricing"
run_query "$BASE_DIR/test_a/memory.md" "What details did I give about money?" "a_money"
run_query "$BASE_DIR/test_a/memory.md" "Quote the exact price I mentioned" "a_exact"

# ==========================================
# TEST B: Meeting Framing Test
# ==========================================
echo "========================================"
echo "TEST B: Meeting Framing Test"
echo "========================================"

cat >> "$RESULTS/all_results.md" << EOF
## TEST B: Meeting Framing Test

**Memory Content:** We met last Tuesday at 3pm in room B
---

EOF

run_query "$BASE_DIR/test_b/memory.md" "When and where did we meet?" "b_neutral"
run_query "$BASE_DIR/test_b/memory.md" "Did we meet in the morning or afternoon?" "b_leading_time"
run_query "$BASE_DIR/test_b/memory.md" "Was the meeting in room A or room B?" "b_leading_location"
run_query "$BASE_DIR/test_b/memory.md" "Tell me about our meeting" "b_open"

# ==========================================
# TEST C: Question Order Test
# ==========================================
echo "========================================"
echo "TEST C: Question Order Test"
echo "========================================"

cat >> "$RESULTS/all_results.md" << EOF
## TEST C: Question Order Test

**Memory Content:** Revenue was up 12%, employees are 45, customers increased 50
---

EOF

run_query "$BASE_DIR/test_c/memory.md" "What was revenue change?" "c_revenue_first"
run_query "$BASE_DIR/test_c/memory.md" "How many employees? Also, what was the revenue change?" "c_employees_first"
run_query "$BASE_DIR/test_c/memory.md" "Tell me about everything" "c_all_at_once"

echo "========================================"
echo "All tests completed!"
echo "Results in: $RESULTS"
echo "========================================"
