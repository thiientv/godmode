## Problem

What user or contributor problem does this change solve?

## Design

Which capability boundary or repository rule does the change follow? If adding
a public capability, explain why an existing one was insufficient.

## Provenance

List any reference material that influenced the change and the license/attribution
decision. State explicitly when the implementation was written from first
principles.

## Verification

List exact commands run and their fresh results:

```text
python3 scripts/validate.py
python3 scripts/behavior_eval.py validate evals/behavior/core-workflows.json
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Add native Claude/Codex checks when the change affects an adapter.

## Scope

Describe known limits and anything deliberately left out.
