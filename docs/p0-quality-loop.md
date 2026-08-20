# P0 quality loop

Godmode's quality loop keeps native agent execution as the authority while making routing, behavior, and completion claims mechanically testable.

## Native routing regression

`evals/routing/core.json` contains portable routing cases. A native adapter can emit a trace with the skills it selected:

```json
{"cases":[{"id":"security-change","skills":["security-and-hardening","test-driven-development"]}]}
```

Evaluate it with:

```bash
python3 -B scripts/routing_eval.py evaluate evals/routing/core.json trace.json result.json
```

Compare a candidate against a known-good baseline with:

```bash
python3 -B scripts/routing_eval.py ratchet baseline.json candidate.json
```

The ratchet rejects rank-1 or top-3 routing regressions and increases in forbidden-skill selection. It is deliberately a regression guard, not a replacement for native intent routing.

## Deterministic behavior grading

Behavior cases can opt into deterministic checks without changing the existing manual assertion contract:

```json
{
  "id": "artifact",
  "required": true,
  "check": {"type":"file_exists", "path":"report.json"}
}
```

Supported checks are `file_exists`, `file_absent`, `text_contains`, `text_absent`, and exact `json_equals`. Assertions without a deterministic check remain `blocked`; the grader never converts an unobserved assertion into success.

```bash
python3 -B scripts/behavior_grader.py evals/behavior/case.json ./workspace
```

## Evidence gates

Completion gates only accept evidence whose ledger entry is explicitly `valid: true`. Stale or invalidated evidence cannot satisfy a gate.

```bash
python3 -B scripts/godmode.py gate
python3 -B scripts/gate.py .godmode/task.json --target DONE
```

`DONE` requires a fresh `evidence-ledger`. High-risk release requires review evidence; critical release additionally requires rollout evidence and an explicit rollback capability. Limits are surfaced rather than hidden.

The result is intentionally conservative: a missing check is a blocked claim, not a score that can be averaged away.
