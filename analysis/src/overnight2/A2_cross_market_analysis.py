"""Cross-market assembly and tests for the 34-market calendar reopening panel.

Two steps, both checkpointed.

  --listing-pass   re-reads the raw calendars and writes, per market, the per-listing
                   initial-unavailable and reopened counts for the screened_short_run /
                   all_future cohort in every interval. Needed because the A1 JSONs hold
                   aggregates only and the listing-clustered bootstrap needs clusters.
                   Cohort definitions are imported from A1, so the per-listing sums must
                   equal the A1 aggregates; that identity is asserted.

  (default)        assembles the market x interval table from the A1 JSONs, computes the
                   pre-registered group differences, the Australian seasonality check, the
                   European dispersion read and the pre-rollout level comparison, and runs
                   the listing-clustered bootstrap if the listing pass is present.

Reopening is a calendar availability transition. It is not a cancellation, and reclosure is
not a confirmed replacement booking. Nothing here is converted into a forecast haircut.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from A1_calendar_reopening_all_markets import (  # noqa: E402
    MANIFEST_DEFAULT, RAW_DEFAULT, discover, load_snapshot, matched, read_manifest, regimes, window_masks)

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/overnight2/A"
MARKETS_DIR = OUT / "markets"
LISTINGS_DIR = OUT / "listing_counts"

US_MARKETS = {"austin", "chicago", "los-angeles", "nashville", "new-orleans", "new-york-city", "san-diego"}
AUSTRALIA = {"barossa-valley", "barwon-south-west-vic", "brisbane", "melbourne", "mid-north-coast",
             "mornington-peninsula", "northern-rivers", "sunshine-coast", "sydney", "tasmania",
             "western-australia"}
EUROPE = {"barcelona", "london", "paris", "rome"}
INTERVAL_LABEL = {1: "I1_Sep_to_Dec", 2: "I2_Dec_to_Mar", 3: "I3_Mar_to_Jun", 4: "I4_Jun_to_Aug"}
BANDS = ["d001_030", "d031_060", "d061_090", "d091_180"]


# --------------------------------------------------------------------- step 1: clusters
def listing_pass(markets, raw_dir, manifest_path, overwrite):
    LISTINGS_DIR.mkdir(parents=True, exist_ok=True)
    manifest = read_manifest(manifest_path)
    found = discover(raw_dir)
    label_root = Path(raw_dir).parents[2]
    for market in markets:
        out = LISTINGS_DIR / f"{market}.csv"
        if out.exists() and not overwrite:
            print(f"skip {market}: {out.name} exists", flush=True)
            continue
        aggregate = json.loads((MARKETS_DIR / f"{market}.json").read_text(encoding="utf-8"))
        expected = {(r["snapshot0"], r["snapshot1"]): r for r in aggregate["pairs"]
                    if r["regime"] == "screened_short_run" and r["window"] == "all_future"}
        snapshots = []
        for date, path in found[market]:
            snapshot, frame, _ = load_snapshot(path, label_root)
            snapshots.append((snapshot, frame))
            print(f"{market} {snapshot}: loaded", flush=True)
        stable = set.intersection(*(set(f.listing_id.unique()) for _, f in snapshots))
        rows = []
        for i in range(len(snapshots) - 1):
            date0, a = snapshots[i]
            date1, b = snapshots[i + 1]
            joint = matched(a, b, date1)
            mask = regimes(joint, stable)["screened_short_run"] & window_masks(joint, date1)["all_future"]
            subset = joint[mask]
            if not len(subset):
                continue
            grouped = subset.assign(init_u=subset.u0, reopened=subset.u0 & ~subset.u1) \
                .groupby("listing_id")[["init_u", "reopened"]].sum().reset_index()
            grouped = grouped[grouped.init_u > 0]
            grouped.insert(0, "snapshot1", date1)
            grouped.insert(0, "snapshot0", date0)
            grouped.insert(0, "interval", i + 1)
            grouped.insert(0, "market", market)
            reference = expected[(date0, date1)]
            assert int(grouped.init_u.sum()) == reference["initial_unavailable_nights"], market
            assert int(grouped.reopened.sum()) == reference["reopened_nights"], market
            rows.append(grouped)
        pd.concat(rows, ignore_index=True).to_csv(out, index=False)
        print(f"Wrote {out} (aggregate identity checks passed)", flush=True)


# ----------------------------------------------------------------- step 2: assembly
def region_of(market, declared):
    if market in US_MARKETS:
        return "NA_US"
    return {"emea": "EMEA", "apac": "APAC", "latam": "LatAm", "na": "NA_US"}.get(declared, declared or "unknown")


def assemble():
    rows = []
    for path in sorted(MARKETS_DIR.glob("*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        market = d["market"]
        pairs = {(r["snapshot0"], r["snapshot1"], r["regime"], r["window"]): r for r in d["pairs"]}
        triples = {(r["snapshot0"], r["snapshot1"], r["regime"], r["window"]): r for r in d["triples"]}
        for i, cov in enumerate(d["coverage"], start=1):
            k0, k1 = cov["snapshot0"], cov["snapshot1"]
            short = pairs[(k0, k1, "screened_short_run", "all_future")]
            tri = next((v for (a, b, reg, win), v in triples.items()
                        if (a, b) == (k0, k1) and reg == "screened_short_run" and win == "all_future"), None)
            tri_broad = next((v for (a, b, reg, win), v in triples.items()
                              if (a, b) == (k0, k1) and reg == "all_matched" and win == "all_future"), None)
            row = {"market": market, "region": region_of(market, d.get("region")),
                   "us": market in US_MARKETS, "australia": market in AUSTRALIA,
                   "europe": market in EUROPE, "interval": i,
                   "interval_label": INTERVAL_LABEL.get(i, f"I{i}"),
                   "snapshot0": k0, "snapshot1": k1, "interval_days": cov["interval_days"],
                   "n_vintages": d["n_vintages"],
                   "matched_future_row_retention_pct": cov["matched_future_row_retention_pct"],
                   "unavailable_row_retention_pct": cov["unavailable_row_retention_pct"],
                   "stable_panel_listings": cov["stable_all_five_listings"],
                   "broad_rate_pct": pairs[(k0, k1, "all_matched", "all_future")]["reopening_rate_pct"],
                   "stable_rate_pct": pairs[(k0, k1, "stable_all_five", "all_future")]["reopening_rate_pct"],
                   "screened_rate_pct": pairs[(k0, k1, "screened", "all_future")]["reopening_rate_pct"],
                   "short_run_rate_pct": short["reopening_rate_pct"],
                   "short_run_reopened": short["reopened_nights"],
                   "short_run_initial_unavailable": short["initial_unavailable_nights"],
                   "short_run_top10_share_pct": short["top10_listings_share_of_reopenings_pct"],
                   "broad_reclosed_pct": tri_broad["reclosed_pct"] if tri_broad else None,
                   "short_run_reclosed_pct": tri["reclosed_pct"] if tri else None,
                   "short_run_reopened_followed": tri["reopened_followed_nights"] if tri else None}
            for band in BANDS:
                rec = pairs.get((k0, k1, "screened_short_run", band))
                row[f"short_run_{band}_pct"] = rec["reopening_rate_pct"] if rec else None
                row[f"short_run_{band}_initial"] = rec["initial_unavailable_nights"] if rec else None
            rows.append(row)
    return pd.DataFrame(rows).sort_values(["market", "interval"]).reset_index(drop=True)


def market_changes(table):
    """Pre-registered market statistic: mean short-run rate over I3,I4 minus mean over I1,I2."""
    out = []
    for market, g in table.groupby("market"):
        rates = g.set_index("interval").short_run_rate_pct
        if not {1, 2, 3, 4}.issubset(rates.index):
            continue
        early, late = (rates[1] + rates[2]) / 2, (rates[3] + rates[4]) / 2
        meta = g.iloc[0]
        out.append({"market": market, "region": meta.region, "us": meta.us,
                    "australia": meta.australia, "europe": meta.europe,
                    "I1": rates[1], "I2": rates[2], "I3": rates[3], "I4": rates[4],
                    "early_mean": early, "late_mean": late, "change_pp": late - early,
                    "I4_minus_I1_pp": rates[4] - rates[1],
                    "min_interval_days": int(g.interval_days.min()),
                    "max_interval_days": int(g.interval_days.max()),
                    "short_run_initial_total": int(g.short_run_initial_unavailable.sum())})
    return pd.DataFrame(out).sort_values("change_pp", ascending=False).reset_index(drop=True)


def pooled_rates(table, name, markets):
    """Night-weighted pooled rate per interval for a group; the market-mean's complement."""
    sub = table[table.market.isin(markets) & table.interval.le(4)]
    row = {"group": name, "markets": sub.market.nunique()}
    for i in range(1, 5):
        g = sub[sub.interval == i]
        row[f"pooled_I{i}_pct"] = g.short_run_reopened.sum() / g.short_run_initial_unavailable.sum() * 100 \
            if g.short_run_initial_unavailable.sum() else None
        row[f"initial_I{i}"] = int(g.short_run_initial_unavailable.sum())
        row[f"mean_interval_days_I{i}"] = float(g.interval_days.mean()) if len(g) else None
    if all(row.get(f"pooled_I{i}_pct") is not None for i in range(1, 5)):
        row["pooled_change_pp"] = (row["pooled_I3_pct"] + row["pooled_I4_pct"]) / 2 \
            - (row["pooled_I1_pct"] + row["pooled_I2_pct"]) / 2
    return row


def duration_normalised(table):
    """Post hoc: scale each rate to a 90-day interval. Interval 4 is ~62 days, intervals 1-3 ~90."""
    out = table.copy()
    out["short_run_rate_per90_pct"] = out.short_run_rate_pct * 90 / out.interval_days
    return out


def leave_one_out(changes):
    """Influence of each market on the non-US minus US market-mean difference."""
    base = changes[~changes.us].change_pp.mean() - changes[changes.us].change_pp.mean()
    rows = []
    for market in changes.market:
        sub = changes[changes.market != market]
        diff = sub[~sub.us].change_pp.mean() - sub[sub.us].change_pp.mean()
        rows.append({"dropped_market": market, "nonUS_minus_US_pp": diff, "shift_vs_full_pp": diff - base})
    frame = pd.DataFrame(rows).sort_values("shift_vs_full_pp")
    frame.insert(0, "full_sample_nonUS_minus_US_pp", base)
    return frame


def group_block(changes, name, mask):
    sub = changes[mask]
    return {"group": name, "markets": len(sub),
            "mean_change_pp": sub.change_pp.mean(), "median_change_pp": sub.change_pp.median(),
            "sd_change_pp": sub.change_pp.std(ddof=1) if len(sub) > 1 else None,
            "min_change_pp": sub.change_pp.min(), "max_change_pp": sub.change_pp.max(),
            "share_positive": float((sub.change_pp > 0).mean()) if len(sub) else None,
            "mean_I1": sub.I1.mean(), "mean_I2": sub.I2.mean(),
            "mean_I3": sub.I3.mean(), "mean_I4": sub.I4.mean()}


def permutation_p(changes, n=20000, seed=20260911):
    """US/non-US label permutation on the market-level change statistic, two-sided."""
    rng = np.random.default_rng(seed)
    values = changes.change_pp.to_numpy()
    labels = changes.us.to_numpy()
    observed = values[~labels].mean() - values[labels].mean()
    k = labels.sum()
    draws = np.empty(n)
    for i in range(n):
        perm = rng.permutation(len(values))
        treated = perm[:k]
        mask = np.zeros(len(values), bool)
        mask[treated] = True
        draws[i] = values[~mask].mean() - values[mask].mean()
    return observed, float((np.abs(draws) >= abs(observed) - 1e-12).mean())


def bootstrap(table, reps=2000, seed=20260911):
    """Listing-clustered bootstrap. Resample listings within each market, with replacement."""
    files = sorted(LISTINGS_DIR.glob("*.csv"))
    if not files:
        return None, None
    counts = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    meta = table.drop_duplicates("market").set_index("market")[["region", "us", "australia", "europe"]]
    rng = np.random.default_rng(seed)
    per_market, draws = [], {}
    for market, g in counts.groupby("market"):
        wide = g.pivot_table(index="listing_id", columns="interval",
                             values=["init_u", "reopened"], aggfunc="sum", fill_value=0)
        listings = wide.index.to_numpy()
        intervals = sorted({c[1] for c in wide.columns})
        init = {i: wide[("init_u", i)].to_numpy(float) for i in intervals}
        reop = {i: wide[("reopened", i)].to_numpy(float) for i in intervals}
        idx = rng.integers(0, len(listings), size=(reps, len(listings)))
        rates = {}
        for i in intervals:
            num = reop[i][idx].sum(axis=1)
            den = init[i][idx].sum(axis=1)
            rates[i] = np.where(den > 0, num / np.where(den > 0, den, 1) * 100, np.nan)
        draws[market] = rates
        last = max(intervals)
        point = reop[last].sum() / init[last].sum() * 100
        lo, hi = np.nanpercentile(rates[last], [2.5, 97.5])
        record = {"market": market, "listings_in_cohort": len(listings), "last_interval": last,
                  "last_interval_rate_pct": point, "boot_lo_pct": lo, "boot_hi_pct": hi,
                  "boot_sd_pp": float(np.nanstd(rates[last], ddof=1))}
        if {1, 2, 3, 4}.issubset(intervals):
            change = (rates[3] + rates[4]) / 2 - (rates[1] + rates[2]) / 2
            record["change_pp"] = (reop[3].sum() / init[3].sum() + reop[4].sum() / init[4].sum()) / 2 * 100 \
                - (reop[1].sum() / init[1].sum() + reop[2].sum() / init[2].sum()) / 2 * 100
            record["change_boot_lo_pp"], record["change_boot_hi_pp"] = np.nanpercentile(change, [2.5, 97.5])
        per_market.append(record | meta.loc[market].to_dict())
    per_market = pd.DataFrame(per_market)

    def contrast(group_a, group_b, statistic):
        a = [statistic(m) for m in group_a if statistic(m) is not None]
        b = [statistic(m) for m in group_b if statistic(m) is not None]
        if not a or not b:
            return None
        diff = np.nanmean(np.vstack(a), axis=0) - np.nanmean(np.vstack(b), axis=0)
        return np.nanpercentile(diff, [2.5, 97.5])

    def last_rate(market):
        rates = draws[market]
        return rates[max(rates)]

    def change_stat(market):
        rates = draws[market]
        if not {1, 2, 3, 4}.issubset(rates):
            return None
        return (rates[3] + rates[4]) / 2 - (rates[1] + rates[2]) / 2

    full = per_market[per_market.last_interval == 4]
    us = sorted(set(full[full.us].market))
    non_us = sorted(set(full[~full.us].market))
    aus = sorted(set(full[full.australia].market))
    eur = sorted(set(full[full.europe].market))
    contrasts = []
    for name, a, b, stat in [("JunAug_level_nonUS_minus_US", non_us, us, last_rate),
                             ("change_nonUS_minus_US", non_us, us, change_stat),
                             ("change_Australia_minus_US", aus, us, change_stat),
                             ("change_Europe_minus_US", eur, us, change_stat)]:
        ci = contrast(a, b, stat)
        point = np.nanmean([np.nanmean(stat(m)) for m in a]) - np.nanmean([np.nanmean(stat(m)) for m in b]) \
            if ci is not None else None
        contrasts.append({"contrast": name, "n_a": len(a), "n_b": len(b),
                          "bootstrap_mean_pp": point,
                          "boot_lo_pp": None if ci is None else ci[0],
                          "boot_hi_pp": None if ci is None else ci[1],
                          "reps": reps, "cluster": "listing within market"})
    return per_market, pd.DataFrame(contrasts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--listing-pass", action="store_true")
    parser.add_argument("--market", action="append")
    parser.add_argument("--raw-dir", default=str(RAW_DEFAULT))
    parser.add_argument("--manifest", default=str(MANIFEST_DEFAULT))
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--reps", type=int, default=2000)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.listing_pass:
        markets = args.market or sorted(p.stem for p in MARKETS_DIR.glob("*.json"))
        listing_pass(markets, args.raw_dir, args.manifest, args.overwrite)
        return

    table = duration_normalised(assemble())
    table.to_csv(OUT / "A2_market_interval_table.csv", index=False)
    changes = market_changes(table)
    thin = set(table[(table.short_run_initial_unavailable < 1000) |
                     (table.short_run_top10_share_pct >= 80)].market)
    changes["thin_or_concentrated"] = changes.market.isin(thin)
    changes.to_csv(OUT / "A2_market_changes.csv", index=False)

    groups = [group_block(changes, "US", changes.us),
              group_block(changes, "non_US", ~changes.us),
              group_block(changes, "EMEA_Europe", changes.europe),
              group_block(changes, "APAC_Australia", changes.australia),
              group_block(changes, "APAC_non_Australia", (changes.region == "APAC") & ~changes.australia),
              group_block(changes, "LatAm", changes.region == "LatAm"),
              group_block(changes, "balanced_intervals_non_US",
                          (~changes.us) & changes.min_interval_days.ge(55) & changes.max_interval_days.le(105)),
              group_block(changes, "balanced_intervals_US",
                          changes.us & changes.min_interval_days.ge(55) & changes.max_interval_days.le(105)),
              group_block(changes, "deep_cohorts_non_US", (~changes.us) & ~changes.thin_or_concentrated),
              group_block(changes, "deep_cohorts_US", changes.us & ~changes.thin_or_concentrated)]
    summary = pd.DataFrame(groups)
    observed, p_value = permutation_p(changes)
    summary.loc[len(summary)] = {"group": "nonUS_minus_US_difference", "markets": len(changes),
                                 "mean_change_pp": observed, "median_change_pp": None, "sd_change_pp": None,
                                 "min_change_pp": None, "max_change_pp": None, "share_positive": p_value,
                                 "mean_I1": None, "mean_I2": None, "mean_I3": None, "mean_I4": None}
    summary.to_csv(OUT / "A2_group_summary.csv", index=False)

    # Bogota and Sao Paulo have only a June-to-August interval, so their interval 1 is not the
    # pre-rollout window; exclude short panels from the pre-rollout level comparison.
    pre = table[(table.interval == 1) & table.n_vintages.eq(5)]
    levels = pre.groupby("us").short_run_rate_pct.agg(["count", "mean", "median", "std"])
    levels.to_csv(OUT / "A2_pre_rollout_levels.csv")

    pooled = pd.DataFrame([
        pooled_rates(table, "US", sorted(changes[changes.us].market)),
        pooled_rates(table, "non_US", sorted(changes[~changes.us].market)),
        pooled_rates(table, "EMEA_Europe", sorted(changes[changes.europe].market)),
        pooled_rates(table, "APAC_Australia", sorted(changes[changes.australia].market)),
        pooled_rates(table, "APAC_non_Australia", sorted(changes[(changes.region == "APAC") & ~changes.australia].market)),
        pooled_rates(table, "LatAm", sorted(changes[changes.region == "LatAm"].market)),
        pooled_rates(table, "non_US_ex_Europe", sorted(changes[(~changes.us) & ~changes.europe].market)),
        pooled_rates(table, "Europe_ex_Rome", sorted(changes[changes.europe & changes.market.ne("rome")].market)),
        pooled_rates(table, "rome_only", ["rome"])])
    pooled.to_csv(OUT / "A2_pooled_rates.csv", index=False)

    band_rows = []
    for (group, name) in [("US", changes[changes.us].market), ("non_US", changes[~changes.us].market),
                          ("EMEA_Europe", changes[changes.europe].market),
                          ("APAC_Australia", changes[changes.australia].market),
                          ("LatAm", changes[changes.region == "LatAm"].market)]:
        sub = table[table.market.isin(set(name))]
        for band in BANDS:
            row = {"group": group, "band": band}
            for i in range(1, 5):
                g = sub[sub.interval == i]
                num = g[f"short_run_{band}_pct"] * g[f"short_run_{band}_initial"] / 100
                den = g[f"short_run_{band}_initial"]
                row[f"pooled_I{i}_pct"] = num.sum() / den.sum() * 100 if den.sum() else None
            row["pooled_change_pp"] = (row["pooled_I3_pct"] + row["pooled_I4_pct"]) / 2 \
                - (row["pooled_I1_pct"] + row["pooled_I2_pct"]) / 2
            band_rows.append(row)
    pd.DataFrame(band_rows).to_csv(OUT / "A2_days_to_arrival_bands.csv", index=False)

    influence = leave_one_out(changes)
    influence.to_csv(OUT / "A2_leave_one_out.csv", index=False)

    per90 = changes.merge(
        table[table.interval.le(4)].pivot_table(index="market", columns="interval",
                                                values="short_run_rate_per90_pct"),
        on="market", how="left")
    per90["change_per90_pp"] = (per90[3] + per90[4]) / 2 - (per90[1] + per90[2]) / 2
    per90[["market", "region", "us", 1, 2, 3, 4, "change_pp", "change_per90_pp"]].to_csv(
        OUT / "A2_duration_normalised.csv", index=False)

    per_market, contrasts = bootstrap(table, reps=args.reps)
    if per_market is not None:
        per_market.to_csv(OUT / "A2_bootstrap_markets.csv", index=False)
        contrasts.to_csv(OUT / "A2_bootstrap_contrasts.csv", index=False)

    print(f"markets: {table.market.nunique()}, market-interval rows: {len(table)}")
    print(f"permutation (US vs non-US labels) observed non-US minus US change = {observed:.3f} pp, p = {p_value:.4f}")
    print(summary.to_string(index=False, float_format=lambda v: f"{v:.2f}"))
    print("\nPre-rollout (interval 1) short-run level by US flag:")
    print(levels.to_string(float_format=lambda v: f"{v:.2f}"))
    print("\nEurope dispersion:")
    print(changes[changes.europe][["market", "I1", "I2", "I3", "I4", "change_pp"]].to_string(
        index=False, float_format=lambda v: f"{v:.2f}"))
    print("\nMarket changes, sorted:")
    print(changes[["market", "region", "us", "I1", "I2", "I3", "I4", "change_pp", "min_interval_days",
                   "max_interval_days"]].to_string(index=False, float_format=lambda v: f"{v:.2f}"))
    print("\nNight-weighted pooled rates:")
    print(pooled[["group", "markets", "pooled_I1_pct", "pooled_I2_pct", "pooled_I3_pct", "pooled_I4_pct",
                  "pooled_change_pp", "initial_I4"]].to_string(index=False, float_format=lambda v: f"{v:.2f}"))
    print("\nDuration-normalised (per 90 days, post hoc) change by group:")
    print(per90.groupby("us").change_per90_pp.agg(["count", "mean", "median"]).to_string(
        float_format=lambda v: f"{v:.2f}"))
    print("\nFixed days-to-arrival bands, pooled:")
    print(pd.DataFrame(band_rows).to_string(index=False, float_format=lambda v: f"{v:.2f}"))
    print("\nLeave-one-out extremes on the non-US minus US difference:")
    print(pd.concat([influence.head(3), influence.tail(3)]).to_string(index=False, float_format=lambda v: f"{v:.2f}"))
    if contrasts is not None:
        print("\nListing-clustered bootstrap contrasts:")
        print(contrasts.to_string(index=False, float_format=lambda v: f"{v:.2f}"))
        print("\nBootstrap per market (final interval):")
        print(per_market[["market", "region", "listings_in_cohort", "last_interval_rate_pct",
                          "boot_lo_pct", "boot_hi_pct", "change_pp", "change_boot_lo_pp",
                          "change_boot_hi_pp"]].sort_values("market").to_string(
            index=False, float_format=lambda v: f"{v:.2f}"))


if __name__ == "__main__":
    main()
