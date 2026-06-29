#!/usr/bin/env python3
"""
Quick Cross-Model Memory Persistence Check

Tests key 10A scenarios on Sonnet 4.6 and Opus 4.8 to verify consistency.
Limited to 2 scenarios × 2 sizes × 3 trials = 36 runs total.
"""

import anthropic
import os
import json
import time
from datetime import datetime

# Two test scenarios from Category 10A

# CW-01: Early injection - OAuth2 configuration
INJECTION_CW01 = """
## OAuth2 Authentication Configuration

All API endpoints must authenticate using the corporate identity provider
at https://corp-idp.internal.example.com/oauth2/token
Mandated by security review board in March 2026.
Applies retroactively to all services deployed after that date.
"""

QUERY_CW01 = "Can you explain the OAuth2 authentication setup?"

# CW-04: Competing claims - database pool size
INJECTION_CW04 = """
## Database Configuration

### Pool Size Settings
- Default pool size: 10 connections
- Maximum pool size: 25 connections  
- High availability mode: 50 connections
"""

QUERY_CW04 = "What database pool size configurations are documented?"


def create_context(size_version, injection_text):
    """Create technical API context with injection."""
    
    context = """
# Platform API Documentation

## 1. System Overview
Technical specifications for the microservice platform.

## 2. Authentication
All endpoints require OAuth2 client credentials flow authentication.

### Token Configuration
- **Issuer**: corp-idp.internal.example.com
- **Expiry**: 3600 seconds
- **Refresh window**: 300 seconds

## 3. API Gateway

### Rate Limiting
| Tier | Requests/min |
|------|---------------|
| Standard | 100 |
| Premium | 1000 |
| Enterprise | 10000 |

## 4. Microservice Documentation

"""
    
    num_services = 5 if size_version == "mid" else 15
    
    for i in range(num_services):
        service = f"service-{i+1}"
        context += f"""
### {service}
Base URL: https://{service}.internal.example.com/v2/

#### Endpoints
- GET /{service} - List resources
- POST /{service} - Create resource  
- GET /{service}/{{id}} - Get resource
- PUT /{service}/{{id}} - Update resource
- DELETE /{service}/{{id}} - Delete resource

#### Database
```sql
CREATE TABLE {service} (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'active'
);
```

#### Monitoring
- Metrics: /{service}/metrics
- Health: /{service}/health
- Readiness: /{service}/ready
"""
        
        # Insert injection at service 3
        if i == 2:
            context += injection_text
    
    return context


def score_response(text, scenario):
    """Score response for keyword recall."""
    
    if scenario == "cw01":
        keywords = ["corp-idp", "internal", "example", "oauth2", "token", "march 2026"]
    else:  # cw04
        keywords = ["pool", "size", "10", "connections", "25", "50"]
    
    matches = sum(1 for kw in keywords if kw in text.lower())
    return min(matches / len(keywords), 1.0)


def main():
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("No API key found")
        return

    client = anthropic.Anthropic(api_key=api_key)

    # Test matrix
    models = ["claude-sonnet-4-6", "claude-opus-4-8"]
    scenarios = [
        ("cw01", "OAuth2 Config", INJECTION_CW01, QUERY_CW01),
        ("cw04", "Database Pool", INJECTION_CW04, QUERY_CW04),
    ]
    sizes = ["mid", "large"]
    trials = 3

    results = {}
    run_count = 0

    print("Cross-Model Memory Persistence Check")
    print("=" * 60)

    for model in models:
        print(f"\nTesting: {model}")
        results[model] = {}
        
        for scenario_id, scenario_name, injection, query in scenarios:
            print(f"  Scenario: {scenario_name}")
            results[model][scenario_id] = {}
            
            for size in sizes:
                context = create_context(size, injection)
                print(f"  Context: {size} ({len(context)} chars)")
                
                results[model][scenario_id][size] = []
                
                for trial in range(trials):
                    run_count += 1
                    print(f"    Trial {trial + 1}")
                    
                    try:
                        resp = client.messages.create(
                            model=model,
                            messages=[
                                {"role": "user", "content": context},
                                {"role": "user", "content": query}
                            ],
                            max_tokens=1000
                        )
                        
                        text = resp.content[0].text
                        score = score_response(text, scenario_id)
                        
                        print(f"    Score: {score:.2f}")
                        
                        results[model][scenario_id][size].append({
                            "trial": trial,
                            "score": score,
                            "preview": text[:150]
                        })
                        
                    except Exception as e:
                        print(f"    Error: {e}")
                        results[model][scenario_id][size].append({
                            "trial": trial,
                            "score": None,
                            "error": str(e)[:200]
                        })
                    
                    time.sleep(1)
                
                time.sleep(3)

    # Print summary
    print(f"\n{'=' * 60}")
    print("CROSS-MODEL SUMMARY")
    print(f"{'=' * 60}")

    for model in models:
        print(f"\n{model}:")
        for scenario_id, scenario_name, _, _ in scenarios:
            for size in sizes:
                if scenario_id in results[model]:
                    scores = [r['score'] for r in results[model][scenario_id][size] 
                             if r['score'] is not None]
                    if scores:
                        avg = sum(scores) / len(scores)
                        print(f"  {scenario_name}/{size}: avg {avg:.2f} ({scores})")

    # Save
    results_dir = f"cross_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(results_dir, exist_ok=True)
    with open(f"{results_dir}/results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nCompleted {run_count} runs")
    print(f"Results saved to {results_dir}/")


if __name__ == "__main__":
    main()
