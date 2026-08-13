---
name: behavior-validation
description: >-
  Validates a running application, CLI, API, service, or generated artifact as
  a user or operator against a prewritten observable behavior contract while
  remaining source-blind. Use for acceptance checks, runtime proof, anti-fake
  probes, release smoke tests, or an independent companion to code review. Not
  for source-quality findings, root-cause diagnosis, or visual design judgment
  outside the contract.
---

# Behavior Validation

Judge what the product does, not how its source appears to do it.

## Establish isolation

Write or read the behavior contract before exercising the target. Use
[behavior-contract.md](references/behavior-contract.md). The contract must name
user tasks, expected outcomes, setup, allowed interfaces, negative cases, and
required evidence.

Do not inspect source, diffs, internal tests, Git history, or implementation
notes during validation. Interact only through public browser, CLI, API,
artifact, accessibility, or operator surfaces. If source is required, mark the
clause blocked and hand it to `root-cause-debugging`.

## Exercise the contract

1. Run each task through the same entry point a real user or operator uses.
2. Vary input and state to detect hard-coded success, stale data, or display-only
   behavior.
3. Test invalid, empty, interrupted, retry, persistence, and permission paths
   where the contract makes them relevant.
4. Capture redacted screenshots, terminal excerpts, response summaries, or
   artifact facts.
5. Mark every clause pass, fail, blocked, or out of scope. Lack of evidence is
   not a pass.

When a finding is fixed, rerun the failed clause and nearby regression probes;
do not rerun unrelated expensive scenarios without reason.

## Completion condition

Every relevant contract clause has a status and reproducible evidence, anti-fake
probes were attempted, secrets and private data were excluded, and the report
does not infer implementation defects from observable symptoms.
