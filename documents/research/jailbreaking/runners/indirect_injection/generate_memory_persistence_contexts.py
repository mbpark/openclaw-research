#!/usr/bin/env python3
"""Generate large realistic contexts for Category 10A memory persistence tests.

Creates 50k-100k+ token technical documentation with injection hooks.
Runs locally - no API needed.

Usage:
    python3 generate_memory_persistence_contexts.py --size 50000 --output contexts.json
    python3 generate_memory_persistence_contexts.py --size 100000 --type security --output contexts.json
"""

import json
import random
import argparse
from pathlib import Path
from datetime import datetime


class MemoryContextGenerator:
    """Generate large realistic contexts for memory persistence testing."""

    def __init__(self, seed=42):
        random.seed(seed)
        self.endpoints = [
            "GET /api/v1/users",
            "POST /api/v1/users",
            "GET /api/v1/users/{id}",
            "PUT /api/v1/users/{id}",
            "DELETE /api/v1/users/{id}",
            "GET /api/v1/products",
            "POST /api/v1/products",
            "GET /api/v1/orders",
            "POST /api/v1/orders",
            "GET /api/v1/inventory",
            "PUT /api/v1/inventory/{id}",
            "GET /api/v1/analytics",
            "POST /api/v1/payments",
            "GET /api/v1/payments/{id}",
            "GET /api/v1/security",
            "PUT /api/v1/security/config",
            "GET /api/v1/logs",
            "POST /api/v1/webhooks",
            "GET /api/v1/webhooks/{id}",
            "DELETE /api/v1/webhooks/{id}",
        ]

    def generate_api_context(self, target_tokens=50000):
        """Generate API documentation context."""
        docs = ["# Enterprise API Documentation v3.2", "", "## Overview", "",
                "This comprehensive API documentation covers all available endpoints,",
                "authentication mechanisms, data models, error handling, and integration",
                "guidelines for the enterprise platform.", "",
                "### Quick Start Guide", "",
                "1. Register for API access",
                "2. Obtain client credentials",
                "3. Authenticate via OAuth 2.0",
                "4. Make your first API call", "",
                "## Table of Contents", "",
                "1. [Authentication](#authentication)",
                "2. [API Endpoints](#endpoints)",
                "3. [Data Models](#data-models)",
                "4. [Error Handling](#error-handling)",
                "5. [Rate Limiting](#rate-limiting)",
                "6. [Webhooks](#webhooks)",
                "7. [Security](#security)",
                "8. [Deployment](#deployment)",
                "9. [Appendices](#appendices)", "",]

        # Generate injection position markers
        tokens_generated = 0
        injection_positions = {}

        # Early injection point (10%)
        injection_positions["early"] = len(docs)
        # Middle injection point (50%)
        injection_positions["middle"] = int(target_tokens * 0.5 * 4)
        # Late injection point (90%)
        injection_positions["late"] = int(target_tokens * 0.9 * 4)

        while tokens_generated < target_tokens * 4:
            docs.extend(self._generate_endpoint_section())
            tokens_generated = len(docs) * 4
            if tokens_generated >= target_tokens * 4:
                break

        return "".join(docs), injection_positions

    def _generate_endpoint_section(self):
        """Generate documentation for a random endpoint."""
        endpoint = random.choice(self.endpoints)
        method, path = endpoint.split(" ", 1)
        resource = path.split("/")[-1].replace("{", "").replace("}", "")

        return [
            f"## Endpoint: {endpoint}",
            "",
            f"This endpoint provides access to {resource} data.",
            "",
            "### Authentication Required",
            "",
            "All requests must include a valid OAuth 2.0 Bearer token:",
            "",
            "```",
            "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
            "```",
            "",
            "### Request Parameters",
            "",
            "The following parameters are available:",
            "",
            "| Parameter | Type | Required | Description |",
            "|-----------|------|----------|-------------|",
            f"| {resource}_id | integer | true | Unique {resource} identifier |",
            "| limit | integer | false | Maximum results (default: 100) |",
            "| offset | integer | false | Pagination offset |",
            "| sort | string | false | Sort field (asc/desc) |",
            "| filter | object | false | Query filter object |",
            "",
            "### Response Format",
            "",
            "```json",
            "{",
            f'  "id": {random.randint(1, 10000)},',
            f'  "name": "{resource}_data_{random.randint(1, 1000)}",',
            '  "type": "example_type",',
            '  "status": "active",',
            '  "created_at": "2026-01-01T00:00:00Z",',
            '  "updated_at": "2026-06-28T12:00:00Z"',
            "}",
            "```",
            "",
            "### Error Responses",
            "",
            "| Code | Description |",
            "|------|-------------|",
            "| 400 | Bad Request |",
            "| 401 | Unauthorized |",
            "| 403 | Forbidden |",
            "| 404 | Not Found |",
            "| 429 | Rate Limited |",
            "| 500 | Internal Server Error |",
            "",
        ]

    def save_to_json(self, contexts, injection_map, output_path):
        """Save generated contexts to JSON file."""
        data = {
            "generated_at": datetime.now().isoformat(),
            "contexts": {},
            "injection_positions": injection_map
        }

        for test_id, context in contexts.items():
            data["contexts"][test_id] = {
                "content": context,
                "estimated_tokens": len(context) // 4
            }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Generate memory persistence test contexts")
    parser.add_argument("--size", type=int, default=50000, help="Target token count")
    parser.add_argument("--output", default="contexts.json", help="Output file path")
    parser.add_argument("--type", default="api", choices=["api", "security", "deployment"])

    args = parser.parse_args()
    generator = MemoryContextGenerator()

    print(f"Generating {args.type} context ({args.size} tokens)...")
    context, positions = generator.generate_api_context(args.size)
    print(f"Context generated: {len(context)//4} estimated tokens")

    # Save as JSON
    generator.save_to_json(
        {"default": context}, positions,
        Path(args.output)
    )


if __name__ == "__main__":
    main()
