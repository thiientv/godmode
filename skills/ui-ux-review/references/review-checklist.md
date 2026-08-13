# UI/UX review checklist

## Priority

- **P0:** blocks access, causes data loss, or makes the primary flow unusable.
- **P1:** major accessibility, responsive, error-recovery, or trust failure.
- **P2:** meaningful clarity, consistency, or interaction defect.
- **P3:** optional polish with no material user harm.

## Findings

```text
[P1] Keyboard focus disappears on the dialog close action
Location: /settings, component X, or screenshot viewport
Failure: keyboard users cannot tell where focus moved and may submit the wrong action
Evidence: keyboard traversal / DOM inspection / screenshot
Correction: restore focus to the invoking control and add a regression check
```

## Minimum surface matrix

| Surface | Narrow | Intermediate | Desktop | Theme/state |
| --- | --- | --- | --- | --- |
| Primary flow |  |  |  |  |
| Empty/error |  |  |  |  |
| Dialog/form |  |  |  |  |

Do not call a page “polished” when only the happy-path desktop screenshot was
examined.
