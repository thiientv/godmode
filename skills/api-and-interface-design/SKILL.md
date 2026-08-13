---
name: api-and-interface-design
description: >-
  Designs or reviews HTTP, REST, GraphQL, RPC, CLI, webhook, event, and
  service interfaces with explicit inputs, outputs, errors, compatibility,
  idempotency, pagination, authentication, versioning, and observability. Use
  when introducing or changing an API or cross-component contract. Not for
  internal implementation details with no boundary or for debugging one API
  failure; use root-cause-debugging there.
---

# API and Interface Design

Design the contract from the caller's failure modes, not only the happy path.

## Establish the contract

1. Identify consumers, trust boundaries, lifecycle, latency expectations, and
   ownership.
2. Define request/command shape, response/event shape, status or error model,
   validation, defaults, and canonical examples.
3. Decide idempotency, retries, ordering, pagination, concurrency, rate limits,
   cancellation, and partial failure behavior.
4. Define authentication, authorization, sensitive fields, and audit needs.
5. Decide compatibility and versioning: additive change, migration, deprecation,
   or explicit breaking release.

Read [contract-checklist.md](references/contract-checklist.md) for the review
matrix. Keep the contract close to the owning schema or source of truth and
generate clients/docs only when the repository already supports generation.

## Implementation handoff

Write examples that can become contract tests. Include malformed input,
missing resource, duplicate request, timeout, dependency failure, permission
denial, and oversized input cases. Make error codes stable enough for callers
and messages safe enough for logs and users.

Do not expose internal stack traces, persistence identifiers, or implementation
details by accident. Do not add versioning machinery before a compatibility
need exists.

## Completion condition

Consumers can predict valid requests, successful and failed responses, retry
behavior, compatibility impact, and the evidence that proves the boundary.
