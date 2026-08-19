#!/usr/bin/env python3
"""Small dependency-free CLI for durable Godmode task execution."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from task_state import checkpoint, init, recover, status, load, save
from events import emit
from risk import assess, impact, changed_files
from evidence import invalidate_ledger


def main() -> int:
    parser = argparse.ArgumentParser(prog="godmode")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init"); p.add_argument("objective"); p.add_argument("--risk", default="medium"); p.add_argument("--task-id", default="local")
    sub.add_parser("status")
    sub.add_parser("resume")
    sub.add_parser("risk")
    sub.add_parser("impact")
    sub.add_parser("checkpoint").add_argument("name")
    p = sub.add_parser("set-state"); p.add_argument("state"); p.add_argument("--next-check", default="run the next observable verification")
    p = sub.add_parser("invalidate"); p.add_argument("evidence", nargs="?", default=".godmode/evidence.json")
    args = parser.parse_args(); root = Path.cwd()
    if args.command == "init":
        state = init(root, args.objective, args.risk, args.task_id); emit(root, "task_started", task_id=args.task_id, risk=args.risk); print(json.dumps(state, indent=2)); return 0
    if args.command == "status": print(status(root)); return 0
    if args.command == "resume":
        recovered = recover(root); emit(root, "context_recovered", source=recovered["source"]); print(json.dumps(recovered, indent=2)); return 0
    if args.command == "risk": print(json.dumps(assess(changed_files(root)), indent=2)); return 0
    if args.command == "impact": print(json.dumps(impact(changed_files(root)), indent=2)); return 0
    if args.command == "checkpoint": checkpoint(root, args.name); print(f"checkpoint: {args.name}"); return 0
    if args.command == "set-state":
        state = load(root)
        if not state: print("no task state", flush=True); return 1
        previous = state.get("state"); state["state"] = args.state; state["next_check"] = args.next_check; save(root, state); emit(root, "state_changed", previous=previous, current=args.state); return 0
    if args.command == "invalidate":
        result = invalidate_ledger(root, Path(args.evidence));
        for reason in result["reasons"]: emit(root, "evidence_invalidated", reason=reason)
        print(json.dumps(result, indent=2)); return 0
    return 1

if __name__ == "__main__": raise SystemExit(main())
