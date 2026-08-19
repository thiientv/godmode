#!/usr/bin/env python3
"""Durable task state, checkpoints, and context recovery for Godmode."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def root_dir(root: Path) -> Path:
    return root / ".godmode"


def load(root: Path) -> dict[str, Any]:
    path = root_dir(root) / "task.json"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save(root: Path, state: dict[str, Any]) -> Path:
    directory = root_dir(root)
    directory.mkdir(parents=True, exist_ok=True)
    state = dict(state)
    state.setdefault("schema_version", 1)
    state["updated_at"] = now()
    path = directory / "task.json"
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def init(root: Path, objective: str, risk: str = "medium", task_id: str = "local") -> dict[str, Any]:
    state = {
        "schema_version": 1,
        "task_id": task_id,
        "objective": objective,
        "risk": risk,
        "state": "DISCOVERY",
        "completed": [],
        "active_skills": [],
        "evidence": [],
        "next_check": "establish repository boundary and constraints",
        "limits": [],
        "blocked_by": [],
        "created_at": now(),
        "updated_at": now(),
    }
    save(root, state)
    return state


def checkpoint(root: Path, name: str, state: dict[str, Any] | None = None) -> Path:
    state = state or load(root)
    directory = root_dir(root) / "checkpoints"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.json"
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def recover(root: Path) -> dict[str, Any]:
    state = load(root)
    if state:
        return {"source": "task.json", "state": state, "limits": state.get("limits", [])}
    sources: list[str] = []
    for candidate in ("plan.md", "implementation-plan.md", "PLAN.md", "evidence.json", "evidence-ledger.json"):
        if (root / candidate).is_file():
            sources.append(candidate)
    return {
        "source": "repository-artifacts",
        "state": {"state": "DISCOVERY", "completed": [], "next_check": "inspect durable artifacts"},
        "sources": sources,
        "limits": ["No durable task state was found; lifecycle state is inferred."],
    }


def status(root: Path) -> str:
    state = load(root)
    if not state:
        return "No .godmode/task.json found. Run: godmode init <objective>"
    lines = [f"Task: {state.get('objective', '-')}", f"Risk: {state.get('risk', '-')}", "", f"Lifecycle: {state.get('state', '-')}"]
    lines.append("Completed: " + ", ".join(state.get("completed", [])))
    lines.append("Active skills: " + ", ".join(state.get("active_skills", [])))
    lines.append("Next check: " + str(state.get("next_check", "-")))
    if state.get("limits"):
        lines.append("Limits: " + "; ".join(state["limits"]))
    return "\n".join(lines)
