#!/usr/bin/env python3
"""Deterministic, dependency-free P0 orchestration primitives."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable


TERMINAL = {"completed", "failed", "cancelled"}
RETRYABLE = {"timeout", "rate_limit", "network", "tool_error"}


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    retryable: set[str] = field(default_factory=lambda: set(RETRYABLE))

    def should_retry(self, reason: str, attempts: int) -> bool:
        return attempts < max(1, self.max_attempts) and reason in self.retryable


@dataclass
class Handoff:
    task: str
    completed: list[str] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)
    files_changed: list[str] = field(default_factory=list)
    evidence: list[dict] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    next_action: str = ""

    def as_dict(self) -> dict:
        return {
            "task": self.task,
            "completed": self.completed,
            "findings": self.findings,
            "files_changed": self.files_changed,
            "evidence": self.evidence,
            "open_questions": self.open_questions,
            "next_action": self.next_action,
        }


def ready_nodes(graph: dict) -> list[str]:
    nodes = graph.get("nodes", [])
    states = {n["id"]: n.get("state", "pending") for n in nodes}
    return sorted(
        n["id"] for n in nodes
        if n.get("state", "pending") == "pending"
        and all(states.get(dep) == "completed" for dep in n.get("depends_on", []))
    )


def execute(graph: dict, runner: Callable[[dict], object], policy: RetryPolicy | None = None) -> dict:
    """Run ready nodes sequentially while preserving deterministic state transitions.

    The runner receives a node and may return True/False or raise an exception. Exceptions
    are classified as retryable when they expose ``reason``; otherwise they fail the node.
    """
    policy = policy or RetryPolicy()
    nodes = {n["id"]: dict(n) for n in graph.get("nodes", [])}
    attempts = {node_id: 0 for node_id in nodes}
    events: list[dict] = []

    while True:
        current = {"nodes": list(nodes.values())}
        ready = ready_nodes(current)
        if not ready:
            break
        progressed = False
        for node_id in ready:
            node = nodes[node_id]
            attempts[node_id] += 1
            node["state"] = "running"
            events.append({"node": node_id, "event": "started", "attempt": attempts[node_id]})
            try:
                result = runner(node)
                if result is False:
                    raise RuntimeError("runner returned false")
                node["state"] = "completed"
                events.append({"node": node_id, "event": "completed", "attempt": attempts[node_id]})
                progressed = True
            except Exception as exc:
                reason = str(getattr(exc, "reason", "tool_error"))
                if policy.should_retry(reason, attempts[node_id]):
                    node["state"] = "pending"
                    events.append({"node": node_id, "event": "retry", "attempt": attempts[node_id], "reason": reason})
                else:
                    node["state"] = "failed"
                    events.append({"node": node_id, "event": "failed", "attempt": attempts[node_id], "reason": reason})
                    progressed = True
        if not progressed and ready:
            break

    failed = sorted(node_id for node_id, node in nodes.items() if node.get("state") == "failed")
    blocked = sorted(
        node_id for node_id, node in nodes.items()
        if node.get("state") == "pending"
        and any(nodes.get(dep, {}).get("state") in {"failed", "cancelled"} for dep in node.get("depends_on", []))
    )
    for node_id in blocked:
        nodes[node_id]["state"] = "blocked"

    return {
        "nodes": list(nodes.values()),
        "events": events,
        "failed": failed,
        "blocked": blocked,
        "completed": sorted(node_id for node_id, node in nodes.items() if node.get("state") == "completed"),
        "attempts": attempts,
    }
