#!/usr/bin/env python3
"""
Chunked Implementation Test Runner

Runs implementation tests in small batches (default 2) to avoid timeouts.
Supports resuming from interruptions.

Usage:
  python3 run_chunked_implementation_tests.py                # Run all tasks
  python3 run_chunked_implementation_tests.py --sample 5     # Run small 5-task sample
  python3 run_chunked_implementation_tests.py --batch 1      # 1 task per batch
  python3 run_chunked_implementation_tests.py --continue     # Continue from last batch
  python3 run_chunked_implementation_tests.py --tasks 1,3    # Run specific tasks
"""
import argparse
import json
import time
import logging
from pathlib import Path
from datetime import datetime

import anthropic

from common import get_client, logger, ProgressTracker
from test_vectors import IMPLEMENTATION_CATEGORIES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(module)s] %(message)s"
)

DEFAULT_MODEL = "claude-opus-4-8"
BASE_DIR = Path(__file__).parent.parent
SUITE_PATH = BASE_DIR.parent / "implementation_test_suite.md"


def extract_tasks_from_suite(suite_path: Path) -> list[dict]:
    """Extract implementation tasks from the test suite file."""
    import re
    
    content = suite_path.read_text()
    tasks = []
    lines = content.split('\n')
    
    task_positions = []
    for i, line in enumerate(lines):
        if re.match(r'## Task \d+\.\d+', line):
            match = re.match(r'## Task (\d+\.\d+):\s*(.*)', line)
            task_positions.append((i, match.group(1), match.group(2).strip()))
    
    for i, (start_pos, task_id, title) in enumerate(task_positions):
        if i + 1 < len(task_positions):
            end_pos = task_positions[i + 1][0]
        else:
            end_pos = len(lines)
        
        content = '\n'.join(lines[start_pos + 1:end_pos])
        
        category_num = task_id.split('.')[0]
        category_name = IMPLEMENTATION_CATEGORIES.get(category_num, "Unknown")
        
        tasks.append({
            'id': task_id,
            'title': title,
            'content': content.strip(),
            'category': category_name,
            'category_num': category_num
        })
    
    return tasks


def run_chunked_implementation_tests(
    client: anthropic.Anthropic,
    model: str,
    tasks: list[dict],
    results_dir: Path,
    progress_file: Path,
    batch_size: int = 2,
) -> list[dict]:
    """Run implementation tests in small chunks."""
    
    tracker = ProgressTracker(progress_file)
    results = []
    
    task_chunks = [tasks[i:i + batch_size] for i in range(0, len(tasks), batch_size)]
    
    for chunk_idx, chunk in enumerate(task_chunks):
        logger.info(f"Running implementation batch {chunk_idx + 1} ({len(chunk)} tasks)...")
        
        for task in chunk:
            output_path = results_dir / f"task_{task['id']}.md"
            
            if tracker.is_completed(task['id']) or output_path.exists():
                logger.info(f"  Skipping task {task['id']} (already done)")
                continue
            
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
                tracker.mark_starting(task['id'])
                
                message = client.messages.create(
                    model=model,
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
                
                results.append({
                    'task_id': task['id'],
                    'title': task['title'],
                    'category': task['category'],
                    'status': 'completed',
                    'output_path': str(output_path)
                })
                tracker.mark_completed(task['id'])
                logger.info(f"  Task {task['id']}: {task['title']} - completed")
                
            except Exception as e:
                logger.error(f"  Error on task {task['id']}: {e}")
                results.append({
                    'task_id': task['id'],
                    'title': task['title'],
                    'category': task['category'],
                    'status': 'error',
                    'error': str(e)
                })
                tracker.mark_failed(task['id'], str(e))
            
            time.sleep(1)
        
        logger.info(f"  Batch {chunk_idx + 1} complete")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Chunked implementation test runner")
    parser.add_argument("--sample", type=int, help="Run small sample (1-20 tasks)")
    parser.add_argument("--batch", type=int, default=2, help="Tasks per batch (default 2)")
    parser.add_argument("--continue-run", action="store_true", help="Continue from last batch")
    parser.add_argument("--tasks", help="Specific task IDs to run (comma-separated, e.g., 1,3,5)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Claude model to use")
    parser.add_argument("--outdir", type=str, help="Output directory")
    
    args = parser.parse_args()
    
    # Setup paths
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = f"_sample_{args.sample}" if args.sample else ""
    outdir = Path(args.outdir) if args.outdir else BASE_DIR / "claude_results" / f"implementation_reverification_{timestamp}{suffix}"
    progress_file = outdir / "progress.json"
    
    # Extract tasks
    tasks = extract_tasks_from_suite(SUITE_PATH)
    logger.info(f"Extracted {len(tasks)} implementation tasks from suite")
    
    # Filter tasks
    if args.sample:
        import random
        random.seed(42)
        tasks = random.sample(tasks, min(args.sample, len(tasks)))
    
    if args.tasks:
        task_ids = set(args.tasks.split(','))
        tasks = [t for t in tasks if t['id'].split('.')[0] in task_ids or t['id'] in task_ids]
    
    # Create client
    client = get_client()
    
    # Check for continuation
    outdir.mkdir(parents=True, exist_ok=True)
    
    tracker = ProgressTracker(progress_file)
    if args.continue_run or tracker.completed:
        tasks = [t for t in tasks if t['id'] not in tracker.completed]
        logger.info(f"Resuming: {len(tasks)} tasks remaining")
    
    # Run tests
    logger.info(f"Starting {len(tasks)} implementation tests in batches of {args.batch}")
    
    results = run_chunked_implementation_tests(
        client=client,
        model=args.model,
        tasks=tasks,
        batch_size=args.batch,
        results_dir=outdir,
        progress_file=progress_file,
    )
    
    # Save summary
    summary = {
        "test_type": "implementation_quality",
        "model": args.model,
        "start_time": datetime.now().isoformat(),
        "total_tasks": len(tasks),
        "completed": len([r for r in results if r['status'] == 'completed']),
        "failed": len([r for r in results if r['status'] == 'error']),
        "batch_size": args.batch,
        "output_dir": str(outdir)
    }
    
    with open(outdir / "summary.json", 'w') as f:
        json.dump(summary, indent=2, fp=f)
    
    logger.info(f"\nCompleted!")
    logger.info(f"  Total tasks: {len(tasks)}")
    logger.info(f"  Completed: {len([r for r in results if r['status'] == 'completed'])}")
    logger.info(f"  Failed: {len([r for r in results if r['status'] == 'error'])}")
    logger.info(f"  Output: {outdir}")


if __name__ == "__main__":
    main()
