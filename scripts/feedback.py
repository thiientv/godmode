#!/usr/bin/env python3
"""Turn recurring agent failures into durable evaluation cases."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any


def classify(message: str) -> str:
    text = message.lower()
    rules = {
        "PREMATURE_IMPLEMENTATION": ("edit before", "without inspecting", "started coding"),
        "MISSING_VERIFICATION": ("claimed complete", "not verified", "no test"),
        "STALE_EVIDENCE": ("stale", "old evidence", "invalidated"),
        "WRONG_RISK": ("risk", "critical", "migration"),
        "ROUTING_COLLISION": ("wrong skill", "wrong route", "routing"),
    }
    for failure, needles in rules.items():
        if any(needle in text for needle in needles):
            return failure
    return "UNCLASSIFIED"


def make_case(failure: str, task: str, expected: list[str], forbidden: list[str] | None = None) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "id": f"failure-{failure.lower().replace('_', '-')}",
        "source": {"type": "failure-taxonomy", "failure": failure},
        "task": task,
        "required_behaviors": expected,
        "forbidden_behaviors": forbidden or [],
        "grading": {"required_assertions": expected},
    }


def append_case(root: Path, case: dict[str, Any]) -> Path:
    path = root / "evals" / "behavior" / "failure-regressions.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        payload = json.loads(path.read_text(encoding="utf-8"))
    else:
        payload = {"schema_version": 1, "cases": []}
    payload.setdefault("cases", []).append(case)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
