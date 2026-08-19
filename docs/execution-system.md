# Godmode execution system

Godmode now has a durable execution layer around the public skill catalog. It does not replace native client discovery or turn every task into a mandatory waterfall.

## Task state

`.godmode/task.json` stores the objective, risk, lifecycle state, completed states, active skills, evidence, next observable check, limits, and timestamps. Checkpoints live under `.godmode/checkpoints/` and execution events are append-only in `.godmode/events.jsonl`.

Use the dependency-free CLI:

```bash
python3 -B scripts/godmode.py init "implement OAuth rotation" --risk high --task-id AUTH-42
python3 -B scripts/godmode.py status
python3 -B scripts/godmode.py resume
python3 -B scripts/godmode.py risk
python3 -B scripts/godmode.py impact
python3 -B scripts/godmode.py checkpoint after-tests
```

## Evidence freshness

Evidence records capture the commit and a digest of their scoped files. When those files change, the evidence is invalidated. A stale result cannot satisfy lifecycle gates.

## Risk and release

Risk assessment is deterministic and advisory. It detects high-impact paths such as authentication, migrations, production infrastructure, secrets, and payment code. Release policy is risk-aware: low-risk work can finish after verification; medium/high risk may release after stronger evidence; critical work requires rollout and rollback evidence.

## Composition and learning

`skill-graph.json` records lightweight dependencies and common follow-up skills without becoming an opaque router. `scripts/feedback.py` maps recurring failures into regression cases, while `evals/golden-tasks.json` provides portable benchmark seeds. `scripts/benchmark.py` compares repeated runs by pass rate, quality, tokens, latency, and quality-per-token.

The design loop is:

```text
execution → events/evidence → failure taxonomy → regression case → benchmark → skill improvement
```

All missing client telemetry is represented as an explicit limit rather than inferred success.
