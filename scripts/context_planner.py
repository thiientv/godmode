#!/usr/bin/env python3
"""Plan context under a deterministic token/character budget."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContextItem:
    name: str
    size: int
    priority: int = 0
    required: bool = False


def plan(items: list[ContextItem], budget: int) -> dict:
    if budget < 0:
        raise ValueError("budget must be non-negative")
    ordered = sorted(items, key=lambda item: (-item.required, -item.priority, item.name))
    selected: list[ContextItem] = []
    excluded: list[ContextItem] = []
    used = 0
    for item in ordered:
        if item.required or used + item.size <= budget:
            selected.append(item)
            used += item.size
        else:
            excluded.append(item)
    required_over_budget = sum(item.size for item in selected if item.required) > budget
    return {
        "budget": budget,
        "used": used,
        "remaining": budget - used,
        "selected": [item.name for item in selected],
        "excluded": [item.name for item in excluded],
        "required_over_budget": required_over_budget,
    }
