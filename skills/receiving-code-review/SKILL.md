---
name: receiving-code-review
description: >-
  Processes code review feedback by classifying each finding, reproducing or
  validating it against the real contract, applying the smallest in-scope fix,
  and re-running focused proof. Use after comments arrive on a diff, pull
  request, design, or implementation. Not for requesting a first review or
  debugging an unrelated failure.
---

# Receiving Code Review

Treat feedback as evidence to investigate, not as an attack to win or a list
to obey blindly.

## Classify each finding

- **Defect:** violates the request, contract, safety, or compatibility.
- **Missing proof:** behavior may be correct but the evidence is insufficient.
- **Clarification:** intent or ownership is unclear.
- **Preference:** stylistic and not worth changing unless it reduces risk.
- **Out of scope:** real issue for a separate owner or change.

For a defect, reproduce the failure or inspect the real code path before
editing. For a disputed finding, state the invariant and the evidence that
supports the decision. Do not dismiss a comment because the suite is green.

## Fix loop

1. Record the finding and its scope classification.
2. Add a failing regression test or a direct falsifying check when practical.
3. Make the smallest correction at the owning boundary.
4. Run focused checks, then the relevant broader checks.
5. Re-read the changed diff and reply with the exact evidence.
6. Request re-review for changed contracts or previously disputed findings.

Do not bundle unrelated cleanup or change the product contract to silence a
reviewer. Use [finding-log.md](references/finding-log.md) for multiple comments.

## Completion condition

Every in-scope finding is fixed, verified, or explicitly accepted with a
reason; out-of-scope work is recorded for follow-up; and the re-review boundary
is clear.
