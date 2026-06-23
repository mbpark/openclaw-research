#!/usr/bin/env python3
"""
Re-verification Orchestrator

Runs complete re-verification protocol:
1. Select sample sizes
2. Run test batches
3. Score results
4. Generate comparison report

Usage:
  # Full re-verification
  python3 run_reverification_orchestrator.py
  
  # Quick sample test
  python3 run_reverification_orchestrator.py --fast
  
  # Specific test suite
  python3 run_reverification_orchestrator.py --suite injection --sample 30
"""
import argparse
import json
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [orchestrator] %(message)s"
)
logger = logging.getLogger("reverification")

BASE_DIR = Path(__file__).parent.parent


def run_script(script: str, args: list[str] = None, **kwargs) -> int:
    """Run a re-verification script and return exit code."""
    cmd = ["python3", f"reverification/{script}"]
    if args:
        cmd.extend(args)
    
    print(f"\n  Running: {' '.join(cmd)}")
    print(f"  {'='*60}")
    
    result = subprocess.run(cmd, cwd=BASE_DIR, **kwargs)
    print(f"  {'='*60}")
    return result.returncode


def run_injection_protocol(
    sample_size: int,
    batch_size: int = 5,
    continue_run: bool = False,
    output_dir: Optional[Path] = None
) -> Path:
    """Run complete injection test protocol."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = output_dir or BASE_DIR / "claude_results" / f"injection_verify_{timestamp}"
    
    print(f"\n### INJECTION TEST PROTOCOL")
    print(f"Sample size: {sample_size}")
    print(f"Batch size: {batch_size}")
    print(f"Output: {output_dir}")
    
    # Run tests
    test_args = [
        "--sample", str(sample_size),
        "--batch", str(batch_size),
        "--outdir", str(output_dir / "raw_results")
    ]
    if continue_run:
        test_args.append("--continue")
    
    ret = run_script("run_chunked_injection_tests.py", test_args)
    if ret != 0:
        logger.warning("Injection tests failed, continuing for resumption")
    
    # Score results
    score_args = [
        "--input", str(output_dir / "raw_results"),
        "--batch", str(batch_size),
        "--outdir", str(output_dir / "scores")
    ]
    if continue_run:
        score_args.append("--continue")
    
    ret = run_script("run_batched_scoring.py", score_args)
    
    return output_dir


def run_implementation_protocol(
    sample_size: int,
    batch_size: int = 2,
    continue_run: bool = False,
    output_dir: Optional[Path] = None
) -> Path:
    """Run complete implementation test protocol."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = output_dir or BASE_DIR / "claude_results" / f"implementation_verify_{timestamp}"
    
    print(f"\n### IMPLEMENTATION TEST PROTOCOL")
    print(f"Sample size: {sample_size}")
    print(f"Batch size: {batch_size}")
    print(f"Output: {output_dir}")
    
    # Run tests
    test_args = [
        "--sample", str(sample_size),
        "--batch", str(batch_size),
        "--outdir", str(output_dir / "raw_results")
    ]
    if continue_run:
        test_args.append("--continue")
    
    ret = run_script("run_chunked_implementation_tests.py", test_args)
    if ret != 0:
        logger.warning("Implementation tests failed, continuing for resumption")
    
    # Score results
    score_args = [
        "--input", str(output_dir / "raw_results"),
        "--batch", str(batch_size),
        "--outdir", str(output_dir / "scores")
    ]
    if continue_run:
        score_args.append("--continue")
    
    ret = run_script("run_batched_scoring.py", score_args)
    
    return output_dir


def run_structured_output_protocol(
    sample_size: int,
    batch_size: int = 5,
    continue_run: bool = False,
    output_dir: Optional[Path] = None
) -> Path:
    """Run complete structured output test protocol."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = output_dir or BASE_DIR / "claude_results" / f"structured_verify_{timestamp}"
    
    print(f"\n### STRUCTURED OUTPUT TEST PROTOCOL")
    print(f"Vector sample size: {sample_size}")
    print(f"Total tests: {sample_size * 4}")
    print(f"Batch size: {batch_size}")
    print(f"Output: {output_dir}")
    
    # Run tests
    test_args = [
        "--sample", str(sample_size),
        "--batch", str(batch_size),
        "--outdir", str(output_dir / "raw_results")
    ]
    if continue_run:
        test_args.append("--continue")
    
    ret = run_script("run_chunked_structured_output.py", test_args)
    
    # Score results
    score_args = [
        "--input", str(output_dir / "raw_results"),
        "--batch", str(batch_size),
        "--outdir", str(output_dir / "scores")
    ]
    if continue_run:
        score_args.append("--continue")
    
    ret = run_script("run_batched_scoring.py", score_args)
    
    return output_dir


def generate_summary(protocols: list[dict]) -> None:
    """Generate final summary report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = BASE_DIR / f"reverification_summary_{timestamp}.md"
    
    report = f"""# Re-verification Summary Report

**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Researcher:** Mitch
**Purpose:** Verify previous test results with additional data collection

## Protocols Executed

"""
    
    for protocol in protocols:
        report += f"""### {protocol['name']}

| Parameter | Value |
|-----------|-------|
| Test type | {protocol['type']} |
| Sample size | {protocol['sample_size']} |
| Batches | {protocol['batches']} |
| Output dir | {protocol['output_dir']} |
| Status | {protocol['status']} |

"""
    
    # Add analysis sections
    report += f"""
## Analysis

### Injection Test Comparison
TODO: Add score comparison

### Implementation Quality Comparison
TODO: Add score comparison

### Structured Output Comparison
TODO: Add format effect analysis

## Methodology Notes
- Tests run in batches of {protocols[0]['batch_size'] if protocols else 5} to prevent timeouts
- Random sampling used with fixed seed (42) for reproducibility
- Results saved incrementally for resumption capability

"""
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\nSummary report written to: {report_file}")
    return report_file


def main():
    parser = argparse.ArgumentParser(description="Re-verification orchestrator")
    parser.add_argument("--fast", action="store_true", help="Run fast protocol (smaller samples)")
    parser.add_argument("--suite", choices=["injection", "implementation", "structured", "all"],
                       default="all", help="Which suite to run")
    parser.add_argument("--sample", type=int, help="Override sample size")
    parser.add_argument("--continue-run", action="store_true", help="Continue from previous state")
    parser.add_argument("--outdir", type=str, help="Base output directory")
    
    args = parser.parse_args()
    
    # Configure sample sizes
    base_dir = Path(args.outdir) if args.outdir else Path("reverification_outputs")
    
    if args.fast:
        injection_sample = 20
        implementation_sample = 5
        structured_sample = 15
    else:
        injection_sample = args.sample or 70  # Full suite by default
        implementation_sample = args.sample or 20  # Full suite
        structured_sample = args.sample or 280  # Full matrix
    
    # Track protocols
    protocols = []
    
    if args.suite in ["all", "injection"]:
        output_dir = run_injection_protocol(
            injection_sample,
            continue_run=args.continue_run,
            output_dir=base_dir / "injection"
        )
        protocols.append({
            "name": "Prompt Injection Re-verification",
            "type": "injection",
            "sample_size": injection_sample,
            "output_dir": str(output_dir),
            "batches": injection_sample // 5,
            "status": "completed"
        })
    
    if args.suite in ["all", "implementation"]:
        output_dir = run_implementation_protocol(
            implementation_sample,
            continue_run=args.continue_run,
            output_dir=base_dir / "implementation"
        )
        protocols.append({
            "name": "Implementation Quality Re-verification",
            "type": "implementation",
            "sample_size": implementation_sample,
            "output_dir": str(output_dir),
            "batches": implementation_sample // 2,
            "status": "completed"
        })
    
    if args.suite in ["all", "structured"]:
        output_dir = run_structured_output_protocol(
            structured_sample,
            continue_run=args.continue_run,
            output_dir=base_dir / "structured"
        )
        protocols.append({
            "name": "Structured Output Vulnerability Re-verification",
            "type": "structured_output",
            "sample_size": structured_sample * 4,  # All formats
            "output_dir": str(output_dir),
            "batches": (structured_sample * 4) // 5,
            "status": "completed"
        })
    
    # Generate summary
    generate_summary(protocols)


if __name__ == "__main__":
    main()
