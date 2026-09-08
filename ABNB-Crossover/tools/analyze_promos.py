"""Analyze promo_intensity.csv: promo depth/frequency/breadth by banner over time,
y/y deltas, and the cuts that test management's merchandise-margin story.

PRIMARY METRIC = event_depth = the deepest TIME-LIMITED promotional offer advertised on the
homepage, across both the hero strip and the promoted-offer nav block. Permanent store
furniture (military discount, pre-owned, outlet, the standing "up to 50% off clearance"
department, and "50% off & up" clearance floors) is stripped out - left in, it pins the
series at a constant ~50 and destroys every y/y comparison. `promo_depth` (furniture
included) is kept in the CSV for transparency.

SECONDARY = sitewide_pct, the rate attached to the word "Everything". This is depth x breadth
in a single number and is the sharpest test of the Q4 FY26 "broader promotions" pivot.

Signet FY ends ~Feb 1: Q1 = Feb-Apr, Q2 = May-Jul, Q3 = Aug-Oct, Q4 = Nov-Jan.
"""
import csv, os, statistics as st
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(os.path.dirname(HERE), "promo_intensity.csv")
M = "event_depth"
B = "n_event_offers"


def fq(ym):
    y, m = int(ym[:4]), int(ym[5:7])
    if m == 1:
        fy, q = y, 4
    else:
        fy, q = y + 1, (m - 2) // 3 + 1
    return f"FY{str(fy)[2:]} Q{q}"


def load():
    allrows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    # keep only captures where a canonical promo region was actually located; the
    # pre-Aug-2024 skin has neither, and zero-filling it would fake a discipline trend
    rows = [r for r in allrows if r["comparable"] == "1"]
    print(f"(loaded {len(allrows)} rows; {len(allrows)-len(rows)} dropped as "
          f"non-comparable legacy template)")
    for r in rows:
        for k in (M, B, "max_pct_off", "promo_depth", "n_pct_offers", "sitewide_pct",
                  "hero_max_pct_off", "deals_max_pct_off"):
            r[k] = float(r[k])
        r["ym"] = r["date"][:7]
        r["fq"] = fq(r["ym"])
    return rows


def stats(v):
    p = [r[M] for r in v]
    return dict(
        n=len(v),
        mean=round(st.mean(p), 1),
        median=round(st.median(p), 1),
        frq=round(100 * sum(1 for x in p if x > 0) / len(p)),      # "days on sale"
        deep=round(100 * sum(1 for x in p if x >= 50) / len(p)),   # depth >= 50%
        brd=round(st.mean([r[B] for r in v]), 1),                 # concurrent events
    )


def agg(rows, keyf):
    d = defaultdict(list)
    for r in rows:
        d[keyf(r)].append(r)
    return {k: stats(v) for k, v in sorted(d.items())}


def table(title, a, prevkey):
    print(f"\n{title}")
    print(f"{'period':10} {'n':>3} {'mean%':>6} {'med%':>5} {'%obs w/':>8} {'%obs':>6} "
          f"{'breadth':>8} | {'y/y mean':>9} {'y/y frq':>8} {'y/y brd':>8}")
    print(f"{'':10} {'':>3} {'':>6} {'':>5} {'offer':>8} {'>=50':>6} {'(#offers)':>8}")
    print("-" * 92)
    for k, v in a.items():
        p = a.get(prevkey(k))
        ym = f"{v['mean']-p['mean']:+.1f}" if p else ""
        yf = f"{v['frq']-p['frq']:+.0f}" if p else ""
        yb = f"{v['brd']-p['brd']:+.1f}" if p else ""
        print(f"{k:10} {v['n']:>3} {v['mean']:>6} {v['median']:>5} {v['frq']:>8} "
              f"{v['deep']:>6} {v['brd']:>8} | {ym:>9} {yf:>8} {yb:>8}")


def window(rows, months, label):
    w = [r for r in rows if r["ym"] in months]
    if not w:
        return None
    s = stats(w)
    print(f"  {label:22} n={s['n']:>3}  mean={s['mean']:>5}  med={s['median']:>5}  "
          f"offer%={s['frq']:>3}  >=50%={s['deep']:>3}  breadth={s['brd']}")
    return s


def main():
    rows = load()
    print(f"PANEL: {len(rows)} observations")
    banners = sorted(set(r["banner"] for r in rows))
    for b in banners:
        br = [r for r in rows if r["banner"] == b]
        src = defaultdict(int)
        for r in br:
            src[r["source"]] += 1
        print(f"  {b:6} {len(br):>3} obs | {br[0]['date']} -> {br[-1]['date']} | "
              f"{len(set(r['ym'] for r in br))} months | {dict(src)}")

    for b in banners:
        br = [r for r in rows if r["banner"] == b]
        table(f"===== {b.upper()} — BY MONTH =====", agg(br, lambda r: r["ym"]),
              lambda k: f"{int(k[:4])-1}{k[4:]}")
        table(f"===== {b.upper()} — BY FISCAL QUARTER =====", agg(br, lambda r: r["fq"]),
              lambda k: f"FY{int(k[2:4])-1:02d} {k[5:]}")

    print("\n\n########## THE FOUR TESTS ##########")
    tests = [
        ("P1  Q3 FY26 vs Q3 FY25 (merch mgn +80bps)",
         ["2025-08", "2025-09", "2025-10"], ["2024-08", "2024-09", "2024-10"]),
        ("P2  Q4 FY26 vs Q4 FY25 (merch mgn -30bps, PIVOT)",
         ["2025-11", "2025-12", "2026-01"], ["2024-11", "2024-12", "2025-01"]),
        ("P3  Q1 FY27 vs Q1 FY26 (merch mgn -70bps, GOLD)",
         ["2026-02", "2026-03", "2026-04"], ["2025-02", "2025-03", "2025-04"]),
        ("P4  Q2 FY27 vs Q2 FY26 (guided 'somewhat lower')",
         ["2026-05", "2026-06", "2026-07"], ["2025-05", "2025-06", "2025-07"]),
        ("P4b LIVE Jul-Aug 2026 vs Jul-Aug 2025",
         ["2026-07", "2026-08"], ["2025-07", "2025-08"]),
    ]
    for b in banners:
        br = [r for r in rows if r["banner"] == b]
        print(f"\n--- {b.upper()} ---")
        for label, cur, prev in tests:
            print(f"\n{label}")
            c = window(br, cur, "current")
            p = window(br, prev, "prior year")
            if c and p:
                print(f"  {'DELTA':22} mean={c['mean']-p['mean']:+.1f}pts  "
                      f"offer%={c['frq']-p['frq']:+.0f}  >=50%={c['deep']-p['deep']:+.0f}  "
                      f"breadth={c['brd']-p['brd']:+.1f}")

    print("\n\n########## HOLIDAY DETAIL (Nov / Dec / Jan) ##########")
    for b in banners:
        br = [r for r in rows if r["banner"] == b]
        a = agg(br, lambda r: r["ym"])
        print(f"\n{b}:")
        for ym in sorted(a):
            if ym[5:7] in ("11", "12", "01"):
                v = a[ym]
                print(f"  {ym}  n={v['n']:>2}  mean={v['mean']:>5}  med={v['median']:>5}  "
                      f"offer%={v['frq']:>3}  >=50%={v['deep']:>3}  breadth={v['brd']}")

    print("\n\n########## PROMO-TYPE MIX (share of obs by calendar year) ##########")
    for b in banners:
        br = [r for r in rows if r["banner"] == b]
        years = sorted(set(r["date"][:4] for r in br))
        types = ["deep_pct", "pct_off", "sitewide", "clearance", "bogo", "free_gift",
                 "financing", "holiday_event", "sale_generic", "no_offer"]
        print(f"\n{b}:")
        print("  " + "type".ljust(15) + "".join(f"{y:>8}" for y in years))
        print("  " + "n".ljust(15) + "".join(
            f"{sum(1 for r in br if r['date'][:4]==y):>8}" for y in years))
        for t in types:
            cells = []
            for y in years:
                yr = [r for r in br if r["date"][:4] == y]
                cells.append(f"{100*sum(1 for r in yr if t in r['promo_type'])/len(yr):7.0f}%")
            print("  " + t.ljust(15) + "".join(cells))

    print("\n\n########## THE 'EVERYTHING' RATE — sitewide_pct by month ##########")
    print("  The discount attached to the word 'Everything' = depth x breadth in one number.")
    print("  This is where a genuine 'pivot to broader promotions' has to show up.")
    for b in banners:
        br = [r for r in rows if r["banner"] == b]
        d = defaultdict(list)
        for r in br:
            d[r["ym"]].append(r["sitewide_pct"])
        print(f"\n{b}:   (month: max 'Everything' rate seen / n obs / % of obs with any"
              f" sitewide language)")
        sw_any = defaultdict(list)
        for r in br:
            sw_any[r["ym"]].append(int(r["sitewide"]))
        for k in sorted(d):
            mx = max(d[k])
            print(f"   {k}  everything={int(mx) if mx else '-':>3}   n={len(d[k]):>2}   "
                  f"sitewide_lang={100*sum(sw_any[k])//len(sw_any[k]):>3}%")

    print("\n\n########## Y/Y 'EVERYTHING' RATE, HOLIDAY WINDOWS ##########")
    for b in banners:
        br = [r for r in rows if r["banner"] == b]
        print(f"\n{b}:")
        for months, lbl in [(["2024-11", "2024-12", "2025-01"], "Q4 FY25 (Nov24-Jan25)"),
                            (["2025-11", "2025-12", "2026-01"], "Q4 FY26 (Nov25-Jan26)"),
                            (["2025-05", "2025-06", "2025-07"], "Q2 FY26 (May-Jul25)"),
                            (["2026-05", "2026-06", "2026-07"], "Q2 FY27 (May-Jul26)"),
                            (["2025-07", "2025-08"], "Jul-Aug 2025"),
                            (["2026-07", "2026-08"], "Jul-Aug 2026")]:
            w = [r for r in br if r["ym"] in months]
            if not w:
                continue
            sw = [r["sitewide_pct"] for r in w]
            nz = [x for x in sw if x]
            print(f"   {lbl:24} n={len(w):>2}  max_everything={int(max(sw)) if max(sw) else '-':>3}"
                  f"  mean_when_present={round(st.mean(nz),1) if nz else '-':>5}"
                  f"  obs_with_everything={100*len(nz)//len(w):>3}%")

    print("\n\n########## REGION DIAGNOSTICS (parser transparency) ##########")
    print("  hero vs Featured-Deals contribution to promo_depth, by template era")
    for b in banners:
        br = [r for r in rows if r["banner"] == b]
        d = defaultdict(list)
        for r in br:
            d[r["era"]].append(r)
        print(f"\n{b}:")
        for k, v in sorted(d.items()):
            hero_hit = 100 * sum(1 for r in v if r["hero_max_pct_off"] > 0) / len(v)
            deal_hit = 100 * sum(1 for r in v if r["deals_max_pct_off"] > 0) / len(v)
            any_hit = 100 * sum(1 for r in v if r[M] > 0) / len(v)
            print(f"   {k:12} n={len(v):>3}  hero_has_pct={hero_hit:>3.0f}%  "
                  f"deals_has_pct={deal_hit:>3.0f}%  either={any_hit:>3.0f}%")


if __name__ == "__main__":
    main()
