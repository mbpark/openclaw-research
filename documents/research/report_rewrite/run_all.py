#!/usr/bin/env python3
"""
Master orchestrator for report rewrite project.
Runs all steps with checkpointing.
"""
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

STEPS = [
    ("Step 1: Extract data", "step1_extract_data.py"),
    ("Step 2: Create comparison sections", "step2_comparison_sections.py"),
    ("Step 3: Assemble v3 report", "step3_assemble_v3_report.py"),
    ("Step 4: Generate Anthropic review", "step4_generate_review.py"),
    ("Step 5: Remediate based on review", "step5_remediate.py"),
    ("Step 6: Create presentation", "step6_create_presentation.py"),
]

DATA_DIR = Path("data")
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

log = open(LOG_DIR / f"master_{datetime.now().strftime('%H%M')}.log", "w")

def logf(msg, *args):
    msg = msg % args if args else msg
    print(msg)
    log.write(msg + "\n")
    log.flush()

def checkpoint_exists(step_num):
    """Check if a step has been completed."""
    cp = DATA_DIR / f"checkpoint_{step_num}.json"
    if cp.exists():
        with open(cp) as f:
            data = json.load(f)
            return data.get('completed', False)
    return False

def run_step(step_num, description, script):
    """Run a single step."""
    logf("\n" + "="*70)
    logf(f"Running {description}")
    logf(f"Script: {script}")
    logf("="*70)
    
    if checkpoint_exists(step_num):
        logf("✓ Step already completed (checkpoint found)")
        return True
    
    try:
        result = subprocess.run(
            ["python3", script],
            capture_output=False
        )
        
        if result.returncode == 0:
            logf(f"✓ Step {step_num} completed successfully")
            return True
        else:
            logf(f"✗ Step {step_num} failed with exit code {result.returncode}")
            return False
    except Exception as e:
        logf(f"✗ Step {step_num} error: {str(e)}")
        return False

def main():
    logf("="*70)
    logf("Report Rewrite Project - Master Orchestrator")
    logf(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logf("="*70)
    
    # Determine where to resume
    resume_from = 1
    for i, (desc, script) in enumerate(STEPS, 1):
        if not checkpoint_exists(i):
            resume_from = i
            break
    
    if resume_from > 1:
        logf(f"Resuming from step {resume_from}")
    
    # Run each step
    for i, (description, script) in enumerate(STEPS, 1):
        if i < resume_from:
            continue
            
        if not run_step(i, description, script):
            logf(f"\n✗ Project paused at step {i}.")
            logf(f"To continue: python3 run_all.py --resume")
            return False
    
    logf("\n" + "="*70)
    logf("✅ All steps completed successfully!")
    logf(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logf("="*70)
    logf("\nGenerated files:")
    logf("- Report: comprehensive_report_v3_unified.md")
    logf("- Review: review/anthropic_review.md")
    logf("- Presentation: slides/executive_presentation.md")
    
    return True

if __name__ == "__main__":
    main()
