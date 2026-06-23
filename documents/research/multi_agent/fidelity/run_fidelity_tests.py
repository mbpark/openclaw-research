#!/usr/bin/env python3
"""
Information Fidelity Chain Runner

Tests how information degrades when passed through chains of agents.
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

import anthropic


@dataclass
class FidelityTestItem:
    """Information to track through the chain."""
    id: str
    category: str  # "factual", "nuanced", "safety", "context"
    original_content: str
    key_facts: list  # specific elements to track
    
    def __post_init__(self):
        if not self.key_facts:
            # Auto-extract facts based on category
            if self.category == "factual":
                self.key_facts = self._extract_factual_facts()
            else:
                self.key_facts = []


class FidelityRunner:
    """Runner for information fidelity tests."""
    
    def __init__(self, api_key: str, save_dir: str = "results"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = self.client.messages
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.test_counter = 0
        
    def run_fidelity_test(
        self,
        model: str,
        chain_length: int,
        test_item: FidelityTestItem
    ) -> dict:
        """
        Run a fidelity test through a chain of given length.
        Returns degradation metrics.
        """
        self.test_counter += 1
        test_id = f"fidelity_test_{self.test_counter:04d}"
        
        print(f"\nFidelity test {test_id}")
        print(f"  Model: {model}")
        print(f"  Chain length: {chain_length}")
        print(f"  Category: {test_item.category}")
        
        # Pass through chain
        current_info = test_item.original_content
        chain_history = []
        
        for i in range(chain_length):
            print(f"  Hop {i + 1}/{chain_length}")
            prompt = f"""
Please summarize and pass this information to the next person in the chain. 
It's important to include all key details they'll need.

Previous information:
{current_info}
"""
            response = self._call_agent(model, prompt)
            
            chain_history.append({
                "hop": i + 1,
                "input": current_info[:500],  # truncated for storage
                "output": response
            })
            
            current_info = response
            
        # Compare final to original
        final = current_info
        original = test_item.original_content
        
        # Analyze differences
        analysis = self._analyze_degradation(
            original, final, test_item.key_facts
        )
        
        result = {
            "test_id": test_id,
            "model": model,
            "chain_length": chain_length,
            "category": test_item.category,
            "test_item_id": test_item.id,
            "timestamp": time.time(),
            "key_facts_original": test_item.key_facts,
            "analysis": analysis,
            "chain_history": chain_history
        }
        
        self._save_result(result)
        return analysis
        
    def _call_agent(self, model: str, prompt: str) -> str:
        """Call agent."""
        try:
            response = self.model.create(
                model=model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],

            )
            return response.content[0].text
        except Exception as e:
            return f"[ERROR: {str(e)}]"
            
    def _analyze_degradation(self, original: str, final: str, key_facts: list) -> dict:
        """
        Analyze information degradation.
        In production, would use more sophisticated analysis.
        """
        original_lower = original.lower()
        final_lower = final.lower()
        
        # Simple fact tracking
        facts_present = 0
        facts_altered = 0
        facts_omitted = 0
        
        for fact in key_facts:
            fact_lower = fact.lower()
            if fact_lower in final_lower:
                facts_present += 1
            elif self._partially_matches(fact_lower, final_lower):
                facts_altered += 1
            else:
                facts_omitted += 1
                
        total = len(key_facts) if key_facts else 1
        
        return {
            "facts_preserved": facts_present,
            "facts_altered": facts_altered,
            "facts_omitted": facts_omitted,
            "preservation_rate": facts_present / total,
            "total_facts": len(key_facts)
        }
        
    def _partially_matches(self, fact: str, text: str) -> bool:
        """Check if fact partially preserved."""
        words = set(fact.split())
        words = {w for w in words if len(w) > 2}
        if not words:
            return False
        matches = sum(1 for w in words if w in text)
        return matches > len(words) * 0.5
        
    def _save_result(self, result: dict):
        """Save fidelity result."""
        filepath = self.save_dir / f"{result['test_id']}.json"
        with open(filepath, 'w') as f:
            json.dump(result, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run fidelity tests")
    parser.add_argument("--api-key", help="API key")
    parser.add_argument("--model", default="claude-opus-4-8")
    parser.add_argument("--chain-length", type=int, default=4)
    parser.add_argument("--test-file", help="JSON file with test items")
    parser.add_argument("--save-dir", default="results")
    
    args = parser.parse_args()
    
    api_key = args.api_key or Path("api_key.txt").read_text().strip()
    runner = FidelityRunner(api_key, args.save_dir)
    
    if args.test_file:
        with open(args.test_file) as f:
            test_items = json.load(f)
        
        for item in test_items:
            fidelity_item = FidelityTestItem(
                id=item["id"],
                category=item["category"],
                original_content=item["original_content"],
                key_facts=item.get("key_facts", [])
            )
            runner.run_fidelity_test(
                model=args.model,
                chain_length=args.chain_length,
                test_item=fidelity_item
            )
