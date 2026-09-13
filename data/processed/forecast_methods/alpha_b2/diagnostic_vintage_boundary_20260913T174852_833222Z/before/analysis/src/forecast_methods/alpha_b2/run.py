"""B2: post-letter kernel versus next-quarter consensus revisions.

Run from the repository root. Input files and prior output runs remain immutable.
Weights vary the arithmetic base only; imported seasonal lambdas are held fixed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "analysis/src/forecast_methods"))
from kernel_engine_v2 import engine as K
from harness import baseline_naive
from harness_v1_1 import RUN_DATE
from harness_v1_1.registry import register, validate_registry_frame

DATA = ROOT / "data/processed/forecast_methods"
OUT = DATA / "alpha_b2"
SEED = 20260913
DRAWS = 10000
WEIGHTS = (0.33, 0.5, 2 / 3)
INPUTS = {
    "calendar": DATA / "harness/calendar.csv",
    "targets": DATA / "harness/targets.csv",
    "vintages": DATA / "L0/L0_vintage_register.csv",
    "fy": ROOT / "data/processed/overnight/02_fy_guide_revisions.csv",
    "guidance": ROOT / "data/processed/overnight/02_guidance_ledger.csv",
    "consensus": ROOT / "data/processed/overnight/16_consensus_at_print_merged.csv",
    "returns": DATA / "returns_v1/earnings_reactions_open_v1.csv",
    "kernel": ROOT / "analysis/src/forecast_methods/kernel_engine_v2/engine.py",
}


def shift(q, n):
    return str(pd.Period(q, freq="Q") + n)


def day(value):
    return pd.Timestamp(value).normalize()


def registry_horizon(target_quarter, vintage_date):
    """FORMAT 1.0/1.1 units: target quarter minus vintage calendar quarter."""
    horizon = pd.Period(target_quarter, freq="Q").ordinal - day(vintage_date).to_period("Q").ordinal
    if horizon < 0:
        raise ValueError("Registry horizon must be nonnegative")
    return int(horizon)


def truth(series):
    return series.astype(str).str.lower().eq("true")


def admissible_consensus(vintages, period, as_of, role, *, exact_day=False):
    """Select only attributed, PIT-usable revenue in the requested role."""
    if role not in ("pre_guide", "at_print", "current"):
        raise ValueError("Unsupported consensus role")
    v = vintages.copy()
    stamps = pd.to_datetime(v.as_of_timestamp, errors="coerce", utc=True, format="mixed").dt.tz_localize(None)
    cutoff = day(as_of) + pd.Timedelta(days=1)
    mask = (v.period.eq(period) & v.metric.eq("revenue") & v.role.eq(role)
            & truth(v.pit_usable) & truth(v.vendor_attributed)
            & pd.to_numeric(v.value, errors="coerce").gt(0) & stamps.lt(cutoff))
    if exact_day:
        mask &= stamps.dt.normalize().eq(day(as_of))
    if role == "current":
        mask &= stamps.le(pd.Timestamp.now(tz="UTC").tz_localize(None))
    v = v.loc[mask].copy()
    if v.empty:
        return None
    v["_stamp"] = stamps[mask]
    return v.sort_values(["_stamp", "register_id"]).iloc[-1].drop(labels="_stamp").to_dict()


def consensus_fields(prefix, value):
    return {prefix + "_" + col: (value.get(col) if value else None)
            for col in ("value", "vendor", "as_of_timestamp", "register_id")}


def trailing_gbv_growth(panel):
    """Observed four-quarter mean of exact y/y growth, in fraction units."""
    p = panel.set_index("quarter").gbv_musd
    values = [(p[q] / p[shift(q, -4)] - 1) for q in p.index if shift(q, -4) in p.index]
    values = np.asarray(values[-4:], dtype=float)
    if len(values) != 4 or not np.isfinite(values).all():
        raise K.DataUnavailable("Four observed GBV y/y growth rates are required")
    return float(values.mean())


def extrapolated_gbv(panel, steps=2):
    growth = trailing_gbv_growth(panel)
    known = panel.set_index("quarter").gbv_musd.to_dict()
    q = str(panel.quarter.max())
    forecasts = {}
    for step in range(1, steps + 1):
        future = shift(q, step)
        forecasts[future] = float(known[q] * (1 + growth) ** step)
    return {**known, **forecasts}, growth


def forecast_term(as_of, *, prior_basis="PIT", max_steps=3):
    """Use the engine at d+1; same-letter inputs are then knowable by d.

    Full-sample is an explicit look-ahead replay of coefficients/cushion only.
    Origin GBVs and trailing growth stay point-in-time for both replays.
    """
    origin = day(as_of)
    engine_date = origin + pd.Timedelta(days=1)
    panel = K._panel(engine_date)
    assert panel.print_date.max() <= origin
    fit_date = engine_date if prior_basis == "PIT" else day(RUN_DATE) + pd.Timedelta(days=1)
    divisor = float(K._cushions(fit_date).ratio.median())
    values, growth = extrapolated_gbv(panel, steps=max_steps - 1)
    latest = str(panel.quarter.max())
    rows = []
    for step in range(1, max_steps + 1):
        q = shift(latest, step)
        try:
            lam = K.pit_lambda(int(q[-1]), fit_date)
            error = ""
        except K.DataUnavailable as exc:
            lam = None
            error = str(exc)
        for weight in WEIGHTS:
            base = weight * values[shift(q, -1)] + (1 - weight) * values[shift(q, -2)]
            revenue = base * lam["lambda_pct"] / 100 if lam else np.nan
            rows.append(dict(
                event_date=str(origin.date()), engine_as_of=str(engine_date.date()),
                prior_basis=prior_basis, quarter=q, horizon_from_print=step,
                latest_printed_quarter=latest, weight=weight, revenue_musd=revenue,
                kernel_guide_musd=revenue / divisor, cushion_ratio=divisor,
                lambda_pct=lam["lambda_pct"] if lam else np.nan,
                lambda_variant=lam["variant"] if lam else None,
                lambda_n=lam["n_train"] if lam else 0,
                lambda_training_quarters="|".join(lam["training_quarters"]) if lam else "",
                coefficient_cutoff=str((fit_date - pd.Timedelta(days=1)).date()),
                gbv_lag1_musd=float(values[shift(q, -1)]),
                gbv_lag2_musd=float(values[shift(q, -2)]),
                gbv_trailing4_growth=growth, known_panel_n=len(panel),
                knowable_from=str(panel.print_date.max().date()), unavailable_reason=error,
            ))
    return pd.DataFrame(rows), panel


def wilson(hits, n):
    if not n:
        return np.nan, np.nan
    z = 1.959963984540054
    p = hits / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0., centre - half), min(1., centre + half)


def correlation(x, y):
    if len(x) < 3 or np.ptp(x) < 1e-12 or np.ptp(y) < 1e-12:
        return np.nan
    return float(np.corrcoef(x, y)[0, 1])


def corr_bootstrap(x, y, draws=DRAWS):
    if len(x) < 4 or not np.isfinite(correlation(x, y)):
        return np.nan, np.nan, 0
    rng = np.random.default_rng(SEED)
    block = 2
    starts = rng.integers(0, len(x) - block + 1, size=(draws, int(np.ceil(len(x) / block))))
    indices = (starts[:, :, None] + np.arange(block)).reshape(draws, -1)[:, :len(x)]
    bx, by = x[indices], y[indices]
    bx, by = bx - bx.mean(axis=1, keepdims=True), by - by.mean(axis=1, keepdims=True)
    denom = np.sqrt((bx * bx).sum(axis=1) * (by * by).sum(axis=1))
    vals = np.divide((bx * by).sum(axis=1), denom, out=np.full(draws, np.nan), where=denom > 1e-12)
    vals = vals[np.isfinite(vals)]
    if not len(vals):
        return np.nan, np.nan, 0
    lo, hi = np.quantile(vals, [.025, .975])
    return float(lo), float(hi), len(vals)


def pair_stats(frame, signal="s1_pct", outcome="revision_pct", threshold=.5):
    pairs = frame.dropna(subset=[signal, outcome]).sort_values("event_date")
    x, y = pairs[signal].to_numpy(float), pairs[outcome].to_numpy(float)
    strong = np.abs(x) > threshold
    hits = int(np.sum(np.sign(x[strong]) == np.sign(y[strong])))
    n = int(strong.sum())
    lo, hi = wilson(hits, n)
    corr = correlation(x, y)
    clo, chi, valid = corr_bootstrap(x, y)
    sign_p = corr_p = np.nan
    if len(x):
        rng = np.random.default_rng(SEED + 1)
        perm = np.stack([rng.permutation(y) for _ in range(DRAWS)])
        if n:
            perm_hits = (np.sign(perm[:, strong]) == np.sign(x[strong])).sum(axis=1)
            sign_p = float((1 + (perm_hits >= hits).sum()) / (DRAWS + 1))
        if np.isfinite(corr):
            centred = x - x.mean()
            pc = (perm - y.mean()) @ centred / np.sqrt((centred ** 2).sum() * ((y - y.mean()) ** 2).sum())
            corr_p = float((1 + (np.abs(pc) >= abs(corr) - 1e-12).sum()) / (DRAWS + 1))
    return dict(signal=signal, outcome=outcome, n_pairs=len(pairs), n_strong=n,
                hits=hits, hit_rate=hits / n if n else np.nan,
                wilson_lo=lo, wilson_hi=hi, corr=corr, corr_lo=clo, corr_hi=chi,
                valid_bootstrap_draws=valid, sign_permutation_p=sign_p,
                corr_permutation_p=corr_p,
                positive_revisions=int((y > 0).sum()), zero_revisions=int((y == 0).sum()),
                negative_revisions=int((y < 0).sum()))


def fy_sensitivity(event_date, panel, term, fy):
    """FY bucket is a management range converted to dollars, not Street FY."""
    d = day(event_date)
    fiscal_year = str(shift(panel.quarter.max(), 1))[:4]
    year_tag = "FY" + fiscal_year
    source = fy[(fy.metric == "revenue_yoy_pct") & (fy.target_period == year_tag)
                & (pd.to_datetime(fy.print_date) <= d)].sort_values("print_date")
    result = dict(fy_period=year_tag, fy_anchor_musd=np.nan, fy_kernel_musd=np.nan,
                  t_pct=np.nan, t_low_anchor_pct=np.nan, t_high_anchor_pct=np.nan,
                  fy_bucket_mid_pct=np.nan, fy_bucket_stamp=None)
    if source.empty:
        return result
    anchor = source.iloc[-1]
    prior = panel[panel.quarter.str.startswith(str(int(fiscal_year) - 1))]
    if len(prior) != 4:
        return result
    prior_total = float(prior.revenue_musd.sum())
    printed = panel.set_index("quarter").revenue_musd.to_dict()
    future = term[term.horizon_from_print.le(2)].set_index("quarter").kernel_guide_musd.to_dict()
    parts = []
    for season in range(1, 5):
        q = f"{fiscal_year}Q{season}"
        parts.append(printed.get(q, future.get(q, printed.get(shift(q, -4), np.nan))))
    kernel_fy = float(np.sum(parts))
    a = prior_total * (1 + float(anchor.value_mid) / 100)
    result.update(fy_anchor_musd=a, fy_kernel_musd=kernel_fy,
                  t_pct=100 * (kernel_fy / a - 1), fy_bucket_mid_pct=float(anchor.value_mid),
                  fy_bucket_stamp=anchor.print_date,
                  t_low_anchor_pct=100 * (kernel_fy / (prior_total * (1 + anchor.value_low / 100)) - 1),
                  t_high_anchor_pct=100 * (kernel_fy / (prior_total * (1 + anchor.value_high / 100)) - 1))
    return result


def bucket_change(fy, period, d, next_d):
    r = fy[(fy.metric == "revenue_yoy_pct") & (fy.target_period == period)].copy()
    stamps = pd.to_datetime(r.print_date)
    before = r[stamps <= day(d)].sort_values("print_date")
    after = r[stamps == day(next_d)]
    if before.empty or after.empty:
        return np.nan
    return float(np.sign(after.iloc[-1].value_mid - before.iloc[-1].value_mid))


def revision_at(vintages, target, d, next_d):
    before = admissible_consensus(vintages, target, d, "pre_guide", exact_day=True)
    after = admissible_consensus(vintages, target, next_d, "at_print", exact_day=True)
    rev = 100 * (float(after["value"]) / float(before["value"]) - 1) if before and after else np.nan
    return before, after, rev


def vendor_family(vendor):
    return "LSEG family" if any(x in str(vendor).lower() for x in ("lseg", "refinitiv", "yahoo", "alpha vantage")) else str(vendor)


def live_comparisons(vintages, live, as_of):
    selected = []
    for q in ("2026Q4", "2027Q1"):
        subset = vintages[(vintages.period == q) & (vintages.metric == "revenue") & (vintages.role == "current")].copy()
        stamps = pd.to_datetime(subset.as_of_timestamp, errors="coerce", utc=True, format="mixed").dt.tz_localize(None)
        subset = subset[truth(subset.pit_usable) & truth(subset.vendor_attributed)
                        & pd.to_numeric(subset.value, errors="coerce").gt(0)
                        & (stamps < day(as_of) + pd.Timedelta(days=1))
                        & stamps.le(pd.Timestamp.now(tz="UTC").tz_localize(None))]
        subset["_stamp"] = stamps.loc[subset.index]
        subset["family"] = subset.vendor.map(vendor_family)
        # Same-day LSEG relay tie: Alpha Vantage first, then provider name; all discarded relays remain auditable in source register.
        subset["_priority"] = subset.vendor.astype(str).str.contains("Alpha Vantage").astype(int)
        subset = subset.sort_values(["_stamp", "_priority", "register_id"]).groupby("family", sort=True).tail(1)
        if subset.empty:
            subset = pd.DataFrame([dict(period=q, family="unavailable", value=np.nan,
                                        vendor="unavailable", as_of_timestamp=None, register_id=None)])
        for source in subset.to_dict("records"):
            for f in live[live.quarter == q].to_dict("records"):
                value = float(source["value"])
                selected.append(dict(quarter=q, weight=f["weight"],
                    revenue_musd=f["revenue_musd"], kernel_guide_musd=f["kernel_guide_musd"],
                    consensus_musd=value, vendor=source["vendor"], vendor_family=source["family"],
                    as_of_timestamp=source["as_of_timestamp"], register_id=source["register_id"],
                    guide_gap_pct=100 * (f["kernel_guide_musd"] / value - 1),
                    revenue_gap_pct=100 * (f["revenue_musd"] / value - 1),
                    forecast_date=str(as_of), status="LIVE arithmetic sensitivity"))
    return pd.DataFrame(selected)


def baselines(frame):
    eligible = frame.dropna(subset=["s1_pct", "revision_pct"])
    rows = []
    for name, col in (("no_revision", None), ("last_revision_continues", "last_revision_pct")):
        cells = eligible if col is None else eligible.dropna(subset=[col])
        pred = np.zeros(len(cells)) if col is None else cells[col].to_numpy(float)
        actual = cells.revision_pct.to_numpy(float)
        strong = cells.s1_pct.abs().gt(.5).to_numpy()
        hits = int((np.sign(pred[strong]) == np.sign(actual[strong])).sum())
        lo, hi = wilson(hits, int(strong.sum()))
        rows.append(dict(baseline=name, n=len(cells), n_strong=int(strong.sum()), hits=hits,
                         hit_rate=hits / strong.sum() if strong.sum() else np.nan,
                         wilson_lo=lo, wilson_hi=hi,
                         mae_revision_pp=float(np.abs(pred - actual).mean()) if len(cells) else np.nan,
                         rmse_revision_pp=float(np.sqrt(((pred - actual) ** 2).mean())) if len(cells) else np.nan))
    return rows


def make_registry(historical, live, targets):
    rows = []
    for f in historical[(historical.horizon_from_print == 2) & np.isclose(historical.weight, 2 / 3)].to_dict("records"):
        if not np.isfinite(f["revenue_musd"]) or not ("2023Q1" <= f["quarter"] <= "2026Q2"):
            continue
        windows = ["W1"] + (["W2"] if f["quarter"] >= "2024Q1" else [])
        for window in windows:
            naive = baseline_naive(f["event_date"], f["quarter"])
            rows.append(dict(method="alpha-b2", object="revenue_q_plus_2", target="revenue_musd",
                quarter=f["quarter"], vintage_date=f["event_date"],
                horizon_q=registry_horizon(f["quarter"], f["event_date"]),
                point=f["revenue_musd"], q50=f["revenue_musd"], window=window,
                prior_basis=f["prior_basis"], n_params=2, n_train=f["known_panel_n"],
                base_naive=naive["point"],
                knowable_from=f["knowable_from"] if f["prior_basis"] == "PIT" else None,
                spec_id="w_2over3_unseasonal_gbv_growth",
                notes="Revenue before guide cushion; full_sample coefficients look ahead to RUN_DATE; horizon_from_print=2 in sidecar; horizon_q uses vintage calendar quarter"))
    for f in live[(live.quarter.isin(["2026Q4", "2027Q1"])) & np.isclose(live.weight, 2 / 3)].to_dict("records"):
        for basis in ("PIT", "full_sample"):
            rows.append(dict(method="alpha-b2", object="revenue_q_plus_2", target="revenue_musd",
                quarter=f["quarter"], vintage_date=str(RUN_DATE),
                horizon_q=registry_horizon(f["quarter"], RUN_DATE),
                point=f["revenue_musd"], q50=f["revenue_musd"], window="LIVE", prior_basis=basis,
                n_params=2, n_train=f["known_panel_n"], knowable_from=f["knowable_from"],
                spec_id="w_2over3_unseasonal_gbv_growth",
                notes="LIVE conditional revenue before guide cushion; Q1 2027 persists GBV growth twice; no predictive interval"))
    registry = pd.DataFrame(rows)
    validate_registry_frame(registry)
    return registry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-register", action="store_true")
    parser.add_argument("--correct-horizon-metadata", action="store_true",
                        help="Preserve the prior registry and replace horizon units and explanatory notes only")
    args = parser.parse_args()
    if args.no_register and args.correct_horizon_metadata:
        parser.error("--correct-horizon-metadata requires registration")
    started = time.perf_counter()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    destination = OUT / ("run_" + stamp)
    destination.mkdir(parents=True, exist_ok=False)
    source_bytes = {k: p.read_bytes() for k, p in INPUTS.items()}
    inputs = {k: pd.read_csv(io.StringIO(source_bytes[k].decode("utf-8-sig")), comment="#")
              for k, p in INPUTS.items() if p.suffix == ".csv"}
    calendar, vintages, fy = inputs["calendar"], inputs["vintages"], inputs["fy"]
    events = calendar[(calendar.next_quarter_guided >= "2023Q1") & (calendar.next_quarter_guided <= "2026Q2")].sort_values("print_date")
    all_events = calendar.sort_values("print_date").reset_index(drop=True)
    ret = inputs["returns"].set_index("event_date")
    terms, cells = [], []
    for event in events.itertuples():
        d, q1 = event.print_date, event.next_quarter_guided
        q2 = shift(q1, 1)
        next_d = calendar.loc[calendar.print_quarter == q1, "print_date"].iloc[0]
        c1, cnext, revision = revision_at(vintages, q1, d, next_d)
        c2 = admissible_consensus(vintages, q2, d, "pre_guide")
        current_idx = all_events.index[all_events.print_date == d][0]
        prior_rev = np.nan
        if current_idx:
            previous = all_events.iloc[current_idx - 1]
            prior_rev = revision_at(vintages, previous.next_quarter_guided, previous.print_date, d)[2]
        for basis in ("PIT", "full_sample"):
            term, panel = forecast_term(d, prior_basis=basis, max_steps=2)
            terms.append(term)
            for w in WEIGHTS:
                spec = term[np.isclose(term.weight, w)]
                f1, f2 = spec[spec.quarter == q1].iloc[0], spec[spec.quarter == q2].iloc[0]
                annual = fy_sensitivity(d, panel, spec, fy)
                row = dict(event_date=d, next_event_date=next_d, guided_quarter=q1, q_plus_2=q2,
                    prior_basis=basis, weight=w, k_q1_musd=f1.kernel_guide_musd,
                    k_q2_musd=f2.kernel_guide_musd, revenue_q2_musd=f2.revenue_musd,
                    s1_pct=100 * (f1.kernel_guide_musd / float(c1["value"]) - 1) if c1 else np.nan,
                    s2_pct=100 * (f2.kernel_guide_musd / float(c2["value"]) - 1) if c2 else np.nan,
                    revision_pct=revision, last_revision_pct=prior_rev,
                    q1_unavailable_reason=f1.unavailable_reason,
                    consensus_unavailable_reason="" if c1 else "No attributed PIT-usable same-day pre-guide row; preserve quarantine",
                    q2_consensus_unavailable_reason="" if c2 else "No pre-guide q+2 consensus at origin",
                    **consensus_fields("c_pre", c1), **consensus_fields("c_next", cnext),
                    **consensus_fields("c_q2", c2), **annual,
                    fy_bucket_change=bucket_change(fy, annual["fy_period"], d, next_d))
                for horizon in (20, 60):
                    col = f"excess_open_{horizon}d_pct"
                    row[col] = float(ret.loc[d, col]) if d in ret.index else np.nan
                cells.append(row)
    cells, terms = pd.DataFrame(cells), pd.concat(terms, ignore_index=True)
    statistics, baseline_rows, returns_rows = [], [], []
    for basis in ("PIT", "full_sample"):
        for window, first in (("W1", "2023Q1"), ("W2", "2024Q1")):
            subset = cells[(cells.prior_basis == basis) & (cells.guided_quarter >= first)
                           & np.isclose(cells.weight, 2 / 3)]
            for signal, outcome in (("s1_pct", "revision_pct"), ("t_pct", "revision_pct"), ("t_pct", "fy_bucket_change")):
                statistics.append(dict(window=window, prior_basis=basis, n_origins=len(subset), **pair_stats(subset, signal, outcome)))
            baseline_rows += [dict(window=window, prior_basis=basis, **row) for row in baselines(subset)]
            for signal in ("s1_pct", "t_pct"):
                for horizon in (20, 60):
                    col = f"excess_open_{horizon}d_pct"
                    paired = subset.dropna(subset=[signal, col])
                    strong = paired[paired[signal].abs() > .5]
                    aligned = np.sign(strong[signal]) * strong[col]
                    returns_rows.append(dict(window=window, prior_basis=basis, signal=signal, horizon_days=horizon,
                        n_pairs=len(paired), n_strong=len(strong), mean_excess_pct=float(strong[col].mean()),
                        mean_signal_aligned_excess_pct=float(aligned.mean()),
                        sign_hits=int((aligned > 0).sum()), corr=correlation(paired[signal].to_numpy(), paired[col].to_numpy())))
    live, _ = forecast_term(RUN_DATE, max_steps=3)
    comparison = live_comparisons(vintages, live, RUN_DATE)
    registry = make_registry(terms, live, inputs["targets"])
    stats = pd.DataFrame(statistics)
    primary = stats[(stats.prior_basis == "PIT") & (stats.signal == "s1_pct")]
    if primary.n_strong.lt(6).any():
        verdict = "UNDERPOWERED"
    elif (primary.hit_rate.ge(.7) & primary["corr"].gt(.4)).all():
        verdict = "PASS"
    else:
        verdict = "FAIL"
    outputs = dict(cells=cells, historical_term_structure=terms, statistics=stats,
        revision_baselines=pd.DataFrame(baseline_rows), return_statistics=pd.DataFrame(returns_rows),
        live_term_structure=live, current_consensus_comparisons=comparison, registry_candidate=registry)
    for name, frame in outputs.items():
        frame.to_csv(destination / (name + ".csv"), index=False)
    manifest = {k: dict(path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(source_bytes[k]).hexdigest()) for k, p in INPUTS.items()}
    (destination / "input_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    registry_path = DATA / "registry/alpha-b2__revenue_q_plus_2.csv"
    status = "candidate only"
    metadata_audit = None
    if not args.no_register:
        if registry_path.exists():
            prior_bytes = registry_path.read_bytes()
            prior = pd.read_csv(io.StringIO(prior_bytes.decode("utf-8-sig")))
            shared = list(registry.columns)
            if args.correct_horizon_metadata:
                preserved = [col for col in shared if col not in ("horizon_q", "notes")]
                pd.testing.assert_frame_equal(prior[preserved], registry[preserved], check_dtype=False,
                                              check_exact=False, atol=1e-8, rtol=1e-10)
                backup = destination / "registry_before_horizon_metadata_correction.csv"
                backup.write_bytes(prior_bytes)
                metadata_audit = dict(changed_fields=["horizon_q", "notes"],
                    horizon_rows_changed=int(prior.horizon_q.ne(registry.horizon_q).sum()),
                    note_rows_changed=int(prior.notes.ne(registry.notes).sum()),
                    preserved_fields=preserved, prior_registry_sha256=hashlib.sha256(prior_bytes).hexdigest(),
                    prior_registry_snapshot=str(backup.relative_to(ROOT)),
                    forecast_values_unchanged=True)
                register(registry)
                status = "horizon metadata corrected; prior registry snapshot preserved"
            else:
                pd.testing.assert_frame_equal(prior[shared], registry[shared], check_dtype=False, check_exact=False,
                                              atol=1e-8, rtol=1e-10)
                status = "existing identical registry preserved"
        else:
            register(registry)
            status = "registered through harness_v1_1"
    summary = dict(verdict=verdict, run_date=str(RUN_DATE), run_timestamp_utc=stamp,
                   elapsed_seconds=time.perf_counter() - started, registry_rows=len(registry),
                   registry_status=status, primary_statistics=primary.to_dict("records"),
                   metadata_audit=metadata_audit,
                   output_directory=str(destination.relative_to(ROOT)), draws=DRAWS, seed=SEED,
                   score_status="Parent must run both scorers",
                   parameter_count="Revenue: 1 seasonal lambda + 1 trailing growth summary = 2; guide adds 1 cushion; fixed weight and fixed half-life not fitted",
                   caveat="Prescribed GBV extrapolation has no seasonal anchor; weight bands are arithmetic sensitivities, not prediction intervals")
    (destination / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
