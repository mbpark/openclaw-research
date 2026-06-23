#!/usr/bin/env python3
"""
Two-Agent Goal Conflict Runner

Tests how agents handle situations where:
1. Human gives competing instructions
2. Other agent suggests conflicting approach
3. Agents have different objectives
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

import anthropic


class ConflictType(Enum):
    DIRECT_OPPOSITION = "direct_opposition"
    COMPETING_PRIORITIES = "competing_priorities"
    INFORMATION_DISCREPANCY = "information_discrepancy"
    CONSTRAINT_VIOLATION = "constraint_violation"


class BehavioralCode(Enum):
    H = "defers_to_human"
    P = "defers_to_peer"
    S = "synthesizes"
    R = "refuses"
    Q = "questions"
    I = "ignores_peer"


@dataclass
class ConflictResult:
    """Result from a goal conflict test."""
    test_id: str
    conflict_type: ConflictType
    agent1_model: str
    agent2_model: str
    scenario_description: str
    agent1_task: str
    agent2_task: str
    agent1_response: str
    agent2_response: str
    agent2_behavioral_code: Optional[BehavioralCode]
    agent2_reasoning_quality: Optional[int]  # 1-5 scale
    timestamp: float


class ConflictRunner:
    """Runner for two-agent goal conflict tests."""
    
    def __init__(self, api_key: str, save_dir: str = "results"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = self.client.messages
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.test_counter = 0
        
    def run_conflict_test(
        self,
        agent1_model: str,
        agent2_model: str,
        scenario: dict
    ) -> ConflictResult:
        """
        Execute a goal conflict test.
        
        Scenario should contain:
            - type: ConflictType
            - agent1_task: What Agent 1 should do
            - agent2_task: What Agent 2 should do (with potential conflict)
            - description: Human-readable scenario
        """
        self.test_counter += 1
        test_id = f"conflict_test_{self.test_counter:04d}_{datetime.now().strftime('%H%M%S')}"
        
        print(f"\nRunning conflict test {test_id}")
        print(f"  Agent 1: {agent1_model}")
        print(f"  Agent 2: {agent2_model}")
        print(f"  Scenario: {scenario['description']}")
        print(f"  Type: {scenario['type']}")
        
        # Agent 1 responds
        print("  Agent 1 responding...")
        agent1_response = self._call_agent(agent1_model, scenario["agent1_task"])
        
        # Agent 2 responds to human instruction with Agent 1's suggestion visible
        print("  Agent 2 responding...")
        agent2_task_with_context = scenario["agent2_task"]
        agent2_response = self._call_agent(agent2_model, agent2_task_with_context)
        
        result = ConflictResult(
            test_id=test_id,
            conflict_type=ConflictType(scenario["type"]),
            agent1_model=agent1_model,
            agent2_model=agent2_model,
            scenario_description=scenario["description"],
            agent1_task=scenario["agent1_task"],
            agent2_task=scenario["agent2_task"],
            agent1_response=agent1_response,
            agent2_response=agent2_response,
            agent2_behavioral_code=None,  # Human scored later
            agent2_reasoning_quality=None,  # Human scored later
            timestamp=time.time()
        )
        
        self._save_result(result)
        return result
        
    def _call_agent(self, model: str, prompt: str) -> str:
        """Call a single agent."""
        try:
            response = self.model.create(
                model=model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],

            )
            return response.content[0].text
        except Exception as e:
            print(f"Error calling {model}: {e}")
            return f"[ERROR: {str(e)}]"
            
    def _save_result(self, result: ConflictResult):
        """Save conflict test result."""
        result_data = {
            "test_id": result.test_id,
            "conflict_type": result.conflict_type.value,
            "agent1_model": result.agent1_model,
            "agent2_model": result.agent2_model,
            "scenario_description": result.scenario_description,
            "agent1_task": result.agent1_task,
            "agent2_task": result.agent2_task,
            "agent1_response": result.agent1_response,
            "agent2_response": result.agent2_response,
            "agent2_behavioral_code": result.agent2_behavioral_code.value if result.agent2_behavioral_code else None,
            "agent2_reasoning_quality": result.agent2_reasoning_quality,
            "timestamp": result.timestamp
        }
        
        filepath = self.save_dir / f"{result.test_id}.json"
        with open(filepath, 'w') as f:
            json.dump(result_data, f, indent=2)
        print(f"  Saved to {filepath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run goal conflict tests")
    parser.add_argument("--api-key", help="Anthropic API key")
    parser.add_argument("--scenarios-file", required=True, help="JSON file with scenarios")
    parser.add_argument("--save-dir", default="results", help="Save directory")
    
    args = parser.parse_args()
    
    api_key = args.api_key or Path("api_key.txt").read_text().strip()
    runner = ConflictRunner(api_key, args.save_dir)
    
    with open(args.scenarios_file) as f:
        scenarios = json.load(f)
    
    for i, scenario in enumerate(scenarios):
        runner.run_conflict_test(
            agent1_model=scenario.get("agent1_model", "claude-opus-4-8"),
            agent2_model=scenario.get("agent2_model", "claude-sonnet-4-8"),
            scenario=scenario
        )
