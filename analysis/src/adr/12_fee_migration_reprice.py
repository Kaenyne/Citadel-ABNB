"""12. How much did hosts reprice when they moved to the single 15.5% fee?

Why it matters for ADR
  ADR is GBV / nights and GBV is gross of the guest fee, so the migration moves ADR only
  through host repricing: guest total per $100 of old subtotal goes 114 -> 100 + 14.8*theta,
  where theta is the fraction of the payout-neutral reprice (+14.8%) the host applies.
  theta = 1 is +0.7% ADR on the migrated cohort; theta = 0 is -12.3%; the forum "+18.3%"
  advice is +3.8%. The migration is already about half done (Q2'26 call), and every 2026
  Inside Airbnb monthly dump from March on is on the same stay-quote basis, so a host who
  switched between two consecutive dumps shows up as a discrete same-listing jump in the
  undiscounted nightly rate. This script measures the excess mass of such jumps.

Method
  Sequential same-basis pairs (Mar->Apr->...->Aug 2026), every market with quote dumps.
  Price = undiscounted nightly subtotal / nights from the raw quote, stays <= 7 nights at
  both ends (so length-of-stay discounts do not masquerade as repricing). Log change per
  matched listing, binned at 1pp. The migration signature is excess density in +12..+20pp
  over a local baseline (the mean density of +6..+10 and +22..+26). Excess share = share of
  listings that repriced in the window; the excess-weighted mean jump is theta * 14.8.

Outputs
  data/processed/adr/12_reprice_hist.csv      bin counts per pair (all + entire homes)
  data/processed/adr/12_reprice_summary.csv   excess share, mean jump, theta per pair/market
Run
  py -3.13 analysis/src/adr/12_fee_migration_reprice.py <dump_inventory.csv>
"""
import json
import sys
import time

import numpy as np
import pandas as pd

RAW = "data/raw/inside_airbnb"
OUT = "data/processed/adr"
CAP = 0.7 * 365
BINS = np.arange(-0.40, 0.505, 0.01)


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def quote_base(s):
    try:
        q = (json.loads(s) or {}).get("quote") or {}
        for it in q.get("raw_price_line_items") or []:
            if it.get("item_type") == "nightly_subtotal":
                return float(it["amount"])
    except Exception:
        return np.nan
    return np.nan


def load(market, date):
    f = f"{RAW}/{market}_{date}_listings.csv.gz"
    cols = ["id", "room_type", "estimated_occupancy_l365d", "price_quote_checkin_date",
            "price_quote_checkout_date", "price_quote_raw"]
    df = pd.read_csv(f, usecols=cols, low_memory=False)
    n = (pd.to_datetime(df["price_quote_checkout_date"], errors="coerce")
         - pd.to_datetime(df["price_quote_checkin_date"], errors="coerce")).dt.days
    sub = df["price_quote_raw"].map(quote_base, na_action="ignore")
    df["p"] = (sub / n.where(n > 0)).where(n.le(7))
    df["w"] = pd.to_numeric(df["estimated_occupancy_l365d"], errors="coerce").fillna(0).clip(0, CAP)
    df["entire"] = df["room_type"].eq("Entire home/apt")
    return df[["id", "p", "w", "entire"]].dropna(subset=["p"])


def excess(counts):
    """Excess mass in +12..+20pp over a local baseline, and the mean jump inside it."""
    centers = BINS[:-1] + 0.005
    sig = (centers >= 0.115) & (centers < 0.205)
    base = ((centers >= 0.055) & (centers < 0.105)) | ((centers >= 0.215) & (centers < 0.265))
    b = counts[base].mean()
    ex = np.clip(counts[sig] - b, 0, None)
    tot = counts.sum()
    if tot == 0 or ex.sum() == 0:
        return 0.0, np.nan, b * sig.sum() / tot
    return ex.sum() / tot, float((ex * centers[sig]).sum() / ex.sum()), b * sig.sum() / tot


def main():
    inv = pd.read_csv(sys.argv[1])
    inv = inv[inv.quote_nn > 0.3].copy()
    inv["date"] = pd.to_datetime(inv["date"])
    hist, summ = [], []
    for mk, g in inv.sort_values("date").groupby("market"):
        dates = g.date.dt.strftime("%Y-%m-%d").tolist()
        prev = None
        for d in dates:
            cur = load(mk, d)
            if prev is not None:
                pd_, pdate = prev
                m = pd_.merge(cur, on="id", suffixes=("_a", "_b"))
                m = m[(m.p_a >= 10) & (m.p_b >= 10)]
                m["d"] = np.log(m.p_b / m.p_a)
                for seg, mm in (("all", m), ("entire", m[m.entire_a])):
                    c, _ = np.histogram(mm.d, bins=BINS)
                    cw, _ = np.histogram(mm.d, bins=BINS, weights=mm.w_a)
                    for tag, cc in (("count", c), ("nights", cw)):
                        hist.append(dict(market=mk, date_a=pdate, date_b=d, segment=seg,
                                         weight=tag, **{f"b{round(x, 2):+.2f}": v for x, v in zip(BINS[:-1], cc)}))
                        sh, mj, bl = excess(cc.astype(float))
                        summ.append(dict(market=mk, date_a=pdate, date_b=d, segment=seg, weight=tag,
                                         n_matched=len(mm), share_unchanged=float((mm.d.abs() < 0.005).mean()),
                                         excess_share_12_20=sh, baseline_share_12_20=bl,
                                         mean_jump_pp=mj * 100 if mj == mj else np.nan,
                                         theta=mj / 0.138 if mj == mj else np.nan,
                                         share_gt_10=float((mm.d > 0.10).mean()),
                                         share_lt_m10=float((mm.d < -0.10).mean())))
                log(f"{mk} {pdate} -> {d}: {len(m)} matched")
            prev = (cur, d)
    pd.DataFrame(hist).to_csv(f"{OUT}/12_reprice_hist.csv", index=False)
    s = pd.DataFrame(summ)
    s.to_csv(f"{OUT}/12_reprice_summary.csv", index=False)
    pd.set_option("display.width", 250)
    print(s[s.segment.eq("entire") & s.weight.eq("count")].round(3).to_string())


if __name__ == "__main__":
    main()
