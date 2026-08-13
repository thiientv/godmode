from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from behavior_eval import (  # noqa: E402
    build_run_skeleton,
    summarize_run,
    validate_cases,
    validate_run,
)


class BehaviorEvalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case_payload = {
            "schema_version": 1,
            "subject": "sample",
            "cases": [
                {
                    "id": "one",
                    "prompt": "Do the task.",
                    "expected": "A verified result.",
                    "assertions": [
                        {"id": "required", "description": "Required proof.", "required": True, "weight": 2},
                        {"id": "quality", "description": "Quality proof."},
                    ],
                }
            ],
        }

    def test_repository_behavior_cases_are_valid(self) -> None:
        payload = json.loads((ROOT / "evals" / "behavior" / "core-workflows.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_cases(payload), [])

    def test_run_skeleton_is_valid_and_blocked(self) -> None:
        skeleton = build_run_skeleton(self.case_payload, "baseline")
        self.assertEqual(validate_run(skeleton, self.case_payload), [])
        self.assertEqual(skeleton["cases"][0]["status"], "blocked")

    def test_summary_preserves_required_failures_and_weight(self) -> None:
        run = build_run_skeleton(self.case_payload, "candidate")
        run["cases"][0].update(
            {
                "status": "fail",
                "duration_ms": 125,
                "assertions": [
                    {"id": "required", "passed": False, "evidence": "missing"},
                    {"id": "quality", "passed": True, "evidence": "artifact"},
                ],
            }
        )
        summary = summarize_run(run, self.case_payload)
        self.assertEqual(summary["weighted_score"], 1 / 3)
        self.assertEqual(summary["required_failures"], ["one:required"])
        self.assertEqual(summary["required_unresolved"], [])
        self.assertEqual(summary["duration_ms"], 125)

    def test_summary_separates_blocked_assertions_from_failures(self) -> None:
        run = build_run_skeleton(self.case_payload, "candidate")
        summary = summarize_run(run, self.case_payload)
        self.assertEqual(summary["required_failures"], [])
        self.assertEqual(summary["required_unresolved"], ["one:required"])

    def test_run_rejects_missing_provenance_and_inconsistent_status(self) -> None:
        run = build_run_skeleton(self.case_payload, "candidate")
        del run["environment"]
        result = run["cases"][0]
        result["status"] = "pass"
        result["usage"] = []
        result["artifacts"] = [""]
        result["limitations"] = "none"
        result["assertions"] = [
            {"id": "required", "passed": True, "evidence": ""},
            {"id": "quality", "passed": False, "evidence": "failure.txt"},
        ]
        errors = validate_run(run, self.case_payload)
        self.assertTrue(any("environment must be an object" in error for error in errors))
        self.assertTrue(any("usage must be an object" in error for error in errors))
        self.assertTrue(any("artifacts must be a list" in error for error in errors))
        self.assertTrue(any("limitations must be a list" in error for error in errors))
        self.assertTrue(any("evidence must be non-empty" in error for error in errors))
        self.assertTrue(any("status pass requires every assertion" in error for error in errors))

    def test_cli_skeleton_can_be_serialized(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "run.json"
            path.write_text(json.dumps(build_run_skeleton(self.case_payload, "baseline")), encoding="utf-8")
            self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)


if __name__ == "__main__":
    unittest.main()
