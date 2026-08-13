---
name: database-design
description: >-
  Designs or reviews relational, document, key-value, graph, or search data
  models with ownership, invariants, access paths, migrations, consistency,
  retention, privacy, and recovery behavior. Use for schema changes, new data
  stores, indexes, migrations, persistence boundaries, or query-driven design.
  Not for a query-only bug without a model change or for API contract design.
---

# Database Design

Start from invariants and access patterns; a schema is an operational contract.

## Design sequence

1. Identify entities, ownership, lifecycle, source of truth, cardinality, and
   deletion/retention rules.
2. Write invariants and transaction boundaries before choosing tables or
   collections.
3. Map real reads, writes, filters, sorts, joins, uniqueness, and expected
   scale. Add indexes for measured access paths, not guesses.
4. Decide consistency, isolation, idempotency, concurrency, and failure
   recovery at each boundary.
5. Design an expand-migrate-contract migration: backward-compatible expand,
   backfill/dual-write when needed, cutover, verification, and cleanup.
6. Protect sensitive data with least privilege, encryption, minimization,
   auditability, and retention limits.

Read [schema-checklist.md](references/schema-checklist.md). Include rollback,
backup/restore, lock duration, online migration behavior, and observability in
the plan. Treat production data as irreplaceable unless a tested recovery path
proves otherwise.

## Evidence

Use representative query plans, migration rehearsal on a safe fixture, invariant
tests, concurrency checks, and restore evidence. A migration that applies once
is not proven safe to roll forward, retry, or roll back.

## Completion condition

The model's invariants, access paths, migration lifecycle, privacy boundary,
recovery path, and proof commands are explicit.
