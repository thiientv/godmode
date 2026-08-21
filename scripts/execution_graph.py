#!/usr/bin/env python3
"""Validate and inspect a small durable task execution DAG."""
from __future__ import annotations
import argparse, json
from pathlib import Path

STATES={"pending","running","blocked","failed","completed"}

def validate(graph:dict)->dict:
    nodes=graph.get("nodes",[]); ids={n.get("id") for n in nodes}; errors=[]
    for n in nodes:
        if not n.get("id") or n.get("state","pending") not in STATES: errors.append(f"invalid node: {n}")
        for dep in n.get("depends_on",[]):
            if dep not in ids: errors.append(f"missing dependency: {n.get('id')} -> {dep}")
    visiting=set(); visited=set()
    def visit(i):
        if i in visiting: errors.append(f"cycle detected at: {i}"); return
        if i in visited:return
        visiting.add(i)
        node=next((n for n in nodes if n.get("id")==i),{})
        for d in node.get("depends_on",[]): visit(d)
        visiting.remove(i); visited.add(i)
    for i in ids: visit(i)
    ready=[]
    states={n.get("id"):n.get("state","pending") for n in nodes}
    for n in nodes:
        if n.get("state","pending")=="pending" and all(states.get(d)=="completed" for d in n.get("depends_on",[])): ready.append(n["id"])
    return {"valid":not errors,"errors":errors,"ready":sorted(ready),"node_count":len(nodes)}

def main()->int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("graph",type=Path,default=Path(".godmode/execution.json"),nargs="?"); a=p.parse_args()
    result=validate(json.loads(a.graph.read_text(encoding="utf-8"))); print(json.dumps(result,indent=2,sort_keys=True)); return 0 if result["valid"] else 1
if __name__=="__main__": raise SystemExit(main())
