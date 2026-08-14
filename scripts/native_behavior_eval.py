#!/usr/bin/env python3
"""Run behavior eval cases through opt-in native CLI clients and capture evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from typing import Sequence

SUPPORTED_CLIENTS = ("codex", "claude", "custom")


def file_manifest(root: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if ".git" in path.relative_to(root).parts:
            continue
        data = path.read_bytes()
        records.append({
            "path": path.relative_to(root).as_posix(),
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    return records


def resolve_fixture(case: dict[str, object], case_file: Path) -> Path | None:
    raw = case.get("fixture")
    if raw is None:
        return None
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("fixture must be a non-empty relative path")
    root = case_file.parent.resolve()
    fixture = (root / raw).resolve()
    if fixture != root and root not in fixture.parents:
        raise ValueError(f"fixture escapes case directory: {raw}")
    if not fixture.exists():
        raise ValueError(f"fixture does not exist: {raw}")
    return fixture


def copy_fixture(fixture: Path | None, workspace: Path) -> None:
    workspace.mkdir(parents=True, exist_ok=True)
    if fixture is None:
        return
    if fixture.is_file():
        shutil.copy2(fixture, workspace / fixture.name)
        return
    for child in fixture.iterdir():
        destination = workspace / child.name
        if child.is_dir():
            shutil.copytree(child, destination)
        else:
            shutil.copy2(child, destination)


def client_command(
    client: str,
    prompt: str,
    workspace: Path,
    executable: str | None = None,
    client_args: Sequence[str] = (),
) -> list[str]:
    if client == "codex":
        return [
            executable or "codex", "exec", "--json", "--ephemeral",
            "--skip-git-repo-check", "--sandbox", "workspace-write",
            "--cd", str(workspace), *client_args, prompt,
        ]
    if client == "claude":
        return [
            executable or "claude", "-p", prompt,
            "--output-format", "stream-json", "--permission-mode", "acceptEdits",
            *client_args,
        ]
    if client == "custom":
        if not executable:
            raise ValueError("custom client requires --executable")
        expanded = [
            item.replace("{prompt}", prompt).replace("{workspace}", str(workspace))
            for item in client_args
        ]
        if not any("{prompt}" in item for item in client_args):
            expanded.append(prompt)
        return [executable, *expanded]
    raise ValueError(f"unsupported client: {client}")


def parse_json_lines(stdout: str) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    for line in stdout.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            events.append(value)
    return events


def usage_from_events(client: str, events: Sequence[dict[str, object]]) -> dict[str, object]:
    usage: dict[str, object] = {}
    if client == "claude":
        for event in events:
            if event.get("type") != "result":
                continue
            for source, target in (
                ("duration_ms", "client_duration_ms"),
                ("duration_api_ms", "api_duration_ms"),
                ("num_turns", "turns"),
                ("total_cost_usd", "cost_usd"),
                ("session_id", "session_id"),
            ):
                if event.get(source) is not None:
                    usage[target] = event[source]
    for event in events:
        for key in ("usage", "token_usage"):
            if isinstance(event.get(key), dict):
                usage.setdefault(key, event[key])
    return usage


def final_message(client: str, events: Sequence[dict[str, object]], stdout: str) -> str:
    if client == "claude":
        for event in reversed(events):
            if event.get("type") == "result" and isinstance(event.get("result"), str):
                return str(event["result"])
    if client == "codex":
        for event in reversed(events):
            item = event.get("item")
            if (
                event.get("type") == "item.completed"
                and isinstance(item, dict)
                and item.get("type") == "agent_message"
                and isinstance(item.get("text"), str)
            ):
                return str(item["text"])
    return stdout.strip()


def artifact_name(path: Path, output: Path) -> str:
    try:
        return path.relative_to(output.parent.resolve()).as_posix()
    except ValueError:
        return str(path)


def blocked(result: dict[str, object], limitation: str, duration_ms: int = 0) -> None:
    result["status"] = "blocked"
    result["duration_ms"] = duration_ms
    result["limitations"] = [limitation]


def execute_case(
    case: dict[str, object],
    result: dict[str, object],
    *,
    case_file: Path,
    output: Path,
    client: str,
    executable: str | None,
    client_args: Sequence[str],
    timeout_seconds: float,
    workspace_root: Path | None,
    keep_workspace: bool,
) -> None:
    started = time.monotonic()
    case_id = str(case["id"])
    artifact_dir = output.parent.resolve() / f"{output.stem}.artifacts" / case_id
    artifact_dir.mkdir(parents=True, exist_ok=True)
    try:
        fixture = resolve_fixture(case, case_file)
    except ValueError as error:
        blocked(result, str(error))
        return

    if workspace_root is not None:
        workspace_root.resolve().mkdir(parents=True, exist_ok=True)
    workspace = Path(tempfile.mkdtemp(
        prefix=f"godmode-{case_id}-",
        dir=workspace_root.resolve() if workspace_root is not None else None,
    ))
    try:
        copy_fixture(fixture, workspace)
        before_path = artifact_dir / "workspace-before.json"
        before_path.write_text(json.dumps(file_manifest(workspace), indent=2) + "\n", encoding="utf-8")
        try:
            argv = client_command(client, str(case["prompt"]), workspace, executable, client_args)
        except ValueError as error:
            blocked(result, str(error))
            return
        if shutil.which(argv[0]) is None and not Path(argv[0]).is_file():
            blocked(result, f"Client executable is unavailable: {argv[0]}")
            return
        try:
            completed = subprocess.run(
                argv, cwd=workspace, stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding="utf-8", errors="replace",
                timeout=timeout_seconds, check=False, env=os.environ.copy(),
            )
        except subprocess.TimeoutExpired as error:
            trace_path = artifact_dir / "trace.jsonl"
            stderr_path = artifact_dir / "stderr.txt"
            trace_path.write_text(error.stdout if isinstance(error.stdout, str) else "", encoding="utf-8")
            stderr_path.write_text(error.stderr if isinstance(error.stderr, str) else "", encoding="utf-8")
            blocked(result, f"Client timed out after {timeout_seconds:g}s", int((time.monotonic() - started) * 1000))
            result["artifacts"] = [artifact_name(trace_path, output), artifact_name(stderr_path, output)]
            return

        trace_path = artifact_dir / "trace.jsonl"
        stderr_path = artifact_dir / "stderr.txt"
        final_path = artifact_dir / "final-message.txt"
        after_path = artifact_dir / "workspace-after.json"
        trace_path.write_text(completed.stdout, encoding="utf-8")
        stderr_path.write_text(completed.stderr, encoding="utf-8")
        events = parse_json_lines(completed.stdout)
        final_path.write_text(final_message(client, events, completed.stdout) + "\n", encoding="utf-8")
        after_path.write_text(json.dumps(file_manifest(workspace), indent=2) + "\n", encoding="utf-8")
        duration_ms = int((time.monotonic() - started) * 1000)
        result["usage"] = usage_from_events(client, events)
        result["artifacts"] = [
            artifact_name(trace_path, output), artifact_name(stderr_path, output),
            artifact_name(final_path, output), artifact_name(before_path, output),
            artifact_name(after_path, output),
        ]
        if completed.returncode:
            blocked(result, f"Client exited with status {completed.returncode}", duration_ms)
            result["usage"] = usage_from_events(client, events)
            result["artifacts"] = [
                artifact_name(trace_path, output), artifact_name(stderr_path, output),
                artifact_name(final_path, output), artifact_name(before_path, output),
                artifact_name(after_path, output),
            ]
        else:
            blocked(
                result,
                "Client execution completed; behavior assertions remain ungraded and must be resolved from captured evidence.",
                duration_ms,
            )
            result["usage"] = usage_from_events(client, events)
            result["artifacts"] = [
                artifact_name(trace_path, output), artifact_name(stderr_path, output),
                artifact_name(final_path, output), artifact_name(before_path, output),
                artifact_name(after_path, output),
            ]
    finally:
        if keep_workspace:
            result.setdefault("limitations", []).append(f"Workspace retained at {workspace}")
        else:
            shutil.rmtree(workspace, ignore_errors=True)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cases", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--variant", required=True)
    parser.add_argument("--client", choices=SUPPORTED_CLIENTS, required=True)
    parser.add_argument("--executable")
    parser.add_argument("--client-arg", action="append", default=[])
    parser.add_argument("--timeout", type=float, default=900.0)
    parser.add_argument("--workspace-root", type=Path)
    parser.add_argument("--keep-workspaces", action="store_true")
    parser.add_argument(
        "--allow-model-run", action="store_true",
        help="Required opt-in because native clients may consume paid model usage.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.timeout <= 0:
        raise SystemExit("--timeout must be positive")
    if not args.allow_model_run:
        print("Native eval is opt-in. Re-run with --allow-model-run to permit client execution.")
        return 2

    from behavior_eval import build_run_skeleton, checked_case_payload, validate_run

    case_file = args.cases.resolve()
    case_payload = checked_case_payload(case_file)
    run = build_run_skeleton(case_payload, args.variant)
    run["environment"] = {
        "runner": "native_behavior_eval.py",
        "client": args.client,
        "executable": args.executable or args.client,
    }
    cases = {
        str(case["id"]): case
        for case in case_payload["cases"]
        if isinstance(case, dict) and isinstance(case.get("id"), str)
    }
    for result in run["cases"]:
        if isinstance(result, dict) and isinstance(result.get("id"), str):
            execute_case(
                cases[result["id"]], result,
                case_file=case_file, output=args.output.resolve(), client=args.client,
                executable=args.executable, client_args=args.client_arg,
                timeout_seconds=args.timeout, workspace_root=args.workspace_root,
                keep_workspace=args.keep_workspaces,
            )
    errors = validate_run(run, case_payload)
    if errors:
        print("Generated run record is invalid:")
        for error in errors:
            print(f"- {error}")
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
    print(f"Created native run record: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
