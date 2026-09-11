"""I1b. Party size and booked capacity for 3Q26-to-date, 2Q26 and 3Q25 on the nights index's
day-matched, vintage-matched windows, and the unit-size term of ex-FX ADR.

Windows (review dates; the prior-year side is shifted 364 days so the day-of-week mix matches):
  3q26_to_date   1 Jul 2026 .. min(late dump - 14 d, old dump - 14 d + 364 d)
  jul26          1 .. 31 Jul 2026
  2q26           1 Apr .. 30 Jun 2026
  3q25_to_date   the same to-date window one year earlier (only the old dump can carry it forward
                 on the vintage-matched basis; its own prior year is within-vintage)
  3q25_full      1 Jul .. 30 Sep 2025
Constructions:
  vmatch    current side from the 2026 dump, prior side from the market's own 2025 dump
            (both sides the same distance from their own scrape: survivorship and posting lag cancel)
  within    both sides from the 2026 dump (the pipeline's own construction, survivor-biased counts;
            for a per-review MEAN such as capacity the bias is second order, and the wedge is reported)
Weights: the pipeline's fixed-2019 market weights (each market's 2019 share of all reviews in
the dump, within the region or globally), plus equal-weighted and review-weighted variants.
Measures per window (pipeline definitions): booked capacity = mean `accommodates` of the
reviewed listing; composition-implied party size = 1/2/3.9/4.7 on solo/couple/family/group
conditional shares; stated head-count mean; sleeps-5+ share; entire-home share.
Unit-size term, pp of ADR y/y = elasticity x booked-capacity y/y (log points x 100);
elasticity 0.592 (quote basis, 13_party_size_adr.elasticities(): 0.399 + 0.140 x 1.374),
0.577 on the listed basis (band).

Outputs data/processed/adrq3/I/
  I1_market_windows.csv      per market x dump x window x side sums and means
  I1_party_size_windows.csv  region/global x window x construction x weighting: levels, y/y, size term
  I1_party_size_quarterly.csv  within-vintage quarterly series 2023Q3-2026Q2 from the refreshed dumps
                               (global and regions, fixed-2019 weights) for the backtest against 13's series
Run: py -3.13 analysis/src/adrq3/I1b_party_size_windows.py
"""
import glob, re
from pathlib import Path
import numpy as np, pandas as pd

WT = Path(__file__).resolve().parents[3]
OUT = WT / "data/processed/adrq3/I"
CACHE = OUT / "cache"
K = 14
SHIFT = pd.Timedelta(days=364)
EPS = {"quote_per_night": 0.5918, "listed_nightly": 0.5767}
E = EPS["quote_per_night"]
PARTY_W = {"solo": 1.0, "couple": 2.0, "family": 3.9, "group": 4.7}
SUMS = ["n", "n_any", "n_solo", "n_couple", "n_family", "n_group", "hc_n", "hc_sum", "hc_ge4",
        "acc_n", "acc_sum", "acc_ge5", "entire_n", "len_sum"]
REGMAP = {"NAM": "north_america", "EMEA": "emea", "LatAm": "latam", "APAC": "apac"}


def load():
    inv = pd.read_csv(OUT / "I1_inventory.csv").fillna("")
    daily, years = [], []
    for r in inv.itertuples():
        for d in (r.vintage_late, r.vintage_old):
            if not d:
                continue
            p = CACHE / f"{r.market_key}_{d}.parquet"
            if not p.exists():
                continue
            a = pd.read_parquet(p)
            a["date"] = pd.to_datetime(a["date"])
            daily.append(a)
            years.append(pd.read_parquet(CACHE / f"{r.market_key}_{d}_years.parquet"))
    return inv, pd.concat(daily, ignore_index=True), pd.concat(years, ignore_index=True)


def sums(d, a0, a1):
    s = d[(d.date >= a0) & (d.date <= a1)][SUMS].sum()
    return s


def means(s):
    n, na = s["n"], s["n_any"]
    out = dict(reviews=n, mention_any=na / n if n else np.nan)
    cond = {k: (s[f"n_{k}"] / na if na else np.nan) for k in PARTY_W}
    tot = sum(cond.values()) if na else np.nan
    out["party_size_composition"] = sum(PARTY_W[k] * cond[k] for k in PARTY_W) / tot if na else np.nan
    for k in PARTY_W:
        out[f"cond_{k}"] = cond[k]
    out["headcount_mean"] = s["hc_sum"] / s["hc_n"] if s["hc_n"] else np.nan
    out["headcount_n"] = s["hc_n"]
    out["headcount_ge4"] = s["hc_ge4"] / s["hc_n"] if s["hc_n"] else np.nan
    out["accommodates_mean"] = s["acc_sum"] / s["acc_n"] if s["acc_n"] else np.nan
    out["accommodates_n"] = s["acc_n"]
    out["accommodates_ge5"] = s["acc_ge5"] / s["acc_n"] if s["acc_n"] else np.nan
    out["entire_share"] = s["entire_n"] / s["acc_n"] if s["acc_n"] else np.nan
    return out


def main():
    inv, daily, years = load()
    inv = inv.set_index("market_key")
    ref = years[years.year.eq(2019)].merge(inv[["vintage_late"]], left_on="market_key", right_index=True)
    ref = ref[ref.dump_date == ref.vintage_late].set_index("market_key").n_all  # 2019 reviews in the 2026 dump
    rows = []
    for mk, g in daily.groupby("market_key"):
        late, old = inv.at[mk, "vintage_late"], inv.at[mk, "vintage_old"]
        lt = pd.Timestamp(late)
        ot = pd.Timestamp(old) if old else None
        gl = g[g.dump_date.eq(late)]
        go = g[g.dump_date.eq(old)] if old else None
        cur_end = lt - pd.Timedelta(days=K)
        if ot is not None:
            cur_end = min(cur_end, ot - pd.Timedelta(days=K) + SHIFT)
        wins = {"3q26_to_date": (pd.Timestamp("2026-07-01"), cur_end),
                "jul26": (pd.Timestamp("2026-07-01"), pd.Timestamp("2026-07-31")),
                "2q26": (pd.Timestamp("2026-04-01"), pd.Timestamp("2026-06-30")),
                "3q25_full": (pd.Timestamp("2025-07-01"), pd.Timestamp("2025-09-30")),
                "2q25": (pd.Timestamp("2025-04-01"), pd.Timestamp("2025-06-30"))}
        if ot is not None:
            wins["3q25_to_date"] = (pd.Timestamp("2025-07-01"), ot - pd.Timedelta(days=K))
        for wname, (a0, a1) in wins.items():
            if a1 < a0:
                continue
            b0, b1 = a0 - SHIFT, a1 - SHIFT
            specs = [("within", "cur", gl, a0, a1, late), ("within", "prior", gl, b0, b1, late)]
            if ot is not None and wname in ("3q26_to_date", "jul26", "2q26"):
                specs.append(("vmatch", "prior", go, b0, b1, old))
            if ot is not None and wname == "3q25_to_date":
                # the old dump carries the 3Q25 to-date window itself (vintage-matched CURRENT side for 3Q25)
                specs.append(("oldvintage", "cur", go, a0, a1, old))
                specs.append(("oldvintage", "prior", go, b0, b1, old))
            for cons, side, dd, x0, x1, dump in specs:
                s = sums(dd, x0, x1)
                if s["n"] == 0:
                    continue
                m = means(s)
                rows.append(dict(market_key=mk, region=inv.at[mk, "region"], window=wname, construction=cons, side=side,
                                 dump_date=dump, win_start=str(x0.date()), win_end=str(x1.date()), ref_2019=float(ref.get(mk, np.nan)), **m))
    mw = pd.DataFrame(rows)
    mw.to_csv(OUT / "I1_market_windows.csv", index=False, encoding="utf-8")

    # --- aggregate: region / global x window x construction x weighting ---------------------
    MEASURES = ["accommodates_mean", "party_size_composition", "headcount_mean", "accommodates_ge5", "entire_share", "mention_any"]
    out = []
    mw["region_p"] = mw.region.map(REGMAP)
    for wname, gw in mw.groupby("window"):
        for cons in ["within", "vmatch", "oldvintage"]:
            cur_cons = "within" if cons == "vmatch" else cons
            cur = gw[gw.construction.eq(cur_cons) & gw.side.eq("cur")].set_index("market_key")
            pri = gw[gw.construction.eq(cons) & gw.side.eq("prior")].set_index("market_key")
            mks = cur.index.intersection(pri.index)
            if len(mks) == 0:
                continue
            cur, pri = cur.loc[mks], pri.loc[mks]
            for reg, sel in [("global", np.ones(len(mks), bool))] + [(REGMAP[r], (cur.region == r).values) for r in REGMAP]:
                c, p = cur[sel], pri[sel]
                if len(c) == 0:
                    continue
                for weighting in ["fixed_2019", "equal", "reviews"]:
                    if weighting == "fixed_2019":
                        w = c.ref_2019.fillna(0).values
                    elif weighting == "equal":
                        w = np.ones(len(c))
                    else:
                        w = c.reviews.values
                    row = dict(window=wname, construction=cons, weighting=weighting, region=reg, n_markets=int(len(c)),
                               reviews_cur=float(c.reviews.sum()), reviews_prior=float(p.reviews.sum()),
                               win_start=c.win_start.min(), win_end=c.win_end.max())
                    for mcol in MEASURES:
                        ok = c[mcol].notna().values & p[mcol].notna().values & (w > 0)
                        if ok.sum() == 0:
                            row[f"{mcol}_cur"] = row[f"{mcol}_prior"] = row[f"{mcol}_yoy_pct"] = np.nan
                            continue
                        ww = w[ok] / w[ok].sum()
                        vc, vp = float((ww * c[mcol].values[ok]).sum()), float((ww * p[mcol].values[ok]).sum())
                        row[f"{mcol}_cur"], row[f"{mcol}_prior"] = vc, vp
                        row[f"{mcol}_yoy_pct"] = 100 * np.log(vc / vp) if vc > 0 and vp > 0 else np.nan
                        if mcol == "accommodates_mean":
                            # market-level dispersion of capacity y/y (weighted bootstrap over markets)
                            d = 100 * np.log(c[mcol].values[ok] / p[mcol].values[ok])
                            rng = np.random.default_rng(11)
                            idx = rng.integers(0, len(d), size=(1000, len(d)))
                            bs = (d[idx] * ww[idx]).sum(axis=1) / ww[idx].sum(axis=1)
                            row["cap_yoy_bs_lo"], row["cap_yoy_bs_hi"] = float(np.percentile(bs, 5)), float(np.percentile(bs, 95))
                            row["cap_yoy_market_median"] = float(np.median(d))
                    row["size_term_pp"] = E * row["accommodates_mean_yoy_pct"]
                    row["size_term_listed_basis_pp"] = EPS["listed_nightly"] * row["accommodates_mean_yoy_pct"]
                    row["size_term_bs_lo_pp"] = E * row.get("cap_yoy_bs_lo", np.nan)
                    row["size_term_bs_hi_pp"] = E * row.get("cap_yoy_bs_hi", np.nan)
                    out.append(row)
    res = pd.DataFrame(out)
    res.to_csv(OUT / "I1_party_size_windows.csv", index=False, encoding="utf-8")

    # --- within-vintage quarterly series from the 2026 dumps, fixed-2019 weights ------------
    qrows = []
    late = daily.merge(inv[["vintage_late"]], left_on="market_key", right_index=True)
    late = late[late.dump_date == late.vintage_late].copy()
    late["q"] = late.date.dt.to_period("Q").astype(str)
    late["region_p"] = late.market_key.map(inv.region).map(REGMAP)
    for q, gq in late.groupby("q"):
        if q < "2022Q3" or q > "2026Q3":
            continue
        for reg in ["global"] + list(REGMAP.values()):
            sel = gq if reg == "global" else gq[gq.region_p.eq(reg)]
            ms = sel.groupby("market_key")[SUMS].sum()
            if len(ms) == 0:
                continue
            w = ms.index.map(ref).fillna(0).values.astype(float)
            mm = pd.DataFrame([means(ms.loc[m]) for m in ms.index], index=ms.index)
            row = dict(q=q, region=reg, n_markets=int(len(ms)), reviews=float(ms.n.sum()))
            for mcol in MEASURES:
                ok = mm[mcol].notna().values & (w > 0)
                row[mcol] = float((w[ok] * mm[mcol].values[ok]).sum() / w[ok].sum()) if ok.sum() else np.nan
            qrows.append(row)
    qs = pd.DataFrame(qrows).sort_values(["region", "q"])
    for mcol in ["accommodates_mean", "party_size_composition", "headcount_mean"]:
        qs[f"{mcol}_yoy_pct"] = qs.groupby("region")[mcol].transform(lambda s: 100 * np.log(s).diff(4))
    qs["size_term_pp"] = E * qs.accommodates_mean_yoy_pct
    qs.to_csv(OUT / "I1_party_size_quarterly.csv", index=False, encoding="utf-8")

    pd.set_option("display.width", 250)
    show = res[res.weighting.eq("fixed_2019")][["window", "construction", "region", "n_markets", "reviews_cur", "accommodates_mean_cur", "accommodates_mean_prior",
                                                "accommodates_mean_yoy_pct", "cap_yoy_bs_lo", "cap_yoy_bs_hi", "party_size_composition_yoy_pct", "headcount_mean_yoy_pct", "size_term_pp"]]
    print(show.round(3).to_string(index=False))
    print(qs[qs.region.eq("global")].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
