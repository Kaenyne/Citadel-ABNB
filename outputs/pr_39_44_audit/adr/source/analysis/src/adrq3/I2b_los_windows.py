"""I2b. Length-of-stay mix term for 3Q26 from blocked-run lengths at matched stay dates and
matched lead times, 34 calendar markets, Aug/Jun 2026 vintages against the same market's
2025 vintage one year earlier (and 2025 against 2024 where 2024 calendars exist).

A blocked run is NOT a booking: it is a contiguous block of nights the host shows as
unavailable, which mixes guest bookings with host blocks (owner use, maintenance, listings
paused for the season) and, in NYC and LA, regulatory minimums. Host blocks are long, so the
level of the 28+ share is inflated by a market-specific factor (14c). Comparing the same
stay window at the same lead time across vintages cancels the part of that inflation that
is stable within a market; it does not cancel a change in host blocking behaviour, which
would read here as a change in the LOS mix. Runs over 90 nights are dropped as blocks (14c
cap); runs are assigned to a window by their START date, so a long stay that began before
the window is excluded on both sides.

Pairs (per market): late = each 2026 vintage in Jun (2026-06-01..07-10) and Aug
(2026-08-01..09-05); old = the 2025 vintage closest to late - 364 days within +/-45 days,
preferring one dated on or before the window start. 2024 pairs likewise for the 2025 Jun
vintages of the four markets with 2024 monthly calendars (Austin, Nashville, Paris, Rome).

Windows (both sides, prior side shifted by 364 days so the day-of-week mix matches):
  lead_matched   stays starting 7 to 97 days after the vintage date, each side on its own vintage
  calendar_q3    Jun pairs: stays starting max(1 Jul, later of the two vintages + 1) .. 30 Sep
  calendar_sep   Aug pairs: stays starting max(1 Sep, later of the two vintages + 1) .. 30 Sep

Weights: 14c's occupancy weighting (each ACTIVE listing, number_of_reviews_ltm > 0,
contributes its estimated_occupancy_l365d nights split across buckets in proportion to its
in-window runs), from the 14c per-listing parquet when the vintage is one of its five, else
the nearest listings dump within 60 days. Unweighted nights shares are reported alongside.

Term: LOS mix pp = sum_b d(nights share_b) x (ratio_b - 1), ratios lt7 1.000, 7-27 0.966,
28+ 0.852 (14a). Regional aggregate ex NYC/LA; global on the 10-K FY25 nights shares.

Outputs data/processed/adrq3/I/
  I2_los_pairs.csv            the vintage pairs used
  I2_los_market_windows.csv   per market x pair x window x side: nights shares, mean run, n
  I2_los_term.csv             region and global: shares both years, d(share), LOS mix pp, by window and weighting
Run: py -3.13 analysis/src/adrq3/I2b_los_windows.py
"""
import re, glob, sys
from pathlib import Path
import numpy as np, pandas as pd

WT = Path(__file__).resolve().parents[3]
MAIN = Path(r"C:\Users\krish\citadel-abnb"
            )
RUNS = WT / "data/processed/adrq3/I/los_runs"
BYL = MAIN / "data/processed/adr/14c_los_runs_by_listing"
LST = MAIN / "data/raw/inside_airbnb"
OUT = WT / "data/processed/adrq3/I"
sys.path.insert(0, str(WT / "analysis/src/adr"))
from importlib import util as _u  # noqa: E402
_s = _u.spec_from_file_location("c14", WT / "analysis/src/adr/14c_los_runs_panel.py")
c14 = _u.module_from_spec(_s); _s.loader.exec_module(c14)
MARKETS, TENK_W, REG_MIN = c14.MARKETS, c14.TENK_W, c14.REG_MIN_MARKETS
RATIO = {"lt7": 1.0, "n7_27": 0.966, "ge28": 0.852}
BUCKETS = list(RATIO)
CAP = 90
SHIFT = pd.Timedelta(days=364)


def vintages(market):
    fs = glob.glob(str(RUNS / f"{market}_*_runs.parquet"))
    return sorted(re.search(r"_(\d{4}-\d{2}-\d{2})_runs", f).group(1) for f in fs)


def weights(market, date):
    """listing_id -> (active, w) for the vintage; 14c parquet if present else nearest listings dump."""
    p = BYL / f"{market}_{date}.parquet"
    if p.exists():
        d = pd.read_parquet(p, columns=["listing_id", "active", "w", "minimum_nights"])
        return d.drop_duplicates("listing_id").set_index("listing_id"), f"14c:{date}"
    fs = glob.glob(str(LST / f"{market}_*_listings.csv.gz"))
    ds = sorted(((abs((pd.Timestamp(re.search(r"_(\d{4}-\d{2}-\d{2})_listings", f).group(1)) - pd.Timestamp(date)).days), f) for f in fs))
    if not ds or ds[0][0] > 60:
        return None, "none"
    f = ds[0][1]
    L = pd.read_csv(f, usecols=lambda c: c in ("id", "number_of_reviews_ltm", "estimated_occupancy_l365d", "minimum_nights"), low_memory=False)
    L = L.rename(columns={"id": "listing_id"}).drop_duplicates("listing_id").set_index("listing_id")
    d = pd.DataFrame(index=L.index)
    d["active"] = pd.to_numeric(L.get("number_of_reviews_ltm"), errors="coerce").fillna(0) > 0
    d["w"] = pd.to_numeric(L.get("estimated_occupancy_l365d"), errors="coerce").clip(0, 0.7 * 365)
    d["minimum_nights"] = pd.to_numeric(L.get("minimum_nights"), errors="coerce")
    return d, f"listings:{re.search(r'_(\d{4}-\d{2}-\d{2})_listings', f).group(1)}"


def window_stats(runs, wdf, a0, a1):
    r = runs[(runs.start >= a0) & (runs.start <= a1)]
    n_over = int((r.len > CAP).sum())
    r = r[r.len <= CAP]
    if wdf is not None:
        r = r.join(wdf, on="listing_id", how="left")
        r = r[r.active.eq(True)]
    else:
        r = r.assign(w=np.nan)
    r = r.assign(b=np.select([r.len < 7, r.len < 28], ["lt7", "n7_27"], "ge28"))
    out = dict(n_runs=int(len(r)), n_listings=int(r.listing_id.nunique()), n_runs_over90=n_over,
               nights=float(r.len.sum()), mean_run_cap90=float(r.len.mean()) if len(r) else np.nan,
               mean_run_cap30=float(r.len[r.len <= 30].mean()) if len(r) else np.nan)
    nb = r.groupby("b").len.sum()
    for b in BUCKETS:
        out[f"nights_{b}"] = float(nb.get(b, 0.0))
    # occupancy weighting as in 14c: each listing contributes w, split in proportion to its in-window runs
    ok = r[r.w.notna() & (r.w > 0)]
    if len(ok):
        tot = ok.groupby("listing_id").len.transform("sum")
        ok = ok.assign(wn=ok.len * ok.w / tot)
        wb = ok.groupby("b").wn.sum()
        for b in BUCKETS:
            out[f"w_nights_{b}"] = float(wb.get(b, 0.0))
        out["w_nights"] = float(ok.wn.sum())
    else:
        for b in BUCKETS:
            out[f"w_nights_{b}"] = np.nan
        out["w_nights"] = np.nan
    return out


def pairs_for(market):
    vs = vintages(market)
    ps = []
    for late in vs:
        lt = pd.Timestamp(late)
        if lt.year not in (2025, 2026):
            continue
        kind = "jun" if lt.month in (5, 6, 7) else "aug"
        if lt.year == 2026 and kind == "jun" and not (pd.Timestamp("2026-06-01") <= lt <= pd.Timestamp("2026-07-10")):
            continue
        if lt.year == 2026 and kind == "aug" and not (pd.Timestamp("2026-08-01") <= lt <= pd.Timestamp("2026-09-05")):
            continue
        if lt.year == 2025 and kind != "jun":
            continue  # 2025-vs-2024 only for the summer window
        cands = [(v, (pd.Timestamp(v) - (lt - SHIFT)).days) for v in vs if abs((pd.Timestamp(v) - (lt - SHIFT)).days) <= 45]
        if not cands:
            continue
        # prefer an old vintage dated on/before the window start (so the window is forward on both sides), then nearest
        wstart = pd.Timestamp(f"{lt.year - 1}-07-01") if kind == "jun" else pd.Timestamp(f"{lt.year - 1}-09-01")
        cands.sort(key=lambda c: (pd.Timestamp(c[0]) > wstart, abs(c[1])))
        ps.append(dict(market=market, region=MARKETS[market][1], kind=kind, late=late, old=cands[0][0],
                       gap_days=(lt - pd.Timestamp(cands[0][0])).days))
    return ps


def main():
    pairs = [p for m in MARKETS for p in pairs_for(m)]
    pairs = pd.DataFrame(pairs)
    pairs.to_csv(OUT / "I2_los_pairs.csv", index=False)
    print(pairs.to_string(index=False))
    rows = []
    wcache = {}
    for p in pairs.itertuples():
        lt, ot = pd.Timestamp(p.late), pd.Timestamp(p.old)
        rl = pd.read_parquet(RUNS / f"{p.market}_{p.late}_runs.parquet")
        ro = pd.read_parquet(RUNS / f"{p.market}_{p.old}_runs.parquet")
        for side, d in (("late", p.late), ("old", p.old)):
            if (p.market, d) not in wcache:
                wcache[(p.market, d)] = weights(p.market, d)
        wl, wl_src = wcache[(p.market, p.late)]
        wo, wo_src = wcache[(p.market, p.old)]
        wins = {"lead_matched": ((lt + pd.Timedelta(days=7), lt + pd.Timedelta(days=97)),
                                 (ot + pd.Timedelta(days=7), ot + pd.Timedelta(days=97)))}
        if p.kind == "jun":
            a0 = max(pd.Timestamp(f"{lt.year}-07-01"), lt + pd.Timedelta(days=1), ot + SHIFT + pd.Timedelta(days=1))
            a1 = pd.Timestamp(f"{lt.year}-09-30")
            wins["calendar_q3"] = ((a0, a1), (a0 - SHIFT, a1 - SHIFT))
        else:
            a0 = max(pd.Timestamp(f"{lt.year}-09-01"), lt + pd.Timedelta(days=1), ot + SHIFT + pd.Timedelta(days=1))
            a1 = pd.Timestamp(f"{lt.year}-09-30")
            wins["calendar_sep"] = ((a0, a1), (a0 - SHIFT, a1 - SHIFT))
        for wname, ((la0, la1), (oa0, oa1)) in wins.items():
            if la1 <= la0 or oa1 <= oa0:
                continue
            for side, runs, wdf, wsrc, (b0, b1) in (("late", rl, wl, wl_src, (la0, la1)), ("old", ro, wo, wo_src, (oa0, oa1))):
                st = window_stats(runs, wdf, b0, b1)
                rows.append(dict(market=p.market, region=p.region, kind=p.kind, late=p.late, old=p.old, window=wname,
                                 side=side, vintage=p.late if side == "late" else p.old, win_start=str(b0.date()),
                                 win_end=str(b1.date()), weights_src=wsrc, **st))
        print(p.market, p.kind, p.late, p.old, "done", flush=True)
    mw = pd.DataFrame(rows)
    for b in BUCKETS:
        mw[f"share_{b}"] = mw[f"nights_{b}"] / mw[[f"nights_{x}" for x in BUCKETS]].sum(axis=1)
        mw[f"w_share_{b}"] = mw[f"w_nights_{b}"] / mw["w_nights"]
    mw.to_csv(OUT / "I2_los_market_windows.csv", index=False)

    # --- regional and global term -------------------------------------------------------
    term = []
    mw["year"] = mw.late.str[:4].astype(int)
    for (year, kind, wname), g in mw.groupby(["year", "kind", "window"]):
        for weighting, pre in (("occupancy_weighted", "w_"), ("unweighted", "")):
            regrows = {}
            for reg, gr in g[~g.market.isin(REG_MIN)].groupby("region"):
                sh = {}
                for side in ("late", "old"):
                    s = gr[gr.side.eq(side)]
                    tot = s[[f"{pre}nights_{b}" for b in BUCKETS]].sum().sum()
                    sh[side] = {b: s[f"{pre}nights_{b}"].sum() / tot if tot else np.nan for b in BUCKETS}
                mix = sum((sh["late"][b] - sh["old"][b]) * (RATIO[b] - 1) for b in BUCKETS) * 100
                nm = gr[gr.side.eq("late")].market.nunique()
                row = dict(year=year, kind=kind, window=wname, weighting=weighting, region=reg, n_markets=nm,
                           los_mix_pp=mix, **{f"share_{b}_late": sh["late"][b] for b in BUCKETS},
                           **{f"share_{b}_old": sh["old"][b] for b in BUCKETS},
                           **{f"d_share_{b}_pp": 100 * (sh["late"][b] - sh["old"][b]) for b in BUCKETS},
                           mean_run_late=gr[gr.side.eq("late")].mean_run_cap90.mean(),
                           mean_run_old=gr[gr.side.eq("old")].mean_run_cap90.mean(),
                           n_runs_late=int(gr[gr.side.eq("late")].n_runs.sum()), n_runs_old=int(gr[gr.side.eq("old")].n_runs.sum()))
                regrows[reg] = row
                term.append(row)
            if all(r in regrows for r in TENK_W):
                gl = dict(year=year, kind=kind, window=wname, weighting=weighting, region="global_10k_weighted",
                          n_markets=sum(regrows[r]["n_markets"] for r in TENK_W),
                          los_mix_pp=sum(TENK_W[r] * regrows[r]["los_mix_pp"] for r in TENK_W))
                for b in BUCKETS:
                    for side in ("late", "old"):
                        gl[f"share_{b}_{side}"] = sum(TENK_W[r] * regrows[r][f"share_{b}_{side}"] for r in TENK_W)
                    gl[f"d_share_{b}_pp"] = sum(TENK_W[r] * regrows[r][f"d_share_{b}_pp"] for r in TENK_W)
                term.append(gl)
            # market-level dispersion for the band
            md = []
            for mk, gm in g[~g.market.isin(REG_MIN)].groupby("market"):
                if set(gm.side) != {"late", "old"}:
                    continue
                shl = gm[gm.side.eq("late")].iloc[0]; sho = gm[gm.side.eq("old")].iloc[0]
                md.append(sum((shl[f"{pre}share_{b}"] - sho[f"{pre}share_{b}"]) * (RATIO[b] - 1) for b in BUCKETS) * 100)
            if md:
                term.append(dict(year=year, kind=kind, window=wname, weighting=weighting, region="market_dispersion",
                                 n_markets=len(md), los_mix_pp=float(np.median(md)), los_mix_p25=float(np.percentile(md, 25)),
                                 los_mix_p75=float(np.percentile(md, 75)), los_mix_sd=float(np.std(md, ddof=1)) if len(md) > 1 else np.nan))
    term = pd.DataFrame(term)
    term.to_csv(OUT / "I2_los_term.csv", index=False)
    pd.set_option("display.width", 250)
    print(term[term.region.isin(["global_10k_weighted", "market_dispersion"]) | term.region.isin(TENK_W)]
          [["year", "kind", "window", "weighting", "region", "n_markets", "share_ge28_old", "share_ge28_late", "d_share_ge28_pp", "los_mix_pp"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()

