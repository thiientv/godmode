# Signal design template

```markdown
Operational question:
Failure or SLO:
Owner and responder:

Trace/correlation identity:
Metric name, unit, type, dimensions:
Log events and structured fields:
Sensitive fields excluded/redacted:
Sampling/cardinality budget:
Alert threshold and duration:
Runbook and recovery:
Verification trigger:
```

Prefer stable names and units. A metric that cannot drive a decision is likely
noise; a log with an unbounded user or request field may be an operational risk.
