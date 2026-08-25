# Godmode catalog

Godmode keeps workflow states and engineering expertise as separate public
skills. This makes activation clearer than a single “build” skill while still
allowing native clients to compose skills for one task.

`catalog.json` owns group membership. The README tables provide localized
descriptions, while repository validation requires every discovered skill,
routing fixture, and documentation consumer to stay synchronized.

## Workflow map

```text
using-godmode
    ├── solution-design
    │     └── implementation-planning
    │            ├── plan-execution
    │            └── subagent-driven-development
    ├── test-driven-development
    ├── root-cause-debugging
    ├── requesting-code-review ── pr-code-reviewer ── receiving-code-review
    ├── completion-verification
    ├── dispatching-parallel-agents
    ├── using-git-worktrees
    ├── branch-integration
    └── writing-skills
```

The arrows are handoffs, not a mandatory sequence for every task.

Supporting lifecycle capabilities compose around that core:

```text
codebase-orientation → technical-research → solution-design
safe-migrations → release-engineering → behavior-validation
observability-and-instrumentation → incident-response
writing-skills → agent-evaluation
architecture-review → code-simplification or implementation-planning
```

## Capability map

| Capability | Boundary | Typical companion |
| --- | --- | --- |
| `frontend-design` | Create or materially change UI | `browser-testing`, `ui-ux-review` |
| `ui-ux-review` | Inspect an existing UI or visual diff | `frontend-design`, `browser-testing` |
| `api-and-interface-design` | Define cross-component contracts | `security-and-hardening`, `observability-and-instrumentation` |
| `database-design` | Define persistent data and lifecycle | `api-and-interface-design`, `security-and-hardening` |
| `security-and-hardening` | Reduce concrete abuse and exposure risk | `api-and-interface-design`, `database-design` |
| `performance-optimization` | Improve a measured bottleneck | `root-cause-debugging`, `observability-and-instrumentation` |
| `test-strategy` | Decide risk-based coverage and release gates | `browser-testing`, `test-driven-development` |
| `browser-testing` | Exercise a real web boundary | `frontend-design`, `root-cause-debugging` |
| `documentation-and-adrs` | Preserve usable decisions and operations knowledge | `solution-design`, `implementation-planning` |
| `observability-and-instrumentation` | Make failures measurable and diagnosable | `api-and-interface-design`, `performance-optimization` |
| `codebase-orientation` | Map relevant code and ownership before acting | `solution-design`, `architecture-review` |
| `technical-research` | Ground version-sensitive decisions in primary sources | `safe-migrations`, `documentation-and-adrs` |
| `safe-migrations` | Preserve compatibility and state through a staged transition | `database-design`, `release-engineering` |
| `release-engineering` | Control artifacts, rollout, promotion, and rollback | `observability-and-instrumentation`, `behavior-validation` |
| `architecture-review` | Prioritize structural improvements from repository evidence | `codebase-orientation`, `solution-design` |
| `code-simplification` | Reduce local complexity without changing behavior | `test-driven-development`, `completion-verification` |
| `behavior-validation` | Test public behavior without source knowledge | `requesting-code-review`, `release-engineering` |
| `agent-evaluation` | Compare stochastic agent behavior against a baseline | `writing-skills`, `release-engineering` |
| `incident-response` | Contain and recover from active production impact | `observability-and-instrumentation`, `root-cause-debugging` |
| `pr-code-reviewer` | Review a GitHub PR or diff for correctness, security, compatibility, tests, and maintainability | `requesting-code-review`, `receiving-code-review` |

## Naming policy

The first foundation used `shape`, `build`, `investigate`, `review`, `prove`,
and `craft-ui`. An intermediate pass adopted several names from reference
projects. Both approaches were replaced before public release: compact aliases
were hard to discover, while borrowed names made Godmode's API feel derivative.
The public vocabulary now names the actual responsibility:

| Previous name | Public replacement |
| --- | --- |
| `shape` | `solution-design` + `implementation-planning` |
| `build` | `plan-execution` + `test-driven-development` |
| `investigate` | `root-cause-debugging` |
| `review` | `requesting-code-review` + `pr-code-reviewer` + `receiving-code-review` |
| `prove` | `completion-verification` |
| `craft-ui` | `frontend-design` + `ui-ux-review` |
| `brainstorming` | `solution-design` |
| `writing-plans` | `implementation-planning` |
| `executing-plans` | `plan-execution` |
| `systematic-debugging` | `root-cause-debugging` |
| `verification-before-completion` | `completion-verification` |
| `finishing-a-development-branch` | `branch-integration` |

This is an intentional pre-1.0 vocabulary change. No aliases are shipped: they
would create duplicate routing candidates and prolong an unstable API.

## Progressive disclosure

Every public skill contains only its activation boundary and core procedure.
References contain templates, matrices, and detailed checklists. The two UI
capabilities also ship dependency-free helpers:

- `frontend-design/scripts/design_system.py` creates a deterministic starting
  brief from product, tone, density, and stack inputs.
- `frontend-design/scripts/extract_design_system.py` extracts lexical evidence
  for tokens, fonts, spacing, radii, and media queries from an existing UI.
- `ui-ux-review/scripts/audit_ui.py` reports conservative static findings for
  supported HTML/CSS/component sources.

The repository-level `scripts/behavior_eval.py` validates behavior case sets,
creates baseline/candidate run records, and compares transparent weighted
results without invoking a proprietary evaluation service.

`scripts/catalog_health.py` reports context-size proxies, bundled resources,
changed skills, and description overlap. These are review signals, not an
automatic merge, retirement, or quality score.

Neither helper is an AI router or a universal design score. Their output is
evidence to inspect and discuss.

## Adding a capability

Use `writing-skills`, add positive and negative routing fixtures, and update the
README/catalog only after the boundary is distinct. If a new skill needs a
large data set, first prove that a small reference cannot solve the task and
add integrity tests for the data.
