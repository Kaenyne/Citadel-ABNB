"""Fixed-market weighting, paired sensitivity and fee-economics calculations."""
import csv
import json
from pathlib import Path

from acquire_churn_archive import ROOT
from execute_listing_churn import write_csv
from research_integrity import finite_number


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def summarize(rows, metadata):
    keys = [(r['panel'], r['cohort'], r['portfolio'], r['policy'], r['market'], r['start_month'], r['end_month']) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate market/cohort/interval rows would silently replace evidence')
    output, comparisons = [], []
    specs = {
        "balanced_event": ("monthly", (("2025-09","2025-10"),("2025-10","2025-11"),("2025-11","2025-12"),("2025-12","2026-01"))),
        "balanced_broad": ("broad_quarterly", (("2025-09","2025-12"),("2025-12","2026-03"),("2026-03","2026-06"))),
        "balanced_pre_quarters": ("team_historical", (("2025-03","2025-06"),("2025-06","2025-09"),("2025-09","2025-12"))),
        "same_season": ("team_historical", (("2024-09","2024-12"),("2025-09","2025-12"))),
        "event_summer_check": ("monthly", (("2025-09","2025-10"),("2026-06","2026-07"))),
    }
    for series, (panel, intervals) in specs.items():
        for cohort in ("all_listings", "reviewed_str_homes"):
            for portfolio in ("all", "one", "five_plus"):
                chosen = [r for r in rows if r["panel"]==panel and r["cohort"]==cohort and r["portfolio"]==portfolio
                          and r["policy"]=="coverage_screen" and r["eligible"]=="True"
                          and r["market"] in metadata["market_sets"]["balanced_event" if series=="event_summer_check" else series]
                          and (r["start_month"],r["end_month"]) in intervals]
                grouped = {period:{r["market"]:r for r in chosen if (r["start_month"],r["end_month"])==period} for period in intervals}
                markets = sorted(set.intersection(*(set(v) for v in grouped.values())))
                if not markets:
                    continue
                weights = {m:int(grouped[intervals[0]][m]["baseline_ids"]) for m in markets}
                weight_total = sum(weights.values())
                for period in intervals:
                    group = [grouped[period][m] for m in markets]
                    n = sum(int(r["baseline_ids"]) for r in group)
                    missing = sum(int(r["missing_ids"]) for r in group)
                    review_n = sum(float(r["baseline_review_total"]) for r in group)
                    output.append(dict(series=series,cohort=cohort,portfolio=portfolio,start_month=period[0],end_month=period[1],
                        markets=len(markets),baseline_ids=n,missing_ids=missing,observed_rate=missing/n,
                        fixed_market_weighted_rate=sum(weights[m]*float(grouped[period][m]["disappearance_rate"]) for m in markets)/weight_total,
                        fixed_market_weighted_30d_rate=sum(weights[m]*float(grouped[period][m]["normalized_30d_rate"]) for m in markets)/weight_total,
                        review_weighted_rate=sum(float(r["missing_baseline_reviews"]) for r in group)/review_n if review_n else None,
                        min_interval_days=min(int(r["interval_days"]) for r in group),max_interval_days=max(int(r["interval_days"]) for r in group),
                        market_set=" | ".join(markets)))
                for period in intervals[1:]:
                    changes = {m:float(grouped[period][m]["normalized_30d_rate"])-float(grouped[intervals[0]][m]["normalized_30d_rate"]) for m in markets}
                    delta = sum(weights[m]*changes[m] for m in markets)/weight_total
                    loo = [sum(weights[m]*changes[m] for m in markets if m!=drop)/(weight_total-weights[drop]) for drop in markets] if len(markets)>1 else []
                    comparisons.append(dict(series=series,cohort=cohort,portfolio=portfolio,comparison_start=period[0],comparison_end=period[1],
                        baseline_start=intervals[0][0],baseline_end=intervals[0][1],markets=len(markets),
                        change_30d_rate_pp=100*delta,markets_increased=sum(v>0 for v in changes.values()),
                        leave_one_market_out_min_pp=100*min(loo) if loo else None,
                        leave_one_market_out_max_pp=100*max(loo) if loo else None,
                        interpretation="Descriptive fixed-weight paired change and concentration sensitivity, not a causal estimate or confidence interval"))
    return output, comparisons


def persistence_summary(rows, metadata):
    periods = (("2025-09","2025-10"),("2025-10","2025-11"),("2025-11","2025-12"),("2025-12","2026-01"))
    output, coverage = [], []
    for policy in ("coverage_screen", "exclude_feb_may_negatives"):
        for cohort in ("all_listings", "reviewed_str_homes"):
            selected = [r for r in rows if r["panel"]=="monthly" and r["cohort"]==cohort and r["portfolio"]=="all"
                        and r["policy"]==policy and r["persistence_eligible"]=="True"
                        and r["market"] in metadata["market_sets"]["balanced_event"]]
            grouped = {p:{r["market"]:r for r in selected if (r["start_month"],r["end_month"])==p} for p in periods}
            markets = sorted(set.intersection(*(set(g) for g in grouped.values())))
            coverage.append(dict(policy=policy,cohort=cohort,common_markets=markets,
                                 identified=bool(markets),interpretation="An empty common panel means unidentified, not zero persistent churn"))
            for p in periods:
                if not markets:
                    continue
                group = [grouped[p][m] for m in markets]
                n = sum(int(r["baseline_ids"]) for r in group)
                missing = sum(int(r["missing_ids"]) for r in group)
                persistent = sum(int(r["persistent_90_ids"]) for r in group)
                output.append(dict(policy=policy,cohort=cohort,start_month=p[0],end_month=p[1],markets=len(markets),
                    baseline_ids=n,missing_ids=missing,persistent_90_ids=persistent,persistent_90_rate=persistent/n,
                    reobserved=missing-persistent,reobserved_share_of_missing=(missing-persistent)/missing if missing else None,
                    min_confirmation_lag_days=min(int(r["confirmation_lag_days"]) for r in group),
                    max_confirmation_lag_days=max(int(r["confirmation_lag_days"]) for r in group),
                    market_set=" | ".join(markets)))
    return output, coverage


def economic_scenarios(ledger):
    e = ledger["economic_example"]
    old_price, old_host, new_host = e["old_booking_subtotal"], e["old_host_fee"], e["new_host_fee"]
    finite_number(old_price, 'Booking subtotal', minimum=0)
    if old_price == 0:
        raise ValueError('Payout-change illustration requires a positive subtotal')
    for label, value in [('old_host_fee', old_host), ('new_host_fee', new_host),
                         ('illustrative_old_guest_fee', e['illustrative_old_guest_fee'])]:
        finite_number(value, label, minimum=0, maximum=1)
    if old_host == 1 or new_host == 1:
        raise ValueError('Host fees must leave a positive payout for the preservation example')
    old_payout = old_price*(1-old_host)
    prices = [("old_split_fee",old_price,old_host,e["illustrative_old_guest_fee"]),
              ("single_fee_unchanged_price",old_price,new_host,0),
              ("single_fee_preserve_payout",old_payout/(1-new_host),new_host,0)]
    economics = [dict(scenario=name,host_set_subtotal=p,host_fee=hf,guest_fee=gf,
        guest_total=p*(1+gf),host_payout=p*(1-hf),platform_fee=p*(hf+gf),
        host_payout_change_pct=100*(p*(1-hf)/old_payout-1),
        interpretation="Calculated illustration excluding taxes; not observed repricing") for name,p,hf,gf in prices]
    scales = [s for s in ledger['sources'] if s['id'] == 'FEE-04']
    if len(scales) != 1:
        raise ValueError('Require one unambiguous Q2 reference-scale source')
    q2 = scales[0]
    for field in ('revenue_usd_m', 'adjusted_ebitda_usd_m'):
        finite_number(q2[field], field, minimum=0)
        if q2[field] == 0:
            raise ValueError('Positive financial reference scale required')
    s = ledger["materiality_scenario"]
    for key in ('affected_share_of_counterfactual_booking_value', 'time_exposure_in_period',
                'incremental_contribution_margin'):
        finite_number(s[key], key, minimum=0, maximum=1)
    finite_number(s['relative_lost_listing_productivity'], 'Relative productivity', minimum=0)
    for key in ('incremental_churn_rates', 'booking_value_recaptured_within_airbnb', 'relative_take_rate_changes'):
        if not s[key]:
            raise ValueError(f'Empty scenario grid: {key}')
        for value in s[key]:
            finite_number(value, key, minimum=-1 if key == 'relative_take_rate_changes' else 0,
                          maximum=None if key == 'relative_take_rate_changes' else 1)
    scenarios = []
    for churn in s["incremental_churn_rates"]:
        for recapture in s["booking_value_recaptured_within_airbnb"]:
            loss = s["affected_share_of_counterfactual_booking_value"]*churn*s["relative_lost_listing_productivity"]*(1-recapture)*s["time_exposure_in_period"]
            finite_number(loss, 'Net company booking-value loss', minimum=0, maximum=1)
            for take in s["relative_take_rate_changes"]:
                revenue_change = (1-loss)*(1+take)-1
                revenue_usd_m = q2["revenue_usd_m"]*revenue_change
                ebitda_usd_m = revenue_usd_m*s["incremental_contribution_margin"]
                scenarios.append(dict(affected_booking_share=s["affected_share_of_counterfactual_booking_value"],incremental_churn=churn,
                    demand_recapture=recapture,relative_take_rate_change=take,net_booking_value_change=-loss,
                    revenue_change=revenue_change,revenue_change_usd_m=revenue_usd_m,adjusted_ebitda_change_usd_m=ebitda_usd_m,
                    adjusted_ebitda_change=ebitda_usd_m/q2["adjusted_ebitda_usd_m"],
                    interpretation=f"Hypothetical sensitivity using Q2 2026 scale, not a forecast; assumed {s['incremental_contribution_margin']:.0%} incremental contribution margin; exposure {s['time_exposure_in_period']}; take-rate change is company-wide and relative, not fee percentage points"))
    return economics, scenarios


def main():
    folder = ROOT / "data/processed/fee_churn_history"
    rows = read(folder / "market_interval_rates.csv")
    metadata = json.loads((folder / "execution_metadata.json").read_text(encoding="utf-8"))
    summary, comparisons = summarize(rows, metadata)
    write_csv(folder / "trend_summary.csv", summary)
    write_csv(folder / "paired_comparisons.csv", comparisons)
    persistent, coverage = persistence_summary(rows, metadata)
    write_csv(folder / "persistence_summary.csv", persistent)
    (folder / "persistence_coverage.json").write_text(json.dumps(coverage, indent=2), encoding="utf-8")
    ledger = json.loads((ROOT / "research/sources/fee_churn_catalyst.json").read_text(encoding="utf-8"))
    economics, scenarios = economic_scenarios(ledger)
    write_csv(folder / "fee_economics.csv", economics)
    write_csv(folder / "catalyst_scenarios.csv", scenarios)
    for row in summary:
        if row["portfolio"]=="all":
            print(row["series"],row["cohort"],row["start_month"],row["end_month"],row["markets"],row["baseline_ids"],row["missing_ids"],f"raw={row['observed_rate']:.3%}",f"fixed30={row['fixed_market_weighted_30d_rate']:.3%}",flush=True)


if __name__ == "__main__":
    main()
