#!/usr/bin/env python3
"""VLMGuard Command Line Interface."""

import argparse
import sys
from pathlib import Path
from .vlmguard_integrated_full import VLMGuard
from .vlmguard_r1_enhanced_intent_analyzer import EnhancedIntentAnalyzer
from .vlmguard_r1_prompt_rewriter import PromptRewriter

def main():
    parser = argparse.ArgumentParser(description='VLMGuard - Visual Prompt Injection Defense System')
    parser.add_argument('mode', choices=['scan', 'analyze', 'rewrite', 'test'], help='Operation mode')
    parser.add_argument('input', help='Input text or file path')
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--threshold', '-t', type=float, default=0.7, help='Detection threshold')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    try:
        # Initialize VLMGuard
        vlmguard = VLMGuard.from_config(args.config) if args.config else VLMGuard()
        
        # Read input
        input_path = Path(args.input)
        if input_path.exists():
            with open(input_path, 'r') as f:
                input_text = f.read()
        else:
            input_text = args.input
        
        if args.mode == 'scan':
            result = vlmguard.scan(input_text)
            output_result(result, args.json, args.verbose)
            
        elif args.mode == 'analyze':
            analyzer = EnhancedIntentAnalyzer()
            analysis = analyzer.analyze(input_text)
            output_result(analysis, args.json, args.verbose)
            
        elif args.mode == 'rewrite':
            rewriter = PromptRewriter()
            rewritten = rewriter.rewrite(input_text)
            print(rewritten)
            
        elif args.mode == 'test':
            results = vlmguard.test()
            output_test_results(results, args.json, args.verbose)
            
    except Exception as e:
        if args.verbose:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def output_result(result, json_output, verbose):
    """Output result in appropriate format."""
    if json_output:
        import json
        print(json.dumps(result, indent=2))
    else:
        if verbose:
            for key, value in result.items():
                print(f"{key}: {value}")
        else:
            status = "SAFE" if result.get('is_safe', True) else "BLOCKED"
            print(f"Status: {status}")
            if 'reason' in result:
                print(f"Reason: {result['reason']}")

def output_test_results(results, json_output, verbose):
    """Output test results."""
    if json_output:
        import json
        print(json.dumps(results, indent=2))
    else:
        print(f"Test Results: {len(results['tests'])} tests run")
        print(f"Success Rate: {results['summary']['success_rate']}")
        print(f"Failures: {results['summary']['failures']}")
        
        if verbose:
            for test in results['tests']:
                status = "PASS" if test['passed'] else "FAIL"
                print(f"[{status}] {test['name']}")

if __name__ == '__main__':
    main()
