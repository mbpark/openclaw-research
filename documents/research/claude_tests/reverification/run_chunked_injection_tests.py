#!/usr/bin/env python3
"""
Chunked Prompt Injection Test Runner

Runs 70 injection tests in small batches (default 5) to avoid timeouts.
Supports resuming from interruptions.

Usage:
  python3 run_chunked_injection_tests.py                    # Run all 70 tests
  python3 run_chunked_injection_tests.py --sample 20        # Run small 20-test sample
  python3 run_chunked_injection_tests.py --batch 3          # 3 tests per batch
  python3 run_chunked_injection_tests.py --continue         # Continue from last batch
"""
import argparse
import json
import time
import logging
from pathlib import Path
from datetime import datetime

from common import (
    get_client, logger, ProgressTracker,
    run_api_test_chunked
)
from test_vectors import INJECTION_VECTORS, get_vectors_for_sample

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(module)s] %(message)s"
)

DEFAULT_MODEL = "claude-opus-4-8"
BASE_DIR = Path(__file__).parent.parent


def main():
    parser = argparse.ArgumentParser(description="Chunked prompt injection test runner")
    parser.add_argument("--sample", type=int, help="Run small sample (10-70 tests)")
    parser.add_argument("--batch", type=int, default=5, help="Tests per batch (default 5)")
    parser.add_argument("--continue-run", action="store_true", help="Continue from last batch")
    parser.add_argument("--category", help="Only run tests for specific category")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Claude model to use")
    parser.add_argument("--outdir", type=str, help="Output directory")
    
    args = parser.parse_args()
    
    # Setup paths
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = f"_sample_{args.sample}" if args.sample else ""
    outdir = Path(args.outdir) if args.outdir else BASE_DIR / "claude_results" / f"injection_reverification_{timestamp}{suffix}"
    progress_file = outdir / "progress.json"
    
    # Select test vectors
    if args.sample:
        vectors = get_vectors_for_sample(args.sample)
        logger.info(f"Selected {len(vectors)} tests for sample")
    else:
        vectors = list(INJECTION_VECTORS)
    
    if args.category:
        vectors = [v for v in vectors if v[2] == args.category]
        logger.info(f"Filtered to {len(vectors)} tests in {args.category}")
    
    # Create client and tracker
    client = get_client()
    tracker = ProgressTracker(progress_file)
    
    # Skip already completed if continuing
    if args.continue_run or tracker.completed:
        vectors = [v for v in vectors if v[0] not in tracker.completed]
        logger.info(f"Resuming: {len(vectors)} tests remaining")
    
    # Convert to (id, name, prompt) tuples for API
    api_tests = [(v[0], v[1], v[3]) for v in vectors]
    
    # Run in chunks
    logger.info(f"Starting {len(api_tests)} injection tests in batches of {args.batch}")
    logger.info(f"Output: {outdir}")
    
    results = run_api_test_chunked(
        client=client,
        model=args.model,
        tests=api_tests,
        batch_size=args.batch,
        results_dir=outdir,
        progress_file=progress_file,
    )
    
    # Save summary
    summary = {
        "test_type": "prompt_injection",
        "model": args.model,
        "start_time": datetime.now().isoformat(),
        "total_tests": len(vectors),
        "completed": len([r for r in results if r.status == "completed"]),
        "failed": len([r for r in results if r.status == "error"]),
        "batch_size": args.batch,
        "output_dir": str(outdir)
    }
    
    with open(outdir / "summary.json", 'w') as f:
        json.dump(summary, indent=2, fp=f)
    
    logger.info(f"\nCompleted!")
    logger.info(f"  Total: {len(vectors)}")
    logger.info(f"  Completed: {len([r for r in results if r.status == 'completed'])}")
    logger.info(f"  Failed: {len([r for r in results if r.status == 'error'])}")
    logger.info(f"  Output: {outdir}")


if __name__ == "__main__":
    main()
