import tempfile
import unittest
from pathlib import Path

from scripts.evidence import create
from scripts.lifecycle import transition
from scripts.orchestrator import execute
from scripts.policy import evaluate
from scripts.router import route


class P0HardeningTests(unittest.TestCase):
    def test_lifecycle_transition_rejects_bypass(self):
        record = {"state": "DISCOVERY", "risk": "medium", "completed": [], "evidence": [], "next_check": "design", "limits": []}
        with self.assertRaises(ValueError):
            transition(record, "DONE")

    def test_scheduler_serializes_conflicting_resources(self):
        graph = {"nodes": [
            {"id": "a", "resources": {"files": ["auth.py"]}},
            {"id": "b", "resources": {"files": ["auth.py"]}},
        ]}
        result = execute(graph, lambda node: True, max_workers=2)
        self.assertEqual(result["completed"], ["a", "b"])
        starts = [e["node"] for e in result["events"] if e["event"] == "started"]
        self.assertEqual(starts, ["a", "b"])

    def test_router_uses_changed_file_context(self):
        result = route("change the endpoint", context={"changed_files": ["src/auth/token.py", "src/api/routes.py"]})
        names = {item["skill"] for item in result["skills"]}
        self.assertIn("security-and-hardening", names)
        self.assertIn("api-and-interface-design", names)
        self.assertEqual(result["risk"], "high")

    def test_policy_requires_approval_for_critical_release(self):
        record = {"risk": "critical"}
        self.assertFalse(evaluate(record, "RELEASE")["allowed"])
        self.assertTrue(evaluate(record, "RELEASE", approved=True)["allowed"])

    def test_evidence_records_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.txt").write_text("ok", encoding="utf-8")
            evidence = create("sample passed", "test", "cat sample.txt", "passed", root, ["sample.txt"])
            self.assertIn("provenance", evidence)
            self.assertEqual(evidence["provenance"]["files"], ["sample.txt"])
            self.assertEqual(evidence["scope"]["digest"], evidence["provenance"]["file_digest"])


if __name__ == "__main__":
    unittest.main()
