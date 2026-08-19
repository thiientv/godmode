#!/usr/bin/env python3
"""Skill dependency and composition metadata."""
from __future__ import annotations
import json
from pathlib import Path

GRAPH_PATH = Path(__file__).resolve().parents[1] / "skill-graph.json"


def load(path: Path = GRAPH_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(graph: dict) -> list[str]:
    errors = []
    skills = graph.get("skills")
    if not isinstance(skills, dict):
        return ["skills must be an object"]
    known = set(skills)
    for name, meta in skills.items():
        if not isinstance(meta, dict):
            errors.append(f"{name}: metadata must be an object")
            continue
        for field in ("requires", "often_followed_by", "conflicts_with"):
            values = meta.get(field, [])
            if not isinstance(values, list) or not all(item in known for item in values):
                errors.append(f"{name}.{field}: unknown skill reference")
    return errors


def recommend(active: list[str], graph: dict | None = None) -> list[str]:
    graph = graph or load()
    known = set(graph.get("skills", {}))
    result: list[str] = []
    for name in active:
        for candidate in graph.get("skills", {}).get(name, {}).get("often_followed_by", []):
            if candidate in known and candidate not in active and candidate not in result:
                result.append(candidate)
    return result
