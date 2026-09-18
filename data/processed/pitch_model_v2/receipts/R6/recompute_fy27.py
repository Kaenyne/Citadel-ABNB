"""R6 — recompute FY27 revenue and its band from COMMITTED CSVs only.

Reads (never writes outside this receipt folder):
  data/processed/margin_build/06_fy27_path_v2/06_revenue_path_3q26_4q27_v2b.csv   (adopted path, v2b)
  data/processed/margin_build/06_fy27_path_v2/06_annual_fy26_fy28_v2b.csv         (its own annual sums)
  data/processed/margin_build/40_line_build/40_short_case_revenue_path.csv        (short scenario)
  data/processed/margin_build/40_line_build/40_short_case_summary.csv             (short FY26/FY27 totals)
  data/processed/forecast_methods/l1_reconciliation_v2/fy27_kernel_band_v2.csv    (B3 w-band)
  data/processed/rnpl_short_audit/kappa_anatomy_and_lambda_refit.csv              (lambda re-fit)
  data/processed/rnpl_short_audit/turns_vs_street_and_w_band.csv                  (lap-aware band)

Run: PYTHONPATH=analysis/src python3 data/processed/pitch_model_v2/receipts/R6/recompute_fy27.py
"""
from __future__ import annotations
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
P06 = ROOT / "data/processed/margin_build/06_fy27_path_v2"
P40 = ROOT / "data/processed/margin_build/40_line_build"
PB3 = ROOT / "data/processed/forecast_methods/l1_reconciliation_v2"
PAU = ROOT / "data/processed/rnpl_short_audit"
OUT = Path(__file__).resolve().parent

FY27Q = ["1Q27", "2Q27", "3Q27", "4Q27"]
H2_26 = ["3Q26", "4Q26"]
H1_26_PRINTED = 2678.0 + 3608.0   # 1Q26 + 2Q26 printed, 10-Q; = 6286.0

rows = []
def add(**kw): rows.append(kw)

# ---------- 1. the adopted path (06 v2b), scenarios bear/base/bull ----------
lng = pd.read_csv(P06 / "06_revenue_path_3q26_4q27_v2b.csv")
rev = (lng[lng.line == "revenue_musd"]
       .pivot_table(index="quarter", columns="scenario", values="value", aggfunc="first"))
ann = pd.read_csv(P06 / "06_annual_fy26_fy28_v2b.csv")

print("=" * 88)
print("1. FY27 recomputed as the SUM of the four committed 2027 quarters (06 v2b)")
print("=" * 88)
for sc in ["base", "bear", "bull"]:
    fy27 = float(rev.loc[FY27Q, sc].sum())
    fy26 = H1_26_PRINTED + float(rev.loc[H2_26, sc].sum())
    a = ann[(ann.period == "FY27") & (ann.scenario == sc)]
    a26 = ann[(ann.period == "FY26") & (ann.scenario == sc)]
    fy27_pub, g_pub = float(a.revenue_musd.iloc[0]), float(a.revenue_musd_yoy_pct.iloc[0])
    fy26_pub = float(a26.revenue_musd.iloc[0])
    g_own = 100.0 * (fy27 / fy26 - 1.0)
    print(f"{sc:5s} FY26 sum {fy26:10.4f} (published {fy26_pub:10.4f}, d {fy26-fy26_pub:+.4f})"
          f" | FY27 sum {fy27:10.4f} (published {fy27_pub:10.4f}, d {fy27-fy27_pub:+.4f})"
          f" | y/y own-base {g_own:7.4f}% (published {g_pub:7.4f}%, d {g_own-g_pub:+.4f}pp)")
    add(item="fy27_revenue_musd", scenario=sc, period="FY27", recomputed=fy27,
        committed=fy27_pub, diff=fy27 - fy27_pub, unit="USD m", source="06 v2b quarterly sum")
    add(item="fy27_revenue_yoy_pct", scenario=sc, period="FY27", recomputed=g_own,
        committed=g_pub, diff=g_own - g_pub, unit="pct", source="06 v2b, own FY26")
    for q in FY27Q:
        add(item="revenue_musd", scenario=sc, period=q, recomputed=float(rev.loc[q, sc]),
            committed=float(rev.loc[q, sc]), diff=0.0, unit="USD m", source="06 v2b")

# quarterly y/y straight out of the path file
yoy = (lng[lng.line == "revenue_yoy_pct"]
       .pivot_table(index="quarter", columns="scenario", values="value", aggfunc="first"))
print("\nquarterly revenue_yoy_pct as the path carries them:")
print(yoy.loc[H2_26 + FY27Q].round(4).to_string())

# ---------- 2. the short case ----------
print("\n" + "=" * 88)
print("2. Short case (40_line_build) — FY27 sum and the two possible y/y bases")
print("=" * 88)
sh = pd.read_csv(P40 / "40_short_case_revenue_path.csv").set_index("quarter")
sh_fy27 = float(sh.loc[FY27Q, "revenue_musd"].sum())
sh_fy26 = H1_26_PRINTED + float(sh.loc[H2_26, "revenue_musd"].sum())
summ = pd.read_csv(P40 / "40_short_case_summary.csv").iloc[0]
base_fy26 = float(ann[(ann.period == "FY26") & (ann.scenario == "base")].revenue_musd.iloc[0])
g_own = 100.0 * (sh_fy27 / sh_fy26 - 1.0)
g_vs_base = 100.0 * (sh_fy27 / base_fy26 - 1.0)
print(f"short FY27 sum      {sh_fy27:10.4f}  (40_short_case_summary fy27_revenue {float(summ.fy27_revenue):10.4f},"
      f" d {sh_fy27-float(summ.fy27_revenue):+.4f})")
print(f"short FY26 sum      {sh_fy26:10.4f}  (40_short_case_summary fy26_revenue {float(summ.fy26_revenue):10.4f},"
      f" d {sh_fy26-float(summ.fy26_revenue):+.4f})")
print(f"y/y on the SHORT's OWN FY26   : {g_own:7.4f}%")
print(f"y/y on the BASE FY26 {base_fy26:.4f} : {g_vs_base:7.4f}%   <-- this is the published '+4.5%'")
print(f"gap between the two bases     : {g_own-g_vs_base:7.4f}pp")
add(item="fy27_revenue_musd", scenario="short", period="FY27", recomputed=sh_fy27,
    committed=float(summ.fy27_revenue), diff=sh_fy27 - float(summ.fy27_revenue), unit="USD m",
    source="40_short_case_revenue_path quarterly sum")
add(item="fy27_revenue_yoy_pct_own_base", scenario="short", period="FY27", recomputed=g_own,
    committed=float("nan"), diff=float("nan"), unit="pct", source="short FY27 / short FY26")
add(item="fy27_revenue_yoy_pct_vs_base_fy26", scenario="short", period="FY27", recomputed=g_vs_base,
    committed=4.5, diff=g_vs_base - 4.5, unit="pct", source="short FY27 / base FY26 (the published +4.5%)")
for q in FY27Q:
    v = float(sh.loc[q, "revenue_musd"])
    add(item="revenue_musd", scenario="short", period=q, recomputed=v, committed=v, diff=0.0,
        unit="USD m", source="40_short_case_revenue_path")

# short quarterly y/y needs prior-year quarters: 1Q26/2Q26 printed, 3Q26/4Q26 short-case
prior = {"1Q27": 2678.0, "2Q27": 3608.0,
         "3Q27": float(sh.loc["3Q26", "revenue_musd"]), "4Q27": float(sh.loc["4Q26", "revenue_musd"])}
print("\nshort-case quarterly y/y, each quarter on the SHORT's own prior-year quarter:")
for q in FY27Q:
    g = 100.0 * (float(sh.loc[q, "revenue_musd"]) / prior[q] - 1.0)
    print(f"  {q}  {float(sh.loc[q,'revenue_musd']):9.4f}  on {prior[q]:9.4f}  -> {g:7.4f}%")
    add(item="revenue_yoy_pct", scenario="short", period=q, recomputed=g, committed=float("nan"),
        diff=float("nan"), unit="pct", source="short quarterly / short prior-year quarter")

# ---------- 3. the B3 band ----------
print("\n" + "=" * 88)
print("3. B3 / l1-reconciliation-v2 kernel-weight band (the pre-registered band)")
print("=" * 88)
b3 = pd.read_csv(PB3 / "fy27_kernel_band_v2.csv")
print(b3[["kernel_w", "fy26_revenue_musd", "fy27_revenue_musd", "fy27_growth_pct",
          "gbv_growth_pct", "kappa_pct", "sd_growth_pp"]].round(4).to_string(index=False))
lo, hi = b3.fy27_growth_pct.min(), b3.fy27_growth_pct.max()
print(f"band: {lo:.4f}% to {hi:.4f}%  (span {hi-lo:.4f}pp)")
add(item="fy27_band_low_pct", scenario="base", period="FY27", recomputed=float(lo), committed=9.18,
    diff=float(lo) - 9.18, unit="pct", source="fy27_kernel_band_v2.csv, w=0.33")
add(item="fy27_band_high_pct", scenario="base", period="FY27", recomputed=float(hi), committed=11.52,
    diff=float(hi) - 11.52, unit="pct", source="fy27_kernel_band_v2.csv, w=2/3")

# ---------- 4. what the later audit does to that band ----------
print("\n" + "=" * 88)
print("4. Later audit (docs/rnpl-short-audit 02): lambda re-fit, and the lap-aware band")
print("=" * 88)
k = pd.read_csv(PAU / "kappa_anatomy_and_lambda_refit.csv")
for conv, g in k.groupby("lambda_convention"):
    print(f"  {conv:45s} span {g.fy27_growth_pct.min():7.4f}% .. {g.fy27_growth_pct.max():7.4f}%"
          f"  = {g.fy27_growth_pct.max()-g.fy27_growth_pct.min():.4f}pp")
    add(item="fy27_growth_span_pp", scenario="base", period="FY27",
        recomputed=float(g.fy27_growth_pct.max() - g.fy27_growth_pct.min()), committed=float("nan"),
        diff=float("nan"), unit="pp", source=f"kappa_anatomy_and_lambda_refit.csv [{conv}]")
t = pd.read_csv(PAU / "turns_vs_street_and_w_band.csv")
lap = t[t.case == "B3 at w = 2/3 + RNPL lap band (global .. NA-only)"].iloc[0]
print(f"  B3 at w=2/3 + RNPL lap band: {lap.our_lo_pct:.4f}% .. {lap.our_hi_pct:.4f}%"
      f"  = {lap.our_hi_pct-lap.our_lo_pct:.4f}pp")
add(item="fy27_growth_lapaware_low_pct", scenario="base", period="FY27", recomputed=float(lap.our_lo_pct),
    committed=float("nan"), diff=float("nan"), unit="pct", source="turns_vs_street_and_w_band.csv")
add(item="fy27_growth_lapaware_high_pct", scenario="base", period="FY27", recomputed=float(lap.our_hi_pct),
    committed=float("nan"), diff=float("nan"), unit="pct", source="turns_vs_street_and_w_band.csv")

pd.DataFrame(rows).to_csv(OUT / "recompute_fy27.csv", index=False)
print(f"\nwrote {OUT / 'recompute_fy27.csv'}  ({len(rows)} rows)")
