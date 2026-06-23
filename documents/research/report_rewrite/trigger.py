"""
Trigger script to run all steps for tomorrow.
"""
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def main():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Get API key from command line or environment
    api_key = sys.argv[1] if len(sys.argv) > 1 else ""
    
    if not api_key:
        print("Error: API key not provided")
        return
    
    log = open(log_dir / f"trigger_{datetime.now().strftime('%H%M')}.log", "w")
    
    def logf(msg, *args):
        msg = msg % args if args else msg
        print(msg)
        log.write(msg + "\n")
        log.flush()
    
    # Step 1: Extract data
    logf("Step 1: Extract data...")
    subprocess.run(["python3", "step1_extract_data.py"])
    
    # Step 2: Create comparison sections
    logf("Step 2: Create comparison sections...")
    subprocess.run(["python3", "step2_comparison_sections.py"])
    
    # Step 3: Assemble v3 report
    logf("Step 3: Assemble v3 report...")
    subprocess.run(["python3", "step3_assemble_v3_report.py"])
    
    # Step 4: Anthropic review
    logf("Step 4: Anthropic review...")
    subprocess.run(["python3", "step4_generate_review.py", api_key])
    
    # Step 5: Remediate
    logf("Step 5: Remediate...")
    subprocess.run(["python3", "step5_remediate.py"])
    
    # Step 6: Create presentation
    logf("Step 6: Create presentation...")
    subprocess.run(["python3", "create_presentation.py", api_key])
    
    logf("All tasks complete!")
    log.close()

if __name__ == "__main__":
    main()
