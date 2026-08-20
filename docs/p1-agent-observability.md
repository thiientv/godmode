# P1 agent observability and feedback loop

P1 adds a measurable execution layer without replacing native client discovery.

## Normalized runs

Adapters can normalize client telemetry into `.godmode/runs/*.json` with provenance, usage, events, activated skills, final message, and explicit limits.

```bash
python3 -B scripts/agent_runs.py normalize raw-run.json .godmode/runs/run-001.json
python3 -B scripts/agent_runs.py list
python3 -B scripts/agent_runs.py show .godmode/runs/run-001.json
```

## Context recovery

`recovery.py` reconstructs context from durable task state, the newest checkpoint, recent execution events, and known repository artifacts. A checkpoint is preferred over guessing lifecycle state from prose.

```bash
python3 -B scripts/recovery.py
python3 -B scripts/godmode.py resume
```

## Skill composition

`skill_composition.py` resolves transitive `requires` dependencies and reports recommended follow-ups and declared conflicts. Native discovery remains the routing authority.

```bash
python3 -B scripts/skill_composition.py solution-design security-and-hardening
```

## Failure feedback

Observed failures can be converted into portable regression cases without pretending the generated task is already graded.

```bash
python3 -B scripts/feedback.py generate failure.json evals/behavior/failure-regressions.json
```

The generated record preserves the failure category, affected skill, required behaviors, forbidden behaviors, and source failure identifier so later benchmarks can consume it.

## Design boundary

Client execution remains client-owned. Godmode stores normalized telemetry, recovery state, composition metadata, and reusable regression inputs. It does not introduce an opaque autonomous router.
