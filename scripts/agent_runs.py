#!/usr/bin/env python3
"""Normalize agent telemetry and inspect durable Godmode runs."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 1


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "timestamp": event.get("timestamp") or now(),
        "type": str(event.get("type", "unknown")),
        "source": str(event.get("source", "agent")),
        "run_id": event.get("run_id"),
        "task_id": event.get("task_id"),
        "skill": event.get("skill"),
        "tool": event.get("tool"),
        "command": event.get("command"),
        "status": event.get("status"),
        "details": event.get("details", {}),
    }


def normalize_run(payload: dict[str, Any]) -> dict[str, Any]:
    events = payload.get("events", [])
    if not isinstance(events, list):
        events = []
    normalized_events = [normalize_event(item) for item in events if isinstance(item, dict)]
    usage = payload.get("usage", {})
    if not isinstance(usage, dict):
        usage = {}
    limits = payload.get("limits", [])
    if not isinstance(limits, list):
        limits = [str(limits)]
    return {
        "schema_version": SCHEMA_VERSION,
        "adapter": str(payload.get("adapter", "unknown")),
        "client_version": str(payload.get("client_version", "unknown")),
        "model": str(payload.get("model", "unknown")),
        "run_id": str(payload.get("run_id", "")),
        "task_id": str(payload.get("task_id", "")),
        "started_at": payload.get("started_at") or now(),
        "finished_at": payload.get("finished_at"),
        "events": normalized_events,
        "usage": usage,
        "final_message": payload.get("final_message", ""),
        "skills": sorted({e["skill"] for e in normalized_events if e.get("skill")}),
        "limits": [str(x) for x in limits if str(x).strip()],
    }


def run_files(root: Path) -> Iterable[Path]:
    directory = root / ".godmode" / "runs"
    if not directory.is_dir():
        return []
    return sorted(directory.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)


def load_run(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"run must be an object: {path}")
    return normalize_run(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("normalize")
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    p = sub.add_parser("list")
    p.add_argument("root", type=Path, nargs="?", default=Path("."))
    p = sub.add_parser("show")
    p.add_argument("run", type=Path)
    args = parser.parse_args()

    if args.command == "normalize":
        run = load_run(args.input)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"normalized run: {args.output}")
        return 0

    if args.command == "list":
        files = list(run_files(args.root))
        if not files:
            print("No .godmode/runs/*.json found.")
            return 0
        for path in files:
            try:
                run = load_run(path)
                usage = run.get("usage", {})
                print(f"{path.name}\t{run.get('run_id') or '-'}\t{run.get('adapter')}\t{run.get('model')}\t{','.join(run.get('skills', []))}\t{usage.get('input_tokens', 0)}/{usage.get('output_tokens', 0)}")
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                print(f"{path.name}\tINVALID\t{exc}")
        return 0

    run = load_run(args.run)
    print(json.dumps(run, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
