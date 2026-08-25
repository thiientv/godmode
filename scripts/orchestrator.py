#!/usr/bin/env python3
"""Deterministic P0 orchestration primitives with dependency-aware concurrency."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Callable

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
        return {"task": self.task, "completed": self.completed, "findings": self.findings, "files_changed": self.files_changed, "evidence": self.evidence, "open_questions": self.open_questions, "next_action": self.next_action}


def ready_nodes(graph: dict) -> list[str]:
    nodes = graph.get("nodes", [])
    states = {n["id"]: n.get("state", "pending") for n in nodes}
    return sorted(n["id"] for n in nodes if n.get("state", "pending") == "pending" and all(states.get(dep) == "completed" for dep in n.get("depends_on", [])))


def _run_one(node: dict, runner: Callable[[dict], object]) -> tuple[str, object, str | None]:
    try:
        result = runner(node)
        if result is False:
            raise RuntimeError("runner returned false")
        return node["id"], result, None
    except Exception as exc:
        return node["id"], None, str(getattr(exc, "reason", "tool_error"))


def execute(graph: dict, runner: Callable[[dict], object], policy: RetryPolicy | None = None, max_workers: int = 4) -> dict:
    """Run independent ready nodes concurrently; dependency order remains deterministic."""
    policy = policy or RetryPolicy(); nodes = {n["id"]: dict(n) for n in graph.get("nodes", [])}
    attempts = {node_id: 0 for node_id in nodes}; events: list[dict] = []
    workers = max(1, min(max_workers, len(nodes) or 1))

    while True:
        ready = ready_nodes({"nodes": list(nodes.values())})
        if not ready: break
        for node_id in ready:
            attempts[node_id] += 1; nodes[node_id]["state"] = "running"
            events.append({"node": node_id, "event": "started", "attempt": attempts[node_id]})
        progressed = False
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="godmode") as pool:
            futures = {pool.submit(_run_one, nodes[node_id], runner): node_id for node_id in ready}
            results = [future.result() for future in as_completed(futures)]
        for node_id, _result, reason in sorted(results, key=lambda item: item[0]):
            if reason is None:
                nodes[node_id]["state"] = "completed"; events.append({"node": node_id, "event": "completed", "attempt": attempts[node_id]})
            elif policy.should_retry(reason, attempts[node_id]):
                nodes[node_id]["state"] = "pending"; events.append({"node": node_id, "event": "retry", "attempt": attempts[node_id], "reason": reason})
            else:
                nodes[node_id]["state"] = "failed"; events.append({"node": node_id, "event": "failed", "attempt": attempts[node_id], "reason": reason})
            progressed = True
        if not progressed: break

    failed = sorted(node_id for node_id, node in nodes.items() if node.get("state") == "failed")
    blocked = sorted(node_id for node_id, node in nodes.items() if node.get("state") == "pending" and any(nodes.get(dep, {}).get("state") in {"failed", "cancelled", "blocked"} for dep in node.get("depends_on", [])))
    for node_id in blocked: nodes[node_id]["state"] = "blocked"
    return {"nodes": list(nodes.values()), "events": events, "failed": failed, "blocked": blocked, "completed": sorted(node_id for node_id, node in nodes.items() if node.get("state") == "completed"), "attempts": attempts, "max_workers": workers}
