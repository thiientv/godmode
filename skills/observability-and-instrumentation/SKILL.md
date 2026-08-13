---
name: observability-and-instrumentation
description: >-
  Designs or reviews logs, metrics, traces, alerts, correlation, dashboards,
  and diagnostic instrumentation so failures and performance changes can be
  detected and explained at component boundaries. Use for observability work,
  incident readiness, instrumentation, or production diagnostics. Not for
  fixing a specific incident before reproducing it or for adding noisy logging
  without an operational question.
---

# Observability and Instrumentation

Start from the question an operator must answer, then emit the smallest safe
signal that answers it.

## Design sequence

1. Name the user or business signal, SLO/error budget, failure mode, and
   responder.
2. Map the request or job across boundaries and choose correlation/trace IDs,
   cardinality, sampling, and clock conventions.
3. Define structured logs for state transitions and failures, metrics for
   rates/latency/saturation, and traces for cross-service causality.
4. Include useful dimensions without high-cardinality or secret data. Redact
   tokens, PII, payloads, and credentials by default.
5. Add alerts with actionable thresholds, runbook links, ownership, deduping,
   and a recovery path. Avoid alerts that merely report expected retries.
6. Verify the signal in a safe environment and test the failure path that
   should emit it.

## Prepare operational baselines

For release and incident use, record the pre-change baseline, freshness,
expected variance, promotion or paging threshold, and recovery signal. Include
one user or business outcome alongside technical health where possible. A
dashboard without a decision owner and action threshold is reference material,
not a guardrail.

Preserve a correlation path from release identifier to request, job, dependency,
and user-visible outcome. Ensure incident responders can distinguish absent
traffic, stale telemetry, collector failure, and healthy zero values.

Read [signal-design.md](references/signal-design.md). Instrumentation must not
change correctness or become the only source of truth for business data.

## Completion condition

An operator can detect the important failure, correlate it across boundaries,
understand the likely cause, and follow a bounded response without exposing
sensitive data. `release-engineering` can consume the baseline as a promotion
gate; `incident-response` can consume it as live evidence.
