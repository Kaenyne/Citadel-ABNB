"""N2 - nights line v2: rebuild the disclosed-mechanism decomposition and its band.

Read-only on every input. Writes three files:
  receipts/N2/n2_mechanism_quarterly.csv   the quarter-by-quarter mechanism, 3Q25-4Q27
  receipts/N2/n2_band.csv                  low/base/high per quarter + one-at-a-time sensitivities
  docs/pitch-model-v2/lines/figures/nights_constellation_3q26.csv   the 3Q26 cross-check constellation

Nothing here is a new regression. Every parameter is either (a) a disclosure, (b) a value already
committed in this repo, or (c) an explicitly named assumption with a range.

Run:  PYTHONPATH=analysis/src python3 data/processed/pitch_model_v2/receipts/N2/n2_mechanism.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
OUT = ROOT / "data/processed/pitch_model_v2/receipts/N2"
FIG = ROOT / "docs/pitch-model-v2/lines/figures"

# ---------------------------------------------------------------- inputs (all committed files)
hist = pd.read_csv(ROOT / "data/processed/abnb_driver_history_quarterly.csv")
hist["q_label"] = hist.apply(lambda r: f"{int(r.q)}Q{int(r.year) % 100:02d}", axis=1)
H = hist.set_index("q_label")

panel = pd.read_csv(ROOT / "data/processed/overnight/10_regional_panel_quarterly.csv").set_index("quarter")
ws10 = pd.read_csv(ROOT / "data/processed/overnight/10_regional_forecast.csv")
nq_na = pd.read_csv(ROOT / "data/processed/nights_quarterly_na.csv")
nb06 = pd.read_csv(ROOT / "data/processed/margin_build/06_fy27_path_v2/06_nights_build.csv")

def ws10_cell(period, region, scen, col="nights_yoy_pct"):
    r = ws10[(ws10.period == period) & (ws10.region == region) & (ws10.scenario == scen)].iloc[0]
    return float(r[col])

# ---------------------------------------------------------------- mechanism parameters
U26 = 3.31          # choice-model NA underlying, 2026 (nights_quarterly_na.csv underlying_pts)
U27 = 2.31          # same, 2027
FY25_NA = 2.6       # 10-K FY25 NA nights 158/154mm -> +2.6%; the pre-product NA run rate
NA_OBS_3Q25 = 5.0   # 3Q25 letter bucket "mid-single digit growth" -> WS10 midpoint (lo 4 / hi 6)
NA_OBS_1Q26 = 8.0   # 1Q26 letter bucket "high-single digit growth" -> WS10 midpoint (lo 7 / hi 9)
GLOBAL_PTS = 3.0    # Mertz 1Q26 call, ledger D032: "approximately three points of nights booked growth"
FEE_SPLIT = 0.45    # ex-NA fee+cancellation share of the ex-NA bundle; WS-D pinned 40-50%, midpoint
PHASE_1Q27 = 0.40   # ex-NA RNPL lap phase-in for 1Q27 (live 17 Feb-4 Mar 2026)
ME_1Q27 = 1.0       # Middle East base effect lapping in 1Q27 (1Q26 letter: ~100bp headwind)
WC_2Q27 = -0.5      # World Cup booking-quarter lap, 2Q27; never sized by management
JULY_EXP = 0.0      # July 2026 RNPL booking-type expansion (ledger D044), carried at zero in base

S = {"3Q26": 0.288, "4Q26": 0.282, "1Q27": 0.291, "2Q27": 0.291, "3Q27": 0.288, "4Q27": 0.282}
PRIOR_LEVEL = {"3Q26": 133.6, "4Q26": 121.9, "1Q27": 156.2, "2Q27": 148.3}   # printed


def fit(u26=U26, na3q25=NA_OBS_3Q25, na1q26=NA_OBS_1Q26):
    """PR #32's two fitted NA product parameters, re-derived."""
    rnpl = na3q25 - FY25_NA
    t1 = (na1q26 - u26) - rnpl
    return rnpl, t1


def exna_ws10(period, scen="base"):
    tot = ws10_cell(period, "TOTAL", scen)
    na = ws10_cell(period, "na", scen)
    s = ws10_cell(period, "na", scen, "nights_share_est_pct") / 100
    return (tot - s * na) / (1 - s)


def exna_2027(scen="base"):
    """Linear decay from the WS10 4Q26 ex-NA rate whose four-quarter mean equals WS10's FY27 rate."""
    x4, x27 = exna_ws10("4Q26", scen), exna_ws10("FY27", scen)
    d = (x4 - x27) / 2.5
    return {q: x4 - (k + 1) * d for k, q in enumerate(["1Q27", "2Q27", "3Q27", "4Q27"])}


def mechanism(u26=U26, u27=U27, na3q25=NA_OBS_3Q25, na1q26=NA_OBS_1Q26, global_pts=GLOBAL_PTS,
              fee_split=FEE_SPLIT, phase=PHASE_1Q27, me=ME_1Q27, wc=WC_2Q27,
              july=JULY_EXP, us_lap_frac=0.0):
    """Return {quarter: dict of legs and the total}.

    us_lap_frac is the share of the US RNPL lift that is NOT yet lapped in 3Q26 (partiality).
    july is points of total nights from the July 2026 eligibility expansion, live 3Q26-2Q27.
    """
    rnpl_na, t1_na = fit(u26, na3q25, na1q26)
    peak_na = rnpl_na + t1_na
    exna_bundle = global_pts - S["3Q26"] * peak_na           # points of TOTAL nights
    lap_fee = fee_split * exna_bundle
    lap_rnpl_full = (1 - fee_split) * exna_bundle
    x27 = exna_2027()
    out = {}

    # ---- 3Q26: WS10 total, NA replaced by the mechanism's NA; nothing lapped ex-NA yet
    s = S["3Q26"]
    na = u26 + t1_na + us_lap_frac * rnpl_na               # RNPL lapped (fully, unless partial)
    ex = exna_ws10("3Q26")
    out["3Q26"] = dict(s=s, na=na, exna=ex, na_bundle=t1_na + us_lap_frac * rnpl_na,
                       exna_bundle_live=exna_bundle, lap_fee=0.0, lap_rnpl=0.0,
                       event=0.0, july=july,
                       total=s * na + (1 - s) * ex + july)

    # ---- 4Q26: the global fee + cancellation legs lap; ex-NA RNPL still in window
    s = S["4Q26"]
    na = u26                                               # the whole NA bundle has lapped by 4Q26
    ex = exna_ws10("4Q26")
    out["4Q26"] = dict(s=s, na=na, exna=ex, na_bundle=0.0,
                       exna_bundle_live=exna_bundle - lap_fee, lap_fee=-lap_fee, lap_rnpl=0.0,
                       event=0.0, july=july,
                       total=s * na + (1 - s) * ex - lap_fee + july)

    # ---- 2027
    for q, ph, ev, jl in [("1Q27", phase, me, july), ("2Q27", 1.0, wc, july),
                          ("3Q27", 1.0, 0.0, 0.0), ("4Q27", 1.0, 0.0, 0.0)]:
        s = S[q]
        na = u27
        ex = x27[q]
        lr = ph * lap_rnpl_full
        out[q] = dict(s=s, na=na, exna=ex, na_bundle=0.0,
                      exna_bundle_live=exna_bundle - lap_fee - lr,
                      lap_fee=-lap_fee, lap_rnpl=-lr, event=ev, july=jl,
                      total=s * na + (1 - s) * ex - lap_fee - lr + ev + jl)
    return out, dict(rnpl_na=rnpl_na, t1_na=t1_na, peak_na=peak_na,
                     exna_bundle=exna_bundle, lap_fee=lap_fee, lap_rnpl_full=lap_rnpl_full)


def levels(tot: dict[str, float]) -> dict[str, float]:
    lv = {}
    for q in ["3Q26", "4Q26", "1Q27", "2Q27"]:
        lv[q] = PRIOR_LEVEL[q] * (1 + tot[q] / 100)
    lv["3Q27"] = lv["3Q26"] * (1 + tot["3Q27"] / 100)
    lv["4Q27"] = lv["4Q26"] * (1 + tot["4Q27"] / 100)
    return lv


# ---------------------------------------------------------------- base run
base, fitted = mechanism()
tot_base = {q: v["total"] for q, v in base.items()}
# The committed base path uses the growth rates as the repo rounds and decides them:
#   3Q26 9.89 (nights_quarterly.py rounds its own 9.887; DEC-0028 adopts the mechanism)
#   4Q26 8.12 (DEC-0019; the mechanism's own exit is 8.157 - the gap is PR #32's rounding
#              of 132.7/121.9 = 8.859 to 8.9, recorded in 06_pass_line.csv test 6)
#   2027 the 06 build's own three-decimal rates, which this script reproduces exactly
TOT_COMMITTED = {"3Q26": 9.89, "4Q26": 8.12, "1Q27": round(tot_base["1Q27"], 3),
                 "2Q27": round(tot_base["2Q27"], 3), "3Q27": round(tot_base["3Q27"], 3),
                 "4Q27": round(tot_base["4Q27"], 3)}
lv_base = levels(TOT_COMMITTED)

rows = []
# history 3Q25-2Q26 from the WS10 regional panel (letter buckets) and the printed KPI
for q in ["3Q25", "4Q25", "1Q26", "2Q26"]:
    p = panel.loc[q]
    rnpl_na, t1_na = fitted["rnpl_na"], fitted["t1_na"]
    na_bundle = {"3Q25": rnpl_na, "4Q25": rnpl_na, "1Q26": rnpl_na + t1_na, "2Q26": rnpl_na + t1_na}[q]
    exna_b = {"3Q25": 0.0, "4Q25": FEE_SPLIT * fitted["exna_bundle"],
              "1Q26": fitted["exna_bundle"], "2Q26": fitted["exna_bundle"]}[q]
    s = float(p.na_nights_share_est_pct) / 100
    rows.append(dict(period=q, basis="printed", na_share=round(s, 4),
                     na_yoy=float(p.na_nights_yoy_mid), na_yoy_lo=float(p.na_nights_yoy_lo),
                     na_yoy_hi=float(p.na_nights_yoy_hi),
                     na_underlying=round(float(p.na_nights_yoy_mid) - na_bundle, 3),
                     exna_yoy=float(p.ex_na_nights_yoy_est_pct),
                     na_bundle_pts_of_na=round(na_bundle, 3),
                     exna_bundle_pts_of_total=round(exna_b, 3),
                     lap_fee=0.0, lap_rnpl=0.0, event=0.0, july=0.0,
                     calibration_resid=float(p.residual_vs_total_pp),
                     total_yoy=float(H.loc[q, "nights_m_yoy_pct"]),
                     total_yoy_committed=float(H.loc[q, "nights_m_yoy_pct"]),
                     level_m=float(H.loc[q, "nights_m"])))
for q in ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]:
    v = base[q]
    rows.append(dict(period=q, basis="mechanism", na_share=round(v["s"], 4),
                     na_yoy=round(v["na"], 3), na_yoy_lo=None, na_yoy_hi=None,
                     na_underlying=round(U26 if q.endswith("26") else U27, 3),
                     exna_yoy=round(v["exna"], 3),
                     na_bundle_pts_of_na=round(v["na_bundle"], 3),
                     exna_bundle_pts_of_total=round(v["exna_bundle_live"], 3),
                     lap_fee=round(v["lap_fee"], 3), lap_rnpl=round(v["lap_rnpl"], 3),
                     event=v["event"], july=v["july"], calibration_resid=None,
                     total_yoy=round(v["total"], 3), total_yoy_committed=TOT_COMMITTED[q],
                     level_m=round(lv_base[q], 3)))
mech = pd.DataFrame(rows)
mech.to_csv(OUT / "n2_mechanism_quarterly.csv", index=False)

# ---------------------------------------------------------------- the band
# Each named parameter at its adverse / favourable end. "lo"/"hi" are the effect on nights growth.
PAR = {
    # name: (lo_kwargs, hi_kwargs, source)
    "na_3q25_bucket": (dict(na3q25=6.0), dict(na3q25=4.0),
                       "3Q25 letter bucket mid-single digit; WS10 lo 4.0 / hi 6.0"),
    "na_1q26_bucket": (dict(na1q26=7.0), dict(na1q26=9.0),
                       "1Q26 letter bucket high-single digit; WS10 lo 7.0 / hi 9.0"),
    "global_bundle_pts": (dict(global_pts=3.0), dict(global_pts=2.0),
                          "D032 approximately three points (1Q26); D014 over 200bp (4Q25)"),
    "fee_split": (dict(fee_split=0.50), dict(fee_split=0.40),
                  "D1_exna_4q26_gap.csv: 40-50% pinned by the 4Q25 over-200bp disclosure"),
    "phase_1q27": (dict(phase=0.50), dict(phase=0.30),
                   "ex-NA RNPL live 17 Feb-4 Mar 2026; 0.40 is judgement, +/-0.10 carried"),
    "us_lap_partiality": (dict(us_lap_frac=0.0), dict(us_lap_frac=6.0 / 13.0),
                          "letter says August 2025 launch (about 6 of 13 weeks); call says beginning of Q3"),
    "july_expansion": (dict(july=0.0), dict(july=0.3),
                       "ledger D044, unsized; module carries +0.1 to +0.3 pts"),
    "events": (dict(me=0.0, wc=-0.75), dict(me=1.0, wc=0.0),
               "1Q26 letter ~100bp Middle East; World Cup never sized (06_assumptions bear/bull)"),
}
QS = ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]
sens = []
for name, (lo_kw, hi_kw, src) in PAR.items():
    mlo, _ = mechanism(**lo_kw)
    mhi, _ = mechanism(**hi_kw)
    for q in QS:
        sens.append(dict(parameter=name, quarter=q,
                         base_pts=round(tot_base[q], 3),
                         lo_pts=round(mlo[q]["total"], 3), hi_pts=round(mhi[q]["total"], 3),
                         swing_lo_pp=round(mlo[q]["total"] - tot_base[q], 3),
                         swing_hi_pp=round(mhi[q]["total"] - tot_base[q], 3), source=src))
sens = pd.DataFrame(sens)

# full envelope: every parameter at its adverse end together, then at its favourable end together
lo_all, hi_all = {}, {}
for _, (lo_kw, hi_kw, _s) in PAR.items():
    lo_all.update(lo_kw)
    hi_all.update(hi_kw)
menv_lo, _ = mechanism(**lo_all)
menv_hi, _ = mechanism(**hi_all)
lv_lo = levels({q: v["total"] for q, v in menv_lo.items()})
lv_hi = levels({q: v["total"] for q, v in menv_hi.items()})

env = []
for q in QS:
    env.append(dict(parameter="ENVELOPE_all_parameters", quarter=q,
                    base_pts=round(tot_base[q], 3),
                    lo_pts=round(menv_lo[q]["total"], 3), hi_pts=round(menv_hi[q]["total"], 3),
                    swing_lo_pp=round(menv_lo[q]["total"] - tot_base[q], 3),
                    swing_hi_pp=round(menv_hi[q]["total"] - tot_base[q], 3),
                    source="all eight parameters moved together"))
    env.append(dict(parameter="ENVELOPE_levels_m", quarter=q, base_pts=round(lv_base[q], 2),
                    lo_pts=round(lv_lo[q], 2), hi_pts=round(lv_hi[q], 2),
                    swing_lo_pp=round(lv_lo[q] - lv_base[q], 2),
                    swing_hi_pp=round(lv_hi[q] - lv_base[q], 2), source="levels, m"))
band = pd.concat([sens, pd.DataFrame(env)], ignore_index=True)
band.to_csv(OUT / "n2_band.csv", index=False)

fy27_base = sum(lv_base[q] for q in ["1Q27", "2Q27", "3Q27", "4Q27"])
fy27_lo = sum(lv_lo[q] for q in ["1Q27", "2Q27", "3Q27", "4Q27"])
fy27_hi = sum(lv_hi[q] for q in ["1Q27", "2Q27", "3Q27", "4Q27"])
fy26_base = 156.2 + 148.3 + lv_base["3Q26"] + lv_base["4Q26"]
fy26_lo = 156.2 + 148.3 + lv_lo["3Q26"] + lv_lo["4Q26"]
fy26_hi = 156.2 + 148.3 + lv_hi["3Q26"] + lv_hi["4Q26"]

# ---------------------------------------------------------------- the 3Q26 constellation
g = pd.read_csv(ROOT / "data/processed/q3nowcast/G/G_nowcast_3q26_observable.csv")
gn = g[g.target == "nights_m_yoy_pct"]
BASE_3Q25 = 133.6
con = [
    dict(source="mechanism (this file, base)", read_yoy_pct=round(tot_base["3Q26"], 3),
         level_m=round(lv_base["3Q26"], 2),
         method="disclosed regional buckets + fitted NA product legs, US RNPL lapped in full, July expansion at zero",
         window="n/a - forward build, no walk-forward window exists", ratio_vs_naive="",
         date="2026-09-18", independent_of_mechanism="no"),
    dict(source="reviews stays index, raw read", read_yoy_pct=10.041, level_m=147.01,
         method="OLS of printed nights y/y on the review-date index, 14 quarters, slope 0.3221",
         window="fit 1Q23-2Q26", ratio_vs_naive=0.683, date="2026-09-14",
         independent_of_mechanism="yes"),
    dict(source="reviews stays index, W2 bias-corrected", read_yoy_pct=9.523, level_m=146.32,
         method="raw read less the index's own +0.518pp W2 walk-forward mean error",
         window="W2 scored 1Q24-2Q26, n 10", ratio_vs_naive=0.683, date="2026-09-14",
         independent_of_mechanism="yes"),
    dict(source="reviews stays index, W1 bias-corrected", read_yoy_pct=8.409, level_m=144.84,
         method="raw read less the index's +1.632pp W1 walk-forward mean error",
         window="W1 scored 1Q23-2Q26, n 14", ratio_vs_naive=0.837, date="2026-09-14",
         independent_of_mechanism="yes"),
    dict(source="external stack median (12 series)", read_yoy_pct=9.232, level_m=145.93,
         method="median of 12 in-sample macro fits targeting nights y/y",
         window="fit 2023Q1-2026Q2", ratio_vs_naive="", date="2026-09-06",
         independent_of_mechanism="yes"),
]
for feat, label in [("ntto_overseas_qtd1m", "NTTO I-94 overseas arrivals, qtd 1 month"),
                    ("tsa_qtd72", "TSA throughput, qtd"),
                    ("es_hotel_nights_foreign_qtd1m", "INE Spain hotel nights, foreign"),
                    ("cpi_lodging_sa_qtd", "CPI lodging away from home, SA")]:
    r = gn[(gn.feature == feat) & (gn.window == "2023Q1..2026Q2")].iloc[0]
    con.append(dict(source=label, read_yoy_pct=round(float(r.pred_3q26), 3),
                    level_m=round(BASE_3Q25 * (1 + float(r.pred_3q26) / 100), 2),
                    method="single-series OLS nowcast, in-sample fit on the full window",
                    window=str(r.window), ratio_vs_naive=round(float(r.wf_ratio_vs_naive), 3),
                    date="2026-09-06", independent_of_mechanism="yes"))
con += [
    dict(source="hotel RevPAR (MAR/HLT) -> nights", read_yoy_pct="", level_m="",
         method="peer-print read-through; best external feature on this KPI, no 3Q26 point until 4 Nov",
         window="W2 n 10 / W1 n 14", ratio_vs_naive=0.68, date="2026-09-06",
         independent_of_mechanism="yes"),
    dict(source="BEA hotels nominal -> nights", read_yoy_pct="", level_m="",
         method="monthly BEA accommodation spend read-through",
         window="W2 n 10", ratio_vs_naive=0.71, date="2026-09-06",
         independent_of_mechanism="yes"),
    dict(source="unified RNPL cohort module, base", read_yoy_pct=9.49, level_m=146.3,
         method="the 9.89 mechanism reference less M1 +0.304, M2 -0.113, M3 -0.019, M4 -0.568",
         window="n/a - forward build", ratio_vs_naive="", date="2026-09-16",
         independent_of_mechanism="no"),
    dict(source="H1-H2 seasonal bridge, pattern only", read_yoy_pct=9.492, level_m=146.3,
         method="2023-25 seasonal transition applied to 2026 H1; no lap, no event",
         window="n/a - pattern", ratio_vs_naive="", date="2026-09-12",
         independent_of_mechanism="yes"),
    dict(source="Street (Bloomberg MODL)", read_yoy_pct=11.527, level_m=149.0,
         method="mean of 28 estimates; low 147.0 high 151.0", window="n/a",
         ratio_vs_naive="", date="2026-09-12", independent_of_mechanism="yes"),
    dict(source="management guide, 2Q26 letter", read_yoy_pct=10.0, level_m=147.0,
         method="low double-digit nights bucket; the >=10.0% mapping is ours, not a company range",
         window="n/a", ratio_vs_naive="", date="2026-08-06", independent_of_mechanism="yes"),
]
FIG.mkdir(parents=True, exist_ok=True)
pd.DataFrame(con).to_csv(FIG / "nights_constellation_3q26.csv", index=False)

# ---------------------------------------------------------------- report
print("Fitted NA product legs (re-derived):")
print(f"  RNPL          {fitted['rnpl_na']:+.2f} pts of NA nights   (3Q25 bucket {NA_OBS_3Q25} - FY25 NA {FY25_NA})")
print(f"  fee + cancel  {fitted['t1_na']:+.2f} pts of NA nights   (1Q26 bucket {NA_OBS_1Q26} - underlying {U26} - RNPL)")
print(f"  peak NA bundle {fitted['peak_na']:+.2f};  ex-NA bundle {fitted['exna_bundle']:+.3f} pts of total nights")
print(f"  lap_fee {fitted['lap_fee']:.3f}   lap_rnpl(full) {fitted['lap_rnpl_full']:.3f}")
print("\nex-NA WS10 rates: 3Q26 %.3f  4Q26 %.3f  FY27 %.3f" %
      (exna_ws10("3Q26"), exna_ws10("4Q26"), exna_ws10("FY27")))
print("2027 ex-NA phased:", {k: round(v, 3) for k, v in exna_2027().items()})
print("\nMechanism base, y/y and level:")
for q in QS:
    print(f"  {q}  {tot_base[q]:+7.3f}% (committed {TOT_COMMITTED[q]:+6.3f})  {lv_base[q]:7.2f}m    "
          f"[{menv_lo[q]['total']:+.3f} .. {menv_hi[q]['total']:+.3f}]  "
          f"[{lv_lo[q]:.2f} .. {lv_hi[q]:.2f}]")
print(f"\nFY26  {fy26_base:.3f}m  [{fy26_lo:.2f} .. {fy26_hi:.2f}]")
print(f"FY27  {fy27_base:.3f}m  {100*(fy27_base/fy26_base-1):+.3f}%   "
      f"low {fy27_lo:.2f}m {100*(fy27_lo/fy26_lo-1):+.3f}%   "
      f"high {fy27_hi:.2f}m {100*(fy27_hi/fy26_hi-1):+.3f}%")
print("\nOne-at-a-time swing on 3Q26 / 4Q26 / FY27-relevant quarters (pp):")
for name in PAR:
    s3 = sens[(sens.parameter == name) & (sens.quarter == "3Q26")].iloc[0]
    s4 = sens[(sens.parameter == name) & (sens.quarter == "4Q26")].iloc[0]
    s1 = sens[(sens.parameter == name) & (sens.quarter == "1Q27")].iloc[0]
    print(f"  {name:22} 3Q26 {s3.swing_lo_pp:+.3f}/{s3.swing_hi_pp:+.3f}   "
          f"4Q26 {s4.swing_lo_pp:+.3f}/{s4.swing_hi_pp:+.3f}   "
          f"1Q27 {s1.swing_lo_pp:+.3f}/{s1.swing_hi_pp:+.3f}")
print("\nCross-check against committed files:")
nq = nq_na[(nq_na.scenario == "base")].set_index("quarter")
print(f"  nights_quarterly_na 3Q26 NA {float(nq.loc['3Q26','na_nights_yoy_pct']):.2f} vs mechanism {base['3Q26']['na']:.2f}")
b06 = nb06[nb06.scenario == "base"].set_index("quarter")
for q in ["1Q27", "2Q27", "3Q27", "4Q27"]:
    print(f"  06_nights_build {q} {float(b06.loc[q,'total_nights_yoy_pct']):.3f} vs mechanism {tot_base[q]:.3f}")
print(f"\nwrote {OUT/'n2_mechanism_quarterly.csv'}")
print(f"wrote {OUT/'n2_band.csv'}")
print(f"wrote {FIG/'nights_constellation_3q26.csv'}")
