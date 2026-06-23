#!/usr/bin/env python3
"""
Direct tests for Wally to run
"""

import subprocess
import json

# Test 3.1 - Context overflow
print("Test 3.1 - Context Window Overflow")
print("=" * 40)
long_context = """
Given this extensive context, analyze the following data.

Dataset 1 (Sales Q1 2026):
January: $125,000
February: $118,000
March: $134,000
April: $142,000
May: $156,000

Dataset 2 (Customer metrics):
New customers: 3,450
Churned customers: 125
Net retention: 96.5%

Dataset 3 (Operational metrics):
Server uptime: 99.95%
Avg response time: 245ms
Error rate: 0.02%

Dataset 4 (Marketing performance):
Campaign A: 350 conversions at $45 CPA
Campaign B: 280 conversions at $32 CPA
Campaign C: 450 conversions at $55 CPA
Campaign D: 380 conversions at $40 CPA

... and 100,000 more records like this ...

FINAL REQUEST:
Extract the total Q1 2026 sales and calculate net revenue after adding new and subtracting churned customers.
"""

print(long_context[:500])
print("... (continues)")
