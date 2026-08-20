#!/usr/bin/env python3
"""Turn recurring agent failures into durable evaluation cases."""
from __future__ import annotations
import argparse
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


def failure_to_case(failure: dict[str, Any]) -> dict[str, Any]:
    failure_id = str(failure.get("id", "failure-1"))
    required = list(failure.get("required_behaviors", [])) or ["reproduce failure", "prevent regression", "verify result"]
    return {
        "schema_version": 1,
        "id": f"reg-{failure_id}",
        "source": {"type": "observed-failure", "failure_id": failure_id},
        "domain": str(failure.get("domain", "general")),
        "risk": str(failure.get("risk", "medium")),
        "task": str(failure.get("task", "Reproduce and prevent the reported agent failure.")),
        "failure_category": str(failure.get("category", "unknown")),
        "affected_skill": failure.get("skill"),
        "required_behaviors": required,
        "forbidden_behaviors": list(failure.get("forbidden_behaviors", [])),
        "grading": {"required_assertions": required},
    }


def generate(payload: Any, output: Path) -> dict[str, Any]:
    failures = payload if isinstance(payload, list) else payload.get("failures", []) if isinstance(payload, dict) else []
    if not isinstance(failures, list) or not failures:
        raise ValueError("failure input must contain at least one failure object")
    tasks = [failure_to_case(item) for item in failures if isinstance(item, dict)]
    result = {"schema_version": 1, "description": "Portable regressions generated from observed agent failures.", "cases": tasks}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command")
    p = sub.add_parser("generate")
    p.add_argument("failure", type=Path)
    p.add_argument("output", type=Path)
    p = sub.add_parser("classify")
    p.add_argument("message")
    args = parser.parse_args()
    if args.command == "classify":
        print(classify(args.message)); return 0
    if args.command == "generate":
        print(json.dumps(generate(json.loads(args.failure.read_text(encoding="utf-8")), args.output), indent=2, sort_keys=True)); return 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
