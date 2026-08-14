# Godmode architecture

Godmode is a portable Agent Skills catalog with thin harness adapters and
dependency-free repository tooling. The public interface is the set of skill
directories under `skills/`; manifests and hooks distribute the same catalog
without creating a second behavior system.

## Layers

```text
Native Agent Skills discovery
        ↓ name + description
Public workflow skills ──────┐
  solution design             │
  planning/execution          │
  TDD/debugging               ├── compose at task boundaries
  review/verification         │
  worktree/subagent delivery  │
Public expert skills ─────────┘
  frontend/UI, API, database, security, performance,
  testing, browser, documentation, observability,
  orientation, research, migration, release, architecture,
  simplification, behavior validation, agent eval, incidents
        ↓ on demand
SKILL.md procedure → references → deterministic helper (when earned)
        ↓
Fresh evidence and explicit limits
```

## Why the vocabulary is explicit

Workflow states have different trigger conditions, user expectations, and
handoffs. A task can need solution design without execution, execution without
solution design, or review after another agent's work. The catalog therefore
keeps literal responsibilities separate instead of routing all of them through
`build` or inheriting another project's vocabulary.

The initial foundation's compact names were replaced before public release:

| Old foundation | Current boundary |
| --- | --- |
| `shape` | `solution-design` and `implementation-planning` |
| `build` | `plan-execution` and `test-driven-development` |
| `investigate` | `root-cause-debugging` |
| `review` | `requesting-code-review` and `receiving-code-review` |
| `prove` | `completion-verification` |
| `craft-ui` | `frontend-design` and `ui-ux-review` |
| `brainstorming` | `solution-design` |
| `writing-plans` | `implementation-planning` |
| `executing-plans` | `plan-execution` |
| `systematic-debugging` | `root-cause-debugging` |
| `verification-before-completion` | `completion-verification` |
| `finishing-a-development-branch` | `branch-integration` |

This is a pre-1.0 breaking vocabulary change. The names are recognizable, but
the instructions are rewritten for Godmode and do not copy another project's
implementation.

## Public skill contract

Each `skills/<name>/` contains:

```text
SKILL.md                 frontmatter, trigger boundary, procedure, stop condition
references/              templates/checklists loaded only when needed
scripts/                 deterministic helpers only when repetition earns one
```

`SKILL.md` stays under 500 lines. Its frontmatter description carries all
activation information because the body is loaded only after discovery. The
repository validator also checks name/directory alignment, local links, body
limits, frontmatter shape, and one routing fixture per public skill.

`catalog.json` is the machine-readable source for the workflow and engineering
groups. Repository validation requires it to match discovered skills, routing
fixtures, both README catalogs, and the catalog narrative. Every entry has a
distinct activation boundary; exploratory testing, contract testing, handoff,
transcript handling, CI mechanics, and provider knowledge remain references or
plugin-pack candidates rather than public micro-skills.

## Routing and composition

Native client discovery is the source of truth. The local lexical router is a
regression tripwire only; it catches missing trigger vocabulary and obvious
description collisions but does not pretend to understand intent.

Descriptions should:

- say what the skill does;
- name concrete activation contexts;
- name at least one adjacent non-activation case;
- avoid generic words that make every skill compete.

The hook bootstrap supplies shared safety and evidence rules, not every skill
body. A client may activate multiple skills when the task crosses boundaries.
Handoffs are guidance rather than an unconditional sequence.

## UI/UX capability design

`frontend-design` combines the useful design-system, stack-aware, responsive,
accessibility, and anti-generic principles found in the UI/UX references with a
small original searchable design-intelligence catalog and deterministic
design-brief helper. `ui-ux-review` is separate so building and reviewing an
existing surface have different activation rules.

The helper deliberately does not ship a large copied style database. Its
original catalog covers style, color, typography, product, layout,
accessibility, and UX patterns. A separate extractor inventories existing
tokens and repeated values before redesign. The static audit reports
conservative semantic, responsive, focus, form, image-layout, and motion
concerns. The workflow still requires a rendered state/viewport matrix,
keyboard traversal, and accessibility tooling for visual or usability claims.

## Evaluation model

Routing and behavior are different evaluation surfaces:

```text
Routing fixture → did the right skill rank near the top?
Behavior case   → did an isolated run produce the required artifact and proof?
Baseline diff   → did quality improve without protected regressions or excess cost?
Native trace    → did a real client discover and execute the skill as expected?
```

The lexical router is a cheap collision detector. `scripts/behavior_eval.py`
stores portable case and run records without executing models. Native clients
or CI adapters own execution; raw artifacts remain separate from grader output.
No aggregate score can override a failed required assertion.

## Verification model

Every workflow follows this contract:

```text
Claim → falsifiable check → fresh result → explicit limit
```

TDD proves a behavior seam, debugging proves a cause and regression, review
tests the contract and risk from a fresh perspective, browser/design skills
inspect the real surface, and `completion-verification` closes the
aggregate claim. None of these layers is allowed to stand in for the others.

## Distribution

- Agent Skills-compatible clients consume `skills/` directly.
- Claude Code uses `.claude-plugin/` plus the thin `hooks/` adapter.
- Codex direct loading uses `.codex-plugin/`; the marketplace entry publishes
  only `skills/`, whose nested `.codex-plugin/plugin.json` is the package
  manifest, keeping the local plugin package surface intentionally narrow.
- Other harnesses can copy the standard skill directories or add their own
  adapter without changing the skill bodies.

Harness-specific behavior belongs in adapters and compatibility notes. Core
instructions must not assume a Claude-only command, Codex-only tool, or one
model's hidden behavior.

## Repository tooling

The repository uses only the Python standard library for validation and tests.
`npm run check` runs frontmatter/link/body validation, manifest validation,
routing fixtures, behavior case validation, catalog and compatibility drift,
workflow and public-file security, helper tests, and catalog tests. Release
archives are extracted and validated before publication. Catalog health remains
advisory so rough token estimates or lexical similarity cannot retire a skill
automatically. The toolchain is intentionally not a hidden runtime dependency
of installed skills.

## Non-goals

- An opaque autonomous router that replaces native discovery.
- A mandatory workflow sequence for every task.
- A giant data catalog before the maintenance and licensing story exists.
- A universal UI score that substitutes for browser and human judgment.
- Claims of cross-harness behavior without a native check or an explicit limit.
