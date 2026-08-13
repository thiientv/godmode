# Implementation plan template

```markdown
# <Feature> Implementation Plan

**Goal:** <observable outcome>
**Architecture:** <ownership and data flow>
**Constraints:** <compatibility, safety, runtime, licensing>
**Spec:** <design document or request>

## File map
- Create: `exact/path` — responsibility
- Modify: `exact/path` — contract changed
- Test: `exact/path` — behavior proved

## Task 1: <vertical slice>

**Files:** ...
**Consumes:** ...
**Produces:** ...

- [ ] Write the failing test or capture the failing observation.
- [ ] Run: `<exact command>`
  Expected: `<specific failure>`
- [ ] Implement the smallest change.
- [ ] Run: `<exact command>`
  Expected: `<specific pass>`
- [ ] Record the checkpoint and remaining limit.
```

Repeat the task block until every acceptance item is covered. Keep code samples
small but concrete; do not refer to an undefined “similar task.”
