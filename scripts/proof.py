#!/usr/bin/env python3
"""Build a small auditable proof graph from a task evidence ledger."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any


def build(record: dict[str, Any]) -> dict[str, Any]:
    evidence = [x for x in record.get("evidence", []) if isinstance(x, dict)]
    nodes = [{"id": "task", "type": "task", "state": record.get("state"), "risk": record.get("risk")}]
    edges = []
    for index, item in enumerate(evidence):
        node_id = f"evidence:{index}"
        nodes.append({"id": node_id, "type": item.get("kind", "evidence"), "claim": item.get("claim", ""), "valid": item.get("valid", True) is not False, "scope": item.get("scope", {})})
        edges.append({"from": "task", "to": node_id, "relation": "proved-by"})
    valid = [node for node in nodes if node["id"] != "task" and node.get("valid")]
    return {"nodes": nodes, "edges": edges, "proof_count": len(valid), "proof_complete": bool(valid) and all(node.get("valid") for node in nodes if node["id"] != "task")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("record", type=Path)
    payload = json.loads(parser.parse_args().record.read_text(encoding="utf-8")); print(json.dumps(build(payload), indent=2, sort_keys=True)); return 0

if __name__ == "__main__": raise SystemExit(main())
