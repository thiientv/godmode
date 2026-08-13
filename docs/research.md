# Reference research and design provenance

The requested repositories were cloned with `git clone --depth 1` into
`examples/` on 2026-08-13. The directory is Git-ignored, is not a package input,
and is not required at runtime. The implementation in this repository was
rewritten from the ideas below; no reference `SKILL.md`, script, dataset,
template, or proprietary document was copied into Godmode.

## Research matrix

| Repository | Observed shape | Ideas adopted | Deliberately not copied |
| --- | --- | --- | --- |
| obra/superpowers | 14 workflow skills, session bootstrap, harness adapters, scripts, worktrees, subagent and integration tests | Familiar workflow decomposition, planning, TDD, debugging, independent review, verification, worktree isolation, branch finishing | Mandatory “invoke everything” posture, large orchestration machinery as a dependency, original text and implementation, adapter breadth before the core is exercised |
| addyosmani/agent-skills | 24 lifecycle and engineering skills, progressive disclosure, routing/evaluation guidance | Lifecycle boundaries, context discipline, anti-rationalization, doubt-driven checks, frontend/API/security/performance coverage | A large undifferentiated public catalog and vendor-specific assumptions |
| mattpocock/skills | 35 small composable skills across engineering, productivity, and handoff | Small task seams, user/model invocation distinction, research and codebase orientation | Personal workflow/productivity skills and repo-specific setup assumptions |
| nextlevelbuilder/ui-ux-pro-max-skill | Searchable UI/UX data, design-system generation, stack-specific rules, CSV validation, CLI packaging | Product-aware design direction, tokens, typography/color/layout/motion/accessibility categories, explicit stack detection, deterministic helper validation | Bundled datasets, platform templates, copied content, and a large search engine before Godmode has a maintenance need |
| nutlope/hallmark | Design skill with audit/redesign/study verbs, anti-slop gates, theme and typography guidance | Separate build/audit behavior, deliberate visual voice, anti-generic checks, rendered-surface inspection | External service/model dependency, theme catalog, copied prose/assets, pixel-clone behavior |
| anthropics/skills | 17 practical skills with rich references, scripts, examples, and testing helpers | Progressive disclosure, procedural skill bodies, real artifact/browser checks, skill authoring discipline | Non-coding artifact domains that do not belong in Godmode's initial catalog |
| agentskills/agentskills | Standard format and validation-oriented ecosystem reference | `SKILL.md` compatibility, simple frontmatter, client portability | Proprietary metadata or runtime assumptions beyond the standard |
| google/skills | 109 provider/domain skills with stack-specific references | Domain specialization and explicit scope as the catalog grows | Provider-scale catalog and cloud-specific knowledge that would not be maintained here |
| hashicorp/agent-skills | Organization-level skill and support metadata | The need for support, model, contribution, and policy documentation | Provider-specific operational scope |
| MicrosoftDocs/Agent-Skills | 202 service-specific skills | Evidence that a domain catalog needs names, indexes, and ownership boundaries | Azure-specific content and scale |
| petrkindlmann/qa-skills | 50 QA skills, indexes, risk-based strategy, browser/visual/accessibility coverage | Risk-to-test mapping, release readiness, visual and accessibility testing boundaries | Copying a QA taxonomy or pretending equal coverage is a strategy |
| openclaw/agent-skills | 8 operational skills, transcript/review validators, README and repo standards | Artifact-based review, deterministic validation, observability of agent behavior | Harness-specific runtime and review engine |

## Important implementation choices

### Literal names over compact or borrowed vocabulary

The first foundation compressed several ideas into `shape`, `build`,
`investigate`, `review`, `prove`, and `craft-ui`. An intermediate pass reused
several reference-project names. Both were rejected before public release:
compact verbs obscured activation, while borrowed vocabulary made the API feel
less intentional. Godmode now uses literal responsibility names such as
`solution-design`, `implementation-planning`, `plan-execution`,
`root-cause-debugging`, `completion-verification`, and `branch-integration`.

### Instructions before engines

Superpowers demonstrates that behavior-changing prose can be useful before a
large runtime exists. UI/UX Pro Max demonstrates that structured data can help
when expert selection is repetitive. Godmode starts with concise instructions,
small references, and transparent standard-library helpers. The UI catalog was
expanded only after review exposed real gaps in product, layout, accessibility,
runtime state, and design-system extraction; it remains original and small
enough to audit.

### Static checks plus real evidence

Routing fixtures and helper tests catch structural regressions. Portable
behavior cases now add baseline/candidate run records, assertions, artifacts,
timing, and usage, but they still cannot prove how every model or client
activates a skill. Browser and visual skills require a rendered state/viewport
matrix, keyboard traversal, and accessibility evidence; source-only inspection
is not marked as proof.

## Licensing and provenance

The researched repositories were checked for their top-level license or notice
before design decisions were recorded. Godmode is MIT. The implementation uses
original wording, original small reference templates, and original helper code.
The large CSVs, scripts, examples, screenshots, and platform templates in
`examples/` remain outside the package and are not imported at runtime.

If a future contribution adapts substantial text, data, code, or assets, it
must record the source license, attribution requirement, exact adapted paths,
and why rewriting was not sufficient. Prefer first-principles rewriting when
the license or provenance is unclear.

## Remaining gaps

Godmode now covers the core Superpowers workflow surface and broader engineering
and operational boundaries. The next evidence-driven work should be:

1. native forward tests across Claude Code, Codex, and at least one additional
   Agent Skills-compatible harness;
2. recorded baseline/candidate runs for the six bundled behavior cases, with
   sanitized artifacts and grader output;
3. optional worktree/subagent and behavior-eval adapters where a client exposes
   stable automation APIs;
4. deeper UI data only when real forward runs expose a repeatable gap;
5. signed release and changelog automation after the 0.3 public preview.
