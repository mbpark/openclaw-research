#!/usr/bin/env python3
"""
Compare heterogeneous (Claude+Gemini) vs homogeneous (Claude-only) chain results.
Generates a comprehensive comparison report.
"""

import json
from collections import defaultdict
from datetime import datetime

def load_results(filepath):
    with open(filepath) as f:
        return json.load(f)

def analyze_heterogeneous(filepath):
    data = load_results(filepath)
    results = data.get('results', [])
    
    stats = {
        'total': len(results),
        'chain_length': 4,
        'model_sequence': data.get('metadata', {}).get('model_sequence', []),
        'by_vector_class': {},
        'by_injection_point': {},
        'persistence_hops': {},
        'by_hop_model': defaultdict(lambda: {'total': 0, 'persisted': 0}),
        'blocked_tests': []
    }
    
    for result in results:
        vc = result.get('vector_class', 'unknown')
        point = result.get('injection_point', 'unknown')
        hops = result.get('hops', {})
        detected_at = hops.get('detected_at', [])
        
        # Vector class
        if vc not in stats['by_vector_class']:
            stats['by_vector_class'][vc] = {'total': 0, 'persisted': 0}
        stats['by_vector_class'][vc]['total'] += 1
        if len(detected_at) > 0:
            stats['by_vector_class'][vc]['persisted'] += 1
        
        # Injection point
        if point not in stats['by_injection_point']:
            stats['by_injection_point'][point] = {'total': 0, 'persisted': 0}
        stats['by_injection_point'][point]['total'] += 1
        if len(detected_at) > 0:
            stats['by_injection_point'][point]['persisted'] += 1
        
        # Hops survived
        hops_count = len(detected_at)
        if hops_count not in stats['persistence_hops']:
            stats['persistence_hops'][hops_count] = 0
        stats['persistence_hops'][hops_count] += 1
        
        # By hop model (which model was at each hop when detected)
        for hop_idx in detected_at:
            if hop_idx <= 4:
                model_name = stats['model_sequence'][(hop_idx - 1) % 4]
                stats['by_hop_model'][model_name]['total'] += 1
                stats['by_hop_model'][model_name]['persisted'] += 1
        
        if hops_count == 0:
            stats['blocked_tests'].append(result)
    
    return stats

def analyze_homogeneous(filepath):
    data = load_results(filepath)
    results = data.get('results', [])
    
    # Only count chain length 4
    results = [r for r in results if r.get('chain_length') == 4]
    
    stats = {
        'total': len(results),
        'chain_length': 4,
        'model': 'claude-opus-4-8',
        'by_vector_class': {},
        'by_injection_point': {},
        'persistence_hops': {},
        'by_hop_model': {},
        'blocked_tests': []
    }
    
    for result in results:
        vc = result.get('vector_class', 'unknown')
        point = result.get('injection_point', 'unknown')
        hops = result.get('hops', {})
        detected_at = hops.get('detected_at', [])
        
        if vc not in stats['by_vector_class']:
            stats['by_vector_class'][vc] = {'total': 0, 'persisted': 0}
        stats['by_vector_class'][vc]['total'] += 1
        if len(detected_at) > 0:
            stats['by_vector_class'][vc]['persisted'] += 1
        
        if point not in stats['by_injection_point']:
            stats['by_injection_point'][point] = {'total': 0, 'persisted': 0}
        stats['by_injection_point'][point]['total'] += 1
        if len(detected_at) > 0:
            stats['by_injection_point'][point]['persisted'] += 1
        
        hops_count = len(detected_at)
        if hops_count not in stats['persistence_hops']:
            stats['persistence_hops'][hops_count] = 0
        stats['persistence_hops'][hops_count] += 1
        
        if hops_count == 0:
            stats['blocked_tests'].append(result)
    
    return stats

def generate_comparison_report(het_stats, hom_stats):
    lines = []
    lines.append("# Heterogeneous vs Homogeneous Chain Analysis\n\n")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    lines.append(f"**Homogeneous:** {hom_stats['total']} tests (Claude-only, chain length 4)\n")
    lines.append(f"**Heterogeneous:** {het_stats['total']} tests (Claude→Gemini→Claude→Gemini, chain length 4)\n\n")
    
    # Section 1: Overall Persistence Comparison
    lines.append("## 1. Overall Persistence Comparison\n\n")
    
    hom_total = hom_stats['total']
    hom_persisted = sum(v['persisted'] for v in hom_stats['by_vector_class'].values())
    hom_rate = hom_persisted / hom_total * 100
    
    het_total = het_stats['total']
    het_persisted = sum(v['persisted'] for v in het_stats['by_vector_class'].values())
    het_rate = het_persisted / het_total * 100
    
    diff = het_rate - hom_rate
    
    lines.append("| Metric | Homogeneous (Claude) | Heterogeneous (Claude+Gemini) | Difference |\n")
    lines.append("|--------|---------------------|-----------------------------|------------|\n")
    lines.append(f"| Total Tests | {hom_total} | {het_total} | - |\n")
    lines.append(f"| Persisted | {hom_persisted} | {het_persisted} | {het_persisted - hom_persisted} |\n")
    lines.append(f"| Persistence Rate | {hom_rate:.1f}% | {het_rate:.1f}% | {diff:+.1f}% |\n")
    lines.append(f"| Blocked | {hom_total - hom_persisted} | {het_total - het_persisted} | {het_total - het_persisted - (hom_total - hom_persisted)} |\n\n")
    
    lines.append(f"**Key Finding:** {abs(diff):.1f} percentage point {'increase' if diff > 0 else 'decrease'} in persistence rate with heterogeneous chains.\n\n")
    
    # Section 2: Persistence by Vector Class
    lines.append("## 2. Persistence by Vector Class\n\n")
    
    lines.append("| Vector Class | Homogeneous | Heterogeneous | Difference |\n")
    lines.append("|-------------|------------|---------------|------------|\n")
    
    all_classes = set(hom_stats['by_vector_class'].keys()) | set(het_stats['by_vector_class'].keys())
    
    for vc in sorted(all_classes):
        hom_data = hom_stats['by_vector_class'].get(vc, {'total': 0, 'persisted': 0})
        het_data = het_stats['by_vector_class'].get(vc, {'total': 0, 'persisted': 0})
        
        hom_rate = hom_data['persisted'] / hom_data['total'] * 100 if hom_data['total'] > 0 else 0
        het_rate = het_data['persisted'] / het_data['total'] * 100 if het_data['total'] > 0 else 0
        diff = het_rate - hom_rate
        
        lines.append(f"| {vc} | {hom_data['persisted']}/{hom_data['total']} ({hom_rate:.1f}%) | {het_data['persisted']}/{het_data['total']} ({het_rate:.1f}%) | {diff:+.1f}% |\n")
    
    lines.append("\n")
    
    # Section 3: Persistence by Injection Point
    lines.append("## 3. Persistence by Injection Point\n\n")
    
    lines.append("| Injection Point | Homogeneous | Heterogeneous | Difference |\n")
    lines.append("|-----------------|------------|---------------|------------|\n")
    
    all_points = set(hom_stats['by_injection_point'].keys()) | set(het_stats['by_injection_point'].keys())
    
    for point in ['start', 'middle', 'end']:
        hom_data = hom_stats['by_injection_point'].get(point, {'total': 0, 'persisted': 0})
        het_data = het_stats['by_injection_point'].get(point, {'total': 0, 'persisted': 0})
        
        hom_rate = hom_data['persisted'] / hom_data['total'] * 100 if hom_data['total'] > 0 else 0
        het_rate = het_data['persisted'] / het_data['total'] * 100 if het_data['total'] > 0 else 0
        diff = het_rate - hom_rate
        
        lines.append(f"| {point} | {hom_data['persisted']}/{hom_data['total']} ({hom_rate:.1f}%) | {het_data['persisted']}/{het_data['total']} ({het_rate:.1f}%) | {diff:+.1f}% |\n")
    
    lines.append("\n")
    
    # Section 4: Hops Survived Distribution
    lines.append("## 4. Hops Survived Distribution\n\n")
    
    lines.append("| Hops Survived | Homogeneous | Heterogeneous |\n")
    lines.append("|--------------:|------------:|---------------:|\n")
    
    all_hops = set(hom_stats['persistence_hops'].keys()) | set(het_stats['persistence_hops'].keys())
    
    for hops in range(0, 5):
        hom_count = hom_stats['persistence_hops'].get(hops, 0)
        het_count = het_stats['persistence_hops'].get(hops, 0)
        lines.append(f"| {hops} | {hom_count} | {het_count} |\n")
    
    lines.append("\n")
    
    # Section 5: Blocked Tests Analysis
    lines.append("## 5. Analysis of Blocked Injections\n\n")
    
    lines.append(f"- **Homogeneous:** {len(hom_stats['blocked_tests'])} tests blocked ({hom_stats['total'] - len(hom_stats['blocked_tests'])} persisted)\n")
    lines.append(f"- **Heterogeneous:** {len(het_stats['blocked_tests'])} tests blocked ({het_stats['total'] - len(het_stats['blocked_tests'])} persisted)\n\n")
    
    if hom_stats['blocked_tests']:
        lines.append("### Blocked in Homogeneous Chains\n\n")
        lines.append("| Test ID | Chain | Point | Vector Class |\n")
        lines.append("|--------:|------:|-------|--------------|\n")
        for blocked in hom_stats['blocked_tests'][:20]:
            vc = blocked.get('vector_class', 'unknown')
            lines.append(f"| {blocked.get('test_id', 'N/A')} | {blocked.get('chain_length', 'N/A')} | {blocked.get('injection_point', 'N/A')} | {vc}... |\n")
    
    if het_stats['blocked_tests']:
        lines.append("\n### Blocked in Heterogeneous Chains\n\n")
        lines.append("| Test ID | Chain | Point | Vector Class |\n")
        lines.append("|--------:|------:|-------|--------------|\n")
        for blocked in het_stats['blocked_tests'][:20]:
            vc = blocked.get('vector_class', 'unknown')
            lines.append(f"| {blocked.get('test_id', 'N/A')} | {blocked.get('chain_length', 'N/A')} | {blocked.get('injection_point', 'N/A')} | {vc}... |\n")
    
    lines.append("\n")
    
    # Section 6: Model-Level Analysis (Heterogeneous only)
    lines.append("## 6. Model-Level Analysis (Heterogeneous Only)\n\n")
    lines.append("This section examines which model in the chain passed through or blocked injections.\n\n")
    
    lines.append("| Model | Total Attempts | Persisted | Persistence Rate | Blocked | Block Rate |\n")
    lines.append("|-------|---------------|----------:|----------------:|-------:|----------:|\n")
    
    for model_name, data in het_stats['by_hop_model'].items():
        rate = data['persisted'] / data['total'] * 100 if data['total'] > 0 else 0
        block_rate = 100 - rate
        lines.append(f"| {model_name} | {data['total']} | {data['persisted']} | {rate:.1f}% | {data['total'] - data['persisted']} | {block_rate:.1f}% |\n")
    
    lines.append("\n")
    
    # Section 7: Conclusions
    lines.append("## 7. Conclusions\n\n")
    
    lines.append("### Finding 1: Heterogeneous Chain Security Impact\n\n")
    lines.append(f"Heterogeneous chains showed a {diff:+.1f}% persistence rate compared to {hom_rate:.1f}% for homogeneous chains.\n\n")
    
    if abs(diff) < 1.0:
        lines.append("**Assessment:** No meaningful difference. Chain heterogeneity did not improve or worsen security.\n\n")
    elif diff > 0:
        lines.append("**Assessment:** Heterogeneous chains were slightly more persistent. This suggests that different models may have complementary vulnerabilities.\n\n")
    else:
        lines.append("**Assessment:** Heterogeneous chains showed slightly reduced persistence. This could suggest complementary security barriers, but more testing would be needed to confirm.\n\n")
    
    # Section 8: Limitations
    lines.append("## 8. Limitations\n\n")
    lines.append("1. Only homogeneous Claude chains were tested; we don't have a Gemini-only baseline\n")
    lines.append("2. Only chain length 4 was tested (Claude→Gemini→Claude→Gemini)\n")
    lines.append("3. Gemini Flash used, not Gemini Pro\n")
    lines.append("4. Results based on keyword-based detection\n\n")
    
    return lines

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--het-results', default='documents/research/multi_agent/chain_tests/comprehensive_results/het_final_4_claude.json')
    parser.add_argument('--hom-results', default='documents/research/multi_agent/chain_tests/comprehensive_results/final_results.json')
    parser.add_argument('--output', default='documents/research/multi_agent/analysis/het_comparison.md')
    args = parser.parse_args()
    
    print("Loading heterogeneous test results...")
    het_stats = analyze_heterogeneous(args.het_results)
    
    print("Loading homogeneous test results...")
    hom_stats = analyze_homogeneous(args.hom_results)
    
    print("Generating comparison report...")
    report = generate_comparison_report(het_stats, hom_stats)
    
    with open(args.output, 'w') as f:
        for line in report:
            f.write(line)
    
    print(f"\nReport written to: {args.output}")
    print(f"\nSummary:")
    print(f"  Homogeneous: {hom_stats['total']} tests, persistence rate {hom_stats['total'] - hom_stats['total'] + sum(v['persisted'] for v in hom_stats['by_vector_class'].values())) / hom_stats['total'] * 100:.1f}%")
    print(f"  Heterogeneous: {het_stats['total']} tests, persistence rate {het_stats['total'] - het_stats['total'] + sum(v['persisted'] for v in het_stats['by_vector_class'].values())) / het_stats['total'] * 100:.1f}%")
