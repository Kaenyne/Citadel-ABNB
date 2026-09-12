"""pytest suite for the L0 constraint spine.

Run:
  python -m pytest \
      "analysis/src/forecast_methods/L0/test_l0.py" -q
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd  # noqa: E402
import pytest  # noqa: E402

import l0  # noqa: E402
from _paths import OVERNIGHT  # noqa: E402

Q4_TARGETS = {"4Q22": 1902.0, "4Q23": 2218.0, "4Q24": 2480.0, "4Q25": 2778.0}


# ----------------------------- file 1 -------------------------------------- #
def test_spine_is_72_cells():
    df = l0.load_exact_regional_revenue()
    assert len(df) == 72
    assert (df["basis"] == "filed").sum() == 56
    assert (df["basis"] == "back_out").sum() == 16


def test_filed_is_14_quarters_x_4_regions():
    f = l0.load_exact_regional_revenue("filed")
    assert f["quarter"].nunique() == 14
    assert set(f["region"]) == {"na", "emea", "latam", "apac"}
    assert f.groupby("quarter").size().eq(4).all()
    assert f["period_days"].between(80, 100).all()
    assert not f["quarter"].str.startswith("4Q").any(), "regional revenue is never filed for Q4"


def test_q4_backout_totals_reproduce_to_one_million():
    b = l0.load_exact_regional_revenue("back_out")
    tot = b.groupby("quarter")["revenue_musd"].sum()
    for q, target in Q4_TARGETS.items():
        assert abs(float(tot.loc[q]) - target) <= 1.0, f"{q}: {tot.loc[q]} vs {target}"


def test_worked_check_4q22_na_emea_latam_apac():
    f = l0.load_exact_regional_revenue("filed").set_index(["quarter", "region"])["revenue_musd"]
    nine_m_total = sum(float(f.loc[(q, r)]) for q in ("1Q22", "2Q22", "3Q22")
                       for r in ("na", "emea", "latam", "apac"))
    # 3Q22 regional sum quoted in the addendum
    q3 = {r: float(f.loc[("3Q22", r)]) for r in ("na", "emea", "latam", "apac")}
    assert abs(sum(q3.values()) - 2884.0) <= 1.0
    assert abs(nine_m_total - 6497.0) <= 1.0
    assert abs(8399.0 - nine_m_total - 1902.0) <= 1.0


def test_backouts_positive():
    b = l0.load_exact_regional_revenue("back_out")
    assert (b["revenue_musd"] > 0).all()


def test_regions_sum_to_consolidated_revenue():
    kpi = pd.read_csv(OVERNIGHT / "02_kpi_panel_quarterly.csv").set_index("quarter")["revenue_musd"]
    w = l0.regional_revenue_wide()
    n = 0
    for q, row in w.iterrows():
        if q in kpi.index and pd.notna(kpi.loc[q]):
            assert abs(float(row["total"]) - float(kpi.loc[q])) <= 1.0, q
            n += 1
    assert n >= 18


def test_other_geo_axis_never_enters_the_spine():
    """country:US / us-gaap:NonUsMember / country:FR must not be summed into the
    four-region axis: their 3-month cells would double-count revenue."""
    df = l0.load_exact_regional_revenue()
    assert set(df["region"]) == {"na", "emea", "latam", "apac"}
    w = l0.regional_revenue_wide()
    # if the US axis had leaked in, 1Q22 would be 1509 + 772 = 2281, not 1509
    assert abs(float(w.loc["1Q22", "total"]) - 1509.0) <= 1.0


# ----------------------------- file 2 -------------------------------------- #
def test_derived_rows_excluded_by_default_but_kept_for_audit():
    default = l0.load_interval_observations()
    audit = l0.load_interval_observations(include_derived=True)
    assert (default["basis"] == "derived").sum() == 0
    assert (audit["basis"] == "derived").sum() == 14
    split = audit[audit["basis"] == "derived"]["region"].value_counts().to_dict()
    assert split["na"] == 8 and split["emea"] == 6


def test_architect_block_counts():
    a = l0.load_interval_observations(include_derived=True)
    assert (a["phrase_kind"] == "bucket_band").sum() == 28
    assert (a["phrase_kind"] == "stated_integer_rounding").sum() == 22
    assert (a["phrase_kind"] == "letter_rounded_integer").sum() == 68
    assert (a["phrase_kind"] == "table_precision").sum() == 24
    assert ((a["phrase_kind"] == "guide_range") & a["scoreable"]).sum() == 19
    assert ((a["phrase_kind"] == "bucket_word") & a["scoreable"]).sum() == 5


def test_every_row_is_an_interval_not_a_point():
    a = l0.load_interval_observations(include_derived=True)
    assert (a["hi"] >= a["lo"]).all()
    letters = a[a["phrase_kind"] == "letter_rounded_integer"]
    assert ((letters["hi"] - letters["lo"]) == 1.0).all(), "letter integers must be [x-0.5, x+0.5]"
    stated = a[a["phrase_kind"] == "stated_integer_rounding"]
    assert (stated["hi"] - stated["lo"] >= 1.0).all(), "stated integers are rounding intervals"


def test_live_guides_are_flagged_unscoreable():
    a = l0.load_interval_observations(include_derived=True)
    live = a[~a["scoreable"]]
    assert set(live["quarter_or_year"]) <= {"3Q26", "FY2026"}
    assert not l0.load_interval_observations(include_live=False)["scoreable"].eq(False).any()


def test_pit_filter_respects_knowable_from():
    rows = l0.interval_likelihood_rows(as_of="2024-01-01")
    assert len(rows) > 0
    assert (rows["knowable_from"].astype(str) < "2024-01-01").all()
    assert len(rows) < len(l0.interval_likelihood_rows())


def test_guide_ranges_are_the_letter_ranges():
    a = l0.load_interval_observations(include_derived=True)
    g = a[a["phrase_kind"] == "guide_range"].set_index("quarter_or_year")
    assert (float(g.loc["3Q26", "lo"]), float(g.loc["3Q26", "hi"])) == (4690.0, 4770.0)
    assert bool(g.loc["3Q26", "scoreable"]) is False


# ----------------------------- file 3 -------------------------------------- #
def test_vintage_register_schema():
    r = l0.load_vintage_register()
    for c in ("vendor", "period", "metric", "value", "n_estimates",
              "as_of_timestamp", "url", "source_path"):
        assert c in r.columns
    assert r["register_id"].is_unique


def test_new_register_does_not_clobber_the_lineage_register():
    lin = pd.read_csv(OVERNIGHT / "20_vintage_register.csv", nrows=1)
    assert "series" in lin.columns and "value" not in lin.columns


def test_six_august_pre_guide_street_is_lseg_4610():
    pg = l0.pre_guide_street("2026Q3")
    assert pg is not None
    assert pg["vendor"] == "LSEG"
    assert pg["value"] == 4610.0
    assert pg["as_of_timestamp"] == "2026-08-06"


def test_zacks_4740_is_not_usable_as_the_six_august_street():
    """Zacks $4,740M is a 4 Sep vintage; a PIT query as of 6 Aug must not see it."""
    hit = l0.pit_consensus("revenue", "2026Q3", "2026-08-06", vendor="Zacks")
    assert hit is None
    later = l0.pit_consensus("revenue", "2026Q3", "2026-09-11", vendor="Zacks")
    assert later is not None and later["value"] == 4740.0


def test_pit_consensus_is_strictly_before():
    assert l0.pit_consensus("revenue", "2026Q3", "2026-08-06", role="pre_guide") is None
    hit = l0.pit_consensus("revenue", "2026Q3", "2026-08-07", role="pre_guide")
    assert hit is not None and hit["value"] == 4610.0


def test_seeded_live_anchors():
    av = l0.pit_consensus("revenue", "2026Q4", "2026-09-12", vendor="Alpha Vantage")
    assert av["value"] == 3158.0 and str(av["n_estimates"]) in ("36", "36.0")
    z = l0.pit_consensus("revenue", "2026Q4", "2026-09-12", vendor="Zacks")
    assert z["value"] == 3200.0
    sp26 = l0.pit_consensus("revenue", "FY2026", "2026-09-12", vendor="S&P Global Market")
    sp27 = l0.pit_consensus("revenue", "FY2027", "2026-09-12", vendor="S&P Global Market")
    assert sp26["value"] == 14160.0 and sp27["value"] == 15760.0


def test_vintage_unknown_rows_are_never_pit_usable():
    r = l0.load_vintage_register()
    unknown = r[~r["pit_usable"]]
    assert len(unknown) >= 1
    for _, row in unknown.iterrows():
        stamp = str(row["as_of_timestamp"]).strip()
        missing_stamp = stamp in ("", "nan", "NaT", "None")
        contested = "vintage_unknown" in str(row["note"])
        assert missing_stamp or contested or pd.isna(row["value"])
    # The 2024Q3 pre-guide cell is the documented gap. 16_consensus_at_print_merged.csv
    # supplies $3,840M (LSEG) for it while the same row's notes column still says
    # "NEXT-QUARTER CONSENSUS NOT FOUND"; 04_consensus_at_print.csv has it blank. The value
    # is registered for audit but must never be PIT-usable.
    assert l0.pre_guide_street("2024Q3") is None
    row = r[(r["period"] == "2024Q3") & (r["role"] == "pre_guide")]
    assert len(row) == 1 and float(row["value"].iloc[0]) == 3840.0
    assert bool(row["pit_usable"].iloc[0]) is False
    assert "NEXT-QUARTER CONSENSUS NOT FOUND" in str(row["note"].iloc[0])


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
