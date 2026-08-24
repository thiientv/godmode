#!/usr/bin/env python3
"""Dependency-free, explainable skill routing for Godmode."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

GRAPH_PATH = Path(__file__).resolve().parents[1] / "skill-graph.json"


def load(path: Path = GRAPH_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9][a-z0-9_-]{2,}", text.lower()))


def route(task: str, graph: dict | None = None, limit: int = 5) -> dict:
    graph = graph or load()
    skills = graph.get("skills", {})
    tokens = tokenize(task)
    scored = []
    for name, meta in skills.items():
        aliases = {str(x).lower() for x in meta.get("keywords", [])}
        words = tokenize(name.replace("-", " "))
        positive = sorted(tokens & (words | aliases))
        negative = {str(x).lower() for x in meta.get("negative_keywords", [])}
        penalty = len(tokens & negative)
        score = len(positive) - penalty
        if name in task.lower():
            score += 3
        if score > 0:
            scored.append({
                "skill": name,
                "score": score,
                "matched": positive or [name],
                "negative_matches": sorted(tokens & negative),
                "reason": f"matched task signals: {', '.join(positive or [name])}",
            })
    scored.sort(key=lambda x: (-x["score"], x["skill"]))
    selected = scored[: max(0, limit)]
    names = {item["skill"] for item in selected}
    missing = []
    for item in selected:
        for dep in skills[item["skill"]].get("requires", []):
            if dep not in names and dep not in missing:
                missing.append(dep)
    expanded = list(selected)
    for dep in missing:
        expanded.append({"skill": dep, "score": 0, "matched": [], "negative_matches": [], "reason": "required dependency"})
    top_score = selected[0]["score"] if selected else 0
    confidence = round(min(1.0, top_score / 4.0) if selected else 0.0, 2)
    return {
        "task": task,
        "skills": expanded,
        "required_dependencies": missing,
        "confidence": confidence,
        "fallback_required": not bool(selected),
        "explainable": True,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("task")
    p.add_argument("--limit", type=int, default=5)
    args = p.parse_args()
    print(json.dumps(route(args.task, limit=args.limit), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
