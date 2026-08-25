#!/usr/bin/env python3
"""Dependency-free, explainable skill routing for Godmode."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

GRAPH_PATH = Path(__file__).resolve().parents[1] / "skill-graph.json"
RISK_KEYWORDS = {
    "critical": {"production outage", "data loss", "destructive", "irreversible"},
    "high": {"security", "vulnerability", "authentication", "authorization", "migration", "production", "incident"},
    "medium": {"api", "database", "deploy", "release", "performance"},
}
LIFECYCLE_KEYWORDS = {
    "DESIGN": {"design", "architecture", "solution"},
    "PLANNING": {"plan", "planning", "roadmap"},
    "IMPLEMENTATION": {"implement", "implementation", "build", "fix", "change"},
    "TESTING": {"test", "testing", "qa", "regression", "coverage"},
    "REVIEW": {"review", "audit", "security review"},
    "VERIFICATION": {"verify", "verification", "evidence", "validate"},
    "RELEASE": {"release", "deploy", "deployment", "production"},
}


def load(path: Path = GRAPH_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9][a-z0-9_-]{2,}", text.lower()))


def _risk(task: str) -> str:
    lowered = task.lower()
    if any(x in lowered for x in RISK_KEYWORDS["critical"]): return "critical"
    if any(x in lowered for x in RISK_KEYWORDS["high"]): return "high"
    if any(x in lowered for x in RISK_KEYWORDS["medium"]): return "medium"
    return "low"


def _lifecycle(task: str) -> list[str]:
    lowered = task.lower()
    return [state for state, signals in LIFECYCLE_KEYWORDS.items() if any(signal in lowered for signal in signals)]


def _expand_dependencies(selected: list[str], skills: dict) -> list[str]:
    result = list(selected); seen = set(result); queue = list(selected)
    while queue:
        name = queue.pop(0)
        for dep in skills.get(name, {}).get("requires", []):
            if dep not in seen:
                seen.add(dep); result.append(dep); queue.append(dep)
    return result


def _conflicts(names: list[str], skills: dict) -> list[dict]:
    selected = set(names); conflicts = []
    for name in names:
        for other in skills.get(name, {}).get("conflicts_with", []):
            if other in selected and name < other:
                conflicts.append({"skills": [name, other], "reason": "skill conflict declared in graph"})
    return conflicts


def route(task: str, graph: dict | None = None, limit: int = 5) -> dict:
    graph = graph or load(); skills = graph.get("skills", {}); tokens = tokenize(task)
    scored = []
    for name, meta in skills.items():
        aliases = {str(x).lower() for x in meta.get("keywords", [])}
        words = tokenize(name.replace("-", " "))
        positive = sorted(tokens & (words | aliases))
        negative = {str(x).lower() for x in meta.get("negative_keywords", [])}
        penalty = len(tokens & negative); score = len(positive) - penalty
        if name in task.lower(): score += 3
        if score > 0:
            scored.append({"skill": name, "score": score, "matched": positive or [name], "negative_matches": sorted(tokens & negative), "reason": f"matched task signals: {', '.join(positive or [name])}"})
    scored.sort(key=lambda x: (-x["score"], x["skill"]))
    selected = scored[: max(0, limit)]; selected_names = [item["skill"] for item in selected]
    expanded_names = _expand_dependencies(selected_names, skills)
    missing = [name for name in expanded_names if name not in selected_names]
    expanded = list(selected)
    for dep in missing:
        expanded.append({"skill": dep, "score": 0, "matched": [], "negative_matches": [], "reason": "required transitive dependency"})
    risk = _risk(task); lifecycle = _lifecycle(task); conflicts = _conflicts(expanded_names, skills)
    top_score = selected[0]["score"] if selected else 0
    confidence = round(min(1.0, top_score / 4.0) if selected else 0.0, 2)
    if conflicts: confidence = max(0.0, round(confidence - 0.2, 2))
    return {
        "task": task,
        "skills": expanded,
        "required_dependencies": missing,
        "risk": risk,
        "lifecycle_signals": lifecycle,
        "conflicts": conflicts,
        "confidence": confidence,
        "fallback_required": not bool(selected),
        "explainable": True,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("task"); p.add_argument("--limit", type=int, default=5)
    args = p.parse_args(); print(json.dumps(route(args.task, limit=args.limit), indent=2, sort_keys=True)); return 0

if __name__ == "__main__": raise SystemExit(main())
