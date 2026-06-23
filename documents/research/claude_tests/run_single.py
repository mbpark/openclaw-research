#!/usr/bin/env python3
"""Run a single Claude test from a markdown file."""
import subprocess
import sys
from pathlib import Path
import os

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 run_single.py <prompt_file.md> <output_file.md>")
        sys.exit(1)
    
    prompt_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    prompt_content = prompt_path.read_text()
    
    result = subprocess.run(
        ["claude", "-p", prompt_content],
        capture_output=True,
        text=True,
        timeout=180
    )
    
    output_path.write_text(result.stdout)
    print(f"Done - {result.stdout[:100]}...")
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    main()
