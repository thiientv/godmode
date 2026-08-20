import json
import tempfile
import unittest
from pathlib import Path

from scripts.behavior_grader import grade
from scripts.routing_eval import evaluate, ratchet, summarize, validate_cases
from scripts.gate import gate


class P0QualityLoopTests(unittest.TestCase):
    def test_deterministic_grader_checks_files_and_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "result.txt").write_text("verified migration\n", encoding="utf-8")
            case = {"id": "migration", "assertions": [
                {"id": "exists", "required": True, "check": {"type": "file_exists", "path": "result.txt"}},
                {"id": "proof", "required": True, "check": {"type": "text_contains", "path": "result.txt", "value": "verified"}},
            ]}
            result = grade(case, root)
            self.assertEqual(result["status"], "pass")
            self.assertTrue(all(item["passed"] for item in result["assertions"]))

    def test_grader_blocks_manual_assertions_instead_of_faking_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = grade({"id": "manual", "assertions": [{"id": "review", "required": True}]}, Path(tmp))
            self.assertEqual(result["status"], "blocked")

    def test_routing_rank_and_forbidden_skill(self):
        case = {"id": "auth", "expected": ["security-and-hardening"], "acceptable": [], "forbidden": ["frontend-design"]}
        result = evaluate(case, {"id": "auth", "skills": ["security-and-hardening", "frontend-design"]})
        self.assertTrue(result["rank1"])
        self.assertTrue(result["forbidden"])
        self.assertEqual(result["status"], "fail")

    def test_routing_ratchet_rejects_regression(self):
        baseline = {"rank1_accuracy": 1.0, "top3_accuracy": 1.0, "forbidden_rate": 0.0}
        candidate = {"rank1_accuracy": 0.9, "top3_accuracy": 1.0, "forbidden_rate": 0.0}
        self.assertFalse(ratchet(baseline, candidate)["passed"])

    def test_routing_cases_validate_and_summarize(self):
        cases = {"schema_version": 1, "cases": [{"id": "one", "prompt": "x", "expected": ["a"], "acceptable": [], "forbidden": []}]}
        self.assertEqual(validate_cases(cases), [])
        summary = summarize(cases, {"cases": [{"id": "one", "skills": ["a"]}]})
        self.assertEqual(summary["rank1_accuracy"], 1.0)

    def test_done_gate_requires_fresh_evidence(self):
        record = {"state": "DONE", "evidence": [{"kind": "evidence-ledger", "valid": False}], "limits": []}
        result = gate(record, "DONE")
        self.assertFalse(result["passed"])
        self.assertIn("evidence-ledger", result["missing"])

    def test_done_gate_accepts_fresh_evidence(self):
        record = {"state": "DONE", "evidence": [{"kind": "evidence-ledger", "valid": True}], "limits": []}
        self.assertTrue(gate(record, "DONE")["passed"])


if __name__ == "__main__":
    unittest.main()
