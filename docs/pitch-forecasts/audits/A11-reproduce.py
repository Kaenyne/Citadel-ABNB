"""A11 read-only reproduction (R06, R08, R09).
Run from the repository root: python -B docs/pitch-forecasts/audits/A11-reproduce.py
Requires stdlib + pandas only (no numpy/scipy). Writes nothing; no network.
"""
from pathlib import Path
import html
import json
import math
import random
import re
import pandas as pd

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions"
R06 = Q / "risk-buyback-upsize"
R08 = Q / "risk-new-2027-growth-lever"
R09 = Q / "risk-new-businesses-quantified-material"


def plain(path):
    s = path.read_text(encoding="utf-8", errors="replace")
    s = re.sub(r"<(script|style)\b.*?</\1>", " ", s, flags=re.I | re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s)))


# ---------------------------------------------------------------- R06 sources
print("=" * 72)
print("R06 / 1. letters vs the capital-return series")
letters = sorted((ROOT / "data/raw/letters").glob("*.htm"))
stated, remaining = {}, {}
for p in letters:
    t = plain(p)
    q = p.name.split("_")[0]
    m = re.search(r"During Q\d \d{4}, we repurchased \$([\d.]+) (billion|million)", t)
    if m:
        stated[q] = float(m.group(1)) * (1000 if m.group(2) == "billion" else 1)
    m = re.search(
        r"we had (?:the authorization to purchase up to )?\$([\d.]+) billion"
        r"(?: of our Class A common stock| remaining under)", t)
    if m:
        remaining[q] = float(m.group(1))
cap = pd.read_csv(ROOT / "data/processed/abnb_capital_return_quarterly.csv")
cash = dict(zip(cap.quarter, cap.buybacks_musd))
print("quarter | letter $M | XBRL cash $M | diff")
for q in sorted(stated, key=lambda x: (x[1:], x[0])):
    c = cash.get(q)
    if c is not None and c == c:
        print("  %-5s %9.0f %12.0f %7.0f" % (q, stated[q], c, c - stated[q]))
print("letter-stated remaining authorization (USD bn):",
      {k: remaining[k] for k in sorted(remaining, key=lambda x: (x[1:], x[0]))})
panel = pd.read_csv(R06 / "datasets/print_state_panel.csv")
panel["cash_bn"] = panel["print"].map(lambda q: cash.get(q, float("nan")) / 1000)
panel["letter_bn"] = panel["print"].map(lambda q: stated.get(q, float("nan")) / 1000)
print(panel[["print", "buyback_in_quarter_usd_bn", "cash_bn", "letter_bn",
             "remaining_after_quarter_usd_bn", "remaining_over_pace_q",
             "new_authorization_announced"]].to_string(index=False))
print("NOTE 3Q25: panel 0.86 = letter basis; log claim 5 quotes 877 = XBRL cash basis.")

print("capital-allocation boilerplate, every letter that carries it:")
for p in letters:
    t = plain(p)
    m = re.search(r"prioritizes investments in organic growth, (.{0,40}?), and return of capital", t)
    if m:
        print("   ", p.name.split("_")[0], "->", m.group(1))

# ------------------------------------------------------- R06 trigger base rate
print("=" * 72)
print("R06 / 2. trigger rule: author's logistic vs the MLE on the same panel")
rows = [(float(r.remaining_over_pace_q),
         int(str(r.new_authorization_announced).startswith("yes")))
        for r in panel.itertuples()
        if r.remaining_over_pace_q == r.remaining_over_pace_q]
print("panel (r, announced):", rows)
le16 = [y for r, y in rows if r <= 1.6]
mid = [y for r, y in rows if 1.6 < r < 2.7]
hi = [y for r, y in rows if r >= 2.7]
print("r<=1.6: %d/%d | 1.6<r<2.7: %d/%d (UNOBSERVED) | r>=2.7: %d/%d, Laplace %.4f"
      % (sum(le16), len(le16), sum(mid), len(mid), sum(hi), len(hi), 1 / (len(hi) + 2)))
third = [y for (r, y), q in zip(rows, panel["print"]) if q.startswith("3Q")]
print("third-quarter prints: %d/%d announcements" % (sum(third), len(third)))


def nll(a, b):
    s = 0.0
    for r, y in rows:
        z = a + b * r
        s -= y * z - (math.log1p(math.exp(z)) if z < 30 else z)
    return s


lo_a, hi_a, lo_b, hi_b = -5.0, 15.0, -15.0, 0.5
best = (0.0, 0.0, 1e18)
for _ in range(8):
    best = (0.0, 0.0, 1e18)
    ga = [lo_a + (hi_a - lo_a) * i / 200 for i in range(201)]
    gb = [lo_b + (hi_b - lo_b) * i / 200 for i in range(201)]
    for a in ga:
        for b in gb:
            v = nll(a, b)
            if v < best[2]:
                best = (a, b, v)
    a, b = best[0], best[1]
    da, db = (hi_a - lo_a) / 40, (hi_b - lo_b) / 40
    lo_a, hi_a, lo_b, hi_b = a - da, a + da, b - db, b + db
a, b, v = best
print("MLE logit = %.4f %+.4f*r -> k=%.3f, r50=%.3f, nll=%.5f" % (a, b, -b, a / -b, v))
print("author k=2.0, r50=1.45 -> nll=%.5f (NOT the MLE)" % nll(2.9, -2.0))
for x in (0.0, 1.0, 1.2, 1.6, 2.2, 2.35, 2.7):
    print("   r=%4.2f  MLE=%.4f  author=%.4f"
          % (x, 1 / (1 + math.exp(-(a + b * x))), 1 / (1 + math.exp(2.0 * (x - 1.45)))))
hist = pd.read_csv(R06 / "datasets/authorization_history.csv")
k5 = int((hist.program_usd_bn >= 5).sum())
print("program sizes (USD bn):", list(hist.program_usd_bn),
      "-> P(>=5bn) historical = %.2f | Laplace = %.3f | log uses 0.78"
      % (k5 / len(hist), (k5 + 1) / (len(hist) + 2)))

# ------------------------------------------------------------- R06 Monte Carlo
print("=" * 72)
print("R06 / 3. Monte Carlo replay (stdlib random; the saved model uses numpy)")


def r06(pace_mu=1.06, pace_sd=0.13, remaining=3.4, k=2.0, r50=1.45,
        p_size=0.78, legB_base=0.06, legB_auth=0.14, legB_thresh=1.5,
        p_nov_override=None, n=200000, seed=11):
    rng = random.Random(seed)
    nov = feb = yes = a_c = b_c = 0
    for _ in range(n):
        common = rng.gauss(pace_mu, pace_sd * 0.8)
        q3 = max(0.6, common + rng.gauss(0, pace_sd * 0.6))
        q4 = max(0.6, common + rng.gauss(0, pace_sd * 0.6))
        rs = max(0.0, remaining - q3)
        rd = max(0.0, rs - q4)
        pace = (q3 + q4) / 2
        pn = 1 / (1 + math.exp(k * (rs / pace - r50))) if p_nov_override is None else p_nov_override
        an = rng.random() < pn
        af = (not an) and (rng.random() < 1 / (1 + math.exp(k * (rd / pace - r50))))
        ann = an or af
        legA = ann and (rng.random() < p_size)
        legB = (rng.random() < (legB_auth if an else legB_base)) or (q4 >= legB_thresh)
        nov += an
        feb += ann
        a_c += legA
        b_c += legB
        yes += (legA or legB)
    return {"nov": nov / n, "by_feb": feb / n, "legA": a_c / n,
            "legB": b_c / n, "yes": yes / n}


def show(label, d):
    print("  %-40s %s" % (label, {k_: round(v_, 4) for k_, v_ in d.items()}))


saved = pd.read_csv(R06 / "datasets/r06_summary.csv").set_index("metric").value
print("saved r06_summary.csv:", saved.to_dict())
show("author parameters", r06())
show("MLE trigger", r06(k=-b, r50=a / -b))
show("MLE trigger + size 0.50 (historical)", r06(k=-b, r50=a / -b, p_size=0.50))
show("auditor: Nov 0.08, MLE Feb, size 0.78", r06(k=-b, r50=a / -b, p_nov_override=0.08))
show("leg B threshold 1.45 (letters round)", r06(legB_thresh=1.45))
print("R06 impact arithmetic:")
print("   0.45bn/165 = %.3fm shares; /586 = %.5f; x FY27 EPS 5.73 = %.4f"
      % (0.45e3 / 165, 0.45e3 / 165 / 586, 5.73 * (0.45e3 / 165 / 586)))
print("   P(legB|yes) = %.4f -> weighted stock = %.3f (log says 1.3); EV 0.55x1.3 = %.3f"
      % (float(saved["p_legB"]) / float(saved["p_yes"]),
         0.859 * 1.0 + 0.141 * 2.5, 0.55 * 1.3))

# ------------------------------------------------------------------------ R08
print("=" * 72)
print("R08 / tree replay and impact arithmetic")


def r08(p_named=0.92, p_nov=0.05, p_feb=0.12, p_loose=0.25, p_oom=0.45, strict=True):
    p = p_named * (1 - (1 - p_nov) * (1 - p_feb))
    return p + (1 - p) * (0.0 if strict else p_named * p_oom * p_loose)


print("saved:", pd.read_csv(R08 / "datasets/r08_summary.csv").to_dict("records"))
print("replay base = %.4f | lenient = %.4f" % (r08(), r08(strict=False)))
print("base rate 0/23 prints, Laplace 1/25 = %.4f -> two prints %.4f"
      % (1 / 25, 1 - (1 - 1 / 25) ** 2))
h8 = pd.read_csv(R08 / "datasets/forward_product_quantification_history.csv")
print("forward-statement rows:", len(h8), "| counting under the R08 convention:",
      int(h8.counts_under_R08_convention.str.startswith("yes").sum()))
print("auditor tree: Nov 0.03, Feb 0.10 -> %.4f" % (1 - 0.97 * 0.90))
FY26_REV, FY27_REV, FY27_EBITDA = 14268.0, 15829.0, 5483.0
up = 0.42 * 158
base_m = 100 * FY27_EBITDA / FY27_REV
print("   FY27 base margin %.3f%%" % base_m)
for cost in (0, 60, 100, 112, 125):
    m = 100 * (FY27_EBITDA + up - cost) / (FY27_REV + 158)
    print("   launch opex $%3dM -> margin %.3f%% (delta %+.3fpp), EPS delta %+.3f"
          % (cost, m, m - base_m, (up - cost) * 0.0014))
print("   log states -0.3pp and EPS 0.00; its own stated cost"
      " (half of $200-250M) gives -0.63pp and -$0.06")
print("   1pt of FY27 growth on the FY26 base = %.1fM"
      " (the brief's $158M is 1%% of FY27 revenue)" % (0.01 * FY26_REV))
print("   EV = 0.15 x 4.90 = %.3f" % (0.15 * 4.9))

# ------------------------------------------------------------------------ R09
print("=" * 72)
print("R09 / route replay, descriptor base rate, disclosure-initiation cross-check")


def r09(p_nov=0.12, p_feb=0.18, p_true=0.65, p_seats=0.02, p_gbv=0.02,
        p_rev=0.03, p_comb=0.03, p_agg=0.0):
    disc = 1 - (1 - p_nov) * (1 - p_feb)
    hotel = disc * p_true
    other = 1 - (1 - p_seats) * (1 - p_gbv) * (1 - p_rev) * (1 - p_comb) * (1 - p_agg)
    return round(1 - (1 - hotel) * (1 - other), 4), round(disc, 4), round(hotel, 4), round(other, 4)


print("saved:", pd.read_csv(R09 / "datasets/r09_summary.csv").to_dict("records"))
print("replay base (p_yes, disc, hotelYes, other) =", r09())
print("auditor (Nov 0.10, true 0.55, aggregation 0.025) =",
      r09(p_nov=0.10, p_feb=0.18, p_true=0.55, p_agg=0.025))
h9 = pd.read_csv(R09 / "datasets/new_business_disclosure_history.csv")
print("disclosure-history rows:", len(h9), "| conference or 10-K rows:",
      int(h9.event.str.contains("Communacopia|10-K").sum()))
print("independent upgrade opportunities: seats descriptor set 2Q25 -> 4 later"
      " prints; hotels descriptor set 1Q26 -> 1 later print = 5, not 8")
for n_ in (5, 8):
    lap = 1 / (n_ + 2)
    two = 1 - (1 - lap) ** 2
    print("   n=%d: Laplace/print %.4f, two prints %.4f, x0.65 = %.4f"
          % (n_, lap, two, two * 0.65))

matrix = pd.read_csv(
    Q / "bundle-attribution-quantified/datasets/metric_persistence_matrix_v2_4Q20-2Q26.csv"
).set_index("metric")
d = matrix.ne("--")
cols = list(d.columns)
firsts = [cols[list(d.loc[i]).index(True)] for i in d.index if d.loc[i].any()]
seed = sorted(set(firsts))[0]
after = [q for q in firsts if q != seed and q != cols[0]]
n_after = len([c for c in cols if c > seed])
print("C05 rev-2 matrix:", matrix.shape, "| seed cohort quarter:", seed,
      "(%d metrics)" % firsts.count(seed),
      "| new quantified metrics initiated later: %d over %d prints -> %.4f per print"
      % (len(after), n_after, len(after) / n_after))
print(pd.read_csv(Q / "bundle-attribution-quantified/datasets/persistence_rates_v2.csv")
      .to_string(index=False))

sub = json.loads((R06 / "sources/edgar_submissions_CIK0001559720_20260917T034243Z.json")
                 .read_text(encoding="utf-8"))["filings"]["recent"]
tenk = [dt for f, dt in zip(sub["form"], sub["filingDate"]) if f == "10-K"]
feb_prints = [dt for f, dt, it in zip(sub["form"], sub["filingDate"], sub["items"])
              if f == "8-K" and "2.02" in it and dt[5:7] == "02"]
print("10-K filing dates:", tenk, "| February 2.02 8-K dates:", feb_prints)
print("=> FY2024 and FY2025 10-Ks filed the SAME DAY as the print; R09 claim 4"
      " dates the FY2025 10-K 2026-02-13 and the log discards the 10-K route"
      " as 'typically files after the print'")

for slug in ("risk-buyback-upsize", "risk-new-2027-growth-lever",
             "risk-new-businesses-quantified-material"):
    obj = json.loads((Q / slug / "forecasts/2026-09-17-forecast.json").read_text(encoding="utf-8"))
    imp = obj["impact"]
    print(obj["question_id"], "p =", obj["final"]["p"], "ci", obj["final"]["ci"],
          "| stock", imp["stock_usd_per_share"], "EV", imp["ev_stock_usd_per_share"],
          "| EV check", round(obj["final"]["p"] * imp["stock_usd_per_share"], 3),
          "| material", imp["material"])
c05 = json.loads((Q / "bundle-attribution-quantified/forecasts/2026-09-17-forecast.json")
                 .read_text(encoding="utf-8"))
print("C05 revision", c05["revision"], "p_any_quantification =",
      c05["p_any_quantification"], "-> R08 and R09 both anchor on the stale 0.27")
