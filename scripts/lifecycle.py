#!/usr/bin/env python3
"""Validate and inspect Godmode's risk-aware engineering lifecycle."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "lifecycle.json"


def load_graph(path: Path = GRAPH_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_graph(payload)
    if errors: raise ValueError("; ".join(errors))
    return payload


def validate_graph(graph: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    states, risks = graph.get("states"), graph.get("risk_levels")
    transitions, minimum_evidence = graph.get("transitions"), graph.get("minimum_evidence")
    risk_requirements, release_policy = graph.get("risk_requirements"), graph.get("release_policy")
    if graph.get("schema_version") not in {1, 2}: errors.append("schema_version must be 1 or 2")
    if not isinstance(states, list) or not states or not all(isinstance(x, str) and x for x in states): return errors + ["states must be a non-empty string list"]
    state_set = set(states)
    if len(state_set) != len(states): errors.append("states must not contain duplicates")
    if not isinstance(risks, list) or set(risks) != {"low", "medium", "high", "critical"}: errors.append("risk_levels must contain low, medium, high, critical")
    if not isinstance(transitions, dict) or set(transitions) != state_set: errors.append("transitions must define every state exactly once")
    else:
        for state, targets in transitions.items():
            if not isinstance(targets, list) or not all(target in state_set for target in targets): errors.append(f"transitions[{state}] contains an unknown target")
    if not isinstance(minimum_evidence, dict) or set(minimum_evidence) != state_set: errors.append("minimum_evidence must define every state exactly once")
    if not isinstance(risk_requirements, dict) or set(risk_requirements) != {"low", "medium", "high", "critical"}: errors.append("risk_requirements must define every risk exactly once")
    else:
        for risk, requirement in risk_requirements.items():
            required = requirement.get("required_states") if isinstance(requirement, dict) else None
            if not isinstance(required, list) or not all(state in state_set for state in required): errors.append(f"risk_requirements[{risk}].required_states contains an unknown state")
    if not isinstance(release_policy, dict) or set(release_policy) != {"low", "medium", "high", "critical"}: errors.append("release_policy must define every risk exactly once")
    return errors


def validate_state_record(record: dict[str, Any], graph: dict[str, Any] | None = None) -> list[str]:
    graph = graph or load_graph(); errors: list[str] = []
    states, risks = set(graph["states"]), set(graph["risk_levels"])
    state, risk = record.get("state"), record.get("risk")
    completed, evidence = record.get("completed", []), record.get("evidence", [])
    if state not in states: errors.append(f"state must be one of {sorted(states)}")
    if risk not in risks: errors.append(f"risk must be one of {sorted(risks)}")
    if not isinstance(completed, list) or not all(item in states for item in completed): errors.append("completed must be a list of known states")
    if not isinstance(evidence, list) or not all(isinstance(item, dict) for item in evidence): errors.append("evidence must be a list of objects")
    if not isinstance(record.get("next_check"), str) or not record["next_check"].strip(): errors.append("next_check must be a non-empty string")
    if not isinstance(record.get("limits", []), list) or not all(isinstance(x, str) and x.strip() for x in record.get("limits", [])): errors.append("limits must be a list of non-empty strings")
    if errors: return errors
    if state == "DONE" and not _has_evidence(evidence, "evidence-ledger"): errors.append("DONE requires evidence-ledger evidence")
    required = graph["risk_requirements"][risk]["required_states"]; missing = [x for x in required if x not in set(completed)]
    if state == "DONE" and missing: errors.append(f"risk {risk} cannot reach DONE without states: {', '.join(missing)}")
    return errors


def _has_evidence(evidence: list[dict[str, Any]], kind: str) -> bool:
    return any(item.get("kind") == kind and item.get("valid", True) is not False for item in evidence)


def can_transition(record: dict[str, Any], target: str, graph: dict[str, Any] | None = None) -> tuple[bool, str]:
    graph = graph or load_graph(); errors = validate_state_record(record, graph)
    if errors: return False, "; ".join(errors)
    current, risk = record["state"], record["risk"]
    if target not in graph["transitions"].get(current, []): return False, f"transition {current} -> {target} is not allowed"
    if target == "VERIFICATION" and risk != "low" and not _has_evidence(record["evidence"], "fresh-test-result"): return False, "non-low-risk verification requires fresh-test-result evidence"
    if target == "RELEASE":
        policy = graph["release_policy"][risk]
        if not policy.get("allowed"): return False, f"release is not required for {risk}-risk tasks"
        missing = [kind for kind in policy.get("required_evidence", []) if not _has_evidence(record["evidence"], kind)]
        if missing: return False, f"release requires evidence: {', '.join(missing)}"
    return True, "ok"


def recover_state(root: Path) -> dict[str, Any]:
    task = root / ".godmode" / "task.json"
    if task.is_file():
        return {"source": ".godmode/task.json", "state": json.loads(task.read_text(encoding="utf-8")), "limits": []}
    sources = [str(root / name) for name in ("plan.md", "implementation-plan.md", "PLAN.md", "evidence.json", "evidence-ledger.json") if (root / name).is_file()]
    return {"source": "repository-artifacts", "sources": sources, "next_check": "inspect durable artifacts and run the smallest fresh verification", "limits": ["state is inferred from repository artifacts; conversational history was not used"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("state_file", type=Path); parser.add_argument("--target"); args = parser.parse_args()
    record = json.loads(args.state_file.read_text(encoding="utf-8"))
    if not isinstance(record, dict): raise SystemExit("state file must contain a JSON object")
    errors = validate_state_record(record)
    if errors:
        for error in errors: print(f"error: {error}")
        return 1
    if args.target:
        ok, message = can_transition(record, args.target); print(message); return 0 if ok else 1
    print("valid lifecycle state record"); return 0

if __name__ == "__main__": raise SystemExit(main())
