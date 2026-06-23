#!/bin/zsh
#
# Run Claude implementation tests
# Usage: ./run_claude_tests.sh [task_id]   # omit task_id for all
#

SUITE="documents/research/implementation_test_suite.md"
RESULTS_DIR="documents/research/claude_tests/claude_results"
TASK_DIR="$RESULTS_DIR/tasks"
OUTPUT_DIR="$RESULTS_DIR/output"

mkdir -p "$TASK_DIR" "$OUTPUT_DIR"

# Extract tasks from suite
echo "Extracting tasks..."
current_task=""
current_content=""
task_num=0

while IFS= read -r line; do
    if [[ "$line" =~ "^##\ Task\ [0-9]+\.[0-9]+" ]]; then
        if [[ -n "$current_task" ]]; then
            task_num=$((task_num + 1))
            echo "$current_task" > "$TASK_DIR/task_${task_num}.md"
            echo "  Task $task_num: $current_task"
        fi
        current_task="$line"
        current_content="$line\n"
    else
        current_content+="$line\n"
    fi
done < "$SUITE"

# Save last task
if [[ -n "$current_task" ]]; then
    task_num=$((task_num + 1))
    echo "$current_task" > "$TASK_DIR/task_${task_num}.md"
    echo "  Task $task_num: $current_task"
fi

echo "\nExtracted $task_num tasks"

# Show tasks
echo -e "\nAvailable tasks:"
for i in $(seq 1 $task_num); do
    title=$(head -1 "$TASK_DIR/task_${i}.md")
    echo "  $i. $title"
done

# Determine which task(s) to run
if [[ -n "$1" ]]; then
    echo -e "\nRunning task $1..."
    echo "" > "$OUTPUT_DIR/task_${1}.md"
    claude -p "$(cat "$TASK_DIR/task_${1}.md")" --print > "$OUTPUT_DIR/task_${1}.md"
    echo "Done. Output: $OUTPUT_DIR/task_${1}.md"
else
    # Run all tasks
    echo -e "\nRunning ALL tasks..."
    for i in $(seq 1 $task_num); do
        echo -e "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Task $i/$task_num"
        head -1 "$TASK_DIR/task_${i}.md"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "" > "$OUTPUT_DIR/task_${i}.md"
        claude -p "$(cat "$TASK_DIR/task_${i}.md")" --print > "$OUTPUT_DIR/task_${i}.md"
        echo "✓ Done - $OUTPUT_DIR/task_${i}.md"
        sleep 2
    done
    echo -e "\n🎉 All tasks complete!"
    echo "Results in: $OUTPUT_DIR/"
fi
