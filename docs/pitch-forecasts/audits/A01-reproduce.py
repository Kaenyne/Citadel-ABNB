from pathlib import Path
from statistics import NormalDist
import json
import math
import pandas as pd

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions/q4-revenue-guide-vs-street"


def read(path):
    return pd.read_csv(ROOT / path, comment="#")


def true(series):
    return series.astype(str).str.lower().eq("true")


def rate(label, frame, col="gap"):
    s = frame[col].dropna()
    k, n = int((s < 0).sum()), len(s)
    print(label, dict(
        n=n, below=k, rate=k/n if n else None,
        laplace=(k+1)/(n+2), mean=s.mean(), sd=s.std()
    ))


def target(s):
    return "20" + s[2:] + "Q" + s[0]


ledger = read("data/processed/overnight/02_guidance_ledger.csv")
g = ledger[
    (ledger.metric == "revenue_usd_m") &
    (ledger.guide_type == "range")
].copy().sort_values("print_date")
g["period"] = g.target_period.map(target)
g["cushion_pct"] = 100 * (g.actual / g.value_mid - 1)
done = g.dropna(subset=["actual"])

print("Dollar ranges:", len(g), "realized:", len(done),
      "midpoint beats:", int((done.actual > done.value_mid).sum()),
      "top beats:", int((done.actual > done.value_high).sum()))
print("Trailing eight:",
      done.tail(8).cushion_pct.agg(["mean", "median", "std"]).to_dict())
print("All Q4:",
      done[done.period.str.endswith("Q4")].cushion_pct
      .agg(["count", "mean", "std"]).to_dict())
recent = done[done.period >= "2023Q1"].copy()
recent["season"] = recent.period.str[-2:]
print(recent.groupby("season").cushion_pct
      .agg(["count", "mean", "std"]).to_string())

# Cushion trend; numerical Student-t integration for a two-sided p-value.
y = done.cushion_pct.tolist()
n = len(y)
xm, ym = (n-1)/2, sum(y)/n
sxx = sum((x-xm)**2 for x in range(n))
slope = sum((x-xm)*(v-ym) for x, v in enumerate(y))/sxx
sse = sum((v-ym-slope*(x-xm))**2 for x, v in enumerate(y))
df = n-2
t = abs(slope / math.sqrt(sse/df/sxx))
h = t/10000


def tpdf(x):
    return (
        math.gamma((df+1)/2) /
        (math.sqrt(df*math.pi)*math.gamma(df/2)) *
        (1+x*x/df)**(-(df+1)/2)
    )


area = h/3 * (
    tpdf(0) + tpdf(t) +
    sum((4 if i % 2 else 2)*tpdf(i*h) for i in range(1, 10000))
)
print("Cushion trend:", slope, "pp/print; p =", 1-2*area)

# Match each print to the quarter being guided.
panel = read("data/processed/abnb_guidance_reaction_panel.csv")
panel["period"] = (
    pd.PeriodIndex(panel.print_quarter, freq="Q").shift(1).astype(str)
)
reg = read("data/processed/forecast_methods/L0/L0_vintage_register.csv")
pg = reg[(reg.role == "pre_guide") & (reg.metric == "revenue")]
p = panel.merge(pg, on="period", validate="one_to_one")
p["gap"] = 100*(p.nq_rev_guide_mid/p.value-1)
ok = p[true(p.pit_usable)].copy()

rate("Panel as used", panel, "guide_vs_street_pct")
rate("PIT-eligible all vendors", ok)
rate("PIT LSEG-era", ok[ok.print_date >= "2023-11-01"])
rate("PIT LSEG/Refinitiv only",
     ok[ok.vendor.isin(["LSEG", "Refinitiv"])])
rate("PIT November", ok[ok.print_date.str[5:7] == "11"])
rate("PIT nights lower",
     ok[(ok.nq_nights_dir == -1) | (ok.nq_nights_guide_pts < -1)])
rate("PIT nights higher",
     ok[(ok.nq_nights_dir == 1) | (ok.nq_nights_guide_pts > .5)])
rate("PIT last four", ok.sort_values("print_date").tail(4))
rate("PIT five-print run",
     ok[(ok.print_date >= "2024-05-01") &
        (ok.print_date <= "2025-08-01")])
for label, start in [("W1", "2023Q1"), ("W2", "2024Q1")]:
    rate(label, ok[(ok.period >= start) & (ok.period <= "2026Q2")])
print("Excluded:", p[~true(p.pit_usable)][
    ["register_id", "period", "value", "as_of_timestamp"]
].to_string(index=False))

# Select early/late observations independently from the source history.
d = read(
    "data/processed/github_altdata/samples/"
    "dolthub-post-no-preference-earnings-consensus-vintages/"
    "sales_estimate_ABNB_BKNG_EXPE.csv"
)
d = d[(d.act_symbol == "ABNB") & (d.period == "Next Quarter")].copy()
d["date"] = pd.to_datetime(d.date)
rows = []
for row in g.itertuples():
    dt = pd.Timestamp(row.print_date)
    end = pd.Period(row.period, freq="Q").end_time.strftime("%Y-%m-%d")
    v = d[d.period_end_date == end].sort_values("date")
    early = v[v.date <= dt-pd.Timedelta(days=50)]
    late = v[v.date < dt]
    if early.empty or late.empty:
        continue
    a, b = early.iloc[-1], late.iloc[-1]
    rows.append(dict(
        print_date=row.print_date,
        early_date=a.date.strftime("%Y-%m-%d"),
        late_date=b.date.strftime("%Y-%m-%d"),
        drift_pct=100*(b.consensus/a.consensus-1),
        late_age_days=(dt-b.date).days
    ))

drift = pd.DataFrame(rows)
for label, sub in [
    ("All", drift),
    ("2023+", drift[drift.print_date >= "2023-01-01"])
]:
    print("DoltHub", label,
          sub.drift_pct.agg(["count", "mean", "median", "std"]).to_dict())
print("November drift:",
      drift[drift.print_date.str[5:7] == "11"].to_string(index=False))
print("Stale endpoint:",
      drift[drift.print_date == "2024-08-06"].to_string(index=False))
saved = pd.read_csv(Q / "datasets/street_drift_dolthub.csv")
check = drift.merge(saved, on="print_date", suffixes=("_new", "_saved"))
assert len(check) == 20
assert (check.drift_pct_new-check.drift_pct_saved).abs().max() < 1e-10

# Published G4 comparison: recompute from individual forecast rows.
bt = read(
    "data/processed/forecast_methods/guidance_policy/"
    "07b_backtest_guide_mid_rows.csv"
)
bt = bt.merge(
    g[["period", "value_mid"]], left_on="quarter", right_on="period"
)
for w in ["W1", "W2"]:
    v = bt[(bt.prior_basis == "PIT") & (bt.window == w)]
    me = 100*(v.point/v.value_mid-1)
    se = 100*(v.base_street/v.value_mid-1)
    print("Published G4", w, "n", len(v),
          "wins", int((me.abs() < se.abs()).sum()),
          "MAE", me.abs().mean(), se.abs().mean(),
          "bias", me.mean(), se.mean())

k = read("data/processed/forecast_methods/kernel_lambda/01_lambda_table.csv")
k = k[(k.season == 4) & (k.q >= "2023Q1")]
lam = k.revenue_musd/(k.gbv_l1*2/3+k.gbv_l2/3)
print("Q4 lambdas %:", list(100*lam),
      "mean", 100*lam.mean(),
      "range pp", 100*(lam.max()-lam.min()))

# Parse actual API field names.
market = json.loads((
    Q / "sources/kalshi_markets_KXABNB_open_20260917T025304Z.json"
).read_text(encoding="utf-8"))
km = pd.DataFrame(market["markets"])
for c in [
    "floor_strike", "yes_bid_dollars", "yes_ask_dollars",
    "volume_fp", "volume_24h_fp"
]:
    km[c] = pd.to_numeric(km[c])
km = km.sort_values("floor_strike")
km["mid"] = (km.yes_bid_dollars+km.yes_ask_dollars)/2
print(km[[
    "floor_strike", "mid", "volume_fp", "volume_24h_fp", "updated_time"
]].to_string(index=False))
print("Volumes:", km.volume_fp.sum(), km.volume_24h_fp.sum())
prices = dict(zip(km.floor_strike/1e6, km.mid))
median = 148+2*(prices[148]-.5)/(prices[148]-prices[150])
print("Interpolated median nights:", median,
      "P(>147):", (prices[146]+prices[148])/2)

print("Stated mixture arithmetic:", .60*.800+.25*.683+.15*.722)
print("Saved mixture:", pd.read_csv(
    Q / "datasets/c01_final_mixture.csv", index_col=0
).value.to_dict())

# Auditor comparison: normal approximation, not fitted calibration.
inputs = read(
    "data/processed/forecast_methods/guidance_policy_v2/01_inputs.csv"
).set_index("input").value
snap = pd.read_csv(
    Q / "sources/yfinance_revenue_estimate_20260917T025239Z.csv"
).set_index("period")
street = float(snap.loc["+1q", "avg"])/1e6
gbv = 133.6*1.095*171.29*1.033
c = inputs["cushion_mean_pct"]/100
a = inputs["lambda_Q4_pct"]/100
fee = .005543
mu = a*(2*gbv/3+27200/3)*(1+fee)/(1+c)
sd = math.hypot(
    mu*inputs["sd_guide_mid_pp_CHOSEN"]/100,
    a*(2/3)*500*(1+fee)/(1+c)
)
dist = NormalDist(mu, sd)
p_yes = .99*NormalDist().cdf(
    (street-mu)/math.hypot(sd, .006*street)
)
print("Auditor GBV, guide mean, SD, P(Yes):", gbv, mu, sd, p_yes)
print("Percentiles:", {
    q: dist.inv_cdf(q/100) for q in [5, 10, 25, 50, 75, 90, 95]
})
print("Bounds mass:", dist.cdf(2900), 1-dist.cdf(3400))
p_surprise = .99*NormalDist().cdf(
    (street*(1-c)-mu)/math.hypot(sd, .006*street*(1-c))
)
print("Auditor cushion-subtracted comparison:", p_surprise)
