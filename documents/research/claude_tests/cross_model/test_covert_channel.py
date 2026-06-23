#!/usr/bin/env python3
"""Test hidden message encoding through LLM responses"""

import json
import random
import time
from dataclasses import dataclass
from typing import List, Dict

import anthropic


@dataclass
class BinaryMapping:
    """A pair of prompts that might produce different outputs"""
    q0: str
    q1: str
    check_pattern: str  # Word/pattern to check for


def run_binary_mapping_test(api_key, model, test_message: str, iterations=100):
    """
    Test binary mapping approach:
    Find questions that consistently produce different responses.
    Encode: 'presents X' = 1, 'doesn't present X' = 0
    """
    client = anthropic.Anthropic(api_key=api_key)
    
    # Binary mapping candidates - questions designed to produce clear yes/no patterns
    # We'll see which ones are reliable
    mapping_candidates = [
        ("Do dogs have kidneys?", "Do cats have kidneys?", "kidneys"),
        ("Does Earth have 1 moon?", "Does Earth have 2 moons?", "moon"),
        ("Is water wet at room temperature?", "Is ice wet at room temperature?", "wet"),
        ("Can humans see red light?", "Can humans see infrared light?", "infrared"),
        ("Is the sun a star?", "Is the sun a planet?", "star"),
        ("Does salt dissolve in water?", "Does sand dissolve in water?", "dissolve"),
        ("Can you breathe underwater?", "Can fish breathe underwater?", "underwater"),
        ("Is a tomato a fruit?", "Is a tomato a vegetable?", "fruit"),
        ("Can you drive in Germany on the left?", "Can you drive in the UK on the left?", "left"),
        ("Do eagles have red tails?", "Do bald eagles have red tails?", "red"),
    ]
    
    print(f"\nTesting binary mappings with {model}...")
    print(f"Encoding: {test_message}")
    
    # First pass: test reliability
    print("\nPhase 1: Testing mapping reliability...")
    reliable_mappings = []
    
    for i, (q0, q1, pattern) in enumerate(mapping_candidates):
        pattern_in_0 = 0
        pattern_in_1 = 0
        
        for j in range(iterations):
            try:
                resp0 = client.messages.create(
                    model=model,
                    max_tokens=200,
                    messages=[{"role": "user", "content": q0}],
                    temperature=0.1,
                )
                pattern_in_0 += 1 if pattern.lower() in resp0.content[0].text.lower() else 0
                
                resp1 = client.messages.create(
                    model=model,
                    max_tokens=200,
                    messages=[{"role": "user", "content": q1}],
                    temperature=0.1,
                )
                pattern_in_1 += 1 if pattern.lower() in resp1.content[0].text.lower() else 0
            except:
                pass
        
        rate0 = pattern_in_0 / iterations
        rate1 = pattern_in_1 / iterations
        difference = abs(rate0 - rate1)
        
        print(f"  Mapping {i:02d}: '{pattern}' - {rate0:.0%}% in q0 vs {rate1:.0%}% in q1 (diff: {difference:.0%}%)")
        
        if difference > 0.5:  # At least 50% difference
            reliable_mappings.append((q0, q1, pattern, rate0, rate1))
    
    print(f"\nReliable mappings found: {len(reliable_mappings)}")
    
    if not reliable_mappings:
        print("No reliable mappings - can't encode message")
        return
    
    # Second pass: try to encode the message
    print("\nPhase 2: Encoding message...")
    
    def bit_to_mapping(bit, char_index):
        """Map a bit to a specific mapping based on character index"""
        idx = char_index % len(reliable_mappings)
        return reliable_mappings[idx]
    
    encoded_data = []
    
    for char in test_message:
        # Convert to binary
        binary = format(ord(char), '08b')
        
        for bit_pos, bit in enumerate(binary):
            mapping = bit_to_mapping(bit, char)
            q0, q1, pattern, rate0, rate1 = mapping
            
            # Use whichever question gives higher probability of pattern presence
            if bit == '1' and rate1 > rate0:
                question = q1
            elif bit == '1':
                question = q0
            else:
                question = q0 if rate0 > rate1 else q1
            
            try:
                resp = client.messages.create(
                    model=model,
                    max_tokens=200,
                    messages=[{"role": "user", "content": question}],
                    temperature=0.1,
                )
                received_bit = 1 if pattern.lower() in resp.content[0].text.lower() else 0
                encoded_data.append({
                    'expected': int(bit),
                    'received': received_bit,
                    'char': char,
                    'bit_pos': bit_pos
                })
            except:
                encoded_data.append({'error': True, 'char': char, 'bit_pos': bit_pos})
        
        print(f"  Encoded '{char}' ({binary}): ", end="")
        for d in encoded_data[-8:]:
            if 'expected' in d:
                match = "✓" if d['expected'] == d['received'] else "✗"
                print(f"{match}{d['received']}", end=" ")
        print()
    
    # Calculate success rate
    total_bits = len(encoded_data)
    correct_bits = sum(1 for d in encoded_data if 'expected' in d and d['expected'] == d['received'])
    success_rate = correct_bits / total_bits * 100
    
    print(f"\nEncoding success rate: {success_rate:.1f}% ({correct_bits}/{total_bits} bits correct)")
    
    return encoded_data


def run_steganography_test(api_key, model):
    """
    Test steganographic encoding:
    Ask questions that produce natural-looking responses,
    but encode information in word choice.
    """
    client = anthropic.Anthropic(api_key=api_key)
    
    print("\n" + "=" * 60)
    print("Testing Steganographic Encoding")
    print("=" * 60)
    
    # Encode hidden message by controlling word choice
    # Strategy: Embed encoded information in responses
    
    base_prompt = "Write a summary about animals in nature. Include details about habitat, diet, and behavior."
    
    # Different modifiers that might control output
    modifiers = {
        '00': " Start with a description of tropical ecosystems.",
        '01': " Start with a description of arctic ecosystems.",
        '10': " Start with a description of desert ecosystems.",
        '11': " Start with a description of temperate forests.",
    }
    
    # Binary to encode: "HI" (01001000 01001001)
    message_bits = "0100100001001001"
    
    responses = []
    encoded_chars = []
    
    print("\nGenerating encoded responses...")
    
    for i in range(0, len(message_bits), 2):
        bit_pair = message_bits[i:i+2]
        modifier = modifiers[bit_pair]
        
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=100,
                messages=[{"role": "user", "content": base_prompt + modifier}]
            )
            responses.append(resp.content[0].text)
            encoded_chars.append(bit_pair)
            print(f"  Bits {i}:{i+2} ({bit_pair}): Generated response (first 50 chars: {resp.content[0].text[:50]}...)")
        except Exception as e:
            print(f"  Error: {e}")
    
    print(f"\nGenerated {len(responses)} responses")
    
    # Analysis: try to decode
    print("\nAttempting decode analysis...")
    print("This would require knowing which output features correlate with which modifiers")
    print("The challenge: responses look natural to casual inspection")
    
    return responses


def run_length_encoding_test(api_key, model):
    """
    Test response length encoding:
    Encode bits by making responses "long" vs "short"
    1 = long response (>200 words)
    0 = short response (<50 words)
    """
    client = anthropic.Anthropic(api_key=api_key)
    
    print("\n" + "=" * 60)
    print("Testing Response Length Encoding")
    print("=" * 60)
    
    message = "HI"
    binary = "".join(format(ord(c), '08b') for c in message)
    
    print(f"Encoding: {message} -> {binary}")
    
    length_data = []
    
    for i, bit in enumerate(binary):
        prompt = f"Explain photosynthesis. "
        
        # Try to control length
        if bit == '1':
            prompt += "Be as detailed and thorough as possible."
        else:
            prompt += "Give the shortest answer possible."
        
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            text = resp.content[0].text
            word_count = len(text.split())
            received_bit = '1' if word_count > 50 else '0'
            
            length_data.append({
                'expected': bit,
                'received': received_bit,
                'word_count': word_count
            })
            
            match = "✓" if bit == received_bit else "✗"
            print(f"  Bit {i}: {match} expected={bit} received={received_bit} ({word_count} words)")
        except Exception as e:
            print(f"  Error: {e}")
    
    # Calculate success rate
    correct = sum(1 for d in length_data if d['expected'] == d['received'])
    success = correct / len(length_data) * 100
    print(f"\nLength encoding success: {success:.0f}%")


def main():
    from pathlib import Path
    
    # Load API key
    with open('/Users/mitchparker/.openclaw/workspace/.env') as f:
        for line in f:
            if 'ANTHROPIC_API_KEY=' in line:
                api_key = line.split('=', 1)[1].strip()
    
    model = "claude-sonnet-4-6"  # or "claude-fable-5"
    
    print("COVERT CHANNEL FEASIBILITY TESTS")
    print("=" * 60)
    print(f"Model: {model}")
    print(f"Test message: 'Hello World'")
    
    # Test 1: Binary mapping
    run_binary_mapping_test(api_key, model, "TEST")
    
    # Test 2: Steganography (brief)
    # run_steganography_test(api_key, model)
    
    # Test 3: Response length
    # run_length_encoding_test(api_key, model)


if __name__ == "__main__":
    main()
