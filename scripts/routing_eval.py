#!/usr/bin/env python3
"""Deterministic routing regression checks for native agent traces."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_cases(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["routing case set must be an object"]
    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        return errors + ["cases must be a non-empty list"]
    seen: set[str] = set()
    for i, case in enumerate(cases):
        p = f"cases[{i}]"
        if not isinstance(case, dict):
            errors.append(f"{p} must be an object")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"{p}.id must be a non-empty string")
        elif case_id in seen:
            errors.append(f"{p}.id duplicates {case_id!r}")
        else:
            seen.add(case_id)
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            errors.append(f"{p}.prompt must be a non-empty string")
        for field in ("expected", "acceptable", "forbidden"):
            value = case.get(field, [])
            if not isinstance(value, list) or not all(isinstance(x, str) and x.strip() for x in value):
                errors.append(f"{p}.{field} must be a list of non-empty strings")
        if not case.get("expected"):
            errors.append(f"{p}.expected must contain at least one skill")
    return errors


def validate_trace(payload: Any, cases: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["routing trace must be an object"]
    results = payload.get("cases")
    if not isinstance(results, list):
        return ["routing trace cases must be a list"]
    seen: set[str] = set()
    for i, result in enumerate(results):
        p = f"cases[{i}]"
        if not isinstance(result, dict):
            errors.append(f"{p} must be an object")
            continue
        case_id = result.get("id")
        if not isinstance(case_id, str) or case_id not in cases:
            errors.append(f"{p}.id must name a known case")
            continue
        seen.add(case_id)
        skills = result.get("skills")
        if not isinstance(skills, list) or not all(isinstance(x, str) and x.strip() for x in skills):
            errors.append(f"{p}.skills must be a list of non-empty strings")
    if seen != set(cases):
        errors.append("routing trace must contain every declared case exactly once")
    return errors


def evaluate(case: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    skills = [str(x) for x in result.get("skills", [])]
    expected = [str(x) for x in case["expected"]]
    acceptable = set(str(x) for x in case.get("acceptable", []))
    forbidden = set(str(x) for x in case.get("forbidden", []))
    top = skills[:1]
    top3 = set(skills[:3])
    rank1 = bool(top and top[0] in expected)
    top3_hit = any(skill in expected or skill in acceptable for skill in top3)
    forbidden_hit = sorted(set(skills) & forbidden)
    return {
        "id": case["id"],
        "rank1": rank1,
        "top3": top3_hit,
        "forbidden": forbidden_hit,
        "selected": skills,
        "status": "fail" if forbidden_hit else ("pass" if rank1 else "fail"),
    }


def summarize(case_payload: dict[str, Any], trace_payload: dict[str, Any]) -> dict[str, Any]:
    indexed = {str(c["id"]): c for c in case_payload["cases"]}
    results = [evaluate(indexed[r["id"]], r) for r in trace_payload["cases"]]
    total = len(results)
    rank1 = sum(bool(r["rank1"]) for r in results)
    top3 = sum(bool(r["top3"]) for r in results)
    forbidden = sum(bool(r["forbidden"]) for r in results)
    return {
        "cases": results,
        "total": total,
        "rank1_accuracy": rank1 / total if total else 0.0,
        "top3_accuracy": top3 / total if total else 0.0,
        "forbidden_rate": forbidden / total if total else 0.0,
    }


def ratchet(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "rank1_not_regressed": candidate["rank1_accuracy"] >= baseline["rank1_accuracy"],
        "top3_not_regressed": candidate["top3_accuracy"] >= baseline["top3_accuracy"],
        "forbidden_not_regressed": candidate["forbidden_rate"] <= baseline["forbidden_rate"],
    }
    return {"checks": checks, "passed": all(checks.values())}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("cases", type=Path)
    run = sub.add_parser("evaluate")
    run.add_argument("cases", type=Path)
    run.add_argument("trace", type=Path)
    run.add_argument("output", type=Path, nargs="?")
    compare = sub.add_parser("ratchet")
    compare.add_argument("baseline", type=Path)
    compare.add_argument("candidate", type=Path)
    args = parser.parse_args()

    if args.command == "validate":
        errors = validate_cases(load_json(args.cases))
        if errors:
            print("Validation failed:\n" + "\n".join(f"- {e}" for e in errors))
            return 1
        print("Routing cases are valid.")
        return 0

    if args.command == "evaluate":
        cases = load_json(args.cases)
        trace = load_json(args.trace)
        errors = validate_cases(cases)
        indexed = {str(c["id"]): c for c in cases.get("cases", [])} if isinstance(cases, dict) else {}
        errors.extend(validate_trace(trace, indexed))
        if errors:
            print("Validation failed:\n" + "\n".join(f"- {e}" for e in errors))
            return 1
        summary = summarize(cases, trace)
        text = json.dumps(summary, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text, encoding="utf-8")
        print(text, end="")
        return 0

    baseline = load_json(args.baseline)
    candidate = load_json(args.candidate)
    result = ratchet(baseline, candidate)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
