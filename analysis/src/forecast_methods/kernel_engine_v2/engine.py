"""Strict-PIT two-lag recognition kernel. Currency outputs are USD millions.

The same-day letter is deliberately unavailable at a date-only guide origin.
Regional coefficients are supplied by X; this module never estimates them.
"""
from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
VARIANTS = ("ex_covid", "last3", "ewm")
WEIGHT = 2 / 3
SEED = 20260912
RNPL_SCENARIO_AVAILABLE = pd.Timestamp("2026-09-11")


class PointInTimeError(ValueError):
    """An input has no admissible publication date before the cutoff."""


class DataUnavailable(ValueError):
    """A required, admissible observation or forecast does not exist."""


def _date(value):
    ts = pd.Timestamp(value)
    if pd.isna(ts):
        raise ValueError("as_of must be a valid date")
    if ts.tzinfo is not None:
        ts = ts.tz_convert("UTC").tz_localize(None)
    return ts.normalize()


def _quarter(value):
    value = str(value).upper().strip()
    if len(value) == 4 and value[1] == "Q":
        value = "20" + value[2:] + "Q" + value[0]
    try:
        return str(pd.Period(value, freq="Q"))
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Invalid quarter: {value}") from exc


def _season(value):
    number = float(value)
    if not np.isfinite(number) or number not in (1, 2, 3, 4):
        raise ValueError("season must be an integer 1..4")
    return int(number)


def _knowable(*frames):
    dates = [f.print_date.max() for f in frames if f is not None and not f.empty]
    if not dates:
        raise DataUnavailable("No dated observations")
    return str(max(dates).date())


def _shift(q, n):
    return str(pd.Period(_quarter(q), freq="Q") + n)


def _calendar():
    c = pd.read_csv(ROOT / "data/processed/forecast_methods/harness/calendar.csv")
    return dict(zip(c.print_quarter, pd.to_datetime(c.print_date)))


def _dated(frame, as_of, keys, values):
    f = frame.copy(deep=True)
    required = set(keys) | set(values) | {"print_date"}
    if required - set(f):
        raise ValueError(f"Missing columns: {sorted(required-set(f))}")
    if f[list(keys)].isna().any().any() or f.duplicated(list(keys)).any():
        raise ValueError(f"Null or duplicate keys: {keys}")
    dates = pd.to_datetime(f.print_date, errors="coerce", utc=True).dt.tz_localize(None).dt.normalize()
    if dates.isna().any() or (dates >= _date(as_of)).any():
        raise PointInTimeError("Every input publication date must be strictly before as_of; same-day data refused")
    f["print_date"] = dates
    for col in values:
        f[col] = pd.to_numeric(f[col], errors="raise")
        if not np.isfinite(f[col]).all() or (f[col] <= 0).any():
            raise ValueError(f"{col} must contain finite positive values")
    return f


def _panel(as_of, panel=None):
    if panel is None:
        f = pd.read_csv(ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv")
        f["quarter"] = f.quarter.map(_quarter)
        f = f.copy()
        f["print_date"] = f.quarter.map(_calendar())
        if f.print_date.isna().any():
            raise PointInTimeError("KPI publication date missing from frozen calendar")
        f = f[f.print_date < _date(as_of)].copy()
    else:
        f = panel.copy(deep=True)
        f["quarter"] = f.quarter.map(_quarter)
    f = _dated(f, as_of, ["quarter"], ["gbv_musd", "revenue_musd"])
    return f.sort_values("quarter").reset_index(drop=True)


def _lambda_rows(panel):
    f = panel.copy()
    lookup = f.set_index("quarter").gbv_musd.to_dict()
    f["season"] = f.quarter.str[-1].astype(int)
    f["gbv_l1"] = f.quarter.map(lambda q: lookup.get(_shift(q, -1), np.nan))
    f["gbv_l2"] = f.quarter.map(lambda q: lookup.get(_shift(q, -2), np.nan))
    f["base_musd"] = WEIGHT * f.gbv_l1 + (1-WEIGHT) * f.gbv_l2
    f["lambda_pct"] = 100 * f.revenue_musd / f.base_musd
    if "nights_yoy_pct" not in f:
        f["nights_yoy_pct"] = np.nan
    return f.dropna(subset=["lambda_pct"]).reset_index(drop=True)


def _estimate(rows, season, variant):
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}")
    f = rows[rows.season == int(season)].sort_values("quarter")
    if variant == "ex_covid":
        f = f[f.nights_yoy_pct.notna() & (f.nights_yoy_pct.abs() <= 25)]
    if variant == "last3":
        f = f.tail(3)
    if f.empty:
        raise DataUnavailable(f"No admissible same-season lambda observations: season={season}; variant={variant}")
    weights = (2.0 ** (-np.arange(len(f)-1, -1, -1)/2)
               if variant == "ewm" else np.ones(len(f)))
    return float(np.average(f.lambda_pct, weights=weights)), f


def _loo(rows):
    # Full W1 LOO is retrospective model selection, never a PIT performance score.
    w = rows[rows.quarter.between("2023Q1", "2026Q2")]
    cells = []
    for row in w.itertuples():
        estimates = {}
        for variant in VARIANTS:
            try:
                lam, _ = _estimate(w[w.quarter != row.quarter], row.season, variant)
                estimates[variant] = 100 * ((lam/100*row.base_musd)/row.revenue_musd-1)
            except DataUnavailable:
                break
        if len(estimates) == len(VARIANTS):
            cells.append({"quarter": row.quarter, **estimates})
    out = []
    for variant in VARIANTS:
        for window, lower in (("W1", "2023Q1"), ("W2", "2024Q1")):
            errors = np.array([c[variant] for c in cells if c["quarter"] >= lower])
            out.append(dict(variant=variant, window=window, n=len(errors),
                            rmse_pct=float(np.sqrt(np.mean(errors**2))) if len(errors) else np.nan,
                            basis="retrospective_LOO_selection"))
    return pd.DataFrame(out)


def _variant(rows, variant):
    if variant is not None:
        if variant not in VARIANTS:
            raise ValueError(f"Unknown variant: {variant}")
        return variant
    table = _loo(rows)
    table = table[(table.window == "W1") & (table.n >= 8)].dropna(subset=["rmse_pct"])
    if table.empty:
        return "ex_covid"
    return str(table.sort_values("rmse_pct", kind="stable").iloc[0].variant)


def _regional(as_of, regional_gbv, regional_lambdas):
    if regional_gbv is None and regional_lambdas is None:
        return None, None
    if regional_gbv is None or regional_lambdas is None:
        raise DataUnavailable("Regional GBV and dated regional lambda coefficients must be supplied together by X")
    g = regional_gbv.copy()
    g["quarter"] = g.quarter.map(_quarter)
    if "print_date" not in g:
        g["print_date"] = g.quarter.map(_calendar())
    g = _dated(g, as_of, ["quarter", "region"], ["gbv_usd_booking_dated"])
    coefficients = regional_lambdas.copy(deep=True)
    coefficients["season"] = coefficients.season.map(_season)
    l = _dated(coefficients, as_of, ["region", "season"], ["lambda_pct"])
    if "lambda_sd_pct" in l:
        l["lambda_sd_pct"] = pd.to_numeric(l.lambda_sd_pct, errors="raise")
        if not np.isfinite(l.lambda_sd_pct).all() or (l.lambda_sd_pct < 0).any():
            raise ValueError("Regional lambda dispersion must be finite and nonnegative")
    if set(g.region) != set(l.region):
        raise ValueError("Regional GBV and lambda regions must match")
    return g, l


def lambda_table(as_of, *, panel=None, regional_gbv=None, regional_lambdas=None):
    """Historical identity table from printed observations; no predictions."""
    p = _panel(as_of, panel)
    g, l = _regional(as_of, regional_gbv, regional_lambdas)
    if g is not None:
        return l.copy()  # X owns regional lambda estimation.
    return _lambda_rows(p)[["quarter", "season", "print_date", "revenue_musd",
                            "gbv_l1", "gbv_l2", "base_musd", "lambda_pct"]]


def pit_lambda(season, as_of, variant=None, *, panel=None, regional_gbv=None, regional_lambdas=None):
    """Estimate in percent, with n and information cutoff; regional estimates supplied by X."""
    season = _season(season)
    p = _panel(as_of, panel)
    g, l = _regional(as_of, regional_gbv, regional_lambdas)
    if g is not None:
        r = l[l.season == int(season)]
        if set(r.region) != set(g.region):
            raise DataUnavailable("Missing a regional coefficient for the requested season")
        return dict(season=int(season), regions=r.to_dict("records"), lambda_pct=None,
                    n_train=len(r), knowable_from=_knowable(g, r),
                    aggregation="sum regional dollar revenue, never lambda coefficients")
    rows = _lambda_rows(p)
    chosen = _variant(rows, variant)
    lam, sample = _estimate(rows, season, chosen)
    return dict(lambda_pct=lam, season=int(season), variant=chosen, n_train=len(sample),
                training_quarters=sample.quarter.tolist(),
                knowable_from=sample.print_date.max().date().isoformat(),
                lambda_sd_pct=float(sample.lambda_pct.std(ddof=1)) if len(sample)>1 else np.nan)


def _bootstrap(sample, centre, draws=4000):
    if len(sample) < 2:
        return np.full(draws, np.nan)
    residuals = np.asarray(sample, dtype=float) - np.mean(sample)
    rng = np.random.default_rng(SEED)
    block = min(2, len(residuals))
    starts = rng.integers(0, len(residuals)-block+1, (draws, int(np.ceil(len(residuals)/block))))
    indices = (starts[:, :, None] + np.arange(block)).reshape(draws, -1)[:, :len(residuals)]
    # Estimation uncertainty plus a predictive residual; year blocks preserve adjacent same-season years.
    predictive = centre + residuals[indices].mean(axis=1) + rng.choice(residuals, draws)
    return np.maximum(predictive, np.finfo(float).eps)


def _quantiles(draws):
    return {key: (float(np.quantile(draws, prob)) if np.isfinite(draws).all() else np.nan)
            for key, prob in (("q05", .05), ("q10", .10), ("q25", .25), ("q50", .50),
                              ("q75", .75), ("q90", .90), ("q95", .95))}


def _forecast(q, as_of, p, g, l, variant=None, forecast_gbv=None):
    q = _quarter(q)
    if q in set(p.quarter):
        raise PointInTimeError("Target has already printed; use lambda_table for historical accounting")
    season = int(q[-1])
    rows = _lambda_rows(p)
    chosen = _variant(rows, variant)
    if g is not None:
        parts = []
        for region in sorted(g.region.unique()):
            a = g[g.region == region].set_index("quarter")
            coef = l[(l.region == region) & (l.season == season)]
            if len(coef) != 1:
                raise DataUnavailable(f"Missing {region} Q{season} lambda")
            if any(_shift(q, -k) not in a.index for k in (1, 2)):
                raise DataUnavailable(f"Missing printed regional GBV lags for {region} {q}")
            base = (WEIGHT*a.loc[_shift(q,-1), "gbv_usd_booking_dated"]+
                    (1-WEIGHT)*a.loc[_shift(q,-2), "gbv_usd_booking_dated"])/1e6
            lam = float(coef.iloc[0].lambda_pct)
            parts.append(dict(region=region, base_musd=float(base), lambda_pct=lam,
                              point=float(base*lam/100)))
        point = sum(r["point"] for r in parts)
        regional_draws = None
        bands = {"q50": point}
        if "lambda_sd_pct" in l:
            sd_by_region = l[l.season == season].set_index("region").lambda_sd_pct
            if not np.isfinite(sd_by_region).all() or (sd_by_region < 0).any():
                raise ValueError("Regional lambda dispersion must be finite and nonnegative")
            sd = sum(r["base_musd"]*float(sd_by_region[r["region"]])/100 for r in parts)
            regional_draws = np.maximum(0,point+np.random.default_rng(SEED).normal(0,sd,4000))
            bands = _quantiles(regional_draws)
        return dict(quarter=q, point=point, **bands, base_musd=sum(r["base_musd"] for r in parts),
                    regions=parts, n_train=len(l), variant="supplied_regional",
                    uncertainty_status="Perfect-positive-correlation regional Gaussian sensitivity when sd supplied; otherwise unavailable",
                    _draws=regional_draws)
    lam, sample = _estimate(rows, season, chosen)
    values = p.set_index("quarter").gbv_musd.to_dict()
    if forecast_gbv:
        values.update(forecast_gbv)
    needed = [_shift(q, -1), _shift(q, -2)]
    if any(k not in values for k in needed):
        raise DataUnavailable(f"GBV not printed strictly before {_date(as_of).date()}: {needed}")
    base = WEIGHT*values[needed[0]]+(1-WEIGHT)*values[needed[1]]
    draws = _bootstrap(sample.lambda_pct, lam)*base/100
    point = float(lam*base/100)
    return dict(quarter=q, point=point, **_quantiles(draws), base_musd=float(base),
                lambda_pct=lam, variant=chosen, n_train=len(sample),
                training_quarters=sample.quarter.tolist(), _draws=draws,
                bootstrap_block_years=min(2,len(sample)), bootstrap_draws=len(draws),
                uncertainty_status="descriptive small-sample predictive bootstrap")


def kernel_forecast(q, as_of, *, variant=None, panel=None, regional_gbv=None, regional_lambdas=None):
    """Forecast from printed GBV only; refuses an unprinted lag, including same-day letters."""
    p = _panel(as_of, panel)
    g, l = _regional(as_of, regional_gbv, regional_lambdas)
    result = _forecast(q, as_of, p, g, l, variant)
    result.pop("_draws")
    result.update(as_of=str(_date(as_of).date()), knowable_from=_knowable(p, g, l))
    return result


def _cushions(as_of, supplied=None, *, trailing=True):
    if supplied is None:
        f = pd.read_csv(ROOT / "data/processed/overnight/02_guidance_cushion_series.csv")
        f["quarter"] = f.target_period.map(_quarter)
        f = f.copy()
        f["print_date"] = f.quarter.map(_calendar())
        if f.print_date.isna().any():
            raise PointInTimeError("Missing cushion target publication date")
        f = f[f.print_date < _date(as_of)].copy()
        f["ratio"] = f.actual/f.value_mid
    else:
        f = supplied.copy()
        f["quarter"] = f.quarter.map(_quarter)
    f = _dated(f, as_of, ["quarter"], ["ratio"])
    f = f.sort_values("quarter")
    if trailing:
        f = f.tail(8)
    if f.empty:
        raise DataUnavailable("No realised guide cushion before as_of")
    return f


def kernel_guide(q, as_of, cushion="median", *, variant=None, panel=None,
                 cushion_frame=None, regional_gbv=None, regional_lambdas=None):
    """Forecast divided by trailing-eight realised actual/guide-mid ratios."""
    p = _panel(as_of, panel)
    g, l = _regional(as_of, regional_gbv, regional_lambdas)
    if cushion not in ("median", "mean"):
        raise ValueError("cushion must be median or mean")
    history = _cushions(as_of, cushion_frame, trailing=False)
    c = history.tail(8)
    divisor = float(c.ratio.median() if cushion == "median" else c.ratio.mean())
    f = _forecast(q, as_of, p, g, l, variant)
    draws = f.pop("_draws")
    point = f["point"]/divisor
    if draws is not None:
        rng = np.random.default_rng(SEED+1)
        sd = float(c.ratio.std(ddof=1)) if len(c)>1 else np.nan
        cushion_draws = np.maximum(rng.normal(divisor, sd, len(draws)), .01)
        f.update(_quantiles(draws/cushion_draws))
    if "regions" in f:
        f["regions"] = [dict(r, point=r["point"]/divisor) for r in f["regions"]]
        if draws is None:
            f["q50"] = point
    f.update(point=point, as_of=str(_date(as_of).date()), cushion=divisor-1,
             cushion_stat=cushion, cushion_n=len(c),
             knowable_from=_knowable(p, g, l, c))
    calibration = _calibration(p, history, variant, cushion) if g is None else {}
    errors = calibration.get("relative_errors", [])
    f["conformal_n_cal"] = len(errors)
    f["conformal_calibration_cells"] = calibration.get("cells", [])
    for coverage in (.5, .8):
        n = len(errors)
        k = int(np.ceil((n+1)*coverage))
        width = sorted(errors)[k-1]*point if n and k <= n else np.nan
        f[f"conformal_{int(coverage*100)}_lo"] = max(0., point-width) if np.isfinite(width) else np.nan
        f[f"conformal_{int(coverage*100)}_hi"] = point+width
    f["conformal_caveat"] = ("Chronological post-letter calibration; exchangeability not assumed; no coverage guarantee"
                              if g is None else "Unavailable: X must supply historical regional forecast residuals")
    return f


def _calibration(p, cushions, variant, cushion="median"):
    # Forecast origins are the day AFTER the preceding letter, never pre-guide alpha.
    errors = []
    cells = []
    for row in _lambda_rows(p).itertuples():
        prior = p[p.quarter == _shift(row.quarter,-1)]
        if prior.empty:
            continue
        origin = prior.iloc[0].print_date + pd.Timedelta(days=1)
        tr = p[p.print_date < origin]
        cr = cushions[cushions.print_date < origin].tail(8)
        if cr.empty:
            continue
        try:
            f = _forecast(row.quarter, origin, tr, None, None, variant)
        except DataUnavailable:
            continue
        # A guide observation is recoverable from realised revenue and its realised ratio.
        actual_ratio = cushions[cushions.quarter == row.quarter]
        if actual_ratio.empty:
            continue
        guide_actual = row.revenue_musd/float(actual_ratio.iloc[0].ratio)
        divisor = float(cr.ratio.median() if cushion == "median" else cr.ratio.mean())
        pred = f["point"]/divisor
        errors.append(abs(pred-guide_actual)/pred)
        cells.append(dict(quarter=row.quarter, origin=str(origin.date()),
                          known_from=str(row.print_date.date()), cushion_n=len(cr),
                          cushion_stat=cushion, pred=pred, actual=guide_actual))
    return dict(relative_errors=errors[-6:], cells=cells[-6:])


def _ledger_nowcasts(p, as_of):
    # Refit K1's UF-growth regression. Ramp shares are dated research scenarios, not disclosure.
    if _date(as_of) <= RNPL_SCENARIO_AVAILABLE:
        raise DataUnavailable("No pre-origin vintage of K1's RNPL ramp scenario; strict historical replay abstains")
    tree = ast.parse((ROOT / "analysis/src/forecast_methods/kernel_phi_v2/stage_d.py").read_text(encoding="utf-8"))
    shares = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)
                  and any(isinstance(t,ast.Name) and t.id == "RNPL_SHARE" for t in n.targets))
    if "unearned_fees_musd" not in p:
        raise DataUnavailable("Unearned-fees observations required for ledger nowcast")
    indexed = p.set_index("quarter")
    def growth(q, col):
        prior = _shift(q,-4)
        if q not in indexed.index or prior not in indexed.index:
            return np.nan
        return 100*(indexed.loc[q,col]/indexed.loc[prior,col]-1)
    def feature(q):
        prior = _shift(q,-1)
        return growth(prior,"unearned_fees_musd")+shares.get(prior,0)-shares.get(_shift(prior,-4),0)
    pairs = [(feature(q),growth(q,"gbv_musd")) for q in indexed.index]
    xy = np.array([v for v in pairs if np.isfinite(v).all()])
    if len(xy)<6 or np.ptp(xy[:,0]) == 0:
        raise DataUnavailable("Ledger regression requires six finite nonconstant training pairs")
    design = np.column_stack([np.ones(len(xy)),xy[:,0]])
    beta = np.linalg.lstsq(design,xy[:,1],rcond=None)[0]
    residual = xy[:,1]-design@beta
    sd = float(np.std(residual,ddof=2))
    first = _shift(max(indexed.index),1)
    x = feature(first)
    if not np.isfinite(x):
        raise DataUnavailable("Latest lagged unearned-fees growth unavailable")
    growth_hat = float(np.array([1,x])@beta)
    result = {}
    for step in (1,2):
        q = _shift(first,step-1)
        base_q = _shift(q,-4)
        if base_q not in indexed.index:
            raise DataUnavailable(f"Missing seasonal GBV anchor {base_q}")
        base = float(indexed.loc[base_q,"gbv_musd"])
        result[q] = dict(point=base*(1+growth_hat/100), sd=base*sd/100*np.sqrt(step),
                         n_train=len(xy), kind="RNPL-corrected ledger scenario" if step==1 else "recursive GBV-growth persistence scenario",
                         scenario_available=str(RNPL_SCENARIO_AVAILABLE.date()),
                         caveat="Undisclosed RNPL ramps; conditional scenario; fitted residual sd is not validated forecast coverage")
    return result


def term_structure(as_of, *, panel=None, regional_gbv=None, regional_lambdas=None):
    """Latest printed quarter +1/+2/+3; first two missing GBVs are labelled scenarios.

    At 12 Sep 2026 this reports Q3, Q4 and Q1. The latter two have missing GBV.
    Historical RNPL scenario vintages are unavailable and cause explicit abstention.
    """
    p = _panel(as_of, panel)
    g,l = _regional(as_of, regional_gbv, regional_lambdas)
    if p.empty:
        raise DataUnavailable("No printed panel before as_of")
    forecasts = None
    try:
        forecasts = _ledger_nowcasts(p,as_of) if g is None else None
        reason = "X must supply regional forecast inputs through its own nowcast layer"
    except DataUnavailable as exc:
        reason = str(exc)
    c = _cushions(as_of)
    divisor = float(c.ratio.median())
    out = []
    for step in (1,2,3):
        q = _shift(p.quarter.max(),step)
        values = {k:v["point"] for k,v in forecasts.items()} if forecasts else None
        try:
            f = _forecast(q,as_of,p,g,l,forecast_gbv=values)
            if step>1 and forecasts is None:
                raise DataUnavailable(reason)
            draw = f.pop("_draws")
            used = [(_shift(q,-1),WEIGHT),(_shift(q,-2),1-WEIGHT)]
            extra_sd = sum(w*forecasts[k]["sd"] for k,w in used if forecasts and k in forecasts)
            if draw is not None and extra_sd:
                # Fully positively correlated GBV forecast errors: do not assume diversification.
                rng=np.random.default_rng(SEED+2)
                draw=np.maximum(0,draw+rng.normal(0,extra_sd*f["lambda_pct"]/100,len(draw)))
                f.update(_quantiles(draw))
            row = {k:v for k,v in f.items() if not isinstance(v,(list,dict))}
            row.update(as_of=str(_date(as_of).date()), status="printed_lags" if step==1 else "conditional_scenario",
                       guide_mid_musd=f["point"]/divisor,
                       gbv_forecast_n=sum(k in (forecasts or {}) for k,_ in used),
                       caveat="" if step==1 else "RNPL ramp scenario; recursive growth for the second missing quarter; no validated forecast coverage")
            if draw is not None:
                csd = float(c.ratio.std(ddof=1)) if len(c)>1 else np.nan
                cdraw = np.maximum(np.random.default_rng(SEED+1).normal(divisor, csd, len(draw)), .01)
                row.update({"guide_"+k:v for k,v in _quantiles(draw/cdraw).items()})
            out.append(row)
        except DataUnavailable as exc:
            out.append(dict(quarter=q,as_of=str(_date(as_of).date()),status="unavailable",point=np.nan,
                            guide_mid_musd=np.nan,caveat=reason if step>1 else str(exc)))
    return pd.DataFrame(out)


def control_chart(as_of, *, panel=None, regional_gbv=None, regional_lambdas=None):
    """Within-season +/-2sd reference; historical alarms use prior cells only."""
    p = _panel(as_of,panel)
    g,l = _regional(as_of,regional_gbv,regional_lambdas)
    if g is not None:
        if "lambda_sd_pct" not in l:
            raise DataUnavailable("X must supply regional lambda dispersion for regional control limits")
        chart=l.copy()
        chart["lower"]=chart.lambda_pct-2*chart.lambda_sd_pct
        chart["upper"]=chart.lambda_pct+2*chart.lambda_sd_pct
        return dict(chart=chart,alarms=pd.DataFrame(),regional=True,
                    caveat="Regional dollar forecasts sum; coefficients and control limits do not")
    rows = _lambda_rows(p)
    w=rows[rows.quarter >= "2023Q1"]
    chart=[]
    alarms=[]
    for season, group in w.groupby("season"):
        centre=float(group.lambda_pct.mean())
        sd=float(group.lambda_pct.std(ddof=1)) if len(group)>1 else np.nan
        chart.append(dict(season=int(season),n=len(group),mean_pct=centre,sd_pct=sd,
                          lower=centre-2*sd,upper=centre+2*sd))
        for row in group.itertuples():
            tr=group[group.print_date < row.print_date]
            if len(tr)<2:
                continue
            m=float(tr.lambda_pct.mean()); s=float(tr.lambda_pct.std(ddof=1))
            alarms.append(dict(quarter=row.quarter,n_train=len(tr),actual_lambda_pct=row.lambda_pct,
                               lower=m-2*s,upper=m+2*s,alarm=bool(abs(row.lambda_pct-m)>2*s)))
    rule=None
    if _date(as_of)>RNPL_SCENARIO_AVAILABLE:
        lookup=p.set_index("quarter").gbv_musd.to_dict()
        if {"2026Q1","2026Q2"} <= set(lookup):
            rule=dict(quarter="2026Q3",base_musd=WEIGHT*lookup["2026Q2"]+(1-WEIGHT)*lookup["2026Q1"],
                      warn_below_lambda_pct=17.09,escalate_below_lambda_pct=16.93,
                      knowable_from=str(RNPL_SCENARIO_AVAILABLE.date()),
                      provenance="pre-registered K0/K1 card rule; separate from estimated limits")
    return dict(chart=pd.DataFrame(chart),alarms=pd.DataFrame(alarms),rule=rule,regional=False)
