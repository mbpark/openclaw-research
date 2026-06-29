#!/usr/bin/env python3
"""
Test #1: Difficulty vs Context - Investigating Gemini's Query-Specific Degradation

Tests whether query-specific recall degradation is due to:
- Query difficulty (harder questions = harder to answer correctly)
- Context pressure (more context = degraded recall regardless of difficulty)

Design:
- Same factual content injected at consistent position
- Two query types:
  - EASY: Simple yes/no recall (e.g., "Is there a password requirement mentioned?")
  - HARD: Specific detail extraction (e.g., "What exact endpoint is used and what's the version?")
- Two context sizes: SMALL (30k tokens) and LARGE (100k tokens)
- 4 conditions per model: SmallEasy, SmallHard, LargeEasy, LargeHard

If degradation only occurs on LargeHard: it's difficulty + context interaction
If degradation occurs on SmallHard but not SmallEasy: it's pure difficulty
If degradation occurs on LargeEasy: it's genuine context pressure
If no degradation: Test 4 result was noise/anomaly
"""

import anthropic
import json
import sys
import time
import hashlib
from datetime import datetime

def create_context_pair(difficulty_version: str, size_version: str):
    """Create matched context with known injection point."""

    # Fixed injected fact that all tests share
    INJECTED_FACT = """
Database Connection Pool Configuration:
- Pool size: 10 connections (minimum)
- Connection timeout: 30 seconds
- Idle timeout: 15 minutes
- Health check interval: 5 minutes
- Connection validation query: SELECT 1
- Maximum wait time: 2000 milliseconds
"""

    # Easy query: simple recognition
    easy_query = "Is there information about database connection settings in these documents?"

    # Hard query: specific detail extraction
    hard_query = "What are the exact pool size, timeout, and health check configuration values?"

    # Generate context
    context = ""

    if size_version == "small":
        target_tokens = 30_000
    else:
        target_tokens = 100_000

    # Build API docs context
    microservices = [
        "auth-service", "user-service", "payment-service",
        "order-service", "inventory-service", "notification-service",
        "analytics-service", "search-service", "recommendation-service",
        "billing-service", "shipping-service", "customer-service",
        "product-service", "review-service", "shipping-service",
        "returns-service", "refund-service", "subscription-service"
    ]

    for i, service in enumerate(microservices):
        # Write extensive API documentation
        context += f"""
============================================================
{service.upper()} - API Documentation
============================================================

1. SERVICE OVERVIEW
-------------------

{service} handles all {service.replace('-service', '').replace('_', ' ')} related operations.
This service is deployed across multiple availability zones and provides high availability
through automatic failover and load balancing.

API Version: v2.4.1
Base URL: https://{service}.internal.example.com/v2/
Documentation: https://docs.internal.example.com/api/{service}/

2. AUTHENTICATION
-----------------

All API endpoints require authentication using OAuth2 client credentials flow.
The following scopes are supported:
- read:{service} - Read access to {service} data
- write:{service} - Write access to {service} data
- admin:{service} - Administrative access to {service} configuration

3. API ENDPOINTS
-----------------
"""

        # Generate endpoint documentation
        endpoints = [
            ("GET", "/{resource}", "List all resources"),
            ("GET", "/{resource}/{id}", "Get single resource"),
            ("POST", "/{resource}", "Create new resource"),
            ("PUT", "/{resource}/{id}", "Update resource"),
            ("DELETE", "/{resource}/{id}", "Delete resource"),
            ("PATCH", "/{resource}/{id}", "Partial update"),
            ("GET", "/{resource}/{id}/related", "Get related resources"),
            ("POST", "/{resource}/{id}/actions/{action}", "Execute action"),
        ]

        for method, path, description in endpoints:
            context += f"""
### {method} {path}

{description}

**Request Parameters:**
- id (integer, path): Unique identifier for the resource

**Query Parameters:**
- page (integer, optional): Page number for pagination (default: 1)
- per_page (integer, optional): Results per page (default: 20, max: 100)
- sort (string, optional): Sort field
- order (string, optional): Sort order (asc/desc)
- filter (object, optional): Filter criteria

**Response Codes:**
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Rate Limited
- 500: Internal Server Error
- 503: Service Unavailable

**Example Response:**
```json
{{
    "id": 12345,
    "name": "Example resource",
    "description": "Sample description",
    "created_at": "2026-06-29T12:00:00Z",
    "updated_at": "2026-06-29T12:00:00Z",
    "status": "active"
}}
```
"""

        # Add database schema info for this service
        context += f"""
4. DATABASE SCHEMA
------------------

Tables for {service}:
"""
        for table in ["resources", "resource_metadata", "resource_history", "resource_relations"]:
            context += f"""
CREATE TABLE {table} (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    CONSTRAINT {table}_name_check CHECK (status IN ('active', 'inactive', 'archived', 'deleted'))
);
"""

        # Insert the injected fact at the same position (after 5 services)
        if i == 5:
            context += INJECTED_FACT

        # Add monitoring, deployment, security sections
        context += f"""
5. MONITORING
-------------

Metrics:
- request_count (counter): Total API requests
- request_duration (histogram): Request duration in seconds
- error_count (counter): Total errors by status code
- active_connections (gauge): Active database connections

Alerts:
- Critical: Error rate > 5%
- Warning: Response time p99 > 500ms
- Info: Active connections > 80% of pool size

6. DEPLOYMENT
-------------

Environment: Kubernetes
Deployment type: Rolling update
Minimum replicas: 3
Maximum replicas: 20 (HPA enabled)
Health check: /healthz endpoint
Readiness check: /ready endpoint
Liveness check: /live endpoint

7. SECURITY
-----------

Rate limits:
- Standard users: 100 requests/minute
- Premium users: 1000 requests/minute
- Service accounts: 5000 requests/minute
- Admin services: 10000 requests/minute

"""

        # Check if we've reached target token count (rough estimate: 4 chars per token)
        if len(context) > target_tokens * 4:
            break

    return context, easy_query, hard_query


def run_condition(model_name, context, query, injected_fact):
    """Run a single test condition."""

    client = anthropic.Anthropic()
    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": context},
                    {"role": "user", "content": query}
                ],
                max_tokens=2000
            )
            return response.content[0].text
        except Exception as e:
            print(f"  Error (attempt {attempt+1}): {e}")
            time.sleep(10)

    return f"ERROR after {max_retries} retries"


def score_response(response, question_type):
    """Score response for accuracy.

    Easy questions: 1 = recognized the topic, 0 = didn't
    Hard questions: 0-5 scale based on detail accuracy
    """

    if "ERROR" in response:
        return None

    if question_type == "easy":
        # Simple recognition
        indicators = [
            "pool", "connection", "timeout", "configuration",
            "yes", "mentioned", "information"
        ]
        return 1 if any(ind in response.lower() for ind in indicators) else 0

    else:  # hard - count specific details recalled
        score = 0
        response_lower = response.lower()

        # Check for each specific detail
        if "10" in response and ("connection" in response or "pool" in response):
            score += 1  # pool size
        if "30" in response and ("second" in response or "timeout" in response):
            score += 1  # connection timeout
        if "15" in response and ("minute" in response or "idle" in response):
            score += 1  # idle timeout
        if "5" in response and ("minute" in response or "health" in response):
            score += 1  # health check interval
        if "2000" in response:
            score += 1  # max wait time

        return score


def main():
    models = ["claude-sonnet-4-6", "claude-opus-4-8"]
    # Could add "gemini-2.5-pro" here but would need different client

    sizes = ["small", "large"]
    difficulties = ["easy", "hard"]
    
    start_time = datetime.now()
    start_time_str = start_time.strftime("%Y%m%d_%H%M%S")
    
    results_dir = f"cat10a_difficulty_results_{start_time_str}"
    import os
    os.makedirs(results_dir, exist_ok=True)
    
    all_results = {}
    run_count = 0
    
    for model in models:
        all_results[model] = {}
        print(f"\n{'='*60}")
        print(f"Testing: {model}")
        print(f"{'='*60}")
        
        for size in sizes:
            # Create context once per size (same content for easy/hard)
            print(f"\n  Generating {size} context...")
            context, easy_query, hard_query = create_context_pair(
                "difficulty", size
            )
            print(f"  Context size: {len(context)} chars")
            
            for difficulty in difficulties:
                query = easy_query if difficulty == "easy" else hard_query
                condition = f"{size}_{difficulty}"
                
                all_results[model][condition] = []
                
                # Run 3 trials per condition (reduced for API budget)
                for trial in range(3):
                    run_count += 1
                    print(f"\n  Run {run_count}: {condition}, trial {trial+1}")
                    
                    response = run_condition(model, context, query, None)
                    score = score_response(response, difficulty)
                    
                    result = {
                        "model": model,
                        "condition": condition,
                        "trial": trial,
                        "score": score,
                        "response_preview": response[:200]
                    }
                    all_results[model][condition].append(result)
                    
                    print(f"  Score: {score}/{'1' if difficulty == 'easy' else '5'}")
                    
                    # Save individual result
                    with open(
                        f"{results_dir}/{model.replace('/', '_')}_{condition}_trial{trial}.json",
                        "w"
                    ) as f:
                        json.dump(result, f, indent=2)
                    
                    time.sleep(2)
                
                time.sleep(10)
    
    # Calculate and print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    summary = {}
    for model in models:
        summary[model] = {}
        print(f"\n{model}:")
        
        for size in sizes:
            for difficulty in difficulties:
                condition = f"{size}_{difficulty}"
                scores = [r['score'] for r in all_results[model][condition]]
                avg_score = sum(scores) / len(scores) if scores else 0
                summary[model][condition] = {
                    "avg_score": avg_score,
                    "scores": scores,
                    "max_score": 1 if difficulty == "easy" else 5
                }
                print(f"  {condition}: avg {avg_score:.2f}/{'1' if difficulty == 'easy' else '5'} "
                      f"({scores})")
    
    # Analysis
    print(f"\n{'='*60}")
    print("ANALYSIS")
    print(f"{'='*60}")
    
    for model in models:
        print(f"\n{model}:")
        
        # Easy questions - should be unaffected by context size
        easy_small = summary[model]["small_easy"]["avg_score"]
        easy_large = summary[model]["large_easy"]["avg_score"]
        print(f"  Easy questions: Small={easy_small:.2f}, Large={easy_large:.2f}")
        
        # Hard questions - this tells us about degradation
        hard_small = summary[model]["small_hard"]["avg_score"]
        hard_large = summary[model]["large_hard"]["avg_score"]
        print(f"  Hard questions: Small={hard_small:.2f}, Large={hard_large:.2f}")
        
        # Check what happened
        if easy_large < 0.8:
            print("  ⚠️  Easy questions degrading in large context - context pressure effect!")
        if hard_large < hard_small * 0.8:
            print("  ⚠️  Hard questions worse in large context - context pressure effect!")
        if hard_small < 0.8 * 5:
            print("  ⚠️  Hard questions also degraded in small context - pure difficulty!")
    
    # Save full results
    with open(f"{results_dir}/analysis_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    with open(f"{results_dir}/summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nCompleted in {datetime.now() - start_time}")
    print(f"Results saved to {results_dir}/")
    

if __name__ == "__main__":
    main()
