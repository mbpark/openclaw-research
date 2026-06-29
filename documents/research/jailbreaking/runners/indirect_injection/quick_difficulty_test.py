#!/usr/bin/env python3
"""
Quick Difficulty vs Context Test

Directly tests whether query-specific recall degradation is due to:
- Query difficulty (harder questions are harder to answer)
- Context pressure (more context degrades recall)

Uses controlled context sizes: SMALL (~10k tokens), LARGE (~40k tokens)
Uses same injected fact, different query types (easy yes/no vs hard specifics)
"""

import anthropic
import os
import json
import time
from datetime import datetime

def create_simple_context(size_version: str):
    """Create simpler context with injected fact."""
    
    INJECTED_FACT = """
## Database Connection Pool Configuration

- **Pool size**: 10 connections minimum
- **Connection timeout**: 30 seconds  
- **Idle timeout**: 15 minutes
- **Health check interval**: 5 minutes
- **Max wait time**: 2000 milliseconds
"""

    context = """
# Platform Architecture Documentation

## 1. System Overview
This document provides comprehensive technical specifications for the platform's microservice architecture.

## 2. Authentication Service

### OAuth2 Configuration
All API endpoints require authentication via OAuth2 client credentials flow.

### Scopes
- `read:users` - Read user data
- `write:users` - Modify user records
- `admin:config` - Administrative configuration
- `read:metrics` - Access monitoring data

### Token Configuration
```yaml
token_issuer: "corp-idp.internal.example.com"
token_audience: "platform-api"
token_expiry: "3600"
refresh_window: "300"
```

### Endpoints
```
POST   /oauth2/token         - Obtain access token
POST   /oauth2/revoke         - Revoke existing token
GET    /oauth2/introspect     - Token introspection
```

## 3. API Gateway

### Rate Limiting
| Tier        | Requests/min | Burst |
|-------------|--------------|-------|
| Standard    | 100          | 15    |
| Premium     | 1000         | 100   |
| Enterprise  | 10000        | 1000  |

### Response Format
```json
{
  "status": 200,
  "data": {},
  "meta": {
    "request_id": "uuid-here",
    "rate_limit_remaining": 95
  }
}
```

## 4. Microservice Documentation

"""
    
    # Add services based on size
    services = [
        "user-service", "order-service", "payment-service",
        "inventory-service", "notification-service", "analytics-service",
        "search-service", "recommendation-service", "billing-service",
        "shipping-service", "product-service", "customer-service",
        "review-service", "subscription-service", "returns-service",
        "tax-service", "fraud-detection-service", "reporting-service"
    ]
    
    num_services = 5 if size_version == "small" else 15
    
    for i, service in enumerate(services[:num_services]):
        context += f"""
### {service}

**Base URL**: https://{service}.internal.example.com/v2/
**Version**: v2.4.1
**Owner**: Platform Team

#### Endpoints
"""
        endpoints = {
            "users": ["/users", "/users/{id}", "/users/{id}/preferences"],
            "orders": ["/orders", "/orders/{id}", "/orders/{id}/status"],
            "payments": ["/payments", "/payments/{id}", "/payments/{id}/refund"],
            "items": ["/items", "/items/{id}", "/items/{id}/stock"],
        }
        endpoint_key = f"{service.split('-')[0]}s"
        if endpoint_key not in endpoints:
            endpoint_key = "users"
        
        for ep in endpoints[endpoint_key]:
            for method in ["GET", "POST", "PUT", "DELETE"]:
                context += f"""
##### {method} {ep}

- **Description**: {method.lower()} operation for {endpoint_key}
- **Auth required**: Yes (OAuth2 Bearer)
- **Rate limit**: Tier-dependent

**Response Codes:**
- 200: Success
- 201: Created  
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Rate Limited
- 500: Internal Error

"""

        context += f"""
#### Database Schema
```sql
CREATE TABLE {service.replace('-service', '')} (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'active'
);
```

#### Monitoring
- Metrics: request_count, request_duration, error_count
- Health endpoint: /health
- Readiness: /ready
- Liveness: /live

"""
        
        # Insert injected fact at consistent position (around service 3)
        if i == 2:
            context += INJECTED_FACT
    
    return context


def main():
    # Verify API works
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("No API key found")
        return
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Models to test (just these two for now)
    models = ["claude-sonnet-4-6", "claude-opus-4-8"]
    
    # Two context sizes
    sizes = ["small", "large"]
    
    # Two query types
    easy_query = "Is there information about database connection settings in these documents?"
    hard_query = "What are the exact pool size, timeout, and health check configuration values?"
    
    # Tracking results
    results = {}
    
    for model in models:
        results[model] = {}
        print(f"\n{'='*60}")
        print(f"Testing: {model}")
        print(f"{'='*60}")
        
        for size in sizes:
            print(f"\n--- {size} context ---")
            context = create_simple_context(size)
            print(f"Context size: {len(context)} chars (~{len(context)//4} tokens)")
            
            for query_name, query in [("easy", easy_query), ("hard", hard_query)]:
                condition = f"{size}_{query_name}"
                results[model][condition] = []
                
                # Run 3 trials
                for trial in range(3):
                    print(f"\nTrial {trial+1}: {condition}")
                    
                    try:
                        response = client.messages.create(
                            model=model,
                            messages=[
                                {"role": "user", "content": context},
                                {"role": "user", "content": query}
                            ],
                            max_tokens=1000
                        )
                        
                        response_text = response.content[0].text
                        print(f"Response preview: {response_text[:150]}...")
                        
                        # Score
                        if query_name == "easy":
                            indicators = ["pool", "connection", "timeout", "configuration",
                                         "yes", "mentioned", "database"]
                            score = 1 if any(i in response_text.lower() for i in indicators) else 0
                        else:  # hard - count specific details
                            score = 0
                            if "10" in response_text and ("connection" in response_text or "pool" in response_text):
                                score += 1
                            if "30" in response_text and ("second" in response_text or "timeout" in response_text):
                                score += 1
                            if "15" in response_text and ("minute" in response_text or "idle" in response_text):
                                score += 1
                            if "5" in response_text and ("minute" in response_text or "health" in response_text):
                                score += 1
                            if "2000" in response_text:
                                score += 1
                        
                        print(f"Score: {score}/{1 if query_name == 'easy' else '5'}")
                        
                        results[model][condition].append({
                            "trial": trial,
                            "score": score,
                            "preview": response_text[:200]
                        })
                        
                    except Exception as e:
                        print(f"Error: {e}")
                        results[model][condition].append({
                            "trial": trial,
                            "score": None,
                            "error": str(e)
                        })
                    
                    time.sleep(2)
                
                time.sleep(5)
    
    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for model in models:
        print(f"\n{model}:")
        for size in sizes:
            for query_name in ["easy", "hard"]:
                condition = f"{size}_{query_name}"
                scores = [r['score'] for r in results[model][condition] if r['score'] is not None]
                if scores:
                    avg = sum(scores) / len(scores)
                    print(f"  {condition}: avg {avg:.1f}/{'1' if query_name == 'easy' else '5'} ({scores})")
    
    # Save results
    results_dir = f"difficulty_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(results_dir, exist_ok=True)
    
    with open(f"{results_dir}/results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {results_dir}/")
    

if __name__ == "__main__":
    main()