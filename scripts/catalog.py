#!/usr/bin/env python3
"""Validate the machine-readable catalog against skills, evals, and documentation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

from skilllib import discover_skills, load_skill


TABLE_SKILL = re.compile(r"(?m)^\|\s*`([a-z0-9-]+)`\s*\|")


def _load_catalog(path: Path) -> tuple[dict[str, object] | None, list[str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return None, [f"{path}: invalid catalog JSON: {error}"]
    if not isinstance(payload, dict):
        return None, [f"{path}: catalog must be a JSON object"]
    return payload, []


def _catalog_names(payload: dict[str, object], path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    if payload.get("schema_version") != 1:
        errors.append(f"{path}: schema_version must be 1")
    groups = payload.get("groups")
    if not isinstance(groups, list) or not groups:
        return [], [*errors, f"{path}: groups must be a non-empty list"]

    names: list[str] = []
    group_ids: set[str] = set()
    for index, group in enumerate(groups):
        if not isinstance(group, dict):
            errors.append(f"{path}: groups[{index}] must be an object")
            continue
        group_id = group.get("id")
        label = group.get("label")
        skills = group.get("skills")
        if not isinstance(group_id, str) or not group_id:
            errors.append(f"{path}: groups[{index}].id must be a non-empty string")
        elif group_id in group_ids:
            errors.append(f"{path}: duplicate group id {group_id!r}")
        else:
            group_ids.add(group_id)
        if not isinstance(label, str) or not label:
            errors.append(f"{path}: groups[{index}].label must be a non-empty string")
        if not isinstance(skills, list) or not all(isinstance(skill, str) and skill for skill in skills):
            errors.append(f"{path}: groups[{index}].skills must be a non-empty string list")
            continue
        names.extend(skills)

    duplicates = sorted({name for name in names if names.count(name) > 1})
    errors.extend(f"{path}: skill appears in multiple groups: {name}" for name in duplicates)
    return names, errors


def _compare_names(label: str, expected: set[str], observed: set[str]) -> list[str]:
    errors: list[str] = []
    missing = sorted(expected - observed)
    extra = sorted(observed - expected)
    if missing:
        errors.append(f"{label}: missing skills: {', '.join(missing)}")
    if extra:
        errors.append(f"{label}: unknown skills: {', '.join(extra)}")
    return errors


def validate_catalog(root: Path) -> list[str]:
    """Return drift between catalog.json and every catalog consumer."""

    path = root / "catalog.json"
    payload, errors = _load_catalog(path)
    if payload is None:
        return errors
    catalog_names, name_errors = _catalog_names(payload, path)
    errors.extend(name_errors)

    discovered = {load_skill(skill_dir).name for skill_dir in discover_skills(root)}
    expected = set(catalog_names)
    errors.extend(_compare_names(str(path), discovered, expected))

    eval_names = {path.stem for path in (root / "evals").glob("*.json")}
    errors.extend(_compare_names("evals/", discovered, eval_names))

    for relative in ("README.md", "README.zh-CN.md"):
        document_path = root / relative
        try:
            table_names = set(TABLE_SKILL.findall(document_path.read_text(encoding="utf-8")))
        except OSError as error:
            errors.append(f"{document_path}: cannot read catalog consumer: {error}")
            continue
        errors.extend(_compare_names(relative, discovered, table_names))

    narrative_path = root / "docs" / "catalog.md"
    try:
        narrative = narrative_path.read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"{narrative_path}: cannot read catalog narrative: {error}")
    else:
        for name in sorted(discovered):
            if f"`{name}`" not in narrative and name not in narrative:
                errors.append(f"{narrative_path}: public skill is not documented: {name}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    errors = validate_catalog(args.root.resolve())
    if errors:
        print(f"Catalog validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Catalog metadata, documentation, and eval fixtures are synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
