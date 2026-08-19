#!/usr/bin/env python3
"""Aggregate repeated agent runs by quality, cost, and latency."""
from __future__ import annotations
import json
from pathlib import Path
from statistics import mean, stdev
from typing import Any


def summarize(runs: list[dict[str, Any]]) -> dict[str, Any]:
    if not runs: return {"runs": 0}
    quality = [float(x.get("quality", 0)) for x in runs]
    tokens = [float(x.get("tokens", 0)) for x in runs]
    latency = [float(x.get("latency_ms", 0)) for x in runs]
    passed = sum(bool(x.get("passed")) for x in runs)
    return {
        "runs": len(runs), "pass_rate": passed / len(runs),
        "quality": {"mean": mean(quality), "stdev": stdev(quality) if len(quality) > 1 else 0.0},
        "tokens": {"mean": mean(tokens)}, "latency_ms": {"mean": mean(latency)},
        "quality_per_1k_tokens": mean(quality) / (mean(tokens) / 1000) if mean(tokens) else 0.0,
    }


def compare(baseline: list[dict[str, Any]], candidate: list[dict[str, Any]]) -> dict[str, Any]:
    left, right = summarize(baseline), summarize(candidate)
    return {"baseline": left, "candidate": right, "delta": {
        "pass_rate": right.get("pass_rate", 0) - left.get("pass_rate", 0),
        "quality": right.get("quality", {}).get("mean", 0) - left.get("quality", {}).get("mean", 0),
        "tokens": right.get("tokens", {}).get("mean", 0) - left.get("tokens", {}).get("mean", 0),
        "latency_ms": right.get("latency_ms", {}).get("mean", 0) - left.get("latency_ms", {}).get("mean", 0),
    }}


def load(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, list) else payload.get("runs", [])
