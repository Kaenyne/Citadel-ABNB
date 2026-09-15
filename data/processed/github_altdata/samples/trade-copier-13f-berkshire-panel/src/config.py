"""Shared configuration: paths, SEC User-Agent, the filer we mirror, and
Alpaca credential loading.

Credentials are read from the same NewsTrader .env the other repos in
this project use -- no new account setup. Paper trading only.
"""
import os
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
DATA_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# --- The institutional filer we mirror --------------------------------
# Berkshire Hathaway Inc. See README for why this filer specifically.
FILER_NAME = "Berkshire Hathaway Inc"
FILER_CIK = "0001067983"

# --- SEC EDGAR access -------------------------------------------------
# SEC's fair-access policy REQUIRES a User-Agent that declares who is
# making the request, including a contact email, or it returns HTTP 403
# ("Undeclared Automated Tool"). We deliberately default to a generic,
# non-personal contact so no private address is leaked in outbound
# request headers; override via the SEC_EDGAR_UA env var with your own
# real contact if you run this at any volume (SEC uses it to reach you
# about rate issues).
SEC_EDGAR_UA = os.environ.get(
    "SEC_EDGAR_UA",
    "trade-copier-13f research admin@example.com",
)
SEC_HEADERS = {"User-Agent": SEC_EDGAR_UA, "Accept-Encoding": "gzip, deflate"}

# SEC rate limit is 10 requests/sec; we stay well under it.
SEC_REQUEST_SLEEP = 0.2

# --- Alpaca (paper) ---------------------------------------------------
_ENV_PATH = Path.home() / "Documents" / "GitHub" / "NewsTrader" / ".env"


def load_alpaca_creds():
    """Return (api_key, secret_key) from the NewsTrader .env, or (None,
    None) if unavailable. Never raises -- the data/diff/backtest paths
    must work without live credentials.
    """
    if not _ENV_PATH.exists():
        return None, None
    vals = dotenv_values(_ENV_PATH)
    return vals.get("ALPACA_API_KEY"), vals.get("ALPACA_SECRET_KEY")
