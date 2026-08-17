import unittest

from scripts.lifecycle import can_transition, load_graph, validate_graph, validate_state_record


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.graph = load_graph()

    def record(self, state="IMPLEMENTATION", risk="medium", completed=None, evidence=None):
        return {
            "state": state,
            "risk": risk,
            "completed": completed or ["DISCOVERY", "IMPLEMENTATION"],
            "evidence": evidence or [{"kind": "fresh-test-result", "result": "passed"}],
            "next_check": "run focused regression",
            "limits": [],
        }

    def test_graph_schema_is_valid(self):
        self.assertEqual(validate_graph(self.graph), [])

    def test_valid_record(self):
        self.assertEqual(validate_state_record(self.record(), self.graph), [])

    def test_invalid_state_is_rejected(self):
        errors = validate_state_record(self.record(state="UNKNOWN"), self.graph)
        self.assertTrue(any("state must be" in error for error in errors))

    def test_implementation_can_move_to_testing(self):
        ok, message = can_transition(self.record(), "TESTING", self.graph)
        self.assertTrue(ok, message)

    def test_illegal_transition_is_rejected(self):
        ok, message = can_transition(self.record(), "RELEASE", self.graph)
        self.assertFalse(ok)
        self.assertIn("not allowed", message)

    def test_non_low_verification_requires_fresh_test_evidence(self):
        record = self.record(evidence=[])
        ok, message = can_transition(record, "TESTING", self.graph)
        self.assertTrue(ok, message)
        record["state"] = "TESTING"
        record["completed"] = ["DISCOVERY", "IMPLEMENTATION", "TESTING"]

        ok, message = can_transition(record, "VERIFICATION", self.graph)
        self.assertFalse(ok)
        self.assertIn("fresh-test-result", message)

    def test_done_requires_evidence_ledger(self):
        record = self.record(
            state="DONE",
            risk="low",
            completed=["DISCOVERY", "VERIFICATION"],
            evidence=[],
        )
        errors = validate_state_record(record, self.graph)
        self.assertTrue(any("evidence-ledger" in error for error in errors))

    def test_high_risk_done_requires_design_and_review(self):
        record = self.record(
            state="DONE",
            risk="high",
            completed=["DISCOVERY", "PLANNING", "IMPLEMENTATION", "TESTING", "VERIFICATION"],
            evidence=[{"kind": "evidence-ledger"}],
        )
        errors = validate_state_record(record, self.graph)
        self.assertTrue(any("DESIGN" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
