#!/usr/bin/env python3
"""Small dependency-free CLI for durable Godmode task execution."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from task_state import checkpoint, init, recover, status, load, save
from events import emit
from risk import assess, impact, changed_files
from evidence import invalidate_ledger
from gate import gate
from recovery import recover_context
from agent_runs import load_run, run_files
from skill_composition import compose
from router import route
from context_budget import budget
from execution_graph import validate as validate_graph
from lifecycle import transition
from report import report


def main() -> int:
    parser=argparse.ArgumentParser(prog="godmode"); sub=parser.add_subparsers(dest="command",required=True)
    p=sub.add_parser("init"); p.add_argument("objective"); p.add_argument("--risk",default="medium"); p.add_argument("--task-id",default="local")
    sub.add_parser("status"); sub.add_parser("resume"); sub.add_parser("runs")
    p=sub.add_parser("show-run"); p.add_argument("run",type=Path)
    p=sub.add_parser("report"); p.add_argument("run",type=Path); p.add_argument("--output",type=Path)
    p=sub.add_parser("compose"); p.add_argument("skills",nargs="+")
    p=sub.add_parser("route"); p.add_argument("task"); p.add_argument("--limit",type=int,default=5)
    p=sub.add_parser("budget"); p.add_argument("task"); p.add_argument("skills",nargs="+"); p.add_argument("--max-chars",type=int,default=40000)
    p=sub.add_parser("graph"); p.add_argument("graph",type=Path,default=Path(".godmode/execution.json"),nargs="?")
    sub.add_parser("risk"); sub.add_parser("impact"); sub.add_parser("checkpoint").add_argument("name")
    p=sub.add_parser("set-state"); p.add_argument("state"); p.add_argument("--next-check",default="run the next observable verification")
    p=sub.add_parser("invalidate"); p.add_argument("evidence",nargs="?",default=".godmode/evidence.json")
    p=sub.add_parser("gate"); p.add_argument("--target",choices=["VERIFICATION","RELEASE","DONE"],default=None)
    args=parser.parse_args(); root=Path.cwd()
    if args.command=="init": state=init(root,args.objective,args.risk,args.task_id); emit(root,"task_started",task_id=args.task_id,risk=args.risk); print(json.dumps(state,indent=2)); return 0
    if args.command=="status": print(status(root)); return 0
    if args.command=="resume": recovered=recover_context(root); emit(root,"context_recovered",source=recovered["source"]); print(json.dumps(recovered,indent=2)); return 0
    if args.command=="runs":
        files=list(run_files(root))
        if not files: print("No .godmode/runs/*.json found."); return 0
        for path in files:
            run=load_run(path); print(f"{path.name}\t{run.get('run_id') or '-'}\t{run.get('adapter')}\t{run.get('model')}\t{','.join(run.get('skills', []))}")
        return 0
    if args.command=="show-run": print(json.dumps(load_run(args.run),indent=2,sort_keys=True)); return 0
    if args.command=="report":
        text=report(args.run)
        if args.output: args.output.write_text(text,encoding="utf-8")
        else: print(text,end="")
        return 0
    if args.command=="compose": result=compose(args.skills); print(json.dumps(result,indent=2,sort_keys=True)); return 1 if result["conflicts"] else 0
    if args.command=="route": print(json.dumps(route(args.task,limit=args.limit),indent=2,sort_keys=True)); return 0
    if args.command=="budget": result=budget(args.task,args.skills,args.max_chars,root); print(json.dumps(result,indent=2,sort_keys=True)); return 0 if result["within_budget"] else 1
    if args.command=="graph": result=validate_graph(json.loads(args.graph.read_text(encoding="utf-8"))); print(json.dumps(result,indent=2,sort_keys=True)); return 0 if result["valid"] else 1
    if args.command=="risk": print(json.dumps(assess(changed_files(root)),indent=2)); return 0
    if args.command=="impact": print(json.dumps(impact(changed_files(root)),indent=2)); return 0
    if args.command=="checkpoint": checkpoint(root,args.name); print(f"checkpoint: {args.name}"); return 0
    if args.command=="set-state":
        state=load(root)
        if not state: print("no task state",flush=True); return 1
        try:
            updated=transition(state,args.state)
        except ValueError as exc:
            print(f"transition rejected: {exc}",flush=True); return 1
        updated["next_check"]=args.next_check; save(root,updated); emit(root,"state_changed",previous=state.get("state"),current=args.state); return 0
    if args.command=="invalidate":
        result=invalidate_ledger(root,Path(args.evidence))
        for reason in result["reasons"]: emit(root,"evidence_invalidated",reason=reason)
        print(json.dumps(result,indent=2)); return 0
    if args.command=="gate":
        state=load(root)
        if not state: print("no task state",flush=True); return 1
        target=args.target or str(state.get("state","VERIFICATION")); result=gate(state,target); print(json.dumps(result,indent=2,sort_keys=True)); return 0 if result["passed"] else 1
    return 1

if __name__=="__main__": raise SystemExit(main())
