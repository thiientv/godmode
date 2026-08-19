# Engineering lifecycle

Godmode skills are reusable procedures, but a coding agent also needs a durable model of where a task is in its engineering lifecycle. This document defines that model without introducing a mandatory workflow for every task.

## States

```text
DISCOVERY → DESIGN → PLANNING → IMPLEMENTATION → TESTING → REVIEW → VERIFICATION → RELEASE → DONE
```

States are checkpoints, not a fixed sequence. Risk and evidence determine which states are required. A skipped state is not represented as completed.

| State | Purpose | Exit evidence |
| --- | --- | --- |
| `DISCOVERY` | establish repository, constraints, and task boundary | task boundary |
| `DESIGN` | decide the intended solution | design decision |
| `PLANNING` | turn the design into executable work | implementation plan |
| `IMPLEMENTATION` | make the scoped change | changed scope |
| `TESTING` | prove changed behavior | fresh test result |
| `REVIEW` | obtain an independent risk check | review result |
| `VERIFICATION` | validate the aggregate completion claim | evidence ledger |
| `RELEASE` | safely ship a validated change | rollout evidence |
| `DONE` | record a defensible completion state | valid evidence ledger |

## Durable task state

`.godmode/task.json` is the durable state record. It stores the current state, risk, completed states, active skills, evidence references, next observable check, explicit limits, and timestamps. `.godmode/checkpoints/` contains point-in-time snapshots; `.godmode/events.jsonl` contains append-only execution events.

The `scripts/godmode.py` CLI exposes `init`, `status`, `resume`, `checkpoint`, `set-state`, `risk`, `impact`, and `invalidate` operations. Recovery prefers durable task state, then repository artifacts, and never requires conversational memory.

## Evidence freshness

Evidence is scoped to files and records the originating commit plus a content digest. If a scoped file changes, the evidence is invalidated. Invalid evidence cannot satisfy lifecycle gates.

The evidence contract remains:

```text
Claim → falsifiable check → fresh result → explicit limit
```

## Risk-aware release

Low-risk work can complete after verification without a release state. Medium- and high-risk changes can release when their required evidence is present. Critical changes require review, rollout evidence, and an explicit rollback capability. The machine-readable policy is in `lifecycle.json`.

## Recovery

When context is lost, reconstruct state from durable artifacts before asking the agent to continue. Prefer `.godmode/task.json`, checkpoints, events, plans, tests, reviews, and the evidence ledger over conversational memory.

## Risk proportionality

A trivial local edit can use a single verification check. Public API changes, migrations, security-sensitive changes, production incidents, and data-destructive operations should normally traverse more states and collect stronger evidence.

The lifecycle is therefore a **risk-aware state machine**, not a mandatory waterfall.
