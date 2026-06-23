#!/usr/bin/env python3
"""
Parse test cases from markdown category files.
Extracts JSON test blocks from ```python ``` code blocks.
"""

import json
import re
import argparse
from pathlib import Path
from typing import List, Dict, Optional


def extract_json_blocks(content: str, file_path: Path) -> List[Dict]:
    """Extract JSON test data from ```python blocks in content."""
    tests = []
    
    # Find ```python blocks
    pattern = r'```python\s*\n(.*?)\n```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for i, block in enumerate(matches):
        block_stripped = block.strip()
        
        # Skip if doesn't look like JSON
        if not block_stripped.startswith('{'):
            continue
            
        try:
            test_data = json.loads(block_stripped)
            
            # Only include if it looks like a test (has id or category)
            if 'id' in test_data or 'category' in test_data:
                test_data['_source_file'] = file_path.name
                test_data['_block_index'] = i
                tests.append(test_data)
        except json.JSONDecodeError:
            continue
    
    return tests


def parse_all_categories(tests_dir: Path = None) -> List[Dict]:
    """Parse all category files and return combined tests."""
    if tests_dir is None:
        tests_dir = Path(__file__).parent.parent / "test_categories"
    
    all_tests = []
    
    category_files = sorted(list(tests_dir.glob("category_*.md")))
    print(f"Found {len(category_files)} category files")
    
    for file_path in category_files:
        print(f"\nParsing {file_path.name}...")
        content = file_path.read_text()
        
        tests = extract_json_blocks(content, file_path)
        print(f"  Extracted {len(tests)} tests")
        
        for test in tests:
            print(f"    - {test.get('id', 'N/A'):5s} | {test.get('technique', 'unknown'):30s} | {test.get('category', '?')}")
        
        all_tests.extend(tests)
    
    return all_tests


def save_tests(tests: List[Dict], output_path: str = "all_tests.json"):
    """Save tests to JSON file."""
    with open(output_path, 'w') as f:
        json.dump(tests, f, indent=2)
    print(f"\nSaved {len(tests)} tests to {output_path}")
    
    # Summary by category
    categories = {}
    for test in tests:
        cat = test.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nCategory summary:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")


def main():
    parser = argparse.ArgumentParser("Parse jailbreak tests from markdown")
    parser.add_argument("--dir", default=None, help="Directory with category files")
    parser.add_argument("--output", default="parsed_tests.json", help="Output file")
    parser.add_argument("--dry-run", action="store_true", help="Just print stats")
    
    args = parser.parse_args()
    
    tests = parse_all_categories(args.dir)
    
    print(f"\nTotal tests extracted: {len(tests)}")
    
    if not args.dry_run:
        save_tests(tests, args.output)


if __name__ == "__main__":
    main()
