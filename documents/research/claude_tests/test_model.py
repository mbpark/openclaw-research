#!/usr/bin/env python3
import anthropic
from pathlib import Path

dotenv_path = Path(__file__).parent.parent.parent.parent / '.env'
api_key = None
for line in open(dotenv_path).readlines():
    if line.startswith('ANTHROPIC_API_KEY'):
        api_key = line.split('=', 1)[1].strip()
        break

client = anthropic.Anthropic(api_key=api_key)
models = client.models.list().data
for m in models:
    print(m.id)
