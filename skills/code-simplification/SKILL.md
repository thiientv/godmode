---
name: code-simplification
description: >-
  Simplifies recently changed or explicitly scoped code while preserving
  observable behavior, error semantics, side effects, ordering, and public
  contracts. Use for readability cleanup, dead-code removal, reducing nesting,
  eliminating redundant wrappers, or making an implementation easier to
  maintain. Not for architecture redesign, new behavior, speculative cleanup,
  or a refactor without an adequate safety net.
---

# Code Simplification

Optimize comprehension and locality, not line count or personal style.

## Establish the invariant

Identify callers, outputs, errors, side effects, ordering, performance-sensitive
behavior, and tests. Read history or comments when a strange construct may be a
compatibility fence. If behavior is unclear, stop and use
`codebase-orientation` or `root-cause-debugging` before editing.

## Find earned simplifications

Prefer concrete signals: duplicated policy, deep conditional nesting, stale
branches, misleading names, pass-through wrappers, abstractions with no current
variation, repeated conversions, and comments that restate code. Preserve
abstractions that own policy, isolate volatility, or provide a real test seam.

Use [simplification-checks.md](references/simplification-checks.md) to classify
each candidate.

## Change incrementally

1. Make one coherent simplification.
2. Run focused behavior proof without weakening existing assertions.
3. Inspect the diff for hidden contract or error changes.
4. Continue only while each step improves comprehension.

Use a codemod or AST-aware transformation for large mechanical rewrites. Keep
feature work and broad cleanup separate unless the simplification is required
to implement the authorized behavior safely.

## Completion condition

Behavioral proof passes unchanged, the diff stays inside the stated scope, no
error handling or compatibility path was accidentally removed, and the result
is demonstrably easier to understand in its local codebase context.
