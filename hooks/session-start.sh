#!/usr/bin/env bash

set -euo pipefail

plugin_root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
context_file="${plugin_root}/hooks/bootstrap.md"

if command -v python3 >/dev/null 2>&1 && [ -f "$context_file" ]; then
  CONTEXT_FILE="$context_file" python3 - <<'PY'
import json
import os
from pathlib import Path

context_path = Path(os.environ["CONTEXT_FILE"])
context = context_path.read_text(encoding="utf-8")
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": context,
    }
}))
PY
else
  printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"Godmode skills are available through native Agent Skills discovery. Use fresh verification evidence before completion claims."}}'
fi
