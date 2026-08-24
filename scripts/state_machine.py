#!/usr/bin/env python3
"""Guard durable task lifecycle transitions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TransitionResult:
    allowed: bool
    reason: str


def transition(record: dict[str, Any], target: str, graph: dict[str, Any]) -> TransitionResult:
    current = record.get("state")
    transitions = graph.get("transitions", {})
    if target not in transitions.get(current, []):
        return TransitionResult(False, f"transition {current} -> {target} is not allowed")

    evidence = record.get("evidence", [])
    valid = {item.get("kind") for item in evidence if isinstance(item, dict) and item.get("valid", True) is not False}
    required = graph.get("minimum_evidence", {}).get(target, [])
    missing = [kind for kind in required if kind not in valid]
    if missing:
        return TransitionResult(False, f"transition requires evidence: {', '.join(sorted(missing))}")

    if target == "DONE" and record.get("limits"):
        return TransitionResult(False, "explicit task limits block DONE")

    return TransitionResult(True, "ok")
