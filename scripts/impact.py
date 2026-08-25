#!/usr/bin/env python3
"""Deterministic change-impact analysis for common repository artifacts."""
from __future__ import annotations
import argparse, json
from pathlib import Path

RULES = [
    ("security", ("auth", "security", "permission", "token", "secret"), ("security-and-hardening", "test-strategy", "completion-verification")),
    ("database", ("migration", "schema", "database", ".sql"), ("database-design", "safe-migrations", "test-strategy")),
    ("api", ("api", "route", "endpoint", "openapi", "schema"), ("api-and-interface-design", "test-strategy", "completion-verification")),
    ("frontend", ("frontend", "component", ".tsx", ".jsx", "ui", "css"), ("frontend-design", "ui-ux-review", "completion-verification")),
    ("release", ("dockerfile", "deploy", "terraform", "helm", ".github/workflows", "production"), ("release-engineering", "completion-verification")),
]


def analyze(paths: list[str]) -> dict:
    normalized = [p.replace("\\", "/").lower() for p in paths]
    domains, skills = set(), []
    for domain, signals, recommendations in RULES:
        if any(any(signal in path for signal in signals) for path in normalized):
            domains.add(domain)
            for skill in recommendations:
                if skill not in skills: skills.append(skill)
    if not domains:
        skills = ["codebase-orientation", "completion-verification"]
    return {"changed_paths": paths, "impact_domains": sorted(domains), "recommended_skills": skills, "validation": ["fresh-test-result", "evidence-ledger"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("paths", nargs="+"); args = parser.parse_args(); print(json.dumps(analyze(args.paths), indent=2, sort_keys=True)); return 0

if __name__ == "__main__": raise SystemExit(main())
