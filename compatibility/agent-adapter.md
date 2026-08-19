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
  "events": ".godmode/events.jsonl",
  "usage": {"input_tokens": 0, "output_tokens": 0},
  "limits": ["client did not expose tool latency"]
}
```
