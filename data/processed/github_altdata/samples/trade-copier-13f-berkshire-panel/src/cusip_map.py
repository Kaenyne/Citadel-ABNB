"""Map 13F CUSIPs to tradeable tickers.

13F filings disclose CUSIP + issuer name, but NOT tickers, and Alpaca
orders need tickers. We resolve CUSIP -> ticker via OpenFIGI's free,
documented mapping API (https://www.openfigi.com/api) -- no scraping, no
key required at low volume (keyless limit is small, so we batch and
cache aggressively to data/cusip_ticker.json).

Not every CUSIP resolves to a US-listed common stock: options, foreign
lines, and delisted names return nothing usable and are cached as None
so we never re-query them and never try to trade them.
"""
import json
import time

import requests

from config import DATA_DIR

_CACHE_PATH = DATA_DIR / "cusip_ticker.json"
_OPENFIGI_URL = "https://api.openfigi.com/v3/mapping"

# Manual overrides for CUSIPs OpenFIGI's KEYLESS endpoint cannot resolve.
# These are almost all foreign-domiciled issuers whose 13F CUSIP is a CINS
# (starts with a letter), for which the free tier returns "No identifier
# found." Every entry below is a public, verifiable CUSIP -> US-listed
# ticker fact, not an estimate. Names OpenFIGI can't resolve AND that are
# genuinely messy (Liberty Media tracking stocks, delisted/acquired lines)
# are intentionally left out -- they'll be reported as unmapped and skipped,
# never guessed.
_OVERRIDES: dict[str, str] = {
    "H1467J104": "CB",     # Chubb Ltd (Switzerland)
    "G0403H108": "AON",    # Aon plc (Ireland)
    "G6683N103": "NU",     # Nu Holdings Ltd (Brazil/Cayman)
    "G6693N103": "NU",     # Nu Holdings Ltd (alt CUSIP)
    "G85158106": "STNE",   # StoneCo Ltd (Brazil/Cayman)
    "G0176J109": "ALLE",   # Allegion plc (Ireland)
    "82968B103": "SIRI",   # Sirius XM Holdings
    "92556H206": "PARA",   # Paramount Global class B
}

# Keyless OpenFIGI: max 10 jobs/request, ~25 requests/min. Stay under it.
_BATCH = 10
_SLEEP = 3.0


def _load_cache() -> dict:
    if _CACHE_PATH.exists():
        return json.loads(_CACHE_PATH.read_text())
    return {}


def _save_cache(cache: dict) -> None:
    _CACHE_PATH.write_text(json.dumps(cache, indent=2, sort_keys=True))


def _normalize(ticker: str | None) -> str | None:
    # OpenFIGI writes share classes as "HEI/A"; Alpaca expects "HEI.A".
    return ticker.replace("/", ".") if ticker else ticker


def _pick_ticker(rows: list[dict]) -> str | None:
    """Prefer a US-listed common stock; fall back to first US row."""
    for want in ("Common Stock", "REIT", "Depositary Receipt"):
        for r in rows:
            if r.get("exchCode") == "US" and r.get("securityType2") == want:
                return _normalize(r.get("ticker"))
    for r in rows:
        if r.get("exchCode") == "US" and r.get("ticker"):
            return _normalize(r.get("ticker"))
    return None


def resolve(cusips: list[str], use_cache: bool = True) -> dict[str, str | None]:
    """Return {cusip: ticker or None} for the given CUSIPs.

    Cached results (including cached None) are never re-queried.
    """
    cache = _load_cache() if use_cache else {}
    # Apply documented overrides first, so they win over any stale cached None.
    for cusip, ticker in _OVERRIDES.items():
        if cache.get(cusip) is None:
            cache[cusip] = ticker
    unknown = [c for c in dict.fromkeys(cusips)
               if c not in cache and c not in _OVERRIDES]

    for i in range(0, len(unknown), _BATCH):
        batch = unknown[i:i + _BATCH]
        body = [{"idType": "ID_CUSIP", "idValue": c} for c in batch]
        try:
            resp = requests.post(_OPENFIGI_URL, json=body,
                                 headers={"Content-Type": "application/json"},
                                 timeout=30)
            if resp.status_code == 429:
                time.sleep(_SLEEP * 3)
                resp = requests.post(_OPENFIGI_URL, json=body,
                                     headers={"Content-Type": "application/json"},
                                     timeout=30)
            resp.raise_for_status()
            results = resp.json()
        except Exception as e:
            print(f"  openfigi batch failed ({e}); leaving {len(batch)} unmapped")
            continue

        for cusip, res in zip(batch, results):
            rows = res.get("data", []) if isinstance(res, dict) else []
            cache[cusip] = _pick_ticker(rows) if rows else None
        _save_cache(cache)
        if i + _BATCH < len(unknown):
            time.sleep(_SLEEP)

    return {c: cache.get(c) for c in cusips}
