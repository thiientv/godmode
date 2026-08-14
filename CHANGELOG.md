# Changelog

All notable user-facing changes are recorded here. Godmode follows semantic
versioning, with pre-1.0 minor releases allowed to change the public skill API.

## [Unreleased]

### Changed

- Reframed both READMEs around the engineering problem, task-driven skill
  composition, and the workflow-plus-knowledge-plus-tooling quality model.
- Hardened GitHub Actions with immutable action revisions, non-persistent
  checkout credentials, least-privilege release jobs, and artifact handoff.
- Made catalog membership and compatibility evidence machine-readable and
  rejected documentation drift in the repository gate.

### Added

- Public-file and workflow security checks, catalog health reporting, and a
  release archive smoke test that validates an isolated extraction.
- Optional validated CodeTour output for codebase orientation and a bounded
  post-deploy verification record for canary and staged releases.

## [0.3.0] - 2026-08-13

### Added

- Simplified Chinese README with language navigation and release-package inclusion.
- Nine capabilities for codebase orientation, technical research, safe
  migrations, release engineering, architecture review, code simplification,
  source-blind behavior validation, agent evaluation, and incident response.
- Portable behavior-evaluation cases and tooling for validating case sets,
  initializing run records, and comparing baseline/candidate evidence.
- UI design-system extraction, stack-specific references, runtime
  state/viewport validation, a broader original design-intelligence catalog,
  and additional static accessibility/responsive checks.
- Support policy and release automation.

### Changed

- Renamed six pre-release workflow skills to literal Godmode vocabulary:
  `solution-design`, `implementation-planning`, `plan-execution`,
  `root-cause-debugging`, `completion-verification`, and `branch-integration`.
- Expanded skill authoring, test strategy, review, and observability workflows
  with baseline evaluation, specialized testing, behavior contracts, and
  operational baselines.

### Removed

- Removed the compact foundation names and intermediate borrowed workflow names
  rather than shipping duplicate routing aliases.
