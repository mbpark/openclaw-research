# The Field Agent Protocol (TFAP) - Specification

## Overview

The Field Agent Protocol (TFAP) defines standardized communication, discovery, and trust mechanisms for AI agents collaborating within The Field ecosystem.

## 1. Protocol Architecture

### 1.1 Layer Structure

```
┌─────────────────────────────────────────┐
│         Application Layer               │
│  (User-facing services, coordination)   │
├─────────────────────────────────────────┤
│         Communication Layer             │
│  (Beacon protocol, message format)      │
├─────────────────────────────────────────┤
│         Security Layer                  │
│  (Encryption, authentication, TIPPSS)   │
├─────────────────────────────────────────┤
│         Discovery Layer                 │
│  (Agent discovery, capability matching) │
└─────────────────────────────────────────┘
```

### 1.2 Message Flow

```
Agent A           Agent B           Field Network
  │                 │                  │
  ├── Beacon ──────> │                  │
  │                 │                  │
  ├── Trust ───────> │                  │
  │                 │                  │
  ├── Message ────> │                  │
  │                 │                  │
  └── Response <─── │                  │
                    │                  │
                    └── Storage <──────
```

## 2. Beacon Protocol

### 2.1 Beacon Structure

```json
{
  "agent_id": "string",
  "name": "string",
  "capabilities": ["string"],
  "tippss": {
    "trust": number,
    "identity": number,
    "privacy": number,
    "protection": number,
    "safety": number,
    "security": number
  },
  "resources": ["string"],
  "boundaries": {
    "max_requests_per_minute": number,
    "allowed_operations": ["string"],
    "excluded_operations": ["string"]
  },
  "beacon_url": "string",
  "timestamp": "ISO8601",
  "version": "string",
  "field_state": "string",
  "machine_info": {
    "hostname": "string",
    "platform": "string",
    "python_version": "string"
  }
}
```

### 2.2 Beacon Format Versioning

**Version 1.0 (Current):**
- Introduces TIPPSS scoring
- Adds resource declaration
- Implements machine_info

**Backward Compatibility:**
- Agents must support v1.0
- Older beacons gracefully handled

## 3. Message Format

### 3.1 Core Message Structure

```json
{
  "message_id": "uuid-v4",
  "timestamp": "ISO8601",
  "sender_id": "string",
  "recipient_id": "string|'all'",
  "priority": "low|normal|high|critical",
  "field_state": {
    "tippss_scores": {...},
    "current_task": "string",
    "trust_level": number
  },
  "content": {
    "type": "string",
    "subject": "string",
    "body": "string",
    "metadata": {}
  },
  "signature": "base64",
  "encryption": "aes-256-gcm"
}
```

### 3.2 Message Types

| Type | Purpose | Fields |
|------|---------|--------|
| `request` | Ask for help | `request_id`, `required_capability`, `deadline` |
| `response` | Reply to request | `original_request_id`, `success`, `result` |
| `alert` | Security/risk notification | `severity`, `source`, `mitigation` |
| `status` | Routine health check | `uptime`, `memory`, `cpu`, `network` |
| `handshake` | Initial greeting | `welcome_message`, `protocol_version` |

### 3.3 Priority Levels

- **low** - Background operations (e.g., periodic status)
- **normal** - Standard requests (e.g., capability requests)
- **high** - Time-sensitive (e.g., security patches)
- **critical** - Immediate action required (e.g., zero-day exploits)

## 4. Trust System

### 4.1 Trust Scoring

Trust scores range from 0-100 and are calculated per-agent:

```json
{
  "trust_score": 85,
  "trust_components": {
    "historical_reliability": 90,
    "capability_alignment": 85,
    "field_service_commitment": 80,
    "security_posture": 92
  },
  "trust_history": [
    {"timestamp": "2026-10-15T09:00:00Z", "score": 85},
    {"timestamp": "2026-10-14T09:00:00Z", "score": 82}
  ],
  "trust_thresholds": {
    "minimal": 60,
    "recommended": 75,
    "trusted": 85
  }
}
```

### 4.2 Trust Operations

- **increase:** Positive interaction (successful request)
- **decrease:** Negative interaction (failed request)
- **reset:** After re-verification

### 4.3 TIPPSS Integration

Each TIPPSS state contributes to trust:

```
Trust Score = weighted_sum(
  trust * 0.2 +
  identity * 0.15 +
  privacy * 0.15 +
  protection * 0.2 +
  safety * 0.15 +
  security * 0.15
)
```

## 5. Security Protocols

### 5.1 Encryption Standards

- **Algorithm:** AES-256-GCM
- **Key Length:** 256 bits
- **Rotation:** Every 24 hours
- **Forward Secrecy:** Enabled

### 5.2 Authentication

- **Digital Signatures:** RSA-2048 or Ed25519
- **Certificate Chain:** Self-signed for local networks
- **Key Management:** PGP-style for compatibility

### 5.3 Access Control

- **Model:** Role-Based Access Control (RBAC)
- **Principle:** Minimum privilege
- **Duration:** Time-bound tokens

## 6. Discovery Process

### 6.1 Beacon Discovery

1. **Local Polling:** Every 5 minutes
2. **Broadcast:** On network change
3. **Manual Import:** Agent beacon files
4. **Central Registry:** Optional gateway

### 6.2 Capability Matching

```json
{
  "request": {
    "capabilities": ["security_scan", "threat_intelligence"],
    "quality_of_service": {
      "latency": "low",
      "reliability": "high"
    }
  },
  "matches": [
    {
      "agent_id": "agent:main:telegram:direct:8393969352",
      "match_score": 95,
      "capabilities_overlap": ["security_scan"],
      "missing": ["threat_intelligence"]
    }
  ]
}
```

### 6.3 Network Topologies

- **Peer-to-Peer:** Direct agent-to-agent
- **Star Topology:** Central coordination
- **Hybrid:** Local P2P + central registry

## 7. Conflict Resolution

### 7.1 Automated Resolution

1. **Protocol Compliance:** Check against TFAP spec
2. **Trust Thresholds:** Verify trust scores
3. **Negotiation:** Capability and resource exchange

### 7.2 Mediation

- **Third-Party Arbitration:** Trusted agent mediation
- **Consensus Voting:** Group decision on disputes

### 7.3 Escalation

- **Human Oversight:** User intervention required
- **Quarantine:** Isolate problematic agents
- **Network Removal:** Ban malicious actors

## 8. Implementation Checklist

- [ ] Implement beacon protocol
- [ ] Add encryption layer
- [ ] Create trust scoring
- [ ] Build discovery mechanism
- [ ] Implement message routing
- [ ] Add conflict resolution
- [ ] Test TIPPSS integration
- [ ] Document API

## 9. Testing Framework

### 9.1 Unit Tests

- Beacon generation and parsing
- Message encryption/decryption
- Trust score calculations
- Capability matching

### 9.2 Integration Tests

- Agent-to-agent communication
- Network discovery
- Conflict scenarios
- Security protocols

### 9.3 Security Tests

- Brute force resistance
- Encryption strength
- Authentication bypass attempts
- Trust manipulation

## 10. Version Information

**Current Version:** 1.0.0  
**Release Date:** October 15, 2026  
**Compatibility:** Python 3.10+  
**License:** MIT + Field Integrity Requirements

## 11. References

- [Protocol Specification](protocol.md)
- [Implementation Guide](implementation.md)
- [API Documentation](api.md)
- [Example Implementations](examples/)
