#!/usr/bin/env python3
"""Evidence ledger helpers with git-aware freshness and provenance."""
from __future__ import annotations
import hashlib, json, os, platform, subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def _git(root: Path, *args: str) -> str:
    try: return subprocess.check_output(["git", *args], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError): return ""

def file_digest(root: Path, paths: list[str]) -> str:
    h=hashlib.sha256()
    for name in sorted(paths):
        path=root/name
        if path.is_file(): h.update(name.encode()); h.update(path.read_bytes())
    return h.hexdigest()

def provenance(root: Path, paths: list[str], command: str = "") -> dict[str, Any]:
    return {"commit_sha": _git(root,"rev-parse","HEAD"), "files": sorted(paths), "file_digest": file_digest(root,paths), "python": platform.python_version(), "platform": platform.platform(), "command": command, "cwd": str(root), "environment": {k: os.environ[k] for k in ("CI","GITHUB_ACTIONS") if k in os.environ}}

def create(claim: str, kind: str, command: str, result: str, root: Path, paths: list[str], limits: list[str] | None = None) -> dict[str, Any]:
    return {"kind":"evidence-ledger","claim":claim,"check":{"type":kind,"command":command},"result":{"status":result},"freshness":{"created_at":datetime.now(timezone.utc).isoformat(),"commit_sha":_git(root,"rev-parse","HEAD")},"scope":{"files":sorted(paths),"digest":file_digest(root,paths)},"provenance":provenance(root,paths,command),"limits":limits or [],"valid":result in {"passed","verified","success"}}

def invalidate(evidence: dict[str, Any], root: Path) -> tuple[bool,str]:
    scope=evidence.get("scope",{}); paths=scope.get("files",[]); expected=scope.get("digest")
    if not isinstance(paths,list) or not expected: return False,"evidence has no file scope/digest"
    actual=file_digest(root,[str(p) for p in paths])
    if actual != expected:
        evidence["valid"]=False; evidence["invalidated"]={"reason":"scoped files changed after evidence was recorded","current_digest":actual}; return True,"stale: scoped files changed"
    commit=evidence.get("freshness",{}).get("commit_sha"); head=_git(root,"rev-parse","HEAD")
    if commit and head and commit != head:
        changed=_git(root,"diff","--name-only",commit,"HEAD").splitlines()
        if any(path in paths for path in changed):
            evidence["valid"]=False; evidence["invalidated"]={"reason":"scoped files changed after evidence commit","current_commit":head}; return True,"stale: scoped files changed"
    return False,"fresh"

def invalidate_ledger(root: Path, evidence_path: Path) -> dict[str, Any]:
    payload=json.loads(evidence_path.read_text(encoding="utf-8")); entries=payload if isinstance(payload,list) else payload.get("evidence",[]); invalidated=[]
    for entry in entries:
        changed,reason=invalidate(entry,root)
        if changed: invalidated.append(reason)
    if isinstance(payload,dict): payload["evidence"]=entries
    evidence_path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return {"invalidated":len(invalidated),"reasons":invalidated}
