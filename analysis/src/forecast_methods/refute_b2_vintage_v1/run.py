"""Independent reconstruction of B2's descriptive claim; no source mutation."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import traceback

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "analysis/src/forecast_methods"))
from kernel_engine_v2 import engine as K

BASE = ROOT / "data/processed/forecast_methods"
ORIGINAL = BASE / "alpha_b2/run_20260913T171654_499731Z"
OUT = BASE / "refute_b2_vintage_v1"


def quarter(q):
    return "20" + q[2:] + "Q" + q[0] if len(q) == 4 else q


def shift(q, n):
    return str(pd.Period(q, freq="Q") + n)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, default=str, allow_nan=True), encoding="utf-8")


def main():
    start = time.perf_counter()
    dest = OUT / datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%S_%fZ")
    dest.mkdir(parents=True, exist_ok=False)
    try:
        calendar = pd.read_csv(BASE / "harness/calendar.csv")
        dates = dict(zip(calendar.print_quarter, pd.to_datetime(calendar.print_date)))
        kpi = pd.read_csv(ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv")
        kpi["quarter"] = kpi.quarter.map(quarter)
        kpi["print_date"] = kpi.quarter.map(dates)
        cs = pd.read_csv(ROOT / "data/processed/overnight/02_guidance_cushion_series.csv")
        cs["quarter"] = cs.target_period.map(quarter)
        cs["print_date"] = cs.quarter.map(dates)
        cs["ratio"] = cs.actual / cs.value_mid
        vintages = pd.read_csv(BASE / "L0/L0_vintage_register.csv", comment="#")
        returns = pd.read_csv(BASE / "returns_v1/earnings_reactions_open_v1.csv").set_index("event_date")
        old = pd.read_csv(ORIGINAL / "cells.csv")
        old = old[(old.prior_basis == "PIT") & np.isclose(old.weight, 2 / 3)].set_index("event_date")
        events = calendar[calendar.next_quarter_guided.between("2023Q1", "2026Q2")].sort_values("print_date")
        source_rows, kernel_rows, cells = [], [], []

        def consensus(q, date, role):
            candidates = vintages[(vintages.period == q) & (vintages.metric == "revenue") & (vintages.role == role)]
            usable = []
            for row in candidates.to_dict("records"):
                raw = row["as_of_timestamp"]
                ts = pd.Timestamp(raw)
                # Convention explicitly treats date-only PG/AP stamps as morning-of-print.
                date_only = len(str(raw)) == 10
                local = ts.tz_localize("America/New_York") if ts.tzinfo is None else ts.tz_convert("America/New_York")
                on_day = str(local.date()) == date
                before_close = date_only or local.hour < 16
                flags = str(row["pit_usable"]).lower() == "true" and str(row["vendor_attributed"]).lower() == "true"
                valid = bool(on_day and before_close and flags and np.isfinite(row["value"]) and row["value"] > 0)
                source_rows.append(dict(origin_or_endpoint=date, **row, date_only=date_only,
                                        pre_close=before_close, flags_pass=flags, admitted=valid))
                if valid:
                    usable.append(row)
            if not usable:
                return None
            assert len(usable) == 1, "Ambiguous historical consensus source"
            return usable[0]

        def guide(q, origin, coef_origin=None, forward_gbv=False, future_cushion=False):
            coef_origin = origin if coef_origin is None else coef_origin
            training = kpi[kpi.print_date <= coef_origin].sort_values("quarter").copy()
            visible = kpi[kpi.print_date <= origin].sort_values("quarter")
            try:
                lam = K.pit_lambda(int(q[-1]), coef_origin + pd.Timedelta(days=1), panel=training)
            except K.DataUnavailable:
                return np.nan, None
            lookup = kpi.set_index("quarter").gbv_musd if forward_gbv else visible.set_index("quarter").gbv_musd
            l1, l2 = (q, shift(q, -1)) if forward_gbv else (shift(q, -1), shift(q, -2))
            cushion_cutoff = coef_origin if future_cushion else origin
            cushion = cs[cs.print_date <= cushion_cutoff].sort_values("quarter").tail(8)
            base = 2 / 3 * lookup[l1] + 1 / 3 * lookup[l2]
            divisor = float(cushion.ratio.median())
            result = base * lam["lambda_pct"] / 100 / divisor
            metadata = dict(lambda_pct=lam["lambda_pct"], lambda_variant=lam["variant"],
                training_quarters="|".join(lam["training_quarters"]),
                training_max_date=str(max(dates[x] for x in lam["training_quarters"]).date()),
                training_n=lam["n_train"], variant_selection_max_date=str(training.print_date.max().date()),
                cushion_quarters="|".join(cushion.quarter), cushion_n=len(cushion),
                cushion_max_date=str(cushion.print_date.max().date()), cushion_ratio=divisor,
                lag1_quarter=l1, lag2_quarter=l2, lag1_gbv=lookup[l1], lag2_gbv=lookup[l2],
                lag1_date=str(dates[l1].date()), lag2_date=str(dates[l2].date()))
            return result, metadata

        for e in events.itertuples():
            d, q = e.print_date, e.next_quarter_guided
            origin = pd.Timestamp(d)
            next_date = dates[q]
            pre = consensus(q, d, "pre_guide")
            after = consensus(q, str(next_date.date()), "at_print")
            forecast, audit = guide(q, origin)
            if audit:
                kernel_rows.append(dict(event_date=d, quarter=q, **audit))
                assert all(pd.Timestamp(audit[k]) <= origin for k in
                    ("training_max_date", "variant_selection_max_date", "cushion_max_date", "lag1_date", "lag2_date"))
            record = dict(event_date=d, guided_quarter=q, next_event_date=str(next_date.date()),
                guide_musd=forecast, consensus_pre=pre["value"] if pre else np.nan,
                consensus_after=after["value"] if after else np.nan,
                pre_id=pre["register_id"] if pre else None, after_id=after["register_id"] if after else None,
                pre_vendor=pre["vendor"] if pre else None, after_vendor=after["vendor"] if after else None,
                pre_timestamp=pre["as_of_timestamp"] if pre else None,
                after_timestamp=after["as_of_timestamp"] if after else None)
            record["s1_pct"] = 100 * (forecast / record["consensus_pre"] - 1)
            record["revision_pct"] = 100 * (record["consensus_after"] / record["consensus_pre"] - 1)
            record["guide_error_musd"] = forecast - old.loc[d, "k_q1_musd"]
            record["signal_error_pp"] = record["s1_pct"] - old.loc[d, "s1_pct"]
            record["revision_error_pp"] = record["revision_pct"] - old.loc[d, "revision_pct"]
            for name, forward, c_future in (("next_lambda", False, False), ("next_gbv", True, False),
                                            ("next_lambda_gbv_cushion", True, True)):
                coef_date = origin if name == "next_gbv" else next_date
                f, _ = guide(q, origin, coef_date, forward, c_future)
                record[name + "_guide_musd"] = f
                record[name + "_s1_pct"] = 100 * (f / record["consensus_pre"] - 1)
            r = returns.loc[d]
            assert pd.Timestamp(r.entry_date) > origin
            record["entry_date"] = r.entry_date
            for h in (20, 60):
                value = float(r[f"open_{h}d_pct"] - r[f"qqq_open_{h}d_pct"])
                assert np.isclose(value, r[f"excess_open_{h}d_pct"], atol=1e-12)
                assert np.isclose(value, old.loc[d, f"excess_open_{h}d_pct"], atol=1e-12)
                record[f"return_{h}d_pp"] = value
            cells.append(record)

        rebuilt = pd.DataFrame(cells)
        pd.testing.assert_series_equal(rebuilt.set_index("event_date").s1_pct, old.s1_pct,
            check_names=False, atol=1e-10, rtol=1e-10)
        pd.testing.assert_series_equal(rebuilt.set_index("event_date").revision_pct, old.revision_pct,
            check_names=False, atol=1e-10, rtol=1e-10)
        summaries = []
        for window, first in (("W1", "2023Q1"), ("W2", "2024Q1")):
            subset = rebuilt[rebuilt.guided_quarter >= first]
            for scenario in ("PIT", "next_lambda", "next_gbv", "next_lambda_gbv_cushion"):
                col = "s1_pct" if scenario == "PIT" else scenario + "_s1_pct"
                pair = subset.dropna(subset=[col, "revision_pct"])
                strong = pair[pair[col].abs() > .5]
                hits = int((np.sign(strong[col]) == np.sign(strong.revision_pct)).sum())
                row = dict(window=window, scenario=scenario, origins=len(subset), n_pairs=len(pair),
                    n_strong=len(strong), hits=hits, hit_rate=hits / len(strong),
                    corr=pair[col].corr(pair.revision_pct), zero_revisions=int((pair.revision_pct == 0).sum()))
                for h in (20, 60):
                    aligned = np.sign(strong[col]) * strong[f"return_{h}d_pp"]
                    row[f"aligned_{h}d_mean_pp"] = aligned.mean()
                    row[f"aligned_{h}d_positive_n"] = int((aligned > 0).sum())
                summaries.append(row)
        summary_table = pd.DataFrame(summaries)

        manifest = json.loads((ORIGINAL / "input_manifest.json").read_text())
        hashes = []
        for name, item in manifest.items():
            current = hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest()
            hashes.append(dict(input=name, path=item["path"], original_sha256=item["sha256"],
                               current_sha256=current, matches=current == item["sha256"]))
        for path in (ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv",
                     ROOT / "data/processed/overnight/02_guidance_cushion_series.csv"):
            hashes.append(dict(input=path.stem, path=str(path.relative_to(ROOT)),
                current_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                original_sha256=None, matches=None))
        registry = pd.read_csv(BASE / "registry/alpha-b2__revenue_q_plus_2.csv")
        historical = registry[(registry.prior_basis == "PIT") & registry.window.isin(["W1", "W2"])].copy()
        historical["expected_horizon"] = historical.apply(lambda r: pd.Period(r.quarter, freq="Q").ordinal
            - pd.Timestamp(r.vintage_date).to_period("Q").ordinal, axis=1)
        assert (historical.horizon_q == historical.expected_horizon).all()
        assert (pd.to_datetime(historical.knowable_from) <= pd.to_datetime(historical.vintage_date)).all()

        # An explicitly post-close PG row must not count as morning consensus.
        spec = importlib.util.spec_from_file_location("b2_selector_diagnostic", ROOT / "analysis/src/forecast_methods/alpha_b2/run.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        synthetic = pd.DataFrame([dict(register_id="SYNTHETIC", period="2026Q3", metric="revenue", role="pre_guide",
            pit_usable=True, vendor_attributed=True, value=4610., vendor="LSEG", as_of_timestamp="2026-08-06T17:00:00-04:00")])
        accepted = module.admissible_consensus(synthetic, "2026Q3", "2026-08-06", "pre_guide", exact_day=True)
        diagnostics = dict(synthetic_postclose_accepted_by_package=accepted is not None,
            synthetic_used_in_research=False, historical_registry_pit_rows=len(historical),
            registered_rows=len(registry), research_pairs_all_match=True,
            max_abs_guide_error_musd=float(rebuilt.guide_error_musd.abs().max()),
            max_abs_signal_error_pp=float(rebuilt.signal_error_pp.abs().max()),
            max_abs_revision_error_pp=float(rebuilt.revision_error_pp.abs().max()),
            exact_claim_survives=bool(list(summary_table[summary_table.scenario == "PIT"].hits) == [5, 4]
                and list(summary_table[summary_table.scenario == "PIT"].n_strong) == [9, 7]
                and (summary_table[summary_table.scenario == "PIT"][["aligned_20d_mean_pp", "aligned_60d_mean_pp"]] < 0).all().all()))
        for name, frame in (("cells", rebuilt), ("consensus_audit", pd.DataFrame(source_rows)),
                            ("kernel_audit", pd.DataFrame(kernel_rows)), ("summary", summary_table),
                            ("input_hashes", pd.DataFrame(hashes)), ("registry_audit", historical)):
            frame.to_csv(dest / (name + ".csv"), index=False)
        write_json(dest / "diagnostics.json", diagnostics)
        receipt = dict(exit_code=0, elapsed_seconds=time.perf_counter() - start,
            output_directory=str(dest.relative_to(ROOT)), diagnostics=diagnostics,
            results=summary_table.to_dict("records"))
        write_json(dest / "receipt.json", receipt)
        print(json.dumps(receipt, indent=2))
    except Exception:
        (dest / "failure_receipt.txt").write_text(traceback.format_exc(), encoding="utf-8")
        raise


if __name__ == "__main__":
    main()
