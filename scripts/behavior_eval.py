#!/usr/bin/env python3
"""Validate, initialize, and compare portable agent behavior-evaluation runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence


SCHEMA_VERSION = 1
CASE_STATUSES = {"pass", "fail", "blocked"}


def read_json(path: Path) -> object:
    """Read one JSON document."""

    return json.loads(path.read_text(encoding="utf-8"))


def validate_cases(payload: object) -> list[str]:
    """Validate a behavior case-set document."""

    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["case set must be an object"]
    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if not isinstance(payload.get("subject"), str) or not payload["subject"].strip():
        errors.append("subject must be a non-empty string")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        return errors + ["cases must be a non-empty list"]

    seen_case_ids: set[str] = set()
    for index, case in enumerate(cases):
        prefix = f"cases[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{prefix} must be an object")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"{prefix}.id must be a non-empty string")
        elif case_id in seen_case_ids:
            errors.append(f"{prefix}.id duplicates {case_id!r}")
        else:
            seen_case_ids.add(case_id)
        for field in ("prompt", "expected"):
            value = case.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{prefix}.{field} must be a non-empty string")
        assertions = case.get("assertions")
        if not isinstance(assertions, list) or not assertions:
            errors.append(f"{prefix}.assertions must be a non-empty list")
            continue
        seen_assertion_ids: set[str] = set()
        for assertion_index, assertion in enumerate(assertions):
            assertion_prefix = f"{prefix}.assertions[{assertion_index}]"
            if not isinstance(assertion, dict):
                errors.append(f"{assertion_prefix} must be an object")
                continue
            assertion_id = assertion.get("id")
            if not isinstance(assertion_id, str) or not assertion_id.strip():
                errors.append(f"{assertion_prefix}.id must be a non-empty string")
            elif assertion_id in seen_assertion_ids:
                errors.append(f"{assertion_prefix}.id duplicates {assertion_id!r}")
            else:
                seen_assertion_ids.add(assertion_id)
            if not isinstance(assertion.get("description"), str) or not assertion["description"].strip():
                errors.append(f"{assertion_prefix}.description must be a non-empty string")
            weight = assertion.get("weight", 1)
            if not isinstance(weight, (int, float)) or isinstance(weight, bool) or weight <= 0:
                errors.append(f"{assertion_prefix}.weight must be a positive number")
            required = assertion.get("required", False)
            if not isinstance(required, bool):
                errors.append(f"{assertion_prefix}.required must be boolean")
    return errors


def case_index(case_payload: dict[str, object]) -> dict[str, dict[str, object]]:
    """Index validated cases by identifier."""

    cases = case_payload["cases"]
    if not isinstance(cases, list):
        return {}
    return {
        str(case["id"]): case
        for case in cases
        if isinstance(case, dict) and isinstance(case.get("id"), str)
    }


def build_run_skeleton(case_payload: dict[str, object], variant: str) -> dict[str, object]:
    """Create an empty run record for a validated case set."""

    indexed = case_index(case_payload)
    results: list[dict[str, object]] = []
    for case_id, case in indexed.items():
        assertions = case.get("assertions")
        assertion_results: list[dict[str, object]] = []
        if isinstance(assertions, list):
            for assertion in assertions:
                if isinstance(assertion, dict) and isinstance(assertion.get("id"), str):
                    assertion_results.append({"id": assertion["id"], "passed": None, "evidence": ""})
        results.append(
            {
                "id": case_id,
                "status": "blocked",
                "assertions": assertion_results,
                "duration_ms": 0,
                "usage": {},
                "artifacts": [],
                "limitations": ["Run has not been executed."],
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "subject": case_payload["subject"],
        "variant": variant,
        "environment": {},
        "cases": results,
    }


def validate_run(payload: object, case_payload: dict[str, object]) -> list[str]:
    """Validate one result record against its case set."""

    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["run must be an object"]
    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if payload.get("subject") != case_payload.get("subject"):
        errors.append("run subject does not match case-set subject")
    if not isinstance(payload.get("variant"), str) or not payload["variant"].strip():
        errors.append("variant must be a non-empty string")
    if not isinstance(payload.get("environment"), dict):
        errors.append("environment must be an object")
    results = payload.get("cases")
    if not isinstance(results, list):
        return errors + ["run cases must be a list"]

    expected = case_index(case_payload)
    seen: set[str] = set()
    for index, result in enumerate(results):
        prefix = f"cases[{index}]"
        if not isinstance(result, dict):
            errors.append(f"{prefix} must be an object")
            continue
        case_id = result.get("id")
        if not isinstance(case_id, str) or case_id not in expected:
            errors.append(f"{prefix}.id must name a known case")
            continue
        if case_id in seen:
            errors.append(f"{prefix}.id duplicates {case_id!r}")
        seen.add(case_id)
        if result.get("status") not in CASE_STATUSES:
            errors.append(f"{prefix}.status must be pass, fail, or blocked")
        duration = result.get("duration_ms")
        if not isinstance(duration, int) or isinstance(duration, bool) or duration < 0:
            errors.append(f"{prefix}.duration_ms must be a non-negative integer")
        if not isinstance(result.get("usage"), dict):
            errors.append(f"{prefix}.usage must be an object")
        artifacts = result.get("artifacts")
        if not isinstance(artifacts, list) or not all(isinstance(item, str) and item.strip() for item in artifacts):
            errors.append(f"{prefix}.artifacts must be a list of non-empty strings")
        limitations = result.get("limitations")
        if not isinstance(limitations, list) or not all(isinstance(item, str) and item.strip() for item in limitations):
            errors.append(f"{prefix}.limitations must be a list of non-empty strings")

        expected_assertions = expected[case_id].get("assertions")
        assertion_ids: set[str] = set()
        if isinstance(expected_assertions, list):
            assertion_ids = {
                assertion["id"]
                for assertion in expected_assertions
                if isinstance(assertion, dict) and isinstance(assertion.get("id"), str)
            }
        actual_assertions = result.get("assertions")
        if not isinstance(actual_assertions, list):
            errors.append(f"{prefix}.assertions must be a list")
            continue
        actual_ids: set[str] = set()
        assertion_outcomes: list[bool | None] = []
        for assertion_index, assertion in enumerate(actual_assertions):
            assertion_prefix = f"{prefix}.assertions[{assertion_index}]"
            if not isinstance(assertion, dict) or assertion.get("id") not in assertion_ids:
                errors.append(f"{assertion_prefix}.id must name a known assertion")
                continue
            assertion_id = str(assertion["id"])
            if assertion_id in actual_ids:
                errors.append(f"{assertion_prefix}.id duplicates {assertion_id!r}")
            actual_ids.add(assertion_id)
            passed = assertion.get("passed")
            if passed is not True and passed is not False and passed is not None:
                errors.append(f"{assertion_prefix}.passed must be boolean or null")
            else:
                assertion_outcomes.append(passed)
            evidence = assertion.get("evidence")
            if not isinstance(evidence, str):
                errors.append(f"{assertion_prefix}.evidence must be a string")
            elif passed is not None and not evidence.strip():
                errors.append(f"{assertion_prefix}.evidence must be non-empty for a resolved assertion")
        if actual_ids != assertion_ids:
            errors.append(f"{prefix}.assertions must cover every declared assertion exactly once")
        status = result.get("status")
        if status == "pass" and (not assertion_outcomes or any(outcome is not True for outcome in assertion_outcomes)):
            errors.append(f"{prefix}.status pass requires every assertion to pass")
        if status == "fail" and False not in assertion_outcomes:
            errors.append(f"{prefix}.status fail requires at least one failed assertion")
        has_limitations = isinstance(limitations, list) and bool(limitations)
        if status == "blocked" and None not in assertion_outcomes and not has_limitations:
            errors.append(f"{prefix}.status blocked requires an unresolved assertion or limitation")
    if seen != set(expected):
        errors.append("run must contain every declared case exactly once")
    return errors


class CounterStatus:
    """Small stable status counter without external dependencies."""

    def __init__(self, passed: int, failed: int, blocked: int) -> None:
        self.passed = passed
        self.failed = failed
        self.blocked = blocked

    @classmethod
    def from_results(cls, results: list[object]) -> "CounterStatus":
        counts = {"pass": 0, "fail": 0, "blocked": 0}
        for result in results:
            if isinstance(result, dict) and result.get("status") in counts:
                status = str(result["status"])
                counts[status] += 1
        return cls(counts["pass"], counts["fail"], counts["blocked"])

    def as_dict(self) -> dict[str, int]:
        return {"pass": self.passed, "fail": self.failed, "blocked": self.blocked}


def summarize_run(payload: dict[str, object], case_payload: dict[str, object]) -> dict[str, object]:
    """Compute transparent pass and weighted assertion statistics."""

    expected = case_index(case_payload)
    results = payload.get("cases")
    if not isinstance(results, list):
        results = []
    statuses = CounterStatus.from_results(results)
    earned = 0.0
    possible = 0.0
    required_failures: list[str] = []
    required_unresolved: list[str] = []
    duration_ms = 0

    for result in results:
        if not isinstance(result, dict) or not isinstance(result.get("id"), str):
            continue
        case_id = result["id"]
        duration = result.get("duration_ms")
        if isinstance(duration, int) and not isinstance(duration, bool):
            duration_ms += duration
        actual = result.get("assertions")
        actual_map: dict[str, object] = {}
        if isinstance(actual, list):
            actual_map = {
                str(item["id"]): item.get("passed")
                for item in actual
                if isinstance(item, dict) and isinstance(item.get("id"), str)
            }
        declared = expected[case_id].get("assertions")
        if not isinstance(declared, list):
            continue
        for assertion in declared:
            if not isinstance(assertion, dict) or not isinstance(assertion.get("id"), str):
                continue
            weight = float(assertion.get("weight", 1))
            possible += weight
            outcome = actual_map.get(assertion["id"])
            if outcome is True:
                earned += weight
            elif outcome is False and assertion.get("required") is True:
                required_failures.append(f"{case_id}:{assertion['id']}")
            elif outcome is None and assertion.get("required") is True:
                required_unresolved.append(f"{case_id}:{assertion['id']}")

    return {
        "variant": payload.get("variant"),
        "case_statuses": statuses.as_dict(),
        "weighted_score": earned / possible if possible else 0.0,
        "required_failures": required_failures,
        "required_unresolved": required_unresolved,
        "duration_ms": duration_ms,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate a case set and optional run")
    validate_parser.add_argument("cases", type=Path)
    validate_parser.add_argument("--run", type=Path)

    init_parser = subparsers.add_parser("init-run", help="create an empty run record")
    init_parser.add_argument("cases", type=Path)
    init_parser.add_argument("output", type=Path)
    init_parser.add_argument("--variant", required=True)

    compare_parser = subparsers.add_parser("compare", help="compare baseline and candidate run records")
    compare_parser.add_argument("cases", type=Path)
    compare_parser.add_argument("baseline", type=Path)
    compare_parser.add_argument("candidate", type=Path)
    return parser.parse_args(argv)


def checked_case_payload(path: Path) -> dict[str, object]:
    """Load a valid case set or exit with actionable errors."""

    payload = read_json(path)
    errors = validate_cases(payload)
    if errors:
        raise SystemExit("\n".join(f"- {error}" for error in errors))
    if not isinstance(payload, dict):
        raise SystemExit("case set must be an object")
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    """Run behavior-evaluation tooling."""

    args = parse_args(argv)
    case_payload = checked_case_payload(args.cases)
    if args.command == "validate":
        errors: list[str] = []
        if args.run is not None:
            errors = validate_run(read_json(args.run), case_payload)
        if errors:
            print("Validation failed:")
            for error in errors:
                print(f"- {error}")
            return 1
        print(f"Validated {len(case_index(case_payload))} behavior case(s).")
        return 0

    if args.command == "init-run":
        args.output.parent.mkdir(parents=True, exist_ok=True)
        skeleton = build_run_skeleton(case_payload, args.variant)
        args.output.write_text(json.dumps(skeleton, indent=2) + "\n", encoding="utf-8")
        print(f"Created run skeleton: {args.output}")
        return 0

    baseline_payload = read_json(args.baseline)
    candidate_payload = read_json(args.candidate)
    errors = [
        *(f"baseline: {error}" for error in validate_run(baseline_payload, case_payload)),
        *(f"candidate: {error}" for error in validate_run(candidate_payload, case_payload)),
    ]
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    if not isinstance(baseline_payload, dict) or not isinstance(candidate_payload, dict):
        return 1
    report = {
        "subject": case_payload["subject"],
        "baseline": summarize_run(baseline_payload, case_payload),
        "candidate": summarize_run(candidate_payload, case_payload),
    }
    baseline_score = report["baseline"]["weighted_score"]
    candidate_score = report["candidate"]["weighted_score"]
    report["weighted_score_delta"] = candidate_score - baseline_score
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
