---
name: dispatching-parallel-agents
description: >-
  Splits a coding task into independent parallel agent workstreams with
  disjoint write sets, explicit inputs and outputs, dependency ordering, and a
  merge/review plan. Use when several subtasks can proceed without shared
  mutable state. Not for tightly coupled edits, one failing root cause, or
  parallel changes to the same files.
---

# Dispatching Parallel Agents

Parallelism reduces elapsed time only when it does not multiply integration
ambiguity.

## Dispatch checklist

1. Define the shared outcome and acceptance evidence.
2. Map dependencies and identify the critical path.
3. Split by coherent responsibility, not arbitrary file count.
4. Give every agent a disjoint write set and a narrow prompt.
5. State repository rules, interfaces, expected artifacts, and stop conditions.
6. Decide who integrates, resolves conflicts, and runs the final proof.

Good units are an independent reference/eval update, a script with its tests,
or separate adapters with a stable manifest contract. Bad units are two agents
editing the same public skill, guessing an interface that another agent owns,
or investigating one symptom with competing hypotheses.

## Handoff contract

Each agent returns:

- files changed;
- decisions and assumptions;
- commands run and exact result;
- known gaps or conflicts;
- follow-up needed by the integrator.

Treat agent output as untrusted work product. Read the diff and rerun the
relevant checks before merging. Do not claim the aggregate task is complete
because every agent reported success.

## Completion condition

Parallel work is integrated only after interface compatibility, conflict
resolution, focused checks, and one fresh aggregate verification pass.
