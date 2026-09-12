"""
WS-L (ADR v3, 11 Sep 2026): shared code for the regional ex-FX ADR forecast.

Question: does a region-by-region forecast of ex-FX ADR (each region on its own rule or proxy,
chosen strictly on data before the scored quarter), aggregated into the blended ex-FX series, beat
the pre-registered last-quarter residual rule on the S harness?

Design (fixed before any result was seen; see research/notes/adrv3/L_regional-residual-and-proxies.md):

* Regional ex-FX ADR y/y comes from data/processed/adr/04_regional_quarterly_wide.csv. A regional
  quarter is USABLE for fitting, selection and per-region scoring only if its ex-FX is disclosed
  (letter) or solved (disclosed reported y/y minus the WS-02 basket x pass-through). Modelled
  quarters (annual anchor x seasonal) are carried in the panel because H's geo-mix identity uses
  them, but no rule is fitted or scored on them. Usable from: NA 2Q23, EMEA 1Q23, LatAm 4Q24,
  APAC 4Q24.

* Aggregation reproduces H's identity exactly: within-region ex-FX = sum(s0 A0 (1+g)) / sum(s0 A0)
  - 1 with s0 the year-ago nights share and A0 the year-ago anchored regional ADR (both knowable
  before the scored quarter); blended ex-FX reconstructed = within + geo mix. The model's ex-FX
  path handed to S.score is within_forecast(t) + H's measured geo_mix_pp(t). S.exfx_from_residual
  is NOT used: it adds the measured size and LOS terms, which regional ex-FX already contains, so
  routing a regional forecast through it would double count. The reconstruction gap (H's
  geo_recon_gap_pp: reconstructed minus disclosed integer, rounding and modelled-region error) is
  not modelled in the primary variant; a gap-last_q variant is reported alongside.

* Candidates per region: own-history rules (last_q, persistence = mean of last two, trailing_4q,
  ar1 expanding with at least four training quarters as the S benchmark, last_q_ex_size = last
  quarter's ex-FX net of workstream I's regional size term plus the current-quarter size term) and,
  where a proxy covers the region, an expanding OLS of regional ex-FX on the proxy in level and
  first difference at lags 0 and 1 (J2's forms, at least four training quarters). NA proxies: CPI
  lodging SA, CPI lodging NSA, CPI hotels and motels NSA, BEA hotels price. EMEA proxies: euro-area
  HICP accommodation services, INE Spain hotel price index. LatAm and APAC have no covering proxy
  and run on own history only. Marriott and Hilton worldwide RevPAR are tested for NA in L2 but
  kept out of the selection pool because there is no 3Q26 reading in hand.

* Walk-forward selection at scored quarter t: every candidate's out-of-sample record is the set of
  predictions it made at usable quarters s < t, each built on data strictly before s. A candidate
  is eligible at t only if that record has at least MIN_SELECT = 4 quarters; the pick is the
  eligible candidate with the lowest RMSE (ties to the earlier candidate in CANDIDATE order, own
  rules first). With no eligible candidate the region runs last_q. Nothing at t uses the actual
  at t; lag-0 proxy forms use the proxy reading for t, which publishes before the print.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import S1_scoring as S  # noqa: E402

ROOT = S.ROOT
QORDER, QI = S.QORDER, S.QI
OUT = os.path.join(ROOT, "data", "processed", "adrv3", "L")
os.makedirs(OUT, exist_ok=True)

REGIONS = ["na", "emea", "latam", "apac"]
REGION_LABEL = {"na": "North America", "emea": "EMEA", "latam": "Latin America", "apac": "Asia Pacific"}
I1_REGION = {"north_america": "na", "emea": "emea", "latam": "latam", "apac": "apac"}
RNG = np.random.default_rng(20260911)

PROXY_COVER = {"na": ["cpi_lodging_sa", "cpi_lodging_nsa", "cpi_hotels_motels_nsa", "bea_hotels_price"],
               "emea": ["hicp_ea_accommodation", "ine_iph_spain"],
               "latam": [], "apac": []}
PROXY_TEST_ONLY = {"na": ["mar_revpar", "hlt_revpar"], "emea": [], "latam": [], "apac": []}
PROXY_KNOWABLE = {"cpi_lodging_sa": "yes: BLS, September value publishes before 5 Nov",
                  "cpi_lodging_nsa": "yes: BLS, September value publishes before 5 Nov",
                  "cpi_hotels_motels_nsa": "yes: BLS, September value publishes before 5 Nov",
                  "bea_hotels_price": "yes: BEA, September value publishes before 5 Nov",
                  "hicp_ea_accommodation": "yes: Eurostat, September flash before 5 Nov",
                  "ine_iph_spain": "yes: INE, September value publishes before 5 Nov",
                  "mar_revpar": "yes (reports 1-8 days before ABNB) but not held today; excluded from the pool",
                  "hlt_revpar": "yes (reports 1-8 days before ABNB) but not held today; excluded from the pool"}
FORMS = [("level", 0), ("level", 1), ("diff", 0), ("diff", 1)]
OWN_RULES = ["last_q", "persistence", "trailing_4q", "ar1", "last_q_ex_size"]
MIN_TRAIN = 4        # training quarters for an OLS proxy fit and for the AR(1) rule (S benchmark convention)
MIN_SELECT = 4       # out-of-sample quarters a candidate needs before t to be eligible for selection
FIRST_SCORED, LAST_SCORED = "1Q24", "2Q26"
FIRST_OOS = "1Q23"   # earliest quarter at which any candidate is asked for a prediction
NOWCAST_QUARTERS = ["3Q26", "4Q26"]

KNOWABLE_L = ("partly: regional ex-FX through t-1 is known at the prior print; proxies are knowable before "
              "the print; the geo term is I's measured in-quarter split (upper bound, as S's measured mix)")


def qprev(q: str, k: int = 1) -> str:
    return QORDER[QI[q] - k]


def cand_name(proxy: str, transform: str, lag: int) -> str:
    return f"{proxy}|{transform}|lag{lag}"


def candidates_for(region: str, pool_only: bool = True) -> list[str]:
    """Candidate order: own rules first, then proxies in PROXY_COVER order and FORMS order."""
    out = list(OWN_RULES)
    prox = list(PROXY_COVER[region]) + ([] if pool_only else list(PROXY_TEST_ONLY[region]))
    for p in prox:
        for tr, lag in FORMS:
            out.append(cand_name(p, tr, lag))
    return out


# ----------------------------------------------------------------------------------
# inputs
# ----------------------------------------------------------------------------------
def _basis_class(s) -> str:
    if not isinstance(s, str):
        return "not available"
    if s.startswith("disclosed"):
        return "disclosed"
    if s.startswith("derived (disclosed"):
        return "solved"
    return "modelled"


def load_regional() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Long regional panel (quarter x region) and the 04 wide frame indexed by quarter."""
    adr = os.path.join(ROOT, "data", "processed", "adr")
    wide = pd.read_csv(os.path.join(adr, "04_regional_quarterly_wide.csv")).set_index("quarter")
    wide = wide.loc[sorted(wide.index, key=lambda q: QI[q])]
    long = pd.read_csv(os.path.join(adr, "04_regional_quarterly.csv"))
    bas = long[long.metric == "adr_yoy_exfx_pct"].pivot(index="quarter", columns="region", values="basis")
    rep_bas = long[long.metric == "adr_yoy_reported_pct"].pivot(index="quarter", columns="region", values="basis")
    size = load_size_terms()
    rows = []
    for q in wide.index:
        for r in REGIONS:
            raw = bas.at[q, r] if (q in bas.index and r in bas.columns) else np.nan
            cls = _basis_class(raw)
            rows.append({"quarter": q, "region": r,
                         "exfx_pp": wide.at[q, f"adr_yoy_exfx_{r}_pct"],
                         "reported_yoy_pp": wide.at[q, f"adr_yoy_{r}_pct"],
                         "fx_pp": wide.at[q, f"fx_pp_{r}"],
                         "nights_share_pct": wide.at[q, f"nights_share_{r}_pct"],
                         "adr_anchored_usd": wide.at[q, f"adr_{r}_usd_anchored"],
                         "adr_usd": wide.at[q, f"adr_{r}_usd"],
                         "exfx_basis": cls,
                         "exfx_basis_raw": raw,
                         "reported_basis_raw": rep_bas.at[q, r] if (q in rep_bas.index and r in rep_bas.columns) else np.nan,
                         "basis_flag_04": wide.at[q, f"basis_adr_{r}"],
                         "usable": cls in ("disclosed", "solved") and pd.notna(wide.at[q, f"adr_yoy_exfx_{r}_pct"]),
                         "size_term_pp": size.get((q, r), np.nan)})
    panel = pd.DataFrame(rows)
    return panel, wide


def load_size_terms() -> dict:
    """Workstream I's regional unit-size term (size_term_pp, pp of ADR) by (quarter, region)."""
    f = os.path.join(ROOT, "data", "processed", "adrq3", "I", "I1_party_size_quarterly.csv")
    d = pd.read_csv(f)
    out = {}
    for _, r in d.iterrows():
        reg = I1_REGION.get(r.region)
        if reg is None or pd.isna(r.size_term_pp):
            continue
        out[(S.b_to_h_quarter(r.q), reg)] = float(r.size_term_pp)
    return out


def load_proxies() -> tuple[pd.DataFrame, pd.DataFrame]:
    """J2's quarterly proxy panel (y/y percent, quarter index) and the 3Q26 readings."""
    jdir = os.path.join(ROOT, "data", "processed", "adrq3", "J")
    panel = pd.read_csv(os.path.join(jdir, "J2_proxy_quarterly_panel.csv")).set_index("quarter")
    panel = panel.loc[sorted(panel.index, key=lambda q: QI[q])].astype(float)
    readings = pd.read_csv(os.path.join(jdir, "J2_proxy_readings_3q26.csv"))
    return panel, readings


def proxy_series_with_readings(panel: pd.DataFrame, readings: pd.DataFrame, hold_for_4q26: bool = True) -> pd.DataFrame:
    """Proxy panel extended by the 3Q26 quarter-to-date reading, and (assumed) the same reading held
    for 4Q26 so a lag-0 form can produce a 4Q26 number. The hold is an assumption and is flagged
    in L4."""
    ext = panel.copy()
    r3 = readings[(readings.quarter == "3Q26") & readings.proxy.isin(panel.columns)].set_index("proxy")["reading_yoy_pct"]
    for q in NOWCAST_QUARTERS:
        if q not in ext.index:
            ext.loc[q] = np.nan
    for p, v in r3.items():
        if pd.notna(v):
            ext.at["3Q26", p] = float(v)
            if hold_for_4q26:
                ext.at["4Q26", p] = float(v)
    return ext.loc[sorted(ext.index, key=lambda q: QI[q])]


# ----------------------------------------------------------------------------------
# the identity: within-region ex-FX, geo mix, reconstructed blended
# ----------------------------------------------------------------------------------
def aggregate_within(g: dict, s0: dict, a0: dict) -> float:
    """H's within-region ex-FX in pp: sum(s0 A0 (1+g/100)) / sum(s0 A0) - 1, over REGIONS."""
    base = sum(s0[r] * a0[r] for r in REGIONS)
    return 100.0 * (sum(s0[r] * a0[r] * (1.0 + g[r] / 100.0) for r in REGIONS) / base - 1.0)


def aggregate_total(g: dict, s0: dict, s1: dict, a0: dict) -> float:
    """H's reconstructed blended ex-FX in pp: sum(s1 A0 (1+g/100)) / sum(s0 A0) - 1."""
    return 100.0 * (sum(s1[r] * a0[r] * (1.0 + g[r] / 100.0) for r in REGIONS) / sum(s0[r] * a0[r] for r in REGIONS) - 1.0)


def weights_for(wide: pd.DataFrame, t: str) -> tuple[dict, dict, dict]:
    """Year-ago nights shares s0, current shares s1 (NaN if t not in the panel) and year-ago anchored ADR a0."""
    p = qprev(t, 4)
    s0 = {r: float(wide.at[p, f"nights_share_{r}_pct"]) for r in REGIONS}
    a0 = {r: float(wide.at[p, f"adr_{r}_usd_anchored"]) for r in REGIONS}
    s1 = {r: (float(wide.at[t, f"nights_share_{r}_pct"]) if t in wide.index else np.nan) for r in REGIONS}
    return s0, s1, a0


def dollar_weights(wide: pd.DataFrame, t: str) -> dict:
    s0, _, a0 = weights_for(wide, t)
    base = sum(s0[r] * a0[r] for r in REGIONS)
    return {r: s0[r] * a0[r] / base for r in REGIONS}


# ----------------------------------------------------------------------------------
# candidate predictions, strictly out of sample
# ----------------------------------------------------------------------------------
class RegionData:
    """One region's series: ex-FX y (all quarters), usable mask, size term, proxy panel."""

    def __init__(self, region: str, panel: pd.DataFrame, proxies: pd.DataFrame):
        self.region = region
        d = panel[panel.region == region].set_index("quarter")
        self.y = d["exfx_pp"].astype(float)
        self.usable = d["usable"].astype(bool)
        self.size = d["size_term_pp"].astype(float)
        self.proxies = proxies
        self.quarters = list(d.index)

    def prior_usable(self, t: str) -> pd.Series:
        idx = [q for q in self.quarters if QI[q] < QI[t] and self.usable[q]]
        return self.y[idx]

    def prior_any(self, t: str) -> pd.Series:
        idx = [q for q in self.quarters if QI[q] < QI[t] and pd.notna(self.y[q])]
        return self.y[idx]

    def proxy_x(self, proxy: str, transform: str, lag: int) -> pd.Series:
        x = self.proxies[proxy].astype(float)
        if transform == "diff":
            x = x.diff()
        return x.shift(lag)


def predict(rd: RegionData, cand: str, t: str, extra_y: pd.Series | None = None) -> tuple[float, str]:
    """Prediction of region rd's ex-FX at quarter t by candidate `cand`, using regional ex-FX strictly
    before t (usable quarters for fits; own rules fall back to the latest value of any basis when no
    usable prior exists, flagged) and, for lag-0 proxy forms, the proxy value at t.
    `extra_y` extends the ex-FX history with forecast values (used for 4Q26, where 3Q26 is unknown:
    own rules chain on the 3Q26 forecast, flagged). Returns (value, basis_note)."""
    yu = rd.prior_usable(t)
    if extra_y is not None and len(extra_y):
        ext = extra_y[[q for q in extra_y.index if QI[q] < QI[t]]]
        yu = pd.concat([yu, ext]).astype(float)
        yu = yu[~yu.index.duplicated(keep="last")]
        yu = yu.loc[sorted(yu.index, key=lambda q: QI[q])]
    note = "usable history"
    if cand in ("last_q", "persistence", "trailing_4q"):
        if len(yu) == 0:
            ya = rd.prior_any(t)
            if len(ya) == 0:
                return np.nan, "no history"
            yu, note = ya, "fallback: latest value of any basis (modelled)"
        v = yu.values
        if cand == "last_q":
            return float(v[-1]), note
        if cand == "persistence":
            return (float(v[-2:].mean()), note) if len(v) >= 2 else (np.nan, "needs two quarters")
        return (float(v[-4:].mean()), note) if len(v) >= 4 else (np.nan, "needs four quarters")
    if cand == "ar1":
        v = yu.values
        if len(v) < MIN_TRAIN:
            return np.nan, "needs four training quarters"
        b1, b0 = np.polyfit(v[:-1], v[1:], 1)
        return float(b0 + b1 * v[-1]), note
    if cand == "last_q_ex_size":
        if len(yu) == 0:
            return np.nan, "no usable history"
        p = yu.index[-1]
        st, sp = rd.size.get(t, np.nan), rd.size.get(p, np.nan)
        if extra_y is not None and p in extra_y.index:
            sp = rd.size.get(p, np.nan)
        if pd.isna(st) or pd.isna(sp):
            return np.nan, "regional size term missing"
        return float(yu.values[-1] - sp + st), note + "; size term from I1 (regional)"
    # proxy OLS
    proxy, transform, lag = cand.split("|")
    lag = int(lag[3:])
    x = rd.proxy_x(proxy, transform, lag)
    if t not in x.index or pd.isna(x.get(t, np.nan)):
        return np.nan, "proxy value at t missing"
    train = [q for q in yu.index if q in x.index and pd.notna(x[q])]
    if len(train) < MIN_TRAIN:
        return np.nan, "fewer than four training quarters"
    b1, b0 = np.polyfit(x[train].values, yu[train].values, 1)
    return float(b0 + b1 * x[t]), f"OLS on {len(train)} usable quarters"


def oos_table(rd: RegionData, cands: list[str], first: str = FIRST_OOS, last: str = LAST_SCORED) -> pd.DataFrame:
    """Out-of-sample predictions for every candidate at every quarter first..last (each built on data
    strictly before that quarter). Index quarter, columns candidates, plus actual and usable."""
    qs = [q for q in S.quarters_between(first, last) if q in rd.quarters]
    out = pd.DataFrame(index=qs, columns=cands, dtype=float)
    for t in qs:
        for c in cands:
            out.at[t, c] = predict(rd, c, t)[0]
    out["actual"] = rd.y.reindex(qs)
    out["usable"] = rd.usable.reindex(qs).fillna(False).astype(bool)
    return out


def select(oos: pd.DataFrame, cands: list[str], t: str, min_select: int = MIN_SELECT) -> dict:
    """Walk-forward pick at t from the OOS record on usable quarters strictly before t."""
    prior = [q for q in oos.index if QI[q] < QI[t] and bool(oos.at[q, "usable"])]
    best, best_rmse, table = None, np.inf, {}
    for c in cands:
        e = (oos.loc[prior, c] - oos.loc[prior, "actual"]).dropna()
        n = len(e)
        rmse = float(np.sqrt((e ** 2).mean())) if n else np.nan
        table[c] = (n, rmse)
        if n >= min_select and rmse < best_rmse - 1e-12:
            best, best_rmse = c, rmse
    if best is None:
        return {"pick": "last_q", "pick_rmse_prior": table.get("last_q", (0, np.nan))[1],
                "n_eligible": 0, "n_oos_prior": table.get("last_q", (0, np.nan))[0],
                "selection_basis": "default: no candidate has four out-of-sample quarters before t", "table": table}
    n_el = sum(1 for c in cands if table[c][0] >= min_select)
    return {"pick": best, "pick_rmse_prior": best_rmse, "n_eligible": n_el, "n_oos_prior": table[best][0],
            "selection_basis": f"lowest OOS RMSE over {table[best][0]} usable quarters before t among {n_el} eligible", "table": table}


def rmse(e) -> float:
    e = pd.Series(e, dtype=float).dropna()
    return float(np.sqrt((e ** 2).mean())) if len(e) else np.nan


def perm_p(x, y, n: int = 1000) -> float:
    """J2's 1,000-shuffle permutation p on |Pearson r|."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    r0 = abs(np.corrcoef(x, y)[0, 1])
    cnt = 0
    for _ in range(n):
        if abs(np.corrcoef(RNG.permutation(x), y)[0, 1]) >= r0:
            cnt += 1
    return (cnt + 1) / (n + 1)


def corr_stats(x: pd.Series, y: pd.Series) -> dict:
    d = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(d) < 6:
        return {"n": len(d), "pearson_r": np.nan, "p": np.nan, "spearman_r": np.nan, "perm_p": np.nan}
    r, p = stats.pearsonr(d.x, d.y)
    return {"n": int(len(d)), "first_q": d.index[0], "last_q": d.index[-1], "pearson_r": float(r), "p": float(p),
            "spearman_r": float(stats.spearmanr(d.x, d.y).correlation), "perm_p": perm_p(d.x.values, d.y.values)}
