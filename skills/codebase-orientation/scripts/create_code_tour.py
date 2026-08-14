#!/usr/bin/env python3
"""Create a CodeTour file from a small validated orientation specification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import sys


SCHEMA_URL = "https://aka.ms/codetour-schema"


def _load_spec(path: Path) -> tuple[dict[str, object] | None, list[str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return None, [f"{path}: invalid tour specification: {error}"]
    if not isinstance(payload, dict):
        return None, [f"{path}: specification must be a JSON object"]
    return payload, []


def _resolve_source(root: Path, raw_path: str) -> tuple[Path | None, list[str]]:
    portable_path = PurePosixPath(raw_path)
    if portable_path.is_absolute() or ".." in portable_path.parts:
        return None, [f"step file must be a repository-relative path: {raw_path}"]
    source = (root / Path(*portable_path.parts)).resolve()
    try:
        source.relative_to(root)
    except ValueError:
        return None, [f"step file escapes the repository: {raw_path}"]
    if not source.is_file():
        return None, [f"step file does not exist: {raw_path}"]
    return source, []


def validate_spec(root: Path, payload: dict[str, object]) -> list[str]:
    """Return invalid metadata, paths, anchors, and descriptions."""

    errors: list[str] = []
    title = payload.get("title")
    if not isinstance(title, str) or not title.strip():
        errors.append("title must be a non-empty string")
    description = payload.get("description")
    if description is not None and (not isinstance(description, str) or not description.strip()):
        errors.append("description must be omitted or a non-empty string")

    steps = payload.get("steps")
    if not isinstance(steps, list) or not steps:
        return [*errors, "steps must be a non-empty list"]
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            errors.append(f"steps[{index}] must be an object")
            continue
        file_value = step.get("file")
        line_value = step.get("line")
        description_value = step.get("description")
        if not isinstance(file_value, str) or not file_value.strip():
            errors.append(f"steps[{index}].file must be a non-empty string")
            continue
        source, source_errors = _resolve_source(root, file_value)
        errors.extend(f"steps[{index}]: {error}" for error in source_errors)
        if not isinstance(line_value, int) or isinstance(line_value, bool) or line_value < 1:
            errors.append(f"steps[{index}].line must be a positive integer")
        elif source is not None:
            line_count = len(source.read_text(encoding="utf-8").splitlines())
            if line_value > max(1, line_count):
                errors.append(f"steps[{index}].line exceeds {file_value} ({line_count} lines)")
        if not isinstance(description_value, str) or not description_value.strip():
            errors.append(f"steps[{index}].description must be a non-empty string")
        step_title = step.get("title")
        if step_title is not None and (not isinstance(step_title, str) or not step_title.strip()):
            errors.append(f"steps[{index}].title must be omitted or a non-empty string")
    return errors


def render_tour(payload: dict[str, object]) -> dict[str, object]:
    """Render validated input into the portable CodeTour JSON shape."""

    tour: dict[str, object] = {
        "$schema": SCHEMA_URL,
        "title": payload["title"],
        "steps": payload["steps"],
    }
    if "description" in payload:
        tour["description"] = payload["description"]
    return tour


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path, help="JSON orientation specification")
    parser.add_argument("output", type=Path, help="destination .tour file")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    payload, errors = _load_spec(args.spec.resolve())
    if payload is not None:
        errors.extend(validate_spec(root, payload))
    if args.output.suffix != ".tour":
        errors.append("output must use the .tour extension")
    if errors or payload is None:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(render_tour(payload), indent=2) + "\n", encoding="utf-8")
    print(f"Created validated CodeTour: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
