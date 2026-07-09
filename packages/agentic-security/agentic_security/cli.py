#!/usr/bin/env python3
"""Agentic Security Command Line Interface."""

import argparse
import sys
from pathlib import Path
from .agentic_workflow_graph_controller import WorkflowGraphController
from .agentjacking_simulator import AgentjackingSimulator
from .agentjacking_defense_framework import AgentjackingDefenseFramework

def main():
    parser = argparse.ArgumentParser(description='Agentic Security - Defense Framework for Agentjacking Attacks')
    parser.add_argument('mode', choices=['validate', 'test', 'scan', 'simulate'], help='Operation mode')
    parser.add_argument('input', help='Input JSON intent or file path')
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'validate':
            controller = WorkflowGraphController.from_config(args.config) if args.config else WorkflowGraphController()
            result = controller.validate_input(args.input)
            output_result(result, args.json, args.verbose)
            
        elif args.mode == 'test':
            controller = WorkflowGraphController.from_config(args.config) if args.config else WorkflowGraphController()
            results = controller.run_tests()
            output_test_results(results, args.json, args.verbose)
            
        elif args.mode == 'scan':
            scanner = AgentjackingDefenseFramework()
            scan_result = scanner.scan_environment()
            output_scan_results(scan_result, args.json, args.verbose)
            
        elif args.mode == 'simulate':
            simulator = AgentjackingSimulator()
            simulation = simulator.run_attack_scenarios(args.input)
            output_simulation_results(simulation, args.json, args.verbose)
            
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
            status = "VALID" if result.get('is_valid', True) else "INVALID"
            print(f"Validation Status: {status}")

def output_test_results(results, json_output, verbose):
    """Output test results."""
    if json_output:
        import json
        print(json.dumps(results, indent=2))
    else:
        print(f"Test Results: {len(results['tests'])} tests run")
        print(f"Success Rate: {results['summary']['success_rate']}")
        print(f"Blocked: {results['summary']['blocked']}")

def output_scan_results(scan_result, json_output, verbose):
    """Output environment scan results."""
    if json_output:
        import json
        print(json.dumps(scan_result, indent=2))
    else:
        print(f"Environment Scan Complete")
        print(f"Threats Found: {scan_result['threats_found']}")
        print(f"Vulnerabilities: {scan_result['vulnerabilities']}")
        print(f"Security Score: {scan_result['security_score']}")

def output_simulation_results(simulation, json_output, verbose):
    """Output simulation results."""
    if json_output:
        import json
        print(json.dumps(simulation, indent=2))
    else:
        print(f"Attack Simulation Results")
        print(f"Attack Scenarios: {len(simulation['scenarios'])}")
        print(f"Successful Attacks: {simulation['successful']}")
        print(f"Blocked Attacks: {simulation['blocked']}")

if __name__ == '__main__':
    main()
