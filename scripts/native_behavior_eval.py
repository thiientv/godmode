#!/usr/bin/env python3
"""Run behavior eval cases through opt-in native CLI clients and capture evidence."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from typing import Sequence


SUPPORTED_CLIENTS = ("codex", "claude", "custom")
RUNNER_VERSION = 2
SAFE_CASE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
HASH_CHUNK_SIZE = 1024 * 1024
FINAL_MESSAGE_BYTES = 64 * 1024


def sha256_file(path: Path) -> tuple[int, str]:
    """Hash one file without loading it entirely into memory."""

    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(HASH_CHUNK_SIZE), b""):
            size += len(chunk)
            digest.update(chunk)
    return size, digest.hexdigest()


def file_manifest(root: Path) -> list[dict[str, object]]:
    """Return a deterministic manifest without dereferencing workspace symlinks."""

    records: list[dict[str, object]] = []
    paths = sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix())
    for path in paths:
        relative = path.relative_to(root)
        if ".git" in relative.parts:
            continue
        if path.is_symlink():
            records.append(
                {
                    "path": relative.as_posix(),
                    "kind": "symlink",
                    "target": os.readlink(path),
                }
            )
            continue
        if not path.is_file():
            continue
        size, digest = sha256_file(path)
        records.append(
            {
                "path": relative.as_posix(),
                "kind": "file",
                "size": size,
                "sha256": digest,
            }
        )
    return records


def resolve_fixture(case: dict[str, object], case_file: Path) -> Path | None:
    """Resolve one fixture and reject traversal or symlink-based host reads."""

    raw = case.get("fixture")
    if raw is None:
        return None
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("fixture must be a non-empty relative path")
    root = case_file.parent.resolve()
    candidate = root / raw
    fixture = candidate.resolve()
    if fixture != root and root not in fixture.parents:
        raise ValueError(f"fixture escapes case directory: {raw}")
    if not fixture.exists():
        raise ValueError(f"fixture does not exist: {raw}")
    if fixture.is_dir():
        for entry in fixture.rglob("*"):
            if entry.is_symlink():
                raise ValueError(
                    f"fixture contains unsupported symlink: {entry.relative_to(root)}"
                )
    return fixture


def _copy_tree_without_symlinks(source: Path, destination: Path) -> None:
    """Copy a directory tree while rejecting symlinks at copy time."""

    destination.mkdir(parents=True, exist_ok=False)
    with os.scandir(source) as entries:
        for entry in entries:
            source_path = Path(entry.path)
            destination_path = destination / entry.name
            if entry.is_symlink():
                raise ValueError(f"fixture symlink is not allowed: {source_path}")
            if entry.is_dir(follow_symlinks=False):
                _copy_tree_without_symlinks(source_path, destination_path)
            elif entry.is_file(follow_symlinks=False):
                shutil.copy2(source_path, destination_path, follow_symlinks=False)


def _reject_workspace_symlinks(workspace: Path) -> None:
    """Ensure fixture copying did not leave a link the client could dereference."""

    for entry in workspace.rglob("*"):
        if entry.is_symlink():
            raise ValueError(f"fixture copy produced symlink: {entry.relative_to(workspace)}")


def copy_fixture(fixture: Path | None, workspace: Path) -> None:
    """Copy a validated fixture into a disposable workspace."""

    workspace.mkdir(parents=True, exist_ok=True)
    if fixture is None:
        return
    if fixture.is_symlink():
        raise ValueError(f"fixture symlink is not allowed: {fixture}")
    if fixture.is_file():
        shutil.copy2(fixture, workspace / fixture.name, follow_symlinks=False)
    else:
        with os.scandir(fixture) as entries:
            for entry in entries:
                child = Path(entry.path)
                destination = workspace / entry.name
                if entry.is_symlink():
                    raise ValueError(f"fixture symlink is not allowed: {child}")
                if entry.is_dir(follow_symlinks=False):
                    _copy_tree_without_symlinks(child, destination)
                elif entry.is_file(follow_symlinks=False):
                    shutil.copy2(child, destination, follow_symlinks=False)
    _reject_workspace_symlinks(workspace)


def artifact_case_key(case_id: str) -> str:
    """Return a safe single-component artifact directory key."""

    if SAFE_CASE_ID.fullmatch(case_id) and case_id not in {".", ".."}:
        return case_id
    digest = hashlib.sha256(case_id.encode("utf-8")).hexdigest()[:16]
    return f"case-{digest}"


def client_command(
    client: str,
    prompt: str,
    workspace: Path,
    executable: str | None = None,
    client_args: Sequence[str] = (),
) -> list[str]:
    """Build a non-shell native client command."""

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
    """Parse JSON object lines from a captured string."""

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
    """Extract stable usage fields from known client event shapes."""

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
    """Extract a final message from known client events."""

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


def tail_text(path: Path, limit: int = FINAL_MESSAGE_BYTES) -> str:
    """Read at most the final bytes of a text artifact."""

    if not path.is_file():
        return ""
    with path.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        handle.seek(max(0, size - limit))
        data = handle.read()
    return data.decode("utf-8", errors="replace").strip()


def summarize_trace(client: str, trace_path: Path) -> tuple[dict[str, object], str]:
    """Extract usage and final-message evidence without retaining the full trace."""

    usage: dict[str, object] = {}
    final = ""
    if trace_path.is_file():
        with trace_path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(event, dict):
                    continue
                extracted = usage_from_events(client, [event])
                for key, value in extracted.items():
                    usage[key] = value
                message = final_message(client, [event], "")
                if message:
                    final = message
    if not final:
        final = tail_text(trace_path)
    return usage, final


def artifact_name(path: Path, output: Path) -> str:
    """Render an artifact path relative to the run record when possible."""

    try:
        return path.relative_to(output.parent.resolve()).as_posix()
    except ValueError:
        return str(path)


def blocked(result: dict[str, object], limitation: str, duration_ms: int = 0) -> None:
    """Mark a result blocked without pretending execution succeeded."""

    result["status"] = "blocked"
    result["duration_ms"] = duration_ms
    result["limitations"] = [limitation]


def terminate_process_tree(process: subprocess.Popen[bytes], grace_seconds: float = 2.0) -> None:
    """Terminate a spawned client and its process group where supported."""

    if process.poll() is not None:
        return
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            try:
                process.terminate()
            except ProcessLookupError:
                return
    else:
        try:
            process.terminate()
        except OSError:
            return
    try:
        process.wait(timeout=grace_seconds)
        return
    except subprocess.TimeoutExpired:
        pass
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            try:
                process.kill()
            except ProcessLookupError:
                return
    else:
        try:
            process.kill()
        except OSError:
            return
    try:
        process.wait(timeout=grace_seconds)
    except subprocess.TimeoutExpired:
        pass


def resolved_executable(executable: str) -> str | None:
    """Resolve an executable path without invoking a shell."""

    located = shutil.which(executable)
    if located:
        return str(Path(located).resolve())
    path = Path(executable)
    if path.is_file():
        return str(path.resolve())
    return None


def command_output(argv: Sequence[str], cwd: Path | None = None, timeout: float = 3.0) -> str | None:
    """Run a small metadata command and return one compact output line."""

    try:
        completed = subprocess.run(
            list(argv),
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    value = completed.stdout.strip()
    return value.splitlines()[0][:512] if value else None


def git_revision(root: Path) -> str | None:
    """Return the checkout revision when the runner lives in a Git repository."""

    return command_output(["git", "rev-parse", "HEAD"], cwd=root)


def build_environment(case_file: Path, client: str, executable: str | None) -> dict[str, object]:
    """Build reproducibility metadata for a native evaluation run."""

    runner_path = Path(__file__).resolve()
    repo_root = runner_path.parents[1]
    _, case_digest = sha256_file(case_file)
    _, runner_digest = sha256_file(runner_path)
    requested = executable or client
    resolved = resolved_executable(requested)
    client_version = None
    if client in {"codex", "claude"} and resolved is not None:
        client_version = command_output([resolved, "--version"])
    return {
        "runner": runner_path.name,
        "runner_version": RUNNER_VERSION,
        "runner_sha256": runner_digest,
        "client": client,
        "client_version": client_version,
        "executable": requested,
        "resolved_executable": resolved,
        "case_set_sha256": case_digest,
        "godmode_commit": git_revision(repo_root),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "started_at": datetime.now(timezone.utc).isoformat(),
    }


def _write_manifest(path: Path, workspace: Path) -> None:
    path.write_text(json.dumps(file_manifest(workspace), indent=2) + "\n", encoding="utf-8")


def _artifact_paths(artifact_dir: Path) -> dict[str, Path]:
    return {
        "trace": artifact_dir / "trace.jsonl",
        "stderr": artifact_dir / "stderr.txt",
        "final": artifact_dir / "final-message.txt",
        "before": artifact_dir / "workspace-before.json",
        "after": artifact_dir / "workspace-after.json",
        "launch_error": artifact_dir / "launch-error.txt",
    }


def _standard_artifacts(paths: dict[str, Path], output: Path) -> list[str]:
    return [
        artifact_name(paths["trace"], output),
        artifact_name(paths["stderr"], output),
        artifact_name(paths["final"], output),
        artifact_name(paths["before"], output),
        artifact_name(paths["after"], output),
    ]


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
    """Execute one case and capture evidence while keeping grading separate."""

    started = time.monotonic()
    case_id = str(case["id"])
    artifact_root = output.parent.resolve() / f"{output.stem}.artifacts"
    artifact_dir = artifact_root / artifact_case_key(case_id)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    paths = _artifact_paths(artifact_dir)
    try:
        fixture = resolve_fixture(case, case_file)
    except ValueError as error:
        blocked(result, str(error))
        return

    if workspace_root is not None:
        workspace_root.resolve().mkdir(parents=True, exist_ok=True)
    workspace = Path(
        tempfile.mkdtemp(
            prefix=f"godmode-{artifact_case_key(case_id)}-",
            dir=workspace_root.resolve() if workspace_root is not None else None,
        )
    )
    try:
        try:
            copy_fixture(fixture, workspace)
        except (OSError, ValueError) as error:
            blocked(result, f"Fixture copy failed: {error}")
            return

        _write_manifest(paths["before"], workspace)
        try:
            argv = client_command(client, str(case["prompt"]), workspace, executable, client_args)
        except ValueError as error:
            _write_manifest(paths["after"], workspace)
            blocked(result, str(error))
            result["artifacts"] = [
                artifact_name(paths["before"], output),
                artifact_name(paths["after"], output),
            ]
            return

        resolved = resolved_executable(argv[0])
        if resolved is None:
            paths["trace"].write_bytes(b"")
            paths["stderr"].write_bytes(b"")
            paths["final"].write_text("", encoding="utf-8")
            _write_manifest(paths["after"], workspace)
            blocked(result, f"Client executable is unavailable: {argv[0]}")
            result["artifacts"] = _standard_artifacts(paths, output)
            return
        argv[0] = resolved

        launch_error: OSError | None = None
        timed_out = False
        process: subprocess.Popen[bytes] | None = None
        with paths["trace"].open("wb") as trace_handle, paths["stderr"].open("wb") as stderr_handle:
            popen_kwargs: dict[str, object] = {
                "cwd": workspace,
                "stdin": subprocess.DEVNULL,
                "stdout": trace_handle,
                "stderr": stderr_handle,
                "env": os.environ.copy(),
            }
            if os.name == "posix":
                popen_kwargs["start_new_session"] = True
            elif os.name == "nt":
                popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            try:
                process = subprocess.Popen(argv, **popen_kwargs)
            except OSError as error:
                launch_error = error
            if process is not None:
                try:
                    process.wait(timeout=timeout_seconds)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    terminate_process_tree(process)

        duration_ms = int((time.monotonic() - started) * 1000)
        _write_manifest(paths["after"], workspace)

        if launch_error is not None:
            paths["launch_error"].write_text(
                f"{type(launch_error).__name__}: {launch_error}\n",
                encoding="utf-8",
            )
            paths["final"].write_text("", encoding="utf-8")
            blocked(result, f"Client launch failed: {launch_error}", duration_ms)
            result["artifacts"] = [
                artifact_name(paths["trace"], output),
                artifact_name(paths["stderr"], output),
                artifact_name(paths["launch_error"], output),
                artifact_name(paths["before"], output),
                artifact_name(paths["after"], output),
            ]
            return

        usage, final = summarize_trace(client, paths["trace"])
        paths["final"].write_text(final + ("\n" if final else ""), encoding="utf-8")
        result["usage"] = usage
        result["artifacts"] = _standard_artifacts(paths, output)

        if timed_out:
            blocked(result, f"Client timed out after {timeout_seconds:g}s", duration_ms)
        elif process is None:
            blocked(result, "Client process did not start.", duration_ms)
        elif process.returncode:
            blocked(result, f"Client exited with status {process.returncode}", duration_ms)
        else:
            blocked(
                result,
                "Client execution completed; behavior assertions remain ungraded and must be resolved from captured evidence.",
                duration_ms,
            )
    finally:
        if keep_workspace:
            result.setdefault("limitations", []).append(f"Workspace retained at {workspace}")
        else:
            shutil.rmtree(workspace, ignore_errors=True)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse native runner arguments."""

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
        "--allow-model-run",
        action="store_true",
        help="Required opt-in because native clients may consume paid model usage.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run selected cases through one native client."""

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
    run["environment"] = build_environment(case_file, args.client, args.executable)
    cases = {
        str(case["id"]): case
        for case in case_payload["cases"]
        if isinstance(case, dict) and isinstance(case.get("id"), str)
    }
    for result in run["cases"]:
        if isinstance(result, dict) and isinstance(result.get("id"), str):
            execute_case(
                cases[result["id"]],
                result,
                case_file=case_file,
                output=args.output.resolve(),
                client=args.client,
                executable=args.executable,
                client_args=args.client_arg,
                timeout_seconds=args.timeout,
                workspace_root=args.workspace_root,
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
