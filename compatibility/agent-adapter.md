# Native agent adapter protocol

Godmode remains native-discovery-first: adapters do not replace a client router. They standardize execution telemetry and artifact collection when a harness supports them.

An adapter should expose these conceptual operations:

- `discover_skills()` — report the client's native skill discovery result.
- `start_run(task)` — create a run identifier and provenance record.
- `stream_events()` — emit normalized execution events.
- `collect_usage()` — return tokens, latency, and tool-call counts when available.
- `collect_final_message()` — capture the final completion claim separately from grader output.
- `interrupt()` — stop execution without pretending the task is complete.
- `get_version()` — record client/model/version provenance.

Adapters may omit capabilities when a client does not expose them. Missing telemetry is an explicit limit, never a synthetic success.

## Normalized run record

```json
{
  "schema_version": 1,
  "adapter": "codex",
  "client_version": "unknown",
  "model": "unknown",
  "run_id": "...",
  "task_id": "...",
  "started_at": "...",
  "finished_at": null,
  "events": [],
  "usage": {"input_tokens": 0, "output_tokens": 0},
  "final_message": "",
  "skills": [],
  "limits": ["client did not expose tool latency"]
}
```

`scripts/agent_runs.py` is the dependency-free reference normalizer and run explorer. Native adapters can emit client-specific records and normalize them before storing them under `.godmode/runs/`.

## Event vocabulary

The normalized event shape is intentionally small: timestamp, type, source, run/task IDs, skill, tool, command, status, and free-form details. Client-specific fields remain inside `details` so the core schema stays stable.

## Provenance boundary

An adapter must never synthesize unavailable client/model/version/usage fields. Use `unknown` or an explicit limit instead. This keeps benchmark comparisons honest and allows different harnesses to expose different telemetry capabilities.
