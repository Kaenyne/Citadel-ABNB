"""los_nowcast / runs.py — blocked-run extraction from raw Inside Airbnb calendars with DuckDB.

stock_runs: I2a's definition. A run is a maximal block of consecutive dates a listing shows as unavailable (`f`) in one
calendar. flow_runs: construction F. A run is a maximal block of consecutive dates that were available (`t`) in the
earlier vintage and unavailable (`f`) in the later one, i.e. nights newly blocked (booked) between the two dumps.
Both are cached as parquet under CACHE (gitignored)."""
from __future__ import annotations
import re
from pathlib import Path
import duckdb
import pandas as pd
from . import config as C


def cal_path(market: str, date: str) -> Path:
    return C.CAL / f"{market}_{date}_calendar.csv.gz"


def vintages(market: str) -> list[str]:
    return sorted(re.search(r"_(\d{4}-\d{2}-\d{2})_calendar", p.name).group(1) for p in C.CAL.glob(f"{market}_*_calendar.csv.gz"))


def _src(path: Path, status: str) -> str:
    p = str(path).replace("\\", "/")
    return (f"SELECT DISTINCT try_cast(listing_id AS BIGINT) AS lid, try_cast(date AS DATE) AS d "
            f"FROM read_csv('{p}', header=true, all_varchar=true, quote='\"', strict_mode=false) "
            f"WHERE available = '{status}' AND try_cast(listing_id AS BIGINT) IS NOT NULL AND try_cast(date AS DATE) IS NOT NULL")


def _islands(inner: str) -> str:
    return (f"WITH n AS ({inner}), g AS (SELECT lid, d, date_diff('day', DATE '2000-01-01', d) "
            f"- row_number() OVER (PARTITION BY lid ORDER BY d) AS grp FROM n) "
            f"SELECT lid AS listing_id, min(d) AS start, max(d) AS stop, count(*)::INTEGER AS len FROM g GROUP BY lid, grp")


def _con() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("SET threads=2; SET memory_limit='4GB'; SET preserve_insertion_order=false; SET enable_progress_bar=false")
    return con


def stock_runs(market: str, date: str) -> pd.DataFrame:
    dest = C.CACHE / f"stock_{market}_{date}.parquet"
    if dest.exists():
        return pd.read_parquet(dest)
    con = _con()
    df = con.execute(_islands(_src(cal_path(market, date), "f"))).df()
    con.close()
    df["start"] = pd.to_datetime(df.start); df["stop"] = pd.to_datetime(df.stop)
    C.CACHE.mkdir(parents=True, exist_ok=True); df.to_parquet(dest, index=False)
    return df


def flow_runs(market: str, v1: str, v2: str) -> pd.DataFrame:
    """Newly blocked runs between v1 and v2, stay dates in [v2 + 1, v1 + 364]. Edge-censored runs are flagged, not dropped
    here (the filter is applied in build so the counts can be reported)."""
    dest = C.CACHE / f"flow_{market}_{v1}_{v2}.parquet"
    if dest.exists():
        return pd.read_parquet(dest)
    lo = (pd.Timestamp(v2) + pd.Timedelta(days=1)).date(); hi = (pd.Timestamp(v1) + pd.Timedelta(days=C.SHIFT_DAYS)).date()
    inner = (f"SELECT b.lid, b.d FROM ({_src(cal_path(market, v2), 'f')}) b JOIN ({_src(cal_path(market, v1), 't')}) a "
             f"ON a.lid = b.lid AND a.d = b.d WHERE b.d BETWEEN DATE '{lo}' AND DATE '{hi}'")
    con = _con()
    df = con.execute(_islands(inner)).df()
    con.close()
    df["start"] = pd.to_datetime(df.start); df["stop"] = pd.to_datetime(df.stop)
    df["edge"] = (df.start == pd.Timestamp(lo)) | (df.stop == pd.Timestamp(hi))
    C.CACHE.mkdir(parents=True, exist_ok=True); df.to_parquet(dest, index=False)
    return df
