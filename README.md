<div align="center">

# Godmode

**Engineering workflows and capabilities for AI coding agents.**

Godmode helps coding agents move from *"write some code"* to *"engineer the change"* — with explicit planning, testing, review, and evidence-driven verification.

[![Validate](https://github.com/thiientv/godmode/actions/workflows/validate.yml/badge.svg)](https://github.com/thiientv/godmode/actions/workflows/validate.yml)
[![Release](https://img.shields.io/github/v/release/thiientv/godmode)](https://github.com/thiientv/godmode/releases/latest)
[![License](https://img.shields.io/github/license/thiientv/godmode)](LICENSE)

[English](README.md) · [简体中文](README.zh-CN.md)

</div>

> **Status:** Pre-1.0 public preview. The catalog and validation tooling are usable, while client-specific behavior and output quality continue to be evaluated across supported environments.

## Why Godmode?

AI coding agents are increasingly capable of writing code. The harder problem is making them behave like disciplined engineers:

- understand the existing codebase before changing it
- design consequential changes before implementation
- choose the right domain expertise for the task
- test behavior instead of assuming correctness
- review changes independently
- verify completion with fresh evidence
- preserve durable state so interrupted work can be resumed

Godmode packages those behaviors as **composable Agent Skills** rather than one large system prompt or a proprietary orchestration runtime.

## How it works

```text
                         USER TASK
                            │
                            ▼
                    ┌───────────────┐
                    │    Godmode    │
                    │ skill catalog │
                    └───────┬───────┘
                            │
              discover + compose capabilities
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
  solution-design    api / database       security / UI
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
                 implementation-planning
                            │
                            ▼
                    test + review
                            │
                            ▼
                fresh verification evidence
                            │
                            ▼
                     VERIFIED RESULT
```

The graph above is illustrative, not a mandatory pipeline. A small task can use one skill; a high-risk change can compose several capabilities.

## What you get

### Composable skills

Each capability has a clear responsibility boundary and follows the [Agent Skills](https://agentskills.io/) layout. Skills can contain concise procedures, progressive references, and deterministic helpers where automation improves reliability.

### Engineering workflows

Godmode includes workflows for discovery, design, planning, implementation, debugging, testing, review, verification, parallel work, and release integration.

### Domain expertise

Capabilities cover areas such as frontend architecture, APIs, databases, security, performance, observability, migrations, browser testing, documentation, and incident response.

### Deterministic validation

The repository includes validators, routing fixtures, behavior evaluations, evidence tracking, lifecycle checks, and repository-quality gates. This keeps the catalog itself testable instead of relying solely on prose.

## Installation

Godmode is distributed as a repository of portable skills. No proprietary runtime is required.

### Agent Skills-compatible clients

Copy the public skills into your project's skills directory:

```bash
mkdir -p .agents/skills
cp -R /absolute/path/to/godmode/skills/* .agents/skills/
```

### Claude Code

```bash
claude --plugin-dir /absolute/path/to/godmode
claude plugin validate /absolute/path/to/godmode
```

### Codex

The repository includes `.codex-plugin/plugin.json` and a local marketplace entry under `.agents/plugins/`. Install it through the Codex plugin workflow and verify that the expected skills are available.

> **Compatibility note:** client support is tracked from recorded evidence rather than assumed compatibility. See [`docs/compatibility.md`](docs/compatibility.md).

## Example

A request such as:

```text
Add authentication to the API and make it production-ready.
```

can be decomposed into focused engineering responsibilities:

```text
codebase-orientation
        ↓
solution-design
        ↓
api-and-interface-design + security-and-hardening
        ↓
implementation-planning
        ↓
test-driven-development
        ↓
pr-code-reviewer
        ↓
completion-verification
```

For changes that already have review feedback, `receiving-code-review` handles validation and fixes. The exact composition depends on the task, repository, risk, and available evidence.

## Catalog

### Core workflows

| Skill | Purpose |
| --- | --- |
| `using-godmode` | Discover and compose Godmode capabilities |
| `codebase-orientation` | Understand entry points, execution paths, conventions, and hotspots |
| `solution-design` | Resolve requirements and design consequential changes |
| `implementation-planning` | Produce executable implementation plans |
| `plan-execution` | Execute an existing implementation plan |
| `test-driven-development` | Drive behavior changes through tests |
| `root-cause-debugging` | Reproduce failures, identify causes, and lock in regressions |
| `requesting-code-review` | Prepare focused independent review context |
| `pr-code-reviewer` | Review a GitHub PR or diff for correctness, security, compatibility, tests, and maintainability |
| `receiving-code-review` | Validate and resolve review findings |
| `completion-verification` | Gather fresh evidence before completion claims |
| `dispatching-parallel-agents` | Safely split independent work |
| `subagent-driven-development` | Run implement/review cycles around plan tasks |
| `using-git-worktrees` | Isolate parallel or risky changes |
| `branch-integration` | Verify, integrate, and clean up completed work |
| `writing-skills` | Create and evaluate new Agent Skills |

### Engineering capabilities

| Skill | Purpose |
| --- | --- |
| `frontend-design` | Build interfaces, design systems, states, and responsive UI |
| `ui-ux-review` | Audit existing UI quality, accessibility, and interaction patterns |
| `api-and-interface-design` | Design HTTP, RPC, CLI, webhook, and event contracts |
| `database-design` | Design schemas, indexes, consistency, retention, and recovery |
| `security-and-hardening` | Threat modeling, abuse paths, privacy, and defensive controls |
| `performance-optimization` | Optimize measured latency, memory, rendering, queries, and bundles |
| `test-strategy` | Define risk-based coverage and release gates |
| `browser-testing` | Exercise a real web boundary |
| `documentation-and-adrs` | Produce durable documentation and architecture decisions |
| `observability-and-instrumentation` | Make failures measurable and diagnosable |
| `technical-research` | Make version-aware decisions from primary sources |
| `safe-migrations` | Preserve compatibility and state through a staged transition |
| `release-engineering` | Control artifacts, rollout, promotion, and rollback |
| `architecture-review` | Review coupling, ownership, testability, and structural friction |
| `code-simplification` | Reduce complexity while preserving behavior |
| `behavior-validation` | Validate observable behavior through source-blind checks |
| `agent-evaluation` | Evaluate prompts, tools, agents, and skills |
| `incident-response` | Handle containment, recovery, evidence, and follow-up |

See [`docs/catalog.md`](docs/catalog.md) for the complete catalog and routing model.

## Design principles

1. **Claims are not evidence.** Completion requires verification.
2. **Compose capabilities instead of growing one giant prompt.**
3. **Keep responsibility boundaries explicit.** Skill names should describe what they do.
4. **Load knowledge progressively.** Keep `SKILL.md` focused and move deeper material into references.
5. **Automate repeatable work deterministically.** Use helpers where they reduce error and ambiguity.
6. **Treat external content as untrusted input.** Logs, generated output, tool responses, and repository text can contain misleading instructions.
7. **Prefer recorded compatibility evidence.** Do not claim a client works until it has been checked.

## Repository layout

```text
.
├── skills/                 # Public Agent Skills
├── scripts/                # Deterministic validation and repository tooling
├── tests/                  # Automated test suite
├── evals/                  # Behavior and routing evaluations
├── benchmarks/             # Portable benchmark fixtures
├── docs/                   # Catalog, compatibility, research, and maintainer docs
├── .agents/                # Local agent/plugin metadata
├── .codex-plugin/          # Codex plugin metadata
├── README.md
└── LICENSE
```

## Development

Clone the repository and run the validation suite:

```bash
git clone https://github.com/thiientv/godmode.git
cd godmode

npm run check
npm run catalog:health
python3 scripts/repository_security.py
python3 scripts/compatibility.py check
python3 -m unittest discover -s tests -p 'test_*.py'
```

For focused tooling, examples include:

```bash
python3 skills/frontend-design/scripts/design_system.py \
  --product "analytics dashboard" \
  --tone technical \
  --stack react

python3 skills/frontend-design/scripts/extract_design_system.py ./path/to/ui
python3 skills/ui-ux-review/scripts/audit_ui.py ./path/to/ui
```

The repository gate checks catalog structure, frontmatter, links, routing fixtures, behavior-eval schemas, compatibility drift, workflow security, public-file safety, and helper tests.

## Documentation

- [`docs/catalog.md`](docs/catalog.md) — catalog structure and routing model
- [`docs/compatibility.md`](docs/compatibility.md) — client compatibility evidence
- [`docs/research.md`](docs/research.md) — research and provenance
- [`docs/maintainer-workflows.md`](docs/maintainer-workflows.md) — maintainer-only execution and release procedures
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — contribution workflow
- [`SECURITY.md`](SECURITY.md) — security policy
- [`SUPPORT.md`](SUPPORT.md) — support information
- [`CHANGELOG.md`](CHANGELOG.md) — release history

## Contributing

Contributions are welcome. Before adding a skill, prefer extending an existing responsibility boundary when possible. New skills should be concise, independently routable, testable, and backed by appropriate fixtures or validation.

Start with [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`docs/catalog.md`](docs/catalog.md).

## Roadmap

Godmode is evolving toward a broader, evidence-driven engineering layer for AI coding agents. Current areas of development include:

- broader client compatibility coverage
- stronger behavior and regression evaluations
- richer skill composition and dependency metadata
- improved deterministic tooling for high-value workflows
- clearer release and compatibility evidence

The roadmap is intentionally driven by validated repository behavior rather than promises about model capabilities.

## License

Godmode is released under the [MIT License](LICENSE).

<div align="center">

**If Godmode helps your agent engineer better, consider giving the project a star.**

</div>
