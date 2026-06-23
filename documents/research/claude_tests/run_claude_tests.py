#!/usr/bin/env python3
"""Run Claude tests from the implementation test suite.

Usage: python3 run_claude_tests.py [task_numbers]

Examples:
  python3 run_claude_tests.py          # Run all tasks
  python3 run_claude_tests.py 1         # Run task 1 only
  python3 run_claude_tests.py 1,2,3     # Run tasks 1-3
  python3 run_claude_tests.py 1,4,7     # Run specific tasks
"""
import anthropic
import re
import sys
from pathlib import Path

# Load API key from workspace .env
dotenv_path = Path(__file__).parent.parent.parent.parent / '.env'
api_key = None
for line in open(dotenv_path).readlines():
    if line.startswith('ANTHROPIC_API_KEY'):
        api_key = line.split('=', 1)[1].strip()
        break

MODEL = "claude-opus-4-8"
SUITE_PATH = Path(__file__).parent.parent / "implementation_test_suite.md"
RESULTS_DIR = Path(__file__).parent / "claude_results"
client = anthropic.Anthropic(api_key=api_key)


def extract_tasks(path):
    content = path.read_text()
    tasks = []
    lines = content.split('\n')

    tasks_info = []
    current_category = "Unknown"
    for i, line in enumerate(lines):
        if line.startswith('# Category'):
            current_category = line.strip()
        if re.match(r'^## Task \d+\.\d+', line):
            tasks_info.append((i, line, current_category))

    for num, (start_pos, header, category) in enumerate(tasks_info):
        match = re.match(r'## Task (\d+\.\d+):\s*(.*)', header)
        task_id = match.group(1) if match else f"{num+1:02d}"
        title = match.group(2).strip() if match else header.strip()

        if num + 1 < len(tasks_info):
            end_pos = tasks_info[num + 1][0]
        else:
            end_pos = len(lines)

        body = '\n'.join(lines[start_pos + 1:end_pos])
        tasks.append({
            'num': num + 1,
            'id': task_id,
            'title': title,
            'category': category,
            'content': body.strip()
        })

    return tasks


def run_task(task):
    output_path = RESULTS_DIR / f"task_{task['id']}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists() and output_path.stat().st_size > 100:
        print(f"  (Skipping - already exists)")
        return output_path

    prompt = (
        "You are an expert software engineer completing an implementation challenge.\n\n"
        "Please provide:\n"
        "1. Complete, runnable code with proper type hints and docstrings\n"
        "2. Explanation of design decisions and tradeoffs\n"
        "3. Edge case handling\n\n"
        f"## Task: {task['title']}\n\n"
        f"{task['content']}"
    )

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=16000,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        chunks = []
        for event in message:
            if event.type == 'content_block_delta':
                chunks.append(event.delta.text)
        response = ''.join(chunks)
        output_path.write_text(response)
        return output_path
    except Exception as e:
        output_path.write_text(f"[ERROR: {e}]")
        return output_path


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if ',' in arg:
            task_indices = [int(n.strip()) - 1 for n in arg.split(',')]
        else:
            task_indices = [int(arg) - 1]
    else:
        task_indices = "all"

    tasks = extract_tasks(SUITE_PATH)
    print(f"Extracted {len(tasks)} tasks from suite\n")

    for i, task in enumerate(tasks, 1):
        print(f"{i:3d}. {task['id']:<6} {task['title'][:50]}")

    if task_indices != "all":
        task_indices = [n for n in task_indices if n < len(tasks)]
    else:
        task_indices = range(len(tasks))

    print(f"\nModel: {MODEL}")
    print(f"Running {len(task_indices)} tasks...\n")

    last_category = None
    for idx in task_indices:
        task = tasks[idx]

        # Category checkpoint
        if task['category'] != last_category and last_category is not None:
            print(f"\n--- Checkpoint: Completed {last_category} ---")
            print("Press Ctrl+C to stop and resume later, or wait 10 seconds to continue...")
            import time
            for sec in range(10, 0, -1):
                time.sleep(1)
                print(f"  Continuing in {sec}s... ", end='\r')

        last_category = task['category']

        print(f"\n{'='*70}")
        print(f"Task {idx + 1}/{len(task_indices)}: {task['id']} - {task['title']}")
        print(f"{'='*70}")

        output = run_task(task)
        if output.exists():
            size_kb = output.stat().st_size / 1024
            print(f"Saved to {output} ({size_kb:.1f}KB)")

    print(f"\nRESULTS - {len(task_indices)} tasks completed")
    print(f"All outputs in: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
