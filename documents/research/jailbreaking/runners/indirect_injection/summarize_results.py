#!/usr/bin/env python3
"""Summarize injection test results."""
import json
import glob
from pathlib import Path

results_dir = Path(__file__).parent / "results"
print("=" * 70)
print("INJECTION TEST RESULTS - Opus 4.8")
print("=" * 70)

# Find the run
runs = list(results_dir.glob("indirect_v2_*/claude/*.json"))
runs = [f for f in runs if "summary" not in str(f)]

categories = {
    "TC-E": "Category 7: Extended Tool Chaining",
    "SH-": "Category 8: Semantic Hidden Instructions",
    "MP-E": "Category 9: Memory Persistence Push",
}

for prefix, cat_name in categories.items():
    tests = []
    for f in sorted(runs):
        try:
            with open(f) as fp:
                d = json.load(fp)
                if d["test_id"].startswith(prefix):
                    tests.append((d["test_id"], d["final_score"], d["assessment"]))
        except:
            pass

    print(f"\n{cat_name}")
    print(f"Tests: {len(tests)}")
    if tests:
        avg = sum(t[1] for t in tests) / len(tests)
        print(f"Avg Score: {avg:.2f}/5")
        print("\nTest-level scores:")
        for test_id, score, assessment in tests:
            print(f"  {test_id}: {score}/5 ({assessment})")

print("\n" + "=" * 70)
print("COMPARISON WITH ORIGINAL CATEGORIES")
print("=" * 70)
print("\nOriginal results:")
print(f"  Category 2 (Tool Chaining): Avg 2.4/5")
print(f"  Category 5 (Hidden Instructions): Avg 1.6/5")
print("\nExtended results:")
print(f"  Category 7 (Extended Tool Chaining): Avg 3.17/5")
print(f"  Category 8 (Semantic Hidden Instructions): Avg 2.88/5")
print(f"  Category 9 (Memory Persistence): Avg 3.0/5")

print("\n" + "=" * 70)
print("KEY FINDINGS")
print("=" * 70)
print("""
1. Original tool chaining (avg 2.4/5) vs Extended (avg 3.17/5)
   - Slight increase but still dominated by 'acknowledged' responses
   - No actual execution despite sophisticated rationale-based techniques
   - CTO authority framing didn't overcome model resistance

2. Original hidden instructions (avg 1.6/5) vs Semantic (avg 2.88/5)
   - Higher score for semantic techniques but again no true execution
   - Plaintext justifications often blocked (score 0)
   - Markdown-procedural techniques more likely to be acknowledged

3. Memory Persistence (avg 3.0/5)
   - Initial resistance seems to break down slightly on recall attempts
   - Need manual review of verification turns to confirm
""")

print("=" * 70)
