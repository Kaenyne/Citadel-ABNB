"""worldcup_premium / config.py — frozen constants of docs/worldcup-premium/PREREG.md (sections 2-3, 8).
Nothing in this file is fitted."""
from __future__ import annotations
import os
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/worldcup_premium"
PREREG = ROOT / "docs/worldcup-premium/PREREG.md"


def _raw_root() -> Path:
    """data/raw is gitignored and lives in the main worktree; use ABNB_RAW, this tree, or the main worktree."""
    if os.environ.get("ABNB_RAW"):
        return Path(os.environ["ABNB_RAW"])
    here = ROOT / "data/raw"
    if (here / "inside_airbnb").exists():
        return here
    common = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--git-common-dir"], capture_output=True, text=True).stdout.strip()
    return (Path(common) if Path(common).is_absolute() else ROOT / common).resolve().parent / "data/raw"


RAW = _raw_root()
IA_MONTHLY = RAW / "inside_airbnb"                 # <market>_<date>_listings.parquet
IA_SNAP = RAW / "inside_airbnb_reviews"            # <country>_<state>_<market>_<date>_listings.csv.gz
IA_CAL = RAW / "inside_airbnb_calendar"            # <market>_<date>_calendar.csv.gz
E_PANEL = ROOT / "data/processed/q3nowcast/E/market_monthly_yoy.csv"
REGIONAL_WIDE = ROOT / "data/processed/adr/04_regional_quarterly_wide.csv"
SCHEDULE = OUT / "wc2026_matches_by_venue.csv"

# ---- section 2: venues (lat, lon), frozen -------------------------------------------------------------------------
VENUES = {
    "SoFi Stadium, Inglewood": (33.9535, -118.3392),
    "MetLife Stadium, East Rutherford": (40.8135, -74.0745),
    "Gillette Stadium, Foxborough": (42.0909, -71.2643),
    "Lincoln Financial Field, Philadelphia": (39.9008, -75.1675),
    "Hard Rock Stadium, Miami Gardens": (25.9580, -80.2389),
    "Mercedes-Benz Stadium, Atlanta": (33.7554, -84.4008),
    "NRG Stadium, Houston": (29.6847, -95.4107),
    "AT&T Stadium, Arlington": (32.7473, -97.0945),
    "Arrowhead Stadium, Kansas City": (39.0489, -94.4839),
    "Lumen Field, Seattle": (47.5952, -122.3316),
    "Levi's Stadium, Santa Clara": (37.4030, -121.9700),
    "BMO Field, Toronto": (43.6332, -79.4186),
    "BC Place, Vancouver": (49.2768, -123.1120),
    "Estadio Azteca, Mexico City": (19.3029, -99.1505),
    "Estadio Akron, Zapopan": (20.6817, -103.4627),
    "Estadio BBVA, Guadalupe": (25.6690, -100.2440),
}
HOST_KM, RING_KM = 75.0, 200.0
NYC_EXCLUDED_FROM_PRICE = {"new-york-city"}          # Local Law 18: 30-night quotes
POST_TOURNAMENT_PLACEBO = {"dallas"}                 # snapshot scraped 2026-07-20

# ---- section 3: nights ---------------------------------------------------------------------------------------------
T_START, T_END = pd.Timestamp("2026-06-11"), pd.Timestamp("2026-07-19")
A_WINDOWS = [(pd.Timestamp("2026-05-14"), pd.Timestamp("2026-06-07")), (pd.Timestamp("2026-07-24"), pd.Timestamp("2026-08-16"))]

# ---- section 4: price sample ---------------------------------------------------------------------------------------
LOS_MIN, LOS_MAX, LEAD_MAX, PPN_MIN, PPN_MAX = 1, 7, 45, 10.0, 5000.0
LEAD_BINS = [-1, 3, 7, 14, 30, 45]
P1_HOSTS = ["los-angeles", "mexico-city"]
P1_CONTROLS = ["chicago", "austin", "nashville", "new-orleans"]
P2_CONTROL_SCRAPE = (pd.Timestamp("2026-06-14"), pd.Timestamp("2026-06-30"))

# ---- section 5: calendar rounds ------------------------------------------------------------------------------------
CAL_HOSTS = ["los-angeles", "mexico-city"]
CAL_CONTROLS = ["chicago", "austin", "nashville", "new-orleans"]
ACTIVE_MAX_BLOCKED = 0.95

# ---- section 7: Paris 2024 analog ----------------------------------------------------------------------------------
PARIS_SNAPS = ["2024-03-16", "2024-05-11", "2024-06-10"]
ROME_SNAPS = ["2024-03-22", "2024-05-17", "2024-06-15"]
OLY = (pd.Timestamp("2024-07-26"), pd.Timestamp("2024-08-11"))
OLY_A = [(pd.Timestamp("2024-07-01"), pd.Timestamp("2024-07-20")), (pd.Timestamp("2024-08-16"), pd.Timestamp("2024-09-05"))]

# ---- section 8: translation -----------------------------------------------------------------------------------------
T_DAYS = 39
SUMMER_FACTOR = {"low": 0.9, "central": 1.0, "high": 1.3}
NIGHTS_Q = {"2Q26": 148.3e6, "4Q25": 121.9e6}
LABEL_LINE_PP = 0.10


def haversine_km(lat1, lon1, lat2, lon2):
    p = np.pi / 180.0
    a = np.sin((lat2 - lat1) * p / 2) ** 2 + np.cos(lat1 * p) * np.cos(lat2 * p) * np.sin((lon2 - lon1) * p / 2) ** 2
    return 12742.0 * np.arcsin(np.sqrt(a))


def nearest_venue(lat: float, lon: float) -> tuple[str, float]:
    d = {v: float(haversine_km(lat, lon, *c)) for v, c in VENUES.items()}
    v = min(d, key=d.get)
    return v, d[v]


def classify(km: float) -> str:
    return "host" if km <= HOST_KM else ("ring" if km <= RING_KM else "control")


def load_schedule() -> pd.DataFrame:
    s = pd.read_csv(SCHEDULE, parse_dates=["date"])
    assert len(s) == 104, f"schedule has {len(s)} matches, expected 104"
    return s


def match_nights(venue: str, schedule: pd.DataFrame) -> set[pd.Timestamp]:
    """Nights of d-1 and d for every match at the venue (PREREG section 3)."""
    out: set[pd.Timestamp] = set()
    for d in schedule.loc[schedule.stadium == venue, "date"]:
        out.update({d - pd.Timedelta(days=1), d})
    return out


def in_windows(d: pd.Series, windows) -> pd.Series:
    m = pd.Series(False, index=d.index)
    for a, b in windows:
        m |= (d >= a) & (d <= b)
    return m
