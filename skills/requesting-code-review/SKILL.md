---
name: requesting-code-review
description: >-
  Prepares a focused code review request for a branch, commit, pull request,
  or substantial working-tree diff by defining the review boundary, contract,
  risk areas, evidence, and questions for an independent reviewer. Use before
  merge or when another agent needs to review an implementation. Not for
  processing feedback already received or for claiming runtime correctness.
---

# Requesting Code Review

Make review cheap to perform and hard to misunderstand.

## Prepare the packet

1. Pin the comparison point and list changed files.
2. Link the originating request, design, plan, or acceptance criteria.
3. Summarize the behavior change and deliberately out-of-scope work.
4. List risky boundaries: data, permissions, concurrency, public API,
   migrations, performance, compatibility, and user-visible behavior.
5. Attach focused test/build/runtime evidence with command and result.
6. Name known limits and ask specific questions rather than “please review.”
7. Attach or write a short observable behavior contract for user-facing, CLI,
   API, generated-artifact, or operational changes. Keep it independent of the
   implementation so a reviewer can request source-blind validation.

Use [review-request.md](references/review-request.md) for the packet shape.

## Reviewer selection

Ask for an independent pass when the change is public, risky, cross-cutting,
security-sensitive, or difficult for its author to judge. Split contract and
engineering-risk passes when independent agents are available. Keep the review
scope large enough to include direct consumers but not unrelated cleanup.

Do not use a green test suite as a substitute for review, and do not present a
review request as evidence that the change is correct. Pair source-aware review
with `behavior-validation` when the change has a runnable public surface; a
clean diff review cannot prove that surface works.

## Completion condition

The request is ready when a reviewer can locate the contract, boundary, diff,
evidence, and highest-risk questions without reconstructing author intent.
