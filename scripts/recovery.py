#!/usr/bin/env python3
"""Improve context recovery using durable state, checkpoints, events, and artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def latest_checkpoint(root: Path) -> tuple[str | None, dict[str, Any] | None]:
    directory = root / ".godmode" / "checkpoints"
    if not directory.is_dir():
        return None, None
    files = sorted(directory.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in files:
        payload = read_json(path)
        if isinstance(payload, dict):
            return path.name, payload
    return None, None


def recover_context(root: Path) -> dict[str, Any]:
    state = read_json(root / ".godmode" / "task.json")
    checkpoint_name, checkpoint_state = latest_checkpoint(root)
    artifacts = [name for name in ("plan.md", "implementation-plan.md", "PLAN.md", ".godmode/evidence.json", ".godmode/events.jsonl") if (root / name).is_file()]
    if isinstance(state, dict):
        source = "task.json"
        active = state
    elif isinstance(checkpoint_state, dict):
        source = f"checkpoint:{checkpoint_name}"
        active = checkpoint_state
    else:
        source = "repository-artifacts"
        active = {"state": "DISCOVERY", "completed": [], "next_check": "inspect repository artifacts"}

    events: list[Any] = []
    event_path = root / ".godmode" / "events.jsonl"
    if event_path.is_file():
        for line in event_path.read_text(encoding="utf-8").splitlines()[-20:]:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    limits = active.get("limits", []) if isinstance(active, dict) else []
    if not isinstance(limits, list):
        limits = [str(limits)]
    if source == "repository-artifacts":
        limits.append("No durable task state or checkpoint was found; lifecycle state is inferred.")
    return {
        "source": source,
        "state": active,
        "checkpoint": checkpoint_name,
        "artifacts": artifacts,
        "recent_events": events,
        "limits": sorted(set(str(item) for item in limits)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?", default=Path("."))
    args = parser.parse_args()
    print(json.dumps(recover_context(args.root), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
