"""RNPL diagnostics and LIVE conditional scenarios; frozen inputs remain read-only."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "analysis/src/forecast_methods"))
from kernel_engine_v2 import engine
from harness_v1_1 import RUN_DATE, registry

OUT = ROOT / "data/processed/forecast_methods/rnpl_v2"
KPI = ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv"
PHI = ROOT / "data/processed/forecast_methods/kernel_phi_v2/A1_phi_estimates.csv"
D1 = ROOT / "data/processed/overnight2/D/D1_rnpl_cohort_scenarios.csv"
SOURCE_DATE = "2026-09-11"
PATHS = {"team": (9.9, 8.9), "theo": (9.3, 7.6), "exna": (9.9, 8.1)}


def qshift(q, n):
    return str(pd.Period(q, freq="Q") + n)


def panel():
    p = pd.read_csv(KPI).copy()
    p["quarter"] = p.quarter.map(lambda x: "20" + x[2:] + "Q" + x[0])
    p["season"] = p.quarter.str[-1].astype(int)
    return p.sort_values("quarter").reset_index(drop=True)


def frozen_stock(p, phi_path=PHI):
    """Reapply K1's frozen allocation, never re-estimate its unidentified phi split."""
    coefficients = pd.read_csv(phi_path)
    fit = coefficients[(coefficients["sample"].str.startswith("ex")) & (coefficients.spec == "pooled")]
    if len(fit) != 1:
        raise ValueError("Expected one frozen ex-COVID pooled fit")
    fit = fit.iloc[0]
    phi = np.array([fit[f"phi_{i}"] for i in range(5)])
    if np.any(phi < 0) or not np.isclose(phi.sum(), 1):
        raise ValueError("Invalid frozen phi simplex")
    gbv = p.set_index("quarter").gbv_musd.to_dict()
    rows = []
    for r in p.itertuples():
        lags = [gbv.get(qshift(r.quarter, -j), np.nan) for j in range(4)]
        if not np.isfinite(lags).all():
            continue
        fees = []
        for i in range(1, 5):
            s = (r.season+i-1) % 4 + 1
            base = sum(phi[j+i]*lags[j] for j in range(4) if j+i <= 4)
            fees.append(fit[f"c_Q{s}"]/100*base)
        rows.append(dict(quarter=r.quarter, kernel_fee_stock_musd=sum(fees),
                         carried_next_revenue_musd=fees[0], alloc_factor=fees[0]/sum(fees)))
    return pd.DataFrame(rows)


def backlog(p):
    d = p[["quarter", "season", "gbv_musd", "revenue_musd", "nights_m", "unearned_fees_musd",
           "funds_held_for_clients_musd"]].copy()
    rev = d.set_index("quarter").revenue_musd.to_dict()
    d["next_revenue_musd"] = d.quarter.map(lambda q: rev.get(qshift(q, 1), np.nan))
    d.loc[d.quarter == "2026Q2", "next_revenue_musd"] = 4730.0
    d["next_revenue_basis"] = np.where(d.quarter == "2026Q2", "Q3 guide midpoint 2026-08-06", "subsequent actual; retrospective")
    d["paid_backlog_musd"] = d.unearned_fees_musd + d.funds_held_for_clients_musd
    for col, balance in [("cov_uf", "unearned_fees_musd"), ("cov_fp", "funds_held_for_clients_musd"), ("cov_total", "paid_backlog_musd")]:
        d[col] = d[balance] / d.next_revenue_musd
    d = d.merge(frozen_stock(p), on="quarter", how="left", validate="one_to_one")
    d["booked_share_next"] = d.carried_next_revenue_musd / d.next_revenue_musd
    d["paid_share_next"] = d.cov_uf * d.alloc_factor
    d["unpaid_share_next"] = d.booked_share_next - d.paid_share_next
    d["unbooked_share_next"] = 1-d.booked_share_next
    d["unpaid_share_stock"] = 1-d.unearned_fees_musd/d.kernel_fee_stock_musd
    norm_sample = d[d.quarter.between("2022Q1", "2025Q2")]
    metrics = ["cov_uf", "cov_fp", "cov_total", "paid_share_next", "unpaid_share_next", "unbooked_share_next", "unpaid_share_stock"]
    norms = norm_sample.groupby("season")[metrics].agg(["count", "mean", "std"])
    norm_rows = [dict(season=int(s), metric=k, n=int(v[(k,"count")]), mean=v[(k,"mean")], sd=v[(k,"std")],
                      basis="retrospective 2022Q1-2025Q2; frozen K1 coefficients")
                 for s, v in norms.iterrows() for k in metrics]
    d["norm_unpaid_share_stock"] = d.season.map(norms[("unpaid_share_stock", "mean")])
    d["excess_unpaid_pp"] = 100*(d.unpaid_share_stock-d.norm_unpaid_share_stock)
    d["basis"] = "retrospective frozen K1 ex-COVID pooled stock; not an RNPL causal estimate"
    return d, pd.DataFrame(norm_rows)


def rejected_joint(uf_ratio, fp_ratio, scale, k=0.124/(1-0.124)):
    """Reproduce rejected equations solely to expose their failure."""
    if min(uf_ratio, fp_ratio, scale) <= 0 or not np.isfinite([uf_ratio, fp_ratio, scale]).all():
        raise ValueError("Joint diagnostic requires finite positive inputs")
    a, b = uf_ratio/scale, fp_ratio/scale
    m = (b-a)/(a*k+b)
    return 1-a/(1-m), m


def solve_sensitivity(d):
    rows = []
    # Current norm window and legacy window both retained, explicitly distinguished.
    for start in ("2022Q1", "2023Q1"):
        norm = d[d.quarter.between(start, "2025Q2")].groupby("season")[["cov_uf", "cov_fp"]].mean()
        for r in d[d.quarter.between("2025Q3", "2026Q2")].itertuples():
            for divisor_basis in ("guide_4730", "legacy_scenario_4800"):
                denominator = 4800.0 if divisor_basis == "legacy_scenario_4800" and r.quarter == "2026Q2" else r.next_revenue_musd
                ufr = (r.unearned_fees_musd/denominator)/norm.loc[r.season,"cov_uf"]
                fpr = (r.funds_held_for_clients_musd/denominator)/norm.loc[r.season,"cov_fp"]
                for scale in (1.0, 1.05, 1.10):
                    old_u, old_m = rejected_joint(ufr, fpr, scale)
                    rows.append(dict(quarter=r.quarter, norm_start=start, norm_end="2025Q2", denominator_basis=divisor_basis,
                                     scale_B=scale, uf_ratio=ufr, fp_ratio=fpr,
                                     fee_only_u_pct=100*(1-ufr/scale),
                                     rejected_u_pct=100*old_u, rejected_m_pct=100*old_m,
                                     current_m_pct=np.nan,
                                     status="m UNIDENTIFIED; joint solve REJECTED; fee-only u conditional on B and stable payment mix"))
    return pd.DataFrame(rows)


def gbv_share(night_share_pct, adr_ratio):
    """Invert the exact GBV-to-nights share identity; grid ADR is relative to non-RNPL."""
    s = night_share_pct/100
    if not 0 <= s <= 1 or adr_ratio <= 0:
        raise ValueError("Invalid share or ADR ratio")
    return s*adr_ratio/(1-s+s*adr_ratio)


def leakage(share, differential_pp):
    if not np.isfinite([share, differential_pp]).all() or not 0 <= share <= 1 or not 0 <= differential_pp <= 100:
        raise ValueError("Invalid leakage inputs")
    return share*differential_pp/100


def grid_leakage(grid):
    ratios = {"adr_equal": 1.0, "adr_plus15": 1.15, "adr_plus25": 1.25}
    if set(grid.adr_ratio)-set(ratios):
        raise ValueError(f"Unmapped ADR ratios: {set(grid.adr_ratio)-set(ratios)}")
    rows = []
    for i, r in grid.iterrows():
        for short, q in (("3q26", "2026Q3"), ("4q26", "2026Q4")):
            s = gbv_share(r[f"rnpl_nights_share_{short}_pct"], ratios[r.adr_ratio])
            rows.append(dict(grid_row=int(i), quarter=q, gbv_share=s, differential_pp=r.delta_pp_applied,
                             L=leakage(s, r.delta_pp_applied), source_date=SOURCE_DATE,
                             share_path=r.share_path, adr_ratio=r.adr_ratio, delta_scenario=r.delta_scenario,
                             lead_time=r.lead_time, lead_uplift=r.lead_uplift, rebook_offset=r.rebook_offset,
                             basis="gross flow-share stress; not conditional backlog survival; no rebooking adjustment"))
    return pd.DataFrame(rows)


def live_paths(p, as_of, grid):
    if pd.Timestamp(as_of) < pd.Timestamp(SOURCE_DATE):
        raise ValueError("D1 scenario inputs were unavailable before 2026-09-11")
    term = engine.term_structure(as_of).set_index("quarter")
    if term.loc[["2026Q3", "2026Q4"], "point"].isna().any():
        raise ValueError("K0 required LIVE quarters unavailable")
    q3 = engine.kernel_forecast("2026Q3", as_of)
    lam4 = engine.pit_lambda(4, as_of)
    bq2 = float(p.set_index("quarter").loc["2026Q2", "gbv_musd"])
    q3_anchor_gbv = (term.loc["2026Q4", "base_musd"]-(1-engine.WEIGHT)*bq2)/engine.WEIGHT
    prior = p.set_index("quarter")
    fixed_adr3 = q3_anchor_gbv/(prior.loc["2025Q3", "nights_m"]*(1+PATHS["team"][0]/100))
    central = grid[(grid.share_path == "share_central") & (grid.adr_ratio == "adr_plus25") &
                   (grid.delta_scenario == "delta_4pp") & (grid.lead_time == "lead_2.2") &
                   (grid.lead_uplift == "uplift_7") & (grid.rebook_offset == .25)]
    if len(central) != 1:
        raise ValueError(f"D1 central cell must be unique; got {len(central)}")
    lg = grid_leakage(central.reset_index(drop=True)).set_index("quarter")
    rows, registration = [], []
    for name, nights in PATHS.items():
        night3 = prior.loc["2025Q3", "nights_m"]*(1+nights[0]/100)
        gbv3 = night3*fixed_adr3
        base4 = engine.WEIGHT*gbv3+(1-engine.WEIGHT)*bq2
        pure = {"2026Q3": q3["point"], "2026Q4": base4*lam4["lambda_pct"]/100}
        for quarter in ("2026Q3", "2026Q4"):
            stress = pure[quarter]*(1-lg.loc[quarter,"L"])
            # Two-lag Q3 has no contemporaneous nights input. Q4's Theo path already
            # contains cancellation revisions in the Q3 GBV lag; avoid adding another
            # unidentified overlap. Keep the full stress column for inspection.
            apply = not (name == "theo" and quarter == "2026Q4")
            point = stress if apply else pure[quarter]
            detail = "D1 gross leakage stress applied" if apply else "D1 extra leakage withheld: Theo Q3 nights already contain tail; overlap unidentified"
            rows.append(dict(nights_variant=name, quarter=quarter, q3_nights_yoy_pct=nights[0], q4_nights_yoy_pct=nights[1],
                             q3_nights_m=night3, q4_nights_m=prior.loc["2025Q4","nights_m"]*(1+nights[1]/100),
                             fixed_q3_adr_usd=fixed_adr3, q3_gbv_musd=gbv3,
                             pure_kernel_revenue_musd=pure[quarter], D1_stress_L=lg.loc[quarter,"L"],
                             D1_stress_revenue_musd=stress, registered_revenue_musd=point,
                             applied_L=lg.loc[quarter,"L"] if apply else 0,
                             overlap_policy=detail, basis="LIVE conditional scenario; no measured RNPL effect"))
            for replay in ("PIT", "full_sample"):
                registration.append(dict(method="rnpl-v2", object="revenue_next_q", target="revenue_musd", quarter=quarter,
                                         vintage_date=as_of, horizon_q=pd.Period(quarter,freq="Q").ordinal-pd.Period(as_of,freq="Q").ordinal,
                                         point=point, q50=point, window="LIVE", prior_basis=replay,
                                         n_params=4, n_train=q3["n_train"] if quarter=="2026Q3" else lam4["n_train"],
                                         knowable_from=as_of, spec_id=name,
                                         notes=f"LIVE scenario {name}; {detail}; D1 assumptions dated {SOURCE_DATE}; fixed ADR; no causal inference; two LIVE replays identical"))
    return pd.DataFrame(rows), pd.DataFrame(registration)


def classify_lambda(revenue, base, rounded=True):
    if not np.isfinite([revenue, base]).all() or min(revenue,base) <= 0:
        raise ValueError("Positive revenue and base required")
    lo, hi = [100*(revenue+s)/base for s in ((-.5,.5) if rounded else (0,0))]
    if lo >= 17.09:
        return "NO ALARM"
    if hi < 16.93:
        return "ESCALATE"
    if lo >= 16.93 and hi < 17.09:
        return "WARN"
    return "AMBIGUOUS"


def chart_outputs(as_of):
    values = engine.lambda_table(as_of)
    chart = engine.control_chart(as_of)
    alarms = chart["alarms"].copy()
    # Mean/std chart is K0's chronological descriptive alarm series, not the fixed card.
    rates = []
    for window, start in (("W1", "2023Q1"), ("W2", "2024Q1")):
        for end, label in (("2025Q2", "pre_RNPL_empirical_false_alarm"), ("2026Q2", "all_history_alarm_not_known_false")):
            a = alarms[alarms.quarter.between(start,end)]
            rates.append(dict(window=window, rule="K0 chronological plus/minus 2sd", sample=label,
                              n=len(a), alarms=int(a.alarm.sum()), rate=float(a.alarm.mean()) if len(a) else np.nan))
    histq3 = values[values.quarter.between("2023Q3","2025Q3") & (values.season==3)]
    for cutoff, label in ((17.09, "warn_or_escalate"), (16.93, "escalate")):
        rates.append(dict(window="descriptive", rule=f"fixed Q3 card {label} below {cutoff}", sample="retrospective_same_cells_helped_set_thresholds",
                          n=len(histq3), alarms=int((histq3.lambda_pct<cutoff).sum()), rate=float((histq3.lambda_pct<cutoff).mean())))
    return values, chart, pd.DataFrame(rates)


def plot_chart(values, chart, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2,2,figsize=(10,6),sharex=False)
    for s, ax in enumerate(axes.flat,1):
        v=values[(values.season==s)&(values.quarter >= "2023Q1")]
        c=chart["chart"].set_index("season").loc[s]
        ax.axhspan(c.lower,c.upper,color="#cbd5e1",alpha=.6,label="Current mean ±2sd (descriptive)")
        ax.plot(v.quarter,v.lambda_pct,"o-",color="#0f766e")
        if s==3:
            ax.axhline(17.09,color="#c77700",ls="--",label="Fixed warning 17.09")
            ax.axhline(16.93,color="#b91c1c",ls="--",label="Fixed escalation 16.93")
        ax.set_title(f"Q{s} | n={int(c.n)}"); ax.set_ylabel("Revenue / weighted GBV (%)")
        ax.tick_params(axis="x",labelrotation=30)
        ax.grid(axis="y",alpha=.2)
    axes[1,0].legend(fontsize=7,loc="upper right")
    fig.suptitle("RNPL monitoring: conversion alarms do not identify cancellations")
    fig.tight_layout(); fig.savefig(out,dpi=160); plt.close(fig)


def filing_evidence():
    """Verify the decisive sentences against local public filing extracts."""
    from bs4 import BeautifulSoup
    annual = ROOT/"data/raw/regulatory/quantification/abnb_2025_10k.json"
    quarterly = ROOT/"data/raw/regulatory/quantification/abnb_2026q2_10q.html"
    pages = {p["page"]: " ".join(p["text"].split()) for p in json.loads(annual.read_text(encoding="utf8"))}
    qtext = " ".join(BeautifulSoup(quarterly.read_text(encoding="utf8"),"html.parser").get_text(" ",strip=True).split())
    sentences = [
        ("10-K",60,"Assets and liabilities for foreign subsidiaries with functional currency other than U.S. dollar are translated into U.S. dollars at the rate of exchange existing at the balance sheet date."),
        ("10-K",61,"Monetary assets and liabilities are remeasured at the exchange rate on the balance sheet date and nonmonetary assets and liabilities are measured at historical exchange rates."),
        ("10-K",63,"Host and guest fees are recorded as cash with a corresponding amount in unearned fees."),
        ("10-K",63,"The Company records guest payments, net of service fees, as funds receivable and amounts held on behalf of customers with a corresponding amount in funds payable and amounts payable to customers when cash is received in advance of check-in."),
        ("10-Q",None,"As adoption of RNPL and our other flexible payment options continues to grow, the timing among GBV, revenue, and cash receipts may become less correlated."),
        ("10-Q",None,"Accordingly, unearned fees are not recorded, and operating cash flows are not generated until payment is received."),
    ]
    rows=[]
    for filing,page,quote in sentences:
        text=pages[page] if filing=="10-K" else qtext
        if quote not in text:
            raise ValueError(f"Primary-source sentence did not verify: {filing} page {page}")
        rows.append(dict(filing=filing,page=page,section="Note 2" if filing=="10-K" else "Item 2 MD&A",
                         quote=quote,source=str((annual if filing=="10-K" else quarterly).relative_to(ROOT)),verified=True))
    return rows


def run(as_of, register=False):
    as_of = str(pd.Timestamp(as_of).date())
    if pd.Timestamp(as_of) > pd.Timestamp(RUN_DATE):
        raise ValueError("Cannot run with a future as-of date")
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"filing_evidence.json").write_text(json.dumps(filing_evidence(),indent=2),encoding="utf8")
    p = panel()
    d,norms = backlog(p)
    solve = solve_sensitivity(d)
    grid = pd.read_csv(D1)
    lg = grid_leakage(grid)
    paths, reg = live_paths(p,as_of,grid)
    values, chart, rates = chart_outputs(as_of)
    outputs={"paid_backlog.csv":d,"seasonal_norms.csv":norms,"solve_sensitivity.csv":solve,
             "leakage_grid.csv":lg,"live_scenarios.csv":paths,"registry_preview.csv":reg,
             "lambda_history.csv":values,"lambda_bands.csv":chart["chart"],
             "lambda_chronological_alarms.csv":chart["alarms"],"false_alarm_rates.csv":rates}
    for name,frame in outputs.items():
        frame.to_csv(OUT/name,index=False)
    (OUT/"lambda_card_rule.json").write_text(json.dumps(chart["rule"],indent=2),encoding="utf8")
    plot_chart(values,chart,OUT/"lambda_control_chart.png")
    excess=d[d.quarter.isin(["2025Q4","2026Q1","2026Q2"])][["quarter","excess_unpaid_pp"]]
    expected=np.array([2.0,8.1,9.7])
    actual=excess.sort_values("quarter").excess_unpaid_pp.to_numpy()
    reproduction=bool(np.all((actual >= expected-.05)&(actual < expected+.05)))
    checks=dict(excess_reproduction=reproduction, excess_values=excess.to_dict("records"),
                scenario_rows=len(paths), registry_rows=len(reg), historical_registry_rows=0,
                source_date=SOURCE_DATE, as_of=as_of,
                verdict="PARTIAL: +8.1 headline rounding not reproduced; original joint identification rejected; UF line-specific historical-rate classification not expressly disclosed")
    (OUT/"acceptance.json").write_text(json.dumps(checks,indent=2),encoding="utf8")
    inputs=[KPI,PHI,D1,Path(__file__),ROOT/"analysis/src/forecast_methods/kernel_engine_v2/engine.py",
            ROOT/"data/raw/regulatory/quantification/abnb_2025_10k.json",
            ROOT/"data/raw/regulatory/quantification/abnb_2026q2_10q.html"]
    pd.DataFrame([dict(path=str(x.relative_to(ROOT)).replace("\\","/"),sha256=hashlib.sha256(x.read_bytes()).hexdigest(),bytes=x.stat().st_size,run_date=as_of) for x in inputs]).to_csv(OUT/"input_manifest.csv",index=False)
    if register:
        registry.register(reg)
    print(json.dumps(checks,indent=2))
    print(paths[["nights_variant","quarter","pure_kernel_revenue_musd","D1_stress_revenue_musd","registered_revenue_musd"]].to_string(index=False))
    print(rates.to_string(index=False))


if __name__ == "__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--as-of",default=str(pd.Timestamp(RUN_DATE).date()))
    ap.add_argument("--register",action="store_true")
    args=ap.parse_args()
    run(args.as_of,args.register)
