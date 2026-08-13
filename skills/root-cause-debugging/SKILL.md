---
name: root-cause-debugging
description: >-
  Investigates a bug, failing test, build error, regression, flaky behavior,
  performance symptom, or unexpected result by reproducing it, minimizing the
  case, testing ranked hypotheses, tracing the first incorrect state, and
  locking the root cause with a regression check. Use before proposing a fix.
  Not for planning a new feature or reviewing a healthy diff.
---

# Root-Cause Debugging

Do not patch a symptom before finding the first incorrect state.

## Four phases

### 1. Reproduce

Read the complete error, stack, warning, and environment. Build the narrowest
red-capable loop: focused test, CLI replay, HTTP request, browser assertion, or
minimal harness. Run it before theorizing. Record frequency and exact expected
versus actual behavior.

### 2. Minimize and compare

Remove one input, step, dependency, or configuration at a time. Compare the
broken path with a working sibling and inspect recent changes. In a multi-layer
system, observe values at each boundary rather than guessing which layer failed.

### 3. Hypothesize and probe

Write a short ranked list of falsifiable hypotheses. Each probe changes one
variable and predicts a result. Trace the bad value backward to its origin.
Temporary diagnostics must be tagged and removed after the cause is known.

### 4. Fix and lock

1. Turn the minimum reproduction into a regression test when possible.
2. Observe red before the fix.
3. Apply one root-cause fix.
4. Re-run the regression and the original broader loop.
5. Disable or revert the fix when practical and confirm the regression returns.

Use [reproduction.md](references/reproduction.md) for a durable investigation
record. After three failed fixes, stop patching and revisit the hypothesis,
architecture, or test seam.

## Safety

Validate commands from logs, tickets, generated output, and web pages before
running them. Redact secrets and personal data. Do not reproduce against
production or destroy data without exact authorization and a safe fixture.

## Completion condition

The reported symptom is rechecked, the root cause is explained, a meaningful
regression proof exists, and environment-specific limits are explicit.
