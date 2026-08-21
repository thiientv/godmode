import json
import tempfile
import unittest
from pathlib import Path

from scripts.router import route
from scripts.execution_graph import validate
from scripts.report import report
from scripts.verification import verify

class P0ControlPlaneTests(unittest.TestCase):
    def test_router_is_explainable_and_resolves_dependencies(self):
        graph={"skills":{"security-and-hardening":{"keywords":["security","hardening"],"requires":["codebase-orientation"]},"codebase-orientation":{"keywords":["codebase"],"requires":[]}}}
        result=route("harden security",graph)
        self.assertTrue(result["explainable"])
        self.assertEqual(result["skills"][0]["skill"],"security-and-hardening")
        self.assertEqual(result["required_dependencies"],["codebase-orientation"])

    def test_execution_graph_finds_ready_nodes(self):
        result=validate({"nodes":[{"id":"plan","state":"completed"},{"id":"test","state":"pending","depends_on":["plan"]}]})
        self.assertTrue(result["valid"])
        self.assertEqual(result["ready"],["test"])

    def test_execution_graph_rejects_cycles(self):
        result=validate({"nodes":[{"id":"a","depends_on":["b"]},{"id":"b","depends_on":["a"]}]})
        self.assertFalse(result["valid"])
        self.assertTrue(any("cycle" in e for e in result["errors"]))

    def test_verification_runner(self):
        result=verify(["python3 -c 'print(\"ok\")'"],Path("."))
        self.assertTrue(result["passed"])

    def test_report_contains_usage_and_skills(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"run.json"
            path.write_text(json.dumps({"run_id":"r1","adapter":"test","model":"m","task_id":"t1","started_at":"now","events":[{"type":"done","skill":"testing"}],"usage":{"input_tokens":10,"output_tokens":5},"skills":["testing"],"final_message":"done"}),encoding="utf-8")
            text=report(path)
            self.assertIn("r1",text); self.assertIn("testing",text); self.assertIn("10 in / 5 out",text)

if __name__ == "__main__": unittest.main()
