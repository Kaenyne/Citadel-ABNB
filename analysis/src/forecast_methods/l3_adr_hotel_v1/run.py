"""Offline frozen ADRv3 reproduction and hotel comparator audit. No registrations."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data/processed/forecast_methods/l3_adr_hotel_v1"
AS_OF = "2026-09-13"
P = "data/processed/"
INPUTS = [
    "analysis/src/adrv3/S1_scoring.py", "analysis/src/adrv3/P1_card_v3.py",
    "analysis/src/overnight2/B4_application_3q26_4q26.py",
    P + "q3nowcast/H/adr_history_components.csv", P + "q3nowcast/H/adr_exfx_backtest.csv",
    P + "adr/15_seats_dilution_annual.csv", P + "adr/07_full_decomposition.csv",
    P + "adrq3/J/card_v2_backtest.csv", P + "adrq3/I/I_mix_terms_3q26.csv",
    P + "overnight2/B/B_adr_fx_estimator_backtest.csv",
    P + "adrv3/P/P1_card_v3_backtest.csv", P + "adrv3/P/P1_card_v3_backtest_paths.csv",
    P + "adrv3/P/adr_card_v3.csv", P + "adrv3/P/P1_card_v3_terms.csv",
    P + "adrv3/K/K3_rule_residual_paths.csv", P + "adrv3/K/K3_residual_fit.csv",
    P + "adrv3/K/K4_fee_lap_schedule.csv", P + "adrv3/K/K2_expected_effect_prestated.csv",
    P + "adrv3/L/L3_pass.csv", P + "adrv3/M/M5_criterion.csv",
    P + "adrv3/N/N1_fx_choice_card.csv", P + "hotel_price_monitor_monthly.csv",
    "data/raw/fred/CUSR0000SEHB.csv", "data/raw/bea/bea_pce_travel_monthly_2015_2026.csv",
    P + "hotel_13_market_panel/market_coverage.csv", P + "hotel_13_market_panel/summary.json",
    P + "hotel_13_market_panel/airbnb_registry_crosswalk_scoped.csv",
    P + "hotel_13_market_panel/airbnb_page_observations_scoped.csv",
    P + "hotel_13_market_panel/airbnb_property_clusters_scoped.csv",
]
MODELS = ["v3_last_q_measured_mix", "v3_point_last_q_plus_K_line_measured_mix"]
WINDOWS = {"ADR_2024Q1_2026Q2": ("2024Q1", "2026Q2"),
           "ADR_2024Q2_2026Q2": ("2024Q2", "2026Q2")}


def read(rel):
    return pd.read_csv(ROOT / rel)


def iso_quarter(q):
    return f"20{q[-2:]}Q{q[0]}"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rmse(a):
    a = np.asarray(a, dtype=float)
    return float(np.sqrt(np.mean(a * a))) if len(a) else np.nan


def paired_score(actual, prediction, baseline, half_width=0.0):
    """Pairwise finite coverage; intervals are a separate scoring sensitivity."""
    a, m, b = [np.asarray(x, dtype=float) for x in (actual, prediction, baseline)]
    if a.shape != m.shape or a.shape != b.shape or half_width < 0:
        raise ValueError("equal shapes and nonnegative interval width required")
    mask = np.isfinite(a) & np.isfinite(m) & np.isfinite(b)
    a, m, b = a[mask], m[mask], b[mask]
    em = np.maximum(np.abs(m - a) - half_width, 0.0)
    eb = np.maximum(np.abs(b - a) - half_width, 0.0)
    den = rmse(eb)
    ratio = rmse(em) / den if den > 0 else np.nan
    jk = []
    for i in range(len(a)):
        d = rmse(np.delete(eb, i))
        if d > 0:
            jk.append(rmse(np.delete(em, i)) / d)
    return {"n": len(a), "rmse_pp": rmse(em), "rmse_naive_pp": den,
            "ratio_vs_naive": ratio, "jackknife_ratio_min": min(jk) if jk else np.nan,
            "jackknife_ratio_max": max(jk) if jk else np.nan,
            "jackknife_n": len(jk), "jackknife_below_1": sum(v < 1 for v in jk),
            "baseline_status": "available" if den > 0 else "zero_or_missing_rmse"}


def complete_quarters(monthly):
    """Mean of monthly growth only when all three calendar months are observed."""
    d = monthly.copy()
    if d.month.duplicated().any():
        raise ValueError("duplicate months")
    d["quarter"] = pd.PeriodIndex(d.month, freq="M").asfreq("Q").astype(str)
    rows = []
    cols = [c for c in d if c not in ("month", "quarter")]
    for q, g in d.groupby("quarter", sort=True):
        row = {"quarter": q}
        for c in cols:
            n = int(g[c].notna().sum())
            row[c + "_months"] = n
            row[c] = float(g[c].mean()) if n == 3 else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def check_information_date(date, as_of=AS_OF):
    if pd.isna(date) or pd.Timestamp(date) > pd.Timestamp(as_of):
        raise ValueError("missing or future information date")


def validate_adapter(df):
    required = ["quarter", "metric", "scenario", "value", "lower", "upper", "units",
                "information_date", "evidence_status", "source_reference", "treatment",
                "baseline_replaced", "embedded_fx", "limitations"]
    if not set(required).issubset(df):
        raise ValueError("missing adapter fields")
    if df.duplicated(["quarter", "metric", "scenario"]).any():
        raise ValueError("duplicate adapter key")
    if not df.treatment.isin(["replacement", "incremental", "descriptive"]).all():
        raise ValueError("unknown treatment")
    for r in df.itertuples():
        check_information_date(r.information_date)
        if r.treatment == "replacement" and not r.baseline_replaced:
            raise ValueError("replacement without a baseline")
        if not r.embedded_fx or not r.limitations:
            raise ValueError("missing FX/double-counting limitations")
        if pd.notna(r.lower) and pd.notna(r.upper) and r.lower > r.upper:
            raise ValueError("reversed bounds")
        if r.metric == "revenue" or r.metric == "revenue_musd_same_q_take":
            raise ValueError("contemporaneous revenue cannot be exported as forecast")


def run(out):
    out = Path(out)
    if out.exists():
        raise FileExistsError("Use a new immutable output directory: " + str(out))
    out.mkdir(parents=True)
    before = {r: sha(ROOT / r) for r in INPUTS}
    checks = []
    def check(name, passed, n, detail):
        checks.append({"check": name, "passed": bool(passed), "n": int(n), "detail": str(detail)})
    def save(name, frame):
        frame.to_csv(out / name, index=False, float_format="%.12g", lineterminator="\n")

    spec = importlib.util.spec_from_file_location("l3_frozen_adr_scoring", ROOT / INPUTS[0])
    s = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s)
    h = read(P + "q3nowcast/H/adr_history_components.csv").set_index("quarter")
    kp = read(P + "adrv3/K/K3_rule_residual_paths.csv")
    kp = kp[kp.variant == "central"].set_index("quarter")
    paths = {MODELS[0]: s.v2_model_paths(str(ROOT))[s.V3_RULE_MODEL],
             MODELS[1]: s.exfx_from_residual(kp.K_mech_central, "measured", root=str(ROOT))}
    scores = pd.concat([s.score(v, k, "DESCRIPTIVE: realised target-quarter mix; fixed retrospective FX calibration", str(ROOT))
                        for k, v in paths.items()], ignore_index=True)
    original = read(P + "adrv3/P/P1_card_v3_backtest.csv")
    cols = ["n", "rmse_pp", "rmse_naive_pp", "ratio_vs_naive", "jackknife_ratio_min", "jackknife_ratio_max"]
    keys = ["model", "target", "window", "fx_estimator"]
    cmp = scores[keys + cols].merge(original[keys + cols], on=keys, validate="one_to_one", suffixes=("", "_frozen"))
    for c in cols:
        cmp[c + "_abs_diff"] = abs(cmp[c] - cmp[c + "_frozen"])
    diff = cmp[[c + "_abs_diff" for c in cols]].to_numpy().max()
    check("ADR P1 reproduction", len(cmp) == 16 and diff < 1e-9, len(cmp), f"max absolute delta {diff:.3g}")
    save("adr_score_reproduction.csv", cmp)
    save("adr_scores.csv", scores)
    jr, ok = s.reproduce_j3(str(ROOT))
    check("J3 reproduction", ok, len(jr), f"max delta {jr.max_abs_diff.max():.3g}")
    save("j3_reproduction.csv", jr)
    stored = read(P + "adrv3/P/P1_card_v3_backtest_paths.csv")
    independent = []
    for (target, est), g in stored.groupby(["target", "fx_estimator"], sort=False):
        for window in s.WINDOWS:
            gg = g if window.startswith("1Q24") else g[g.quarter != "1Q24"]
            for model in MODELS:
                row = {"model": model, "target": target, "window": window, "fx_estimator": est}
                row.update(paired_score(gg.actual, gg[model], gg.naive))
                independent.append(row)
    independent = pd.DataFrame(independent)
    ic = independent.merge(scores, on=keys, suffixes=("", "_S"), validate="one_to_one")
    idiff = max((ic[c] - ic[c + "_S"]).abs().max() for c in cols)
    check("independent path scoring", len(ic) == 16 and idiff < 1e-9, len(ic), f"max delta {idiff:.3g}")
    save("adr_independent_scores.csv", independent)
    interval = []
    for model, path in paths.items():
        tf = s.target_frame("t1_exfx_integer_fair", root=str(ROOT))
        for window in s.WINDOWS:
            t = tf if window.startswith("1Q24") else tf.drop("1Q24")
            interval.append({"model": model, "window": window,
                             "target": "exfx_interval_halfwidth_0.5_continuous_forecast",
                             **paired_score(t.actual, path.reindex(t.index), t.naive, 0.5)})
    save("adr_interval_sensitivity.csv", pd.DataFrame(interval))
    comp = ["geo_mix_pp", "unit_size_pp", "los_mix_pp", "new_business_pp", "interaction_pp"]
    hist = h.reset_index()[["quarter", "adr_exfx_yoy_pp", "residual_pricing_pp", "identity_check_pp"] + comp]
    hist["recomputed_residual_pp"] = hist.adr_exfx_yoy_pp - hist[comp].fillna(0).sum(axis=1)
    hist["residual_gap_pp"] = hist.recomputed_residual_pp - hist.residual_pricing_pp
    hist["unfilled_new_business"] = hist.new_business_pp.isna()
    check("historical residual identity", hist.residual_gap_pp.abs().max() < 1e-9, len(hist), hist.residual_gap_pp.abs().max())
    save("adr_historical_identity.csv", hist)
    kerr = (kp.K_mech_central - kp.last_q - 0.007 * kp.dd4share_pp).abs().max()
    check("K historical imposed mechanics", kerr < 1e-9, len(kp), kerr)
    rejected_l = read(P + "adrv3/L/L3_pass.csv")
    rejected_l = rejected_l[(rejected_l.model == "L_wf") & rejected_l.in_pass_criterion]
    rejected_m = read(P + "adrv3/M/M5_criterion.csv")
    rejected_m = rejected_m[rejected_m.variant == "entire_home_premium"]
    check("failed additions remain failed", len(rejected_l) == 4 and not rejected_l.beats_last_q_ratio.any()
          and len(rejected_m) == 1 and not rejected_m.M_criterion_met.any(), 5,
          "Regional primary 0/4; new-listing primary 2/4 improvements, criterion false")
    fits = read(P + "adrv3/K/K3_residual_fit.csv")
    fit = fits[(fits.variant == "central") & (fits.basis == "nights") &
               (fits.spec == "levels, no constant, baseline = 2023-25 mean")].iloc[0]
    identification = [
        ("quarter_t_mix", "realised current-quarter components used in historical score", "descriptive_upper_bound_not_PIT", "analysis/src/adrv3/S1_scoring.py:v2_components"),
        ("FX_euro", "fixed intercept -0.5687, slope 0.4512 from ex21 n17 calibration reused backward", "retrospective_fixed_fit_not_walk_forward", "analysis/src/overnight2/B4_application_3q26_4q26.py:ADR_FX_EUR"),
        ("FX_baskets", "FY2025 regional GBV shares and fixed regional pass-through reused backward", "retrospective_weights_not_historical_vintages", "analysis/src/overnight2/B4_application_3q26_4q26.py:GBV_SHARE_2025"),
        ("K_fit", f"coefficient {fit.coef_pp_per_pp_share:.12g}; {fit.ratio_to_expected_central:.12g} times imposed central mechanics; n={fit.n}", "rejected_as_fee_mechanism", "data/processed/adrv3/K/K3_residual_fit.csv"),
        ("K_path", "Call-calibrated listing shares converted using assumed nights-per-listing and geography; not measured nights cohorts", "assumption_not_identified_pass_through", "research/notes/adrv3/K_residual-decomposition-fee-migration.md"),
        ("half_point_history", "3Q23/4Q23 ex-FX are 0.5; 1Q24 naive is 0.5; score preserves frozen values", "not_all_history_is_integer", "data/processed/q3nowcast/H/adr_history_components.csv"),
        ("fx_identity", f"max reported-minus-exFX-minus-FX identity gap {h.identity_check_pp.abs().max():.12g} pp; tight identity partly constructed", "not_independent_FX_measurement", "research/notes/adrv3/S_scoring-harness-and-v3-preregistration.md"),
        ("selection", "last_q selected after seeing J3 sensitivity table, then preregistered for v3", "post_hoc_rule_selection_disclosed", "docs/adrv3/SYNTHESIS.md"),
        ("bands", "RSS of component half-ranges around point; no fitted joint error distribution or probabilities", "scenario_band_not_confidence_interval", "analysis/src/adrv3/P1_card_v3.py"),
    ]
    save("adr_identification_audit.csv", pd.DataFrame(identification, columns=["item", "finding", "evidence_status", "source_reference"]))

    terms = read(P + "adrv3/P/P1_card_v3_terms.csv")
    terms = terms[terms.in_point].copy()
    card = read(P + "adrv3/P/adr_card_v3.csv")
    audit, adapter = [], []
    def emit(q, metric, scenario, value, low=np.nan, high=np.nan, units="percentage_points", treatment="descriptive",
             evidence="scenario_assumption_research_only", source="data/processed/adrv3/P/adr_card_v3.csv", baseline="none",
             fx="none in this component", limits="Scenario only; no investment adoption; do not sum alternate scenarios."):
        adapter.append(dict(quarter=iso_quarter(q) if len(q) == 4 else q, metric=metric, scenario=scenario,
                            value=value, lower=low, upper=high, units=units, information_date=AS_OF,
                            evidence_status=evidence, source_reference=source, treatment=treatment,
                            baseline_replaced=baseline, embedded_fx=fx, limitations=limits))
    lap = read(P + "adrv3/K/K4_fee_lap_schedule.csv")
    lap = lap[lap.variant == "central"].set_index("quarter")
    nfx = read(P + "adrv3/N/N1_fx_choice_card.csv").set_index(["quarter", "fx_estimator"])
    for (q, variant), g in terms.groupby(["quarter", "variant"], sort=False):
        exfx = g.point_pp.sum()
        half = np.sqrt(np.square((g.hi_pp - g.lo_pp) / 2).sum())
        if variant == "v3_with_K":
            k = g[g.term == "fee_migration_mechanics_K"].iloc[0]
            delta = lap.loc[q, "yoy_change_pp"] - lap.loc["2Q26", "yoy_change_pp"]
            check("K live chain " + q, abs(k.point_pp - 0.007 * delta) < 1e-9 and abs(k.hi_pp - 0.038 * delta) < 1e-9, 1, f"share delta={delta}; point={k.point_pp}")
        for r in g.itertuples():
            emit(q, "adr_component_" + r.term, variant, r.point_pp, r.lo_pp, r.hi_pp,
                 source="data/processed/adrv3/P/P1_card_v3_terms.csv; " + r.source,
                 evidence="assumed_or_proxy_component: " + r.label,
                 limits="Component of named ADR scenario, already included in total. Residual absorbs omitted mix; not measured like-for-like pricing. Q4 mix is carried from Q3.")
        rows = card[(card.quarter == q) & (card.variant == variant)]
        for r in rows.itertuples():
            fx = nfx.loc[(q, r.fx_estimator), "fx_effect_pp"]
            rep, adr = exfx + fx, r.base_adr_usd * (1 + (exfx + fx) / 100)
            gbv = adr * r.nights_m / 1000
            vals = {"exfx": (exfx, r.adr_exfx_yoy_pp, .005), "reported": (rep, r.adr_reported_yoy_pp, .005),
                    "adr": (adr, r.adr_usd_point, .005), "gbv": (gbv, r.gbv_busd_point, .005),
                    "revenue_comparison": (gbv * 1000 * r.take_rate_same_q_prior_year, r.revenue_musd_same_q_take, .5),
                    "central_lower": (exfx - half + fx, r.adr_reported_central_lo_pp, .005),
                    "central_upper": (exfx + half + fx, r.adr_reported_central_hi_pp, .005)}
            for metric, (rebuild, frozen, tolerance) in vals.items():
                audit.append(dict(quarter=q, variant=variant, fx=r.fx_estimator, nights_case=r.nights_case,
                                  metric=metric, rebuilt=rebuild, frozen=frozen, difference=rebuild-frozen,
                                  tolerance=tolerance, passed=abs(rebuild-frozen) <= tolerance + 1e-9))
            scenario = f"{variant}__{r.fx_estimator}"
            if r.nights_case == rows[rows.fx_estimator == r.fx_estimator].nights_case.iloc[0]:
                common = dict(treatment="replacement", baseline="L4 ADR for same quarter; do not replace revenue or its FX layer",
                              limits="Conditional component scenario; current-quarter mix backtest is retrospective. Bounds are RSS sensitivity ranges, not probabilistic intervals. Original source snapshot 2026-09-11; audited 2026-09-13.")
                emit(q, "adr_exfx_yoy", scenario, exfx, exfx-half, exfx+half, fx="FX excluded; add exactly one ADR FX bridge", **common)
                emit(q, "adr_reported_yoy", scenario, rep, rep-half, rep+half, fx=f"Includes ADR FX {fx:+.6g} pp ({r.fx_estimator}); do not add full FX again", **common)
                emit(q, "adr_usd", scenario, adr, r.base_adr_usd*(1+(rep-half)/100), r.base_adr_usd*(1+(rep+half)/100),
                     units="USD_per_night", fx=f"USD base ADR already translated; includes current ADR FX {fx:+.6g} pp", **common)
            emit(q, "gbv_identity_comparison", scenario + "__" + r.nights_case, gbv, units="USD_billions",
                 evidence="descriptive_identity_on_unadopted_nights_scenario", fx=f"Includes reported ADR FX {fx:+.6g} pp",
                 limits=f"Nights={r.nights_m} million; same-quarter GBV identity only. Feed lagged kernel only through L4. Same-quarter take-rate revenue is deliberately omitted.")
    audit = pd.DataFrame(audit)
    check("live card arithmetic", audit.passed.all(), len(audit), f"failed={int((~audit.passed).sum())}")
    save("adr_card_identity.csv", audit)

    cpi = read("data/raw/fred/CUSR0000SEHB.csv")
    cpi["value"] = pd.to_numeric(cpi.CUSR0000SEHB, errors="coerce")
    cpi["month"] = cpi.observation_date.str[:7]
    bea = read("data/raw/bea/bea_pce_travel_monthly_2015_2026.csv")
    bea = bea[(bea.series == "hotels_motels") & (bea.measure == "price_index_2017eq100")].copy()
    bea["month"] = bea.date.str[:7]
    monthly = None
    for d, col in [(cpi, "cpi_lodging_yoy_pct"), (bea, "bea_hotels_price_yoy_pct")]:
        if d.month.duplicated().any():
            raise ValueError("duplicate raw hotel price month")
        levels = d.set_index("month").value.astype(float)
        frame = pd.DataFrame({"month": levels.index, col: [100*(v/levels.get(f"{int(m[:4])-1}{m[4:]}", np.nan)-1) for m, v in levels.items()]})
        monthly = frame if monthly is None else monthly.merge(frame, on="month", how="outer", validate="one_to_one")
    monthly = monthly[monthly.month >= "2023-01"].sort_values("month").reset_index(drop=True)
    legacy = read(P + "hotel_price_monitor_monthly.csv")
    mc = monthly.merge(legacy, on="month", suffixes=("", "_frozen"), validate="one_to_one")
    for c in ["cpi_lodging_yoy_pct", "bea_hotels_price_yoy_pct"]:
        finite = mc[c].notna() & mc[c + "_frozen"].notna()
        err = (mc.loc[finite, c] - mc.loc[finite, c + "_frozen"]).abs().max()
        same = (mc[c].isna() == mc[c + "_frozen"].isna()).all()
        check("hotel monitor reproduction " + c, same and err <= .051, finite.sum(), f"max rounding delta={err}")
    save("hotel_monthly_comparators.csv", monthly)
    quarters = complete_quarters(monthly)
    hh = h.reset_index()[["quarter", "adr_exfx_yoy_pp", "adr_yoy_reported_pp"]]
    hh["quarter"] = hh.quarter.map(iso_quarter)
    quarters = quarters.merge(hh, on="quarter", how="left", validate="one_to_one")
    save("hotel_quarterly_comparators.csv", quarters)
    associations = []
    windows = {"history_2023Q1_2026Q2": ("2023Q1", "2026Q2"), **WINDOWS}
    for name, (start, end) in windows.items():
        d = quarters[(quarters.quarter >= start) & (quarters.quarter <= end)]
        for x in ["cpi_lodging_yoy_pct", "bea_hotels_price_yoy_pct"]:
            for y in ["adr_exfx_yoy_pp", "adr_yoy_reported_pp"]:
                for transform in ["growth_level", "change_in_growth"]:
                    z = d[[x,y]].copy()
                    if transform == "change_in_growth":
                        # Diff on the calendar-aligned frame BEFORE dropping missing quarters.
                        z = z.diff()
                    z = z.dropna()
                    j = [z.drop(i)[x].corr(z.drop(i)[y]) for i in z.index] if len(z) >= 4 else []
                    associations.append(dict(window=name, comparator=x, abnb_target=y, transform=transform, n=len(z),
                                             pearson=z[x].corr(z[y]), spearman=z[x].corr(z[y], method="spearman"),
                                             drop_one_min=min(j) if j else np.nan, drop_one_max=max(j) if j else np.nan,
                                             evidence_status="descriptive_same_period_archived_vintage_no_causality"))
    save("hotel_associations.csv", pd.DataFrame(associations))
    for c, url in [("cpi_lodging_yoy_pct", "https://fred.stlouisfed.org/series/CUSR0000SEHB"),
                   ("bea_hotels_price_yoy_pct", "https://apps.bea.gov/national/Release/XLS/Underlying/Section2All_xls.xlsx")]:
        for r in quarters[quarters.quarter >= "2026Q1"].itertuples():
            v, n = getattr(r, c), getattr(r, c+"_months")
            emit(r.quarter, "hotel_comparator_"+c, "archived_public_snapshot", v,
                 source=url+"; data/processed/forecast_methods/l3_adr_hotel_v1/hotel_quarterly_comparators.csv",
                 evidence="descriptive_complete_quarter" if n == 3 else "missing_incomplete_quarter",
                 limits=f"{n}/3 months. US category price index; not measured Airbnb pricing. Frozen history without release-vintage reconstruction. Incomplete-quarter value remains missing.")
    coverage = read(P + "hotel_13_market_panel/market_coverage.csv")
    pages = read(P + "hotel_13_market_panel/airbnb_page_observations_scoped.csv")
    clusters = read(P + "hotel_13_market_panel/airbnb_property_clusters_scoped.csv")
    cross = read(P + "hotel_13_market_panel/airbnb_registry_crosswalk_scoped.csv")
    accepted = cross[cross.accepted_roomcount_link == True]
    cs = {"markets": len(coverage), "markets_with_page_captures": int((coverage.airbnb_pages_observed_in_existing_capture > 0).sum()),
          "existing_page_observations": len(pages), "existing_property_clusters": len(clusters),
          "accepted_registered_room_matches": len(accepted), "registered_rooms": float(accepted.registered_physical_rooms.sum()),
          "markets_with_absolute_airbnb_hotel_nights": int(coverage.actual_airbnb_hotel_nights.notna().sum()),
          "markets_with_absolute_airbnb_hotel_revenue": int(coverage.actual_airbnb_hotel_revenue_usd.notna().sum()),
          "markets_with_current_verified_independent_rooms": int(coverage.current_verified_independent_rooms.notna().sum()),
          "capacity_total": None, "reason": "Mixed room/license/property units, vintages and geographies; no defensible sum. Hotel onboarding demand unidentified."}
    frozen = json.loads((ROOT / (P+"hotel_13_market_panel/summary.json")).read_text())
    check("hotel coverage reproduction", cs["markets"] == 13 and cs["existing_page_observations"] == frozen["existing_page_captures_in_scope"]
          and len(clusters) == frozen["existing_property_clusters_in_scope"] and len(accepted) == frozen["accepted_registered_room_matches_in_scope"]
          and cs["registered_rooms"] == frozen["registered_rooms_in_accepted_matches"], 13, json.dumps(cs))
    (out / "hotel_coverage.json").write_text(json.dumps(cs, indent=2)+"\n", encoding="utf-8")
    save("hotel_market_coverage.csv", coverage[["market", "capacity_metric", "capacity_unit", "observation_period", "source_geography", "source_url",
         "actual_airbnb_hotel_nights", "actual_airbnb_hotel_revenue_usd", "current_verified_independent_rooms", "limitations"]])
    ad = pd.DataFrame(adapter)
    validate_adapter(ad)
    save("l4_adr_hotel_inputs.csv", ad)
    check("L4 adapter contract", True, len(ad), "Alternates not additive; no revenue forecast; dates and FX fields verified")
    after = {r: sha(ROOT/r) for r in INPUTS}
    check("source files unchanged", before == after, len(before), "SHA-256 before/after")
    save("source_manifest.csv", pd.DataFrame([{"path": r, "sha256": before[r], "after_sha256": after[r], "audit_information_date": AS_OF} for r in INPUTS]))
    save("checks.csv", pd.DataFrame(checks))
    results = {"implementation": "PASS" if all(c["passed"] for c in checks) else "FAIL",
               "adr_descriptive_research": {m: s.preregistered_pass(scores, m)["verdict"] for m in MODELS},
               "adr_pit_forecast_evidence": "NOT ESTABLISHED: realised mix and retrospective fixed FX calibration",
               "fees": "K imposed mechanics only; cohort calibration and causal pass-through unidentified",
               "hotel_comparator_forecast_or_demand_edge": "NOT ESTABLISHED",
               "investment_adoption": "PENDING TEAM; no card/nights/forecast adopted",
               "l4_rows": len(ad), "source_count": len(before), "checks": len(checks)}
    (out/"summary.json").write_text(json.dumps(results, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(results, indent=2))
    return 0 if results["implementation"] == "PASS" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True, help="New immutable output directory; must not exist")
    args = parser.parse_args()
    raise SystemExit(run(args.out))
