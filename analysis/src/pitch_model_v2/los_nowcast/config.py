"""los_nowcast / config.py — paths and fixed parameters (docs/pitch-model-v2/lines/los_nowcast_prereg.md)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MAIN = Path(r"C:\Users\krish\citadel-abnb")            # raw Inside Airbnb stores live in the main tree (gitignored)
CAL = MAIN / "data/raw/inside_airbnb_calendar"
LST = MAIN / "data/raw/inside_airbnb"
BYL = MAIN / "data/processed/adr/14c_los_runs_by_listing"
OUT = ROOT / "data/processed/pitch_model_v2/los_nowcast"
CACHE = OUT / "cache"                                   # per-vintage / per-pair run parquet (gitignored, rebuildable)
I2_TERM = ROOT / "data/processed/adrq3/I/I2_los_term.csv"
WC_RESULTS = "docs/worldcup-premium/RESULTS.md section 3b (branch krish/worldcup-premium)"

# region map and weights: 14c (analysis/src/adr/14c_los_runs_panel.py)
REGION = {
    "new-york-city": "na", "los-angeles": "na", "chicago": "na", "austin": "na", "nashville": "na", "new-orleans": "na",
    "san-diego": "na", "paris": "emea", "london": "emea", "barcelona": "emea", "rome": "emea", "sydney": "apac",
    "mexico-city": "latam", "buenos-aires": "latam", "rio-de-janeiro": "latam", "sao-paulo": "latam", "santiago": "latam",
    "bogota": "latam", "belize": "latam", "tokyo": "apac", "singapore": "apac", "bangkok": "apac", "taipei": "apac",
    "hong-kong": "apac", "melbourne": "apac", "brisbane": "apac", "tasmania": "apac", "western-australia": "apac",
    "barossa-valley": "apac", "sunshine-coast": "apac", "mornington-peninsula": "apac", "northern-rivers": "apac",
    "mid-north-coast": "apac", "barwon-south-west-vic": "apac",
}
TENK_W = {"na": 0.296, "emea": 0.403, "latam": 0.169, "apac": 0.131}
REG_MIN = {"new-york-city", "los-angeles"}              # regulatory night minimums; out of every aggregate (I2 / 14c)
RATIO = {"lt7": 1.0, "n7_27": 0.966, "ge28": 0.852}     # 14a price ratios by stay-length bucket
BUCKETS = list(RATIO)
CAP = 90                                                # runs over 90 nights are host blocks (14c)
CLOSURE = 180                                           # F: a listing with more newly blocked nights than this closed its calendar
LEAD = (7, 97)                                          # S: lead-matched window (I2b)
TOL_F, TOL_S = 31, 45                                   # prior-year vintage tolerance, days
LEN_TOL_F = 14                                          # F: prior-year interval length within 14 days of 2026's (amendment 1)
SHIFT_DAYS = 364
IN_CORE_LOS = 0.30                                      # the H decomposition's 2026 LOS fill, carried in the core
BOOT_N, BOOT_SEED = 2000, 7
F_MIN_MARKETS = 12

# quarter mapping (2026 vintage months)
F_PAIRS_2026 = {"2Q26": ("03", "06"), "3Q26": ("06", "08")}
S_KIND_2026 = {"2Q26": ("2026-06-01", "2026-07-10"), "3Q26": ("2026-08-01", "2026-09-05")}

# World Cup (prereg section 3)
WC_HOSTS = {"los-angeles", "mexico-city"}
WC_CONTROLS = {"austin", "chicago", "nashville", "new-orleans", "san-diego", "buenos-aires", "rio-de-janeiro",
               "sao-paulo", "santiago", "bogota", "belize"}
WC_END = "2026-07-19"
WC_POST = ("2026-08-01", "2026-09-15")
WC_NIGHTS_M = {"covered": 1.53, "scaled": 1.53 * 104 / 69}
WC_F2Q26 = (1.0, 0.5)
Q2_NIGHTS_M = 148.3
WC_MATERIAL_PP = 0.02
