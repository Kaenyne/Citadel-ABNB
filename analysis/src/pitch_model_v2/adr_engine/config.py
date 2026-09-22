"""adr_engine / config.py — paths, frozen constants and the pre-registered pass lines for the ADR line v1.
Governing pre-registration: docs/pitch-model-v2/lines/adr_fx_prereg.md (git blob 0495e5f3, 21 Sep 2026).
Nothing in this file is fitted."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data/processed/pitch_model_v2/adr_engine"
FIG = ROOT / "docs/pitch-model-v2/lines/figures"
KPI_PANEL = ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv"
LEDGER = ROOT / "data/processed/overnight/02_guidance_ledger.csv"
REGIONAL_ANNUAL = ROOT / "data/processed/adr/01_regional_annual.csv"
H_COMPONENTS = ROOT / "data/processed/q3nowcast/H/adr_history_components.csv"
I_MIX_3Q26 = ROOT / "data/processed/adrq3/I/I_mix_terms_3q26.csv"
K4_NOWCAST = ROOT / "data/processed/adrv3/K/K4_residual_nowcast.csv"
CARD_V3 = ROOT / "data/processed/adrv3/P/adr_card_v3.csv"
N1_CARD = ROOT / "data/processed/adrv3/N/N1_fx_choice_card.csv"
FX_DAILY = OUT / "fx_daily_2026-09-21.csv"          # FRED refresh, this engine's own copy (fetch_fx.py)
FX_LAST_OBS = pd.Timestamp("2026-09-18")
XLSX = ROOT / "model/ABNB_official_model.xlsx"

H10_LAG_DAYS = 7          # H.10 publishes weekly with about a one-week lag (B4 §2 convention)
TENK_LAG_DAYS = 7         # 10-K Geographic Mix table knowable 7 days after the 4Q letter print date
BDAY_60 = 59              # "day 60" origin = first day of quarter + 59 days

# Within-region destination-currency baskets, FROZEN (WS-B / adrv3-N judgement weights, collapsed to FRED bilaterals;
# 01b_basket_weights_used.csv: EMEA OTHER_EUR_LINKED -> EUR, LatAm OTHER_LATAM -> BRL, APAC OTHER_APAC -> AUD).
KAPPA = {
    "na":    {"USD": 0.90, "CAD": 0.08, "MXN": 0.02},
    "emea":  {"EUR": 0.70, "GBP": 0.25, "USD": 0.05},
    "latam": {"BRL": 0.55, "MXN": 0.38, "USD": 0.07},
    "apac":  {"AUD": 0.55, "JPY": 0.20, "KRW": 0.10, "INR": 0.07, "USD": 0.08},
}
REGIONS = ["na", "emea", "latam", "apac"]
CCYS = ["EUR", "GBP", "BRL", "MXN", "JPY", "AUD", "KRW", "CAD", "INR"]

# Prior on the regional pass-through scale (pre-registered): beta_r ~ Normal(1, 0.25^2); sigma ~ HalfNormal(1pp)
BETA_PRIOR_MEAN, BETA_PRIOR_SD, SIGMA_PRIOR_SD = 1.0, 0.25, 1.0

# Disclosed ADR-FX target: 17 quarters 2Q22..2Q26; half-width 0.5pp except the two half-point ex-FX quarters
HALF_POINT_QUARTERS = {"3Q23", "4Q23"}
TARGET_QUARTERS = ["2Q22", "3Q22", "4Q22", "1Q23", "2Q23", "3Q23", "4Q23", "1Q24", "2Q24", "3Q24", "4Q24",
                   "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]
WINDOWS = {"W1": ["1Q23", "2Q23", "3Q23", "4Q23", "1Q24", "2Q24", "3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"],
           "W2": ["1Q24", "2Q24", "3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]}
PASS_RATIO = 0.75                       # promotion line: point-RMSE ratio to naive at O2 and O3, both windows
ORIGINS = ["O1", "O2", "O3"]
FORWARD_QUARTERS = ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27"]
ASOF_DATES = {"2026-09-21": "this build (FRED through 18 Sep)", "2026-10-02": "memo / pitch date",
              "2026-11-05": "3Q26 print, 4Q26 guide", "2027-02-11": "4Q26 print, FY27 guide"}
BOOT_BLOCK, BOOT_PATHS, BOOT_START = 20, 4000, pd.Timestamp("2015-01-02")
USD_SHIFT = 0.05                        # D5's one-sigma parallel dollar device, comparability only

# Street (Bloomberg MODL, screenshot 12 Sep 2026, Krish; V1 dossier rows 48-49). No FY rows exist anywhere.
STREET_ADR = {"3Q26": (177.06, 173.71, 179.12, 26), "4Q26": (171.33, None, None, 25)}
# Nights line (DEC-0029 / DEC-0019 / DEC-0025), for the GBV cross-check only
NIGHTS_BASE_M = {"3Q26": 146.8, "4Q26": 131.8, "1Q27": 169.02, "2Q27": 157.10, "3Q27": 155.96, "4Q27": 139.77}


def qlabel_to_period(q: str) -> pd.Period:
    return pd.Period(year=2000 + int(q[2:]), quarter=int(q[0]), freq="Q")


def period_to_qlabel(p: pd.Period) -> str:
    return f"{p.quarter}Q{str(p.year)[2:]}"


def prior_quarter(q: str, k: int = 1) -> str:
    return period_to_qlabel(qlabel_to_period(q) - k)
