"""L0 file 2 — L0_interval_observations.csv: every censored/rounded disclosure as an interval.

HEADER RULE (enforced by the loader, restated in the file's own `included` column):
  * Rows with basis == 'derived' are EXCLUDED from every likelihood. They are kept in the
    file for audit only, with included = False. There are 14 of them (NA 8, EMEA 6,
    spanning 4Q22-3Q24); they are a residual-to-total construction, not a disclosure.
  * The 22 basis == 'numeric' regional nights cells are ROUNDING INTERVALS [x-0.5, x+0.5],
    never equalities.
  * NEVER enter a bucket as its midpoint. Measured here on the 7 quarters where all four
    regions carry a genuine bucket (4Q24-2Q26), with the nights-share weights the panel
    itself supplies: bias = (share-weighted band midpoint) - (actual total nights growth)
    = +0.17pp on average and +0.91pp over the last two quarters, i.e. the midpoints
    OVERSTATE total nights growth, and badly so in 1Q26 (+0.76pp) and 2Q26 (+1.06pp).
    The addendum quotes -0.22pp / -0.72pp; the sign convention there is the opposite one
    (actual minus midpoint) and the magnitudes differ because the weighting differs -- see
    the L0-spine note. Either way the instruction is the same: never use a midpoint.

Blocks, with the architect's target counts in brackets:
  B1 regional nights bucket cells, 4Q24-2Q26                                [28]
  B2 regional nights derived residual cells (audit only, included = False)  [14]
  B3 regional nights stated-integer cells as rounding intervals             [22]
  B4 regional ADR integers from letters, +/-0.5pp                           [68]
  B5 annual 10-K regional nights cells at the table's own precision         [24]
  B6 quarterly revenue guide ranges                                         [19 + 1 LIVE]
  B7 bucket-word guides (nights / GBV / FY revenue)                         [5 scoreable + 5]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from _paths import ADR, OUT, OVERNIGHT, rel  # noqa: E402

SRC_PANEL = OVERNIGHT / "10_regional_panel_quarterly.csv"
SRC_LEDGER = OVERNIGHT / "02_guidance_ledger.csv"
SRC_ANNUAL = ADR / "01_regional_annual.csv"
SRC_KPI = OVERNIGHT / "02_kpi_panel_quarterly.csv"
SRC_GEO = OVERNIGHT / "10_xbrl_revenue_geography.csv"

REGIONS = ["na", "emea", "latam", "apac"]
LIVE_TARGETS = {"3Q26", "FY2026"}  # no realised actual as of 2026-09-11

COLS = [
    "obs_id", "quarter_or_year", "region", "metric", "lo", "hi", "unit",
    "basis", "phrase_kind", "included", "scoreable", "point_reported",
    "source_path", "source_quote_id", "knowable_from", "note",
]


def _print_date_map() -> dict:
    """quarter (e.g. '2Q26') -> the shareholder-letter print date that first disclosed it."""
    led = pd.read_csv(SRC_LEDGER, parse_dates=["print_date"])
    m = (led.dropna(subset=["print_quarter", "print_date"])
            .groupby("print_quarter")["print_date"].min())
    return {k: v.strftime("%Y-%m-%d") for k, v in m.items()}


def _tenk_map() -> dict:
    """fiscal year -> 10-K filing date, read off the XBRL geography file's own accessions."""
    geo = pd.read_csv(SRC_GEO, parse_dates=["filed", "end"])
    k = geo[geo["form"] == "10-K"]
    out = {}
    for accn, grp in k.groupby("accn"):
        fy = int(grp["end"].dt.year.max())
        d = grp["filed"].min().strftime("%Y-%m-%d")
        out[fy] = min(out.get(fy, d), d)
    # ABNB 10-K filing dates not represented in this extract (documented, not guessed:
    # they are the filing dates of the FY2020 and FY2021 Forms 10-K on EDGAR).
    out.setdefault(2020, "2021-02-26")
    out.setdefault(2021, "2022-02-25")
    out.setdefault(2022, "2023-02-16")
    return out


def build(verbose: bool = True) -> tuple[pd.DataFrame, dict]:
    diag: dict = {}
    pdate = _print_date_map()
    tenk = _tenk_map()
    rows: list[dict] = []

    panel = pd.read_csv(SRC_PANEL)
    panel_src = rel(SRC_PANEL)

    # ---- B1/B2/B3 regional nights growth cells ---------------------------
    for _, r in panel.iterrows():
        qq = r["quarter"]
        for reg in REGIONS:
            basis = str(r.get(f"{reg}_basis", "none"))
            lo, hi = r.get(f"{reg}_nights_yoy_lo"), r.get(f"{reg}_nights_yoy_hi")
            if basis == "none" or pd.isna(lo) or pd.isna(hi):
                continue
            if basis == "bucket":
                phrase, included, block = "bucket_band", True, "B1"
                lo_v, hi_v = float(lo), float(hi)
            elif basis.startswith("derived"):
                phrase, included, block = "derived_residual", False, "B2"
                lo_v, hi_v = float(lo), float(hi)
            elif basis == "numeric":
                phrase, included, block = "stated_integer_rounding", True, "B3"
                lo_v, hi_v = float(lo) - 0.5, float(hi) + 0.5
            else:
                continue
            rows.append({
                "obs_id": f"{block}-{qq}-{reg}-nights_yoy_pct",
                "quarter_or_year": qq, "region": reg, "metric": "nights_yoy_pct",
                "lo": round(lo_v, 4), "hi": round(hi_v, 4), "unit": "pct",
                "basis": "bucket" if basis == "bucket" else ("derived" if basis.startswith("derived") else "letter_integer"),
                "phrase_kind": phrase, "included": included, "scoreable": True,
                "point_reported": np.nan,
                "source_path": panel_src,
                "source_quote_id": f"{qq}:{reg}_phrase",
                "knowable_from": pdate.get(qq, ""),
                "note": str(r.get(f"{reg}_phrase", ""))[:180],
            })

    # ---- B4 regional ADR integers, +/-0.5pp ------------------------------
    for _, r in panel.iterrows():
        qq = r["quarter"]
        for reg in REGIONS:
            for suffix, metric in (("adr_yoy_reported_pct", "adr_yoy_reported_pct"),
                                   ("adr_yoy_exfx_pct", "adr_yoy_exfx_pct")):
                v = r.get(f"{reg}_{suffix}")
                if pd.isna(v):
                    continue
                rows.append({
                    "obs_id": f"B4-{qq}-{reg}-{metric}",
                    "quarter_or_year": qq, "region": reg, "metric": metric,
                    "lo": round(float(v) - 0.5, 4), "hi": round(float(v) + 0.5, 4), "unit": "pct",
                    "basis": "letter_integer", "phrase_kind": "letter_rounded_integer",
                    "included": True, "scoreable": True, "point_reported": float(v),
                    "source_path": panel_src,
                    "source_quote_id": f"{qq}:{reg}_{suffix}",
                    "knowable_from": pdate.get(qq, ""),
                    "note": "letter integer; score on [x-0.5, x+0.5], never as a point",
                })

    # ---- B5 annual 10-K regional nights cells ----------------------------
    ann = pd.read_csv(SRC_ANNUAL)
    ann = ann[ann["region"].isin(REGIONS)]
    for _, r in ann.iterrows():
        yr = int(r["year"])
        prec = float(r["nights_precision_m"])
        v = float(r["nights_m"])
        rows.append({
            "obs_id": f"B5-FY{yr}-{r['region']}-nights_m",
            "quarter_or_year": f"FY{yr}", "region": r["region"], "metric": "nights_m",
            "lo": round(v - prec / 2.0, 4), "hi": round(v + prec / 2.0, 4), "unit": "m_nights",
            "basis": "filed", "phrase_kind": "table_precision",
            "included": True, "scoreable": True, "point_reported": v,
            "source_path": rel(SRC_ANNUAL),
            "source_quote_id": f"{r['source_10k']}:{r['region']}:nights_m",
            "knowable_from": tenk.get(yr, tenk.get(yr + 1, "")),
            "note": f"10-K table precision {prec} m nights ({r['source_10k']})",
        })

    # ---- B6 / B7 guidance -------------------------------------------------
    led = pd.read_csv(SRC_LEDGER, parse_dates=["print_date"])
    g = led[(led["guide_type"].isin(["range", "bucket"]))
            & led["value_low"].notna() & led["value_high"].notna()].copy()

    # B6: quarterly revenue level guide ranges (the 19 scoreable + the LIVE 3Q26)
    b6 = g[(g["metric"] == "revenue_usd_m") & (~g["target_period"].astype(str).str.startswith("FY"))]
    for _, r in b6.iterrows():
        tgt = str(r["target_period"])
        rows.append({
            "obs_id": f"B6-{tgt}-revenue_usd_m",
            "quarter_or_year": tgt, "region": "total", "metric": "revenue_usd_m",
            "lo": float(r["value_low"]), "hi": float(r["value_high"]), "unit": "musd",
            "basis": "letter_bucket", "phrase_kind": "guide_range",
            "included": True, "scoreable": bool(pd.notna(r["actual"])),
            "point_reported": np.nan,
            "source_path": rel(SRC_LEDGER), "source_quote_id": str(r["guide_id"]),
            "knowable_from": r["print_date"].strftime("%Y-%m-%d"),
            "note": ("LIVE guide, scores in no metric or gate" if pd.isna(r["actual"])
                     else f"actual {r['actual']}"),
        })

    # B7: bucket-word guides mapped to the ledger's own band
    b7 = g[g["guide_type"] == "bucket"]
    for _, r in b7.iterrows():
        tgt = str(r["target_period"])
        rows.append({
            "obs_id": f"B7-{tgt}-{r['metric']}-{r['print_quarter']}",
            "quarter_or_year": tgt, "region": "total", "metric": str(r["metric"]),
            "lo": float(r["value_low"]), "hi": float(r["value_high"]), "unit": "pct",
            "basis": "letter_bucket", "phrase_kind": "bucket_word",
            "included": True, "scoreable": bool(pd.notna(r["actual"])),
            "point_reported": np.nan,
            "source_path": rel(SRC_LEDGER), "source_quote_id": str(r["guide_id"]),
            "knowable_from": r["print_date"].strftime("%Y-%m-%d"),
            "note": str(r["quote"])[:180],
        })

    obs = pd.DataFrame(rows)[COLS]
    assert obs["obs_id"].is_unique, "duplicate obs_id"
    assert (obs["hi"] >= obs["lo"]).all(), "an interval has hi < lo"

    # ---------------- counts vs the architect ------------------------------
    counts = {
        "B1_bucket_cells": int((obs["phrase_kind"] == "bucket_band").sum()),
        "B2_derived_cells_excluded": int((obs["basis"] == "derived").sum()),
        "B3_numeric_rounding_cells": int((obs["phrase_kind"] == "stated_integer_rounding").sum()),
        "B4_adr_integers": int((obs["phrase_kind"] == "letter_rounded_integer").sum()),
        "B5_annual_nights_cells": int((obs["phrase_kind"] == "table_precision").sum()),
        "B6_guide_ranges_total": int((obs["phrase_kind"] == "guide_range").sum()),
        "B6_guide_ranges_scoreable": int(((obs["phrase_kind"] == "guide_range") & obs["scoreable"]).sum()),
        "B7_bucket_words_total": int((obs["phrase_kind"] == "bucket_word").sum()),
        "B7_bucket_words_scoreable": int(((obs["phrase_kind"] == "bucket_word") & obs["scoreable"]).sum()),
        "rows_total": int(len(obs)),
        "rows_included": int(obs["included"].sum()),
    }
    diag["counts"] = counts
    target = {"B1_bucket_cells": 28, "B2_derived_cells_excluded": 14,
              "B3_numeric_rounding_cells": 22, "B4_adr_integers": 68,
              "B5_annual_nights_cells": 24, "B6_guide_ranges_scoreable": 19,
              "B7_bucket_words_scoreable": 5}
    diag["counts_vs_architect"] = {k: {"got": counts[k], "architect": v, "match": counts[k] == v}
                                   for k, v in target.items()}
    for k, v in target.items():
        assert counts[k] == v, f"COUNT MISMATCH {k}: got {counts[k]}, architect {v}"

    # the 14 derived rows must be NA 8 + EMEA 6
    dsplit = obs[obs["basis"] == "derived"]["region"].value_counts().to_dict()
    diag["derived_split"] = dsplit
    assert dsplit.get("na") == 8 and dsplit.get("emea") == 6, f"derived split wrong: {dsplit}"

    # ---------------- band-midpoint bias -----------------------------------
    kpi = pd.read_csv(SRC_KPI).set_index("quarter")
    bias_rows = []
    for _, r in panel.iterrows():
        qq = r["quarter"]
        mids, wts = [], []
        for reg in REGIONS:
            if str(r.get(f"{reg}_basis")) != "bucket":
                continue
            lo, hi = r.get(f"{reg}_nights_yoy_lo"), r.get(f"{reg}_nights_yoy_hi")
            w = r.get(f"{reg}_nights_share_est_pct")
            if pd.isna(lo) or pd.isna(hi) or pd.isna(w):
                continue
            mids.append((float(lo) + float(hi)) / 2.0)
            wts.append(float(w))
        if len(mids) != 4:
            continue
        wts = np.array(wts) / np.sum(wts)
        implied = float(np.dot(wts, mids))
        actual = kpi.loc[qq, "nights_yoy_pct"] if qq in kpi.index else np.nan
        if pd.isna(actual):
            continue
        bias_rows.append({"quarter": qq, "band_midpoint_implied_pct": round(implied, 4),
                          "actual_total_nights_yoy_pct": round(float(actual), 4),
                          "bias_pp": round(implied - float(actual), 4)})
    bias = pd.DataFrame(bias_rows)
    if not bias.empty:
        diag["midpoint_bias_mean_pp"] = round(float(bias["bias_pp"].mean()), 4)
        diag["midpoint_bias_last2_mean_pp"] = round(float(bias["bias_pp"].tail(2).mean()), 4)
        diag["midpoint_bias_n"] = int(len(bias))
        bias.to_csv(OUT / "L0_interval_observations_midpoint_bias.csv", index=False)

    out = OUT / "L0_interval_observations.csv"
    header = (
        "# L0_interval_observations.csv -- HARD RULES\n"
        "# 1. basis == 'derived' rows (included == False) are EXCLUDED from every likelihood, "
        "in every package. They are a residual-to-total construction, not a disclosure.\n"
        "# 2. Every row is an INTERVAL [lo, hi]. Never enter a band as its midpoint: the "
        "nights band-midpoint bias measured here is "
        f"{diag.get('midpoint_bias_mean_pp')}pp on average and "
        f"{diag.get('midpoint_bias_last2_mean_pp')}pp over the last two quarters.\n"
        "# 3. Letter integers are scored on [x-0.5, x+0.5]; the 22 stated-integer regional "
        "nights cells are rounding intervals, not equalities.\n"
        "# 4. scoreable == False marks LIVE guides (3Q26 / FY2026) which enter no metric or gate.\n"
    )
    with open(out, "w") as fh:
        fh.write(header)
        obs.to_csv(fh, index=False)

    if verbose:
        print(f"[L0.2] wrote {rel(out)}  rows={len(obs)} (included {counts['rows_included']})")
        for k, v in diag["counts_vs_architect"].items():
            print(f"[L0.2]   {k}: got {v['got']}, architect {v['architect']}, match={v['match']}")
        print(f"[L0.2] band-midpoint bias: mean {diag.get('midpoint_bias_mean_pp')}pp, "
              f"last 2 {diag.get('midpoint_bias_last2_mean_pp')}pp, n={diag.get('midpoint_bias_n')}")
    return obs, diag


if __name__ == "__main__":
    build()
