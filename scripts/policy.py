#!/usr/bin/env python3
"""Risk-aware policy checks for autonomous and human-approved execution."""
from __future__ import annotations

POLICIES = {
    "low": {"human_approval": [], "blocked_actions": []},
    "medium": {"human_approval": ["RELEASE"], "blocked_actions": []},
    "high": {"human_approval": ["RELEASE"], "blocked_actions": ["destructive-production-change"]},
    "critical": {"human_approval": ["IMPLEMENTATION", "RELEASE"], "blocked_actions": ["destructive-production-change", "irreversible-migration"]},
}

def policy_for(risk: str) -> dict:
    if risk not in POLICIES: raise ValueError(f"unknown risk: {risk}")
    return POLICIES[risk]

def requires_approval(risk: str, action: str) -> bool:
    return action in policy_for(risk)["human_approval"]

def check_action(risk: str, action: str, approved: bool = False, requested_action: str | None = None) -> tuple[bool, str]:
    policy = policy_for(risk)
    if requested_action and requested_action in policy["blocked_actions"]:
        return False, f"action {requested_action} is blocked for {risk}-risk tasks"
    if requires_approval(risk, action) and not approved:
        return False, f"human approval required before {action} for {risk}-risk tasks"
    return True, "ok"

def evaluate(record: dict, action: str, approved: bool = False) -> dict:
    risk = str(record.get("risk", "medium")); ok, reason = check_action(risk, action, approved)
    return {"allowed": ok, "risk": risk, "action": action, "approval_required": requires_approval(risk, action), "approved": approved, "reason": reason}
