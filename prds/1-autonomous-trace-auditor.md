# PRD: Autonomous Trace Auditor

**Issue**: [#1](https://github.com/insidemedia/trace-auditor/issues/1)
**Priority**: High
**Status**: In Progress
**Created**: 2026-05-14
**Author**: @insidemedia

---

## Problem Statement

Local LLM traffic running through the LiteLLM gateway on the dss-k3s-01 cluster generates traces in Langfuse, but there is **no automated quality assurance layer** reviewing those traces. Errors such as context window overflows, inference timeouts, and malformed prompts go undetected until a user manually notices degraded output or reports an issue.

This creates a blind spot in the observability stack — telemetry data exists, but nobody is reviewing it systematically.

## Solution Overview

Build a **lightweight, transient Kubernetes CronJob** that acts as an automated QA engineer for LLM traffic:

1. **Runs every 15 minutes** via a K3s CronJob with minimal resource footprint
2. **Fetches recent traces** from Langfuse tagged with errors or high latency using the Langfuse Python SDK
3. **Analyzes each trace** using Pydantic AI, routing inference through the internal LiteLLM gateway to determine root cause
4. **Outputs structured JSON** conforming to a strict Pydantic BaseModel schema — containing Trace ID, Issue Category, Root Cause, and Recommended Fix
5. **Delivers results to stdout** for pickup by standard Kubernetes logging (MVP)

## Technical Architecture

### Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Runtime | Python 3.12+ | Application runtime |
| Framework | Pydantic AI | Structured LLM output + agent orchestration |
| LLM Gateway | LiteLLM (cluster-internal) | Route inference to local models |
| Trace Source | Langfuse Python SDK | Fetch error/latency traces |
| Scheduling | Kubernetes CronJob | 15-minute trigger cycle |
| Output | JSON to stdout | K8s log aggregation (MVP) |

### Data Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  K3s CronJob │────▶│   Langfuse   │────▶│  Pydantic AI │────▶│   stdout     │
│  (15 min)    │     │  SDK Fetch   │     │  + LiteLLM   │     │  (JSON logs) │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### Output Schema (Pydantic BaseModel)

```python
from pydantic import BaseModel, Field

class TraceAuditResult(BaseModel):
    trace_id: str
    issue_category: str = Field(description="E.g., Context Overflow, Prompt Injection, Inference Timeout, Format Error")
    root_cause: str = Field(description="A concise explanation of why the trace failed or lagged.")
    recommended_fix: str = Field(description="Actionable step to prevent this in the future.")
    severity: str = Field(description="Low, Medium, High, or Critical")
```

### Integration Points

| System | Endpoint | Auth |
|--------|----------|------|
| Langfuse | `http://langfuse.dss-k3s-01` | API keys via K8s Secret |
| LiteLLM | `http://litellm.100.80.0.55.nip.io/v1` | `sk-litellm-admin` via K8s Secret |

### Resource Requirements

| Resource | Request | Limit |
|----------|---------|-------|
| CPU | 100m | 250m |
| Memory | 128Mi | 256Mi |
| Ephemeral Storage | — | 100Mi |

## User Journey

1. CronJob fires every 15 minutes
2. Python script initializes Langfuse SDK client
3. Fetches traces from the last 15-minute window where `status=error` or `latency > threshold`
4. For each problematic trace:
   - Extracts relevant context (input, output, metadata, error message)
   - Sends to Pydantic AI agent with LiteLLM backend
   - Receives structured `TraceAuditResult`
5. Prints each result as formatted JSON to stdout
6. Pod exits cleanly (exit code 0 if no errors, 1 if SDK/connectivity failures)

## Success Criteria

- [ ] CronJob runs reliably every 15 minutes without manual intervention
- [x] Successfully connects to Langfuse and fetches recent error traces
- [x] Pydantic AI produces valid, structured JSON output for every analyzed trace
- [ ] Root cause classifications are meaningful and actionable (not generic)
- [ ] Resource usage stays within defined limits (no OOM kills)
- [ ] Zero impact on cluster stability — fully transient workload

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Langfuse API unavailable | Low | Medium | Retry with backoff, graceful exit |
| LiteLLM gateway down | Low | High | Health check before processing, skip run |
| No error traces in window | High | None | Log "no issues found", exit cleanly |
| LLM hallucinated root cause | Medium | Low | Confidence score + category constraints |
| CronJob overlap (slow run) | Low | Low | `concurrencyPolicy: Forbid` |

## Out of Scope (MVP)

- Alerting (Slack, PagerDuty, email notifications)
- Historical trend analysis / dashboards
- Automated remediation actions
- Multi-cluster support
- Custom trace query filters via config

## Future Enhancements

- **v1.1**: Push audit results to a dedicated Langfuse dataset for tracking
- **v1.2**: Webhook/Slack integration for critical findings
- **v1.3**: Trend analysis — detect recurring failure patterns over time
- **v2.0**: Closed-loop remediation — auto-restart services, adjust rate limits

---

## Milestones

### Milestone 1: Project Scaffolding & Local Dev
- [x] Python project structure with `pyproject.toml` (Pydantic AI, Langfuse SDK, httpx)
- [x] Dockerfile for minimal Python container
- [x] Local development working with `.env` configuration

### Milestone 2: Langfuse Trace Ingestion
- [x] Langfuse SDK client connects and authenticates
- [x] Fetch traces by time window with error/latency filters
- [x] Extract relevant fields from trace objects for analysis

### Milestone 3: Pydantic AI Analysis Pipeline
- [x] Pydantic AI agent configured with LiteLLM endpoint
- [x] Structured output schema enforced via `TraceAuditResult` model
- [x] Root cause analysis prompt tuned for accuracy

### Milestone 4: Kubernetes CronJob Deployment
- [ ] CronJob manifest with proper scheduling, resource limits, and concurrency policy
- [ ] Secrets management for Langfuse and LiteLLM credentials
- [ ] Container image built and pushed to registry

### Milestone 5: Integration Testing & Validation
- [ ] End-to-end test with real Langfuse traces on dss-k3s-01
- [ ] Verify JSON output appears in `kubectl logs`
- [ ] Confirm resource usage stays within limits across multiple runs

### Milestone 6: Documentation & Operational Readiness
- [ ] README with setup, configuration, and troubleshooting guide
- [ ] Deployment instructions for K3s cluster
- [ ] Runbook for common failure modes
