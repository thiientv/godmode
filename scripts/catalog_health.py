#!/usr/bin/env python3
"""Report catalog context cost, resources, routing overlap, and changed skills."""

from __future__ import annotations

import argparse
from itertools import combinations
import json
import math
from pathlib import Path
import subprocess
import sys

from skilllib import discover_skills, load_skill, tokenize


def _git_paths(root: Path, arguments: list[str]) -> set[str]:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or f"git {' '.join(arguments)} failed")
    return set(result.stdout.splitlines())


def _changed_skills(root: Path, reference: str | None) -> set[str]:
    if reference is None:
        return set()

    paths = set()
    for arguments in (
        ["diff", "--name-only", f"{reference}...HEAD", "--", "skills"],
        ["diff", "--name-only", "--", "skills"],
        ["diff", "--cached", "--name-only", "--", "skills"],
        ["ls-files", "--others", "--exclude-standard", "--", "skills"],
    ):
        paths.update(_git_paths(root, arguments))
    return {
        parts[1]
        for line in paths
        if len(parts := Path(line).parts) >= 3 and parts[0] == "skills"
    }


def _resource_count(directory: Path, child: str) -> int:
    resource_root = directory / child
    return (
        sum(
            1
            for path in resource_root.rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix not in {".pyc", ".pyo"}
        )
        if resource_root.is_dir()
        else 0
    )


def _overlap(left: str, right: str) -> float:
    left_terms = tokenize(left)
    right_terms = tokenize(right)
    union = left_terms | right_terms
    return len(left_terms & right_terms) / len(union) if union else 0.0


def build_health_report(root: Path, changed_since: str | None = None) -> dict[str, object]:
    """Build a deterministic catalog health snapshot without declaring quality scores."""

    changed = _changed_skills(root, changed_since)
    records = [load_skill(path) for path in discover_skills(root)]
    skills: list[dict[str, object]] = []
    for record in records:
        body_characters = len(record.body)
        skills.append(
            {
                "name": record.name,
                "body_lines": len(record.body.splitlines()),
                "body_characters": body_characters,
                "estimated_body_tokens": math.ceil(body_characters / 4),
                "description_characters": len(record.description),
                "references": _resource_count(record.directory, "references"),
                "scripts": _resource_count(record.directory, "scripts"),
                "has_routing_eval": (root / "evals" / f"{record.name}.json").is_file(),
                "changed": record.name in changed,
            }
        )

    collisions = [
        {"left": left.name, "right": right.name, "similarity": round(score, 3)}
        for left, right in combinations(records, 2)
        if (score := _overlap(left.description, right.description)) >= 0.45
    ]
    collisions.sort(key=lambda item: (-float(item["similarity"]), str(item["left"]), str(item["right"])))
    return {
        "skill_count": len(skills),
        "changed_since": changed_since,
        "skills": skills,
        "routing_collisions": collisions,
        "notes": [
            "Token counts are a characters/4 planning proxy, not model billing data.",
            "Routing similarity is a review signal, not proof of a collision in a native client.",
        ],
    }


def _print_text(report: dict[str, object]) -> None:
    skills = report["skills"]
    collisions = report["routing_collisions"]
    assert isinstance(skills, list)
    assert isinstance(collisions, list)
    print(f"Catalog health: {report['skill_count']} skills")
    for skill in sorted(skills, key=lambda item: (-int(item["estimated_body_tokens"]), str(item["name"])))[:10]:
        marker = " changed" if skill["changed"] else ""
        print(
            f"- {skill['name']}: ~{skill['estimated_body_tokens']} body tokens, "
            f"{skill['references']} refs, {skill['scripts']} scripts{marker}"
        )
    if collisions:
        print("Routing overlap to review:")
        for collision in collisions:
            print(f"- {collision['left']} / {collision['right']}: {collision['similarity']:.3f}")
    else:
        print("No routing-description overlap reached the review threshold.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--changed-since", help="Git reference used to mark changed skills")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)
    try:
        report = build_health_report(args.root.resolve(), args.changed_since)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        _print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
