from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from native_behavior_eval import (  # noqa: E402
    artifact_case_key,
    build_environment,
    client_command,
    execute_case,
    file_manifest,
    final_message,
    parse_json_lines,
    resolve_fixture,
    summarize_trace,
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

    def test_artifact_case_key_never_preserves_path_components(self) -> None:
        self.assertEqual(artifact_case_key("safe-case_1"), "safe-case_1")
        self.assertTrue(artifact_case_key("../escape").startswith("case-"))
        self.assertTrue(artifact_case_key("/tmp/escape").startswith("case-"))
        self.assertNotIn("/", artifact_case_key("../escape"))

    def test_fixture_resolution_rejects_escape_and_nested_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            cases = root / "cases.json"
            cases.write_text("{}", encoding="utf-8")
            fixture = root / "fixture"
            fixture.mkdir()
            self.assertEqual(resolve_fixture({"fixture": "fixture"}, cases), fixture)
            with self.assertRaisesRegex(ValueError, "escapes"):
                resolve_fixture({"fixture": "../outside"}, cases)

            outside = root.parent / f"{root.name}-outside.txt"
            outside.write_text("secret", encoding="utf-8")
            link = fixture / "nested-link"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are unavailable")
            try:
                with self.assertRaisesRegex(ValueError, "symlink"):
                    resolve_fixture({"fixture": "fixture"}, cases)
            finally:
                outside.unlink(missing_ok=True)

    def test_manifest_hashes_incrementally_and_does_not_dereference_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "large.bin").write_bytes(b"a" * (2 * 1024 * 1024 + 7))
            outside = root.parent / f"{root.name}-outside.txt"
            outside.write_text("outside", encoding="utf-8")
            link = root / "external-link"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are unavailable")
            try:
                with mock.patch.object(Path, "read_bytes", side_effect=AssertionError("read_bytes must not be used")):
                    manifest = file_manifest(root)
            finally:
                outside.unlink(missing_ok=True)
            records = {item["path"]: item for item in manifest}
            self.assertEqual(records["large.bin"]["size"], 2 * 1024 * 1024 + 7)
            self.assertEqual(records["external-link"]["kind"], "symlink")
            self.assertNotIn("sha256", records["external-link"])

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

    def test_trace_summary_streams_known_events(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            trace = Path(temporary_directory) / "trace.jsonl"
            trace.write_text(
                "noise\n"
                '{"type":"result","result":"done","duration_ms":12,"num_turns":2}\n',
                encoding="utf-8",
            )
            usage, final = summarize_trace("claude", trace)
            self.assertEqual(final, "done")
            self.assertEqual(usage["client_duration_ms"], 12)

    def _result(self, case_id: str = "sample") -> dict[str, object]:
        return {
            "id": case_id,
            "status": "blocked",
            "assertions": [{"id": "proof", "passed": None, "evidence": ""}],
            "duration_ms": 0,
            "usage": {},
            "artifacts": [],
            "limitations": ["Run has not been executed."],
        }

    def test_custom_client_executes_and_remains_blocked_until_graded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            cases = root / "cases.json"
            cases.write_text("{}", encoding="utf-8")
            output = root / "run.json"
            result = self._result()
            script = (
                "import json, pathlib; "
                "pathlib.Path('created.txt').write_text('ok'); "
                "print(json.dumps({'type':'result','result':'ok'}))"
            )
            execute_case(
                {"id": "sample", "prompt": "hello"},
                result,
                case_file=cases,
                output=output,
                client="custom",
                executable=sys.executable,
                client_args=["-S", "-c", script],
                timeout_seconds=5,
                workspace_root=None,
                keep_workspace=False,
            )
            self.assertEqual(result["status"], "blocked")
            self.assertIn("remain ungraded", result["limitations"][0])
            self.assertEqual(len(result["artifacts"]), 5)
            artifact_dir = root / "run.artifacts" / "sample"
            after = json.loads((artifact_dir / "workspace-after.json").read_text(encoding="utf-8"))
            self.assertEqual([item["path"] for item in after], ["created.txt"])

    def test_launch_oserror_becomes_blocked_with_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            cases = root / "cases.json"
            cases.write_text("{}", encoding="utf-8")
            output = root / "run.json"
            result = self._result()
            with mock.patch("native_behavior_eval.subprocess.Popen", side_effect=OSError("launch boom")):
                execute_case(
                    {"id": "sample", "prompt": "hello"},
                    result,
                    case_file=cases,
                    output=output,
                    client="custom",
                    executable=sys.executable,
                    client_args=["-S", "-c", "print('x')"],
                    timeout_seconds=5,
                    workspace_root=None,
                    keep_workspace=False,
                )
            self.assertEqual(result["status"], "blocked")
            self.assertIn("launch failed", result["limitations"][0])
            self.assertTrue((root / "run.artifacts" / "sample" / "launch-error.txt").is_file())
            self.assertTrue((root / "run.artifacts" / "sample" / "workspace-after.json").is_file())

    def test_timeout_preserves_partial_trace_and_workspace_after(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            cases = root / "cases.json"
            cases.write_text("{}", encoding="utf-8")
            output = root / "run.json"
            result = self._result()
            script = (
                "import pathlib, time; "
                "pathlib.Path('changed.txt').write_text('changed'); "
                "print('partial', flush=True); "
                "time.sleep(30)"
            )
            execute_case(
                {"id": "sample", "prompt": "hello"},
                result,
                case_file=cases,
                output=output,
                client="custom",
                executable=sys.executable,
                client_args=["-S", "-c", script],
                timeout_seconds=0.15,
                workspace_root=None,
                keep_workspace=False,
            )
            artifact_dir = root / "run.artifacts" / "sample"
            self.assertEqual(result["status"], "blocked")
            self.assertIn("timed out", result["limitations"][0])
            self.assertIn("partial", (artifact_dir / "trace.jsonl").read_text(encoding="utf-8"))
            after = json.loads((artifact_dir / "workspace-after.json").read_text(encoding="utf-8"))
            self.assertEqual([item["path"] for item in after], ["changed.txt"])
            self.assertEqual(len(result["artifacts"]), 5)

    def test_path_like_case_id_cannot_escape_artifact_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            cases = root / "cases.json"
            cases.write_text("{}", encoding="utf-8")
            output = root / "run.json"
            result = self._result("../escape")
            execute_case(
                {"id": "../escape", "prompt": "hello"},
                result,
                case_file=cases,
                output=output,
                client="custom",
                executable=sys.executable,
                client_args=["-S", "-c", "print('ok')"],
                timeout_seconds=5,
                workspace_root=None,
                keep_workspace=False,
            )
            self.assertFalse((root / "escape").exists())
            artifact_root = root / "run.artifacts"
            children = list(artifact_root.iterdir())
            self.assertEqual(len(children), 1)
            self.assertTrue(children[0].name.startswith("case-"))

    def test_environment_includes_reproducibility_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            case_file = Path(temporary_directory) / "cases.json"
            case_file.write_text('{"schema_version":1}', encoding="utf-8")
            env = build_environment(case_file, "custom", sys.executable)
            self.assertEqual(env["runner_version"], 2)
            self.assertEqual(len(str(env["case_set_sha256"])), 64)
            self.assertEqual(len(str(env["runner_sha256"])), 64)
            self.assertEqual(env["resolved_executable"], str(Path(sys.executable).resolve()))
            self.assertIn("python_version", env)
            self.assertIn("platform", env)


if __name__ == "__main__":
    unittest.main()
