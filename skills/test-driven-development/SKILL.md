---
name: test-driven-development
description: >-
  Implements behavior changes with a test-first red-green-refactor loop: write
  one meaningful failing test, watch it fail for the intended reason, make the
  smallest change, then refactor while green. Use for new behavior, bug fixes,
  refactors with preserved contracts, and regression tests. Not required for
  disposable prototypes, generated files, or documentation-only edits.
---

# Test-Driven Development

The test is an executable statement of behavior, not a coverage decoration.

## Red-green-refactor

1. **Red:** name one behavior and write the smallest test at the highest seam
   that can fail for the missing behavior.
2. **Verify red:** run the focused command. Confirm it fails because the
   behavior is absent, not because of a typo, broken fixture, or setup error.
3. **Green:** implement the simplest production change that makes the test
   pass. Do not add speculative options or unrelated cleanup.
4. **Verify green:** run the focused test and relevant existing tests.
5. **Refactor:** improve names, duplication, and boundaries while keeping the
   suite green. Add the next behavior only after the current loop is stable.

## Honest tests

- Assert user-visible or contract-visible behavior, not private call counts.
- Prefer real collaborators; mock only an expensive, nondeterministic, or
  unavailable boundary and state why.
- Make failures diagnostic: clear name, small fixture, one cause.
- Include error, empty, boundary, retry, ordering, and permission cases when
  they are part of the contract.

## Exceptions

For a prototype, generated output, or docs-only change, state why test-first is
not useful and choose another observable check. “I will test later” is not an
exception for production behavior.

Use [test-design.md](references/test-design.md) when the test seam or fixture
quality is unclear. Pair with `root-cause-debugging` for an existing failure
and `completion-verification` at the final gate.

## Completion condition

The loop is credible when the test was observed failing for the intended reason,
passes after the change, neighboring checks remain green, and the remaining
untested behavior is named.
