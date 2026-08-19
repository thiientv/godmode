#!/usr/bin/env python3
"""Deterministic risk scoring and change-impact analysis."""
from __future__ import annotations
import fnmatch
from pathlib import Path

RULES = [
    ("critical", 4, ("payment", "billing", "production", "infrastructure", "secrets", "credentials")),
    ("high", 3, ("auth", "security", "migration", "migrations", "database", "schema", "public-api", "deploy")),
    ("medium", 2, ("api", "backend", "frontend", "service", "config", "workflow")),
]


def assess(paths: list[str]) -> dict:
    score = 0
    reasons: list[str] = []
    for path in paths:
        lowered = path.lower()
        if any(token in lowered for token in ("test", "docs", "readme", "changelog")):
            score -= 1
            continue
        for label, weight, tokens in RULES:
            if any(token in lowered for token in tokens):
                score = max(score, weight)
                reasons.append(f"{path}: {label} risk signal")
                break
        else:
            score = max(score, 1)
    if not paths:
        level = "low"
    elif score >= 4:
        level = "critical"
    elif score >= 3:
        level = "high"
    elif score >= 2:
        level = "medium"
    else:
        level = "low"
    return {"risk": level, "score": score, "reasons": reasons}


def impact(paths: list[str]) -> dict:
    domains: dict[str, list[str]] = {}
    patterns = {
        "security": ("auth", "security", "crypto", "permission", "secret"),
        "data": ("migration", "database", "schema", "sql", "prisma"),
        "api": ("api", "route", "controller", "endpoint", "graphql"),
        "ui": ("frontend", "component", "page", "css", "tsx", "jsx"),
        "operations": ("docker", "deploy", "terraform", "workflow", "infra", "k8s"),
        "tests": ("test", "spec"),
    }
    for path in paths:
        low = path.lower()
        for domain, tokens in patterns.items():
            if any(token in low for token in tokens):
                domains.setdefault(domain, []).append(path)
    suggestions = []
    if "security" in domains: suggestions.append("security-and-hardening")
    if "data" in domains: suggestions.append("safe-migrations")
    if "api" in domains: suggestions.append("api-and-interface-design")
    if "ui" in domains: suggestions.extend(["frontend-design", "ui-ux-review"])
    if "operations" in domains: suggestions.append("release-engineering")
    suggestions.extend(["test-strategy", "completion-verification"])
    return {"domains": domains, "suggested_skills": list(dict.fromkeys(suggestions))}


def changed_files(root: Path) -> list[str]:
    try:
        import subprocess
        raw = subprocess.check_output(["git", "diff", "--name-only", "HEAD"], cwd=root, text=True)
        return [line for line in raw.splitlines() if line]
    except (OSError, subprocess.CalledProcessError):
        return []
