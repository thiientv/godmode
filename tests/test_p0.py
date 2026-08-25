import threading
import time
import unittest

from scripts.impact import analyze
from scripts.orchestrator import execute
from scripts.proof import build
from scripts.router import route


class P0Tests(unittest.TestCase):
    def test_router_expands_transitive_dependencies_and_detects_risk(self):
        result = route("security production deployment", limit=3)
        names = {item["skill"] for item in result["skills"]}
        self.assertEqual(result["risk"], "high")
        self.assertIn("codebase-orientation", names)
        self.assertIn("completion-verification", names)

    def test_parallel_orchestrator_runs_independent_nodes_concurrently(self):
        active = 0; peak = 0; lock = threading.Lock()
        def runner(node):
            nonlocal active, peak
            with lock:
                active += 1; peak = max(peak, active)
            time.sleep(0.03)
            with lock: active -= 1
            return True
        graph = {"nodes": [
            {"id": "a", "state": "pending"}, {"id": "b", "state": "pending"},
            {"id": "c", "state": "pending", "depends_on": ["a", "b"]},
        ]}
        result = execute(graph, runner, max_workers=2)
        self.assertEqual(result["completed"], ["a", "b", "c"])
        self.assertGreaterEqual(peak, 2)

    def test_proof_graph_marks_invalid_evidence(self):
        result = build({"state": "VERIFICATION", "risk": "high", "evidence": [{"kind": "review-result", "valid": True}, {"kind": "fresh-test-result", "valid": False}]})
        self.assertEqual(result["proof_count"], 1)
        self.assertFalse(result["proof_complete"])

    def test_impact_analysis_recommends_domain_skills(self):
        result = analyze(["src/auth/token.py", "db/migration.sql", "src/api/routes.py"])
        self.assertIn("security", result["impact_domains"])
        self.assertIn("database", result["impact_domains"])
        self.assertIn("security-and-hardening", result["recommended_skills"])
        self.assertIn("safe-migrations", result["recommended_skills"])


if __name__ == "__main__":
    unittest.main()
