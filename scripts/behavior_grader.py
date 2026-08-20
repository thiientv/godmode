#!/usr/bin/env python3
"""Deterministic artifact assertions for behavior-evaluation runs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

CHECKS = {"file_exists", "file_absent", "text_contains", "text_absent", "json_equals"}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def check(workspace: Path, spec: dict[str, Any]) -> tuple[bool, str]:
    kind = spec.get("type")
    path_value = spec.get("path", "")
    path = workspace / str(path_value)
    if kind not in CHECKS:
        return False, f"unsupported deterministic check: {kind}"
    if kind == "file_exists":
        return path.is_file(), str(path_value)
    if kind == "file_absent":
        return not path.exists(), str(path_value)
    if not path.is_file():
        return False, f"file not found: {path_value}"
    text = path.read_text(encoding="utf-8")
    if kind == "text_contains":
        needle = str(spec.get("value", ""))
        return needle in text, f"{path_value} contains expected text"
    if kind == "text_absent":
        needle = str(spec.get("value", ""))
        return needle not in text, f"{path_value} excludes forbidden text"
    try:
        actual = json.loads(text)
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON in {path_value}: {exc.msg}"
    return actual == spec.get("value"), f"{path_value} equals expected JSON"


def grade(case: dict[str, Any], workspace: Path) -> dict[str, Any]:
    assertions = []
    for assertion in case.get("assertions", []):
        if not isinstance(assertion, dict):
            continue
        spec = assertion.get("check")
        if not isinstance(spec, dict):
            assertions.append({"id": assertion.get("id"), "passed": None, "evidence": "manual assertion"})
            continue
        passed, evidence = check(workspace, spec)
        assertions.append({"id": assertion.get("id"), "passed": passed, "evidence": evidence})
    required_failed = any(
        not item["passed"]
        for item, declaration in zip(assertions, case.get("assertions", []))
        if isinstance(declaration, dict) and declaration.get("required") is True and item["passed"] is False
    )
    unresolved = any(item["passed"] is None for item in assertions)
    status = "fail" if required_failed else ("blocked" if unresolved else "pass")
    return {"id": case.get("id"), "status": status, "assertions": assertions}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    case = load(args.case)
    if not isinstance(case, dict):
        print("case must be an object")
        return 1
    result = grade(case, args.workspace)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
