---
name: subagent-driven-development
description: >-
  Executes an approved implementation plan through fresh implementer and
  reviewer agents for each task, with explicit handoffs, focused tests, and
  task-by-task integration. Use for multi-task work where independent agent
  context improves implementation and review quality. Not for a single small
  edit, an unresolved design, or a failure that still needs root-cause analysis.
---

# Subagent-Driven Development

Use fresh context to reduce author bias, while keeping the plan and evidence
as the shared contract.

## Before dispatch

- Confirm the design and implementation plan are approved.
- Create or select an isolated workspace when concurrent edits need it.
- Split the plan into tasks with disjoint ownership and explicit interfaces.
- Define the focused test and review gate for each task.
- Prepare a compact handoff packet from
  [handoff-packet.md](references/handoff-packet.md). Include verified facts and
  portable anchors, not a full conversation dump or the expected solution.

## Per-task cycle

1. Give the implementer the handoff packet, repository rules, and only the
   context needed for the task. Ask it to edit the files directly and report
   evidence.
2. Inspect the implementation diff and run the focused test yourself.
3. Give a fresh reviewer the task contract, diff, and test output—not the
   implementer's private reasoning or your expected answer.
4. Validate every finding against the real code path.
5. Fix in scope, rerun proof, and only then dispatch the next task.

If a task reveals a design contradiction, stop and return to
`solution-design`/`implementation-planning`; do not make the subagent silently redesign the
system. Keep unrelated agents independent and close them when finished.

## Integration

The coordinator owns final interfaces, conflict resolution, broader tests, and
the completion claim. Agent success is an input, never final evidence. Use
`requesting-code-review` for a final aggregate review and
`completion-verification` for closure.

## Completion condition

Every task has implementer evidence and reviewer disposition, the integrated
branch passes its relevant checks, and remaining limits are visible.
