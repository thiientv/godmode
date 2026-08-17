# Engineering lifecycle

Godmode skills are reusable procedures, but a coding agent also needs a durable model of where a task is in its engineering lifecycle. This document defines that model without introducing a mandatory workflow for every task.

## States

```text
DISCOVERY → DESIGN → PLANNING → IMPLEMENTATION → TESTING → REVIEW → VERIFICATION → RELEASE → DONE
```

States are checkpoints, not a fixed sequence. Low-risk work may skip states when the task evidence makes them unnecessary. A skipped state must not be confused with a completed state.

| State | Purpose | Typical skills | Exit evidence |
| --- | --- | --- | --- |
| `DISCOVERY` | establish repository, constraints, and task boundary | `codebase-orientation`, `technical-research` | relevant files, constraints, unknowns |
| `DESIGN` | decide the intended solution | `solution-design`, `architecture-review` | accepted design decision |
| `PLANNING` | turn the design into executable work | `implementation-planning` | ordered plan with checks |
| `IMPLEMENTATION` | make the scoped change | `plan-execution`, domain skills | changed files and local checks |
| `TESTING` | prove changed behavior | `test-driven-development`, `test-strategy`, `browser-testing` | fresh test results |
| `REVIEW` | obtain an independent risk check | `requesting-code-review`, `receiving-code-review` | review findings and disposition |
| `VERIFICATION` | validate the aggregate completion claim | `completion-verification`, `behavior-validation` | evidence ledger and explicit limits |
| `RELEASE` | safely ship a validated change | `release-engineering` | rollout evidence |
| `DONE` | record a defensible completion state | `completion-verification` | no unverified required claim |

## Task state contract

A task state record should answer four questions:

1. Where are we?
2. What has actually been completed?
3. What evidence supports those claims?
4. What is the next observable check?

Example:

```json
{
  "state": "IMPLEMENTATION",
  "completed": ["DISCOVERY", "DESIGN", "PLANNING"],
  "active_skills": ["plan-execution", "test-driven-development"],
  "next_check": "run the focused regression test",
  "limits": ["OAuth provider was not exercised"]
}
```

## Recovery

When context is lost, reconstruct state from durable artifacts before asking the agent to continue:

- `git status` and `git diff`;
- task or issue description;
- implementation plan and TODOs;
- test results;
- review comments;
- behavior artifacts;
- evidence ledger, when present.

Recovery should prefer observed repository state over conversational memory.

## Risk proportionality

Risk controls the depth of the lifecycle. A trivial local edit can use a single verification check. Public API changes, migrations, security-sensitive changes, production incidents, and data-destructive operations should normally traverse more states and collect stronger evidence.

The lifecycle is therefore a **risk-aware state machine**, not a mandatory waterfall.
