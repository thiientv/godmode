#!/usr/bin/env python3
"""Append-only execution events for observable agent runs."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EVENT_TYPES = {"task_started", "skill_discovered", "skill_activated", "state_changed", "tool_started", "tool_finished", "evidence_created", "evidence_invalidated", "test_started", "test_finished", "review_started", "review_finished", "blocked", "context_recovered", "task_completed"}


def emit(root: Path, event_type: str, **data: Any) -> dict[str, Any]:
    if event_type not in EVENT_TYPES:
        raise ValueError(f"unknown event type: {event_type}")
    event = {"schema_version": 1, "type": event_type, "timestamp": datetime.now(timezone.utc).isoformat(), **data}
    path = root / ".godmode" / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
    return event


def read(root: Path) -> list[dict[str, Any]]:
    path = root / ".godmode" / "events.jsonl"
    if not path.is_file():
        return []
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def last(root: Path) -> dict[str, Any] | None:
    events = read(root)
    return events[-1] if events else None
