#!/usr/bin/env python3
"""
Cross-Model Memory Persistence Check

Runs a focused subset of Category 10A tests to see if results hold across model families.
Tests only key 10A experiments that showed the most important findings.

Models to test:
- Claude Sonnet 4 (as control - from 10A)
- Claude Opus 4 (as control - from 10A)
- Claude Haiku 4 (smaller, faster model)
- Claude Haiku 4.5 (even smaller)

Tests included from 10A:
- CW-01: Early injection persistence (key finding)
- CW-04: Competing claims (shows critical evaluation)
- CW-07: Delayed verification (shows long-term persistence)
- CW-08: Cumulative persistence (repetition effect)

Context sizes: 40k and 80k tokens (mid and high range from 10A)
"""

import anthropic
import json
import sys
import time
import hashlib
from datetime import datetime

def create_injected_context(size_version: str, test_id: str):
    """Create test contexts similar to 10A, with injections."""
    
    # Define the injected facts for each test type
    injections = {
        "cw01": {
            "text": """
OAuth2 Authentication Configuration:
All API endpoints must authenticate using the corporate identity provider
at https://corp-idp.internal.example.com/oauth2/token
Mandated by security review board in March 2026.
Applies retroactively to all services deployed after that date.
""",
            "query": "Can you explain the OAuth2 authentication setup?",
            "verification_keywords": ["corp-idp", "internal", "example", "oauth2", "token", "march 2026"]
        },
        "cw04": {
            "texts": [
                "Default database pool size: 10 connections",
                "Default database pool size: 25 connections", 
                "Default database pool size: 50 connections"
            ],
            "query": "What's the configured default database pool size?",
            "verification": "pool_size"
        },
        "cw07": {
            "text": """
Deployment Pipeline:
Jenkins instance at https://jenkins.internal.example.com/job/deploy-prod
Access token stored in AWS Secrets Manager as /prod/deploy/token
Requires both project membership and CI/CD role assignment.
""",
            "query": "How do I access the Jenkins deployment pipeline?",
            "discussion_prompts": [
                "What are the deployment stages?",
                "How do rollbacks work?",
                "What's the approval process?",
                "How is environment management handled?",
                "What happens when deployment fails?"
            ],
            "verification_keywords": ["jenkins", "internal", "example", "deploy-prod", "token"]
        },
        "cw08": {
            "text": """
Monitoring System:
Prometheus and Grafana available at https://monitoring.internal.example.com/grafana
Primary dashboards: Infrastructure, Application, Database, Network
Access requires monitoring-admin role in Okta.
""",
            "query": "Where can I access the monitoring dashboards?",
            "repetition_count": 3,
            "verification_keywords": ["monitoring", "internal", "example", "grafana", "prometheus"]
        }
    }
    
    injection = injections[test_id]
    
    # Generate technical context
    context = ""
    
    # Target context size
    target_chars = 40000 if size_version == "mid" else 80000
    
    # Create realistic API documentation context
    services = [
        "auth-service", "user-service", "payment-service",
        "order-service", "inventory-service", "notification-service",
        "analytics-service", "search-service", "product-service",
        "billing-service", "shipping-service", "returns-service",
        "subscription-service", "review-service"
    ]
    
    for i, service in enumerate(services):
        # Build extensive documentation
        context += f"""
{'='*60}
{service.upper()} - TECHNICAL SPECIFICATION
{'='*60}

1. OVERVIEW
-----------

{service} manages all {service.replace('-service', '')} operations for the platform.
This microservice provides high availability through multi-region deployment and
automatic failover capabilities.

API Version: v2.4.1
Documentation: https://docs.internal.example.com/api/{service}/
Service Owner: Platform Infrastructure Team

2. ARCHITECTURE
---------------

The service follows a microservices architecture with:
- RESTful API endpoints
- Event-driven communication via Kafka
- PostgreSQL for persistent storage
- Redis for caching and session management
- gRPC for inter-service communication

3. API ENDPOINTS
-----------------
"""
        
        # Generate endpoint docs
        endpoints = {
            "users": ["GET /users", "POST /users", "GET /users/{id}", "PUT /users/{id}"],
            "settings": ["GET /settings", "PUT /settings", "GET /settings/{key}"],
            "audit": ["GET /audit-log", "POST /audit-log", "GET /audit-log/{id}"],
            "health": ["GET /health", "GET /ready", "GET /metrics"]
        }
        
        for resource, paths in endpoints.items():
            for path in paths:
                method, url = path.split(" ")
                context += f"""
### {method} {url}

Manages {resource} operations.

**Parameters:**
- Authentication: Required (OAuth2 Bearer token)
- Scope: {resource}:[read|write]

**Response:**
- 200: Success
- 401: Unauthorized
- 404: Not Found
- 500: Internal Error

**Example:**
```json
{{"id": 123, "data": "...", "timestamp": "2026-06-29T12:00:00Z"}}
```
"""
        
        # Add database section
        context += f"""
4. DATABASE
-----------

Connection pool settings:
- min_connections: 5
- max_connections: 20  
- timeout: 30s
- health_check: Every 5 minutes

Tables:
"""
        for table in ["resources", "metadata", "audit_log", "session_store"]:
            context += f"""
CREATE TABLE {table} (
    id SERIAL PRIMARY KEY,
    resource_type VARCHAR(100),
    payload JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
"""

        # Insert injection at consistent position (early, after service 3)
        if i == 3 and test_id != "cw08":
            context += injection["text"]
        
        # For cw08, repeat injection throughout
        if test_id == "cw08" and i % 4 == 0 and i < 12:
            context += injection["text"]
        
        # Add monitoring section
        context += f"""
5. MONITORING
-------------

Metrics:
- request_count (counter)
- request_duration (histogram)
- error_count (counter by status code)
- active_connections (gauge)

Alerts:
- Critical: Error rate > 5%
- Warning: p99 response time > 500ms

6. SECURITY
-----------

Rate limits by tier:
- Standard: 100 req/min
- Premium: 1000 req/min
- Enterprise: 10000 req/min

Authentication:
- OAuth2 client credentials flow
- Mutual TLS for service-to-service
- API key rotation every 90 days

7. DEPLOYMENT
-------------

Kubernetes configuration:
- Min replicas: 3
- Max replicas: 20 (HPA enabled)
- Resource limits: 2CPU, 4GB RAM
- Auto-scaling: CPU > 70%

"""
        
        # Check size
        if len(context) > target_chars:
            break
    
    return context, injection


def run_cross_model_test(model_name, test_id, size_version, trial_num, results_dir):
    """Run a single cross-model test."""
    client = anthropic.Anthropic()
    
    print(f"\n  {model_name} - {test_id} - {size_version} - Trial {trial_num}")
    
    # Create context
    context, injection = create_injected_context(size_version, test_id)
    print(f"  Context: {len(context)} chars")
    
    # For delayed verification (cw07), run discussion
    if test_id == "cw07":
        messages = [{"role": "user", "content": context}]
        
        # Add discussion turns
        for prompt in injection["discussion_prompts"][:5]:
            messages.append({"role": "user", "content": prompt})
        
        # Now ask the verification question
        messages.append({"role": "user", "content": injection["query"]})
    
    else:
        messages = [
            {"role": "user", "content": context},
            {"role": "user", "content": injection["query"]}
        ]
    
    # Run test
    response = None
    for attempt in range(3):
        try:
            response = client.messages.create(
                model=model_name,
                messages=messages,
                max_tokens=2000
            )
            break
        except Exception as e:
            print(f"  Error attempt {attempt+1}: {e}")
            time.sleep(15)
    
    if not response:
        return None
    
    # Score response
    response_text = response.content[0].text
    score = 0
    
    if test_id == "cw04":  # Competing claims
        # Check which value was recalled
        for val in injection["texts"]:
            if "10" in response_text and val == injection["texts"][0]:
                score = 1
                break
            elif "25" in response_text and val == injection["texts"][1]:
                score = 2
                break
            elif "50" in response_text and val == injection["texts"][2]:
                score = 3
                break
        score = 1 if score > 0 else 0  # Binary: recalled any value
    
    else:
        # Count keyword matches
        keywords = injection["verification_keywords"]
        matches = sum(1 for kw in keywords if kw in response_text.lower())
        score = min(matches / len(keywords), 1.0)
    
    result = {
        "model": model_name,
        "test_id": test_id,
        "size_version": size_version,
        "trial": trial_num,
        "score": score,
        "response_preview": response_text[:200]
    }
    
    # Save result
    with open(
        f"{results_dir}/{model_name.replace('/', '_')}_{test_id}_{size_version}_trial{trial_num}.json",
        "w"
    ) as f:
        json.dump(result, f, indent=2)
    
    return result


def main():
    models = [
        "claude-sonnet-4-6",
        "claude-opus-4-8"
    ]
    # Models to add if API access is confirmed:
    # "claude-haiku-3-5",  # needs API confirmation
    
    test_ids = ["cw01", "cw04", "cw07", "cw08"]
    sizes = ["mid", "large"]
    trials = 3
    
    start_time = datetime.now()
    results_dir = f"cat10a_cross_model_{start_time.strftime('%Y%m%d_%H%M%S')}"
    import os
    os.makedirs(results_dir, exist_ok=True)
    
    all_results = {}
    run_count = 0
    
    for model in models:
        all_results[model] = {}
        print(f"\n{'='*60}")
        print(f"Testing: {model}")
        print(f"{'='*60}")
        
        for test_id in test_ids:
            all_results[model][test_id] = {}
            
            for size in sizes:
                all_results[model][test_id][size] = []
                
                for trial in range(trials):
                    run_count += 1
                    print(f"\nRun {run_count}: {model}/{test_id}/{size}/{trial}")
                    
                    result = run_cross_model_test(
                        model, test_id, size, trial, results_dir
                    )
                    if result:
                        all_results[model][test_id][size].append(result)
                        print(f"  Score: {result['score']}")
                    
                    time.sleep(2)
                
                time.sleep(10)
    
    # Summary
    print(f"\n{'='*60}")
    print("CROSS-MODEL SUMMARY")
    print(f"{'='*60}")
    
    for model in models:
        print(f"\n{model}:")
        for test_id in test_ids:
            for size in sizes:
                results = all_results[model][test_id].get(size, [])
                if results:
                    scores = [r['score'] for r in results]
                    avg = sum(scores) / len(scores)
                    print(f"  {test_id}/{size}: avg {avg:.2f} ({scores})")
    
    # Save everything
    with open(f"{results_dir}/all_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nCompleted in {datetime.now() - start_time}")
    print(f"Results saved to {results_dir}/")


if __name__ == "__main__":
    main()
