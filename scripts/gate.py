#!/usr/bin/env python3
"""Deterministic lifecycle gates backed by fresh evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED = {
    "DISCOVERY": ["task-boundary"],
    "DESIGN": ["design-decision"],
    "PLANNING": ["implementation-plan"],
    "IMPLEMENTATION": ["changed-scope"],
    "TESTING": ["fresh-test-result"],
    "REVIEW": ["review-result"],
    "VERIFICATION": ["evidence-ledger"],
    "RELEASE": ["rollout-result"],
    "DONE": ["evidence-ledger"],
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def valid_evidence(entry: Any) -> bool:
    return isinstance(entry, dict) and entry.get("valid") is True


def evidence_kinds(record: dict[str, Any]) -> set[str]:
    evidence = record.get("evidence", [])
    if not isinstance(evidence, list):
        return set()
    return {str(item.get("kind")) for item in evidence if valid_evidence(item)}


def gate(record: dict[str, Any], target: str) -> dict[str, Any]:
    state = str(record.get("state", ""))
    kinds = evidence_kinds(record)
    required = REQUIRED.get(target, [])
    missing = [kind for kind in required if kind not in kinds]
    if target == "RELEASE":
        risk = str(record.get("risk", "medium"))
        if risk == "high" and "review-result" not in kinds:
            missing.append("review-result")
        if risk == "critical":
            for kind in ("review-result", "rollout-result"):
                if kind not in kinds and kind not in missing:
                    missing.append(kind)
            if not bool(record.get("rollback_capability")):
                missing.append("rollback-capability")
    limits = record.get("limits", [])
    blocked_by_limits = bool(limits) and target in {"DONE", "RELEASE"}
    passed = not missing and not blocked_by_limits
    return {
        "passed": passed,
        "target": target,
        "current_state": state,
        "required_evidence": required,
        "available_evidence": sorted(kinds),
        "missing": sorted(set(missing)),
        "limits": limits if isinstance(limits, list) else [],
        "reason": "all required fresh evidence is present" if passed else "required evidence or explicit limits block completion",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path, nargs="?", default=Path(".godmode/task.json"))
    parser.add_argument("--target", choices=["VERIFICATION", "RELEASE", "DONE"], default=None)
    args = parser.parse_args()
    record = load(args.state)
    if not isinstance(record, dict):
        print("task state must be an object")
        return 1
    target = args.target or str(record.get("state", "VERIFICATION"))
    result = gate(record, target)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
