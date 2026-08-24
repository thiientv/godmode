import unittest

from scripts.context_planner import ContextItem, plan
from scripts.lifecycle import can_transition
from scripts.orchestrator import Handoff, RetryPolicy, execute
from scripts.router import route


class P0OrchestrationCoreTests(unittest.TestCase):
    def test_router_expands_dependencies_and_reports_fallback(self):
        graph = {"skills": {
            "security-and-hardening": {"keywords": ["security"], "requires": ["codebase-orientation"]},
            "codebase-orientation": {"keywords": ["repository"], "requires": []},
        }}
        result = route("security", graph)
        self.assertEqual(result["skills"][-1]["skill"], "codebase-orientation")
        self.assertFalse(result["fallback_required"])
        self.assertTrue(route("zzzz", graph)["fallback_required"])

    def test_context_planner_keeps_required_items(self):
        result = plan([ContextItem("optional", 80), ContextItem("required", 120, required=True)], 100)
        self.assertIn("required", result["selected"])
        self.assertIn("optional", result["excluded"])
        self.assertTrue(result["required_over_budget"])

    def test_dag_executor_retries_transient_failure(self):
        calls = {"task": 0}
        def runner(node):
            calls["task"] += 1
            if calls["task"] == 1:
                error = RuntimeError("timeout")
                error.reason = "timeout"
                raise error
            return True
        result = execute({"nodes": [{"id": "task"}]}, runner, RetryPolicy(max_attempts=2))
        self.assertEqual(result["completed"], ["task"])
        self.assertEqual(result["attempts"]["task"], 2)

    def test_lifecycle_rejects_invalid_transition(self):
        record = {"state": "DISCOVERY", "risk": "medium", "completed": [], "evidence": [], "next_check": "verify", "limits": []}
        graph = {"transitions": {"DISCOVERY": ["DESIGN"]}, "minimum_evidence": {"DESIGN": ["design-decision"]}}
        allowed, reason = can_transition(record, "IMPLEMENTATION", graph)
        self.assertFalse(allowed)
        self.assertIn("not allowed", reason)

    def test_handoff_is_structured(self):
        handoff = Handoff("fix auth", completed=["reproduce"], next_action="implement")
        self.assertEqual(handoff.as_dict()["next_action"], "implement")


if __name__ == "__main__":
    unittest.main()
