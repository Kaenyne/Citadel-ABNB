"""Preregistered between-release information dates, with guarded point reuse."""
from pathlib import Path
import argparse
import importlib.util
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[5]
RUN=Path(__file__).with_name("run.py")
spec=importlib.util.spec_from_file_location("gd_horizon",RUN)
horizon=importlib.util.module_from_spec(spec);spec.loader.exec_module(horizon)
ADDENDUM=ROOT/"docs/revenue-forecast-strategy/05_backtests/GD_CALENDAR_ORIGIN_ADDENDUM_v1.md"


def main():
    p=argparse.ArgumentParser();p.add_argument("--release",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();out=args.out.resolve()
    if out.exists():raise FileExistsError("New output directory required")
    core=horizon.accepted_core();panel,calendar=core.load_inputs()
    original=pd.read_csv(args.release/"predictions.csv");rows=[];checks=[]
    engine=horizon.FrozenForecasts(panel,calendar)
    company_dates=calendar.set_index("print_quarter").print_date.to_dict()
    for (old,pquarter),group in original.groupby(["origin_date","last_reported_quarter"],sort=True):
        new=pd.Period(horizon.qshift(pquarter,2),freq="Q").start_time-pd.Timedelta(days=16)
        newdate=str(new.date());new_known=panel[panel.print_date<=new]
        old_known=panel[panel.print_date<=pd.Timestamp(old)]
        new_guides=horizon.guides_available(calendar,new);old_guides=horizon.guides_available(calendar,old)
        same_actuals=old_known.reset_index(drop=True).equals(new_known.reset_index(drop=True))
        same_guides=old_guides.equals(new_guides)
        allowed=bool(same_actuals and same_guides)
        checks.append(dict(last_reported_quarter=pquarter,source_origin_date=old,
                           company_release_origin_date=company_dates[pquarter],calendar_origin_date=newdate,
                           known_actuals_identical=same_actuals,issued_guides_identical=same_guides,
                           source_known_rows=len(old_known),calendar_known_rows=len(new_known),
                           source_guides=len(old_guides),calendar_guides=len(new_guides),point_reuse_allowed=allowed))
        if allowed:
            replacement=group.copy();replacement["origin_date"]=newdate
        else:
            # Preregistered fallback: actual information changes force the unchanged predictor.
            blocks=[]
            for target in sorted(group.target.unique()):
                is_live=bool(group.loc[group.target==target,"is_live"].iloc[0])
                blocks.extend(engine.predict(target,newdate,is_live)[0])
            replacement=pd.DataFrame(blocks)
        replacement["source_origin_date"]=old
        replacement["company_release_origin_date"]=company_dates[pquarter]
        replacement["calendar_origin_date"]=newdate
        replacement["origin_arm"]="start_p_plus_2_minus_16_calendar_days"
        replacement["point_reused_after_information_equality_check"]=allowed
        rows.append(replacement)
    result=pd.concat(rows,ignore_index=True).sort_values(["is_live","horizon_quarters","target","model"]).reset_index(drop=True)
    out.mkdir(parents=True)
    result.to_csv(out/"predictions.csv",index=False)
    horizon.wide_table(result).to_csv(out/"wide_predictions.csv",index=False)
    pd.DataFrame(checks).to_csv(out/"information_equivalence_checks.csv",index=False)
    receipt={"historical_and_live_origin_groups":len(checks),"all_point_reuses_verified":all(r["point_reuse_allowed"] for r in checks),
             "preregistered_calendar_offset_days":16,"new_origin_rule":"start(p+2)-16calendar_days",
             "original_release_arm_preserved":True,"no_consensus_inputs_used":True,
             "row_count":len(result),"new_optimizer_search":False}
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2),encoding="utf-8")
    sources={"original_predictions":args.release/"predictions.csv","accepted_core":horizon.CORE_PATH,"horizon_code":RUN,
             "addendum":ADDENDUM,"kpi":core.SOURCES["kpi"],"calendar":core.SOURCES["calendar"]}
    manifest={"source_hashes":{k:horizon.sha(v) for k,v in sources.items()},"code_sha256":horizon.sha(__file__),
              "outputs":{p.name:horizon.sha(p) for p in sorted(out.iterdir())}}
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps(receipt,indent=2))


if __name__=="__main__":main()
