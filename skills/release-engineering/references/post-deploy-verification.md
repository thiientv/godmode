# Post-deploy verification

Use this record for a canary, staged rollout, or high-risk production change.
It converts “watch production” into bounded observations and explicit promotion
or rollback decisions.

## Contract

- Artifact/version and environment:
- Deployment timestamp and observer:
- Baseline window and comparison source:
- Watch window and sampling interval:
- Critical user journeys and API paths:
- Regions, tenants, devices, or cohorts:
- Promote thresholds:
- Abort thresholds:
- Rollback or kill-switch command and authority:

## Observations

| Time | Build marker | HTTP/API | Browser console/network | Errors/latency/saturation | Business signal | Decision |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

Use `browser-testing` for critical browser journeys. Verify the deployed build
marker before interpreting results. Compare against the recorded baseline, not
memory. Treat missing telemetry, stale data, partial regional coverage, and
unavailable rollback authority as explicit blockers or limitations.

## Closeout

- Final promote, hold, or rollback decision:
- Evidence locations and freshness:
- Recovery verification, if rolled back:
- Delayed effects still being watched:
- Owner and expiry for temporary controls:
