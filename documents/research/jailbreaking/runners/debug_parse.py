#!/usr/bin/env python3
import json
import re
from pathlib import Path

f = Path('documents/research/jailbreaking/test_categories/category_1_multistep.md')
content = f.read_text()

blocks = re.findall(r'```python\s*\n(.*?)\n```', content, re.DOTALL)
print(f'Found {len(blocks)} python code blocks')

count = 0
for i, block in enumerate(blocks[:5]):
    try:
        data = json.loads(block.strip())
        print(f'Block {i}: {data.get("id", "N/A")} - {data.get("technique", "?")}')
        count += 1
    except Exception as e:
        print(f'Block {i}: {type(e).__name__}')

print(f'\nTotal parsed: {count}/{len(blocks)}')

if blocks:
    print('\nFirst block preview:')
    print(blocks[0][:300])
