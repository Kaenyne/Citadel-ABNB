"""Four-quarter, additive GBV-conversion review. No component or annual model."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "analysis/src/forecast_methods"))
from kernel_engine_v2 import engine as k0

AS_OF = "2026-09-15"
PARAMETER_CUTOFF = "2026-09-13"
TARGETS = ["2026Q3", "2026Q4", "2027Q1", "2027Q2"]
REVENUE_DIR = ROOT / "data/processed/forecast_methods/lane4_revenue_v2/snapshot_v1"
MODEL_PATH = ROOT / "data/processed/forecast_methods/lane4_model_v2/snapshot_v2/model_input.json"
L0_PATH = ROOT / "data/processed/forecast_methods/L0/L0_vintage_register.csv"
OUT = ROOT / "data/processed/forecast_methods/gbv_event_v1/integration_v1"


def shift(q: str, n: int) -> str:
    return str(pd.Period(q, freq="Q") + n)


def conversion(target: str, gbv: dict[str, float], lam: float, cushion: float,
               weight: float = 2 / 3) -> dict:
    if target not in TARGETS:
        raise ValueError("Target outside the four-quarter submission scope")
    if not math.isfinite(lam) or lam <= 0:
        raise ValueError("Conversion must be positive and finite")
    if not math.isfinite(cushion) or cushion <= -1:
        raise ValueError("Cushion must exceed -100%")
    if weight != 2 / 3:
        raise ValueError("This package retains the fixed two-thirds weight")
    a, b = shift(target, -1), shift(target, -2)
    for q in (a, b):
        if q not in gbv or not math.isfinite(gbv[q]) or gbv[q] <= 0:
            raise ValueError(f"Missing/invalid required GBV input {q}")
    base = weight * gbv[a] + (1 - weight) * gbv[b]
    revenue = base * lam
    return dict(quarter=target,lag1_quarter=a,lag2_quarter=b,
                lag1_gbv_musd=gbv[a],lag2_gbv_musd=gbv[b],weight=weight,
                weighted_gbv_musd=base,lambda_decimal=lam,cushion_decimal=cushion,
                revenue_musd=revenue,implied_guide_musd=revenue/(1+cushion),
                guide_kind="already_issued_diagnostic" if target=="2026Q3" else "conditional_future_guide")


def truth(s):
    return str(s).strip().lower() in {"true", "1", "yes"}


def latest_panels(reg: pd.DataFrame) -> pd.DataFrame:
    r = reg[(reg.metric == "revenue") & reg.period.isin(TARGETS)].copy()
    r = r[r.role.isin(["current", "pit_history"])]
    r = r[r.pit_usable.map(truth) & r.vendor_attributed.map(truth)]
    r = r[(r.unit == "musd") & pd.to_numeric(r.value,errors="coerce").notna()]
    r["observed_timestamp"] = pd.to_datetime(r.as_of_timestamp, utc=True, format="mixed")
    r = r[r.observed_timestamp <= pd.Timestamp(AS_OF+"T00:00:00Z")]
    # Keep source vendors separate. Do not call l0.pit_consensus(vendor=None).
    r = r.sort_values(["observed_timestamp", "register_id"]).groupby(["period","vendor"],sort=False).tail(1)
    return r.sort_values(["period","vendor"])


def prepare() -> dict:
    ops = pd.read_csv(REVENUE_DIR / "operating_inputs.csv")
    old_forecasts = pd.read_csv(REVENUE_DIR / "forecast.csv")
    model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
    case = next(x for x in model["cases"] if x["scenario"] == "review_with_k")
    quarters = {x["quarter"]: x for x in case["quarters"]}
    op = ops[ops.scenario == "review_with_k"].set_index("quarter")
    # Keep the exact prior review's reported-input convention. Precise filing values
    # are a separately calculated comparison; they do not silently refresh lambda.
    actual = {"2026Q1": 29200.0, "2026Q2": 27200.0}
    gbv = {**actual, "2026Q3": float(op.loc["2026Q3","gbv_musd"]),
           "2026Q4": float(op.loc["2026Q4","gbv_musd"]),
           "2027Q1": float(quarters["2027Q1"]["gbv"])}
    source_rows = []
    for q,v in gbv.items():
        source_rows.append(dict(quarter=q,gbv_musd=v,
            status="Reported, original rounded convention" if q in actual else "Conditional GBV assumption",
            source="L4 frozen lag inputs" if q in actual else "L4 working GBV scenario" if q in op.index else "L4 inherited Q1 GBV assumption",
            information_date=("2026-05-07" if q == "2026Q1" else "2026-08-06") if q in actual else "2026-09-13",
            limitation="Exact filing comparison shown separately" if q in actual else "Originally component-derived; shared-input uncertainty" if q in op.index else "Not a validated Q1 GBV forecast"))
    cushion = float(pd.read_csv(REVENUE_DIR/"cushion_inputs.csv").set_index("statistic").loc["median","cushion_decimal"])
    forecast_rows=[]
    for q in TARGETS:
        info=k0.pit_lambda(int(q[-1]),PARAMETER_CUTOFF,variant="ewm")
        row=conversion(q,gbv,float(info["lambda_pct"])/100,cushion)
        row.update(lambda_n_train=int(info["n_train"]),lambda_knowable_from=info["knowable_from"],
                   parameter_cutoff=PARAMETER_CUTOFF,prepared_at=AS_OF,
                   evidence_status="Conditional scenario, not promoted forecast",cushion_n=8)
        forecast_rows.append(row)
    # Existing three-quarter outputs must be preserved; Q2 is genuinely extended.
    reference=old_forecasts[old_forecasts.scenario=="review_with_k"].set_index("quarter")
    preservation=[]
    for r in forecast_rows[:3]:
        for field,prior in [("revenue_musd","revenue_musd"),("implied_guide_musd","guide_musd")]:
            delta=r[field]-float(reference.loc[r["quarter"],prior])
            if abs(delta)>1e-7: raise AssertionError(f"Unintended reference drift: {r['quarter']} {field} {delta}")
            preservation.append(dict(quarter=r["quarter"],field=field,difference_musd=delta))
    precise={**gbv,"2026Q1":29187.0,"2026Q2":27247.0}
    precision=[]
    for r in forecast_rows:
        p=conversion(r["quarter"],precise,r["lambda_decimal"],cushion)
        precision.append(dict(quarter=r["quarter"],revenue_musd=p["revenue_musd"],
                              implied_guide_musd=p["implied_guide_musd"],
                              revenue_delta_musd=p["revenue_musd"]-r["revenue_musd"],
                              scope="Input precision only; frozen lambda unchanged"))
    reg=pd.read_csv(L0_PATH,comment="#")
    panels=latest_panels(reg)
    comparisons=[]
    for r in forecast_rows:
        for c in panels[panels.period==r["quarter"]].to_dict("records"):
            val=float(c["value"])
            comparisons.append(dict(quarter=r["quarter"],vendor=c["vendor"],register_id=c["register_id"],
              observed_at=str(c["as_of_timestamp"]),consensus_revenue_musd=val,
              revenue_gap_musd=r["revenue_musd"]-val,revenue_gap_pct=100*(r["revenue_musd"]/val-1),
              source_role=c["role"],
              break_even_conversion_given_our_gbv=val/r["weighted_gbv_musd"],
              assumed_street_cushion=cushion,implied_street_guide_musd=val/(1+cushion),
              implied_guide_gap_musd=r["implied_guide_musd"]-val/(1+cushion),
              guide_expectation_status="Implied with common cushion, not observed guide expectations"))
    # Default comparison is named Yahoo/LSEG only; no fallback to a different vendor.
    selected=[]
    for q in TARGETS:
        choices=[x for x in comparisons if x["quarter"]==q and "Yahoo" in x["vendor"]]
        selected.append(max(choices,key=lambda x:x["observed_at"]) if choices else dict(quarter=q,
            vendor="Yahoo/LSEG",consensus_revenue_musd=None,observed_at=None,
            guide_expectation_status="Unavailable; no silent cross-vendor fill"))
    lam_history=k0.lambda_table(PARAMETER_CUTOFF)
    all_sources=[REVENUE_DIR/"operating_inputs.csv",REVENUE_DIR/"forecast.csv",REVENUE_DIR/"cushion_inputs.csv",
        MODEL_PATH,L0_PATH,ROOT/"analysis/src/forecast_methods/kernel_engine_v2/engine.py",
        ROOT/"data/processed/forecast_methods/harness/calendar.csv",
        ROOT/"data/processed/overnight/02_kpi_panel_quarterly.csv",
        ROOT/"data/processed/overnight/02_guidance_cushion_series.csv"]
    return dict(as_of=AS_OF,parameter_cutoff=PARAMETER_CUTOFF,forecast=forecast_rows,gbv_inputs=source_rows,
        comparisons=comparisons,selected_comparisons=selected,precision_comparison=precision,
        preservation=preservation,lambda_history=lam_history.to_dict("records"),
        source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in all_sources},
        inherited_q2_revenue_musd=float(quarters["2027Q2"]["revenue"]),
        direct_guide_expectations_available=False,
        instructions="Edit GBV, conversion and cushion inputs. Current path is conditional; no Street-outperformance claim.")


def json_default(x):
    if hasattr(x,"isoformat"): return x.isoformat()
    if hasattr(x,"item"): return x.item()
    raise TypeError(type(x).__name__)


def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=OUT);args=p.parse_args()
    if args.out.exists(): raise FileExistsError("Use a new output directory")
    result=prepare()
    args.out.mkdir(parents=True)
    (args.out/"model.json").write_text(json.dumps(result,indent=2,default=json_default,allow_nan=False),encoding="utf-8")
    for key in ["forecast","gbv_inputs","comparisons","selected_comparisons","precision_comparison","preservation","lambda_history"]:
        pd.DataFrame(result[key]).to_csv(args.out/f"{key}.csv",index=False)
    print(json.dumps({"output":str(args.out),"forecast":result["forecast"],"comparison_rows":len(result["comparisons"])}))


if __name__=="__main__": main()
