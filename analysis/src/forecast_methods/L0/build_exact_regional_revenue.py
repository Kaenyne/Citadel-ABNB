"""L0 file 1 — L0_exact_regional_revenue.csv: the 72-cell exact regional revenue spine.

56 filed three-month regional revenue cells (1Q22-2Q26) + 16 Q4 back-outs (2022-2025).

Rules enforced here (from the addendum, verified against the raw file tonight):
  * The four-region axis is srt:NorthAmericaMember / us-gaap:EMEAMember /
    srt:LatinAmericaMember / srt:AsiaPacificMember (45 rows each).
    country:US, us-gaap:NonUsMember and country:FR are a DIFFERENT axis and are
    NEVER mixed in or summed with the four-region axis.
  * Filter to period length 80-100 days (three-month facts), then de-duplicate on
    (start, end, geo) keeping the EARLIEST filing date as the vintage, because the
    file restates the same cell across filings.
  * Regional revenue is filed only in the three 10-Qs each year, so there is never a
    filed Q4 cell. The 16 back-outs are annual (10-K) minus the three filed quarters.

Hard assertions (raise on failure):
  A1  exactly 56 filed cells, 14 quarter-ends x 4 regions
  A2  exactly 16 back-out cells, 4 years x 4 regions
  A3  company Q4 totals reproduce to $1M: 4Q22 1902 / 4Q23 2218 / 4Q24 2480 / 4Q25 2778
  A4  every back-out strictly positive
  A5  the four regions sum to consolidated revenue (02_kpi_panel_quarterly.csv) within $1M,
      for every quarter in 1Q22-2Q26 including the back-out quarters

Soft check (reported, never raises):
  S1  the architect's "each back-out within 40% of its own Q3". This FAILS for EMEA in
      all four years and for LatAm 4Q25; Q4 is structurally ~55% below Q3 in EMEA and
      ~40-50% above Q3 in LatAm. The defensible version is S2.
  S2  the region's own Q4/Q3 ratio within 15% of that region's mean Q4/Q3 ratio.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd  # noqa: E402

from _paths import OUT, OVERNIGHT, rel  # noqa: E402

REGION_MEMBER = {
    "srt:NorthAmericaMember": "na",
    "us-gaap:EMEAMember": "emea",
    "srt:LatinAmericaMember": "latam",
    "srt:AsiaPacificMember": "apac",
}
OTHER_AXIS = {"country:US", "us-gaap:NonUsMember", "country:FR"}

Q4_TOTAL_TARGETS = {"4Q22": 1902.0, "4Q23": 2218.0, "4Q24": 2480.0, "4Q25": 2778.0}

SRC_GEO = OVERNIGHT / "10_xbrl_revenue_geography.csv"
SRC_REGXBRL = OVERNIGHT / "10_regional_revenue_xbrl.csv"
SRC_KPI = OVERNIGHT / "02_kpi_panel_quarterly.csv"


def _qlabel(ts: pd.Timestamp) -> str:
    p = pd.Period(ts, freq="Q-DEC")
    return f"{p.quarter}Q{str(p.year)[2:]}"


def _load_geo() -> pd.DataFrame:
    df = pd.read_csv(SRC_GEO, parse_dates=["filed", "start", "end"])
    df["row_id"] = df.index  # 0-based row index in the raw file (excl. header)
    df["period_days"] = (df["end"] - df["start"]).dt.days + 1
    return df


def build(verbose: bool = True) -> tuple[pd.DataFrame, dict]:
    geo = _load_geo()
    diag: dict = {}

    # --- axis hygiene -----------------------------------------------------
    seen = set(geo["geo"].unique())
    assert set(REGION_MEMBER) <= seen, f"missing region members: {set(REGION_MEMBER) - seen}"
    diag["geo_members"] = {g: int((geo["geo"] == g).sum()) for g in sorted(seen)}
    diag["other_axis_rows_excluded"] = int(geo["geo"].isin(OTHER_AXIS).sum())

    three_mo_all = geo[geo["period_days"].between(80, 100)]
    diag["three_month_rows_all_axes"] = int(len(three_mo_all))

    reg = geo[geo["geo"].isin(REGION_MEMBER)].copy()
    reg["region"] = reg["geo"].map(REGION_MEMBER)

    # --- 56 filed three-month cells --------------------------------------
    q = reg[reg["period_days"].between(80, 100)].copy()
    diag["three_month_regional_rows_before_dedup"] = int(len(q))
    q = q.sort_values(["filed", "accn"]).drop_duplicates(subset=["start", "end", "geo"], keep="first")
    diag["three_month_regional_rows_after_dedup"] = int(len(q))

    q["quarter"] = q["end"].map(_qlabel)
    q["revenue_musd"] = (q["value_usd"] / 1e6).round(3)
    filed = pd.DataFrame(
        {
            "quarter": q["quarter"],
            "region": q["region"],
            "revenue_musd": q["revenue_musd"],
            "basis": "filed",
            "source_row": q["row_id"],
            "period_days": q["period_days"],
            "vintage": q["filed"].dt.strftime("%Y-%m-%d"),
            "accn": q["accn"],
            "form": q["form"],
            "period_start": q["start"].dt.strftime("%Y-%m-%d"),
            "period_end": q["end"].dt.strftime("%Y-%m-%d"),
            "source_path": rel(SRC_GEO),
            "knowable_from": q["filed"].dt.strftime("%Y-%m-%d"),
        }
    ).sort_values(["quarter", "region"])

    # --- 16 Q4 back-outs --------------------------------------------------
    ann = reg[reg["period_days"].between(350, 380)].copy()
    ann = ann.sort_values(["filed", "accn"]).drop_duplicates(subset=["start", "end", "geo"], keep="first")
    ann["year"] = ann["end"].dt.year
    ann["revenue_musd"] = (ann["value_usd"] / 1e6).round(3)
    diag["annual_regional_cells"] = int(len(ann))

    rows = []
    filed_idx = filed.set_index(["quarter", "region"])["revenue_musd"]
    for _, a in ann.iterrows():
        yr, region = int(a["year"]), REGION_MEMBER[a["geo"]]
        yy = str(yr)[2:]
        qs = [f"{i}Q{yy}" for i in (1, 2, 3)]
        if not all((qq, region) in filed_idx.index for qq in qs):
            continue  # 2021 has no filed quarterly regional cells in this file
        nine_m = float(sum(filed_idx.loc[(qq, region)] for qq in qs))
        rows.append(
            {
                "quarter": f"4Q{yy}",
                "region": region,
                "revenue_musd": round(float(a["revenue_musd"]) - nine_m, 3),
                "basis": "back_out",
                "source_row": int(a["row_id"]),
                "period_days": int(a["period_days"]),
                "vintage": a["filed"].strftime("%Y-%m-%d"),
                "accn": a["accn"],
                "form": a["form"],
                "period_start": f"{yr}-10-01",
                "period_end": f"{yr}-12-31",
                "source_path": rel(SRC_GEO),
                "knowable_from": a["filed"].strftime("%Y-%m-%d"),
            }
        )
    backout = pd.DataFrame(rows).sort_values(["quarter", "region"])

    spine = pd.concat([filed, backout], ignore_index=True)
    spine["quarter_end"] = pd.PeriodIndex(
        [f"20{qq[2:]}Q{qq[0]}" for qq in spine["quarter"]], freq="Q-DEC"
    )
    spine = spine.sort_values(["quarter_end", "region"]).drop(columns=["quarter_end"]).reset_index(drop=True)

    # ---------------- assertions -----------------------------------------
    assert len(filed) == 56, f"A1 FAILED: {len(filed)} filed cells, expected 56"
    assert filed.groupby("quarter").size().eq(4).all(), "A1 FAILED: not 4 regions in every filed quarter"
    assert filed["quarter"].nunique() == 14, f"A1 FAILED: {filed['quarter'].nunique()} filed quarters"
    assert len(backout) == 16, f"A2 FAILED: {len(backout)} back-outs, expected 16"

    q4tot = backout.groupby("quarter")["revenue_musd"].sum().round(3)
    diag["q4_totals"] = {k: float(v) for k, v in q4tot.items()}
    for qq, target in Q4_TOTAL_TARGETS.items():
        got = float(q4tot.loc[qq])
        assert abs(got - target) <= 1.0, f"A3 FAILED: {qq} back-out total {got:.1f} vs {target:.1f}"

    assert (backout["revenue_musd"] > 0).all(), "A4 FAILED: a back-out is non-positive"

    kpi = pd.read_csv(SRC_KPI)[["quarter", "revenue_musd"]].dropna()
    kpi = kpi.set_index("quarter")["revenue_musd"]
    tot = spine.groupby("quarter")["revenue_musd"].sum()
    recon = []
    for qq, v in tot.items():
        if qq in kpi.index:
            recon.append({"quarter": qq, "regions_sum_musd": round(float(v), 3),
                          "consolidated_musd": float(kpi.loc[qq]),
                          "diff_musd": round(float(v) - float(kpi.loc[qq]), 3)})
    recon = pd.DataFrame(recon)
    bad = recon[recon["diff_musd"].abs() > 1.0]
    assert bad.empty, f"A5 FAILED: regions do not sum to consolidated:\n{bad}"
    diag["reconciliation_max_abs_diff_musd"] = float(recon["diff_musd"].abs().max())
    diag["reconciliation_quarters"] = int(len(recon))

    # ---------------- soft checks ----------------------------------------
    soft = []
    b_idx = backout.set_index(["quarter", "region"])["revenue_musd"]
    for (qq, region), v in b_idx.items():
        q3 = f"3Q{qq[2:]}"
        q3v = float(filed_idx.loc[(q3, region)])
        ratio = float(v) / q3v
        soft.append({"quarter": qq, "region": region, "backout_musd": float(v),
                     "q3_musd": q3v, "q4_over_q3": round(ratio, 4),
                     "within_40pct_of_q3": bool(abs(ratio - 1.0) <= 0.40)})
    soft = pd.DataFrame(soft)
    mean_ratio = soft.groupby("region")["q4_over_q3"].transform("mean")
    soft["region_mean_q4_over_q3"] = mean_ratio.round(4)
    soft["rel_dev_from_region_mean"] = ((soft["q4_over_q3"] / mean_ratio) - 1.0).round(4)
    soft["within_15pct_of_region_mean"] = soft["rel_dev_from_region_mean"].abs() <= 0.15
    diag["S1_within_40pct_of_own_q3_pass"] = int(soft["within_40pct_of_q3"].sum())
    diag["S1_fail_cells"] = soft.loc[~soft["within_40pct_of_q3"], ["quarter", "region", "q4_over_q3"]].to_dict("records")
    diag["S2_within_15pct_of_region_mean_pass"] = int(soft["within_15pct_of_region_mean"].sum())
    assert soft["within_15pct_of_region_mean"].all(), "S2 FAILED (region-relative seasonality unstable)"

    # cross-check against the repo's own regional file (independent transcription)
    rx = pd.read_csv(SRC_REGXBRL, comment="#", nrows=23)
    rx = rx[rx["quarter"].notna()].set_index("quarter")
    xdiff = []
    for _, r in spine.iterrows():
        if r["quarter"] in rx.index and r["region"] in rx.columns:
            ref = rx.loc[r["quarter"], r["region"]]
            if pd.notna(ref):
                xdiff.append(abs(float(ref) - float(r["revenue_musd"])))
    diag["crosscheck_vs_10_regional_revenue_xbrl_max_abs_musd"] = round(max(xdiff), 3) if xdiff else None
    diag["crosscheck_cells"] = len(xdiff)

    out = OUT / "L0_exact_regional_revenue.csv"
    spine.to_csv(out, index=False)
    soft.to_csv(OUT / "L0_exact_regional_revenue_seasonality_check.csv", index=False)
    recon.to_csv(OUT / "L0_exact_regional_revenue_reconciliation.csv", index=False)

    if verbose:
        print(f"[L0.1] wrote {rel(out)}  rows={len(spine)} (filed {len(filed)}, back_out {len(backout)})")
        print(f"[L0.1] Q4 totals: {diag['q4_totals']}")
        print(f"[L0.1] regions-sum-to-consolidated max |diff| = "
              f"${diag['reconciliation_max_abs_diff_musd']:.3f}M over {diag['reconciliation_quarters']} quarters")
        print(f"[L0.1] S1 (within 40% of own Q3): {diag['S1_within_40pct_of_own_q3_pass']}/16 pass "
              f"-- FAILS are structural seasonality, see note")
        print(f"[L0.1] S2 (within 15% of region mean Q4/Q3): "
              f"{diag['S2_within_15pct_of_region_mean_pass']}/16 pass")
    return spine, diag


if __name__ == "__main__":
    build()
