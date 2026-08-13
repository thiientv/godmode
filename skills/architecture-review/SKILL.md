---
name: architecture-review
description: >-
  Reviews an existing codebase for structural friction, unclear ownership,
  leaky or shallow interfaces, excessive coupling, misplaced state, poor
  testability, and risky dependency direction, then prioritizes evidence-backed
  improvement candidates. Use for architecture audits, modularization,
  modernization, or recurring cross-cutting change pain. Not for designing one
  new interface, simplifying a local function, or fixing a reproduced bug.
---

# Architecture Review

Find structural changes that reduce the cost and risk of likely future work.
Do not produce a generic best-practices checklist.

## Scope the review

Use `codebase-orientation` first when ownership and execution paths are not
known. Focus on the user-named subsystem or on evidence-backed hotspots from
history, incidents, change coupling, and test failures. Read relevant ADRs and
domain vocabulary before proposing alternatives.

## Inspect structural pressure

Look for:

- behavior spread across many callers instead of owned behind one interface;
- interfaces that expose nearly as much complexity as they hide;
- dependency cycles, unstable direction, duplicated policy, and hidden global
  state;
- abstractions with one hypothetical implementation or pass-through layers;
- tests that require internal knowledge because the public seam is wrong;
- concepts named inconsistently across code, data, and product language.

Apply the deletion test: if removing a module only moves its complexity into
every caller, it may be earning its place; if complexity disappears, it may be
ceremony. Use [candidate-report.md](references/candidate-report.md) to compare
current and proposed ownership.

## Prioritize, do not redesign silently

Rank candidates by observed friction, expected locality/leverage, migration
risk, reversibility, and relevance to upcoming work. Include a smallest useful
change and explicit non-goals. Mark speculative ideas as speculative.

Hand an approved candidate to `solution-design` and
`implementation-planning`; use `code-simplification` when no architectural
boundary changes.

## Completion condition

The report ties each candidate to repository evidence, shows current and
proposed ownership, respects existing decisions or explicitly challenges them,
and recommends a bounded first move without implementing an unapproved
redesign.
