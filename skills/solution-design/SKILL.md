---
name: solution-design
description: >-
  Explores ambiguous product or engineering intent before implementation,
  clarifies users, constraints, alternatives, risks, and acceptance criteria,
  and turns the result into an approved design direction. Use for a new
  feature, subsystem, creative UI, architecture change, or unclear request.
  Not for an already-scoped bug fix, an existing implementation plan, or a
  narrow code review.
---

# Solution Design

Make the problem concrete before choosing the solution. The goal is shared
understanding, not a long ceremony.

## Classify the request

- **Spike:** the output is a recommendation or feasibility result; keep any
  prototype disposable.
- **Bounded:** an existing flow is understood and the change is narrow; use a
  short design and one approval gate.
- **Architectural:** the request creates a subsystem, changes a public
  contract, or has several independent surfaces; write a design artifact.

When uncertain, choose the heavier path until discovery proves otherwise.

## Explore in order

1. Read repository instructions, nearby code, tests, and recent changes.
2. Separate observed facts from assumptions and unknowns.
3. Ask only the questions that change scope, safety, data shape, or user
   outcome. Ask one focused question at a time when a conversation is needed.
4. State the outcome, users, constraints, non-goals, acceptance evidence, and
   principal risks.
5. Compare two or three viable approaches when the choice is material. Explain
   the trade-off and recommend the smallest safe option.
6. Present the design at the depth the request requires. Get approval before
   consequential implementation when the user has not already authorized it.

Use [discovery-questions.md](references/discovery-questions.md) when the brief
has unclear goals or competing stakeholders.

## Design artifact

For architectural work, save a concise design under the repository's normal
docs location. Include:

```text
Problem and users
Outcome and non-goals
Constraints and assumptions
Options considered and recommendation
Interfaces and data affected
Failure modes and rollback
Acceptance evidence
Open decisions
```

Do not start implementation while a decision that materially changes the
public behavior, data model, or safety boundary is unresolved.

## Handoff

- Hand an approved multi-step design to `implementation-planning`.
- Hand a concrete failure to `root-cause-debugging`.
- Add a domain skill only when its expertise changes the design.

## Completion condition

Solution design is complete when the outcome, scope, constraints, acceptance
evidence, risks, and next decision are explicit. A polished idea without a
testable outcome is not a completed design.
