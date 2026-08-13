---
name: safe-migrations
description: >-
  Designs and executes compatibility-preserving migrations across APIs,
  schemas, frameworks, dependencies, protocols, storage, and infrastructure
  with baselines, coexistence, staged cutover, rollback or forward-fix paths,
  and explicit removal criteria. Use for deprecations, upgrades, data moves,
  contract changes, and replacing live implementations. Not for a local
  refactor with no external state or compatibility boundary.
---

# Safe Migrations

Treat compatibility, state, and reversibility as first-class requirements.

## Decide whether to migrate

Identify the forcing function, affected producers and consumers, stored state,
support window, blast radius, and cost of leaving the old path in place. Reject
a migration whose benefit does not justify its operational risk.

## Establish the baseline

Before changing implementation, capture current contracts and representative
behavior: tests, state snapshots, traffic shape, performance, error semantics,
and rollback prerequisites. Existing consumers are part of the contract even
when their behavior is undocumented.

## Design coexistence and cutover

Choose a pattern from [migration-patterns.md](references/migration-patterns.md):
expand/contract, adapter, dual-read/write, shadow, strangler, or versioned
contract. Define phases, ownership, observability, data reconciliation, entry
and exit criteria, and the exact point of no return.

Prefer additive steps:

1. Introduce the new shape or implementation without removing the old one.
2. Backfill or translate state with idempotent, resumable operations.
3. Validate old and new behavior side by side.
4. Shift traffic or consumers in measured stages.
5. Hold through a defined observation window.
6. Remove compatibility code only after usage reaches the agreed threshold.

For each phase, define rollback when reversible and a forward-fix when rollback
would corrupt or discard newer state. Never label an untested rollback as a
rollback plan.

## Verification

Prove old-state/new-code and, when relevant, new-state/old-code compatibility.
Check idempotency, interruption recovery, reconciliation, mixed-version
operation, and empty-plan/no-diff behavior. Pair production cutover with
`release-engineering` and data modeling with `database-design`.

## Completion condition

The migration has phase-specific evidence, measurable cutover and abort gates,
an owned recovery path, and explicit cleanup criteria; no destructive removal
occurs while supported consumers or unreconciled state remain.
