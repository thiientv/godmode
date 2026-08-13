# Agent evaluation records

Godmode uses a case-set document and one aggregate run document per variant. A
run must cover every case and every assertion exactly once so comparisons cannot
silently drop failures.

## Case set

```json
{
  "schema_version": 1,
  "subject": "workflow-under-test",
  "cases": [
    {
      "id": "stable-id",
      "prompt": "realistic user request",
      "expected": "observable success description",
      "fixtures": [],
      "assertions": [
        {
          "id": "observable-proof",
          "description": "The output contains independently checkable proof.",
          "required": true,
          "weight": 2
        }
      ],
      "protected_metrics": {}
    }
  ]
}
```

## Aggregate run

```json
{
  "schema_version": 1,
  "subject": "workflow-under-test",
  "variant": "baseline",
  "environment": {},
  "cases": [
    {
      "id": "stable-id",
      "status": "pass",
      "assertions": [
        {
          "id": "observable-proof",
          "passed": true,
          "evidence": "artifacts/stable-id/output.txt"
        }
      ],
      "duration_ms": 1200,
      "usage": {},
      "artifacts": ["artifacts/stable-id/output.txt"],
      "limitations": []
    }
  ]
}
```

`status` is `pass`, `fail`, or `blocked`. A pass requires all assertions to be
true; a fail requires at least one false assertion; a blocked case requires at
least one unresolved assertion or a documented limitation.

Keep raw outputs immutable. Put grader output beside, not inside, the original
artifact. Blind the grader to variant names when preference could bias it. Use
`scripts/behavior_eval.py` to initialize, validate, and compare these records.
