#!/usr/bin/env python3
"""Check public files and GitHub workflows for avoidable security hazards."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable


ACTION_REFERENCE = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)")
FULL_COMMIT_SHA = re.compile(r"^[0-9a-fA-F]{40}$")
POSIX_HOME_PATH = re.compile(r"(?<![A-Za-z0-9])/(?:Users|home)/([A-Za-z0-9._-]+)")
WINDOWS_HOME_PATH = re.compile(r"(?i)(?:^|[^A-Za-z0-9])(?:[A-Z]:)?\\Users\\([A-Za-z0-9._-]+)")
SAFE_PLACEHOLDERS = {"absolute", "example", "name", "path", "runner", "user", "username"}
DANGEROUS_CODEPOINTS = {
    0x061C,
    0x200B,
    0x200E,
    0x200F,
    0x202A,
    0x202B,
    0x202C,
    0x202D,
    0x202E,
    0x2060,
    0x2066,
    0x2067,
    0x2068,
    0x2069,
    0x3164,
    0xFFA0,
}


def _tracked_files(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if result.returncode == 0:
        return [root / path.decode("utf-8") for path in result.stdout.split(b"\0") if path]

    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(root).parts
    )


def _is_dangerous_character(character: str, index: int) -> bool:
    codepoint = ord(character)
    if codepoint == 0xFEFF:
        return index != 0
    if codepoint in DANGEROUS_CODEPOINTS or 0xE0000 <= codepoint <= 0xE007F:
        return True
    return (codepoint < 32 and character not in "\t\n\r") or 0x7F <= codepoint <= 0x9F


def _line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _read_text(path: Path) -> str | None:
    try:
        content = path.read_bytes()
    except OSError:
        return None
    if b"\0" in content:
        return None
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _step_block(lines: list[str], uses_index: int) -> list[str]:
    uses_line = lines[uses_index]
    uses_indent = len(uses_line) - len(uses_line.lstrip())
    step_indent = uses_indent if uses_line.lstrip().startswith("-") else max(0, uses_indent - 2)
    end = len(lines)
    for index in range(uses_index + 1, len(lines)):
        line = lines[index]
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= step_indent and line.lstrip().startswith("-"):
            end = index
            break
    return lines[uses_index:end]


def validate_public_files(root: Path, paths: Iterable[Path] | None = None) -> list[str]:
    """Return dangerous Unicode, personal paths, and symlink findings in public files."""

    errors: list[str] = []
    candidates = list(paths) if paths is not None else _tracked_files(root)
    for path in candidates:
        try:
            relative = path.relative_to(root)
        except ValueError:
            relative = path

        # Do not follow repository symlinks while scanning public content. A symlink
        # can otherwise make a "repository" validator inspect arbitrary host files,
        # and release_smoke.py already treats links as invalid release payloads.
        if path.is_symlink():
            errors.append(f"{relative}: symbolic links are not allowed in public files")
            continue

        text = _read_text(path)
        if text is None:
            continue

        for index, character in enumerate(text):
            if _is_dangerous_character(character, index):
                errors.append(
                    f"{relative}:{_line_number(text, index)}: dangerous Unicode/control "
                    f"character U+{ord(character):04X}"
                )

        for pattern in (POSIX_HOME_PATH, WINDOWS_HOME_PATH):
            for match in pattern.finditer(text):
                if match.group(1).lower() not in SAFE_PLACEHOLDERS:
                    errors.append(
                        f"{relative}:{_line_number(text, match.start())}: personal home path "
                        "must not be published"
                    )
    return errors


def validate_workflows(root: Path) -> list[str]:
    """Return unsafe or mutable GitHub Actions workflow findings."""

    errors: list[str] = []
    workflow_root = root / ".github" / "workflows"
    if not workflow_root.is_dir():
        return errors

    for path in sorted([*workflow_root.glob("*.yml"), *workflow_root.glob("*.yaml")]):
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        has_sensitive_trigger = bool(re.search(r"(?m)^\s*(pull_request_target|workflow_run):", text))
        has_pull_request = bool(re.search(r"(?m)^\s*pull_request:\s*$", text))
        has_write_permission = bool(re.search(r"(?m)^\s*[a-z-]+:\s*write\s*(?:#.*)?$", text))

        if has_pull_request and has_write_permission:
            errors.append(f"{path.relative_to(root)}: pull_request workflow must not receive write permissions")

        for index, line in enumerate(lines):
            match = ACTION_REFERENCE.match(line)
            if match is None:
                continue
            reference = match.group(1)
            if reference.startswith(("./", "docker://")):
                continue
            if "@" not in reference:
                errors.append(f"{path.relative_to(root)}:{index + 1}: action reference has no immutable revision")
                continue
            action, revision = reference.rsplit("@", 1)
            if FULL_COMMIT_SHA.fullmatch(revision) is None:
                errors.append(
                    f"{path.relative_to(root)}:{index + 1}: {action} must be pinned to a full commit SHA"
                )
            if action == "actions/checkout":
                block = "\n".join(_step_block(lines, index))
                if re.search(r"(?m)^\s*persist-credentials:\s*false\s*(?:#.*)?$", block) is None:
                    errors.append(
                        f"{path.relative_to(root)}:{index + 1}: checkout must set persist-credentials: false"
                    )
                if has_sensitive_trigger:
                    errors.append(
                        f"{path.relative_to(root)}:{index + 1}: sensitive trigger must not check out untrusted code"
                    )

        shell_hazards = (
            (re.compile(r"(?:curl|wget)[^\n|]*\|\s*(?:ba)?sh\b"), "remote script is piped into a shell"),
            (re.compile(r"\bnpm\s+(?:ci|install)\b(?![^\n]*--ignore-scripts)"), "npm install must disable lifecycle scripts"),
        )
        for pattern, message in shell_hazards:
            for match in pattern.finditer(text):
                errors.append(
                    f"{path.relative_to(root)}:{_line_number(text, match.start())}: {message}"
                )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    root = args.root.resolve()

    errors = [*validate_public_files(root), *validate_workflows(root)]
    if errors:
        print(f"Repository security checks failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Repository security checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
