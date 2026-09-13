"""Rebuild A without using same-day inputs or substituting close-based returns."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "analysis/src/forecast_methods"))
from kernel_engine_v2 import engine as k0
from harness import REGISTRY_COLUMNS

OUT = ROOT / "data/processed/forecast_methods/alpha_a"
SEED = 20260912
AS_OF = "2026-09-12"


def quarter(value):
    value = str(value)
    if len(value) == 4 and value[1] == "Q":
        return f"20{value[2:]}Q{value[0]}"
    return str(pd.Period(value, freq="Q"))


def flag(series):
    return series.astype(str).str.lower().eq("true")


def consensus_candidates(frame, target, origin, *, role=None):
    """Return only documented, attributed, strictly earlier revenue observations."""
    cutoff = pd.Timestamp(origin).normalize()
    dates = pd.to_datetime(frame.as_of_timestamp, format="mixed", errors="coerce", utc=True).dt.tz_localize(None).dt.normalize()
    use = (frame.period.eq(target) & frame.metric.eq("revenue")
           & frame.unit.eq("musd") & flag(frame.pit_usable)
           & flag(frame.vendor_attributed) & frame.vendor.notna()
           & ~frame.vendor.astype(str).str.contains("unattributed|not_recorded", case=False)
           & frame.value.notna() & (frame.value > 0) & dates.lt(cutoff))
    if role is not None:
        use &= frame.role.eq(role)
    return frame.loc[use].assign(_date=dates[use]).sort_values(["_date", "register_id"])


def wilson(hits, n, confidence=.95):
    if not n:
        return None, None
    if not 0 <= hits <= n:
        raise ValueError("Hits must lie between zero and n")
    z = norm.ppf((1 + confidence) / 2)
    p = hits / n
    center = (p + z*z / (2*n)) / (1 + z*z/n)
    half = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1+z*z/n)
    return max(0., center-half), min(1., center+half)


def interval_sign(lo, hi):
    """A rounded interval straddling zero cannot receive a directional hit."""
    if not np.isfinite(lo) or not np.isfinite(hi):
        return np.nan
    if lo > hi:
        raise ValueError("Inverted interval")
    return 1 if lo > 0 else (-1 if hi < 0 else 0)


def ridge_slope(x, y, penalty=1.):
    """Unpenalized intercept; slope shrunk toward one, fixed penalty."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    dx, dy = x-x.mean(), y-y.mean()
    slope = (dx @ dy + penalty) / (dx @ dx + penalty)
    return float(y.mean()-slope*x.mean()), float(slope)


def block_ci(x, statistic=np.mean, *, draws=2000):
    x = np.asarray(x, float)
    if len(x) < 2:
        return None, None
    rng = np.random.default_rng(SEED)
    n = len(x)
    samples = []
    for _ in range(draws):
        starts = rng.integers(0, n-1, size=(n+1)//2)
        indices = np.concatenate([np.arange(i, i+2) for i in starts])[:n]
        samples.append(statistic(x[indices]))
    return tuple(float(v) for v in np.quantile(samples, [.025, .975]))


def executable_column(frame, days):
    # Only columns explicitly identifying executable open-entry returns qualify.
    for name in (f"open_excess_{days}d_pct", f"open_abnb_{days}d_pct", f"open_{days}d_pct"):
        if name in frame:
            return name
    return None


def statistics(frame):
    outputs = []
    for window, first in (("W1", "2023Q1"), ("W2", "2024Q1")):
        f = frame[frame.quarter.between(first, "2026Q2")].copy()
        s = pd.to_numeric(f.signal_pct, errors="coerce")
        signs = pd.to_numeric(f.actual_sign, errors="coerce")
        selected = f[s.abs().gt(1) & signs.isin([-1, 1])]
        n = len(selected)
        hits = int((np.sign(selected.signal_pct) == selected.actual_sign).sum())
        lo, hi = wilson(hits, n)
        ret = selected.dropna(subset=["open_20d_pct"])
        signed = (np.sign(ret.signal_pct) * ret.open_20d_pct).to_numpy(float)
        rlo, rhi = block_ci(signed)
        permutation_p = None
        if n:
            rng = np.random.default_rng(SEED)
            pred = np.sign(selected.signal_pct.to_numpy(float))
            actual = selected.actual_sign.to_numpy(float)
            exceed = sum((pred == rng.permutation(actual)).sum() >= hits for _ in range(9999))
            permutation_p = (1+exceed)/10000
        pairs = f.dropna(subset=["signal_pct", "actual_gap_pct"]).sort_values("guide_date")
        slope_lo = slope_hi = final_slope = None
        expanding_errors = []
        for i in range(6, len(pairs)):
            tr = pairs.iloc[:i]
            intercept, slope = ridge_slope(tr.signal_pct, tr.actual_gap_pct)
            expanding_errors.append(float(intercept+slope*pairs.iloc[i].signal_pct-pairs.iloc[i].actual_gap_pct))
        if len(pairs) >= 6:
            _, final_slope = ridge_slope(pairs.signal_pct, pairs.actual_gap_pct)
            xy = pairs[["signal_pct", "actual_gap_pct"]].to_numpy(float)
            slope_lo, slope_hi = block_ci(xy, lambda a: ridge_slope(a[:, 0], a[:, 1])[1])
        outputs.append(dict(window=window, n_dates=len(f), n_signal=int(s.notna().sum()),
                            n_consensus=int(f.consensus_musd.notna().sum()),
                            n_threshold=int(s.abs().gt(1).sum()), n_sign_scored=n,
                            hits=hits if n else None, hit_rate=hits/n if n else None,
                            wilson_lo=lo, wilson_hi=hi, permutation_p=permutation_p,
                            ridge_n_train=len(pairs), ridge_n_test=len(expanding_errors),
                            ridge_slope=final_slope, ridge_slope_ci_lo=slope_lo,
                            ridge_slope_ci_hi=slope_hi,
                            n_return=len(ret), signed_open_20d_mean=float(signed.mean()) if len(signed) else None,
                            signed_open_20d_ci_lo=rlo, signed_open_20d_ci_hi=rhi,
                            verdict="underpowered" if n < 6 else ("pass" if hits/n >= .7 and len(signed) and signed.mean() > 0 else "fail")))
    return pd.DataFrame(outputs)


def read_inputs():
    paths = ["data/processed/overnight/02_guidance_ledger.csv",
             "data/processed/forecast_methods/L0/L0_vintage_register.csv",
             "data/processed/abnb_earnings_reactions.csv"]
    frames = [pd.read_csv(ROOT / p, comment="#") for p in paths]
    hashes = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    return (*frames, hashes)


def build_history(guides, vintages, reactions):
    g = guides[guides.metric.eq("revenue_usd_m") & guides.value_mid.notna()].copy()
    g["quarter"] = g.target_period.map(quarter)
    g = g[g.quarter.le("2026Q2")].sort_values("print_date")
    rows, audits, diagnostic = [], [], []
    for row in g.itertuples():
        origin = pd.Timestamp(row.print_date)
        target = row.quarter
        prior_period = str(pd.Period(target, freq="Q")-1)
        r = dict(quarter=target, guide_date=str(origin.date()), extension=target < "2023Q1",
                 guide_mid_musd=float(row.value_mid), guide_mid_lo=float(row.value_mid)-.5,
                 guide_mid_hi=float(row.value_mid)+.5, consensus_musd=np.nan,
                 street_vendor="", street_as_of="", register_id="", kernel_guide_musd=np.nan,
                 signal_pct=np.nan, actual_gap_pct=np.nan, actual_gap_lo=np.nan,
                 actual_gap_hi=np.nan, actual_sign=np.nan, kernel_status="unavailable",
                 kernel_reason="", consensus_status="no_strictly_earlier_attributed_vintage")
        admitted = consensus_candidates(vintages, target, origin)
        if len(admitted):
            v = admitted.iloc[-1]
            r.update(consensus_musd=float(v.value), street_vendor=v.vendor,
                     street_as_of=v.as_of_timestamp, register_id=v.register_id, consensus_status="admitted")
        candidates = vintages[vintages.period.eq(target) & vintages.metric.eq("revenue") & vintages.role.eq("pre_guide")]
        for v in candidates.itertuples():
            stamp = pd.to_datetime(v.as_of_timestamp, errors="coerce")
            audits.append(dict(quarter=target, guide_date=str(origin.date()), register_id=v.register_id,
                               vendor=v.vendor, value_musd=v.value, as_of_timestamp=v.as_of_timestamp,
                               pit_usable=v.pit_usable, vendor_attributed=v.vendor_attributed,
                               admitted=v.register_id in set(admitted.register_id),
                               reason="missing_timestamp_or_quarantined" if pd.isna(stamp) or not v.pit_usable else
                                      ("same_date_not_strictly_before" if stamp.normalize() == origin else
                                       "unattributed_vendor" if not v.vendor_attributed else "later_than_origin")))
        try:
            forecast = k0.kernel_guide(target, origin)
            r.update(kernel_guide_musd=forecast["point"], kernel_status="available")
        except (k0.DataUnavailable, k0.PointInTimeError) as exc:
            r["kernel_reason"] = str(exc)
        if np.isfinite(r["consensus_musd"]):
            c = r["consensus_musd"]
            r.update(actual_gap_pct=100*(r["guide_mid_musd"]/c-1),
                     actual_gap_lo=100*(r["guide_mid_lo"]/c-1), actual_gap_hi=100*(r["guide_mid_hi"]/c-1))
            r["actual_sign"] = interval_sign(r["actual_gap_lo"], r["actual_gap_hi"])
            if np.isfinite(r["kernel_guide_musd"]):
                r["signal_pct"] = 100*(r["kernel_guide_musd"]/c-1)
        event = reactions[reactions.quarter.eq(prior_period)]
        for day in (1, 5, 20):
            col = executable_column(reactions, day)
            r[f"open_{day}d_pct"] = float(event.iloc[0][col]) if col and len(event) == 1 else np.nan
        rows.append(r)
        # Date d+1 admits the newly printed GBV but is after the target guide.
        # This arithmetic diagnostic is never included in the pass statistics.
        after = origin + pd.Timedelta(days=1)
        admitted_after = consensus_candidates(vintages, target, after, role="pre_guide")
        if len(admitted_after):
            v = admitted_after.iloc[-1]
            try:
                f = k0.kernel_guide(target, after)
            except (k0.DataUnavailable, k0.PointInTimeError):
                continue
            diagnostic.append(dict(quarter=target, guide_date=str(origin.date()),
                                   as_of=str(after.date()), basis="post_letter_not_preguide",
                                   street_vendor=v.vendor, street_as_of=v.as_of_timestamp,
                                   consensus_musd=float(v.value), register_id=v.register_id,
                                   kernel_guide_musd=f["point"], actual_guide_mid_musd=row.value_mid,
                                   signal_pct=100*(f["point"]/v.value-1), actual_gap_pct=100*(row.value_mid/v.value-1)))
    return pd.DataFrame(rows), pd.DataFrame(audits), pd.DataFrame(diagnostic)


def live_rows(vintages):
    term = k0.term_structure(AS_OF)
    q4 = term[term.quarter.eq("2026Q4")].iloc[0]
    rows = []
    admitted = consensus_candidates(vintages, "2026Q4", AS_OF, role="current")
    families = (("LSEG-family Alpha Vantage", "Alpha Vantage"),
                ("S&P Global", "S&P Global"), ("Zacks", "Zacks"))
    for family, needle in families:
        v = admitted[admitted.vendor.str.contains(needle, regex=False)].iloc[-1]
        rows.append(dict(quarter="2026Q4", forecast_as_of=AS_OF, guide_event_date="2026-11-05",
                         vendor_family=family, street_vendor=v.vendor, street_as_of=v.as_of_timestamp,
                         register_id=v.register_id, consensus_musd=float(v.value),
                         conditional_guide_musd=float(q4.guide_mid_musd),
                         conditional_signal_pct=100*(q4.guide_mid_musd/v.value-1),
                         guide_q10=float(q4.guide_q10), guide_q90=float(q4.guide_q90),
                         status="conditional_RNPL_scenario_not_future_November_vintage"))
    return pd.DataFrame(rows)


def baseline_audit(history, vintages):
    rows = []
    for i, r in history.iterrows():
        previous = history.iloc[:i]
        prior_sign, vendor, stamp = np.nan, "", ""
        if len(previous):
            last = previous.iloc[-1]
            # A past surprise can be known today even though its date-only
            # consensus was inadmissible for trading ahead of that past guide.
            values = consensus_candidates(vintages, last.quarter, r.guide_date, role="pre_guide")
            if len(values):
                v = values.iloc[-1]
                prior_sign = interval_sign(last.guide_mid_lo-v.value, last.guide_mid_hi-v.value)
                vendor, stamp = v.vendor, v.as_of_timestamp
        for name, prediction in (("zero", 0.), ("previous_surprise_sign", prior_sign),
                                 ("consensus_base", np.nan)):
            rows.append(dict(quarter=r.quarter, guide_date=r.guide_date, baseline=name,
                             predicted_sign=prediction,
                             evaluation_available=bool(np.isfinite(r.actual_sign)),
                             street_vendor=vendor if name == "previous_surprise_sign" else r.street_vendor,
                             street_as_of=stamp if name == "previous_surprise_sign" else r.street_as_of,
                             reason="No admissible current pre-guide consensus; no baseline score",
                             consensus_base_definition="guide=consensus/(1+trailing8_median_cushion)" if name == "consensus_base" else ""))
    return pd.DataFrame(rows)


def conditional_returns(history):
    rows = []
    for window, first in (("W1", "2023Q1"), ("W2", "2024Q1")):
        f = history[history.quarter.between(first, "2026Q2")]
        for selection in ("all_nonzero_signals", "abs_signal_gt_1pp"):
            use = f[f.signal_pct.notna() & f.signal_pct.ne(0)]
            if selection == "abs_signal_gt_1pp":
                use = use[use.signal_pct.abs().gt(1)]
            for side in ("positive", "negative", "signed_pooled"):
                selected = use if side == "signed_pooled" else use[np.sign(use.signal_pct).eq(1 if side == "positive" else -1)]
                for day in (1, 5, 20):
                    actual = selected.dropna(subset=[f"open_{day}d_pct"])
                    values = actual[f"open_{day}d_pct"].to_numpy(float)
                    if side == "signed_pooled":
                        values = values*np.sign(actual.signal_pct.to_numpy(float))
                    lo, hi = block_ci(values)
                    rows.append(dict(window=window, selection=selection, side=side, horizon_days=day,
                                     n_signals=len(selected), n_executable_returns=len(values),
                                     mean_pct=float(values.mean()) if len(values) else np.nan,
                                     ci_lo_pct=lo, ci_hi_pct=hi))
    return pd.DataFrame(rows)


def main():
    start = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    guides, vintages, reactions, hashes = read_inputs()
    history, audits, diagnostic = build_history(guides, vintages, reactions)
    stats = statistics(history)
    live = live_rows(vintages)
    for name, frame in (("pit_cells", history), ("consensus_exclusions", audits),
                        ("post_letter_diagnostic", diagnostic), ("statistics", stats),
                        ("live_november_guide_scenario", live),
                        ("baseline_audit", baseline_audit(history, vintages)),
                        ("conditional_returns", conditional_returns(history))):
        frame.to_csv(OUT / f"{name}.csv", index=False)
    # The frozen registry accepts neither today's actual date nor guide-gap target.
    # No row may be backdated to September 11 or future-dated to November 5.
    request = dict(method="alpha-a", object="guide_gap_next_q", historical_rows=0,
                   live_rows_registered=0, actual_forecast_date=AS_OF,
                   reason="No admissible historical signals; LIVE date 2026-09-12 is outside frozen calendar; gap target is absent",
                   requested_target="guide_gap_next_q_pct", requested_date=AS_OF,
                   target_alternative="guide_mid is supported but changes object from gap to guide level")
    (OUT / "registry_status.json").write_text(json.dumps(request, indent=2)+"\n", encoding="utf-8")
    pd.DataFrame(columns=REGISTRY_COLUMNS).to_csv(OUT / "alpha-a__guide_gap_next_q_UNREGISTERED.csv", index=False)
    # Produce the S-versus-gap figure even when there are no admissible points.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    complete = history.dropna(subset=["signal_pct", "actual_gap_pct"])
    if len(complete):
        axes[0].scatter(complete.signal_pct, complete.actual_gap_pct, color="#356b81")
    else:
        counts = "; ".join(f"{r.n_signal}/{r.n_dates} {r.window}" for r in stats.itertuples())
        axes[0].text(.5, .5, f"Strict pre-guide\n{counts} admissible signals\nNo points to estimate an edge", ha="center", va="center", transform=axes[0].transAxes)
    axes[0].set_title("Preregistered test")
    if len(diagnostic):
        axes[1].scatter(diagnostic.signal_pct, diagnostic.actual_gap_pct, color="#ad6542", alpha=.8)
    axes[1].set_title(f"Post-letter diagnostic only (n={len(diagnostic)})")
    for ax in axes:
        ax.axhline(0, color="gray", lw=.6); ax.axvline(0, color="gray", lw=.6)
        ax.set_xlabel("Kernel guide minus dated consensus (%)")
        ax.set_ylabel("Actual guide minus dated consensus (%)")
    fig.suptitle("A: same-letter inputs cannot establish a pre-guide expectations edge")
    fig.tight_layout(); fig.savefig(OUT / "signal_vs_gap.png", dpi=170); plt.close(fig)
    audit = dict(as_of=AS_OF, input_hashes=hashes, reaction_columns=list(reactions.columns),
                 open_columns=[c for c in reactions if c.startswith("open_")],
                 historical_dates=len(history), extension_dates=int(history.extension.sum()),
                 post_letter_diagnostic_n=len(diagnostic), imported_kernel="kernel_engine_v2.engine",
                 prereg_note="docs/revenue-forecast-strategy/05_backtests/ALPHA_A_GUIDE_SURPRISE.md",
                 parameter_count=dict(kernel_season=1, trailing_cushion=1, ridge_intercept_and_slope=2,
                                      fixed_kernel_weights=0, fixed_ridge_penalty=0),
                 elapsed_seconds=round(time.perf_counter()-start, 3))
    (OUT / "audit.json").write_text(json.dumps(audit, indent=2)+"\n", encoding="utf-8")
    print(stats.to_string(index=False))
    print(live[["street_vendor", "street_as_of", "consensus_musd", "conditional_guide_musd", "conditional_signal_pct"]].to_string(index=False))
    verdict = "underpowered" if stats.verdict.eq("underpowered").any() else ("pass" if stats.verdict.eq("pass").all() else "fail")
    print(f"A verdict: {verdict}; historical registry rows=0; open columns={audit['open_columns']}; runtime={audit['elapsed_seconds']}s")


if __name__ == "__main__":
    main()
