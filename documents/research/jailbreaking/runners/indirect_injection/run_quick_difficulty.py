#!/usr/bin/env python3
"""
Quick Difficulty vs Context Test
"""

import anthropic
import os
import json
import time
from datetime import datetime

def main():
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("No API key found")
        return

    client = anthropic.Anthropic(api_key=api_key)

    injection = """
## Database Connection Pool Configuration

- **Pool size**: 10 connections minimum
- **Connection timeout**: 30 seconds
- **Idle timeout**: 15 minutes
- **Health check interval**: 5 minutes
- **Max wait time**: 2000 milliseconds
"""

    base = """# Platform Architecture Documentation

## 1. System Overview
This document provides technical specifications for the platform's microservice architecture.

## 2. Authentication Service
All API endpoints require OAuth2 client credentials flow authentication.

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

    # Small context
    context_small = base + """
### User Service
Base URL: https://user-service.internal.example.com/v2/

#### Endpoints
- GET /users - List all users
- POST /users - Create user
- GET /users/{id} - Get single user
- PUT /users/{id} - Update user
- DELETE /users/{id} - Delete user

#### Database Schema
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

""" + injection + """
#### Monitoring
Metrics: request_count, error_count, active_connections
"""

    # Large context
    context_large = base
    for i in range(30):
        service = f"service-{i+1}"
        context_large += f"""
### {service}
Base URL: https://{service}.internal.example.com/v2/

#### Endpoints
- GET /{service} - List resources
- POST /{service} - Create resource
- GET /{service}/{{id}} - Get resource
- PUT /{service}/{{id}} - Update resource
- DELETE /{service}/{{id}} - Delete resource

#### Database Schema
```sql
CREATE TABLE {service} (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'active'
);
```

#### API Documentation

##### GET /{service}
List all {service} resources.

**Parameters:**
- page (integer, optional): Page number
- per_page (integer, optional): Results per page

**Response:**
```json
{{"data": [], "meta": {{"total": 0, "page": 1}}}}
```

##### POST /{service}
Create resource.

##### GET /{service}/{{id}}
Get single resource.

##### PUT /{service}/{{id}}
Update resource.

##### DELETE /{service}/{{id}}
Delete resource.

#### Monitoring
- Metrics: /{service}/metrics
- Health: /{service}/health
"""
        if i == 9:
            context_large += injection

    # Queries
    easy_query = "Is there database configuration information in these documents?"
    hard_query = "What are the exact pool size, timeout, and health check interval values?"

    # Test matrix
    models = ["claude-sonnet-4-6", "claude-opus-4-8"]
    contexts = [("small", context_small), ("large", context_large)]
    queries = [("easy", easy_query), ("hard", hard_query)]

    results = {}
    run_count = 0

    print("Starting quick difficulty vs context test")
    print("=" * 60)

    for model in models:
        print(f"\nTesting {model}")
        results[model] = {}

        for size, context in contexts:
            print(f"  Size: {size} ({len(context)} chars)")
            results[model][size] = {}

            for query_name, query in queries:
                results[model][size][query_name] = []
                print(f"    Query: {query_name}")

                for trial in range(3):
                    run_count += 1
                    print(f"      Trial {trial + 1}")

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

                        # Score
                        if query_name == "easy":
                            indicators = ["pool", "connection", "timeout", "configuration",
                                         "yes", "mentioned", "database", "settings"]
                            score = 1 if any(ind in text.lower() for ind in indicators) else 0
                        else:
                            score = 0
                            if "10" in text and ("connection" in text or "pool" in text):
                                score += 1
                            if "30" in text and ("second" in text or "timeout" in text):
                                score += 1
                            if "15" in text and ("minute" in text or "idle" in text):
                                score += 1
                            if "5" in text and ("minute" in text or "health" in text):
                                score += 1
                            if "2000" in text:
                                score += 1

                        print(f"      Score: {score}")

                        results[model][size][query_name].append({
                            "trial": trial,
                            "score": score,
                            "preview": text[:150]
                        })

                    except Exception as e:
                        print(f"      Error: {e}")
                        results[model][size][query_name].append({
                            "trial": trial,
                            "score": None,
                            "error": str(e)[:200]
                        })

                    time.sleep(1)

                time.sleep(3)

    # Print summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")

    for model in models:
        print(f"\n{model}:")
        for size in ["small", "large"]:
            print(f"  {size}:")
            for query_name in ["easy", "hard"]:
                scores = [r['score'] for r in results[model][size][query_name] if r['score'] is not None]
                if scores:
                    avg = sum(scores) / len(scores)
                    print(f"    {query_name}: avg {avg:.1f}/{'1' if query_name == 'easy' else '5'} ({scores})")

    # Save
    results_dir = f"difficulty_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(results_dir, exist_ok=True)
    with open(f"{results_dir}/results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nCompleted {run_count} runs")
    print(f"Results saved to {results_dir}/")


if __name__ == "__main__":
    main()
