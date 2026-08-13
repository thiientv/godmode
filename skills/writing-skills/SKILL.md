---
name: writing-skills
description: >-
  Creates or improves an Agent Skill by defining a precise trigger boundary,
  concise procedural instructions, progressive-disclosure references,
  deterministic helpers, routing evals, and validation evidence. Use when
  authoring or reviewing SKILL.md, skill metadata, bundled references, or skill
  packaging. Not for ordinary project documentation or application code.
---

# Writing Skills

Write a skill for another agent to use under pressure. Context is a shared
budget, so every paragraph must earn its place.

## Design the boundary

1. Collect concrete prompts that should and should not activate the skill.
2. Name the responsibility in plain language and use a short verb-led name.
3. Put all activation conditions in frontmatter `description`; the body loads
   only after activation.
4. Keep `SKILL.md` procedural and under 500 lines.
5. Move detailed rules, variants, schemas, and examples into one-level-deep
   `references/` files.
6. Add a script only for deterministic repeated work, with `--help` and tests.

Use [skill-checklist.md](references/skill-checklist.md) before opening a PR.

## Write and test

- Use Agent Skills-compatible `name` and `description` frontmatter.
- State when to use, when not to use, safety boundaries, workflow, handoffs,
  and completion evidence.
- Avoid copying a reference repository's text, names, examples, or scripts;
  rewrite principles and record provenance.
- Add at least three positive and two negative routing cases, including close
  neighbors that must not activate.
- Create two or three realistic behavior cases with observable outputs and
  edge conditions before expanding the suite.
- Run each case in a fresh context with the candidate skill and with no skill or
  a frozen previous version. Keep prompts, fixtures, model settings, and output
  locations identical.
- Capture artifacts, public trace/tool summaries, duration, and usage. Grade
  deterministic assertions first and use blinded rubric or human review for
  judgment-heavy output.
- Optimize description triggering on a training set and choose the final result
  by a held-out validation set; do not paste missed query keywords into the
  description until fixtures pass by accident.
- Run the repository validator and at least one realistic forward test for a
  behavior-changing skill.

Descriptions should be specific enough to distinguish neighboring skills, but
not so broad that every task activates the skill.

Use `agent-evaluation` for the baseline/candidate result format and regression
analysis. Read [evaluation-loop.md](references/evaluation-loop.md) before
claiming that a skill improves agent behavior.

## Completion condition

A skill is ready when its trigger boundary is understandable, its body is
actionable, its links and helpers work, its routing cases generalize, and a
realistic isolated comparison produces better evidence than the baseline
without an unacceptable cost or protected-metric regression.
