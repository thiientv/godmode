import json
import tempfile
import unittest
from pathlib import Path

from scripts.evidence import create, invalidate
from scripts.events import emit, last, read
from scripts.risk import assess, impact
from scripts.skill_graph import load, recommend, validate
from scripts.task_state import init, load as load_state, recover, save
from scripts.lifecycle import can_transition, load_graph


class ExecutionSystemTests(unittest.TestCase):
    def test_task_state_round_trip_and_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = init(root, "ship feature", "high", "T-1")
            self.assertEqual(load_state(root)["task_id"], "T-1")
            self.assertEqual(recover(root)["source"], "task.json")
            state["state"] = "TESTING"
            save(root, state)
            self.assertEqual(load_state(root)["state"], "TESTING")

    def test_evidence_invalidates_when_scoped_file_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); path = root / "src.txt"; path.parent.mkdir(); path.write_text("a")
            evidence = create("claim", "test", "cat src.txt", "passed", root, ["src.txt"])
            path.write_text("b")
            changed, reason = invalidate(evidence, root)
            self.assertTrue(changed); self.assertIn("stale", reason); self.assertFalse(evidence["valid"])

    def test_events_are_append_only_and_readable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); emit(root, "task_started", task_id="T-1"); emit(root, "state_changed", current="TESTING")
            self.assertEqual(len(read(root)), 2); self.assertEqual(last(root)["type"], "state_changed")

    def test_risk_and_impact(self):
        result = assess(["src/auth/token.py", "db/migrations/001.sql"])
        self.assertIn(result["risk"], {"high", "critical"})
        self.assertIn("security-and-hardening", impact(["src/auth/token.py"])["suggested_skills"])

    def test_skill_graph(self):
        graph = load(); self.assertEqual(validate(graph), [])
        self.assertIn("implementation-planning", recommend(["solution-design"], graph))

    def test_medium_release_requires_evidence(self):
        graph = load_graph()
        record = {"state": "VERIFICATION", "risk": "medium", "completed": ["DISCOVERY", "IMPLEMENTATION", "TESTING", "VERIFICATION"], "evidence": [{"kind": "evidence-ledger"}], "next_check": "release", "limits": []}
        ok, message = can_transition(record, "RELEASE", graph)
        self.assertTrue(ok, message)

    def test_high_release_requires_review(self):
        graph = load_graph()
        record = {"state": "VERIFICATION", "risk": "high", "completed": ["DISCOVERY", "DESIGN", "PLANNING", "IMPLEMENTATION", "TESTING", "REVIEW", "VERIFICATION"], "evidence": [{"kind": "evidence-ledger"}], "next_check": "review", "limits": []}
        ok, message = can_transition(record, "RELEASE", graph)
        self.assertFalse(ok); self.assertIn("review-result", message)


if __name__ == "__main__": unittest.main()
