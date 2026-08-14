#!/usr/bin/env python3
"""Inspect and validate a built Godmode release archive before publication."""

from __future__ import annotations

import argparse
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile

from validate import validate_repository


REQUIRED_PATHS = {
    "LICENSE",
    "README.md",
    "catalog.json",
    "compatibility/evidence.json",
    "package.json",
    "skills",
}
FORBIDDEN_SEGMENTS = {".git", ".idea", ".pytest_cache", ".vscode", "__pycache__", "node_modules"}


def _safe_members(archive: tarfile.TarFile) -> tuple[list[tarfile.TarInfo], list[str]]:
    errors: list[str] = []
    members = archive.getmembers()
    for member in members:
        path = PurePosixPath(member.name)
        if path.is_absolute() or ".." in path.parts:
            errors.append(f"archive contains unsafe path: {member.name}")
        if member.issym() or member.islnk() or member.isdev():
            errors.append(f"archive contains unsupported link/device entry: {member.name}")
        if FORBIDDEN_SEGMENTS & set(path.parts):
            errors.append(f"archive contains forbidden generated/private path: {member.name}")
    return members, errors


def _release_root(members: list[tarfile.TarInfo]) -> tuple[str | None, list[str]]:
    roots = {PurePosixPath(member.name).parts[0] for member in members if PurePosixPath(member.name).parts}
    if len(roots) != 1:
        return None, ["archive must contain exactly one top-level directory"]
    return next(iter(roots)), []


def validate_archive(path: Path) -> list[str]:
    """Return archive safety, payload, and repository validation errors."""

    try:
        archive = tarfile.open(path, mode="r:gz")
    except (OSError, tarfile.TarError) as error:
        return [f"{path}: cannot open release archive: {error}"]

    with archive:
        members, errors = _safe_members(archive)
        root_name, root_errors = _release_root(members)
        errors.extend(root_errors)
        if errors or root_name is None:
            return errors

        relative_paths = {
            str(PurePosixPath(*PurePosixPath(member.name).parts[1:]))
            for member in members
            if len(PurePosixPath(member.name).parts) > 1
        }
        for required in sorted(REQUIRED_PATHS):
            if required not in relative_paths and not any(
                candidate.startswith(f"{required}/") for candidate in relative_paths
            ):
                errors.append(f"archive is missing required payload: {required}")
        if errors:
            return errors

        with tempfile.TemporaryDirectory(prefix="godmode-release-") as temporary_directory:
            archive.extractall(temporary_directory)
            extracted_root = Path(temporary_directory) / root_name
            errors.extend(validate_repository(extracted_root))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args(argv)
    errors = validate_archive(args.archive.resolve())
    if errors:
        print(f"Release smoke test failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Release archive passed structural, safety, and repository validation: {args.archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
