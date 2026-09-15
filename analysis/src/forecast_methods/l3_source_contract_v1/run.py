"""Rebuild the three audited source contracts offline in a NEW directory."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE))
import preserve
import quality

def run(out):
    out=Path(out).resolve()
    allowed=ROOT/'data/processed/forecast_methods/l3_source_contract_v1'
    if not out.is_relative_to(allowed) or out==allowed:
        raise ValueError('Use a new child directory inside the source-contract data package')
    if out.exists():raise FileExistsError('Use a NEW supplement output directory')
    before=preserve.verify()
    out.mkdir(parents=True)
    receipts=[]
    try:
        commands=[('integration_tests',[sys.executable,'-B','-X','utf8','-m','pytest',
                                        *[str(p) for p in sorted(HERE.glob('test_*.py'))],'-q'])]
        for label in ['precision','accounting','consumption']:
            commands.append((label+'_tests',[sys.executable,'-B','-X','utf8','-m','pytest',str(HERE/label),'-q']))
            commands.append((label,[sys.executable,'-B','-X','utf8',str(HERE/label/'run.py'),'--out',str(out/label)]))
        for label,cmd in commands:
            started=time.monotonic()
            p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
            receipts.append({'label':label,'command':subprocess.list2cmdline(cmd),'exit_code':p.returncode,
                             'seconds':time.monotonic()-started})
            (out/(label+'_stdout.txt')).write_text(p.stdout+p.stderr,encoding='utf-8')
            print(f'{label}: exit {p.returncode}',flush=True)
            if p.returncode:raise RuntimeError(label+' failed; receipt preserved')
        check=quality.consumption(quality.read(ROOT/preserve.BUNDLE/'l4_inputs.csv'),
                                  quality.read(out/'consumption/consumption_matrix.csv'))
        if preserve.verify()!=before:raise ValueError('Frozen objects changed during reproduction')
        (out/'integration_checks.json').write_text(json.dumps({'status':'PASS',**check,'preservation':before},indent=2)+'\n',encoding='utf-8')
    finally:
        (out/'reproduction.json').write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8')

def main():
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);args=a.parse_args();run(args.out)

if __name__=='__main__':main()
