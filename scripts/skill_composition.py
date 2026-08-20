#!/usr/bin/env python3
"""Compose skills from dependency metadata without replacing native discovery."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

GRAPH_PATH = Path(__file__).resolve().parents[1] / "skill-graph.json"


def load(path: Path = GRAPH_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def transitive_requirements(active: list[str], graph: dict | None = None) -> list[str]:
    graph = graph or load()
    skills = graph.get("skills", {})
    result: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(name: str) -> None:
        if name in visited or name in visiting or name not in skills:
            return
        visiting.add(name)
        for dep in skills[name].get("requires", []):
            visit(dep)
            if dep not in active and dep not in result:
                result.append(dep)
        visiting.remove(name)
        visited.add(name)

    for name in active:
        visit(name)
    return result


def compose(active: list[str], graph: dict | None = None) -> dict:
    graph = graph or load()
    skills = graph.get("skills", {})
    required = transitive_requirements(active, graph)
    recommendations: list[str] = []
    conflicts: list[str] = []
    for name in active:
        meta = skills.get(name, {})
        for item in meta.get("often_followed_by", []):
            if item not in active and item not in recommendations:
                recommendations.append(item)
        for item in meta.get("conflicts_with", []):
            if item in active and item not in conflicts:
                conflicts.append(f"{name}:{item}")
    return {"active": active, "required": required, "recommended": recommendations, "conflicts": conflicts}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skills", nargs="+", help="active skill names")
    args = parser.parse_args()
    result = compose(args.skills)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result["conflicts"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
