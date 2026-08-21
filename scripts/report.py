#!/usr/bin/env python3
"""Render a concise human-readable report from a normalized agent run."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def report(path:Path)->str:
    r=json.loads(path.read_text(encoding="utf-8")); usage=r.get("usage",{}); events=r.get("events",[])
    lines=[f"# Godmode Run: {r.get('run_id') or '-'}",'',f"- Adapter: {r.get('adapter')}",f"- Model: {r.get('model')}",f"- Task: {r.get('task_id') or '-'}",f"- Started: {r.get('started_at')}",f"- Finished: {r.get('finished_at') or '-'}",f"- Skills: {', '.join(r.get('skills',[])) or '-'}",f"- Tokens: {usage.get('input_tokens',0)} in / {usage.get('output_tokens',0)} out",f"- Events: {len(events)}",f"- Limits: {', '.join(r.get('limits',[])) or 'none'}",'']
    if r.get('final_message'): lines += ['## Final message','',str(r['final_message']),'']
    lines += ['## Event summary','',*([f"- {e.get('timestamp')} — {e.get('type')} — {e.get('status') or 'n/a'}" for e in events] or ['- none'])]
    return '\n'.join(lines)+'\n'

def main()->int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('run',type=Path); p.add_argument('--output',type=Path); a=p.parse_args(); text=report(a.run)
    if a.output:a.output.write_text(text,encoding='utf-8')
    else:print(text,end='')
    return 0
if __name__=='__main__':raise SystemExit(main())
