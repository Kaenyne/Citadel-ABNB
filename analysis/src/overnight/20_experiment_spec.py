"""20_experiment_spec.py -- audit finding A03: a frozen, machine-readable experiment specification,
a data-vintage register, and an incremental-value table computed on identical events.

A03 items implemented
  1. 20_experiment_spec.json    primary candidate features (<=8), primary targets and horizons,
                                transformations, weights, minimum training size, missing-data policy,
                                evaluation windows and the baselines allowed for each target.
                                Frozen 6 Sep 2026, before the 5 Nov 2026 print. Also carries the
                                pointer to the SEPARATE exploratory ledger.
  2. 20_vintage_register.csv    for every series in the spec: publication lag, whether the historical
                                vintage can be reconstructed, the lag actually applied, and an
                                explicit approximation label where it cannot.
  3. 20_incremental_value.csv   baseline vs baseline + feature on IDENTICAL events, for both
                                evaluation windows (2023Q1+ and 2024Q1+).
     20_funds_held_windows.csv  the funds-held-for-clients case shown in both windows side by side,
                                with the training-start effect separated from the evaluation-window
                                effect, so no one can pair n from one window with a ratio from the
                                other.

READS  data/processed/overnight/08_panel_quarterly.csv, 20_pre_earnings_forecasts.csv,
       data/processed/predictive/02_peer_prints.csv
WRITES data/processed/overnight/20_experiment_spec.json, 20_vintage_register.csv,
       20_incremental_value.csv, 20_funds_held_windows.csv
Run: py -3.13 analysis/src/overnight/20_experiment_spec.py   (after 20_temporal_validation.py)
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
PROC = ROOT / "data/processed"
OUT = PROC / "overnight"
OUT.mkdir(parents=True, exist_ok=True)

FREEZE_DATE = "2026-09-06"
NEXT_PRINT = "2026-11-05"


# --------------------------------------------------------------------- 1. the spec
SPEC = {
    "spec_id": "ABNB-WS20-v1",
    "frozen_at": FREEZE_DATE,
    "frozen_before": {"event": "ABNB Q3 2026 print", "date": NEXT_PRINT,
                      "note": "no feature, transformation, weight or window below may be changed "
                              "after this date without incrementing spec_id and re-freezing; a "
                              "changed spec makes the 5 Nov observation exploratory, not prospective"},
    "written_by": "analysis/src/overnight/20_experiment_spec.py",
    "audit_finding": "A03 (window sensitivity, multiple testing, data vintage)",
    "primary_targets": [
        {"name": "nights_surprise_pct", "definition": "100*(actual nights - Street consensus nights)/consensus",
         "horizon": "the next ABNB print", "source": "data/processed/overnight/16_reaction_panel.csv",
         "n_available": 19,
         "allowed_baselines": ["zero", "last_quarter", "prior_year", "ar1", "expanding_mean",
                               "trailing4_mean", "trailing8_mean"],
         "baselines_not_applicable": ["guide", "guide_plus_cushion"],
         "why_not": "ABNB gives no numeric nights guide; nights guidance is qualitative"},
        {"name": "revenue_surprise_pct", "definition": "100*(actual revenue - Street consensus revenue)/consensus",
         "horizon": "the next ABNB print", "source": "data/processed/overnight/16_reaction_panel.csv",
         "n_available": 23,
         "allowed_baselines": ["zero", "last_quarter", "prior_year", "ar1", "expanding_mean",
                               "trailing4_mean", "trailing8_mean", "guide", "guide_plus_cushion"]},
        {"name": "open_5d_pct", "definition": "ABNB minus QQQ, OPEN of the reaction session to the "
                                              "close of the 5th session (reaction session = 1)",
         "horizon": "5 trading sessions after the release",
         "source": "data/processed/overnight/20_executable_returns.csv",
         "allowed_baselines": ["zero", "last_quarter", "expanding_mean", "trailing4_mean"]},
        {"name": "open_20d_pct", "definition": "same, to the close of the 20th session",
         "horizon": "20 trading sessions after the release",
         "source": "data/processed/overnight/20_executable_returns.csv",
         "allowed_baselines": ["zero", "last_quarter", "expanding_mean", "trailing4_mean"]},
    ],
    "baseline_note": "trailing4_mean and trailing8_mean are mandatory. The full expanding mean of a "
                     "surprise series beginning in 2021 is dominated by the COVID-rebound surprises "
                     "(+16.1%, +24.2%), so any model that is effectively an intercept shift beats it "
                     "trivially. pred_sd_over_actual_sd in 20_task_summary.csv flags such models.",
    "primary_candidate_features": [
        {"name": "f_prior_surprise", "transform": "lag 1 of the same surprise", "family": "autoregressive",
         "available_at_cutoff": "the prior print"},
        {"name": "f_surprise_trail4", "transform": "mean of the same surprise over t-4..t-1",
         "family": "autoregressive", "available_at_cutoff": "the prior print"},
        {"name": "f_guide_vs_street_lag1", "transform": "guide midpoint vs Street for quarter t, as "
                                                        "published at print t-1", "family": "guidance",
         "available_at_cutoff": "the prior print"},
        {"name": "f_guide_cushion_trail4", "transform": "mean revenue actual-vs-guide-midpoint over "
                                                        "t-4..t-1", "family": "guidance",
         "available_at_cutoff": "the prior print"},
        {"name": "pr_hotel_revpar_yoy_pit", "transform": "mean RevPAR y/y of MAR and HLT, restricted "
                                                         "to the peers whose report date precedes the "
                                                         "ABNB print", "family": "peer",
         "available_at_cutoff": "1-15 days before the print, when a peer reported first"},
        {"name": "bl_funds_yoy_lag1", "transform": "y/y of funds held for clients at end of t-1",
         "family": "backlog", "available_at_cutoff": "10-Q filed at the prior print"},
        {"name": "eu_platform_yoy_lag1", "transform": "y/y of Eurostat EU27 platform nights for t-1",
         "family": "alt-data", "available_at_cutoff": "~3 months after quarter t-1 ends"},
        {"name": "ia_reviews_ltm_matched_yoy", "transform": "y/y of matched-listing LTM reviews across "
                                                            "the fixed Inside Airbnb city set",
         "family": "alt-data", "available_at_cutoff": "dump date, 1-8 weeks before the print"},
    ],
    "post_release_features": ["nights_surprise_pct", "revenue_surprise_pct", "guide_vs_street_pct"],
    "weights": "equal; single-feature OLS with an intercept. No feature weighting, no feature "
               "selection inside the evaluation loop, no shrinkage, no interaction terms.",
    "min_training_size": 8,
    "fitting_scheme": "expanding window, chronological; the fit for event t uses only events "
                      "strictly earlier than t",
    "missing_data_policy": "listwise. An event with a missing feature or a missing label is skipped, "
                           "never imputed and never forward-filled. Every table reports n after "
                           "filters. A quarter with no Inside Airbnb dump or no Common Crawl crawl "
                           "stays missing.",
    "evaluation_windows": {"2023Q1+": "evaluated events from 2023Q1", "2024Q1+": "evaluated events from 2024Q1",
                           "rule": "both windows are reported for every headline. Never pair n from "
                                   "one window with a ratio from another."},
    "entry_convention_for_return_targets": "OPEN of the first session after the release. The "
                                           "pre-release close is not transactable with knowledge of "
                                           "the released numbers and is reported only as 'legacy'.",
    "decision_rule": "a feature is reported as adding value only if its walk-forward RMSE is below "
                     "EVERY allowed baseline for that target, on identical events, in BOTH windows.",
    "multiple_testing": {
        "primary_tests_planned": "8 features x 2 surprise targets + 3 features x 2 return targets = 22 "
                                 "primary model/target pairs, each reported in 3 windows",
        "note": "no p-value in this specification is corrected for multiplicity; a single surviving "
                "pair out of 22 is what one expects by chance at a 5% threshold. The out-of-sample "
                "RMSE ratio, not a p-value, is the decision rule."},
    "exploratory_ledger": {
        "pointer": ["data/processed/overnight/08_feature_tests_all.csv",
                    "data/processed/overnight/08_index_backtests.csv",
                    "data/processed/overnight/04_reaction_tests.csv",
                    "data/processed/overnight/16_reaction_tests.csv",
                    "data/processed/overnight/09_test_ledger.csv"],
        "status": "EXPLORATORY. 598 alt-data test rows and 97 reaction specifications. Results there "
                  "may be quoted as hypothesis generation only, never as validated forecasts."},
    "prospective_record": "data/processed/overnight/20_frozen_q3_2026.csv",
    "prediction_ledger": "data/processed/overnight/20_prediction_ledger.csv",
    "leakage_check": "data/processed/overnight/20_perturbation_check.csv",
}


# --------------------------------------------------------------------- 2. vintage register
VINTAGE = [
    dict(series="ABNB reported KPIs and revenue (8-K Ex.99.1 shareholder letter)",
         file="data/raw/letters/, data/processed/abnb_driver_history_quarterly.csv",
         native_freq="quarterly", release_lag_days="33-46 after quarter end (the print date)",
         vintage_reconstructible="yes", how="the print date IS the release; no revisions to the KPIs",
         lag_applied="none needed", approximation_label="exact"),
    dict(series="Street revenue consensus at the print (LSEG/Refinitiv or Zacks via CNBC/Reuters)",
         file="data/processed/overnight/04_consensus_sources.csv",
         native_freq="per print", release_lag_days="0 (quoted in the print-day article)",
         vintage_reconstructible="yes for 21 of 23 prints", how="print-day news article carries the "
         "number as of that morning", lag_applied="none",
         approximation_label="2 prints rely on a Zacks estimates page retrieved 2026-09-04; those "
                             "rows are supplementary and are not the primary consensus"),
    dict(series="Street nights consensus (StreetAccount via CNBC)",
         file="data/processed/overnight/04_consensus_sources.csv", native_freq="per print",
         release_lag_days="0", vintage_reconstructible="yes for the 19 prints where a print-day "
         "article quotes it", how="print-day article", lag_applied="none",
         approximation_label="4 prints have no retrievable nights consensus and are dropped, not imputed"),
    dict(series="Revenue guide midpoint and range", file="data/processed/abnb_revenue_guidance_vs_actual.csv",
         native_freq="quarterly", release_lag_days="0 (given in the prior shareholder letter)",
         vintage_reconstructible="yes", how="the guide is in the letter of the prior print",
         lag_applied="lag 1 print", approximation_label="exact"),
    dict(series="Funds held for clients, unearned fees (XBRL 10-Q/10-K)",
         file="data/raw/xbrl/ABNB_companyfacts.json, data/processed/abnb_backlog_indicators.csv",
         native_freq="quarterly", release_lag_days="0-3 after the print (10-Q filed same week)",
         vintage_reconstructible="partially", how="EDGAR carries filing dates, but companyfacts "
         "returns the CURRENTLY reported value, so a later restatement would silently replace the "
         "originally filed figure", lag_applied="1 full quarter (bl_*_lag1)",
         approximation_label="APPROXIMATION: as-currently-reported values, no restatement vintage. "
                             "Balance-sheet cash items of this kind are rarely restated, but this "
                             "has not been verified filing by filing."),
    dict(series="Eurostat tour_ce_omr platform nights (EU27)",
         file="data/raw/eurostat/, data/processed/eurostat_platform_nights_monthly.csv",
         native_freq="monthly", release_lag_days="~90 after month end, with later revisions",
         vintage_reconstructible="no", how="our pull is the current vintage; Eurostat revises back "
         "series and we did not archive prior vintages",
         lag_applied="1 full quarter (eu_platform_yoy_lag1); the lag-0 variant is flagged "
                     "not-available-before-print in 08_feature_tests_all.csv",
         approximation_label="APPROXIMATION: current-vintage series used as if it were the "
                             "point-in-time series. The one-quarter lag is the conservative control."),
    dict(series="Marriott / Hilton RevPAR y/y", file="data/processed/predictive/02_peer_prints.csv",
         native_freq="quarterly", release_lag_days="report dates recorded per quarter",
         vintage_reconstructible="yes", how="peer report dates and ABNB lead days are in the file",
         lag_applied="none, but the PIT feature drops any peer whose lead_days <= 0",
         approximation_label="exact, after the point-in-time correction in 20_temporal_validation.py"),
    dict(series="Inside Airbnb listing dumps", file="data/raw/inside_airbnb/, "
         "data/processed/overnight/08_ia_city_yoy.csv", native_freq="irregular monthly/quarterly",
         release_lag_days="dump date known exactly", vintage_reconstructible="yes for the dump date",
         how="each dump is a dated snapshot", lag_applied="none; dumps precede the print by 1-8 weeks",
         approximation_label="CAVEAT (audit A04): partial snapshots contaminate some y/y comparisons. "
                             "Coverage flags must be respected; the matched-listing series is the "
                             "safer one and is what the spec uses."),
    dict(series="Common Crawl listing survival", file="data/processed/cc_listing_survival.csv",
         native_freq="per crawl", release_lag_days="crawl date known", vintage_reconstructible="yes",
         how="crawl dates are in the file",
         lag_applied="none; not in the primary set",
         approximation_label="CAVEAT (audit A05): crawls do not cover every quarter; the y/y is now "
                             "computed on a contiguous quarterly index so a gap stays missing"),
    dict(series="Google Trends", file="data/processed/overnight/08_trends_weekly.csv",
         native_freq="weekly", release_lag_days="~2 days", vintage_reconstructible="no",
         how="Google renormalises the whole history on every pull, so today's history is not the "
             "history a 2023 decision-maker saw", lag_applied="n/a",
         approximation_label="EXCLUDED FROM THE PRIMARY SET for exactly this reason; kept in the "
                             "exploratory ledger only"),
    dict(series="FRED macro (DTWEXBGS, ICSA, CUSR0000SEHB)", file="data/processed/overnight/05_fred_cache",
         native_freq="daily/weekly/monthly", release_lag_days="1-30",
         vintage_reconstructible="in principle via ALFRED; not done here",
         how="ALFRED archives FRED vintages", lag_applied="none; not in the primary set",
         approximation_label="APPROXIMATION: current vintage. DTWEXBGS and ICSA are essentially "
                             "unrevised; CPI lodging is revised through seasonal factors."),
    dict(series="BEA hotel spend and price", file="data/raw/bea/",
         native_freq="monthly", release_lag_days="~30, revised for years",
         vintage_reconstructible="no (our pull is current vintage)", how="-",
         lag_applied="none; not in the primary set",
         approximation_label="APPROXIMATION: current vintage; materially revised series, so any "
                             "result using it is exploratory"),
    dict(series="ABNB and QQQ daily OHLC", file="data/processed/overnight/20_prices_ohlc.csv (yfinance)",
         native_freq="daily", release_lag_days="0", vintage_reconstructible="yes",
         how="prices are not revised; ABNB pays no dividend and has not split",
         lag_applied="none", approximation_label="exact"),
]


# --------------------------------------------------------------------- 3. incremental value
def ols(X, y):
    X = np.asarray(X, float)
    b, *_ = np.linalg.lstsq(np.column_stack([np.ones(len(X)), X]), np.asarray(y, float), rcond=None)
    return b


def rmse(p, a):
    p, a = np.asarray(p, float), np.asarray(a, float)
    m = ~(np.isnan(p) | np.isnan(a))
    return float(np.sqrt(np.mean((p[m] - a[m]) ** 2))) if m.sum() else np.nan


def incremental(panel, feature, target, train_start, eval_start, min_train=8):
    """M0 = AR(1) on the target. M1 = AR(1) + feature. Expanding, same events, same training start.
    Also scores the two model-free baselines (last quarter, prior year) on those same events."""
    d = panel.loc[train_start:].copy()
    d["lag1"] = d[target].shift(1)
    d["lag4"] = d[target].shift(4)
    rows = []
    for t in d.index:
        if t < eval_start:
            continue
        if pd.isna(d.at[t, target]) or pd.isna(d.at[t, feature]) or pd.isna(d.at[t, "lag1"]):
            continue
        tr = d.loc[d.index < t, [target, "lag1", feature]].dropna()
        if len(tr) < min_train:
            continue
        b0 = ols(tr[["lag1"]].values, tr[target].values)
        b1 = ols(tr[["lag1", feature]].values, tr[target].values)
        rows.append(dict(q=str(t), actual=d.at[t, target],
                         pred_m0=float(b0[0] + b0[1] * d.at[t, "lag1"]),
                         pred_m1=float(b1[0] + b1[1] * d.at[t, "lag1"] + b1[2] * d.at[t, feature]),
                         naive=d.at[t, "lag1"], prior_year=d.at[t, "lag4"]))
    if len(rows) < 4:
        return None
    r = pd.DataFrame(rows)
    r["trail4"] = pd.Series(r["actual"]).shift(1).rolling(4, min_periods=2).mean()
    out = dict(target=target, feature=feature, train_start=str(train_start),
               eval_window=str(eval_start) + "+", n_events=len(r),
               first_event=r.q.min(), last_event=r.q.max(),
               rmse_baseline_ar1=rmse(r.pred_m0, r.actual),
               rmse_baseline_plus_feature=rmse(r.pred_m1, r.actual),
               rmse_naive_last_quarter=rmse(r.naive, r.actual),
               rmse_prior_year=rmse(r.prior_year, r.actual),
               rmse_trailing4_mean=rmse(r.trail4, r.actual))
    out["incremental_ratio"] = out["rmse_baseline_plus_feature"] / out["rmse_baseline_ar1"]
    out["ratio_vs_naive"] = out["rmse_baseline_plus_feature"] / out["rmse_naive_last_quarter"]
    beats = [out["rmse_baseline_ar1"], out["rmse_naive_last_quarter"], out["rmse_prior_year"],
             out["rmse_trailing4_mean"]]
    beats = [b for b in beats if b == b]
    out["feature_adds_value"] = bool(out["rmse_baseline_plus_feature"] < min(beats)) if beats else False
    return out


def main():
    (OUT / "20_experiment_spec.json").write_text(json.dumps(SPEC, indent=2), encoding="utf-8")
    pd.DataFrame(VINTAGE).to_csv(OUT / "20_vintage_register.csv", index=False)

    panel = pd.read_csv(OUT / "08_panel_quarterly.csv", index_col=0)
    panel.index = pd.PeriodIndex(panel.index, freq="Q")
    # point-in-time hotel RevPAR: drop any peer that reported AFTER the ABNB print for that quarter
    pp = pd.read_csv(PROC / "predictive/02_peer_prints.csv")
    pp["q"] = pd.PeriodIndex(pp["quarter"], freq="Q")
    pp = pp.set_index("q")
    mar = pd.to_numeric(pp["mar_revpar_yoy"], errors="coerce").where(
        pd.to_numeric(pp["mar_lead_days"], errors="coerce") > 0)
    hlt = pd.to_numeric(pp["hlt_revpar_yoy"], errors="coerce").where(
        pd.to_numeric(pp["hlt_lead_days"], errors="coerce") > 0)
    panel["pr_hotel_revpar_yoy_pit"] = pd.concat([mar, hlt], axis=1).mean(axis=1).reindex(panel.index)

    # KPI-growth targets, WS08 alt-data features
    rows = []
    feats = ["bl_funds_yoy_lag1", "bl_unearned_yoy_lag1", "eu_platform_yoy_lag1",
             "pr_hotel_revpar_yoy", "pr_hotel_revpar_yoy_pit", "ia_reviews_ltm_matched_yoy",
             "demand_p22_eq"]
    for tgt in ["rev_yoy", "nights_yoy", "gbv_yoy"]:
        for f in feats:
            if f not in panel.columns:
                continue
            for ts, es in [(pd.Period("2022Q1"), pd.Period("2023Q1")),
                           (pd.Period("2022Q1"), pd.Period("2024Q1")),
                           (pd.Period("2023Q1"), pd.Period("2024Q1"))]:
                r = incremental(panel.loc[:pd.Period("2026Q2")], f, tgt, ts, es)
                if r:
                    r["block"] = "WS08 KPI growth"
                    rows.append(r)

    # surprise targets, the WS20 primary feature set (uses the per-event file, so the same
    # expanding scheme and the same MIN_TRAIN)
    pe = pd.read_csv(OUT / "20_pre_earnings_forecasts.csv")
    for (f, tgt), g in pe.groupby(["feature", "target"]):
        for wlab, w0 in [("2023Q1", pd.Period("2023Q1")), ("2024Q1", pd.Period("2024Q1"))]:
            gg = g[g.print_quarter.map(lambda q: pd.Period(q) >= w0)]
            if len(gg) < 4:
                continue
            rows.append(dict(block="WS20 surprise", target=tgt, feature=f,
                             train_start="expanding from the first print",
                             eval_window=wlab + "+", n_events=len(gg),
                             first_event=gg.print_quarter.min(), last_event=gg.print_quarter.max(),
                             rmse_baseline_ar1=rmse(gg["bl_ar1"], gg.actual),
                             rmse_baseline_plus_feature=rmse(gg.pred, gg.actual),
                             rmse_naive_last_quarter=rmse(gg["bl_last_quarter"], gg.actual),
                             rmse_prior_year=rmse(gg["bl_prior_year"], gg.actual),
                             rmse_trailing4_mean=rmse(gg["bl_trailing4_mean"], gg.actual),
                             incremental_ratio=rmse(gg.pred, gg.actual) / rmse(gg["bl_ar1"], gg.actual),
                             ratio_vs_naive=rmse(gg.pred, gg.actual) / rmse(gg["bl_last_quarter"], gg.actual),
                             feature_adds_value=bool(rmse(gg.pred, gg.actual) < min(
                                 rmse(gg["bl_ar1"], gg.actual), rmse(gg["bl_last_quarter"], gg.actual),
                                 rmse(gg["bl_prior_year"], gg.actual), rmse(gg["bl_zero"], gg.actual),
                                 rmse(gg["bl_trailing4_mean"], gg.actual),
                                 rmse(gg["bl_trailing8_mean"], gg.actual)))))
    inc = pd.DataFrame(rows)
    inc.round(4).to_csv(OUT / "20_incremental_value.csv", index=False)

    # funds held, both windows side by side, with the training-start effect separated
    fh = inc[(inc.feature == "bl_funds_yoy_lag1") & (inc.block == "WS08 KPI growth")].copy()
    fh["case"] = fh.apply(lambda r: "train %s, evaluate %s" % (r.train_start, r.eval_window), axis=1)
    fh = fh[["target", "case", "train_start", "eval_window", "n_events", "first_event", "last_event",
             "rmse_baseline_ar1", "rmse_baseline_plus_feature", "rmse_naive_last_quarter",
             "incremental_ratio", "ratio_vs_naive", "feature_adds_value"]]
    fh["reading_rule"] = ("quote n_events together with the ratio on the SAME row; the 2023Q1 and "
                          "2024Q1 rows are different samples AND different training histories")
    fh["method"] = "WS20 incremental: AR(1) vs AR(1)+feature, min_train 8, identical events"
    # also carry the ORIGINAL WS08 single-feature walk-forward rows the audit quoted (min_train 4,
    # no AR(1) term), so the two are visibly side by side rather than paired across files
    t8 = pd.read_csv(OUT / "08_feature_tests_all.csv")
    t8 = t8[(t8.feature == "bl_funds_yoy_lag1") & (t8.target.isin(["rev_yoy", "nights_yoy", "gbv_yoy"]))]
    ws08 = pd.DataFrame([dict(
        target=r.target,
        case="WS08 single feature: %s" % r.window,
        train_start=r.window.split("..")[0], eval_window=r.wf_first + "+",
        n_events=r.wf_n, first_event=r.wf_first, last_event=r.wf_last,
        rmse_baseline_ar1=r.wf_rmse_ar1, rmse_baseline_plus_feature=r.wf_rmse,
        rmse_naive_last_quarter=r.wf_rmse_naive,
        incremental_ratio=r.wf_ratio_vs_ar1, ratio_vs_naive=r.wf_ratio_vs_naive,
        feature_adds_value=bool(r.wf_ratio_vs_ar1 < 1 and r.wf_ratio_vs_naive < 1),
        reading_rule="the audit quoted these two rows; n=14 goes with 1.69/1.85 and n=10 with "
                     "0.60/0.59. They are different samples: never pair one n with the other ratio.",
        method="WS08 original: single feature vs naive/AR(1), min_train 4, no AR term in the model")
        for _, r in t8.iterrows() if pd.notna(r.wf_n)])
    pd.concat([fh, ws08], ignore_index=True).round(4).to_csv(OUT / "20_funds_held_windows.csv", index=False)
    fh = pd.concat([fh, ws08], ignore_index=True)

    pd.set_option("display.width", 250)
    print("spec written:", OUT / "20_experiment_spec.json")
    print("vintage rows:", len(VINTAGE), "| incremental rows:", len(inc))
    print("\n--- funds held for clients, both windows side by side ---")
    print(fh.drop(columns=["reading_rule"]).round(3).to_string(index=False))
    print("\n--- incremental value, WS08 KPI growth, features that add value ---")
    w = inc[(inc.block == "WS08 KPI growth") & (inc.feature_adds_value)]
    print(w[["target", "feature", "train_start", "eval_window", "n_events",
             "incremental_ratio", "ratio_vs_naive"]].round(3).to_string(index=False))
    print("\n--- incremental value, WS20 surprise targets, features that add value ---")
    w2 = inc[(inc.block == "WS20 surprise") & (inc.feature_adds_value)]
    print(w2[["target", "feature", "eval_window", "n_events", "incremental_ratio",
              "ratio_vs_naive"]].round(3).to_string(index=False))
    print("\ntotal incremental tests:", len(inc),
          "| adding value:", int(inc.feature_adds_value.sum()))


if __name__ == "__main__":
    main()
