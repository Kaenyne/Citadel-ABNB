"""reviews_index_v2 — paths, constants and the frozen pass lines. Nothing in this file is fitted.
Spec and pre-registration: docs/revenue-forecast-strategy/05_backtests/REVIEWS_INDEX_v2.md"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
E = ROOT / "data/processed/q3nowcast/E"
E23 = ROOT / "data/processed/q3nowcast_v2/E"
OUT = ROOT / "data/processed/forecast_methods/reviews_index_v2"
FIG = OUT / "figures"
NOTE = ROOT / "docs/revenue-forecast-strategy/05_backtests/REVIEWS_INDEX_v2.md"
KPI = ROOT / "data/processed/abnb_driver_history_quarterly.csv"
EUROSTAT = ROOT / "data/processed/eurostat_platform_nights_monthly.csv"
K2 = ROOT / "data/processed/forecast_methods/kernel_leadtime_v2/K2_M_matrix.csv"
E6_NOWCAST = E / "q3_2026_nowcast.csv"

# region map and weights exactly as analysis/src/q3nowcast/E4_build_index.py
REGION_OF_COUNTRY = {
    "united-states": "NAM", "canada": "NAM",
    "argentina": "LatAm", "belize": "LatAm", "brazil": "LatAm", "chile": "LatAm",
    "colombia": "LatAm", "mexico": "LatAm",
    "australia": "APAC", "china": "APAC", "japan": "APAC", "new-zealand": "APAC",
    "singapore": "APAC", "taiwan": "APAC", "thailand": "APAC",
}
FY25_NIGHTS_SHARE = {"NAM": 28.3, "EMEA": 41.6, "LatAm": 17.9, "APAC": 12.3}
# Eurostat codes exactly as analysis/src/q3nowcast/E5_backtest.py
EU_CODE = {"austria": "AT", "belgium": "BE", "czech-republic": "CZ", "denmark": "DK", "france": "FR",
           "germany": "DE", "greece": "EL", "hungary": "HU", "ireland": "IE", "italy": "IT",
           "latvia": "LV", "malta": "MT", "portugal": "PT", "spain": "ES", "sweden": "SE",
           "the-netherlands": "NL", "switzerland": "CH", "norway": "NO"}

LAG_TRIM_MONTHS = 2            # months up to and including the dump month dropped for posting lag
PRIMARY = "yoy_vmatch_mix"     # v2.1 (18 Sep, Theo): stay-quarter regional mix weights; "yoy_vmatch" = v2 with FY25 annual weights
VMATCH_DAYS = (300, 430)       # prior vintage must be this many days older than the latest (E4 rule)


def qi(year, q):
    return int(year) * 4 + int(q) - 1


def ymi(year, month):
    return int(year) * 12 + int(month) - 1


FREEZE_QI = qi(2025, 2)                                      # Stage C calibration ends here
POST_QIS = [qi(2025, 3), qi(2025, 4), qi(2026, 1), qi(2026, 2)]
WINDOWS = {"W1": (qi(2022, 1), qi(2023, 1)), "W2": (qi(2023, 1), qi(2024, 1))}   # (window start, first scored)
PANEL_START, PANEL_END, PANEL_SCORE_START = ymi(2023, 1), ymi(2026, 3), ymi(2024, 1)
RNPL_US_LAUNCH_YMI = ymi(2025, 8)
NEVER_TREATED = set(c for c in EU_CODE) | {"turkey", "south-africa", "kenya", "brazil"}

PREREG = {
    "A1_beta_p_max": 0.01,
    "A2_diff_p_max": 0.05,
    "A5_median_ratio_max": 0.75,
    "B1_ratio_max": 0.75,
    "C1_mean_gap_min_bands": 1.0,
    "C1_quarters_min": 3,
    "C1_quarter_min_bands": 0.5,
    "beta_B_bundle_pts": [2.0, 3.0],
    "windows": {k: list(v) for k, v in WINDOWS.items()},
    "post_quarters": POST_QIS,
    "freeze_qi": FREEZE_QI,
    "primary_measure": "yoy_vmatch",
    "lag_trim_months": LAG_TRIM_MONTHS,
    "panel_window_ymi": [PANEL_START, PANEL_END, PANEL_SCORE_START],
}

# ---- Stage E: the view. Inputs from the record, not fitted here (DEC ids cited). ----
KPI_PANEL = ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv"     # unearned fees, GBV (reported, ex-FX)
BASE_PATH = [  # quarter, base level (m), y/y %, decomposition text, DEC
    dict(q="3Q26", qi=qi(2026, 3), base_m=146.8, base_yoy=9.886, decomposition="0.288 x NA +5.60 + 0.712 x ex-NA +11.62 (mechanism)", dec="DEC-0029"),
    dict(q="4Q26", qi=qi(2026, 4), base_m=131.8, base_yoy=8.12, decomposition="reference +8.90 - 0.78 ex-NA fee-and-cancellation lap", dec="DEC-0019"),
    dict(q="1Q27", qi=qi(2027, 1), base_m=169.02, base_yoy=8.21, decomposition="0.291 x NA +2.31 + 0.709 x ex-NA +10.773 - 0.742 fee/cancel lap - 0.363 ex-NA RNPL lap (40%) + 1.0 event", dec="DEC-0025"),
    dict(q="2Q27", qi=qi(2027, 2), base_m=157.10, base_yoy=5.93, decomposition="0.291 x NA +2.31 + 0.709 x ex-NA +10.452 - 0.742 - 0.907 ex-NA RNPL lap (full) - 0.5 World Cup lap", dec="DEC-0025"),
    dict(q="3Q27", qi=qi(2027, 3), base_m=155.96, base_yoy=6.23, decomposition="0.291 x NA +2.31 + 0.709 x ex-NA +10.131 - 0.742 - 0.907", dec="DEC-0025"),
    dict(q="4Q27", qi=qi(2027, 4), base_m=139.77, base_yoy=6.05, decomposition="0.291 x NA +2.31 + 0.709 x ex-NA +9.810 - 0.742 - 0.907", dec="DEC-0025"),
]
FY26_BASE_M, FY27_BASE_M, FY27_BASE_YOY = 583.11, 621.84, 6.64
STREET = {  # nights consensus in the record
    "3Q26": dict(mean_m=149.0, low_m=147.0, high_m=151.0, n=28, source="Bloomberg MODL 12 Sep 2026 (DEC-0005)"),
    "4Q26": dict(mean_m=134.0, low_m=None, high_m=None, n=None, source="final_nights.md section 4.6"),
}
BASE_3Q25_M, BASE_4Q25_M = 133.6, 121.9
RNPL_PRE_QIS = list(range(qi(2023, 1), qi(2025, 2) + 1))    # 1Q23-2Q25
RNPL_POST_QIS = POST_QIS                                    # 3Q25-2Q26
