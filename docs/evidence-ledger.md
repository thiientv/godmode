# Evidence ledger

Completion is an evidence-backed claim, not a narrative statement. Godmode uses the contract:

```text
Claim → falsifiable check → fresh result → explicit limit
```

## Record

A ledger entry should contain:

```json
{
  "claim": "Authentication works for the supported login flow",
  "checks": [
    {
      "kind": "test",
      "command": "python -m unittest discover",
      "result": "passed",
      "observed_at": "2026-08-17T06:00:00Z"
    }
  ],
  "limits": ["OAuth provider was not exercised"]
}
```

## Rules

- A claim is not evidence.
- A plan is not evidence.
- A tool invocation is not evidence until its result is observed.
- Cached, remembered, or inferred results should not be presented as fresh verification.
- Required assertions must pass; an aggregate score cannot override a failed required assertion.
- Every material completion claim should expose meaningful limits when coverage is incomplete.
- Verification should be independent from the implementation narrative whenever practical.

## Risk levels

`low` tasks can use a focused check. `medium` tasks should normally combine the changed-behavior check with regression coverage. `high` and `critical` tasks should collect evidence across the affected boundary, review risk, and final completion verification.

## Completion decision

A task may be marked `DONE` only when every required claim has sufficient evidence for its risk level. Unknowns remain explicit limits rather than being silently converted into confidence.
