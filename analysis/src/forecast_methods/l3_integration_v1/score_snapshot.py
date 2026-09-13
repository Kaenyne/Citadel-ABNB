"""Reuse audited Lane 2 scorer wrapper, preserving the complete committed close board."""
from pathlib import Path
import argparse
import json
import sys
import pandas as pd

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'analysis/src/forecast_methods'))
from lane2_validation_v1.run import scorer, compare_frames, tests

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--tests',action='store_true')
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    summary={}
    try:
        if a.tests:
            summary['frozen_tests']=tests(a.out)
        one=scorer('harness',a.out/'format_1_0')
        two=scorer('harness_v1_1',a.out/'format_1_1')
        baseline=ROOT/'data/processed/forecast_methods/lane2_validation_v1/close/format_1_0/scoreboard.csv'
        summary['base_scoreboard']=str(baseline.relative_to(ROOT))
        summary['compared_to_l2_close']=compare_frames(pd.read_csv(baseline),one)
        summary['both_formats']=compare_frames(one,two)
        summary['verdict']='PASS'
    except Exception as exc:
        summary.update(verdict='FAIL',error=repr(exc))
        raise
    finally:
        (a.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
