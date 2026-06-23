#!/bin/zsh
# Memory framing tests - direct API calls with curl

API="http://127.0.0.1:8000/v1/chat/completions"
KEY="gr0epaz!"
MODEL="custom-127-0-0-1-8000/Qwen3.6-40B-Claude-4.6-Opus-Deckard-Heretic-Uncensored-Thinking-8bit"
DIR="/Users/mitchparker/.openclaw/workspace/memory-framing-tests/results"

mkdir -p "$DIR"

query() {
    local memory="$1"
    local question="$2"
    local temp=${3:-0.7}
    
    curl -s -X POST "$API" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $KEY" \
      -d "{
        \"model\": \"$MODEL\",
        \"messages\": [
          {\"role\": \"system\", \"content\": \"Answer based only on the memory content. Be specific.\"},
          {\"role\": \"user\", \"content\": \"Memory: $memory\\nQuestion: $question\\nAnswer:\"}
        ],
        \"temperature\": $temp,
        \"max_tokens\": 100
      }" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null || echo "ERROR"
}

echo "# Memory Framing Test Results" > "$DIR/report.md"
echo "Date: $(date)" >> "$DIR/report.md"
echo "" >> "$DIR/report.md"

# TEST A
echo "=== TEST A: Price Framing ==="
MEMORY_A="The product price is \$47 and it's made in Germany"
echo "" >> "$DIR/report.md"
echo "## Test A: Price Framing" >> "$DIR/report.md"
echo "Memory: $MEMORY_A" >> "$DIR/report.md"
echo "" >> "$DIR/report.md"

for i in 1 2 3 4 5; do
    case $i in
        1) Q="What's the price?";;
        2) Q="How much does it cost?";;
        3) Q="Tell me about pricing";;
        4) Q="What details did I give about money?";;
        5) Q="Quote the exact price I mentioned";;
    esac
    
    echo "Q$i: $Q"
    A=$(query "$MEMORY_A" "$Q")
    echo "A$i: $A"
    echo "$A" > "$DIR/a_$i.txt"
    
    echo "**Q$i:** $Q" >> "$DIR/report.md"
    echo "**A:** $A" >> "$DIR/report.md"
    echo "" >> "$DIR/report.md"
    sleep 1
done

# TEST B
echo ""
echo "=== TEST B: Meeting Framing ==="
MEMORY_B="We met last Tuesday at 3pm in room B"
echo "" >> "$DIR/report.md"
echo "## Test B: Meeting Framing" >> "$DIR/report.md"
echo "Memory: $MEMORY_B" >> "$DIR/report.md"
echo "" >> "$DIR/report.md"

for i in 1 2 3 4; do
    case $i in
        1) Q="When and where did we meet?";;
        2) Q="Did we meet in the morning or afternoon?";;
        3) Q="Was the meeting in room A or room B?";;
        4) Q="Tell me about our meeting";;
    esac
    
    echo "Q$i: $Q"
    A=$(query "$MEMORY_B" "$Q")
    echo "A$i: $A"
    echo "$A" > "$DIR/b_$i.txt"
    
    echo "**Q$i:** $Q" >> "$DIR/report.md"
    echo "**A:** $A" >> "$DIR/report.md"
    echo "" >> "$DIR/report.md"
    sleep 1
done

# TEST C
echo ""
echo "=== TEST C: Question Order ==="
MEMORY_C="Revenue was up 12%, employees are 45, customers increased 50"
echo "" >> "$DIR/report.md"
echo "## Test C: Question Order" >> "$DIR/report.md"
echo "Memory: $MEMORY_C" >> "$DIR/report.md"
echo "" >> "$DIR/report.md"

for i in 1 2 3; do
    case $i in
        1) Q="What was revenue change?";;
        2) Q="How many employees? Also, what was the revenue change?";;
        3) Q="Tell me about everything";;
    esac
    
    echo "Q$i: $Q"
    A=$(query "$MEMORY_C" "$Q")
    echo "A$i: $A"
    echo "$A" > "$DIR/c_$i.txt"
    
    echo "**Q$i:** $Q" >> "$DIR/report.md"
    echo "**A:** $A" >> "$DIR/report.md"
    echo "" >> "$DIR/report.md"
    sleep 1
done

echo ""
echo "Tests complete! Results in $DIR/report.md"
