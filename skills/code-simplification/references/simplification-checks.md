# Simplification checks

Before changing a candidate, answer:

- What observable behavior and error semantics must remain identical?
- Why might the current shape exist?
- Does the candidate own policy or only pass it through?
- Would deletion remove complexity or distribute it into callers?
- Is the change local to the authorized task?
- Can existing tests prove equivalence without being rewritten?

Reject simplifications motivated only by fewer lines, personal naming taste,
future hypothetical reuse, or a linter score. Prefer guard clauses, direct data
flow, truthful names, one owner for duplicated policy, and removal of confirmed
dead paths.
