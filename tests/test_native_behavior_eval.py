from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from native_behavior_eval import (  # noqa: E402
    client_command,
    copy_fixture,
    execute_case,
    file_manifest,
    final_message,
    parse_json_lines,
    resolve_fixture,
    usage_from_events,
)


class NativeBehaviorEvalTests(unittest.TestCase):
    def test_client_commands_are_non_interactive_argv(self) -> None:
        workspace = Path("/tmp/workspace")
        codex = client_command("codex", "Do it", workspace)
        self.assertEqual(codex[:3], ["codex", "exec", "--json"])
        self.assertIn("--ephemeral", codex)
        self.assertIn("workspace-write", codex)
        self.assertEqual(codex[-1], "Do it")

        claude = client_command("claude", "Do it", workspace)
        self.assertEqual(claude[:3], ["claude", "-p", "Do it"])
        self.assertIn("stream-json", claude)
        self.assertIn("acceptEdits", claude)

        custom = client_command("custom", "Do it", workspace, sys.executable, ["tool.py", "{prompt}"])
        self.assertEqual(custom, [sys.executable, "tool.py", "Do it"])

    def test_fixture_resolution_rejects_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            cases = root / "cases.json"
            cases.write_text("{}", encoding="utf-8")
            fixture = root / "fixture"
            fixture.mkdir()
            self.assertEqual(resolve_fixture({"fixture": "fixture"}, cases), fixture)
            with self.assertRaisesRegex(ValueError, "escapes"):
                resolve_fixture({"fixture": "../outside"}, cases)

    def test_manifest_and_fixture_copy_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            fixture = root / "fixture"
            fixture.mkdir()
            (fixture / "b.txt").write_text("b", encoding="utf-8")
            (fixture / "a.txt").write_text("a", encoding="utf-8")
            workspace = root / "workspace"
            copy_fixture(fixture, workspace)
            manifest = file_manifest(workspace)
            self.assertEqual([item["path"] for item in manifest], ["a.txt", "b.txt"])
            self.assertTrue(all(len(str(item["sha256"])) == 64 for item in manifest))

    def test_usage_and_final_message_extract_known_client_fields(self) -> None:
        claude_events = parse_json_lines(
            '{"type":"result","result":"done","duration_ms":12,"num_turns":2,"total_cost_usd":0.01}\n'
        )
        self.assertEqual(final_message("claude", claude_events, ""), "done")
        usage = usage_from_events("claude", claude_events)
        self.assertEqual(usage["client_duration_ms"], 12)
        self.assertEqual(usage["turns"], 2)
        self.assertEqual(usage["cost_usd"], 0.01)

        codex_events = [
            {"type": "item.completed", "item": {"type": "agent_message", "text": "finished"}}
        ]
        self.assertEqual(final_message("codex", codex_events, ""), "finished")

    def test_custom_client_executes_and_remains_blocked_until_graded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            cases = root / "cases.json"
            cases.write_text("{}", encoding="utf-8")
            output = root / "run.json"
            result = {
                "id": "sample",
                "status": "blocked",
                "assertions": [{"id": "proof", "passed": None, "evidence": ""}],
                "duration_ms": 0,
                "usage": {},
                "artifacts": [],
                "limitations": ["Run has not been executed."],
            }
            script = (
                "import json, pathlib; "
                "pathlib.Path('created.txt').write_text('ok'); "
                "print(json.dumps({'type':'result','result':'ok'}))"
            )
            execute_case(
                {"id": "sample", "prompt": "hello"}, result,
                case_file=cases, output=output, client="custom",
                executable=sys.executable, client_args=["-c", script],
                timeout_seconds=5, workspace_root=None, keep_workspace=False,
            )
            self.assertEqual(result["status"], "blocked")
            self.assertIn("remain ungraded", result["limitations"][0])
            self.assertGreaterEqual(result["duration_ms"], 0)
            self.assertEqual(len(result["artifacts"]), 5)
            artifact_dir = root / "run.artifacts" / "sample"
            after = json.loads((artifact_dir / "workspace-after.json").read_text(encoding="utf-8"))
            self.assertEqual([item["path"] for item in after], ["created.txt"])


if __name__ == "__main__":
    unittest.main()
