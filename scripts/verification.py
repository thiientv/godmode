#!/usr/bin/env python3
"""Run configured verification commands and emit machine-readable evidence."""
from __future__ import annotations
import argparse,json,subprocess
from pathlib import Path

def verify(commands:list[str], root:Path)->dict:
    results=[]
    for command in commands:
        p=subprocess.run(command,shell=True,cwd=root,text=True,capture_output=True)
        results.append({'command':command,'passed':p.returncode==0,'exit_code':p.returncode,'stdout':p.stdout[-4000:],'stderr':p.stderr[-4000:]})
    return {'passed':all(x['passed'] for x in results),'checks':results}

def main()->int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('commands',nargs='+'); p.add_argument('--root',type=Path,default=Path('.')); p.add_argument('--output',type=Path)
    a=p.parse_args(); result=verify(a.commands,a.root); text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if a.output:a.output.write_text(text,encoding='utf-8')
    else:print(text,end='')
    return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
