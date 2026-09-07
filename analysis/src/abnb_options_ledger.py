"""Weekly options ledger for ABNB vs travel peers, with an identified event-variance estimator.

REWRITTEN 2026-09-06 to close audit finding A08 (see docs/2026-09-06_audit_findings_ai_handoff.md
section 10 and research/notes/overnight/23_options-estimator-fix.md).

What the previous version did wrong
-----------------------------------
It computed  var_event = sigma_near^2 * T_near - sigma_far^2 * T_near, floored it at zero and
multiplied sqrt(.) by 0.8.  Under a background variance b plus one event variance E,
sigma_near^2 = b + E/T_near and sigma_far^2 = b + E/T_far, so that expression equals
E * (1 - T_near/T_far)  --  NOT E.  Both expiries contained the same earnings event, so the far
expiry was not an event-free baseline.  Expiry choice was "nearest to a hard-coded target date",
which for EXPE/HLT selected an expiry BEFORE the intended print, and the ATM "straddle" summed a
nearest-strike call and a nearest-strike put that need not share a strike.

What this version does
----------------------
1. Every ticker carries an explicit event specification: an earliest and latest plausible release
   timestamp, a confidence label, and the sources.  No event timestamp -> no event estimate.
2. Expiry eligibility is decided against that window, not against a target date:
     post_event  iff  expiry settlement (16:00 ET on the expiry date) is strictly after the LATEST
                      plausible release timestamp;
     pre_event   iff  settlement is strictly before the EARLIEST plausible release timestamp;
     ambiguous   otherwise (never used for identification).
   If no post_event expiry is listed, the event estimate is reported unavailable and only raw
   measures are published.
3. Explicit total-variance model, fitted by least squares over eligible maturities:
        sigma_i^2 * T_i  =  b * T_i  +  E * d_i           d_i = 1 if expiry i is post-event
   b = annualised background (diffusive) variance, assumed constant across the maturities used.
   E = event variance, in variance-of-log-return units, assumed to be a single point jump.
   Identification needs rank 2: either >= 2 post-event maturities, or >= 1 pre-event and
   >= 1 post-event maturity.  One post-event maturity alone is NOT identified.
4. Raw measures (ATM IV, ATM straddle % of spot) are kept and labelled as TOTAL implied move to
   expiry -- they are not event-specific and are never presented as an event move.
5. A "straddle" is only called a straddle when the call and the put share a strike; bid, ask, mid,
   strike, observation timestamp, spreads, open interest, volume and quote age are all stored, with
   a quote_quality flag.
6. E <= 0 is reported as `non_positive_event_variance`, NOT as "no earnings premium".  A negative
   fit means the observed term structure has no event kink at these quotes, which at 60+ days out
   is usually thin/stale quotes or a changing background, not a market view that the print is a
   non-event.

Reads   : live yfinance option chains; optionally the legacy 5 Sep 2026 ledger in the main tree.
Writes  : data/processed/abnb_options_ledger.csv          (one row per ticker/expiry, schema v2)
          data/processed/overnight/23_options_event_estimates.csv (one row per ticker/specification)
Run     : py -3.13 analysis/src/abnb_options_ledger.py
          py -3.13 analysis/src/abnb_options_ledger.py --tickers ABNB
          py -3.13 analysis/src/abnb_options_ledger.py --no-write     (print only)

Caveat: implied volatilities are Yahoo's own, computed from Yahoo's mid quotes with Yahoo's rate
and dividend assumptions.  Treat single-snapshot IVs on 60-day strikes as indicative.
"""
from __future__ import annotations

import argparse
import datetime as dt
import math
import warnings
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

SCHEMA_VERSION = 2
ROOT = Path(__file__).resolve().parents[2]
PROC = ROOT / "data" / "processed"
OUT_OVERNIGHT = PROC / "overnight"
LEDGER_PATH = PROC / "abnb_options_ledger.csv"
EVENT_PATH = OUT_OVERNIGHT / "23_options_event_estimates.csv"

ET = "America/New_York"
SETTLE_HOUR_ET = 16  # US equity options settle on the 16:00 ET close of the expiry date
DAYS_PER_YEAR = 365.0
RATE = 0.04  # only used for 25-delta bucketing, not for any headline number


# --------------------------------------------------------------------------- event specifications
@dataclass
class EventSpec:
    """An earnings release with an explicit uncertainty window and a confidence label.

    confidence tiers (only the first two are allowed to produce an event estimate):
      company_confirmed        - the issuer has published the date/time itself
      third_party_estimate     - a data vendor publishes a specific date; window widened
      pattern_estimate         - inferred from the historical reporting pattern only
      unknown                  - no usable timestamp
    """
    ticker: str
    date_early: str | None          # earliest plausible release date (inclusive)
    date_late: str | None           # latest plausible release date (inclusive)
    release_time_et: str            # "after_close" or "before_open"
    confidence: str
    sources: str
    label: str = ""

    ALLOWED_FOR_ESTIMATE = ("company_confirmed", "third_party_estimate")

    @property
    def usable(self) -> bool:
        return (self.date_early is not None and self.date_late is not None
                and self.confidence in self.ALLOWED_FOR_ESTIMATE)

    def _ts(self, d: str) -> pd.Timestamp:
        hh = 16 if self.release_time_et == "after_close" else 7
        mm = 5 if self.release_time_et == "after_close" else 0
        return pd.Timestamp(f"{d} {hh:02d}:{mm:02d}", tz=ET)

    @property
    def ts_early(self) -> pd.Timestamp:
        return self._ts(self.date_early)

    @property
    def ts_late(self) -> pd.Timestamp:
        return self._ts(self.date_late)


# As of 6 Sep 2026 NO travel issuer in this set has published a Q3 2026 date.  Everything below is
# an estimate and is labelled as one.  Windows are set wide enough to cover the disagreement
# between vendors; every window still sits strictly between the 23 Oct and 20 Nov expiries, so
# expiry eligibility is robust to the date uncertainty (this is checked, not assumed).
EVENTS: dict[str, EventSpec] = {
    "ABNB": EventSpec(
        "ABNB", "2026-11-04", "2026-11-12", "after_close", "third_party_estimate",
        "Yahoo Finance earnings calendar 6 Sep 2026 = 2026-11-05 (single date, not a range); "
        "repo-wide working assumption 5 Nov 2026 (docs/overnight/00_BRIEF.md); historical Q3 "
        "prints 6 Nov 2025, 7 Nov 2024, 1 Nov 2023. Airbnb IR had NOT posted the date as of "
        "6 Sep 2026 (16_news_since_5sep.csv).",
        "Q3 2026"),
    "BKNG": EventSpec(
        "BKNG", "2026-10-26", "2026-11-05", "after_close", "third_party_estimate",
        "Yahoo calendar 6 Sep 2026 = 2026-10-27; TipRanks (estimated) = 2026-11-04 "
        "(16_news_since_5sep.csv line 15). Vendors disagree by 8 days; window covers both.",
        "Q3 2026"),
    "MAR": EventSpec(
        "MAR", "2026-10-27", "2026-11-04", "after_close", "third_party_estimate",
        "Yahoo calendar 6 Sep 2026 = 2026-11-03; TipRanks (estimated) = 2026-10-29 "
        "(16_news_since_5sep.csv line 16). MAR normally releases before the open; treated as "
        "after_close only to make eligibility conservative.",
        "Q3 2026"),
    "HLT": EventSpec(
        "HLT", "2026-10-26", "2026-11-04", "after_close", "third_party_estimate",
        "Yahoo calendar 6 Sep 2026 = 2026-10-28; WS16 pattern read 'last week of October' "
        "(16_news_since_5sep.csv line 17). Company had not confirmed as of 6 Sep 2026.",
        "Q3 2026"),
    "EXPE": EventSpec(
        "EXPE", "2026-11-02", "2026-11-12", "after_close", "third_party_estimate",
        "Yahoo calendar 6 Sep 2026 = 2026-11-05; WS16 pattern read 'first week of November' "
        "(16_news_since_5sep.csv line 17). Company had not confirmed as of 6 Sep 2026.",
        "Q3 2026"),
    # No usable Q3 2026 timestamp for these: raw measures only, no event estimate.
    "TRIP": EventSpec("TRIP", None, None, "after_close", "unknown", "no vendor date located 6 Sep 2026", "Q3 2026"),
    "H": EventSpec("H", None, None, "after_close", "unknown", "no vendor date located 6 Sep 2026", "Q3 2026"),
    "JETS": EventSpec("JETS", None, None, "after_close", "unknown", "ETF, no issuer earnings event", "n/a"),
}

DEFAULT_TICKERS = ["ABNB", "BKNG", "EXPE", "MAR", "HLT", "TRIP", "H", "JETS"]


# --------------------------------------------------------------------------- expiry eligibility
def settle_ts(expiry: str) -> pd.Timestamp:
    return pd.Timestamp(f"{expiry} {SETTLE_HOUR_ET:02d}:00", tz=ET)


def classify_expiry(expiry: str, spec: EventSpec) -> str:
    """pre_event / post_event / ambiguous / no_event_timestamp.

    STRICT: post_event requires settlement strictly after the LATEST plausible release; pre_event
    requires settlement strictly before the EARLIEST plausible release.  An expiry that could fall
    on either side of the release is 'ambiguous' and is never used for identification.
    """
    if not spec.usable:
        return "no_event_timestamp"
    s = settle_ts(expiry)
    if s > spec.ts_late:
        return "post_event"
    if s < spec.ts_early:
        return "pre_event"
    return "ambiguous"


# --------------------------------------------------------------------------- variance model
@dataclass
class VarianceFit:
    status: str                 # ok | unavailable_* | (ok with non_positive flag)
    detail: str = ""
    b_var: float = float("nan")             # annualised background variance
    event_var: float = float("nan")         # E, variance of the event log-return
    background_vol_pct: float = float("nan")
    event_sd_pct: float = float("nan")
    event_exp_abs_move_pct: float = float("nan")
    n_maturities: int = 0
    n_post: int = 0
    n_pre: int = 0
    method: str = ""
    resid_rmse_var: float = float("nan")
    cond_number: float = float("nan")
    loo_event_sd_min_pct: float = float("nan")
    loo_event_sd_max_pct: float = float("nan")
    maturities: list = field(default_factory=list)


def fit_variance_model(obs: list[dict], method_label: str = "ols",
                       _loo: bool = False) -> VarianceFit:
    """Fit sigma_i^2 * T_i = b * T_i + E * d_i.

    obs: [{'T': years, 'iv': decimal annualised vol, 'event_class': 'pre_event'|'post_event', ...}]
    Only pre_event and post_event observations are used.  Returns a VarianceFit whose `status` is
    'ok' when E is identified (E may still be <= 0, flagged via `detail`).

    Assumptions, stated because they are load-bearing:
      A1  a single background variance rate b applies across every maturity used;
      A2  exactly one discrete event sits inside every post-event expiry and none inside the
          pre-event expiries (no other scheduled catalyst differentiates the maturities);
      A3  the ATM IV of each expiry is a usable proxy for that expiry's total variance
          (ignores skew/convexity, i.e. no variance-swap replication);
      A4  quotes across maturities are contemporaneous.
    """
    use = [o for o in obs if o.get("event_class") in ("pre_event", "post_event")]
    n_post = sum(1 for o in use if o["event_class"] == "post_event")
    n_pre = len(use) - n_post
    base = dict(n_maturities=len(use), n_post=n_post, n_pre=n_pre, method=method_label,
                maturities=[(o.get("expiry"), o["event_class"], round(o["T"], 5),
                             round(o["iv"], 6)) for o in use])

    if n_post == 0:
        return VarianceFit(status="unavailable_no_post_event_expiry",
                           detail="no listed expiry strictly follows the latest plausible release "
                                  "timestamp; event estimate unavailable", **base)
    if len(use) < 2:
        return VarianceFit(status="unavailable_insufficient_maturities",
                           detail="need >= 2 post-event maturities, or >= 1 pre-event and >= 1 "
                                  "post-event maturity", **base)
    if n_post < 2 and n_pre < 1:
        return VarianceFit(status="unavailable_insufficient_maturities",
                           detail="one post-event maturity and no pre-event maturity: b and E are "
                                  "not separately identified", **base)

    T = np.array([o["T"] for o in use], dtype=float)
    d = np.array([1.0 if o["event_class"] == "post_event" else 0.0 for o in use])
    y = np.array([o["iv"] ** 2 * o["T"] for o in use], dtype=float)
    A = np.column_stack([T, d])
    if np.linalg.matrix_rank(A) < 2:
        return VarianceFit(status="unavailable_rank_deficient",
                           detail="design matrix [T, post_event] is rank deficient (maturities are "
                                  "not distinct enough to separate b from E)", **base)

    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    b, E = float(coef[0]), float(coef[1])
    resid = y - A @ coef
    rmse = float(np.sqrt(np.mean(resid ** 2))) if len(use) > 2 else 0.0
    cond = float(np.linalg.cond(A))

    # leave-one-out spread when over-identified
    loo_lo = loo_hi = float("nan")
    if len(use) >= 3 and not _loo:
        vals = []
        for i in range(len(use)):
            sub = [o for j, o in enumerate(use) if j != i]
            f = fit_variance_model(sub, method_label="loo", _loo=True)
            if f.status == "ok" and f.event_var > 0:
                vals.append(math.sqrt(f.event_var) * 100)
        if vals:
            loo_lo, loo_hi = float(min(vals)), float(max(vals))

    fit = VarianceFit(status="ok", b_var=b, event_var=E,
                      background_vol_pct=math.sqrt(b) * 100 if b > 0 else float("nan"),
                      event_sd_pct=math.sqrt(E) * 100 if E > 0 else float("nan"),
                      event_exp_abs_move_pct=(math.sqrt(E) * math.sqrt(2 / math.pi) * 100
                                              if E > 0 else float("nan")),
                      resid_rmse_var=rmse, cond_number=cond,
                      loo_event_sd_min_pct=loo_lo, loo_event_sd_max_pct=loo_hi, **base)
    if E <= 0:
        fit.detail = ("non_positive_event_variance: the fitted term structure shows no event kink "
                      "at these quotes. This is NOT evidence that the market prices no earnings "
                      "premium; at this maturity it is normally thin/stale quotes or a background "
                      "variance that is not constant across the maturities used.")
    elif b <= 0:
        fit.detail = "fitted background variance is non-positive; treat E as unreliable"
    else:
        fit.detail = "identified"
    return fit


# --------------------------------------------------------------------------- chain snapshot
def _norm_side(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    for c in ("bid", "ask", "lastPrice", "impliedVolatility", "openInterest", "volume"):
        if c not in d.columns:
            d[c] = np.nan
    d["mid"] = (d["bid"] + d["ask"]) / 2.0
    d["rel_spread"] = (d["ask"] - d["bid"]) / d["mid"].replace(0, np.nan)
    return d


def bs_delta(S, K, T, sigma, call, r=RATE):
    from statistics import NormalDist
    if T <= 0 or sigma is None or not np.isfinite(sigma) or sigma <= 0:
        return np.nan
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    n = NormalDist().cdf(d1)
    return n if call else n - 1


def snapshot_expiry(tk, ticker: str, expiry: str, spot: float, asof: pd.Timestamp,
                    spec: EventSpec) -> dict | None:
    """One ledger row.  Returns None only if the chain cannot be fetched at all."""
    import yfinance as yf  # noqa: F401  (import kept local so the module imports without network)
    ch = tk.option_chain(expiry)
    c = _norm_side(ch.calls)
    p = _norm_side(ch.puts)

    T = max((settle_ts(expiry) - asof).total_seconds(), 0) / (86400.0 * DAYS_PER_YEAR)
    dte = int(round(T * DAYS_PER_YEAR))
    cls = classify_expiry(expiry, spec)

    row = dict(schema_version=SCHEMA_VERSION,
               run_datetime_utc=pd.Timestamp.utcnow().tz_localize(None).isoformat(timespec="seconds"),
               run_date=asof.tz_convert("UTC").date().isoformat(),
               ticker=ticker, spot=round(spot, 4), spot_source="yfinance fast_info.last_price",
               expiry=expiry, expiry_settle_et=settle_ts(expiry).isoformat(),
               dte_cal=dte, T_years=round(T, 6),
               event_label=spec.label, event_date_early=spec.date_early,
               event_date_late=spec.date_late, event_release_time_et=spec.release_time_et,
               event_confidence=spec.confidence, expiry_event_class=cls,
               n_calls_quoted=0, n_puts_quoted=0)

    # --- two-sided quotes only for anything used numerically
    cq = c[(c["bid"] > 0) & (c["ask"] > 0) & (c["ask"] >= c["bid"])]
    pq = p[(p["bid"] > 0) & (p["ask"] > 0) & (p["ask"] >= p["bid"])]
    row["n_calls_quoted"] = int(len(cq))
    row["n_puts_quoted"] = int(len(pq))

    # --- straddle: MUST be the same strike on both sides
    common = sorted(set(cq["strike"]).intersection(set(pq["strike"])))
    flags = []
    if not common:
        row["straddle_verified"] = False
        row["straddle_reject_reason"] = "no strike has two-sided quotes on both call and put"
        flags.append("no_common_strike")
    else:
        k = min(common, key=lambda x: abs(x - spot))
        cr = cq[cq["strike"] == k].iloc[0]
        pr = pq[pq["strike"] == k].iloc[0]
        row.update(straddle_verified=True, straddle_reject_reason="",
                   straddle_strike=float(k),
                   straddle_moneyness_pct=round((k / spot - 1) * 100, 3),
                   call_bid=float(cr["bid"]), call_ask=float(cr["ask"]), call_mid=float(cr["mid"]),
                   put_bid=float(pr["bid"]), put_ask=float(pr["ask"]), put_mid=float(pr["mid"]),
                   straddle_bid=float(cr["bid"] + pr["bid"]),
                   straddle_ask=float(cr["ask"] + pr["ask"]),
                   straddle_mid=float(cr["mid"] + pr["mid"]),
                   call_rel_spread=float(cr["rel_spread"]), put_rel_spread=float(pr["rel_spread"]),
                   call_oi=float(cr["openInterest"]) if pd.notna(cr["openInterest"]) else np.nan,
                   put_oi=float(pr["openInterest"]) if pd.notna(pr["openInterest"]) else np.nan,
                   call_volume=float(cr["volume"]) if pd.notna(cr["volume"]) else 0.0,
                   put_volume=float(pr["volume"]) if pd.notna(pr["volume"]) else 0.0,
                   raw_atm_iv_call_pct=round(float(cr["impliedVolatility"]) * 100, 4),
                   raw_atm_iv_put_pct=round(float(pr["impliedVolatility"]) * 100, 4))
        row["raw_atm_iv_pct"] = round((row["raw_atm_iv_call_pct"] + row["raw_atm_iv_put_pct"]) / 2, 4)
        # RAW, TOTAL-to-expiry measures. Not event measures.
        row["raw_straddle_mid_pct_spot"] = round(row["straddle_mid"] / spot * 100, 4)
        row["raw_straddle_bid_pct_spot"] = round(row["straddle_bid"] / spot * 100, 4)
        row["raw_straddle_ask_pct_spot"] = round(row["straddle_ask"] / spot * 100, 4)
        for side, r_ in (("call", cr), ("put", pr)):
            lt = r_.get("lastTradeDate")
            try:
                lt = pd.Timestamp(lt)
                if lt.tzinfo is None:
                    lt = lt.tz_localize("UTC")
                row[f"{side}_last_trade_utc"] = lt.tz_convert("UTC").isoformat(timespec="seconds")
                row[f"{side}_quote_age_hours"] = round(
                    (asof - lt).total_seconds() / 3600.0, 2)
            except Exception:
                row[f"{side}_last_trade_utc"] = ""
                row[f"{side}_quote_age_hours"] = np.nan
        # quote-quality flags
        age = np.nanmax([row.get("call_quote_age_hours", np.nan),
                         row.get("put_quote_age_hours", np.nan)])
        row["quote_age_hours_max"] = float(age) if np.isfinite(age) else np.nan
        if abs(row["straddle_moneyness_pct"]) > 2.5:
            flags.append("atm_strike_off_by_gt_2.5pct")
        if max(row["call_rel_spread"], row["put_rel_spread"]) > 0.25:
            flags.append("wide_spread_gt_25pct_of_mid")
        if np.isfinite(row["quote_age_hours_max"]) and row["quote_age_hours_max"] > 48:
            flags.append("stale_last_trade_gt_48h")
        if min(row.get("call_oi", 0) or 0, row.get("put_oi", 0) or 0) < 10:
            flags.append("thin_open_interest_lt_10")
        if min(len(cq), len(pq)) < 5:
            flags.append("few_two_sided_strikes_lt_5")

    row["qq_flags"] = ";".join(flags)
    row["quote_quality"] = ("unusable" if not row.get("straddle_verified") else
                            "good" if not flags else
                            "fair" if len(flags) <= 1 else "poor")

    # --- 25-delta skew (descriptive only)
    try:
        cq2 = cq.assign(delta=[bs_delta(spot, k, T, s, True)
                               for k, s in zip(cq["strike"], cq["impliedVolatility"])])
        pq2 = pq.assign(delta=[bs_delta(spot, k, T, s, False)
                               for k, s in zip(pq["strike"], pq["impliedVolatility"])])
        c25 = cq2.iloc[(cq2["delta"] - 0.25).abs().argsort()[:1]]
        p25 = pq2.iloc[(pq2["delta"] + 0.25).abs().argsort()[:1]]
        row.update(iv_call25_pct=round(float(c25["impliedVolatility"].iloc[0]) * 100, 2),
                   k_call25=float(c25["strike"].iloc[0]),
                   iv_put25_pct=round(float(p25["impliedVolatility"].iloc[0]) * 100, 2),
                   k_put25=float(p25["strike"].iloc[0]))
        row["skew25_pts"] = round(row["iv_put25_pct"] - row["iv_call25_pct"], 2)
    except Exception:
        pass
    try:
        row["put_call_oi"] = round(float(pq["openInterest"].sum() /
                                         max(cq["openInterest"].sum(), 1)), 3)
        row["put_call_vol"] = round(float(pq["volume"].fillna(0).sum() /
                                          max(cq["volume"].fillna(0).sum(), 1)), 3)
    except Exception:
        pass
    return row


# --------------------------------------------------------------------------- per-ticker driver
def eligible_obs(rows: list[dict]) -> list[dict]:
    """Rows usable for identification: verified straddle, usable IV, non-ambiguous class."""
    out = []
    for r in rows:
        if not r.get("straddle_verified"):
            continue
        iv = r.get("raw_atm_iv_pct")
        if iv is None or not np.isfinite(iv) or iv <= 1.0 or iv >= 300:
            continue
        if r["expiry_event_class"] not in ("pre_event", "post_event"):
            continue
        if r["quote_quality"] == "unusable":
            continue
        out.append(dict(expiry=r["expiry"], T=r["T_years"], iv=iv / 100.0,
                        event_class=r["expiry_event_class"],
                        quote_quality=r["quote_quality"]))
    return sorted(out, key=lambda o: o["T"])


def event_estimates_for(ticker: str, rows: list[dict], spec: EventSpec, asof) -> list[dict]:
    """Produce one record per identification specification, so the reader sees the spread."""
    obs = eligible_obs(rows)
    stamp = dict(run_datetime_utc=pd.Timestamp.utcnow().tz_localize(None).isoformat(timespec="seconds"),
                 run_date=pd.Timestamp(asof).tz_convert("UTC").date().isoformat(),
                 ticker=ticker, event_label=spec.label,
                 event_date_early=spec.date_early, event_date_late=spec.date_late,
                 event_confidence=spec.confidence, event_sources=spec.sources)

    if not spec.usable:
        return [dict(stamp, spec_name="all_eligible",
                     status="unavailable_no_event_timestamp",
                     detail=f"confidence='{spec.confidence}' is not sufficient to place the event "
                            "relative to an expiry; event estimate unavailable, raw measures only")]

    specs: list[tuple[str, list[dict]]] = [("all_eligible", obs)]
    pre = [o for o in obs if o["event_class"] == "pre_event"]
    post = [o for o in obs if o["event_class"] == "post_event"]
    if pre and post:
        specs.append(("pre_plus_first_post", [pre[-1], post[0]]))
    if len(post) >= 2:
        specs.append(("first_two_post", post[:2]))

    recs = []
    for name, sub in specs:
        f = fit_variance_model(sub, method_label="ols" if len(sub) > 2 else "exact")
        recs.append(dict(stamp, spec_name=name, status=f.status, detail=f.detail,
                         maturities_used="|".join(f"{m[0]}:{m[1]}" for m in f.maturities),
                         n_maturities=f.n_maturities, n_pre=f.n_pre, n_post=f.n_post,
                         background_var_ann=round(f.b_var, 8) if np.isfinite(f.b_var) else np.nan,
                         background_vol_pct=round(f.background_vol_pct, 3) if np.isfinite(f.background_vol_pct) else np.nan,
                         event_var=round(f.event_var, 8) if np.isfinite(f.event_var) else np.nan,
                         event_sd_pct=round(f.event_sd_pct, 3) if np.isfinite(f.event_sd_pct) else np.nan,
                         event_exp_abs_move_pct=round(f.event_exp_abs_move_pct, 3) if np.isfinite(f.event_exp_abs_move_pct) else np.nan,
                         event_var_sign="positive" if (np.isfinite(f.event_var) and f.event_var > 0)
                                        else ("non_positive" if np.isfinite(f.event_var) else ""),
                         resid_rmse_var=round(f.resid_rmse_var, 10) if np.isfinite(f.resid_rmse_var) else np.nan,
                         cond_number=round(f.cond_number, 2) if np.isfinite(f.cond_number) else np.nan,
                         loo_event_sd_min_pct=round(f.loo_event_sd_min_pct, 3) if np.isfinite(f.loo_event_sd_min_pct) else np.nan,
                         loo_event_sd_max_pct=round(f.loo_event_sd_max_pct, 3) if np.isfinite(f.loo_event_sd_max_pct) else np.nan,
                         model="sigma_i^2*T_i = b*T_i + E*d_i",
                         assumptions="A1 constant background variance across maturities used; "
                                     "A2 exactly one discrete event inside every post-event expiry "
                                     "and none inside pre-event expiries; A3 ATM IV proxies total "
                                     "expiry variance (no skew/variance-swap correction); "
                                     "A4 quotes contemporaneous across maturities"))
    return recs


def run(tickers: list[str], write: bool = True) -> tuple[pd.DataFrame, pd.DataFrame]:
    import yfinance as yf
    asof = pd.Timestamp.utcnow()
    if asof.tzinfo is None:
        asof = asof.tz_localize("UTC")
    ledger_rows, event_rows = [], []
    for tkr in tickers:
        spec = EVENTS.get(tkr, EventSpec(tkr, None, None, "after_close", "unknown", "no spec", ""))
        try:
            t = yf.Ticker(tkr)
            spot = float(t.fast_info["last_price"])
            exps = list(t.options)
        except Exception as exc:
            print(f"{tkr:5s} FETCH ERR {str(exc)[:100]}")
            continue
        if not exps:
            print(f"{tkr:5s} no listed options")
            continue
        # Keep every expiry out to ~5 months: the model needs the term structure, not two guesses.
        keep = [e for e in exps if (pd.Timestamp(e) - asof.tz_convert(ET).tz_localize(None)).days <= 160]
        rows = []
        for e in keep:
            try:
                r = snapshot_expiry(t, tkr, e, spot, asof, spec)
                if r:
                    rows.append(r)
            except Exception as exc:
                print(f"{tkr:5s} {e} chain err {str(exc)[:80]}")
        ledger_rows.extend(rows)
        ev = event_estimates_for(tkr, rows, spec, asof)
        event_rows.extend(ev)

        cls_counts = pd.Series([r["expiry_event_class"] for r in rows]).value_counts().to_dict()
        print(f"\n{tkr:5s} spot {spot:8.2f}  expiries {len(rows)}  classes {cls_counts}  "
              f"event_conf={spec.confidence}")
        for r in rows:
            if r.get("straddle_verified") and r["expiry_event_class"] != "ambiguous":
                print(f"      {r['expiry']} {r['expiry_event_class']:>10s} dte {r['dte_cal']:>3d} "
                      f"K {r.get('straddle_strike')} raw_iv {r.get('raw_atm_iv_pct')}% "
                      f"raw_straddle {r.get('raw_straddle_mid_pct_spot')}% of spot  "
                      f"[{r['quote_quality']}] {r['qq_flags']}")
        for e in ev:
            if e["status"] == "ok":
                print(f"      -> {e['spec_name']:22s} b_vol {e['background_vol_pct']}%  "
                      f"E_sd {e['event_sd_pct']}%  ({e['event_var_sign']})")
            else:
                print(f"      -> {e['spec_name']:22s} {e['status']}")

    led = pd.DataFrame(ledger_rows)
    evd = pd.DataFrame(event_rows)
    if write and len(led):
        LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
        if LEDGER_PATH.exists():
            # legacy rows are already carried inside the existing file; never re-import them
            old = pd.read_csv(LEDGER_PATH)
            old = old[~((old.get("run_date", pd.Series(dtype=str)).isin(led["run_date"].unique())) &
                        (old.get("schema_version", pd.Series(dtype=float)) == SCHEMA_VERSION))]
            led = pd.concat([old, led], ignore_index=True)
        else:
            led = merge_legacy(led)
        led.to_csv(LEDGER_PATH, index=False)
        OUT_OVERNIGHT.mkdir(parents=True, exist_ok=True)
        evd.to_csv(EVENT_PATH, index=False)
        print(f"\nwrote {LEDGER_PATH}  ({len(led)} rows)")
        print(f"wrote {EVENT_PATH}  ({len(evd)} rows)")
    return led, evd


def merge_legacy(new: pd.DataFrame) -> pd.DataFrame:
    """Carry the 5 Sep 2026 main-tree snapshot forward as schema_version=1 rows with the defective
    event estimate WITHDRAWN, so the weekly series is not lost but the bad number is not republished.
    """
    src = ROOT.parent / "citadel-abnb" / "data" / "processed" / "abnb_options_ledger.csv"
    if not src.exists():
        return new
    try:
        old = pd.read_csv(src)
    except Exception:
        return new
    if "event_implied_move_pct" not in old.columns:
        return new
    keep = old.rename(columns={"straddle_pct_spot": "raw_straddle_mid_pct_spot",
                               "atm_iv_pct": "raw_atm_iv_pct",
                               "dte": "dte_cal",
                               "n_calls": "n_calls_quoted",
                               "n_puts": "n_puts_quoted"}).drop(columns=["event_implied_move_pct"])
    keep["schema_version"] = 1
    keep["straddle_verified"] = False
    keep["straddle_reject_reason"] = ("legacy row: nearest-strike call and put were selected "
                                      "independently, same-strike not verified")
    keep["quote_quality"] = "legacy_unverified"
    keep["expiry_event_class"] = "legacy_not_classified"
    keep["event_confidence"] = "legacy_none"
    keep["qq_flags"] = "legacy_schema_v1;event_estimate_withdrawn_A08"
    return pd.concat([keep, new], ignore_index=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tickers", nargs="*", default=DEFAULT_TICKERS)
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args()
    run([t.upper() for t in a.tickers], write=not a.no_write)


if __name__ == "__main__":
    main()
