"""Reproduce all five L3 packages in a new directory and retain test/run receipts."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
SRC=ROOT/'analysis/src/forecast_methods'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--fx-bundle',type=Path)
    a=ap.parse_args();out=a.out.resolve()
    if out.exists():raise FileExistsError('Use new output directory '+str(out))
    if not out.is_relative_to(ROOT):raise ValueError('Use output inside this repository for relative source manifests')
    out.mkdir(parents=True)
    # Packages intentionally expose their own standalone run.py. Isolate Python's
    # module cache across suites instead of allowing a bare `import run` collision.
    suites=[('cohort_fx','cohort_fx_v2/tests'),('fee_panel','fee_panel_v1/test_fee_panel.py'),
            ('adr_hotel','l3_adr_hotel_v1/test_audit.py'),('nclh','nclh_transfer_v1/test_nclh.py'),
            ('bundle','l3_integration_v1/test_bundle.py'),('conversion','conversion_validation_v1')]
    commands=[(label+'_tests',[sys.executable,'-B','-X','utf8','-m','pytest',str(SRC/path),'-q'])
              for label,path in suites]
    for label,pkg in [('cohort_fx','cohort_fx_v2'),('fee_panel','fee_panel_v1'),
                      ('adr_hotel','l3_adr_hotel_v1'),('nclh','nclh_transfer_v1'),('conversion','conversion_validation_v1')]:
        cmd=[sys.executable,'-B','-X','utf8',str(SRC/pkg/'run.py'),'--out',str(out/label)]
        if label=='cohort_fx' and a.fx_bundle:cmd+=['--fx-bundle',str(a.fx_bundle)]
        commands.append((label,cmd))
    receipts=[]
    try:
        for label,cmd in commands:
            started=time.monotonic()
            p=subprocess.run(cmd,cwd=ROOT,text=True,encoding='utf-8',capture_output=True)
            elapsed=time.monotonic()-started
            (out/(label+'_stdout.txt')).write_text(p.stdout+p.stderr,encoding='utf-8')
            receipts.append({'label':label,'command':subprocess.list2cmdline(cmd),'exit_code':p.returncode,'seconds':elapsed})
            print(f'{label}: exit {p.returncode}, {elapsed:.2f}s',flush=True)
            if p.returncode:raise RuntimeError(label+' failed; inspect preserved receipt')
    finally:
        (out/'reproduction.json').write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
