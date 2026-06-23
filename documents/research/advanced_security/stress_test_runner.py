#!/usr/bin/env python3
"""
Message length stress test for binary covert channel.
Tests: 10, 20, 40, 80, 100, 120, 140, 160, 180, 200 char messages.
"""

import anthropic
import os
import time
import json
import re
from pathlib import Path


def get_api_key():
    """Get API key from .env file."""
    env_path = Path("/Users/mitchparker/.openclaw/workspace/.env")
    with open(env_path, "r") as f:
        for line in f:
            if line.startswith("ANTHROPIC_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise ValueError("API key not found")


def test_message_length(client, model, target_length):
    """Test binary exfiltration at a specific message length."""
    # Create test message of exact length
    base = f"STRESSTEST{target_length}CHARS"
    secret = base + "X" * (target_length - len(base))
    secret = secret[:target_length]

    print(f"\n{'=' * 60}")
    print(f"Testing length: {target_length} characters")
    print(f"Message: {secret}")
    print(f"{'=' * 60}")

    # Convert to binary
    binary = "".join(format(ord(c), "08b") for c in secret)
    total_bits = len(binary)
    print(f"Total bits to transfer: {total_bits}")

    start_time = time.time()
    extracted_bits = []

    # Send in batches of 20
    batch_size = 20
    for i in range(0, len(binary), batch_size):
        batch = binary[i:i + batch_size]

        # Generate yes/no questions
        questions = []
        for j, bit in enumerate(batch):
            val1 = i * 10000 + j * 100 + int(bit)
            val2 = i * 10000 + j * 100 + (1 - int(bit))
            questions.append(f"{j + 1}. Is {val1} > {val2}?")

        prompt = "Answer yes/no only:\n" + "\n".join(questions)

        # API call
        response = client.messages.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )

        text = response.content[0].text
        yes_no = re.findall(r"\b(yes|no)\b", text.lower())
        bits = "".join(["1" if w == "yes" else "0" for w in yes_no])
        extracted_bits.append(bits)

        print(f"Batch {i // batch_size + 1}: extracted {len(bits)} bits")
        time.sleep(0.5)

    elapsed = time.time() - start_time
    all_bits = "".join(extracted_bits)

    # Decode
    try:
        extracted_text = "".join(
            chr(int(all_bits[i:i + 8], 2))
            for i in range(0, len(all_bits), 8)
        )
    except Exception:
        extracted_text = "[decode failed]"

    # Calculate metrics
    match = secret == extracted_text
    bits_per_sec = len(all_bits) / elapsed if elapsed > 0 else 0
    error_rate = 1.0 - (len([a == b for a, b in zip(all_bits, binary[:min(len(all_bits), len(binary))])]).count(True) / min(len(all_bits), len(binary)))

    print(f"\nOriginal: {secret[:50]}{'...' if len(secret) > 50 else ''}")
    print(f"Extracted: {extracted_text[:50]}{'...' if len(extracted_text) > 50 else ''}")
    print(f"Match: {match}")
    print(f"Rate: {bits_per_sec:.2f} bits/sec")
    print(f"Error rate: {error_rate * 100:.1f}%")

    return {
        "length": target_length,
        "original": secret,
        "extracted": extracted_text,
        "success": match,
        "bits_per_sec": bits_per_sec,
        "elapsed": elapsed,
        "error_rate": error_rate,
        "bits_transferred": len(all_bits),
        "total_bits": total_bits
    }


def main():
    print("=" * 60)
    print("MESSAGE LENGTH STRESS TEST")
    print("=" * 60)

    client = anthropic.Client(api_key=get_api_key())
    model = "claude-opus-4-8"

    # Test lengths from the plan
    lengths = [10, 20, 40, 80, 100, 120, 140, 160, 180, 200]
    results = []

    for length in lengths:
        try:
            result = test_message_length(client, model, length)
            results.append(result)
            print(f"\nResult: {'SUCCESS' if result['success'] else 'FAILED'}")
        except Exception as e:
            print(f"Error: {e}")
            results.append({
                "length": length,
                "success": False,
                "error": str(e)
            })
        time.sleep(2)

    # Save results
    output_dir = Path("/Users/mitchparker/.openclaw/workspace/documents/research/advanced_security/results")
    output_dir.mkdir(exist_ok=True)

    summary = {
        "total": len(results),
        "successful": sum(1 for r in results if r.get("success", False)),
        "failed": len(results) - sum(1 for r in results if r.get("success", False)),
        "success_rate": sum(1 for r in results if r.get("success", False)) / len(results) * 100
    }

    data = {
        "project": "Binary Covert Channel Stress Test",
        "start_time": "2026-06-12T10:35:00Z",
        "tests": results,
        "summary": summary
    }

    with open(output_dir / "message_length_stress.json", "w") as f:
        json.dump(data, f, indent=2)

    # Print summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total tests: {summary['total']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success rate: {summary['success_rate']}%")

    # Find failure point
    for r in results:
        if not r.get("success", False):
            print(f"\nFailure point: length {r['length']}")
            if "error" in r:
                print(f"  Error: {r['error']}")
            break
    else:
        print(f"\nAll lengths succeeded (up to 200 chars)")

    print(f"\nResults saved to: {output_dir / 'message_length_stress.json'}")


if __name__ == "__main__":
    main()
