"""A16 read-only reproduction (B08, B09, B10, B17 + the R04/C11 coherence checks).
Run from the repository root: python -B docs/pitch-forecasts/audits/A16-reproduce.py
Requires stdlib + pandas only (no numpy, no scipy). Writes nothing; uses no network.
The saved models use numpy; this script re-implements them with `random` and reproduces
their published figures to within Monte Carlo error (N = 200,000).
"""
from pathlib import Path
import html, json, math, random, re, statistics as st
import pandas as pd

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions"
B10 = Q / "bonus-interest-income-falls"
N = 200_000


def Phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def text(p):
    s = Path(p).read_text(encoding="utf-8", errors="replace")
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s)))


def dmargin(dR, dE, R, E):
    return 100 * (E + dE) / (R + dR) - 100 * E / R


FY26R, FY26E, FY27R, FY27E = 14268.0, 5098.0, 15829.0, 5483.0
print("=" * 78)
print("0. line-build annuals behind every section 9 table")
print("   FY26 rev %.0f ebitda %.0f margin %.3f%% | FY27 rev %.0f ebitda %.0f margin %.3f%%"
      % (FY26R, FY26E, 100 * FY26E / FY26R, FY27R, FY27E, 100 * FY27E / FY27R))

# ======================================================================= B08
print("=" * 78)
print("B08 / 1. claims 1 and 3 against the repo")
p = pd.read_csv(ROOT / "data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv")
h = p[p.quarter.isin(["1Q23", "2Q23", "3Q23", "4Q23", "1Q24", "2Q24", "3Q24", "4Q24",
                      "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"])]
print("   panel cor_cash 1Q25-2Q26:", [int(x) for x in h.cor_cash.tail(6)])
print("   FY25 %d ; 9M25 %d ; 4Q25 %d  (registry base 487)"
      % (h[h.quarter.str.endswith("25")].cor_cash.sum(),
         h[h.quarter.isin(["1Q25", "2Q25", "3Q25"])].cor_cash.sum(), 487))
ratio = list(h.cor_cash / h.gbv_busd / 10)
ryoy = [(ratio[i] / ratio[i - 4] - 1) * 100 for i in range(4, len(ratio))]
print("   CoR/GBV y/y (n=%d) mean %.2f sd %.2f   (log: -1.0 / 3.7)"
      % (len(ryoy), st.mean(ryoy), st.stdev(ryoy)))
print("   needed ratio change at GBV +12.7pct = %.2f ; observed >= that in %d of %d quarters"
      % ((1.18 / 1.127 - 1) * 100, sum(1 for x in ryoy if x >= 4.70), len(ryoy)))
lb = pd.read_csv(ROOT / "data/processed/margin_build/40_line_build/40_lines_quarterly.csv")
q4 = lb[lb.quarter == "4Q26"][["scenario", "cor_fees", "cor_chargebacks", "cor_hosting",
                               "cor_other", "cor_cash", "cor_cash_yoy_pct"]]
print("   40_lines_quarterly 4Q26 cost of revenue by scenario:")
print(q4.to_string(index=False))
print("   scenarios at or above the 575 threshold: %d of %d" % ((q4.cor_cash >= 575).sum(), len(q4)))

print("B08 / 2. leg-2 Monte Carlo (stdlib replay of b08_model.py)")


def leg2(mix=(0.45, 0.35, 0.20), gbv_sd=650.0, rate_sd=0.04, gbv_mu=22990.0,
         rate_mu=1.756, resid_sd=12.0, thr=575.0, seed=8):
    rng = random.Random(seed)
    cut1, cut2 = mix[0], mix[0] + mix[1]
    hits = 0
    vals = []
    for _ in range(N):
        fees = rng.gauss(gbv_mu, gbv_sd) * rng.gauss(rate_mu, rate_sd) / 100.0
        cb = rng.gauss(0.72 * 132.7 / 3.65, 4.0)
        other = rng.gauss(0.36 * 132.7, 3.0)
        u = rng.random()
        step = rng.gauss(15, 5) if u < cut1 else (rng.gauss(30, 8) if u < cut2 else rng.gauss(45, 10))
        cor = fees + cb + 56.0 + max(step, 0.0) + other + rng.gauss(0, resid_sd)
        vals.append(cor)
        hits += cor >= thr
    vals.sort()
    return hits / N, vals[N // 2]


for lbl, kw in (("published 0.45/0.35/0.20, gbv_sd 650", {}),
                ("audit 0.33/0.37/0.30, gbv_sd 800, rate_sd 0.05",
                 dict(mix=(0.33, 0.37, 0.30), gbv_sd=800.0, rate_sd=0.05))):
    p2, med = leg2(**kw)
    print("   %-46s p2 %.4f median %.0f | total at leg1|no 0.18 %.4f / 0.19 %.4f"
          % (lbl, p2, med, p2 + (1 - p2) * 0.18, p2 + (1 - p2) * 0.19))
print("   model values: p2 0.2598, median 559.2, total 0.3930; published headline 0.38")

print("B08 / 3. FY25 10-K purchase-obligation schedule (claim 6)")
t = text(ROOT / "data/raw/filings/abnb_10k_FY2025.htm")
i = t.find("Purchase obligations $")
print("   ", t[i - 150:i + 250].strip())

print("B08 / 4. section 9 arithmetic")
print("   FY26 +12 of cost, revenue unchanged -> %+.3fpp (log -0.1)" % dmargin(0, -12, FY26R, FY26E))
print("   FY27 +100 of cost -> %+.3fpp (log -0.6); on Street revenue 15819 -> %+.3fpp (log ~ -0.9)"
      % (dmargin(0, -100, FY27R, FY27E), -100.0 / 15819.0 * 100))
print("   EPS -100 x 0.0014 = %+.3f (log -0.14): one application, correct" % (-100 * 0.0014))
print("   level effect -100 x 16 / 573m = %+.2f ; / 620m as the log uses = %+.2f"
      % (-1600 / 573, -1600 / 620))

# ======================================================================= B09
print("=" * 78)
print("B09 / 1. SBC series: the releases against the repo CSVs")
for f, lbl in ((ROOT / "data/raw/letters/4Q25_d58192dex991.htm", "4Q25 letter"),
               (ROOT / "data/raw/letters/4Q24_d915198dex991.htm", "4Q24 letter")):
    s = text(f)
    j = s.find("Stock-based compensation expense $")
    print("   %s -> %s" % (lbl, s[j:j + 55].strip()))
s = text(ROOT / "data/raw/letters/2Q26_d70413dex991.htm")
j = s.find("Stock-based compensation expense 382")
print("   2Q26 letter nine-quarter row -> %s" % s[j:j + 60].strip())
dh = pd.read_csv(ROOT / "data/processed/abnb_driver_history_quarterly.csv")
for qq, printed in (("4Q23", 290), ("4Q24", 368), ("4Q25", 411)):
    print("   %s: driver_history %.0f | 02_panel sbc_total_is %.0f | printed release %d"
          % (qq, dh.loc[dh.quarter == qq, "stock_based_comp_total_musd"].iloc[0],
             p.loc[p.quarter == qq, "sbc_total_is"].iloc[0], printed))

print("B09 / 2. the guidance ledger's sbc_yoy_pct actuals are on the DRIVER-HISTORY basis")
g = pd.read_csv(ROOT / "data/processed/overnight/02_guidance_ledger.csv")
print(g[g.metric == "sbc_yoy_pct"][["print_quarter", "target_period", "value_mid", "actual",
                                    "outcome"]].to_string(index=False))
print("   printed basis: FY23 %.2f  FY24 %.2f  FY25 %.2f"
      % ((1120 / 930 - 1) * 100, (1407 / 1120 - 1) * 100, (1592 / 1407 - 1) * 100))
print("   driver basis : FY23 %.2f  FY24 %.2f  FY25 %.2f  <- the ledger's 18.28 / 30.82"
      % ((1100 / 930 - 1) * 100, (1439 / 1100 - 1) * 100, (1581 / 1439 - 1) * 100))
print("   so FY23 ~20pct was MET, FY24 ~20pct missed by 5.6 points not 10.8, 3Q24 ~25pct was MET")

print("B09 / 3. seasonal and y/y routes")
sbc = dict(zip(["1Q22", "2Q22", "3Q22", "4Q22", "1Q23", "2Q23", "3Q23", "4Q23", "1Q24", "2Q24",
                "3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"],
               [195, 247, 234, 254, 240, 304, 286, 290, 295, 382, 362, 368, 358, 424, 399, 411,
                410, 487]))
rat = [sbc["4Q%d" % y] / sbc["2Q%d" % y] for y in (22, 23, 24, 25)]
print("   Q4/Q2 %s | mean4 %.4f sd4 %.4f | mean 23-25 %.4f sd %.5f | needed %.4f"
      % ([round(x, 4) for x in rat], st.mean(rat), st.stdev(rat), st.mean(rat[1:]),
         st.stdev(rat[1:]), 500 / 487))
print("   needed y/y on the printed 4Q25 411 = %.2f pct (on the registry's 400 = 25.0)"
      % ((500 / 411 - 1) * 100))


def rA(mu, sd, seed=1):
    rng = random.Random(seed)
    return sum(1 for _ in range(N) if 487 * rng.gauss(mu, sd) + rng.gauss(0, 8) >= 500) / N


def rB(mu, sd, seed=2):
    rng = random.Random(seed)
    return sum(1 for _ in range(N) if 411 * (1 + rng.gauss(mu, sd) / 100) >= 500) / N


def rC(pmiss=0.20, mu=6.0, sd=3.0, seed=3, q3=399 * 1.132):
    rng = random.Random(seed)
    k = 0
    for _ in range(N):
        gg = rng.gauss(mu, sd) if rng.random() < pmiss else rng.gauss(-1.5, 2.5)
        k += (1592 * (1 + (13.1 + gg) / 100) - 897 - q3 + rng.gauss(0, 10)) >= 500
    return k / N


A = rA(st.mean(rat[1:]), 0.035)
Bm7 = rB(13.18, 6.0)
C = rC()
print("   A(.962,.035) %.4f | B(M7 13.2 +- 6) %.4f | C(miss .20 / +6) %.4f -> blend %.4f, +0.02 = %.4f"
      % (A, Bm7, C, 0.4 * A + 0.4 * Bm7 + 0.2 * C, 0.4 * A + 0.4 * Bm7 + 0.2 * C + 0.02))
print("   model blend 0.0904; published headline 0.10")
print("   section 7 replay: all-four %.3f (pub 0.13) | sd 0.02 %.3f (pub 0.05) | last-8 %.3f (pub 0.22)"
      " | 1H26 %.3f (pub 0.06)"
      % (0.4 * rA(st.mean(rat), st.stdev(rat)) + 0.4 * Bm7 + 0.2 * C + 0.02,
         0.4 * rA(st.mean(rat[1:]), 0.02) + 0.4 * Bm7 + 0.2 * C + 0.02,
         0.4 * A + 0.4 * rB(17.14, 6.86) + 0.2 * C + 0.02,
         0.4 * A + 0.4 * rB(14.7, 4.0) + 0.2 * C + 0.02))
Cc = rC(0.15, 4.0)
print("   corrected C (0.15 x N(+4,3)) %.4f -> blend .45/.45/.10 + 0.010 = %.4f  [audit number]"
      % (Cc, 0.45 * A + 0.45 * Bm7 + 0.10 * Cc + 0.010))
print("   section 9: +140 FY27 SBC x (1 - 0.175) / 573m = %+.3f EPS (log -0.20)" % (-140 * 0.825 / 573))

# ======================================================================= B10
print("=" * 78)
print("B10 / 1. interest-income series, threshold, rates")
s = text(ROOT / "data/raw/letters/2Q26_d70413dex991.htm")
j = s.find("Interest income (226)")
print("   2Q26 letter nine-quarter row -> %s" % s[j:j + 70].strip())
print("   threshold = 0.90 x 162 = %.1f" % (0.9 * 162))
d = pd.read_csv(B10 / "sources/fred_DTB3_20260917T082052Z.csv")
d.columns = ["date", "v"]
d["v"] = pd.to_numeric(d.v, errors="coerce")
d = d.dropna()
d["q"] = pd.to_datetime(d.date).dt.to_period("Q")
print("   DTB3 quarter means:", {str(k): round(v, 3) for k, v in d.groupby("q").v.mean().tail(4).items()})
f = pd.read_csv(B10 / "sources/fred_DFEDTARU_20260917T082052Z.csv")
print("   DFEDTARU last row %s = %s ; DTB3 last row %s = %.2f -> the 16 Sep hike is NOT in the snapshot"
      % (f.iloc[-1, 0], f.iloc[-1, 1], d.iloc[-1].date, d.iloc[-1].v))
kf = json.loads((B10 / "sources/kalshi_KXFED_open_20260917T082121Z.json").read_text(encoding="utf-8"))
kd = json.loads((B10 / "sources/kalshi_KXFEDDECISION_open_20260917T082121Z.json").read_text(encoding="utf-8"))
for m in kf["markets"]:
    if m["ticker"] in ("KXFED-26OCT-T3.75", "KXFED-26DEC-T4.00", "KXFED-26DEC-T4.25"):
        print("   %-18s bid %.2f ask %.2f vol %.0f oi %.0f vol24 %.0f updated %s"
              % (m["ticker"], float(m["yes_bid_dollars"]), float(m["yes_ask_dollars"]),
                 float(m["volume_fp"]), float(m["open_interest_fp"]),
                 float(m["volume_24h_fp"]), str(m["updated_time"])[:10]))
oct0 = [m for m in kd["markets"] if m["ticker"] == "KXFEDDECISION-26OCT-H0"][0]
print("   updated_time is 2026-04-09 on all %d KXFEDDECISION and all %d KXFED markets, newly listed"
      % (len(kd["markets"]), len(kf["markets"])))
print("   27JAN strikes included -> metadata, not a quote stamp; 26OCT-H0 volume_24h = %.0f, so live."
      % float(oct0["volume_24h_fp"]))

print("B10 / 2. the M7 rule replay and the buyback-draw ramp")


def b10(r_mu=4.10, r_sd=0.15, beta_mu=0.88, beta_sd=0.045, c3m=12100.0, c4m=12000.0,
        c_sd=500.0, fh=0.127, fh_sd=0.03, rnpl=0.10, resid=0.05, d3=0.0, d4=0.0, seed=10):
    rng = random.Random(seed)
    thr = 0.9 * 162
    k = k162 = 0
    tot = []
    for _ in range(N):
        r = rng.gauss(r_mu, r_sd)
        b = rng.gauss(beta_mu, beta_sd)
        gg = rng.gauss(fh, fh_sd)
        rn = rng.uniform(0, rnpl) if rnpl > 0 else 0.0
        base = ((rng.gauss(c3m, c_sd) - d3 + 7209 * (1 + gg) * (1 - rn))
                + (rng.gauss(c4m, c_sd) - d4 + 6959 * (1 + gg) * (1 - rn))) / 2
        ii = b * r / 100 * base / 4 * (1 + rng.gauss(0, resid))
        tot.append(ii)
        k += ii <= thr
        k162 += ii <= 162
    tot.sort()
    return k / N, k162 / N, tot[N // 2]


base, b162, med = b10()
print("   base regime P(<=145.8) %.4f | P(<=162, any decline) %.4f | median %.0f"
      % (base, b162, med))
print("   model values 0.01365 / -- / 176.7 ; the log's companion states P(<=162) about 0.13")
flat15 = b10(d3=1500, d4=1500)[0]
flat30 = b10(d3=3000, d4=3000)[0]
ramp15 = b10(d3=750, d4=1500)[0]
ramp30 = b10(d3=1500, d4=3000)[0]
cuts = b10(r_mu=3.25, r_sd=0.2)[0]
print("   upsize conditionals: flat 1.5bn %.4f / 3bn %.4f  vs ramped 1.5bn %.4f / 3bn %.4f"
      % (flat15, flat30, ramp15, ramp30))
print("   mixture .88/.07/.03/.02 published %.4f | ramped %.4f"
      % (.88 * base + .07 * flat15 + .03 * flat30 + .02 * cuts,
         .88 * base + .07 * ramp15 + .03 * ramp30 + .02 * cuts))
print("   section 9: -90 FY27 x (1 - 0.175) / 573m = %+.3f EPS (log -0.13)" % (-90 * 0.825 / 573))

# ======================================================================= B17
print("=" * 78)
print("B17 / 1. the 13-letter take-rate direction record (claim 1)")
tr = g[g.metric == "take_rate_yoy_pts"]
print("   ledger rows %d | 'lower' %d | flat/similar/in-line %d | higher/above %d"
      % (len(tr), sum(1 for x in tr.quote if "lower" in x),
         sum(1 for x in tr.quote if re.search(r"similar|flat|in-line", x)),
         sum(1 for x in tr.quote if re.search(r"higher|above", x))))
print("   realised y/y pts:", [None if pd.isna(x) else round(x, 2) for x in tr.actual])

print("B17 / 2. the Q3-call record, the gate route (b) must pass")
for qq in ("3Q21", "3Q22", "3Q23", "3Q24", "3Q25", "4Q25", "1Q26", "2Q26"):
    s = text(ROOT / ("data/raw/transcripts/web/%s.html" % qq))
    firms = len(set(re.findall(r"(Barclays|Goldman|Morgan Stanley|Bernstein|Jefferies|Truist|Citi|"
                               r"Deutsche|Wells Fargo|Piper|Evercore|Susquehanna|BTIG|Mizuho|Cowen|"
                               r"UBS|KeyBanc|Benchmark|Oppenheimer)", s)))
    print("   %s call chars %6d | Q&A firms %2d | 'take rate' %2d | 'moneti' %d | 'incentive' %d"
          % (qq, len(s), firms, len(re.findall(r"take rate", s, re.I)),
             len(re.findall(r"moneti", s, re.I)), len(re.findall(r"incentive", s, re.I))))
inc = {}
for f in sorted((ROOT / "data/raw/letters").glob("*.htm")):
    s = text(f)
    inc[f.name[:4]] = len(re.findall(r"incentive", s, re.I))
print("   letters from 1Q23 on that contain the word 'incentive': %s"
      % [k for k, v in sorted(inc.items()) if v > 0 and k[-2:] >= "23"])
print("   so route (b) has no letter door, and the Q3 call was silent in 2 of the last 3 years")

print("B17 / 3. the 2Q26 sentence (claim 2), verbatim")
s = text(ROOT / "data/raw/transcripts/web/2Q26.html")
j = s.find("For the full year, we expect our implied take rate")
print("   ", s[j:j + 390].strip())
print("   (CFO prepared-remarks outlook block, not Q&A)")

print("B17 / 4. route union replay")


def sim(pa=0.12, pt=0.80, pq=0.50, pc=0.06, rho=0.5, strict=None, seed=17):
    rng = random.Random(seed)
    k = 0
    r2 = math.sqrt(1 - rho ** 2)
    for _ in range(N):
        z0 = rng.gauss(0, 1)
        a = Phi(z0) < pa
        b = Phi(rho * z0 + r2 * rng.gauss(0, 1)) < pt and rng.random() < pq
        if b and strict:
            b = rng.random() < strict
        c = Phi(rho * z0 + r2 * rng.gauss(0, 1)) < pc
        k += a or b or c
    return k / N


print("   published (.12/.80/.50/.06, rho .5) %.4f (model 0.4812) | strict x0.55 %.4f (model 0.3344)"
      % (sim(), sim(strict=0.55)))
print("   audit     (.13/.65/.52/.06, rho .5) %.4f | strict %.4f"
      % (sim(0.13, 0.65, 0.52), sim(0.13, 0.65, 0.52, strict=0.55)))

print("B17 / 5. section 9 arithmetic, the R04 mirror, and the team's own FY26 take rate")
print("   FY26 -30 rev / -27 ebitda -> %+.3fpp (log -0.2) | FY27 -170 / -153 -> %+.3fpp (log -1.0)"
      % (dmargin(-30, -27, FY26R, FY26E), dmargin(-170, -153, FY27R, FY27E)))
r04 = json.loads((Q / "risk-single-fee-take-rate-accretion-stated/forecasts/2026-09-17-forecast.json")
                 .read_text(encoding="utf-8"))
c11 = json.loads((Q / "q3-take-rate-above-1810/forecasts/2026-09-17-forecast.json")
                 .read_text(encoding="utf-8"))
print("   R04 mirror +23 rev / +20.7 ebitda -> %+.3fpp ; R04 publishes %s (computed correctly there)"
      % (dmargin(23, 20.7, FY27R, FY27E), r04["impact"]["margin_fy27_pp"]))
print("   R04 revision %s p %.2f (B17 claim 7 quotes 0.58) | C11 revision %s p %.2f"
      % (r04["revision"], r04["final"]["p"], c11["revision"], c11["final"]["p"]))
g26 = float(p.loc[p.quarter == "1Q26", "gbv_busd"].iloc[0]) + float(p.loc[p.quarter == "2Q26", "gbv_busd"].iloc[0])
r26 = float(p.loc[p.quarter == "1Q26", "revenue"].iloc[0]) + float(p.loc[p.quarter == "2Q26", "revenue"].iloc[0])
lb26 = lb[(lb.scenario == "base") & (lb.quarter.isin(["3Q26", "4Q26"]))]
g25 = sum(float(p.loc[p.quarter == q_, "gbv_busd"].iloc[0]) for q_ in ("1Q25", "2Q25", "3Q25", "4Q25"))
r25 = sum(float(p.loc[p.quarter == q_, "revenue"].iloc[0]) for q_ in ("1Q25", "2Q25", "3Q25", "4Q25"))
tr26 = (r26 + lb26.revenue.sum()) / ((g26 + lb26.gbv_busd.sum()) * 1000) * 100
print("   team FY26 implied take rate %.3f%% vs FY25 %.3f%% = %+.1fbp -- management guides 'relatively flat'"
      % (tr26, r25 / (g25 * 1000) * 100, (tr26 - r25 / (g25 * 1000) * 100) * 100))
forms = (("repeat of the standing 2Q26 FY26 form", 0.60, -0.5),
         ("incentives named for a new period or mechanism", 0.15, -5.0),
         ("letter Q4 sentence reads lower y/y", 0.20, -5.0),
         ("explicit quantified FY27 lower", 0.05, -9.0))
e = sum(w * v for _, w, v in forms)
print("   R04-style split of the Yes mass -> E[stock|Yes] %.2f ; EV at p 0.38 = %.2f (log -6 and -2.5)"
      % (e, 0.38 * e))

# ================================================================== registers
print("=" * 78)
print("Batch register")
for slug in ("bonus-ai-hosting-cost-step", "bonus-sbc-step-up", "bonus-interest-income-falls",
             "bonus-take-rate-guided-down"):
    o = json.loads((Q / slug / "forecasts/2026-09-17-forecast.json").read_text(encoding="utf-8"))
    im = o["impact"]
    print("  %-4s rev %s p %.2f ci %s | anchor %.2f flag %s | stock %s EV %s material %s | EV check %.2f"
          % (o["question_id"], o["revision"], o["final"]["p"], o["final"]["ci"],
             o["estimates"]["anchor"], o["estimates"].get("not_independently_derived_flag"),
             im["stock_usd_per_share"], im["ev_stock_usd_per_share"], im["material"],
             o["final"]["p"] * im["stock_usd_per_share"]))
