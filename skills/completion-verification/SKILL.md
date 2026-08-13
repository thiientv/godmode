---
name: completion-verification
description: >-
  Verifies a completion, fix, passing, compatibility, release, or readiness
  claim with fresh task-specific evidence mapped to the actual requirements.
  Use before saying a change is done, before merge, after review fixes, and at
  release gates. Not a substitute for diagnosing the cause of a failing check.
---

# Completion Verification

No completion claim without fresh evidence that can falsify the claim.

## Completion gate

1. State the exact claim and its scope.
2. Map each requirement to the smallest meaningful evidence: focused test,
   type check, build, package validation, browser flow, API response,
   screenshot, database state, static analysis, or independent review.
3. Run the full relevant command now. Do not rely on an earlier transcript or
   another agent's report.
4. Read the output and record exit status, counts, and failures.
5. Compare what was exercised with what the claim covers.
6. Report blocked checks, unavailable environments, unrelated failures, and
   residual risk explicitly.

Use [evidence-map.md](references/evidence-map.md) for multi-surface changes.

## Evidence discipline

- A unit test does not prove deployment or a browser flow.
- A build does not prove user-visible behavior.
- A screenshot does not prove keyboard or data correctness.
- A reviewer report does not prove runtime behavior.
- One green path does not prove negative and boundary paths.

If a check fails, preserve the failure and hand it to
`root-cause-debugging`. Never weaken, delete, skip, or rewrite a check merely
to obtain green output.

## Completion condition

Every in-scope acceptance item has a fresh result, every unavailable check is
marked as a limit, and the final wording is no broader than the evidence.
