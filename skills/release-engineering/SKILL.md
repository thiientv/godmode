---
name: release-engineering
description: >-
  Prepares and controls software releases with risk classification, CI quality
  gates, artifact provenance, feature flags, staged rollout, measurable
  promotion and rollback thresholds, post-deploy verification, and cleanup.
  Use for deployment pipelines, launch readiness, canaries, production rollout,
  release automation, or rollback planning. Not for merely merging a completed
  development branch or proving one local change.
---

# Release Engineering

Turn a release into a sequence of evidence-backed decisions rather than one
irreversible event.

## Build the release contract

Record the artifact/version, environments, owner, change scope, affected users,
data or contract changes, dependencies, risk class, maintenance window, and
success metrics. Use [release-record.md](references/release-record.md) for the
go/no-go and rollout record.

## Establish gates

Require checks proportional to risk: build and tests, contract and migration
proof, security findings, performance budgets, smoke paths, accessibility or
visual checks, artifact signing/provenance, monitoring, and a tested recovery
path. A green generic pipeline is not proof of the release's critical behavior.

## Roll out safely

1. Separate deployment from exposure with a flag or routing control when
   practical.
2. Start with internal, shadow, canary, or low-percentage traffic.
3. Compare errors, latency, saturation, business outcomes, and support signals
   against a pre-release baseline.
4. Promote only after the observation window and all gates pass.
5. Roll back or disable immediately when a predefined threshold is crossed.
6. Verify recovery, communicate status, and preserve the timeline.

For canaries and production observation windows, use
[post-deploy-verification.md](references/post-deploy-verification.md). Confirm
the deployed build marker, run critical browser journeys through
`browser-testing`, and record each promote, hold, or rollback decision against
fresh baseline evidence.

Use immutable artifacts across environments. Keep release credentials out of
logs and command lines. Require explicit authority for production mutation.

## Close the release

Verify critical paths after deployment, monitor delayed jobs and regional
effects, remove stale flags and compatibility paths on schedule, update release
notes, and create owned follow-ups for non-blocking debt. Never substitute a
successful deployment command for an observation window. Use
`incident-response` if live impact begins and `safe-migrations` for stateful
cutovers.

## Completion condition

The intended artifact reached the intended audience, promotion evidence and
remaining limits are recorded, rollback readiness was real, and temporary
release controls have owners and expiry dates.
