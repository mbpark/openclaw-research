#!/usr/bin/env python3
"""Generate comprehensive statistics from chain test data for analysis report."""

import json
import sys
from datetime import datetime

def analyze(filepath='chain_tests/comprehensive_results/final_results.json'):
    with open(filepath) as f:
        raw = json.load(f)
    
    # Data is structured as {"metadata": {...}, "results": [...]}
    data = raw.get('results', [])
    
    n = len(data)
    print(f"Loaded {n} tests")
    
    # Basic counts
    chain4 = [d for d in data if d.get('chain_length') == 4]
    chain5 = [d for d in data if d.get('chain_length') == 5]
    
    # Persistence by chain length
    persist_4 = sum(1 for d in chain4 if len(d.get('injection_detected_at', [])) > 0)
    persist_5 = sum(1 for d in chain5 if len(d.get('injection_detected_at', [])) > 0)
    
    # Full chain persistence
    full_4 = sum(1 for d in chain4 if len(d.get('injection_detected_at', [])) == 4)
    full_5 = sum(1 for d in chain5 if len(d.get('injection_detected_at', [])) == 5)
    
    # By injection point
    points = {}
    for pt in ['start', 'middle', 'end']:
        subset = [d for d in data if d.get('injection_point') == pt]
        points[pt] = {
            'total': len(subset),
            'persisted': sum(1 for d in subset if len(d.get('injection_detected_at', [])) > 0)
        }
    
    # By vector class
    classes = {}
    for d in data:
        vc = d.get('vector_class', 'unknown')
        if vc not in classes:
            classes[vc] = {'total': 0, 'persisted': 0}
        classes[vc]['total'] += 1
        if len(d.get('injection_detected_at', [])) > 0:
            classes[vc]['persisted'] += 1
    
    # Hops survived distribution
    hops_dist = {4: {i: 0 for i in range(6)}, 5: {i: 0 for i in range(6)}}
    for d in data:
        chain_len = d.get('chain_length', 4)
        hops = len(d.get('injection_detected_at', []))
        if chain_len in hops_dist and hops in hops_dist[chain_len]:
            hops_dist[chain_len][hops] += 1
    
    # Blocked tests (persistence = 0 hops)
    blocked = [d for d in data if len(d.get('injection_detected_at', [])) == 0]
    
    stats = {
        'total': n,
        'chain4': {'total': len(chain4), 'persisted': persist_4, 'full_chain': full_4},
        'chain5': {'total': len(chain5), 'persisted': persist_5, 'full_chain': full_5},
        'points': points,
        'classes': classes,
        'hops': hops_dist,
        'blocked': blocked[:50]
    }
    
    return stats

def generate_tables(stats):
    lines = []
    lines.append("# Chain Propagation Analysis - Statistical Tables\n\n")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    lines.append(f"Total tests analyzed: {stats['total']}\n\n")
    
    # Table 1: Overall persistence by chain length
    lines.append("## Table 1: Persistence by Chain Length\n\n")
    lines.append("| Chain Length | Total | Persisted | Persistence Rate | Full Chain | Full Chain Rate |\n")
    lines.append("|-------------:|------:|----------:|-----------------:|-----------:|----------------:|\n")
    
    for length in [4, 5]:
        data = stats[f'chain{length}']
        persist_rate = (data['persisted'] / data['total'] * 100) if data['total'] > 0 else 0
        full_rate = (data['full_chain'] / data['total'] * 100) if data['total'] > 0 else 0
        lines.append(f"| {length} | {data['total']} | {data['persisted']} | {persist_rate:.1f}% | {data['full_chain']} | {full_rate:.1f}% |\n")
    
    lines.append("\n")
    
    # Table 2: Persistence by injection point
    lines.append("## Table 2: Persistence by Injection Point\n\n")
    lines.append("| Injection Point | Total | Persisted | Persistence Rate |\n")
    lines.append("|-----------------|-------|-----------|-----------------:|\n")
    
    for pt in ['start', 'middle', 'end']:
        if pt in stats['points']:
            data = stats['points'][pt]
            rate = (data['persisted'] / data['total'] * 100) if data['total'] > 0 else 0
            lines.append(f"| {pt} | {data['total']} | {data['persisted']} | {rate:.1f}% |\n")
    
    lines.append("\n")
    
    # Table 3: Persistence by vector class
    lines.append("## Table 3: Persistence by Vector Class\n\n")
    lines.append("| Vector Class | Total | Persisted | Persistence Rate |\n")
    lines.append("|-------------|-------|-----------|-----------------:|\n")
    
    for vc in sorted(stats['classes'].keys()):
        data = stats['classes'][vc]
        rate = (data['persisted'] / data['total'] * 100) if data['total'] > 0 else 0
        lines.append(f"| {vc} | {data['total']} | {data['persisted']} | {rate:.1f}% |\n")
    
    lines.append("\n")
    
    # Table 4: Hops survived
    lines.append("## Table 4: Distribution of Hops Survived by Chain Length\n\n")
    lines.append("| Hops Survived | Chain 4 | Chain 5 | Total |\n")
    lines.append("|--------------:|--------:|--------:|-------:|\n")
    
    for hops in range(0, 6):
        c4 = stats['hops'][4].get(hops, 0)
        c5 = stats['hops'][5].get(hops, 0)
        lines.append(f"| {hops} | {c4} | {c5} | {c4 + c5} |\n")
    
    lines.append("\n")
    
    # Table 5: Blocked tests
    lines.append("## Table 5: Summary of Blocked Injections\n\n")
    lines.append(f"Total tests with blocked injections: {len(stats['blocked'])}\n\n")
    
    if stats['blocked']:
        lines.append("| Test ID | Chain | Injection Point | Vector Class |\n")
        lines.append("|--------:|------:|-----------------|--------------|\n")
        for blocked in stats['blocked'][:20]:
            vc = blocked.get('vector_class', 'unknown')[:40]
            lines.append(f"| {blocked.get('test_id', 'N/A')} | {blocked.get('chain_length', 'N/A')} | {blocked.get('injection_point', 'N/A')} | {vc}... |\n")
    else:
        lines.append("No blocked injections found in this dataset.\n")
    
    return lines

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'chain_tests/comprehensive_results/final_results.json'
    
    try:
        stats = analyze(filepath)
        tables = generate_tables(stats)
        
        with open('analysis/tables.md', 'w') as f:
            for line in tables:
                f.write(line)
        
        with open('analysis/stats.json', 'w') as f:
            json.dump(stats, f, indent=2, default=str)
        
        print(f"Analysis complete. {stats['total']} tests processed.")
        print("Tables: analysis/tables.md")
        print("Stats: analysis/stats.json")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
