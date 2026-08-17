#!/usr/bin/env python3
"""Validate and inspect Godmode's risk-aware engineering lifecycle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "lifecycle.json"


def load_graph(path: Path = GRAPH_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("unsupported lifecycle schema")
    return payload


def validate_state_record(record: dict[str, Any], graph: dict[str, Any] | None = None) -> list[str]:
    graph = graph or load_graph()
    errors: list[str] = []
    states = set(graph["states"])
    risks = set(graph["risk_levels"])

    state = record.get("state")
    risk = record.get("risk")
    completed = record.get("completed", [])
    evidence = record.get("evidence", [])
    next_check = record.get("next_check")
    limits = record.get("limits", [])

    if state not in states:
        errors.append(f"state must be one of {sorted(states)}")
    if risk not in risks:
        errors.append(f"risk must be one of {sorted(risks)}")
    if not isinstance(completed, list) or not all(item in states for item in completed):
        errors.append("completed must be a list of known states")
    if not isinstance(evidence, list) or not all(isinstance(item, dict) for item in evidence):
        errors.append("evidence must be a list of objects")
    if not isinstance(next_check, str) or not next_check.strip():
        errors.append("next_check must be a non-empty string")
    if not isinstance(limits, list) or not all(isinstance(item, str) and item.strip() for item in limits):
        errors.append("limits must be a list of non-empty strings")

    if errors:
        return errors

    if state == "DONE" and not _has_evidence(evidence, "evidence-ledger"):
        errors.append("DONE requires evidence-ledger evidence")

    required = graph["risk_requirements"][risk]["required_states"]
    completed_set = set(completed)
    if state == "DONE":
        missing = [required_state for required_state in required if required_state not in completed_set]
        if missing:
            errors.append(f"risk {risk} cannot reach DONE without states: {', '.join(missing)}")

    return errors


def _has_evidence(evidence: list[dict[str, Any]], kind: str) -> bool:
    return any(item.get("kind") == kind for item in evidence)


def can_transition(record: dict[str, Any], target: str, graph: dict[str, Any] | None = None) -> tuple[bool, str]:
    graph = graph or load_graph()
    errors = validate_state_record(record, graph)
    if errors:
        return False, "; ".join(errors)
    current = record["state"]
    allowed = graph["transitions"].get(current, [])
    if target not in allowed:
        return False, f"transition {current} -> {target} is not allowed"

    if target == "VERIFICATION" and not _has_evidence(record["evidence"], "fresh-test-result") and record["risk"] != "low":
        return False, "non-low-risk verification requires fresh-test-result evidence"
    if target == "RELEASE" and record["risk"] not in {"critical"}:
        return False, "RELEASE is reserved for critical-risk tasks in schema v1"
    return True, "ok"


def recover_state(root: Path) -> dict[str, Any]:
    """Infer durable task context from repository artifacts without chat history."""
    git_diff = _read_command_hint(root, "git diff")
    git_status = _read_command_hint(root, "git status")
    plan = _find_artifact(root, ["plan.md", "implementation-plan.md", "PLAN.md"])
    evidence = _find_artifact(root, ["evidence.json", "evidence-ledger.json", "evidence.md"])
    return {
        "sources": [source for source in [git_status, git_diff, plan, evidence] if source],
        "next_check": "inspect the listed durable artifacts and run the smallest fresh verification",
        "limits": ["state is inferred from repository artifacts; conversational history was not used"],
    }


def _find_artifact(root: Path, names: list[str]) -> str | None:
    for name in names:
        path = root / name
        if path.is_file():
            return str(path.relative_to(root))
    return None


def _read_command_hint(root: Path, command: str) -> str:
    marker = root / ".godmode" / (command.replace(" ", "-") + ".txt")
    return str(marker.relative_to(root)) if marker.is_file() else ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state_file", type=Path, help="JSON task-state record")
    parser.add_argument("--target", help="optional lifecycle target state")
    args = parser.parse_args()
    record = json.loads(args.state_file.read_text(encoding="utf-8"))
    if not isinstance(record, dict):
        raise SystemExit("state file must contain a JSON object")
    errors = validate_state_record(record)
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    if args.target:
        ok, message = can_transition(record, args.target)
        print(message)
        return 0 if ok else 1
    print("valid lifecycle state record")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
