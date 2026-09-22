"""D2 recompute: 4Q26 nights scenarios, the RNPL / ex-NA lap and the cancellation drag.

Reads only committed artefacts. Writes only into this receipt folder.

Chain
-----
  4Q25 printed base            <- data/processed/abnb_driver_history_quarterly.csv
  team reference 4Q26 +8.90%   <- data/processed/nights_baseline_reconciliation.csv (PR #32 base)
  ex-NA lap points             <- data/processed/overnight2/D/D1_exna_4q26_gap.csv (reproduced)
  cancellation drag points     <- data/processed/overnight2/D/D1_rnpl_cohort_scenarios.csv (reproduced)
  unified module               <- data/processed/rnpl_short_audit/rnpl_nights_module.csv (read-only)
  adopted print distribution   <- .../risk-q4-nights-print-meets-street/datasets/adopted_q4_states_v2.json
  committed line               <- data/processed/h2_bridge_v3/h2_bridge_v3_rebased_lines.csv
                                  data/processed/forecast_methods/rnpl_v2/live_scenarios.csv (reproduced)
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent

# ---------------------------------------------------------------- printed bases
hist = pd.read_csv(ROOT / "data/processed/abnb_driver_history_quarterly.csv")
base = {q: float(hist.loc[hist["quarter"] == q, "nights_m"].iloc[0]) for q in ("4Q25", "1Q26", "2Q26")}

# ---------------------------------------------------------------- team reference growths
recon = pd.read_csv(ROOT / "data/processed/nights_baseline_reconciliation.csv")
pr32 = recon.loc[recon["model"].str.startswith("PR #32 NA-lap model, base")].iloc[0]
REF = {"4Q26": float(pr32["q4_yoy_pct"])}                      # 8.90, NA-only lap
mod = pd.read_csv(ROOT / "data/processed/rnpl_short_audit/rnpl_nights_module.csv")
mb = mod[(mod["scenario"] == "base")].set_index("quarter")
REF["1Q27"] = float(mb.loc["1Q27", "reference_growth_pct"])    # 8.17, exna_lap=False
REF["2Q27"] = float(mb.loc["2Q27", "reference_growth_pct"])    # 8.17, exna_lap=False

# ---------------------------------------------------------------- the lap, reproduced
gap = pd.read_csv(ROOT / "data/processed/overnight2/D/D1_exna_4q26_gap.csv")
admissible = gap[gap["consistent_with_4q25_disclosure"] == "yes"]      # 40% and 50% splits only
lap_lo = float(admissible["pts_missing_from_4q26"].min())              # 0.70 at a 40% split
lap_hi = float(admissible["pts_missing_from_4q26"].max())              # 0.88 at a 50% split
nights_lo = float(admissible["adjusted_4q26_nights_mm"].min())         # 131.7
nights_hi = float(admissible["adjusted_4q26_nights_mm"].max())         # 131.9
base_4q26_mm = round((nights_lo + nights_hi) / 2, 1)                   # 131.8, the pinned 45% midpoint
base_4q26_pct = round((base_4q26_mm / base["4Q25"] - 1) * 100, 2)      # 8.12
lap_pp = round(base_4q26_pct - REF["4Q26"], 2)                         # -0.78

# ledger-dated ex-NA lap schedule beyond 4Q26 (note 01 s2.4, D-11-safe: applied to the
# exna_lap=False reference, never on top of PR #32's flat -1.75)
LEDGER_LAP = {"1Q27": (-1.32, -1.07), "2Q27": (-1.93, -1.57)}

# ---------------------------------------------------------------- the cancellation drag
cells = pd.read_csv(ROOT / "data/processed/overnight2/D/D1_rnpl_cohort_scenarios.csv")
nz = cells[cells["4Q26_growth_delta_pts"] != 0]
drag_grid = (round(float(nz["4Q26_growth_delta_pts"].min()), 2),
             round(float(nz["4Q26_growth_delta_pts"].max()), 2))
central = cells[(cells["share_path"] == "share_central") & (cells["adr_ratio"] == "adr_plus25")
                & (cells["lead_time"] == "lead_2.2") & (cells["lead_uplift"] == "uplift_7")
                & (cells["rebook_offset"] == 0.25)]
drag_central = {r["delta_scenario"]: round(float(r["4Q26_growth_delta_pts"]), 2)
                for _, r in central.iterrows()}
drag_module_base = round(float(mb.loc["4Q26", "m3_plus_m4_tail_pts"]), 3)   # -0.542

# ---------------------------------------------------------------- scenarios
adopted = json.loads((ROOT / "docs/pitch-forecasts/questions/risk-q4-nights-print-meets-street"
                      / "datasets/adopted_q4_states_v2.json").read_text())
pct = adopted["parametric"]["percentiles"]

def mm(q: str, g: float) -> float:
    prior = {"4Q26": base["4Q25"], "1Q27": base["1Q26"], "2Q27": base["2Q26"]}[q]
    return round(prior * (1 + g / 100), 1)

rows: list[dict] = []

def add(scn, per, pt, lo, hi, src):
    rows.append({"scenario": scn, "period": per, "yoy_pct": round(pt, 2),
                 "nights_mm": mm(per, pt), "lo_pct": round(lo, 2), "lo_mm": mm(per, lo),
                 "hi_pct": round(hi, 2), "hi_mm": mm(per, hi), "source": src})

# 4Q26 -- the committed line
add("base", "4Q26", base_4q26_pct, (nights_lo / base["4Q25"] - 1) * 100,
    (float(pr32["q4_nights_mm"]) / base["4Q25"] - 1) * 100,
    "N memo 2 case B, global lap at the pinned 45% split; hi = case A (PR #32 NA-only lap)")
add("short", "4Q26", float(mb.loc["4Q26", "nights_yoy_pct"]),
    float(mod[(mod.scenario == "bear") & (mod.quarter == "4Q26")]["nights_yoy_pct"].iloc[0]),
    float(mod[(mod.scenario == "bull") & (mod.quarter == "4Q26")]["nights_yoy_pct"].iloc[0]),
    "unified RNPL module base; band = module bear/bull (lap + pull-forward + deferral + propensity)")
add("breaker", "4Q26", 10.0, 10.0, pct["90"],
    "management repeats 'low double digits' (>=10.0); hi = P90 of the adopted 4Q26 print object")

# 1Q27 / 2Q27 -- descriptive
for q in ("1Q27", "2Q27"):
    llo, lhi = LEDGER_LAP[q]
    add("base", q, REF[q] + (llo + lhi) / 2, REF[q] + llo, REF[q] + lhi,
        "exna_lap=False reference + ledger-dated ex-NA lap (note 01 s2.4); D-11 safe")
    add("short", q, float(mb.loc[q, "nights_yoy_pct"]),
        float(mod[(mod.scenario == "bear") & (mod.quarter == q)]["nights_yoy_pct"].iloc[0]),
        float(mod[(mod.scenario == "bull") & (mod.quarter == q)]["nights_yoy_pct"].iloc[0]),
        "unified RNPL module base; band = module bear/bull")
    add("breaker", q, REF[q], REF[q], REF[q],
        "the pre-registered February falsifier: the ex-NA lap is absent (PR #32 reference)")

df = pd.DataFrame(rows)
df.to_csv(OUT / "d2_scenarios.csv", index=False)

inputs = pd.DataFrame([
    {"item": "lap_pp", "scenario": "base", "period": "4Q26", "point": lap_pp,
     "unit": "pts of y/y", "note": "8.90 reference minus the adopted 8.12; = 1.75 x 0.45 split"},
    {"item": "lap_pp_range_lo", "scenario": "base", "period": "4Q26", "point": -lap_hi,
     "unit": "pts of y/y", "note": "50% ex-NA split, the harsh admissible end"},
    {"item": "lap_pp_range_hi", "scenario": "base", "period": "4Q26", "point": -lap_lo,
     "unit": "pts of y/y", "note": "40% ex-NA split, the gentle admissible end"},
    {"item": "cancel_drag_pp", "scenario": "base", "period": "4Q26", "point": 0.0,
     "unit": "pts of y/y", "note": "case B is lap-only; the drag enters the short scenario only"},
    {"item": "cancel_drag_pp", "scenario": "short", "period": "4Q26", "point": drag_module_base,
     "unit": "pts of y/y", "note": "module m3_plus_m4_tail_pts, base scenario"},
])
inputs.to_csv(OUT / "d2_model_inputs.csv", index=False)

# ---------------------------------------------------------------- match against committed
rebased = pd.read_csv(ROOT / "data/processed/h2_bridge_v3/h2_bridge_v3_rebased_lines.csv")
cm = rebased[(rebased.quarter == "4Q26") & (rebased.line == "nights_yoy_pct")].iloc[0]
live = pd.read_csv(ROOT / "data/processed/forecast_methods/rnpl_v2/live_scenarios.csv")
live_exna = float(live[(live.nights_variant == "exna") & (live.quarter == "2026Q4")]["q4_nights_m"].iloc[0])
live_theo = float(live[(live.nights_variant == "theo") & (live.quarter == "2026Q4")]["q4_nights_m"].iloc[0])

checks = pd.DataFrame([
    {"object": "4Q26 base y/y", "recomputed": base_4q26_pct, "committed": float(cm["adopted"]),
     "tolerance": 0.01, "source": "h2_bridge_v3_rebased_lines.csv adopted"},
    {"object": "4Q26 base nights mm", "recomputed": base_4q26_mm, "committed": float(cm["adopted_mm"]),
     "tolerance": 0.1, "source": "h2_bridge_v3_rebased_lines.csv adopted_mm"},
    {"object": "4Q26 base nights mm", "recomputed": base_4q26_mm, "committed": round(live_exna, 1),
     "tolerance": 0.1, "source": "rnpl_v2 live_scenarios.csv exna path"},
    {"object": "4Q26 short nights mm", "recomputed": mm("4Q26", float(mb.loc["4Q26", "nights_yoy_pct"])),
     "committed": round(live_theo, 1), "tolerance": 0.1,
     "source": "rnpl_v2 live_scenarios.csv theo path"},
    {"object": "4Q26 short nights mm", "recomputed": mm("4Q26", float(mb.loc["4Q26", "nights_yoy_pct"])),
     "committed": float(mb.loc["4Q26", "nights_mm"]), "tolerance": 0.1,
     "source": "rnpl_nights_module.csv nights_mm"},
    {"object": "4Q26 breaker nights mm", "recomputed": mm("4Q26", 10.0), "committed": 134.0,
     "tolerance": 0.2, "source": "Bloomberg MODL 4Q26 bar 134.0m (R16 threshold)"},
])
checks["abs_diff"] = (checks["recomputed"] - checks["committed"]).abs().round(4)
checks["match"] = checks["abs_diff"] <= checks["tolerance"]
checks.to_csv(OUT / "d2_match_check.csv", index=False)

print("4Q25 base nights, mm                :", base["4Q25"])
print("team reference 4Q26 y/y, %          :", REF["4Q26"])
print("admissible ex-NA lap, pts           :", f"-{lap_hi} to -{lap_lo}")
print("adopted lap at the 45% midpoint, pts:", lap_pp)
print("4Q26 base                           :", base_4q26_pct, "% ->", base_4q26_mm, "mm")
print("4Q26 cancellation drag, central cell:", drag_central)
print("4Q26 cancellation drag, grid ex-zero:", drag_grid)
print("module 4Q26 tail (m3+m4), pts       :", drag_module_base)
print()
print(df.to_string(index=False))
print()
print(checks.to_string(index=False))
print()
print("all matches:", bool(checks["match"].all()))
