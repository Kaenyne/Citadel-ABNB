"""WS22 step 6: before/after table for the regulatory Monte Carlo repair (audit finding A06).

"Before" is regenerated from the frozen pre-fix sampler in `22_regulatory_before.py` (not from a saved CSV), so
the whole comparison is reproducible from source. "After" is the live
`analysis/src/abnb_regulatory_forecast.py`. Both use the same seed (20260905) and 200,000 draws, and both are
summarised with the same `summarise()`, so every difference comes from the probability mechanics.

Revenue loss, EBITDA compliance cost and one-off cash are kept as separate line items throughout: the compliance
row is an EBITDA cost expressed as a % of revenue (not lost revenue), the cash row is a one-off ($M, not
run-rate). The by-year/by-region block replicates the WS11 overlay arithmetic in
`analysis/src/overnight/11_competition_supply_overlays.py` section 4 (2026 = one third of end-2027; 2028 =
one third of the way from end-2027 to end-2030; EMEA/NA nights drag = drag x region share of drag / region
share of revenue).

Reads:  analysis/src/abnb_regulatory_forecast.py, analysis/src/overnight/22_regulatory_before.py
Writes: data/processed/overnight/22_regulatory_delta.csv
Run: py -3.13 analysis/src/overnight/22_regulatory_delta.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/overnight"

EU_IDS = {"EU-AHA", "EU-TAIL", "ES-REMOVE", "ES-REGIONS", "BCN-2028", "BCN-PARTIAL", "PARIS-PRO", "PARIS-COPRO",
          "GR-FREEZE", "IE-REG", "UK-ENG", "IT-NAT", "PT-RETIGHT", "NL-AMS"}
US_IDS = {"US-CITY", "NYC-LOOSEN", "CHI-SUIT", "MAUI"}
SHARE_EMEA_REV, SHARE_NA_REV = 0.39, 0.42


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def interp(v27, v30, year):
    if year == 2026:
        return v27 / 3
    if year == 2027:
        return v27
    return v27 + (v30 - v27) * (year - 2027) / 3


def stats(out, contribs):
    """Horizon-level statistics plus the WS11 year/region overlay, from one simulation's output."""
    s = {}
    for h in ("2027", "2030"):
        comp = out[h]["per_event"]["COMPLIANCE"][1]
        rl = out[h]["loss"] - comp
        s[h] = dict(rev_median=np.median(rl), rev_mean=rl.mean(), rev_p95=np.percentile(rl, 95),
                    comp_median=np.median(comp), comp_mean=comp.mean(), comp_p95=np.percentile(comp, 95),
                    cash_median=np.median(out[h]["cash"]), cash_mean=out[h]["cash"].mean(),
                    cash_p95=np.percentile(out[h]["cash"], 95))
    frac = {}
    for h, hn in (("2027", 2027), ("2030", 2030)):
        d = contribs[contribs.horizon == hn] if contribs.horizon.dtype != object else contribs[contribs.horizon == h]
        eu = d[d.id.isin(EU_IDS)].expected_loss_pct.sum()
        us = d[d.id.isin(US_IDS)].expected_loss_pct.sum()
        frac[h] = eu / (eu + us)
    return s, frac


def main():
    live = load(ROOT / "analysis/src/abnb_regulatory_forecast.py", "reg_after")
    old = load(Path(__file__).with_name("22_regulatory_before.py"), "reg_before")

    ev_a, out_a = live.draw(live.N)
    _, con_a = live.summarise(ev_a, out_a)
    o_b = old.draw_old()
    out_b = {h: dict(loss=o_b[h]["loss"], cash=np.zeros(old.N), per_event=o_b[h]["per"]) for h in ("2027", "2030")}
    for h in ("2027", "2030"):  # the frozen sampler drops cash; rebuild it with the same rule
        c = np.zeros(old.N)
        for (eid, p27, p30, _l, _s, _g, cash) in old.OLD:
            if cash:
                c += np.where(o_b[h]["per"][eid][0], cash, 0.0)
        out_b[h]["cash"] = c
    _, con_b = live.summarise(pd.DataFrame(live.EVENTS), out_b)

    sa, fa = stats(out_a, con_a)
    sb, fb = stats(out_b, con_b)

    rows = []

    def add(scope, year_or_h, region, line, stat, before, after):
        rows.append(dict(scope=scope, period=year_or_h, region=region, line_item=line, statistic=stat,
                         before=round(float(before), 4), after=round(float(after), 4),
                         delta=round(float(after - before), 4)))

    for h in ("2027", "2030"):
        for stat in ("median", "mean", "p95"):
            add("horizon", f"end-{h}", "global", "revenue loss, % of global revenue", stat,
                sb[h][f"rev_{stat}"], sa[h][f"rev_{stat}"])
            add("horizon", f"end-{h}", "global", "compliance cost (EBITDA), % of revenue", stat,
                sb[h][f"comp_{stat}"], sa[h][f"comp_{stat}"])
            add("horizon", f"end-{h}", "global", "one-off cash, $M", stat,
                sb[h][f"cash_{stat}"], sa[h][f"cash_{stat}"])

    for y in (2026, 2027, 2028):
        for stat in ("median", "mean", "p95"):
            b = interp(sb["2027"][f"rev_{stat}"], sb["2030"][f"rev_{stat}"], y)
            a = interp(sa["2027"][f"rev_{stat}"], sa["2030"][f"rev_{stat}"], y)
            fb_y = fb["2027"] if y <= 2027 else fb["2027"] + (fb["2030"] - fb["2027"]) * (y - 2027) / 3
            fa_y = fa["2027"] if y <= 2027 else fa["2027"] + (fa["2030"] - fa["2027"]) * (y - 2027) / 3
            add("overlay_year", y, "global", "revenue drag, % of global revenue", stat, b, a)
            add("overlay_year", y, "EMEA", "nights drag, % of regional nights", stat,
                b * fb_y / SHARE_EMEA_REV, a * fa_y / SHARE_EMEA_REV)
            add("overlay_year", y, "NA", "nights drag, % of regional nights", stat,
                b * (1 - fb_y) / SHARE_NA_REV, a * (1 - fa_y) / SHARE_NA_REV)

    for h in ("2027", "2030"):
        hb = con_b[con_b.horizon.astype(str) == h].set_index("id")
        ha = con_a[con_a.horizon.astype(str) == h].set_index("id")
        for eid in ha.index:
            add("event", f"end-{h}", "EU" if eid in EU_IDS else ("US" if eid in US_IDS else "global"),
                f"{eid}: P(in force)", "probability", hb.p_in_force.get(eid, np.nan), ha.p_in_force.get(eid, np.nan))
            add("event", f"end-{h}", "EU" if eid in EU_IDS else ("US" if eid in US_IDS else "global"),
                f"{eid}: expected loss, % of revenue", "mean", hb.expected_loss_pct.get(eid, np.nan),
                ha.expected_loss_pct.get(eid, np.nan))

    df = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "22_regulatory_delta.csv", index=False)
    pd.set_option("display.width", 200); pd.set_option("display.max_rows", 400); pd.set_option("display.max_colwidth", 60)
    print(df[df.scope != "event"].to_string(index=False))
    print()
    print(df[(df.scope == "event") & (df.delta.abs() > 0.005)].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
