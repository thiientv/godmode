#!/usr/bin/env python3
"""Validate or render the compatibility matrix from recorded evidence."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys


START_MARKER = "<!-- compatibility-table:start -->"
END_MARKER = "<!-- compatibility-table:end -->"


def _load_evidence(path: Path) -> tuple[dict[str, object] | None, list[str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return None, [f"{path}: invalid compatibility evidence: {error}"]
    if not isinstance(payload, dict):
        return None, [f"{path}: evidence must be a JSON object"]
    return payload, []


def _escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _render_table(surfaces: list[dict[str, object]]) -> str:
    lines = [
        START_MARKER,
        "| Surface | Current evidence | Status |",
        "| --- | --- | --- |",
    ]
    for surface in surfaces:
        lines.append(
            "| "
            + " | ".join(
                _escape_cell(str(surface[field]))
                for field in ("surface", "evidence", "status")
            )
            + " |"
        )
    lines.append(END_MARKER)
    return "\n".join(lines)


def _validate_surfaces(payload: dict[str, object], path: Path) -> tuple[list[dict[str, object]], list[str]]:
    errors: list[str] = []
    if payload.get("schema_version") != 1:
        errors.append(f"{path}: schema_version must be 1")
    raw_surfaces = payload.get("surfaces")
    if not isinstance(raw_surfaces, list) or not raw_surfaces:
        return [], [*errors, f"{path}: surfaces must be a non-empty list"]

    surfaces: list[dict[str, object]] = []
    identifiers: set[str] = set()
    for index, item in enumerate(raw_surfaces):
        if not isinstance(item, dict):
            errors.append(f"{path}: surfaces[{index}] must be an object")
            continue
        for field in ("id", "surface", "evidence", "status", "observed_at"):
            value = item.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{path}: surfaces[{index}].{field} must be a non-empty string")
        identifier = item.get("id")
        if isinstance(identifier, str):
            if identifier in identifiers:
                errors.append(f"{path}: duplicate surface id {identifier!r}")
            identifiers.add(identifier)
        observed_at = item.get("observed_at")
        if isinstance(observed_at, str):
            try:
                date.fromisoformat(observed_at)
            except ValueError:
                errors.append(f"{path}: surfaces[{index}].observed_at must be YYYY-MM-DD")
        version = item.get("client_version")
        if version is not None and (not isinstance(version, str) or not version.strip()):
            errors.append(f"{path}: surfaces[{index}].client_version must be null or a non-empty string")
        limitations = item.get("limitations")
        if not isinstance(limitations, list) or not all(
            isinstance(limitation, str) and limitation.strip() for limitation in limitations
        ):
            errors.append(f"{path}: surfaces[{index}].limitations must be a string list")
        surfaces.append(item)
    return surfaces, errors


def _replace_table(document: str, table: str) -> str:
    pattern = re.compile(re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL)
    if pattern.search(document) is None:
        raise ValueError("compatibility document is missing generated table markers")
    return pattern.sub(table, document, count=1)


def validate_compatibility(root: Path) -> list[str]:
    """Return schema and documentation drift errors for compatibility evidence."""

    evidence_path = root / "compatibility" / "evidence.json"
    payload, errors = _load_evidence(evidence_path)
    if payload is None:
        return errors
    surfaces, surface_errors = _validate_surfaces(payload, evidence_path)
    errors.extend(surface_errors)

    document_path = root / "docs" / "compatibility.md"
    try:
        document = document_path.read_text(encoding="utf-8")
        expected = _replace_table(document, _render_table(surfaces))
    except (OSError, ValueError) as error:
        errors.append(f"{document_path}: {error}")
    else:
        if document != expected:
            errors.append(f"{document_path}: generated compatibility table is stale")
    return errors


def write_compatibility(root: Path) -> list[str]:
    """Render validated evidence into the compatibility document."""

    evidence_path = root / "compatibility" / "evidence.json"
    payload, errors = _load_evidence(evidence_path)
    if payload is None:
        return errors
    surfaces, surface_errors = _validate_surfaces(payload, evidence_path)
    errors.extend(surface_errors)
    if errors:
        return errors

    document_path = root / "docs" / "compatibility.md"
    try:
        document = document_path.read_text(encoding="utf-8")
        rendered = _replace_table(document, _render_table(surfaces))
        document_path.write_text(rendered, encoding="utf-8")
    except (OSError, ValueError) as error:
        return [f"{document_path}: {error}"]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "write"), nargs="?", default="check")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    root = args.root.resolve()
    errors = write_compatibility(root) if args.command == "write" else validate_compatibility(root)
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Compatibility evidence is valid and synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
