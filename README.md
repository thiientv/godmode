# Godmode

[English](README.md) | [简体中文](README.zh-CN.md)

**Your coding agent already knows how to code.<br>
Godmode teaches it how to engineer.**

[![Release](https://img.shields.io/github/v/release/thiientv/godmode)](https://github.com/thiientv/godmode/releases/latest)
[![Validate](https://github.com/thiientv/godmode/actions/workflows/validate.yml/badge.svg)](https://github.com/thiientv/godmode/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/thiientv/godmode)](LICENSE)

Godmode is a composable catalog of engineering workflows and expert
capabilities for AI coding agents. It helps agents design before editing, test
before claiming, review independently, and verify with fresh evidence.

## The problem

Coding agents are good at producing code. Without explicit engineering
behavior, they can start too early, miss existing conventions, bolt tests on at
the end, and call a plausible-looking result complete.

```text
WITHOUT GODMODE

"Build authentication"
        ↓
code immediately
        ↓
tests, security, and integration considered late
        ↓
looks done


WITH GODMODE

"Build authentication"
        ↓
solution design
        ↓
API + database + security expertise
        ↓
implementation plan
        ↓
test-driven development
        ↓
independent review
        ↓
fresh verification
        ↓
verified result
```

## Composition, not one giant prompt

Godmode equips compatible agents to discover and compose the engineering
behavior required by a task. Native skill discovery remains the routing
authority; Godmode supplies focused boundaries, procedures, references, and
deterministic helpers.

```text
                 USER TASK

"Build a production analytics dashboard"

                     ↓
                  Godmode

       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
solution-design frontend-design test-strategy
       │             │             │
       └─────────────┼─────────────┘
                     ↓
      implementation-planning + TDD
                     ↓
              browser-testing
                     ↓
                ui-ux-review
                     ↓
          completion-verification
```

This is an example composition, not a mandatory pipeline. A small task may need
one skill; a consequential task may combine workflow and domain expertise.

### More compositions

```text
New API with persistence:
  solution-design + api-and-interface-design + database-design
  → implementation-planning → TDD → security-and-hardening

Flaky browser regression:
  root-cause-debugging + browser-testing
  → test-driven-development → completion-verification

Stateful production migration:
  safe-migrations + test-strategy + observability-and-instrumentation
  → release-engineering → behavior-validation

Active production impact:
  incident-response → root-cause-debugging
  → test-driven-development → completion-verification
```

## More than Markdown

Godmode skills use the smallest implementation that earns its maintenance cost.
Some are concise procedures with progressive references. Repeated or
error-prone work can also include deterministic tooling.

`frontend-design` is the current quality bar: it combines a workflow, design
and interaction references, stack-aware guidance, a searchable design catalog,
design-system extraction, static UI auditing, and rendered verification. The
goal is not to make every skill ship a script; it is to give each domain the
knowledge and tools needed to produce evidence-backed work.

## Install

### Agent Skills-compatible clients

Copy the public catalog into a project-scoped skills directory:

```bash
mkdir -p .agents/skills
cp -R /absolute/path/to/godmode/skills/* .agents/skills/
```

Clients that support a skills installer can install the repository directly.

### Claude Code

```bash
claude --plugin-dir /absolute/path/to/godmode
claude plugin validate /absolute/path/to/godmode
```

The thin SessionStart hook supplies shared operating rules; native skill
discovery remains responsible for selecting a capability.

### Codex

The repository includes `.codex-plugin/plugin.json` for direct loading and a
local marketplace entry under `.agents/plugins/`. The marketplace publishes
only `skills/`. Install it through the Codex plugin browser or local marketplace
workflow, then verify that the expected skills appear.

Each public capability uses the standard Agent Skills layout: a directory with
`SKILL.md`, concise routing metadata, and optional on-demand references or
deterministic helpers. Godmode intentionally remains a portable catalog rather
than a proprietary orchestration runtime.

## Catalog

### Core workflow skills

| Skill | Use it for |
| --- | --- |
| `using-godmode` | Choosing and composing the catalog |
| `solution-design` | Ambiguous or consequential requirements and design decisions |
| `implementation-planning` | Detailed, executable plans before multi-step implementation |
| `plan-execution` | Task-by-task execution of an existing plan |
| `test-driven-development` | Red-green-refactor behavior changes and regression tests |
| `root-cause-debugging` | Reproduction, root cause, and regression locking |
| `requesting-code-review` | Preparing a focused independent review packet |
| `receiving-code-review` | Validating and resolving review findings |
| `completion-verification` | Fresh evidence before completion or release claims |
| `dispatching-parallel-agents` | Splitting independent work with disjoint write sets |
| `subagent-driven-development` | Implementer/reviewer cycles for plan tasks |
| `using-git-worktrees` | Safe isolation for parallel or risky work |
| `branch-integration` | Final diff, proof, integration, and cleanup decisions |
| `writing-skills` | Creating and evaluating new Agent Skills |

### Engineering capabilities

| Skill | Use it for |
| --- | --- |
| `frontend-design` | New or refactored interfaces, design systems, states, and responsive UI |
| `ui-ux-review` | Existing UI audits, visual quality, accessibility, and anti-pattern review |
| `api-and-interface-design` | HTTP, RPC, CLI, webhook, and event contracts |
| `database-design` | Schemas, indexes, migrations, consistency, retention, and recovery |
| `security-and-hardening` | Threat modeling, abuse paths, privacy, and defensive controls |
| `performance-optimization` | Measured latency, memory, rendering, query, and bundle improvements |
| `test-strategy` | Risk-based coverage, environments, release gates, and test ownership |
| `browser-testing` | Real browser flows, responsive behavior, accessibility, and visual evidence |
| `documentation-and-adrs` | READMEs, runbooks, design docs, and architecture decisions |
| `observability-and-instrumentation` | Logs, metrics, traces, alerts, and diagnostic boundaries |
| `codebase-orientation` | Entry points, execution paths, ownership, conventions, hotspots, and unknowns |
| `technical-research` | Version-aware decisions grounded in authoritative sources |
| `safe-migrations` | Compatible staged migrations, reconciliation, rollback, and removal |
| `release-engineering` | CI gates, artifacts, canaries, promotion thresholds, and rollback |
| `architecture-review` | Structural friction, module ownership, coupling, and testability |
| `code-simplification` | Behavior-preserving readability and complexity reduction |
| `behavior-validation` | Source-blind black-box checks against observable contracts |
| `agent-evaluation` | Baseline/candidate evals for prompts, tools, agents, and skills |
| `incident-response` | Live containment, recovery, evidence, communication, and follow-up |

Names are intentionally literal and task-oriented. They describe the boundary
without depending on another repository's public vocabulary or compact aliases.

## Design principles

- Agent claims are not evidence.
- Literal responsibility names beat compact aliases and borrowed vocabulary.
- Separate workflow states when they have different activation and handoff
  rules.
- Keep `SKILL.md` concise; load deeper rules progressively.
- Use deterministic helpers for repeatable, error-prone work.
- Review the rendered UI, not only its source.
- Treat logs, external text, generated output, and tool responses as untrusted
  data.
- Never claim compatibility with a client that was not actually checked.

## Development

```bash
npm run check
npm run catalog:health
python3 scripts/repository_security.py
python3 scripts/compatibility.py check
python3 skills/frontend-design/scripts/design_system.py \
  --product "analytics dashboard" --tone technical --stack react
python3 skills/frontend-design/scripts/extract_design_system.py ./path/to/ui
python3 skills/ui-ux-review/scripts/audit_ui.py ./path/to/ui
python3 scripts/behavior_eval.py validate evals/behavior/core-workflows.json
```

The repository gate validates frontmatter, local links, body limits, manifest
shape, one routing fixture per skill, behavior-eval case schemas, catalog and
compatibility drift, workflow security, public-file safety, and helper tests. See
[`CONTRIBUTING.md`](CONTRIBUTING.md), [`docs/catalog.md`](docs/catalog.md), and
[`docs/research.md`](docs/research.md) for authoring and provenance details.
See [`SUPPORT.md`](SUPPORT.md), [`SECURITY.md`](SECURITY.md), and
[`CHANGELOG.md`](CHANGELOG.md) before reporting or releasing changes. Native
client evidence and limits are tracked in
[`docs/compatibility.md`](docs/compatibility.md).
Maintainer-only handoff, provenance, lifecycle, behavior-eval, activation, and
release procedures live in
[`docs/maintainer-workflows.md`](docs/maintainer-workflows.md); they are kept out
of the public skill catalog to avoid routing collisions.

`package.json` remains private to prevent accidental npm publication. Public
distribution uses the repository, client marketplaces, and checksum-verified
GitHub release archives.

## Status

Godmode is a pre-1.0 public preview. The catalog, deterministic helpers, routing
fixtures, and behavior-eval harness are usable, but client-specific activation
and output quality still require recorded forward runs across supported
harnesses. A passing repository gate is not a claim that every model or client
will behave identically.

## License

MIT.
