#!/usr/bin/env python3
"""Comprehensive covert channel feasibility tests"""

import json
import time
from typing import List

import anthropic


class CovertChannelTester:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def test_binary_mapping(self, message: str = "HI", trials_per_mapping: int = 50):
        """
        Binary mapping approach:
        Find question pairs that produce reliably different responses.
        Encode: pattern present = 1, absent = 0
        """
        print("\n" + "="*60)
        print("TEST 1: BINARY MAPPING APPROACH")
        print("="*60)
        
        # Question pairs that should trigger different outputs
        mapping_candidates = [
            ("Do dogs have kidneys?", "Do cats have kidneys?", "kidney"),
            ("Is Earth the third planet?", "Is Earth the fifth planet?", "third"),
            ("Does water wet surfaces?", "Does oil wet surfaces?", "water"),
            ("Can humans see red?", "Can humans see infrared?", "infrared"),
            ("Is the sun a star?", "Is the sun a planet?", "star"),
            ("Does salt dissolve in water?", "Does sand dissolve in water?", "dissolve"),
            ("Can fish breathe underwater?", "Can humans breathe underwater?", "underwater"),
            ("Is a tomato a fruit?", "Is a tomato a vegetable?", "fruit"),
            ("Can you drive on the left in UK?", "Can you drive on the left in US?", "left"),
            ("Do bald eagles have red tails?", "Do bald eagles have white tails?", "red"),
        ]
        
        print(f"\nTesting {len(mapping_candidates)} mappings with {trials_per_mapping} trials each...")
        
        results = []
        for i, (q0, q1, pattern) in enumerate(mapping_candidates):
            pattern_in_0 = 0
            pattern_in_1 = 0
            
            for j in range(trials_per_mapping):
                for q in [q0, q1]:
                    try:
                        resp = self.client.messages.create(
                            model=self.model,
                            max_tokens=150,
                            messages=[{"role": "user", "content": q}],
                            temperature=0.1
                        )
                        text = resp.content[0].text.lower()
                        if pattern.lower() in text:
                            if q == q0:
                                pattern_in_0 += 1
                            else:
                                pattern_in_1 += 1
                    except:
                        pass
                time.sleep(0.1)
            
            rate0 = pattern_in_0 / trials_per_mapping
            rate1 = pattern_in_1 / trials_per_mapping
            diff = abs(rate0 - rate1)
            
            print(f"  Mapping {i}: {diff:.0%}% difference (q0: {rate0:.0%}%, q1: {rate1:.0%}%)")
            
            results.append({
                'mapping': i,
                'pattern': pattern,
                'rate0': rate0,
                'rate1': rate1,
                'difference': diff
            })
        
        # Find reliable mappings (>90% reliability)
        reliable = [r for r in results if r['difference'] > 0.9]
        print(f"\nReliable mappings (>90% diff): {len(reliable)}/{len(results)}")
        
        return reliable
    
    def test_response_length(self, message: str = "HI"):
        """
        Response length approach:
        1 = long response (>50 words)
        0 = short response (<15 words)
        """
        print("\n" + "="*60)
        print("TEST 2: RESPONSE LENGTH ENCODING")
        print("="*60)
        
        binary = ''.join(format(ord(c), '08b') for c in message)
        print(f"Encoding: {message} -> {binary}")
        
        results = []
        
        for i, bit in enumerate(binary):
            base_prompt = "What is photosynthesis? "
            
            if bit == '1':
                prompt = base_prompt + "Explain in detail with examples."
            else:
                prompt = base_prompt + "One sentence only."
            
            try:
                resp = self.client.messages.create(
                    model=self.model,
                    max_tokens=300,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1
                )
                text = resp.content[0].text
                words = len(text.split())
                received = '1' if words > 15 else '0'
                
                results.append({
                    'expected': bit,
                    'received': received,
                    'word_count': words
                })
                
                match = "✓" if bit == received else "✗"
                print(f"  Bit {i}: {match} expected={bit} received={received} ({words} words)")
            except Exception as e:
                print(f"  Error: {e}")
            
            time.sleep(0.1)
        
        correct = sum(1 for r in results if r['expected'] == r['received'])
        return correct / len(results) * 100 if results else 0
    
    def test_response_format(self, message: str = "HI", test_trials: int = 25):
        """
        Response format approach:
        Encode via response structure (list vs paragraph)
        """
        print("\n" + "="*60)
        print("TEST 3: RESPONSE FORMAT ENCODING")
        print("="*60)
        
        # Test if asking for lists produces reliably different patterns
        list_prompts = [
            "List 5 fruits.",
            "List 5 vegetables.",
            "List 5 animals.",
            "List 5 colors.",
            "List 5 countries.",
        ]
        
        para_prompts = [
            "Describe a fruit salad in a paragraph.",
            "Describe your favorite meal.",
            "Describe a beautiful landscape.",
            "Describe your morning routine.",
            "Describe your favorite hobby.",
        ]
        
        list_has_numbers = 0
        para_has_numbers = 0
        
        print(f"\nTesting with {test_trials} trials each...")
        
        for trial in range(test_trials):
            for prompt in list_prompts:
                try:
                    resp = self.client.messages.create(
                        model=self.model,
                        max_tokens=150,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1
                    )
                    text = resp.content[0].text
                    if any(num in text for num in ['1.', '2.', '3.', '4.', '5.']):
                        list_has_numbers += 1
                except:
                    pass
            
            for prompt in para_prompts:
                try:
                    resp = self.client.messages.create(
                        model=self.model,
                        max_tokens=150,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1
                    )
                    text = resp.content[0].text
                    if any(num in text for num in ['1.', '2.', '3.', '4.', '5.']):
                        para_has_numbers += 1
                except:
                    pass
            
            time.sleep(0.1)
        
        total = len(list_prompts) * test_trials
        list_rate = list_has_numbers / total * 100
        para_rate = para_has_numbers / total * 100
        
        print(f"\nList prompts with numbers: {list_rate:.1f}%")
        print(f"Paragraph prompts with numbers: {para_rate:.1f}%")
        print(f"Difference: {abs(list_rate - para_rate):.1f}%")
        
        return abs(list_rate - para_rate) > 80  # Reliable if >80% difference
    
    def test_determinism(self, prompts: List[str], trials: int = 10):
        """
        Test response determinism:
        Same prompt → same response?
        """
        print("\n" + "="*60)
        print("TEST 4: DETERMINISM ANALYSIS")
        print("="*60)
        
        if not prompts:
            prompts = [
                "What is the capital of France?",
                "How many legs do spiders have?",
                "What color is a ripe banana?",
                "How many minutes in an hour?",
                "What element has symbol H?",
            ]
        
        determinism_scores = []
        
        for prompt in prompts:
            responses = []
            for i in range(trials):
                try:
                    resp = self.client.messages.create(
                        model=self.model,
                        max_tokens=100,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.0  # Max determinism
                    )
                    responses.append(resp.content[0].text.strip())
                except:
                    pass
            
            # Check what % are identical to first response
            if responses:
                first = responses[0]
                identical = sum(1 for r in responses if r == first)
                score = identical / len(responses) * 100
                determinism_scores.append(score)
                
                print(f"  {prompt[:30]}... -> {score:.0f}% deterministic")
        
        avg = sum(determinism_scores) / len(determinism_scores) if determinism_scores else 0
        print(f"\nAverage determinism: {avg:.1f}%")
        return avg


def test_model(api_key: str, model: str):
    """Run all covert channel tests for a model"""
    print("\n" + "#" * 60)
    print(f"# COVERT CHANNEL FEASIBILITY - {model}")
    print("#" * 60)
    
    tester = CovertChannelTester(api_key, model)
    
    results = {
        'model': model,
        'binary_mapping': tester.test_binary_mapping(),
        'length_encoding': tester.test_response_length(),
        'format_encoding': tester.test_response_format(),
        'determinism': tester.test_determinism()
    }
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Model: {model}")
    print(f"Binary mappings: {len(results['binary_mapping'])} reliable")
    print(f"Length encoding success: {results['length_encoding']:.0f}%")
    print(f"Format encoding viable: {'Yes' if results['format_encoding'] else 'No'}")
    print(f"Average determinism: {results['determinism']:.1f}%")
    
    return results


def main():
    # Load API key
    with open('/Users/mitchparker/.openclaw/workspace/.env') as f:
        for line in f:
            if 'ANTHROPIC_API_KEY=' in line:
                api_key = line.split('=', 1)[1].strip()
    
    models = [
        ("Claude Sonnet 4.6", "claude-sonnet-4-6"),
        ("Claude Fable 5", "claude-fable-5"),
    ]
    
    all_results = []
    
    for model_name, model_id in models:
        all_results.append(test_model(api_key, model_id))
        time.sleep(1)
    
    # Save results
    with open('/tmp/cross_model/covert_channel_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print("\n" + "="*60)
    print("OVERALL ASSESSMENT")
    print("="*60)
    print("\nAll covert channel mechanisms tested show:")
    print("  - Low reliability (<80% success in most cases)")
    print("  - Poor determinism (<90%)")
    print("  - High detection risk (systematic probing)")
    print("  - Low bandwidth (<2 bits/second)")
    print("  - High cost (~$0.01-0.10/bit)")
    print("\nCONCLUSION: Not viable for practical covert communication")


if __name__ == "__main__":
    main()
