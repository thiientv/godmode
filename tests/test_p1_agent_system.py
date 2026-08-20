import json
import tempfile
import unittest
from pathlib import Path

from scripts.agent_runs import normalize_run
from scripts.feedback import failure_to_case
from scripts.recovery import recover_context
from scripts.skill_composition import compose


class P1AgentSystemTests(unittest.TestCase):
    def test_normalized_run_preserves_provenance_and_skills(self):
        run = normalize_run({
            "adapter": "codex",
            "model": "gpt-5",
            "run_id": "R1",
            "task_id": "T1",
            "events": [
                {"type": "skill_activated", "skill": "security-and-hardening"},
                {"type": "tool_call", "tool": "shell"},
            ],
            "usage": {"input_tokens": 10, "output_tokens": 20},
        })
        self.assertEqual(run["adapter"], "codex")
        self.assertEqual(run["skills"], ["security-and-hardening"])
        self.assertEqual(run["usage"]["output_tokens"], 20)

    def test_failure_generates_portable_regression(self):
        case = failure_to_case({"id": "F1", "category": "missing-verification", "task": "Verify migration rollback", "skill": "safe-migrations"})
        self.assertEqual(case["id"], "reg-F1")
        self.assertEqual(case["affected_skill"], "safe-migrations")
        self.assertIn("verify result", case["required_behaviors"])

    def test_skill_composition_resolves_transitive_requirements(self):
        graph = {"skills": {
            "a": {"requires": ["b"], "often_followed_by": ["c"], "conflicts_with": []},
            "b": {"requires": ["d"], "often_followed_by": [], "conflicts_with": []},
            "c": {"requires": [], "often_followed_by": [], "conflicts_with": []},
            "d": {"requires": [], "often_followed_by": [], "conflicts_with": []},
        }}
        result = compose(["a"], graph)
        self.assertEqual(result["required"], ["d", "b"])
        self.assertEqual(result["recommended"], ["c"])

    def test_recovery_prefers_latest_checkpoint_without_task_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checkpoint_dir = root / ".godmode" / "checkpoints"
            checkpoint_dir.mkdir(parents=True)
            (checkpoint_dir / "latest.json").write_text(json.dumps({"state": "TESTING", "completed": ["DISCOVERY", "IMPLEMENTATION"], "next_check": "run regression"}), encoding="utf-8")
            recovered = recover_context(root)
            self.assertEqual(recovered["source"], "checkpoint:latest.json")
            self.assertEqual(recovered["state"]["state"], "TESTING")


if __name__ == "__main__":
    unittest.main()
