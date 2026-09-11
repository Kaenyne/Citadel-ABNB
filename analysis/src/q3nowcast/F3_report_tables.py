"""WS-F step 3: the tables that go in the note, written to a markdown file so the note and
the data cannot drift apart.

Run after F2. Output: data/processed/q3nowcast/F/F3_note_tables.md
"""
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/q3nowcast/F"
MAIN_TREE = Path(r"C:\Users\krish\citadel-abnb")
REGION_ORDER = ["na", "emea", "latam", "apac"]


def pooled(frame, num, den):
    d = frame[den].sum()
    return float(frame[num].sum() / d) if d else np.nan


def table(frame, cols, floats=3):
    """Pipe table by hand: tabulate is not installed in this environment."""
    sub = frame[cols].copy()
    for c in sub.columns:
        if pd.api.types.is_float_dtype(sub[c]):
            sub[c] = sub[c].round(floats)
    header = [str(c) for c in sub.columns]
    body = [[("" if pd.isna(v) else str(v)) for v in row] for row in sub.itertuples(index=False)]
    width = [max(len(header[i]), *(len(r[i]) for r in body)) if body else len(header[i])
             for i in range(len(header))]
    lines = ["| " + " | ".join(h.ljust(width[i]) for i, h in enumerate(header)) + " |",
             "|" + "|".join("-" * (w + 2) for w in width) + "|"]
    for r in body:
        lines.append("| " + " | ".join(v.ljust(width[i]) for i, v in enumerate(r)) + " |")
    return chr(10).join(lines)


def main():
    parts = ["# WS-F calendar pace tables", ""]
    lv = pd.read_csv(OUT / "F2_levels_by_horizon.csv")
    tb = pd.read_csv(OUT / "F2_transitions_by_horizon.csv")
    yl = pd.read_csv(OUT / "F2_yoy_levels.csv")
    yf = pd.read_csv(OUT / "F2_yoy_flows.csv")
    q3 = pd.read_csv(OUT / "F2_q3_in_progress.csv")
    rec = pd.read_csv(OUT / "F2_theo_reconciliation.csv")
    prov = pd.read_csv(OUT / "F1_provenance.csv")

    parts += ["## 0. Coverage", "",
              f"- {prov.market.nunique()} markets, {len(prov)} calendar vintages, "
              f"{prov.raw_rows.sum() / 1e6:.0f}mm listing-night rows, "
              f"{prov.compressed_bytes.sum() / 1e9:.2f} GB gzip, full listing set (no sampling).",
              f"- vintage dates {prov.snapshot.min()} to {prov.snapshot.max()}; "
              f"{int((prov.snapshot < '2025-09').sum())} of them added by WS-F from the CDN.",
              f"- {tb[tb.horizon == 'd001_180'].groupby(['market', 'snapshot0', 'snapshot1']).ngroups}"
              " matched vintage pairs.", ""]

    # ---- 1. Theo reconciliation
    parts += ["## 1. Reconciliation with Theo's Jun 2026 booking curve", ""]
    if len(rec):
        parts += [f"- overlapping cells: {len(rec)} (market x snapshot x horizon), "
                  f"{rec.market.nunique()} markets",
                  f"- median absolute difference in blocked rate: {rec.diff_pp.abs().median():.4f} pp; "
                  f"max {rec.diff_pp.abs().max():.4f} pp",
                  f"- listing-night ratio ours / his: median {rec.night_ratio.median():.4f}, "
                  f"min {rec.night_ratio.min():.4f}, max {rec.night_ratio.max():.4f}", ""]
        wide = rec.pivot_table(index="market", columns="horizon", values="diff_pp")
        parts += ["Difference in pp by horizon (ours minus his), first 10 markets:", "",
                  table(wide.head(10).reset_index(), list(wide.reset_index().columns), 4), ""]
    else:
        parts += ["- no overlap found", ""]

    # ---- 2. the pace metric, latest pair, by region
    parts += ["## 2. Pace metric, latest vintage pair, screened listings", ""]
    scr = tb[tb.regime == "screened"]
    latest = scr[scr.snapshot1 == scr.groupby("market").snapshot1.transform("max")]
    rows = []
    for (region, horizon), g in latest.groupby(["region", "horizon"]):
        rows.append(dict(region=region, horizon=horizon, n_markets=g.market.nunique(),
                         blocked_share_v0=pooled(g, "blocked_v0", "matched_nights"),
                         blocked_share_v1=pooled(g, "blocked_v1", "matched_nights"),
                         net_change_pp=pooled(g, "blocked_v1", "matched_nights") * 100
                         - pooled(g, "blocked_v0", "matched_nights") * 100,
                         new_block_rate_pct=pooled(g, "new_blocks", "available_v0") * 100,
                         reopen_rate_pct=pooled(g, "reopenings", "blocked_v0") * 100))
    pace = pd.DataFrame(rows)
    parts += [table(pace, list(pace.columns)), ""]

    # ---- 3. y/y levels
    parts += ["## 3. Year over year blocked share, calendar-matched vintage pairs", ""]
    for tight in (True, False):
        sub = yl[yl.tight_pair == tight]
        if not len(sub):
            continue
        sub = sub[sub.snapshot_current >= "2026-06-01"]
        if not len(sub):
            continue
        rows = []
        for (region, horizon), g in sub.groupby(["region", "horizon"]):
            rows.append(dict(region=region, horizon=horizon, n_markets=g.market.nunique(),
                             yoy_diff_pp_wtd=float(
                                 (g.yoy_diff_pp * g.listing_nights_current).sum()
                                 / g.listing_nights_current.sum()),
                             yoy_diff_pp_median=float(g.yoy_diff_pp.median()),
                             markets_negative=int(
                                 (g.groupby("market").yoy_diff_pp.mean() < 0).sum()),
                             listing_nights_change_pct_median=float(
                                 g.listing_nights_change_pct.median())))
        frame = pd.DataFrame(rows)
        label = ("2026 vintage against a prior-year vintage within 10 days of the "
                 "anniversary" if tight else
                 "2026 vintage against a prior-year vintage 11 to 35 days off the anniversary")
        parts += [f"### {label}", "", table(frame, list(frame.columns)), ""]

    # ---- 4. Q3 in progress
    parts += ["## 4. Q3 in progress, stay dates to 30 Sep, same day-of-year window", ""]
    if len(q3):
        rows = []
        for region, g in q3.groupby("region"):
            rows.append(dict(region=region, n_markets=g.market.nunique(),
                             blocked_share_2025=float(
                                 (g.blocked_share_2025 * g.listing_nights_2025).sum()
                                 / g.listing_nights_2025.sum()),
                             blocked_share_2026=float(
                                 (g.blocked_share_2026 * g.listing_nights_2026).sum()
                                 / g.listing_nights_2026.sum()),
                             yoy_diff_pp=float((g.yoy_diff_pp * g.listing_nights_2026).sum()
                                               / g.listing_nights_2026.sum()),
                             yoy_diff_pp_adjusted=float(
                                 (g.yoy_diff_pp_adjusted * g.listing_nights_2026).sum()
                                 / g.listing_nights_2026.sum()),
                             mean_horizon_offset_days=float(g.horizon_offset_days.mean()),
                             stay_days=float(g.stay_days_2026.median())))
        frame = pd.DataFrame(rows)
        parts += [table(frame, list(frame.columns)), ""]

    # ---- 5. y/y flows and the backtest
    parts += ["## 5. Year over year of the booking flow", ""]
    if len(yf):
        sub = yf[(yf.regime == "screened") & (yf.horizon == "d001_180")
                 & (yf.years_back == 1)]
        rows = []
        for (region, cur), g in sub.groupby(["region", "current_pair"]):
            rows.append(dict(region=region, current_pair=cur,
                             n_markets=g.market.nunique(),
                             median_match_score_days=float(g.match_score.median()),
                             net_change_pp_prior=float(
                                 (g.net_change_pp_prior * g.matched_nights_prior).sum()
                                 / g.matched_nights_prior.sum()),
                             net_change_pp_current=float(
                                 (g.net_change_pp_current * g.matched_nights_current).sum()
                                 / g.matched_nights_current.sum()),
                             net_change_yoy_pp=float(
                                 (g.net_change_yoy_pp * g.matched_nights_current).sum()
                                 / g.matched_nights_current.sum()),
                             n_tight=int(g.tight_pair.sum())))
        frame = pd.DataFrame(rows).sort_values(["current_pair", "region"])
        parts += [table(frame, list(frame.columns)), ""]
        two = yf[(yf.regime == "screened") & (yf.horizon == "d001_180")
                 & (yf.years_back == 2)]
        parts += [f"- markets with a two-years-back pair as well: {two.market.nunique()}", ""]
    bt = pd.read_csv(OUT / "F2_backtest.csv") if (OUT / "F2_backtest.csv").exists() else pd.DataFrame()
    parts += ["## 6. Backtest points", ""]
    if len(bt):
        parts += [table(bt.drop(columns=["markets"]), [c for c in bt.columns if c != "markets"]), ""]
    else:
        parts += ["- none", ""]

    (OUT / "F3_note_tables.md").write_text("\n".join(parts), encoding="utf-8")
    print("\n".join(parts))
    print(f"\nwrote {OUT / 'F3_note_tables.md'}", flush=True)


if __name__ == "__main__":
    main()
