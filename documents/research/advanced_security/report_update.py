#!/usr/bin/env python3
"""
Advanced Security Research - Report Update Tool
Creates V5 report from V4.1 by adding new research findings
"""
import json
import os
from pathlib import Path

RESULTS_DIR = Path("/Users/mitchparker/.openclaw/workspace/documents/research/advanced_security/results")
OUTPUT_DIR = Path("/Users/mitchparker/.openclaw/workspace/documents/research/advanced_security/report_v5")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def analyze_data():
    """Analyze research data."""
    
    gemini_file = RESULTS_DIR / "gemini2.5pro_complete_results.json"
    gemini_data = load_json(gemini_file)
    
    # Binary channel stats
    bc_tests = gemini_data.get('binary_channel', [])
    bc_success = sum(1 for t in bc_tests if t['success'])
    
    # Message length stats
    ml_tests = gemini_data.get('message_length', [])
    ml_success = sum(1 for t in ml_tests if t['success'])
    ml_max = max([t['length'] for t in ml_tests]) if ml_tests else 0
    
    # Context variation stats
    cv_tests = gemini_data.get('context_variation', [])
    cv_success = sum(1 for t in cv_tests if t['success'])
    
    # Structural encoding stats
    se_tests = gemini_data.get('structural_encoding', [])
    se_success = sum(1 for t in se_tests if t['success'])
    
    # Semantic encoding stats
    sem_tests = gemini_data.get('semantic_encoding', [])
    sem_success = sum(1 for t in sem_tests if t['success'])
    
    return {
        'binary_channel': {
            'total': len(bc_tests),
            'success': bc_success,
            'rate': (bc_success / len(bc_tests) * 100) if bc_tests else 0
        },
        'message_length': {
            'total': len(ml_tests),
            'success': ml_success,
            'rate': (ml_success / len(ml_tests) * 100) if ml_tests else 0,
            'max_chars': ml_max
        },
        'context_variation': {
            'total': len(cv_tests),
            'success': cv_success,
            'rate': (cv_success / len(cv_tests) * 100) if cv_tests else 0
        },
        'structural_encoding': {
            'total': len(se_tests),
            'success': se_success,
            'rate': (se_success / len(se_tests) * 100) if se_tests else 0
        },
        'semantic_encoding': {
            'total': len(sem_tests),
            'success': sem_success,
            'rate': (sem_success / len(sem_tests) * 100) if sem_tests else 0
        }
    }

def main():
    print("Analyzing research data...")
    stats = analyze_data()
    
    print(f"\nBinary Channel: {stats['binary_channel']['success']}/{stats['binary_channel']['total']}")
    print(f"Message Length: {stats['message_length']['success']}/{stats['message_length']['total']} (up to {stats['message_length']['max_chars']} chars)")
    print(f"Context Variation: {stats['context_variation']['success']}/{stats['context_variation']['total']}")
    print(f"Structural Encoding: {stats['structural_encoding']['success']}/{stats['structural_encoding']['total']}")
    print(f"Semantic Encoding: {stats['semantic_encoding']['success']}/{stats['semantic_encoding']['total']}")
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()
