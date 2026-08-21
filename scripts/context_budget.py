#!/usr/bin/env python3
"""Estimate and enforce skill context budgets without external dependencies."""
from __future__ import annotations
import argparse, json
from pathlib import Path

GRAPH_PATH = Path(__file__).resolve().parents[1] / "skill-graph.json"

def load(path: Path = GRAPH_PATH) -> dict: return json.loads(path.read_text(encoding="utf-8"))

def estimate_skill(root: Path, name: str) -> int:
    skill = root / "skills" / name / "SKILL.md"
    if not skill.exists(): return 0
    return len(skill.read_text(encoding="utf-8"))

def budget(task: str, skills: list[str], max_chars: int = 40000, root: Path | None = None) -> dict:
    root = root or Path(__file__).resolve().parents[1]
    entries=[]; total=0
    for name in skills:
        chars=estimate_skill(root,name); total += chars
        entries.append({"skill":name,"estimated_chars":chars,"selected": total <= max_chars})
    selected=[x["skill"] for x in entries if x["selected"]]
    excluded=[x["skill"] for x in entries if not x["selected"]]
    return {"task":task,"max_chars":max_chars,"estimated_chars":total,"selected":selected,"excluded":excluded,"entries":entries,"within_budget":not excluded}

def main()->int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("task"); p.add_argument("skills",nargs="+"); p.add_argument("--max-chars",type=int,default=40000)
    a=p.parse_args(); result=budget(a.task,a.skills,a.max_chars); print(json.dumps(result,indent=2,sort_keys=True)); return 0 if result["within_budget"] else 1
if __name__=="__main__": raise SystemExit(main())
