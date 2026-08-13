# Interface contract checklist

| Area | Questions |
| --- | --- |
| Inputs | Required, optional, defaults, limits, encoding, validation? |
| Outputs | Stable fields, nullability, ordering, pagination, caching? |
| Errors | Machine code, safe message, retryability, status, correlation ID? |
| Auth | Authentication, authorization, tenant isolation, audit? |
| Reliability | Idempotency key, timeout, retry, backoff, duplicate delivery? |
| Evolution | Additive path, deprecation window, migration, version owner? |
| Operations | Metrics, logs, tracing, rate limits, alerts, runbook? |
| Tests | Contract, negative, compatibility, load, and consumer checks? |

For events, add producer/consumer ownership, schema version, delivery
semantics, replay behavior, and poison-message handling.
