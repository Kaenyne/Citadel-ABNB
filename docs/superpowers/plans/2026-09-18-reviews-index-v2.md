# Reviews Index v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build, freeze, run and plot the four-stage reviews-index v2 (measurement panel, walk-forward calibration, post-RNPL gap, DiD power) exactly as pre-registered in the spec.

**Architecture:** One flat package of small modules (config / data / index / kernel / scoring / panel / gap / did_power / figures / run) run as scripts from the package directory, the way `lane4_review_v2` does. Every stage reads only committed inputs, writes only into the lane's output folder, and records pass/fail against `prereg.json`. Tests are pytest files under `tests/` with a `conftest.py` that puts the package on `sys.path`.

**Tech Stack:** Python 3.13, pandas 3, numpy, scipy 1.17, matplotlib; pytest 9.

**Spec:** `docs/revenue-forecast-strategy/05_backtests/REVIEWS_INDEX_v2.md`

## Global Constraints

- Lane: code `analysis/src/forecast_methods/reviews_index_v2/`, outputs `data/processed/forecast_methods/reviews_index_v2/`, note `docs/revenue-forecast-strategy/05_backtests/REVIEWS_INDEX_v2.md`. Copy-never-overwrite: never write under `q3nowcast/`, `q3nowcast_v2/`, or any other lane.
- Pass lines come from `config.PREREG` and are frozen (sha256 in the note §2) before Stage A runs. No pass line is edited after the freeze.
- Windows: W1 window 2022Q1+ scored from 1Q23; W2 window 2023Q1+ scored from 1Q24; naive = y[t−1]; pass ≤ 0.75 on both (Stage B1).
- Primary construction `yoy_vmatch`; `yoy_all` sensitivity; posting-lag trim = 2 months before each dump.
- Stage C mapping frozen with data through 2Q25 (qi 8101); post quarters 3Q25, 4Q25, 1Q26, 2Q26.
- The scorer must reproduce E5's 0.683209 for `GLOBAL|yoy_all|w_reviews` on W2 before any v2 number is written.
- Code blocks tagged `file=` are the implementation; `python3 tools_extract.py` (Task 0) materialises them.

---

### Task 0: Package skeleton, config, prereg freeze

**Files:**
- Create: `analysis/src/forecast_methods/reviews_index_v2/config.py`
- Create: `analysis/src/forecast_methods/reviews_index_v2/tests/conftest.py`
- Create: `analysis/src/forecast_methods/reviews_index_v2/tests/test_config.py`

**Interfaces:**
- Produces: `config.ROOT, E, E23, OUT, FIG, NOTE, KPI, EUROSTAT, K2, E6_NOWCAST` (Paths); `REGION_OF_COUNTRY`, `FY25_NIGHTS_SHARE`, `EU_CODE` (dicts); `LAG_TRIM_MONTHS=2`; `VMATCH_DAYS=(300,430)`; `FREEZE_QI`, `POST_QIS`, `WINDOWS`, `PREREG` (dict); `qi(year,q)->int`.

- [ ] **Step 1: Write the failing test**

```python file=analysis/src/forecast_methods/reviews_index_v2/tests/test_config.py
def test_prereg_lines_are_the_specs():
    import config as C
    assert C.PREREG["B1_ratio_max"] == 0.75 and C.PREREG["A5_median_ratio_max"] == 0.75
    assert C.PREREG["C1_mean_gap_min_bands"] == 1.0 and C.PREREG["C1_quarters_min"] == 3
    assert C.FREEZE_QI == 2025 * 4 + 1 and C.POST_QIS == [8102, 8103, 8104, 8105]
    assert C.WINDOWS == {"W1": (2022 * 4, 2023 * 4), "W2": (2023 * 4, 2024 * 4)}
    assert abs(sum(C.FY25_NIGHTS_SHARE.values()) - 100.1) < 0.2
```

```python file=analysis/src/forecast_methods/reviews_index_v2/tests/conftest.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
```

- [ ] **Step 2: Run test to verify it fails** — `cd analysis/src/forecast_methods/reviews_index_v2 && python3 -m pytest tests/test_config.py -q` → FAIL, no module `config`.

- [ ] **Step 3: Write config**

```python file=analysis/src/forecast_methods/reviews_index_v2/config.py
"""reviews_index_v2 — paths, constants and the frozen pass lines. Nothing in this file is fitted.
Spec and pre-registration: docs/revenue-forecast-strategy/05_backtests/REVIEWS_INDEX_v2.md"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
E = ROOT / "data/processed/q3nowcast/E"
E23 = ROOT / "data/processed/q3nowcast_v2/E"
OUT = ROOT / "data/processed/forecast_methods/reviews_index_v2"
FIG = OUT / "figures"
NOTE = ROOT / "docs/revenue-forecast-strategy/05_backtests/REVIEWS_INDEX_v2.md"
KPI = ROOT / "data/processed/abnb_driver_history_quarterly.csv"
EUROSTAT = ROOT / "data/processed/eurostat_platform_nights_monthly.csv"
K2 = ROOT / "data/processed/forecast_methods/kernel_leadtime_v2/K2_M_matrix.csv"
E6_NOWCAST = E / "q3_2026_nowcast.csv"

# region map and weights exactly as analysis/src/q3nowcast/E4_build_index.py
REGION_OF_COUNTRY = {
    "united-states": "NAM", "canada": "NAM",
    "argentina": "LatAm", "belize": "LatAm", "brazil": "LatAm", "chile": "LatAm",
    "colombia": "LatAm", "mexico": "LatAm",
    "australia": "APAC", "china": "APAC", "japan": "APAC", "new-zealand": "APAC",
    "singapore": "APAC", "taiwan": "APAC", "thailand": "APAC",
}
FY25_NIGHTS_SHARE = {"NAM": 28.3, "EMEA": 41.6, "LatAm": 17.9, "APAC": 12.3}
# Eurostat codes exactly as analysis/src/q3nowcast/E5_backtest.py
EU_CODE = {"austria": "AT", "belgium": "BE", "czech-republic": "CZ", "denmark": "DK", "france": "FR",
           "germany": "DE", "greece": "EL", "hungary": "HU", "ireland": "IE", "italy": "IT",
           "latvia": "LV", "malta": "MT", "portugal": "PT", "spain": "ES", "sweden": "SE",
           "the-netherlands": "NL", "switzerland": "CH", "norway": "NO"}

LAG_TRIM_MONTHS = 2            # months up to and including the dump month dropped for posting lag
VMATCH_DAYS = (300, 430)       # prior vintage must be this many days older than the latest (E4 rule)


def qi(year, q):
    return int(year) * 4 + int(q) - 1


def ymi(year, month):
    return int(year) * 12 + int(month) - 1


FREEZE_QI = qi(2025, 2)                                      # Stage C calibration ends here
POST_QIS = [qi(2025, 3), qi(2025, 4), qi(2026, 1), qi(2026, 2)]
WINDOWS = {"W1": (qi(2022, 1), qi(2023, 1)), "W2": (qi(2023, 1), qi(2024, 1))}   # (window start, first scored)
PANEL_START, PANEL_END, PANEL_SCORE_START = ymi(2023, 1), ymi(2026, 3), ymi(2024, 1)
RNPL_US_LAUNCH_YMI = ymi(2025, 8)
NEVER_TREATED = set(c for c in EU_CODE) | {"turkey", "south-africa", "kenya", "brazil"}

PREREG = {
    "A1_beta_p_max": 0.01,
    "A2_diff_p_max": 0.05,
    "A5_median_ratio_max": 0.75,
    "B1_ratio_max": 0.75,
    "C1_mean_gap_min_bands": 1.0,
    "C1_quarters_min": 3,
    "C1_quarter_min_bands": 0.5,
    "beta_B_bundle_pts": [2.0, 3.0],
    "windows": {k: list(v) for k, v in WINDOWS.items()},
    "post_quarters": POST_QIS,
    "freeze_qi": FREEZE_QI,
    "primary_measure": "yoy_vmatch",
    "lag_trim_months": LAG_TRIM_MONTHS,
    "panel_window_ymi": [PANEL_START, PANEL_END, PANEL_SCORE_START],
}
```

- [ ] **Step 4: Run test** → PASS.
- [ ] **Step 5: Extractor and freeze are Task 9; no commit yet (user decides commits).**

---

### Task 1: Scorer that reproduces E5

**Files:**
- Create: `analysis/src/forecast_methods/reviews_index_v2/scoring.py`
- Test: `analysis/src/forecast_methods/reviews_index_v2/tests/test_scoring.py`

**Interfaces:**
- Produces: `ols(x,y)->(b,a)`; `walkforward(x,y,start,season_lag)->dict|None` (E5 semantics, keys `wf_n, wf_rmse, wf_rmse_naive, wf_rmse_prior, wf_rmse_ar1, wf_ratio_vs_naive, wf_ratio_vs_prior, wf_ratio_vs_ar1, sign_acc, mean_err, _path`); `score_window(x: Series[qi], y: Series[qi], window_start, score_start, season_lag=4, score_end=None)->dict` with `path` DataFrame(qi, pred, actual, err_feature, err_naive); `ratio_interval(ef,en)->(lo,hi)`; `dm_test(ef,en)->(stat,p)`.

- [ ] **Step 1: Failing test — must reproduce 0.683209**

```python file=analysis/src/forecast_methods/reviews_index_v2/tests/test_scoring.py
import numpy as np, pandas as pd


def test_reproduces_e5_v1_cell_on_w2():
    import config as C, scoring as S
    qq = pd.read_csv(C.E / "index_quarterly.csv"); qq["qi"] = qq.year * 4 + qq.q - 1
    x = qq[(qq.region == "GLOBAL") & (qq.measure == "yoy_all")].set_index("qi").w_reviews * 100
    k = pd.read_csv(C.KPI); k["qi"] = k.year * 4 + k.q - 1; y = k.set_index("qi").nights_m_yoy_pct
    r2 = S.score_window(x, y, *C.WINDOWS["W2"])
    r1 = S.score_window(x, y, *C.WINDOWS["W1"])
    assert abs(r2["wf_ratio_vs_naive"] - 0.683209) < 1e-4 and r2["wf_n"] == 10
    assert abs(r1["wf_ratio_vs_naive"] - 0.837125) < 1e-4 and r1["wf_n"] == 14
    assert abs(r2["mean_err"] - 0.518452) < 1e-4


def test_dm_and_interval_behave():
    import scoring as S
    rng = np.random.default_rng(0); en = rng.normal(0, 2, 40); ef = en * 0.5
    stat, p = S.dm_test(ef, en); assert stat < 0 and p < 0.01
    lo, hi = S.ratio_interval(ef, en); assert lo <= 0.5 <= hi
```

- [ ] **Step 2: Run** → FAIL (no scoring module).

- [ ] **Step 3: Implement**

```python file=analysis/src/forecast_methods/reviews_index_v2/scoring.py
"""Walk-forward scorer. ols() and walkforward() are E5_backtest.py's functions, unchanged, so that v2 is scored on
exactly the record's yardstick (test_scoring.py reproduces E5's 0.683209). Added: score_window(), a moving-block
bootstrap interval for the RMSE ratio, and a Diebold-Mariano test with the Harvey-Leybourne-Newbold correction."""
import numpy as np, pandas as pd
from scipy import stats


def ols(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if len(x) < 3 or np.std(x) == 0:
        return np.nan, np.nanmean(y)
    b = np.cov(x, y, ddof=1)[0, 1] / np.var(x, ddof=1)
    return b, y.mean() - b * x.mean()


def walkforward(x, y, start, season_lag):
    """x, y aligned arrays indexed 0..n-1 in time order. start = first index scored. (E5, verbatim, plus preds.)"""
    e_f, e_n, e_p, e_a, sg, ts, pr = [], [], [], [], [], [], []
    for t in range(start, len(y)):
        xs, ys = x[:t], y[:t]
        ok = np.isfinite(xs) & np.isfinite(ys)
        if ok.sum() < 4 or not np.isfinite(x[t]) or not np.isfinite(y[t]):
            continue
        b, a = ols(xs[ok], ys[ok])
        pred = a + b * x[t]
        if not np.isfinite(pred) or not np.isfinite(y[t - 1]):
            continue
        e_f.append(pred - y[t]); e_n.append(y[t - 1] - y[t]); pr.append(pred)
        e_p.append((y[t - season_lag] - y[t]) if t >= season_lag and np.isfinite(y[t - season_lag]) else np.nan)
        yl, yy = ys[:-1], ys[1:]
        m = np.isfinite(yl) & np.isfinite(yy)
        if m.sum() >= 4:
            b2, a2 = ols(yl[m], yy[m]); e_a.append(a2 + b2 * y[t - 1] - y[t])
        else:
            e_a.append(np.nan)
        sg.append(np.sign(pred - y[t - 1]) == np.sign(y[t] - y[t - 1]))
        ts.append(t)
    if len(e_f) < 4:
        return None
    r = lambda e: float(np.sqrt(np.nanmean(np.asarray(e, float) ** 2))) if np.isfinite(np.asarray(e, float)).sum() else np.nan
    return dict(wf_n=len(e_f), wf_rmse=r(e_f), wf_rmse_naive=r(e_n), wf_rmse_prior=r(e_p), wf_rmse_ar1=r(e_a),
                wf_ratio_vs_naive=r(e_f) / r(e_n) if r(e_n) else np.nan,
                wf_ratio_vs_prior=r(e_f) / r(e_p) if r(e_p) else np.nan,
                wf_ratio_vs_ar1=r(e_f) / r(e_a) if r(e_a) else np.nan,
                sign_acc=float(np.mean(sg)), mean_err=float(np.mean(e_f)), _path=(ts, e_f, e_n, pr))


def score_window(x, y, window_start, score_start, season_lag=4, score_end=None):
    """x, y: Series indexed by the same integer period key (qi or ymi). Contiguous index is rebuilt so lag
    baselines are honest (E5 convention). score_end (inclusive) truncates the series before scoring."""
    df = pd.DataFrame({"x": x, "y": y}).dropna()
    df = df[(df.index >= window_start) & ((df.index <= score_end) if score_end is not None else True)].sort_index()
    if len(df) < 7:
        return None
    full = pd.DataFrame(index=range(int(df.index.min()), int(df.index.max()) + 1)).join(df)
    xa, ya = full.x.to_numpy(float), full.y.to_numpy(float)
    start = max(4, int(np.searchsorted(full.index.to_numpy(), score_start)))
    res = walkforward(xa, ya, start, season_lag)
    if res is None:
        return None
    ts, ef, en, pr = res.pop("_path")
    res["path"] = pd.DataFrame({"t": [int(full.index[t]) for t in ts], "pred": pr,
                                "actual": [ya[t] for t in ts], "err_feature": ef, "err_naive": en})
    return res


def ratio_interval(ef, en, B=2000, block=2, seed=20260918, q=(0.05, 0.95)):
    """Moving-block bootstrap (block = 2 periods) of the RMSE ratio over the scored periods."""
    rng = np.random.default_rng(seed); ef = np.asarray(ef, float); en = np.asarray(en, float); n = len(ef)
    out = []
    for _ in range(B):
        starts = rng.integers(0, n - block + 1, size=int(np.ceil(n / block)))
        idx = np.concatenate([np.arange(s, s + block) for s in starts])[:n]
        out.append(np.sqrt(np.mean(ef[idx] ** 2)) / np.sqrt(np.mean(en[idx] ** 2)))
    return float(np.quantile(out, q[0])), float(np.quantile(out, q[1]))


def dm_test(ef, en):
    """Diebold-Mariano on squared loss, h = 1, HLN small-sample factor sqrt((n-1)/n), two-sided p on t(n-1).
    Negative statistic = feature loss below naive loss."""
    d = np.asarray(ef, float) ** 2 - np.asarray(en, float) ** 2
    n = len(d); v = d.var(ddof=1) / n
    if n < 3 or v == 0:
        return np.nan, np.nan
    dm = d.mean() / np.sqrt(v) * np.sqrt((n - 1) / n)
    return float(dm), float(2 * (1 - stats.t.cdf(abs(dm), df=n - 1)))
```

- [ ] **Step 4: Run** → both PASS (if the 0.683209 check fails, the scorer is wrong — do not proceed).

---

### Task 2: Data loaders and the index constructions

**Files:**
- Create: `data.py`, `index.py`; Test: `tests/test_index.py`

**Interfaces:**
- `data.load_counted(path=None)->DataFrame[market_key, dump_date, dump_ymi, ymi, n_reviews, n_reviews_mature12, n_listings, country, region]`
- `data.select_vintages(mv)->(latest, prior)` both trimmed by `LAG_TRIM_MONTHS`
- `data.load_kpi()->DataFrame[year,q,qi,nights_m,nights_m_yoy_pct]`; `data.load_eurostat_yoy()->DataFrame[code, ymi, nights, y_yoy]` (log y/y); `data.load_kernel()->dict{q:int -> ndarray[4]}`
- `index.market_monthly(latest, prior)->DataFrame[market_key, ymi, country, region, n_reviews, n_lag12, n_reviews_mature12, n_mature12_lag12, n_vm_cur, n_vm_prior]`
- `index.MEASURES`; `index.ratio_of_sums(df, by, measure)->(Series, sums)`; `index.country_monthly(my, measure)->DataFrame[country, ymi, <measure>]`; `index.global_quarterly(my, measure)->(Series[qi], regional DataFrame)`

- [ ] **Step 1: Failing tests**

```python file=analysis/src/forecast_methods/reviews_index_v2/tests/test_index.py
import numpy as np, pandas as pd


def _toy():
    # two markets, one region each, 30 months, latest dump 2026-08, prior dump 2025-08
    rows = []
    for mkt, reg_c in [("united-states_x_a", "united-states"), ("france_x_b", "france")]:
        for dump, base in [("2026-08-15", 100), ("2025-08-15", 90)]:
            for i in range(2024 * 12, 2026 * 12 + 8):
                rows.append(dict(market_key=mkt, dump_date=dump, ymi=i, n_reviews=base + (i % 12),
                                 n_reviews_mature12=base // 2, n_listings=10))
    return pd.DataFrame(rows)


def test_vintage_selection_and_trim(monkeypatch):
    import data as D, config as C
    mv = D.load_counted.__wrapped__(_toy()) if hasattr(D.load_counted, "__wrapped__") else D.tag(_toy())
    latest, prior = D.select_vintages(mv)
    assert latest.dump_date.unique().tolist() == ["2026-08-15"] and prior.dump_date.unique().tolist() == ["2025-08-15"]
    assert latest.ymi.max() == C.ymi(2026, 6) and prior.ymi.max() == C.ymi(2025, 6)   # two months trimmed


def test_vmatch_arithmetic():
    import data as D, index as I
    latest, prior = D.select_vintages(D.tag(_toy()))
    my = I.market_monthly(latest, prior)
    r = my[(my.market_key == "france_x_b") & (my.ymi == 2026 * 12 + 3)].iloc[0]     # Apr 2026
    assert r.n_vm_cur == 100 + 3 and r.n_vm_prior == 90 + 3                         # prior dump, Apr 2025
    assert r.n_lag12 == 100 + 3                                                       # same dump, Apr 2025
    s, _ = I.ratio_of_sums(my[my.ymi == 2026 * 12 + 3], ["ymi"], "yoy_vmatch")
    assert abs(s.iloc[0] - (206 / 186 - 1)) < 1e-12


def test_global_quarterly_uses_fy25_weights():
    import data as D, index as I, config as C
    latest, prior = D.select_vintages(D.tag(_toy()))
    my = I.market_monthly(latest, prior)
    g, reg = I.global_quarterly(my, "yoy_vmatch")
    q = C.qi(2026, 1)
    w = C.FY25_NIGHTS_SHARE
    expect = (reg.loc[q, "NAM"] * w["NAM"] + reg.loc[q, "EMEA"] * w["EMEA"]) / (w["NAM"] + w["EMEA"])
    assert abs(g.loc[q] - expect) < 1e-12
```

- [ ] **Step 2: Run** → FAIL.

- [ ] **Step 3: Implement**

```python file=analysis/src/forecast_methods/reviews_index_v2/data.py
"""Loaders. Reads only committed inputs (q3nowcast/E counted layer, KPI history, Eurostat, K2 kernel)."""
import numpy as np, pandas as pd
import config as C


def tag(mv):
    mv = mv.copy()
    mv["country"] = mv.market_key.str.split("_").str[0]
    mv["region"] = mv.country.map(C.REGION_OF_COUNTRY).fillna("EMEA")
    d = pd.to_datetime(mv.dump_date)
    mv["dump_ymi"] = d.dt.year * 12 + d.dt.month - 1
    return mv


def load_counted(path=None):
    return tag(pd.read_csv(path or C.E / "market_vintage_monthly.csv"))


def select_vintages(mv):
    """Per market: the latest dump, and the prior dump 300-430 days older (E4's rule). Both trimmed: the
    LAG_TRIM_MONTHS months up to and including the dump month are dropped (posting lag, truncation)."""
    lat = mv.sort_values("dump_date").groupby("market_key").dump_date.last().rename("latest")
    m = mv.merge(lat, on="market_key")
    latest = m[m.dump_date == m.latest].copy()
    parts = []
    for mkt, g in m.groupby("market_key"):
        late = pd.Timestamp(g.latest.iloc[0])
        olds = sorted(v for v in g.dump_date.unique()
                      if C.VMATCH_DAYS[0] <= (late - pd.Timestamp(v)).days <= C.VMATCH_DAYS[1])
        if olds:
            parts.append(g[g.dump_date == olds[-1]])
    prior = pd.concat(parts, ignore_index=True) if parts else latest.iloc[0:0].copy()
    trim = lambda d: d[d.ymi <= d.dump_ymi - C.LAG_TRIM_MONTHS].drop(columns=["latest"])
    return trim(latest), trim(prior)


def load_kpi():
    k = pd.read_csv(C.KPI).dropna(subset=["nights_m"])
    k["qi"] = k.year.astype(int) * 4 + k.q.astype(int) - 1
    return k[["year", "q", "qi", "nights_m", "nights_m_yoy_pct"]].sort_values("qi")


def load_eurostat_yoy():
    e = pd.read_csv(C.EUROSTAT)
    d = pd.to_datetime(e.month); e["ymi"] = d.dt.year * 12 + d.dt.month - 1
    cols = [c for c in e.columns if c.endswith("_nights") and not c.startswith("eu27")]
    wide = e.set_index("ymi")[cols]
    wide = wide.reindex(range(wide.index.min(), wide.index.max() + 1))
    yoy = np.log(wide / wide.shift(12))
    long = wide.stack().rename("nights").reset_index().rename(columns={"level_1": "code"})
    long["code"] = long.code.str[:2]
    ly = yoy.stack().rename("y_yoy").reset_index().rename(columns={"level_1": "code"}); ly["code"] = ly.code.str[:2]
    return long.merge(ly, on=["ymi", "code"], how="left")


def load_kernel():
    k = pd.read_csv(C.K2).set_index("northern_stay_quarter")
    return {int(q[1]): k.loc[q, [f"weight_on_GBV_q-{i}" for i in range(4)]].to_numpy(float) for q in k.index}
```

```python file=analysis/src/forecast_methods/reviews_index_v2/index.py
"""The three y/y constructions per market-month, and their aggregation by ratio of sums (review-share weighting
within a group) and by FY25 nights shares across regions. yoy_vmatch is the primary (WPK-A §4)."""
import numpy as np, pandas as pd
import config as C

MEASURES = {"yoy_all": ("n_reviews", "n_lag12"),
            "yoy_mature": ("n_reviews_mature12", "n_mature12_lag12"),
            "yoy_vmatch": ("n_vm_cur", "n_vm_prior")}


def market_monthly(latest, prior):
    parts = []
    for mkt, g in latest.groupby("market_key"):
        d = g.set_index("ymi")[["n_reviews", "n_reviews_mature12"]].sort_index()
        full = d.reindex(range(int(d.index.min()), int(d.index.max()) + 1))
        out = pd.DataFrame({"n_reviews": full.n_reviews, "n_lag12": full.n_reviews.shift(12),
                            "n_reviews_mature12": full.n_reviews_mature12,
                            "n_mature12_lag12": full.n_reviews_mature12.shift(12)})
        p = prior[prior.market_key == mkt].set_index("ymi").n_reviews
        out["n_vm_cur"] = full.n_reviews
        out["n_vm_prior"] = [p.get(m - 12, np.nan) for m in full.index]
        out = out.dropna(subset=["n_reviews"]); out.index.name = "ymi"
        out = out.reset_index(); out.insert(0, "market_key", mkt); parts.append(out)
    my = pd.concat(parts, ignore_index=True)
    geo = latest[["market_key", "country", "region"]].drop_duplicates()
    return my.merge(geo, on="market_key", how="left")


def ratio_of_sums(df, by, measure):
    num, den = MEASURES[measure]
    g = df.dropna(subset=[num, den]).groupby(by)[[num, den]].sum()
    g = g[g[den] > 0]
    return (g[num] / g[den] - 1).rename(measure), g


def country_monthly(my, measure):
    s, _ = ratio_of_sums(my, ["country", "ymi"], measure)
    return s.reset_index()


def global_quarterly(my, measure, min_weight=0.5):
    """Quarter = ratio of the 3 monthly sums (markets must have all 3 months); region by review share; global
    by FY25 nights shares over the regions present (at least min_weight of the nights weight)."""
    d = my.copy(); d["qi"] = d.ymi // 3
    cnt = d.groupby(["market_key", "qi"]).ymi.transform("count"); d = d[cnt == 3]
    reg, _ = ratio_of_sums(d, ["region", "qi"], measure)
    reg = reg.reset_index().pivot(index="qi", columns="region", values=measure)
    w = pd.Series(C.FY25_NIGHTS_SHARE).reindex(reg.columns).fillna(0)
    ok = reg.notna()
    wsum = (ok * w).sum(axis=1)
    glob = (reg.fillna(0) * w).sum(axis=1) / wsum
    glob[wsum < min_weight * w.sum()] = np.nan
    return glob.rename(measure), reg
```

- [ ] **Step 4: Run** → PASS. Also run a smoke check against E4: `GLOBAL yoy_all w_reviews` for 2024 quarters from v2's `ratio_of_sums(d,["qi"],"yoy_all")` must match `E/index_quarterly.csv` within 0.5pp (the only differences are the trim, which does not touch 2024). Print both; do not proceed if they differ by more.

---

### Task 3: Kernel deconvolution

**Files:** Create `kernel.py`; Test `tests/test_kernel.py`

**Interfaces:** `kernel.deconvolve(stays: Series[qi], M)->Series[qi]`; `kernel.realised_share(qi_cohort, last_qi, M)->float`; `kernel.convolve(G: Series[qi], M)->Series[qi]`.

- [ ] **Step 1: Failing test**

```python file=analysis/src/forecast_methods/reviews_index_v2/tests/test_kernel.py
import numpy as np, pandas as pd


def test_roundtrip_and_realisation():
    import kernel as K, data as D
    M = D.load_kernel()
    rng = np.random.default_rng(3)
    G = pd.Series(100 + rng.normal(0, 5, 24).cumsum(), index=range(8080, 8104))
    S = K.convolve(G, M)
    G2 = K.deconvolve(S, M)
    assert np.allclose(G2.iloc[3:], G.iloc[3:], atol=1e-9)
    assert abs(K.realised_share(8102, 8105, M) - 1.0) < 1e-9            # 3Q25 fully landed by 2Q26
    assert 0.85 < K.realised_share(8104, 8105, M) < 0.95                  # 1Q26 ~87% by 2Q26
```

- [ ] **Step 2: Run** → FAIL. **Step 3: Implement**

```python file=analysis/src/forecast_methods/reviews_index_v2/kernel.py
"""Bookings <-> stays through the K2 lead-time kernel: stays in calendar quarter q come from bookings in
q..q-3 with weights M[q][0..3]. Levels, lower-triangular; the first three bookings are set to stays."""
import numpy as np, pandas as pd


def _q(qi):
    return int(qi % 4) + 1


def convolve(G, M):
    qi = G.index.to_numpy(); g = G.to_numpy(float); S = np.full(len(g), np.nan)
    for t in range(len(g)):
        w = M[_q(qi[t])]
        S[t] = g[t] if t < 3 else sum(w[k] * g[t - k] for k in range(4))
    return pd.Series(S, index=G.index)


def deconvolve(S, M):
    qi = S.index.to_numpy(); s = S.to_numpy(float); G = np.full(len(s), np.nan)
    for t in range(len(s)):
        w = M[_q(qi[t])]
        G[t] = s[t] if t < 3 else (s[t] - sum(w[k] * G[t - k] for k in range(1, 4))) / w[0]
    return pd.Series(G, index=S.index)


def realised_share(qi_cohort, last_qi, M):
    """Share of cohort qi_cohort's eventual stays observed by last_qi. K2 rows are normalised per STAY quarter,
    so the four weights that belong to one booking cohort do not sum to exactly 1; normalise by their total."""
    total = sum(M[_q(qi_cohort + k)][k] for k in range(4))
    seen = sum(M[_q(qi_cohort + k)][k] for k in range(4) if qi_cohort + k <= last_qi)
    return float(seen / total)
```

- [ ] **Step 4: Run** → PASS.

---

### Task 4: Stage A — the measurement panel

**Files:** Create `panel.py`; Test `tests/test_panel.py`

**Interfaces:** `panel.build_panel(my)->DataFrame[code, ymi, nights, y_yoy, x_yoy_vmatch, x_yoy_all, x_yoy_mature]`; `panel.fe_ols(df,y,x,group)->(beta, se_cluster, d, xd, yd, resid)`; `panel.wild_cluster_p(d, xd, yd, group)->(p, t)`; `panel.run_stage_a(my)->(tests DataFrame, panel DataFrame, per_country DataFrame)`.

- [ ] **Step 1: Failing test (synthetic panel recovers beta)**

```python file=analysis/src/forecast_methods/reviews_index_v2/tests/test_panel.py
import numpy as np, pandas as pd


def test_fe_ols_recovers_beta_and_wild_p_small():
    import panel as P
    rng = np.random.default_rng(7); rows = []
    for g in range(18):
        fe = rng.normal(0, 0.3); x = rng.normal(0, 0.2, 39); y = fe + 0.5 * x + rng.normal(0, 0.05, 39)
        rows += [dict(code=f"C{g}", ymi=i, x=x[i], y=y[i]) for i in range(39)]
    df = pd.DataFrame(rows)
    beta, se, d, xd, yd, resid = P.fe_ols(df, "y", "x", "code")
    assert abs(beta - 0.5) < 0.05
    p, t = P.wild_cluster_p(d, xd, yd, "code", B=299)
    assert p < 0.02
```

- [ ] **Step 2: Run** → FAIL. **Step 3: Implement**

```python file=analysis/src/forecast_methods/reviews_index_v2/panel.py
"""Stage A: do review counts measure stays? Country x month, review y/y (log) against observed Eurostat
platform-nights y/y (log). Country fixed effects; wild-cluster bootstrap over countries; first differences;
leave-one-country-out; era split; per-country expanding walk-forward vs naive."""
import numpy as np, pandas as pd
import config as C, data as D, index as I, scoring as S


def build_panel(my):
    eu = D.load_eurostat_yoy()
    p = eu[["code", "ymi", "nights", "y_yoy"]].copy()
    sub = my[my.country.isin(C.EU_CODE)]
    for meas in ["yoy_vmatch", "yoy_all", "yoy_mature"]:
        s = I.country_monthly(sub, meas); s["code"] = s.country.map(C.EU_CODE)
        s[f"x_{meas}"] = np.log1p(s[meas])
        p = p.merge(s[["code", "ymi", f"x_{meas}"]], on=["code", "ymi"], how="left")
    return p[p.code.isin(set(C.EU_CODE.values()))]


def fe_ols(df, y, x, group):
    d = df[[y, x, group]].dropna().copy()
    yd = d[y] - d.groupby(group)[y].transform("mean")
    xd = d[x] - d.groupby(group)[x].transform("mean")
    beta = float((xd * yd).sum() / (xd ** 2).sum())
    resid = yd - beta * xd
    se = cluster_se(xd, resid, d[group])
    return beta, se, d, xd, yd, resid


def cluster_se(xd, e, cl):
    s = pd.Series(xd.to_numpy() * e.to_numpy()).groupby(np.asarray(cl)).sum()
    return float(np.sqrt((s ** 2).sum()) / (xd ** 2).sum())


def wild_cluster_p(d, xd, yd, group, B=999, seed=1):
    """Rademacher wild cluster bootstrap of the t statistic under H0 beta = 0 (restricted residuals = yd)."""
    rng = np.random.default_rng(seed)
    beta = float((xd * yd).sum() / (xd ** 2).sum()); t0 = beta / cluster_se(xd, yd - beta * xd, d[group])
    cl = d[group].to_numpy(); ucl = np.unique(cl); pos = pd.Series(range(len(ucl)), index=ucl).reindex(cl).to_numpy()
    xd_np, yd_np = xd.to_numpy(), yd.to_numpy(); sxx = (xd_np ** 2).sum(); ts = []
    for _ in range(B):
        w = rng.choice([-1.0, 1.0], size=len(ucl))[pos]
        ystar = yd_np * w; b = (xd_np * ystar).sum() / sxx; e = ystar - b * xd_np
        s = np.bincount(pos, weights=xd_np * e); se = np.sqrt((s ** 2).sum()) / sxx
        ts.append(b / se if se > 0 else 0.0)
    ts = np.abs(np.array(ts))
    return float((np.sum(ts >= abs(t0)) + 1) / (B + 1)), float(t0)


def first_differences(p, x):
    d = p.sort_values(["code", "ymi"]).copy()
    for c in ["y_yoy", x]:
        d[f"d_{c}"] = d.groupby("code")[c].diff()
        d.loc[d.groupby("code").ymi.diff() != 1, f"d_{c}"] = np.nan
    return d


def per_country_walkforward(p, x):
    rows = []
    for code, g in p.groupby("code"):
        r = S.score_window(g.set_index("ymi")[x], g.set_index("ymi").y_yoy, C.PANEL_START, C.PANEL_SCORE_START,
                           season_lag=12, score_end=C.PANEL_END)
        if r:
            rows.append(dict(code=code, n_scored=r["wf_n"], ratio_vs_naive=r["wf_ratio_vs_naive"],
                             ratio_vs_prior=r["wf_ratio_vs_prior"], rmse=r["wf_rmse"]))
    return pd.DataFrame(rows)


def run_stage_a(my, measure="yoy_vmatch"):
    x = f"x_{measure}"
    p = build_panel(my)
    w = p[(p.ymi >= C.PANEL_START) & (p.ymi <= C.PANEL_END)].dropna(subset=["y_yoy", x])
    rows = []
    beta, se, d, xd, yd, resid = fe_ols(w, "y_yoy", x, "code")
    pA1, t = wild_cluster_p(d, xd, yd, "code")
    n_obs, n_c = len(d), d.code.nunique()
    r2w = 1 - (resid ** 2).sum() / (yd ** 2).sum()
    rows.append(dict(test="A1_elasticity", statistic="beta (country FE)", value=beta, se_cluster=se, t=t, p=pA1,
                     n=n_obs, clusters=n_c, extra=f"within-R2 {r2w:.3f}", pass_line="p<0.01",
                     passed=bool(pA1 < C.PREREG["A1_beta_p_max"])))
    fd = first_differences(w, x)
    bD, seD, dD, xdD, ydD, _ = fe_ols(fd, "d_y_yoy", f"d_{x}", "code")
    pA2, tD = wild_cluster_p(dD, xdD, ydD, "code")
    rows.append(dict(test="A2_first_differences", statistic="beta on d(y/y)", value=bD, se_cluster=seD, t=tD, p=pA2,
                     n=len(dD), clusters=dD.code.nunique(), extra="", pass_line="beta>0, p<0.05",
                     passed=bool(bD > 0 and pA2 < C.PREREG["A2_diff_p_max"])))
    loco = {c: fe_ols(w[w.code != c], "y_yoy", x, "code")[0] for c in sorted(w.code.unique())}
    rows.append(dict(test="A3_leave_one_country_out", statistic="beta range", value=min(loco.values()),
                     se_cluster=np.nan, t=np.nan, p=np.nan, n=len(loco), clusters=n_c,
                     extra=f"max {max(loco.values()):.3f}; all same sign {all(np.sign(v) == np.sign(beta) for v in loco.values())}",
                     pass_line="reported", passed=bool(all(np.sign(v) == np.sign(beta) for v in loco.values()))))
    early = w[w.ymi < C.ymi(2025, 1)]; late = w[w.ymi >= C.ymi(2025, 1)]
    b1, s1 = fe_ols(early, "y_yoy", x, "code")[:2]; b2, s2 = fe_ols(late, "y_yoy", x, "code")[:2]
    z = (b2 - b1) / np.sqrt(s1 ** 2 + s2 ** 2)
    rows.append(dict(test="A4_era_split", statistic="beta 2023-24 vs 2025-26", value=b1, se_cluster=s1, t=z, p=np.nan,
                     n=len(early) + len(late), clusters=n_c, extra=f"beta late {b2:.3f} se {s2:.3f}; |z| {abs(z):.2f}",
                     pass_line="reported (|z|<2)", passed=bool(abs(z) < 2)))
    pc = per_country_walkforward(p, x)
    med = float(pc.ratio_vs_naive.median())
    rows.append(dict(test="A5_out_of_sample_by_country", statistic="median walk-forward RMSE ratio vs naive", value=med,
                     se_cluster=np.nan, t=np.nan, p=np.nan, n=int(pc.n_scored.sum()), clusters=len(pc),
                     extra=f"countries<=0.75: {int((pc.ratio_vs_naive <= 0.75).sum())}/{len(pc)}",
                     pass_line="median<=0.75", passed=bool(med <= C.PREREG["A5_median_ratio_max"])))
    t = pd.DataFrame(rows); t.insert(0, "measure", measure)
    return t, p, pc
```

- [ ] **Step 4: Run** → PASS.

---

### Task 5: Stage B — calibration and walk-forward (in `stages.py`)

**Files:** Create `stages.py` (Stage B and C functions live together: they share the index and the mapping). Test `tests/test_stages.py`.

**Interfaces:** `stages.build_index(my)->DataFrame[qi, yoy_vmatch, yoy_all, yoy_mature]` (percent); `stages.run_stage_b(idx, kpi)->(results DataFrame, paths DataFrame)`; `stages.run_stage_c(idx, kpi, my, M)->(results DataFrame, gap DataFrame)`.

- [ ] **Step 1: Failing test**

```python file=analysis/src/forecast_methods/reviews_index_v2/tests/test_stages.py
import numpy as np, pandas as pd


def test_frozen_mapping_uses_only_pre_freeze_quarters():
    import stages as T, config as C
    qi = np.arange(C.qi(2023, 1), C.qi(2026, 2) + 1)
    idx = pd.DataFrame({"qi": qi, "yoy_vmatch": np.linspace(30, 5, len(qi))})
    y = pd.Series(2 + 0.3 * idx.yoy_vmatch.to_numpy(), index=qi)
    y[C.POST_QIS] += 5.0                                             # a post-RNPL jump must not move the fit
    a, b, n = T.frozen_mapping(idx.set_index("qi").yoy_vmatch, y)
    assert n == C.FREEZE_QI - C.qi(2023, 1) + 1 and abs(b - 0.3) < 1e-9 and abs(a - 2) < 1e-9
```

- [ ] **Step 2: Run** → FAIL. **Step 3: Implement**

```python file=analysis/src/forecast_methods/reviews_index_v2/stages.py
"""Stage B (walk-forward calibration on the record's windows) and Stage C (the post-RNPL gap against the
pre-RNPL band, the cohort-consistent variant, the exercised-share bound, the 3Q26 read)."""
import numpy as np, pandas as pd
import config as C, index as I, kernel as K, scoring as S


def build_index(my):
    cols = {}
    for meas in I.MEASURES:
        g, _ = I.global_quarterly(my, meas); cols[meas] = g * 100.0
    return pd.DataFrame(cols).rename_axis("qi").reset_index()


def run_stage_b(idx, kpi):
    y = kpi.set_index("qi").nights_m_yoy_pct
    rows, paths = [], []
    for meas in ["yoy_vmatch", "yoy_all", "yoy_mature"]:
        x = idx.set_index("qi")[meas]
        for wname, (ws, ss) in C.WINDOWS.items():
            for sub, end in [("full", None), ("pre_rnpl", C.FREEZE_QI)]:
                r = S.score_window(x, y, ws, ss, score_end=end)
                if r is None:
                    continue
                pth = r.pop("path"); lo, hi = S.ratio_interval(pth.err_feature, pth.err_naive)
                dm, pdm = S.dm_test(pth.err_feature, pth.err_naive)
                rows.append(dict(measure=meas, window=wname, subset=sub, target="level", **r, ratio_lo90=lo, ratio_hi90=hi,
                                 dm_stat=dm, dm_p=pdm,
                                 passed=(bool(r["wf_ratio_vs_naive"] <= C.PREREG["B1_ratio_max"]) if sub == "full" else np.nan)))
                pth.insert(0, "subset", sub); pth.insert(0, "window", wname); pth.insert(0, "measure", meas); paths.append(pth)
            # B5: acceleration
            ra = S.score_window(x.diff(), y.diff(), ws, ss)
            if ra is not None:
                pa = ra.pop("path"); rows.append(dict(measure=meas, window=wname, subset="full", target="acceleration", **ra,
                                                    ratio_lo90=np.nan, ratio_hi90=np.nan, dm_stat=np.nan, dm_p=np.nan, passed=np.nan))
    res = pd.DataFrame(rows)
    # B1 verdict on the primary
    prim = res[(res.measure == "yoy_vmatch") & (res.subset == "full") & (res.target == "level")]
    res.attrs["B1_passed"] = bool((prim.wf_ratio_vs_naive <= C.PREREG["B1_ratio_max"]).all() and len(prim) == 2)
    return res, pd.concat(paths, ignore_index=True)


def loco_slopes(x, y, start_qi=C.qi(2023, 1), end_qi=C.qi(2026, 2)):
    d = pd.DataFrame({"x": x, "y": y}).dropna(); d = d[(d.index >= start_qi) & (d.index <= end_qi)]
    full_b, full_a = S.ols(d.x, d.y)
    rows = [dict(left_out=None, slope=full_b, intercept=full_a)]
    for q in d.index:
        b, a = S.ols(d.drop(q).x, d.drop(q).y); rows.append(dict(left_out=int(q), slope=b, intercept=a))
    return pd.DataFrame(rows)


def frozen_mapping(x, y, start_qi=C.qi(2023, 1), freeze_qi=C.FREEZE_QI):
    d = pd.DataFrame({"x": x, "y": y}).dropna(); d = d[(d.index >= start_qi) & (d.index <= freeze_qi)]
    b, a = S.ols(d.x, d.y)
    return float(a), float(b), int(len(d))


def cohort_index(my, M):
    """Cohort-consistent vmatch: deconvolve quarterly stays levels within each vintage per region, then the
    same-relative-age ratio, then FY25 weights. Returns percent series by booking quarter with realised share."""
    d = my.copy(); d["qi"] = d.ymi // 3
    cnt = d.groupby(["market_key", "qi"]).ymi.transform("count"); d = d[cnt == 3]
    reg_rows = {}
    for reg, g in d.groupby("region"):
        cur = g.groupby("qi").n_vm_cur.sum(); pri = g.groupby("qi").n_vm_prior.sum()
        ok = (cur > 0) & (pri > 0); cur, pri = cur[ok], pri[ok]
        full = range(int(cur.index.min()), int(cur.index.max()) + 1)
        Gc = K.deconvolve(cur.reindex(full).interpolate(), M); Gp = K.deconvolve(pri.reindex(full).interpolate(), M)
        reg_rows[reg] = (Gc / Gp - 1.0)
    reg = pd.DataFrame(reg_rows)
    w = pd.Series(C.FY25_NIGHTS_SHARE).reindex(reg.columns).fillna(0); ok = reg.notna()
    glob = (reg.fillna(0) * w).sum(axis=1) / (ok * w).sum(axis=1)
    last = int(reg.index.max())
    out = pd.DataFrame({"qi": glob.index, "yoy_cohort_vmatch": glob.to_numpy() * 100.0,
                        "realised_share": [K.realised_share(q, last, M) for q in glob.index]})
    return out


def run_stage_c(idx, kpi, my, M):
    y = kpi.set_index("qi").nights_m_yoy_pct
    rows, gaps = [], []
    # primary: same-quarter vmatch
    x = idx.set_index("qi").yoy_vmatch
    a, b, n = frozen_mapping(x, y)
    band_res = S.score_window(x, y, *C.WINDOWS["W2"], score_end=C.FREEZE_QI)
    band = float(band_res["wf_rmse"]) if band_res else np.nan
    for q in C.POST_QIS:
        if q in x.index and q in y.index and np.isfinite(x[q]):
            g = float(y[q] - (a + b * x[q]))
            gaps.append(dict(variant="primary", qi=q, index_pct=float(x[q]), mapped_pct=a + b * x[q], actual_pct=float(y[q]),
                             gap_pp=g, band_pp=band, gap_in_bands=g / band if band else np.nan, realised_share=1.0))
    gp = pd.DataFrame([r for r in gaps if r["variant"] == "primary"])
    mean_gap = float(gp.gap_pp.mean()); nq = int((gp.gap_in_bands > C.PREREG["C1_quarter_min_bands"]).sum())
    c1 = bool(mean_gap > C.PREREG["C1_mean_gap_min_bands"] * band and nq >= C.PREREG["C1_quarters_min"])
    reading = ("pass: KPI above stays-implied beyond the band" if c1 else
               "no measurable RNPL signature in stays" if abs(mean_gap) <= band else
               "bookings below stays-implied (contradicts the mechanism)" if mean_gap < -band else "positive but inside the pass line")
    rows.append(dict(test="C1_primary_gap", value=mean_gap, band_pp=band, quarters_over_half_band=nq, n_quarters=len(gp),
                     frozen_a=a, frozen_b=b, n_fit=n, passed=c1, reading=reading))
    # cohort-consistent variant
    ci = cohort_index(my, M).set_index("qi").yoy_cohort_vmatch
    ac, bc, ncn = frozen_mapping(ci, y)
    bres = S.score_window(ci, y, *C.WINDOWS["W2"], score_end=C.FREEZE_QI); bandc = float(bres["wf_rmse"]) if bres else np.nan
    rs = cohort_index(my, M).set_index("qi").realised_share
    for q in C.POST_QIS[:3]:
        if q in ci.index and np.isfinite(ci[q]):
            g = float(y[q] - (ac + bc * ci[q]))
            gaps.append(dict(variant="cohort", qi=q, index_pct=float(ci[q]), mapped_pct=ac + bc * ci[q], actual_pct=float(y[q]),
                             gap_pp=g, band_pp=bandc, gap_in_bands=g / bandc if bandc else np.nan, realised_share=float(rs[q])))
    gc = pd.DataFrame([r for r in gaps if r["variant"] == "cohort"])
    if len(gc):
        mg = float(gc.gap_pp.mean()); nqc = int((gc.gap_in_bands > 0.5).sum())
        rows.append(dict(test="C1_cohort_gap", value=mg, band_pp=bandc, quarters_over_half_band=nqc, n_quarters=len(gc),
                         frozen_a=ac, frozen_b=bc, n_fit=ncn, passed=bool(mg > bandc and nqc >= 2), reading="reported beside primary"))
    # C2: exercised-share bound
    for bB in C.PREREG["beta_B_bundle_pts"]:
        rows.append(dict(test=f"C2_exercised_share_betaB_{bB:.0f}", value=mean_gap / bB, band_pp=band / bB,
                         quarters_over_half_band=np.nan, n_quarters=len(gp), frozen_a=a, frozen_b=b, n_fit=n, passed=np.nan,
                         reading="share of the disclosed bundle lift that did not become stays, +/- band"))
    return pd.DataFrame(rows), pd.DataFrame(gaps)


def stage_c3_3q26(a, b, band):
    """3Q26 partial read through the frozen mapping. Primary: E6's per-region vintage-matched, review-weighted
    quarter-to-date y/y (vintage_matched_nowcast.csv, period 3q26_to_date) combined with FY25 nights shares —
    the same construction as the v2 index — lifted by E6's measured review-weighted partial-to-full gap.
    Sensitivity: E6's own GLOBAL w_reviews cell (construction mismatch). Band = pre-RNPL walk-forward RMSE and
    the gap sd in quadrature."""
    q = pd.read_csv(C.E6_NOWCAST)
    r = q[(q.measure == "yoy_vmatch") & (q.weighting == "w_reviews") & (q.region == "GLOBAL")].iloc[0]
    vm = pd.read_csv(C.E / "vintage_matched_nowcast.csv")
    reg = vm[(vm.period == "3q26_to_date") & (vm.region.isin(C.FY25_NIGHTS_SHARE))].set_index("region").vmatch_cw
    w = pd.Series(C.FY25_NIGHTS_SHARE).reindex(reg.index)
    partial_v2 = float((reg * w).sum() / w.sum() * 100)
    gap = float(r.gap_mean_pp); gsd = float(r.gap_sd_pp) if np.isfinite(r.gap_sd_pp) else 0.0
    full_v2 = partial_v2 + gap; pt = a + b * full_v2
    sd = float(np.sqrt(band ** 2 + (b * gsd) ** 2))
    full_e6 = float(r.full_index_3q26_pct)
    return dict(index_3q26_partial_pct=partial_v2, partial_to_full_gap_pp=gap, index_3q26_full_pct=full_v2,
                implied_nights_yoy=float(pt), band_pp=sd, lo=float(pt - sd), hi=float(pt + sd),
                regional_partial_pct={k: float(v * 100) for k, v in reg.items()},
                sensitivity_e6_global_cw=dict(index_full_pct=full_e6, implied_nights_yoy=float(a + b * full_e6)),
                note="primary uses E6 per-region vmatch_cw x FY25 shares (v2 construction); sensitivity is E6's GLOBAL w_reviews cell")


```

- [ ] **Step 4: Run** → PASS.

---

### Task 6: Stage D — power and the exploratory event study

**Files:** Create `did_power.py`; no unit test beyond a smoke run (the numbers are the ones already produced by the throwaway scripts and are checked against them: US pre-trend mean 2024-01..2025-07 ≈ −4.6pp; permutation MDE on the normalised window ≈ 4.7–7.2pp).

```python file=analysis/src/forecast_methods/reviews_index_v2/did_power.py
"""Stage D: why the staggered DiD is not the evidence. Pre-trend of US vs never-treated controls, minimum
detectable effect from pre-period placebo launches and permutation, and an EXPLORATORY event study on the
US arm (never-treated controls, single cohort), cluster-bootstrap bands. No coefficient is a claim."""
import numpy as np, pandas as pd
import config as C


def _yoy_panel(my, measure="yoy_vmatch"):
    from index import MEASURES
    num, den = MEASURES[measure]
    d = my.dropna(subset=[num, den]); d = d[d[den] > 0]
    p = d.assign(v=np.log(d[num] / d[den])).pivot_table(index="ymi", columns="market_key", values="v")
    return p


def _arms(my):
    cty = my.groupby("market_key").country.first()
    us = cty.index[cty == "united-states"]; ct = cty.index[cty.isin(C.NEVER_TREATED)]
    return list(us), list(ct)


def _did(y, tr, co, t0, pre, post):
    w = y.loc[t0 - pre: t0 + post - 1]; ip = w.index >= t0
    e = w.loc[ip].mean() - w.loc[~ip].mean(); return float(e[tr].mean() - e[co].mean())


def run_stage_d(my, B=150, seed=20260918):
    rng = np.random.default_rng(seed)
    y = _yoy_panel(my); us, ct = _arms(my); us = [m for m in us if m in y.columns]; ct = [m for m in ct if m in y.columns]
    gap = ((y[us].mean(axis=1) - y[ct].mean(axis=1)) * 100).loc[C.ymi(2024, 1): C.ymi(2026, 6)]
    pre = gap.loc[: C.RNPL_US_LAUNCH_YMI - 1]
    rows = [dict(item="US_minus_controls_pretrend_mean_pp", value=float(pre.mean()), detail="2024-01..2025-07, y/y log stays")]
    allm = np.array(us + ct); dates = range(C.ymi(2024, 7), C.ymi(2025, 2) + 1)
    real = np.array([_did(y, us, ct, d, 6, 6) for d in dates])
    perm = np.array([_did(y, s[: len(us)], s[len(us):], d, 6, 6) for d in dates for s in (rng.permutation(allm) for _ in range(B))])
    rows += [dict(item="MDE_pp_permutation", value=float(2.8 * perm.std() * 100), detail="alpha .05 two-sided, power .8; 6 pre / 6 post; normalised window"),
             dict(item="MDE_pp_placebo_dates", value=float(2.8 * real.std() * 100), detail="same, true assignment across placebo dates"),
             dict(item="effect_looked_for_pp", value=3.0, detail="upper end of the disclosed bundle lift on bookings")]
    # exploratory event study: e in -12..+10 relative to Aug 2025; ATT(e) = mean_US[y_e - ybar_pre] - mean_CT[same]
    base = y.loc[C.RNPL_US_LAUNCH_YMI - 12: C.RNPL_US_LAUNCH_YMI - 1].mean()
    es = []
    for e in range(-12, 11):
        m = C.RNPL_US_LAUNCH_YMI + e
        if m not in y.index: continue
        dev = y.loc[m] - base
        att = float(dev[us].mean() - dev[ct].mean())
        boots = [float(dev[rng.choice(us, len(us))].mean() - dev[rng.choice(ct, len(ct))].mean()) for _ in range(300)]
        es.append(dict(event_month=e, ymi=m, att_pp=att * 100, lo90=np.quantile(boots, .05) * 100, hi90=np.quantile(boots, .95) * 100))
    return pd.DataFrame(rows), gap.rename("us_minus_controls_pp").reset_index(), pd.DataFrame(es)
```

- [ ] Smoke: `python3 -c "import did_power"` imports cleanly; full run in Task 9.

---

### Task 7: Figures

**Files:** Create `figures.py`. **Before writing it, load the `dataviz` skill** and use its palette/marks. Five figures into `FIG/`: `fig1_panel_measurement.png` (country-month scatter, β line, CI, per-country ratios inset), `fig2_walkforward.png` (actual nights y/y vs v2 walk-forward prediction and naive, both windows; error bars panel), `fig3_post_rnpl_gap.png` (four post quarters: gap bars against ±band, calibration residuals as grey dots, 3Q26 read as an open marker), `fig4_did_power.png` (US-minus-controls pre-trend line with the launch date; MDE vs effect looked for), `fig5_event_study.png` (EXPLORATORY watermark). Each figure's CSV lives beside it. The code is written at execution time after the skill is loaded (its palette rules are the contract), then smoke-tested by rendering all five.

---

### Task 8: Orchestrator, freeze, results

**Files:** Create `run.py`, `tools_extract.py` (plan-block extractor used in Task 0 onward).

```python file=analysis/src/forecast_methods/reviews_index_v2/tools_extract.py
"""Materialise the `file=` code blocks of the implementation plan into the repo. Idempotent."""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
PLAN = ROOT / "docs/superpowers/plans/2026-09-18-reviews-index-v2.md"
blocks = re.findall(r"```python file=(\S+)\n(.*?)```", PLAN.read_text(), flags=re.S)
for rel, code in blocks:
    p = ROOT / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(code)
    print("wrote", rel, len(code.splitlines()), "lines")
```

```python file=analysis/src/forecast_methods/reviews_index_v2/run.py
"""Orchestrator. python3 run.py --stage freeze|A|B|C|D|figures|all. Stages write into config.OUT only.
freeze: writes prereg.json, appends its sha256 and timestamp as the first line of the note's §2. Refuses to run
A/B/C/D before a freeze line exists."""
import argparse, hashlib, json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C, data as D, index as I


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def freeze():
    C.OUT.mkdir(parents=True, exist_ok=True)
    txt = json.dumps(C.PREREG, indent=2, sort_keys=True); (C.OUT / "prereg.json").write_text(txt)
    h = hashlib.sha256(txt.encode()).hexdigest(); stamp = time.strftime("%Y-%m-%d %H:%M %Z")
    note = C.NOTE.read_text()
    if "FROZEN" in note:
        log("already frozen; not re-freezing"); return
    line = f"**FROZEN {stamp}** — `prereg.json` sha256 `{h}`. Stages run in order below; no pass line changes after this line.\n"
    note = note.replace("*(empty until frozen and run)*", line); C.NOTE.write_text(note); log(f"frozen {h[:12]}")


def require_frozen():
    if "FROZEN" not in C.NOTE.read_text():
        sys.exit("refusing to run: pre-registration not frozen (python3 run.py --stage freeze)")


def load_all():
    mv = D.load_counted(); latest, prior = D.select_vintages(mv); my = I.market_monthly(latest, prior)
    log(f"market-months {len(my)}, markets {my.market_key.nunique()}, vintage-matched markets {my.dropna(subset=['n_vm_prior']).market_key.nunique()}")
    return my


def stage_a(my):
    import panel as P
    res, p, pc = P.run_stage_a(my)
    p.to_csv(C.OUT / "panel_country_month.csv", index=False); pc.to_csv(C.OUT / "panel_per_country_walkforward.csv", index=False)
    resA = [res]
    for sens in ["yoy_all", "yoy_mature"]:
        r, _, _ = P.run_stage_a(my, sens); resA.append(r)
    out = pd.concat(resA, ignore_index=True); out.to_csv(C.OUT / "stage_a_tests.csv", index=False)
    prim = out[out.measure == "yoy_vmatch"].set_index("test")
    passed = bool(prim.loc["A1_elasticity", "passed"] and prim.loc["A2_first_differences", "passed"] and prim.loc["A5_out_of_sample_by_country", "passed"])
    log(f"Stage A {'PASS' if passed else 'FAIL'}\n{out[['measure','test','value','p','passed','extra']].to_string(index=False)}")
    return passed


def stage_b(my):
    import stages as T
    idx = T.build_index(my); idx.to_csv(C.OUT / "index_quarterly_v2.csv", index=False)
    kpi = D.load_kpi(); res, paths = T.run_stage_b(idx, kpi)
    res.to_csv(C.OUT / "stage_b_walkforward.csv", index=False); paths.to_csv(C.OUT / "stage_b_paths.csv", index=False)
    loco = T.loco_slopes(idx.set_index("qi").yoy_vmatch, kpi.set_index("qi").nights_m_yoy_pct); loco.to_csv(C.OUT / "stage_b_loco_slopes.csv", index=False)
    log(f"Stage B B1 {'PASS' if res.attrs['B1_passed'] else 'FAIL'}\n" + res[["measure","window","subset","target","wf_n","wf_ratio_vs_naive","ratio_lo90","ratio_hi90","dm_p","mean_err","passed"]].to_string(index=False))
    return res.attrs["B1_passed"]


def stage_c(my):
    import stages as T
    idx = pd.read_csv(C.OUT / "index_quarterly_v2.csv"); kpi = D.load_kpi(); M = D.load_kernel()
    res, gaps = T.run_stage_c(idx, kpi, my, M)
    r0 = res.iloc[0]; c3 = T.stage_c3_3q26(r0.frozen_a, r0.frozen_b, r0.band_pp)
    res.to_csv(C.OUT / "stage_c_tests.csv", index=False); gaps.to_csv(C.OUT / "stage_c_gap.csv", index=False)
    (C.OUT / "stage_c3_3q26.json").write_text(json.dumps(c3, indent=2))
    log(f"Stage C C1 {'PASS' if bool(r0.passed) else 'FAIL'} — {r0.reading}\n{gaps.to_string(index=False)}\n{res.to_string(index=False)}\n3Q26: {c3}")
    return bool(r0.passed)


def stage_d(my):
    import did_power as DP
    rows, gap, es = DP.run_stage_d(my)
    rows.to_csv(C.OUT / "stage_d_power.csv", index=False); gap.to_csv(C.OUT / "stage_d_pretrend.csv", index=False); es.to_csv(C.OUT / "stage_d_event_study_EXPLORATORY.csv", index=False)
    log(f"Stage D\n{rows.to_string(index=False)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", default="all"); a = ap.parse_args()
    C.OUT.mkdir(parents=True, exist_ok=True); C.FIG.mkdir(parents=True, exist_ok=True)
    if a.stage == "freeze":
        freeze(); sys.exit()
    require_frozen(); my = load_all(); verdict = {}
    if a.stage in ("A", "all"): verdict["A"] = stage_a(my)
    if a.stage in ("B", "all"): verdict["B"] = stage_b(my)
    if a.stage in ("C", "all"): verdict["C"] = stage_c(my)
    if a.stage in ("D", "all"): stage_d(my)
    if a.stage in ("figures", "all"):
        import figures as F; F.render_all()
    (C.OUT / "RESULTS.json").write_text(json.dumps({**verdict, "ran": time.strftime("%Y-%m-%d %H:%M")}, indent=2)); log(f"verdicts {verdict}")
```

- [ ] Steps: extract → `pytest tests -q` all green → `--stage freeze` → `--stage A` → `--stage B` → `--stage C` → `--stage D` → figures → write §2 of the note from the CSVs (prose by the session, numbers from files only).

---

## Self-review

- Spec coverage: §1-A (A1–A5) → Task 4; §1-B (B1–B5, bootstrap, DM, E5 regression check) → Tasks 1, 5; §1-C (primary four quarters, cohort three, C2, C3) → Task 5; §1-D → Task 6; freeze → Task 8; figures → Task 7; note §2 → Task 8 last step. Gap: B4's 2023-vintage substitution of 1Q23 is deferred (needs the v2 folder's `yoy_all` index aligned to the vmatch primary and is a sensitivity, not a gate) — recorded in the note as not run.
- Placeholders: none; Task 7 code is deliberately written after the dataviz skill loads, with its figure list fixed here.
- Types: `score_window` returns `path` with columns `t, pred, actual, err_feature, err_naive`; `run_stage_b` consumes `err_feature/err_naive`; `run_stage_c` consumes `wf_rmse`; `run_stage_a` consumes `wf_ratio_vs_naive/wf_ratio_vs_prior/wf_rmse/wf_n`. `frozen_mapping` returns `(a, b, n)` and `run_stage_c` writes `frozen_a, frozen_b, n_fit` — consistent.

---

### Task 9 (added after the run, on Theo's instruction): Stage E — the view

**Files:** Create `view.py` (`view_vs_street()`, `rnpl_evidence()`, `run_stage_e()`); extend `config.py` with `BASE_PATH` (DEC-0029/0019/0025 numbers), `STREET` (DEC-0005), `KPI_PANEL`; extend `figures.py` with `fig6_view_vs_street()` and `fig7_rnpl_evidence()`; `run.py --stage E`. Outputs `stage_e_view_vs_street.csv` (our base and v2 read vs Street, z and tail probabilities), `stage_e_rnpl_evidence.csv` (unearned fees − GBV spread, pre mean/sd, per-quarter z, Welch t). Note §3. Nothing fitted; all inputs cited to the record. Done 18 Sep 16:16.

### Task 10 (added): Stage F — the final model, two channels

`final_model.py`: print = stays + I. Stays = v2 read (3Q26) then the mechanism path; I observed 3Q25–2Q26 (Stage C gaps), 3Q26 scenarios {0, +0.72, +1.59}, base +0.54 (DEC-0029 print minus stays read). Two channels with sources: level (each wave's exercise lands at stay dates via K2: `final_model_landing.csv`) and y/y (lap of the year-ago gap). Parameters: ceiling, exercise-at-stay-date (D002), long-lead share 3–6%. `fig8_final_model.png`; fig0 overview panel 4 = fig8. Note §4, §4.1. Done 18 Sep 17:15.
