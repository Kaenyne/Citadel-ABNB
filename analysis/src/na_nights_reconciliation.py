"""Reconcile the choice-probability nights model against the team's North America nights path.

THE CONTRADICTION
-----------------
Two documents in this repo point opposite ways at the same quarters and neither cites the other:

  research/blotnick_framework_abnb.md  §1  the guide is a floor. 19-for-19 revenue beats, 15 of 19
                                           above the top of the range, mean beat +2.54%. Model
                                           next-quarter revenue at the midpoint x 1.018.
  research/notes/choice_nights_driver.md   NA at the team's pace "needs share gains or category
                                           adoption above the 2025 exit rate". The model gets
                                           US +3.3% for 2026 against WS10's NA +7%.

This script does not argue. It inverts the choice model: for each lever, what value would be
REQUIRED to reach the team's NA path, holding everything else at base? Then each required value is
put next to the evidence for that lever, so the disagreement resolves into a list of things that
would have to be true rather than a difference of opinion.

TARGETS (model/assumptions.md, WS10 regional build -> 10_regional_forecast.csv)
  NA nights growth   3Q26/4Q26   bear 5/4   base 7/7   bull 9/9
  NA nights growth   FY27        bear 3     base 6     bull 8
The choice model forecasts the U.S. (145.4mm = 92% of NA's 158mm). NA-ex-US is ~12.6mm and the
global build already assumes it tracks the U.S., so US-vs-NA is treated as comparable here and the
residual is flagged rather than modelled.

Run:  py -3.13 analysis/src/na_nights_reconciliation.py
Out:  data/processed/na_nights_reconciliation.csv       one row per lever x target
      data/processed/na_nights_decomposition.csv        the base growth decomposition
"""
from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import pandas as pd

import choice_nights_driver as cnd

ROOT = Path(__file__).resolve().parents[2]
OUT_REQ = ROOT / "data/processed/na_nights_reconciliation.csv"
OUT_DEC = ROOT / "data/processed/na_nights_decomposition.csv"

SEG = cnd.SEG
# WS10 regional build, NA nights growth
TARGETS = {2026: {"bear": 0.045, "base": 0.07, "bull": 0.09},   # 3Q26/4Q26 5/4, 7/7, 9/9 -> FY-ish
           2027: {"bear": 0.03, "base": 0.06, "bull": 0.08}}


def growth_for(year: int, **over) -> float:
    """Run the model with `over` applied and return that year's U.S. nights growth."""
    kw = dict(switch_rate=cnd.SWITCH_RATE,
              abnb_adr=dict(cnd.ABNB_ADR_GROWTH), hotel_adr=dict(cnd.HOTEL_ADR_GROWTH),
              mix=dict(cnd.MIX_DRIFT), mkt=dict(cnd.MARKET_GROWTH),
              shift=dict(cnd.PRODUCT_SHIFT), cat=dict(cnd.CATEGORY_GROWTH))
    contestable = over.pop("contestable", None)
    for k, v in over.items():
        kw[k] = v
    if contestable is None:
        cal = CAL_BASE
    else:
        old = cnd.CONTESTABLE
        cnd.CONTESTABLE = contestable
        cal = cnd.calibrate()
        cnd.CONTESTABLE = old
    df, _ = cnd.project(cal, **kw)
    return float(df.loc[df.year == year, "us_nights_growth"].iloc[0])


def solve(year: int, target: float, build, lo: float, hi: float) -> float | None:
    """Bisect for the scalar x where growth_for(year, **build(x)) == target."""
    f = lambda x: growth_for(year, **build(x)) - target
    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:
        return None  # target unreachable inside the bracket
    for _ in range(80):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


# ---------------------------------------------------------------- levers
def _cat(year):
    def build(x):
        c = dict(cnd.CATEGORY_GROWTH); c[year] = x
        return {"cat": c}
    return build


def _shift(year):
    # one uniform logit-point shift applied in `year` only
    def build(x):
        return {"shift": {g: x for g in SEG}}
    return build


def _mkt(year):
    def build(x):
        m = dict(cnd.MARKET_GROWTH); m[year] = x
        return {"mkt": m}
    return build


def _adr(year):
    def build(x):
        a = dict(cnd.ABNB_ADR_GROWTH); a[year] = x
        return {"abnb_adr": a}
    return build


def _switch(year):
    def build(x):
        return {"switch_rate": x}
    return build


def _contestable(year):
    def build(x):
        return {"contestable": x}
    return build


LEVERS = [
    ("Category adoption (own-category nights growth)", _cat, 0.04, "%", -0.20, 0.60,
     "Inverting the model on disclosed NA nights gives 7.9% (2024) -> 4.5% (2025). 4% is the observed "
     "2025 exit rate. category_adoption_evidence.csv"),
    ("Product shift (logit points, one year)", _shift, 0.0, "logit", -1.0, 3.0,
     "Set to zero in the model. Management quantified RNPL + cancellation redesign + single fee at "
     "~3 pts of nights growth and ~4 pts of GBV in 1Q26 (Mertz, 1Q26 call). This is the lever that "
     "bucket belongs in."),
    ("U.S. lodging demand growth (contestable pool)", _mkt, 0.017, "%", -0.05, 0.40,
     "CoStar/Tourism Economics Aug-2026: demand +1.7% 2026, +1.1% 2027. An independent third-party "
     "forecast for the whole U.S. market."),
    ("Airbnb ADR growth (share via the price gap)", _adr, 0.035, "%", -0.40, 0.10,
     "Team WS13 base ex-FX: FY26 ~+3.5%, FY27/28 +2.5%. Bear +2.0% / bull +4.0% for 2H26. Lower ADR "
     "buys share but costs the ADR line one-for-one."),
    ("Switch rate", _switch, 5.0, "x", 0.0, 60.0,
     "Central 5.0, grid 2.5-10.3, anchored on F&F Table E9. No direct estimate; the cross-city "
     "attempt was a recorded null."),
    ("Contestable share of Airbnb nights", _contestable, 0.38, "%", 0.05, 0.95,
     "Farronato & Fradkin (AER 2022): 62% would not have used a hotel. Validated out-of-sample on "
     "NYC Local Law 18 (predicted hotel ADR +4.0-6.5%, observed +4.7-6.3%)."),
]


def main():
    global CAL_BASE
    CAL_BASE = cnd.calibrate()
    base_df, dec = cnd.project(CAL_BASE)
    dec.to_csv(OUT_DEC, index=False)

    print("Base decomposition of U.S. nights growth (percentage points of the prior-year base)")
    d = dec.copy()
    for c in ["market_pts", "mix_pts", "category_pts", "share_pts", "total"]:
        d[c] = (d[c] * 100).round(2)
    print(d.to_string(index=False))

    base_2026 = float(base_df.loc[base_df.year == 2026, "us_nights_growth"].iloc[0])
    rows = []
    for year in (2026, 2027):
        base_g = float(base_df.loc[base_df.year == year, "us_nights_growth"].iloc[0])
        for name, factory, base_val, unit, lo, hi, evidence in LEVERS:
            for scen, target in TARGETS[year].items():
                x = solve(year, target, factory(year), lo, hi)
                rows.append({"year": year, "lever": name, "unit": unit, "base_value": base_val,
                             "model_growth_at_base": round(base_g, 4), "target_scenario": scen,
                             "target_na_growth": target,
                             "required_value": None if x is None else round(x, 4),
                             "reachable_in_bracket": x is not None,
                             "evidence": evidence})
    req = pd.DataFrame(rows)
    req.to_csv(OUT_REQ, index=False)

    for year in (2026, 2027):
        base_g = float(base_df.loc[base_df.year == year, "us_nights_growth"].iloc[0])
        print(f"\n=== {year}: model says U.S. {base_g:+.2%}. What each lever alone would have to be ===")
        sub = req[(req.year == year)]
        for name, *_ in [(l[0],) for l in LEVERS]:
            r = sub[sub.lever == name]
            b = r.base_value.iloc[0]
            unit = r.unit.iloc[0]
            fmt = (lambda v: "  n/a  " if v is None or (isinstance(v, float) and np.isnan(v))
                   else (f"{v:+.1%}" if unit == "%" else f"{v:.2f}"))
            bfmt = f"{b:+.1%}" if unit == "%" else f"{b:.2f}"
            cells = "  ".join(f"{s}->{fmt(r[r.target_scenario == s].required_value.iloc[0]):>8}"
                              for s in ("bear", "base", "bull"))
            print(f"  {name:47} base {bfmt:>7}   {cells}")

    # ------------------------------------------------------------------ the lap test
    # A product launch is a LEVEL effect on share: it lifts nights in the year it lands, then laps.
    # cnd.project now takes a year-keyed shift so a launch can be told apart from a standing gain.
    pts3 = solve(2026, base_2026 + 0.03, _shift(2026), -1.0, 3.0)   # management's "~3 pts of nights"
    hit7 = solve(2026, TARGETS[2026]["base"], _shift(2026), -1.0, 3.0)
    scen = []
    for label, sh in [("base: no product lever", {}),
                      ("one-off 2026 launch (+0.10 logit), then laps", {2026: {g: 0.10 for g in SEG}}),
                      ("a launch of the same size every year", {g: 0.10 for g in SEG})]:
        df, _ = cnd.project(CAL_BASE, shift=sh)
        g = df.set_index("year").us_nights_growth
        scen.append({"scenario": label, **{str(y): round(float(g.loc[y]), 4) for y in cnd.YEARS[1:]}})
    sc = pd.DataFrame(scen)
    sc.to_csv(ROOT / "data/processed/na_nights_lap_scenarios.csv", index=False)

    print("\n=== The lap test: is the product lever a level effect or a growth rate? ===")
    print(f"  {pts3:.3f} logit pts reproduces management's '~3 pts of nights' (three features, 1Q26 call)")
    print(f"  {hit7:.3f} logit pts reaches WS10's NA base of +7.0% for 2026")
    print(sc.to_string(index=False))
    print("\n  WS10 NA targets:   2026 base +7.0%   2027 base +6.0%")

    # ------------------------------------------------------------------ corroboration
    # Does the disclosed NA path look like a product step or like a trend? If the three features are
    # what lifted NA, the step should be visible on the quarter they landed and absent before it.
    panel = pd.read_csv(ROOT / "data/processed/overnight/10_regional_panel_quarterly.csv")
    fc = pd.read_csv(ROOT / "data/processed/overnight/10_regional_forecast.csv")
    hist = panel[["quarter", "na_nights_yoy_mid"]].dropna().tail(8)
    fut = (fc[(fc.region == "na") & (fc.scenario == "base")][["period", "nights_yoy_pct"]]
           .rename(columns={"period": "quarter", "nights_yoy_pct": "na_nights_yoy_mid"}))
    track = pd.concat([hist, fut], ignore_index=True)
    track["source"] = ["WS10 estimate"] * len(hist) + ["WS10 base forecast"] * len(fut)
    track.to_csv(ROOT / "data/processed/na_nights_step_history.csv", index=False)
    print("\n=== Corroboration: the disclosed NA path is a step, not a trend ===")
    print(track.to_string(index=False))
    print(f"\n  Model base, no product lever:              {base_2026:+.1%} (2026)")
    print("  NA disclosed FY25 (158/154 10-K):          +2.6%")
    print("  The model's pre-product run rate and the pre-RNPL NA run rate are the same number.")

    print(f"\nwrote {OUT_REQ}\nwrote {OUT_DEC}")


if __name__ == "__main__":
    main()
