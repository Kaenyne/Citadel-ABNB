"""14a. What does a night cost, by length of stay? (step 1 of the LOS build for the ADR model)

The question
  ADR is GBV / nights. If the stay-length mix moves -- more 7-27 night stays, more 28+ night
  stays -- ADR per night falls mechanically, because Airbnb hosts set weekly and monthly
  discounts and Airbnb itself funds an extra "monthly stay savings" line. Before modelling any
  mix shift we need the price wedge each bucket carries. This script measures it from host
  discount structures in the 2026 Inside Airbnb stay quotes.

  Three buckets, by the length of the quoted stay: under 7 nights (no length discount can
  apply), 7-27 nights (the weekly discount applies), 28+ nights (the monthly discount applies).

Method
  Every 2026 Inside Airbnb dump from 2026-03-16 carries ONE stay quote per listing, for the
  first available window. price_quote_raw is a JSON quote whose raw_price_line_items are an
  exact ledger: an undiscounted base line, then signed discount lines, summing to the
  discounted subtotal (verified to 5e-6 relative error on 183k quotes). Two base labels:
      nightly_subtotal   "3 nights x 182.59"       short stays
      other              "Average monthly price"   28+ stays -- despite the label this is the
                                                   undiscounted subtotal for the WHOLE stay
  Discount lines enumerated across six large markets (every distinct description found):
      discount_amount  Weekly stay discount     length-of-stay, host funded
      discount_amount  Monthly stay discount    length-of-stay, host funded
      discount_amount  Long stay discount       length-of-stay, host funded (custom threshold)
      discount_amount  Special offer            host promo, any length (new-listing / bespoke)
      discount_amount  Early booking discount   timing, host funded
      discount_amount  Last-minute discount     timing, host funded
      other            Airbnb monthly stay savings   PLATFORM funded, 28+ only
      taxes            Taxes / Taxes and fees   excluded (guest-side, not in the ADR base)
      other            Resort fee               excluded (a surcharge, not a discount)
      other            Total / Monthly total    the tax-inclusive footer, not a price line
  Per quote we take rates as a fraction of the undiscounted base, so the discount RATE is
  recoverable regardless of the quoted stay length, and form three per-night price factors
  relative to that listing's own undiscounted rate:
      f_los       1 - (weekly + monthly + long) / base       length-of-stay discounts only
      f_host      1 - (all host discount lines) / base       host discount, any reason
      f_hostplat  f_host - (Airbnb monthly savings) / base   host plus platform funded
  The bucket price ratio is mean(f | bucket) / mean(f | under 7), unweighted and weighted by
  estimated_occupancy_l365d (estimated nights booked, capped at 0.7*365). Dividing by the
  under-7 mean nets out the discounting a short stay already carries (last-minute offers are
  common there, because the quoted window is the first AVAILABLE one and so is near-term).

  THE SELECTION PROBLEM, stated plainly. Each listing is quoted once, and the quoted length is
  set by minimum_nights, so the 28+ bucket is mostly listings that REQUIRE 28+ -- in New York
  City that is Local Law 18, not guest demand. So: (a) ratios are reported by QUOTED-stay
  bucket, never as a realised mix; (b) markets where minimum_nights >= 28 exceeds 30% of
  listings are flagged `regulatory_min` and excluded from the regional and global headline;
  (c) the incidence shares (what fraction of listings offer a weekly / monthly discount) are
  conditional on being quoted in that bucket and are NOT population incidence. The discount
  RATES are listing-level parameters and travel better than the incidence does.

Outputs
  data/processed/adr/14a_los_discount_by_listing_summary.csv  scope x region x market x bucket
  data/processed/adr/14a_los_bucket_price_ratios.csv          region x bucket headline ratios
Run
  py -3.13 analysis/src/adr/14a_los_discount_ratios.py <dump_inventory.csv>
"""
import json
import os
import sys
import time
from collections import defaultdict

import numpy as np
import pandas as pd

RAW = "data/raw/inside_airbnb"
OUT = "data/processed/adr"
CAP = 0.7 * 365                      # estimated_occupancy_l365d is censored here
MIN_CELL = 100                       # below this a bucket ratio is not reported
REG_MIN_THRESH = 0.30                # share of listings with minimum_nights >= 28
NIGHTS_SHARE = {"na": 0.296, "emea": 0.403, "latam": 0.169, "apac": 0.131}  # 2025 10-K

REGION = {"new-york-city": "na", "los-angeles": "na", "chicago": "na", "austin": "na",
          "nashville": "na", "new-orleans": "na", "san-diego": "na", "paris": "emea",
          "london": "emea", "barcelona": "emea", "rome": "emea", "sydney": "apac",
          "mexico-city": "latam", "bangkok": "apac", "tokyo": "apac", "taipei": "apac",
          "singapore": "apac", "hong-kong": "apac", "brisbane": "apac", "melbourne": "apac",
          "barossa-valley": "apac", "barwon-south-west-vic": "apac", "mid-north-coast": "apac",
          "mornington-peninsula": "apac", "northern-rivers": "apac", "sunshine-coast": "apac",
          "tasmania": "apac", "western-australia": "apac", "belize": "latam",
          "rio-de-janeiro": "latam", "santiago": "latam", "buenos-aires": "latam",
          "bogota": "latam", "sao-paulo": "latam"}

BUCKETS = ["lt7", "7_27", "ge28"]
# discount families -> the raw line-item descriptions that map into them
FAMILY = {"weekly": ("Weekly stay discount",),
          "monthly": ("Monthly stay discount",),
          "longstay": ("Long stay discount",),
          "special": ("Special offer",),
          "early": ("Early booking discount",),
          "lastmin": ("Last-minute discount",)}
DESC2FAM = {d: f for f, ds in FAMILY.items() for d in ds}
FAMS = list(FAMILY) + ["other_host", "los_total", "host_all", "platform"]
FACTORS = ["f_los", "f_host", "f_hostplat"]


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def parse_quote(s):
    """One raw quote -> (base, {family: amount}) or None if unavailable / unparseable."""
    try:
        q = (json.loads(s) or {}).get("quote") or {}
    except Exception:
        return None
    base = None
    d = defaultdict(float)
    for it in q.get("raw_price_line_items") or []:
        t = it.get("item_type")
        de = it.get("description") or ""
        try:
            a = float(it["amount"])
        except (TypeError, ValueError, KeyError):
            continue
        if t == "nightly_subtotal" or de == "Average monthly price":
            base = a
        elif t == "discount_amount":
            d[DESC2FAM.get(de, "other_host")] += abs(a)
        elif t == "other" and "savings" in de.lower():
            d["platform"] += abs(a)
        # taxes, Resort fee, Total, Monthly total, discounted_subtotal: not price lines
    if base is None or base <= 0:
        return None
    return base, d


def blank():
    z = dict(n=0.0, nights=0.0, n_min_ge28=0.0, n_min_ge7=0.0, n_entire=0.0,
             sum_base_pn=0.0, sum_w_base_pn=0.0, sum_nights_stay=0.0)
    for f in FAMS:
        z[f"n_with_{f}"] = 0.0
        z[f"nights_with_{f}"] = 0.0
        z[f"sum_rate_{f}"] = 0.0          # over every quote in the cell, zeros included
        z[f"sum_w_rate_{f}"] = 0.0
        z[f"sum_rate_cond_{f}"] = 0.0     # over quotes that carry the discount
        z[f"sum_w_rate_cond_{f}"] = 0.0
    for f in FACTORS:
        z[f"sum_{f}"] = 0.0
        z[f"sum_w_{f}"] = 0.0
    return z


def scan_dump(market, date):
    """Aggregate one dump into {bucket: accumulator}. Only the needed columns are read."""
    cols = ["id", "room_type", "minimum_nights", "estimated_occupancy_l365d",
            "price_quote_checkin_date", "price_quote_checkout_date",
            "price_quote_price_per_night", "price_quote_raw"]
    df = pd.read_csv(f"{RAW}/{market}_{date}_listings.csv.gz", usecols=cols, low_memory=False)
    nights = (pd.to_datetime(df["price_quote_checkout_date"], errors="coerce")
              - pd.to_datetime(df["price_quote_checkin_date"], errors="coerce")).dt.days
    w = pd.to_numeric(df["estimated_occupancy_l365d"], errors="coerce").fillna(0).clip(0, CAP)
    minn = pd.to_numeric(df["minimum_nights"], errors="coerce")
    entire = df["room_type"].eq("Entire home/apt")
    acc = {b: blank() for b in BUCKETS}
    n_raw = n_unavail = n_bad = 0
    for s, nn, ww, mn, en in zip(df["price_quote_raw"], nights, w, minn, entire):
        if not isinstance(s, str):
            continue
        n_raw += 1
        if not (nn == nn) or nn <= 0:
            n_bad += 1
            continue
        p = parse_quote(s)
        if p is None:
            n_unavail += 1
            continue
        base, d = p
        d["los_total"] = d["weekly"] + d["monthly"] + d["longstay"]
        d["host_all"] = sum(d[f] for f in list(FAMILY) + ["other_host"])
        if d["host_all"] + d["platform"] > base:      # ledger implies price <= 0; discard
            n_bad += 1
            continue
        b = "lt7" if nn < 7 else ("7_27" if nn < 28 else "ge28")
        a = acc[b]
        a["n"] += 1
        a["nights"] += ww
        a["n_min_ge28"] += float(mn >= 28) if mn == mn else 0.0
        a["n_min_ge7"] += float(mn >= 7) if mn == mn else 0.0
        a["n_entire"] += float(en)
        a["sum_nights_stay"] += nn
        bpn = base / nn
        a["sum_base_pn"] += bpn
        a["sum_w_base_pn"] += ww * bpn
        for f in FAMS:
            r = d[f] / base
            a[f"sum_rate_{f}"] += r
            a[f"sum_w_rate_{f}"] += ww * r
            if r > 0:
                a[f"n_with_{f}"] += 1
                a[f"nights_with_{f}"] += ww
                a[f"sum_rate_cond_{f}"] += r
                a[f"sum_w_rate_cond_{f}"] += ww * r
        fl = 1 - d["los_total"] / base
        fh = 1 - d["host_all"] / base
        fp = fh - d["platform"] / base
        for k, v in (("f_los", fl), ("f_host", fh), ("f_hostplat", fp)):
            a[f"sum_{k}"] += v
            a[f"sum_w_{k}"] += ww * v
    log(f"  {market} {date}: {n_raw} quotes, {n_unavail} unavailable, {n_bad} dropped, "
        + " ".join(f"{b}={int(acc[b]['n'])}" for b in BUCKETS))
    return acc


def add(x, y):
    return {k: x[k] + y[k] for k in x}


def cell_stats(a):
    """Accumulator -> reportable means. NaN where the cell is empty."""
    n, W = a["n"], a["nights"]
    r = dict(n_quotes=int(n), nights_l365d=W, n_entire=int(a["n_entire"]),
             share_entire=a["n_entire"] / n if n else np.nan,
             mean_quoted_nights=a["sum_nights_stay"] / n if n else np.nan,
             share_min_nights_ge28=a["n_min_ge28"] / n if n else np.nan,
             share_min_nights_ge7=a["n_min_ge7"] / n if n else np.nan,
             mean_base_price_per_night_lcy=a["sum_base_pn"] / n if n else np.nan,
             wmean_base_price_per_night_lcy=a["sum_w_base_pn"] / W if W else np.nan)
    for f in FAMS:
        nf, Wf = a[f"n_with_{f}"], a[f"nights_with_{f}"]
        r[f"share_with_{f}"] = nf / n if n else np.nan
        r[f"nights_share_with_{f}"] = Wf / W if W else np.nan
        r[f"mean_rate_{f}"] = a[f"sum_rate_{f}"] / n if n else np.nan
        r[f"wmean_rate_{f}"] = a[f"sum_w_rate_{f}"] / W if W else np.nan
        r[f"mean_rate_{f}_cond"] = a[f"sum_rate_cond_{f}"] / nf if nf else np.nan
        r[f"wmean_rate_{f}_cond"] = a[f"sum_w_rate_cond_{f}"] / Wf if Wf else np.nan
    for f in FACTORS:
        r[f"mean_{f}"] = a[f"sum_{f}"] / n if n else np.nan
        r[f"wmean_{f}"] = a[f"sum_w_{f}"] / W if W else np.nan
    return r


def ratios(cells):
    """{bucket: stats} -> per-night price ratio of each bucket vs under-7."""
    out = {}
    ref = cells.get("lt7")
    for b in BUCKETS:
        c = cells.get(b)
        for f in FACTORS:
            for tag, key in (("", "mean_"), ("_nw", "wmean_")):
                k = f"ratio_{f[2:]}{tag}"
                v = np.nan
                if (c and ref and c["n_quotes"] >= MIN_CELL and ref["n_quotes"] >= MIN_CELL
                        and ref[key + f] == ref[key + f] and ref[key + f] > 0
                        and c[key + f] == c[key + f]):
                    v = c[key + f] / ref[key + f]
                out.setdefault(b, {})[k] = v
    return out


def main():
    inv = pd.read_csv(sys.argv[1])
    inv = inv[inv.quote_nn > 0.3].copy()
    inv["date"] = pd.to_datetime(inv["date"])
    inv = inv.sort_values(["market", "date"])
    log(f"{inv.market.nunique()} markets, {len(inv)} quote dumps")

    per_dump = {}                                  # (market, date) -> {bucket: acc}
    for i, r in enumerate(inv.itertuples(), 1):
        d = r.date.strftime("%Y-%m-%d")
        if not os.path.exists(f"{RAW}/{r.market}_{d}_listings.csv.gz"):
            log(f"  MISSING {r.market} {d}")
            continue
        log(f"[{i}/{len(inv)}] {r.market} {d}")
        per_dump[(r.market, d)] = scan_dump(r.market, d)

    latest = {m: max(d for (mm, d) in per_dump if mm == m)
              for m in {mm for mm, _ in per_dump}}

    # ---- market level, two scopes -------------------------------------------------------
    mk_acc = {}
    for scope in ("latest_dump", "pooled_2026"):
        for m in latest:
            keys = [(m, latest[m])] if scope == "latest_dump" else [k for k in per_dump if k[0] == m]
            a = {b: blank() for b in BUCKETS}
            for k in keys:
                for b in BUCKETS:
                    a[b] = add(a[b], per_dump[k][b])
            mk_acc[(scope, m)] = (a, sorted(d for _, d in keys))

    rows = []
    for (scope, m), (a, dates) in mk_acc.items():
        cells = {b: cell_stats(a[b]) for b in BUCKETS}
        tot = sum(cells[b]["n_quotes"] for b in BUCKETS)
        totw = sum(a[b]["nights"] for b in BUCKETS)
        allm = cell_stats({k: sum(a[b][k] for b in BUCKETS) for k in a["lt7"]})
        reg_min = allm["share_min_nights_ge28"] >= REG_MIN_THRESH
        rt = ratios(cells)
        for b in BUCKETS:
            rows.append(dict(scope=scope, level="market", region=REGION.get(m, "?"), market=m,
                             bucket=b, n_dumps=len(dates), dump_dates=";".join(dates),
                             share_of_quotes=cells[b]["n_quotes"] / tot if tot else np.nan,
                             nights_share_of_quotes=a[b]["nights"] / totw if totw else np.nan,
                             market_share_min_nights_ge28=allm["share_min_nights_ge28"],
                             regulatory_min_market=bool(reg_min),
                             **cells[b], **rt[b]))

    # ---- region and global, pooling listings across the region's markets ----------------
    for scope in ("latest_dump", "pooled_2026"):
        for excl in (True, False):
            groups = defaultdict(list)
            for m in latest:
                a, dates = mk_acc[(scope, m)]
                allm = cell_stats({k: sum(a[b][k] for b in BUCKETS) for k in a["lt7"]})
                if excl and allm["share_min_nights_ge28"] >= REG_MIN_THRESH:
                    continue
                groups[REGION.get(m, "?")].append((m, a))
                groups["global_pooled"].append((m, a))
            for reg, items in groups.items():
                acc = {b: blank() for b in BUCKETS}
                for _, a in items:
                    for b in BUCKETS:
                        acc[b] = add(acc[b], a[b])
                cells = {b: cell_stats(acc[b]) for b in BUCKETS}
                tot = sum(cells[b]["n_quotes"] for b in BUCKETS)
                totw = sum(acc[b]["nights"] for b in BUCKETS)
                allm = cell_stats({k: sum(acc[b][k] for b in BUCKETS) for k in acc["lt7"]})
                rt = ratios(cells)
                for b in BUCKETS:
                    rows.append(dict(scope=scope,
                                     level="region" if reg != "global_pooled" else "global",
                                     region=reg,
                                     market="ALL" + ("_ex_regulatory_min" if excl else ""),
                                     bucket=b, n_dumps=len(items), dump_dates="",
                                     share_of_quotes=cells[b]["n_quotes"] / tot if tot else np.nan,
                                     nights_share_of_quotes=acc[b]["nights"] / totw if totw else np.nan,
                                     market_share_min_nights_ge28=allm["share_min_nights_ge28"],
                                     regulatory_min_market=False, **cells[b], **rt[b]))
    summ = pd.DataFrame(rows).sort_values(["scope", "level", "region", "market", "bucket"])
    os.makedirs(OUT, exist_ok=True)
    summ.to_csv(f"{OUT}/14a_los_discount_by_listing_summary.csv", index=False)
    log(f"wrote {OUT}/14a_los_discount_by_listing_summary.csv ({len(summ)} rows)")

    # ---- headline table ------------------------------------------------------------------
    head = []
    src = summ[summ.market.eq("ALL_ex_regulatory_min")]
    for scope in ("latest_dump", "pooled_2026"):
        s = src[src.scope.eq(scope)]
        for reg in ["na", "emea", "latam", "apac", "global_pooled"]:
            g = s[s.region.eq(reg)]
            for b in BUCKETS:
                r = g[g.bucket.eq(b)]
                if r.empty:
                    continue
                r = r.iloc[0]
                head.append(dict(scope=scope, region=reg, bucket=b, n_quotes=int(r.n_quotes),
                                 n_markets=int(r.n_dumps), share_of_quotes=r.share_of_quotes,
                                 nights_share_of_quotes=r.nights_share_of_quotes,
                                 ratio_host=r.ratio_host_nw, ratio_hostplat=r.ratio_hostplat_nw,
                                 ratio_los_only=r.ratio_los_nw, ratio_host_unweighted=r.ratio_host,
                                 ratio_hostplat_unweighted=r.ratio_hostplat,
                                 share_with_weekly=r.share_with_weekly,
                                 share_with_monthly=r.share_with_monthly,
                                 share_with_platform=r.share_with_platform,
                                 wmean_rate_los_total=r.wmean_rate_los_total,
                                 wmean_rate_platform=r.wmean_rate_platform))
    h = pd.DataFrame(head)
    # 10-K-weighted global row: weight the four regional ratios by 2025 regional nights shares
    for scope in ("latest_dump", "pooled_2026"):
        for b in BUCKETS:
            g = h[h.scope.eq(scope) & h.bucket.eq(b) & h.region.isin(NIGHTS_SHARE)]
            row = dict(scope=scope, region="global_10k_nights_weighted", bucket=b,
                       n_quotes=int(g.n_quotes.sum()), n_markets=int(g.n_markets.sum()),
                       share_of_quotes=np.nan, nights_share_of_quotes=np.nan)
            for c in ("ratio_host", "ratio_hostplat", "ratio_los_only", "ratio_host_unweighted",
                      "ratio_hostplat_unweighted", "share_with_weekly", "share_with_monthly",
                      "share_with_platform", "wmean_rate_los_total", "wmean_rate_platform"):
                wgt = g.region.map(NIGHTS_SHARE).where(g[c].notna())
                row[c] = float((g[c] * wgt).sum() / wgt.sum()) if wgt.sum() > 0 else np.nan
            row["regions_covered"] = ",".join(sorted(g.region[g.ratio_host.notna()]))
            head.append(row)
    h = pd.DataFrame(head)
    h["basis"] = ("per-night price relative to the same listing's undiscounted nightly rate, "
                  "indexed to the under-7-night bucket = 1.00; nights-weighted by "
                  "estimated_occupancy_l365d unless the column says unweighted")
    h["caveats"] = ("QUOTED-stay bucket, not realised stay mix: each listing carries one quote "
                    "for its first available window, so bucket membership is largely set by "
                    "minimum_nights. Markets with >=30% of listings at minimum_nights>=28 "
                    "(regulatory minimums) are excluded. Incidence shares are conditional on "
                    "being quoted in the bucket and are not population incidence. The ratio is "
                    "the discount effect only -- it does not include any difference in the "
                    "underlying nightly rate of listings that accept long stays. Fees and taxes "
                    "are absent from these quotes, so this is a subtotal basis.")
    h.to_csv(f"{OUT}/14a_los_bucket_price_ratios.csv", index=False)
    log(f"wrote {OUT}/14a_los_bucket_price_ratios.csv ({len(h)} rows)")

    pd.set_option("display.width", 260)
    print("\n=== headline ratios (latest dump per market, ex regulatory-min markets) ===")
    print(h[h.scope.eq("latest_dump")][["region", "bucket", "n_quotes", "share_of_quotes",
          "ratio_host", "ratio_hostplat", "ratio_los_only", "share_with_weekly",
          "share_with_monthly", "share_with_platform"]].round(4).to_string(index=False))
    print("\n=== pooled 2026 robustness ===")
    print(h[h.scope.eq("pooled_2026")][["region", "bucket", "n_quotes", "ratio_host",
          "ratio_hostplat", "ratio_los_only"]].round(4).to_string(index=False))
    print("\n=== by market (latest dump) ===")
    mm = summ[summ.scope.eq("latest_dump") & summ.level.eq("market")]
    print(mm[["region", "market", "bucket", "n_quotes", "share_of_quotes",
              "market_share_min_nights_ge28", "regulatory_min_market", "share_with_weekly",
              "share_with_monthly", "share_with_platform", "mean_rate_weekly_cond",
              "mean_rate_monthly_cond", "ratio_host_nw", "ratio_hostplat_nw"]]
          .round(3).to_string(index=False))


if __name__ == "__main__":
    main()
