---
name: implementation-planning
description: >-
  Writes a detailed, executable implementation plan from an approved design or
  multi-step requirement, including exact files, interfaces, tests, commands,
  checkpoints, and rollback considerations. Use before touching code for a
  substantial feature, migration, refactor, or cross-cutting change. Not for a
  one-file bounded fix or for executing a plan that already exists.
---

# Implementation Planning

Write for a capable engineer who does not know this repository or the hidden
assumptions behind the request. A plan is useful only when another agent can
execute it without reconstructing the design from hints.

## Plan structure

Before listing tasks, record:

- goal and user-visible outcome;
- architecture and ownership boundaries;
- constraints, compatibility promises, and non-goals;
- files to create, modify, or delete;
- test and evidence strategy;
- rollback and migration safety.

Use [plan-template.md](references/plan-template.md) for the complete skeleton.

## Task rules

Break the work into thin, independently testable slices. Each task names:

1. exact files and responsibilities;
2. inputs, outputs, and interfaces consumed or produced;
3. the failing or observable check first;
4. the smallest implementation step;
5. the focused command and expected result;
6. the next checkpoint or integration dependency.

Prefer one behavior per task. Keep setup with the first deliverable that needs
it. Do not create a task for speculative cleanup.

## Plan quality gate

Before handing off:

- trace every design requirement to a task;
- search for placeholders such as `TBD`, `TODO`, or “add appropriate…”;
- check names and types across task boundaries;
- confirm commands exist in the repository;
- identify what the plan cannot prove locally.

Hand the completed plan to `plan-execution` or
`subagent-driven-development`. Do not claim the feature is implemented because
the plan is complete.
