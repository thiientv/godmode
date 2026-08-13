---
name: plan-execution
description: >-
  Executes an existing implementation plan task by task, preserving its
  interfaces and constraints, running focused checks after each slice, and
  stopping when the repository differs from the plan. Use when a written plan
  or approved checklist already exists. Not for inventing the plan, debugging
  an unexplained failure, or broad unscoped cleanup.
---

# Plan Execution

Treat the plan as an executable contract with room for evidence-backed
corrections. Do not silently redesign it while implementing.

## Before the first task

1. Read the plan, referenced design, repository instructions, and current diff.
2. Verify the starting branch, worktree, runtime, and baseline checks.
3. Check that referenced files, commands, interfaces, and dependencies exist.
4. Identify the first task whose result can invalidate the architecture.

## Per-task loop

For each task:

1. Restate the behavior and files in scope.
2. Write or update the failing test/observation before implementation when the
   plan calls for behavior change.
3. Run the focused check and confirm the failure is meaningful.
4. Make the smallest change that satisfies the task.
5. Run the focused check, then relevant neighboring checks.
6. Inspect the diff for scope creep, accidental generated files, and contract
   drift.
7. Record the result, evidence, and remaining limit before moving on.

If a test, dependency, or interface contradicts the plan, stop at a checkpoint
and re-shape the affected task. Do not delete a check to make the plan green.

## Integration discipline

- Keep each slice buildable when practical.
- Preserve the plan's public names unless an evidence-backed correction is
  approved.
- Run the broader suite after related slices stabilize.
- Use `completion-verification` for the final claim.

## Completion condition

Execution is complete when every in-scope task has a fresh result, the final
diff matches the approved scope, and unverified surfaces are reported.
