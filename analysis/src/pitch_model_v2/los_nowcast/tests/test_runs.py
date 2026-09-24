"""Synthetic-calendar checks of the run definitions (stock and flow) and the bucket/term arithmetic."""
import gzip
import numpy as np
import pandas as pd
import pytest
from pitch_model_v2.los_nowcast import config as C, runs as R, build as B


def _write(path, rows):
    with gzip.open(path, "wt") as f:
        f.write("listing_id,date,available,minimum_nights,maximum_nights\n")
        for lid, d, a in rows:
            f.write(f"{lid},{d},{a},1,365\n")


@pytest.fixture()
def cal(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "CAL", tmp_path); monkeypatch.setattr(C, "CACHE", tmp_path / "cache")
    days = pd.date_range("2026-06-01", periods=365)
    v1 = []
    for lid in (1, 2):
        for d in days:
            a = "f" if (lid == 1 and pd.Timestamp("2026-06-10") <= d <= pd.Timestamp("2026-06-12")) else "t"
            v1.append((lid, d.date(), a))
    _write(tmp_path / "mk_2026-06-01_calendar.csv.gz", v1)
    days2 = pd.date_range("2026-08-01", periods=365)
    v2 = []
    for lid in (1, 2):
        for d in days2:
            a = "t"
            if lid == 1 and pd.Timestamp("2026-08-10") <= d <= pd.Timestamp("2026-08-14"):
                a = "f"                                   # 5-night new booking
            if lid == 1 and pd.Timestamp("2026-09-01") <= d <= pd.Timestamp("2026-09-30"):
                a = "f"                                   # 30-night new booking
            if lid == 2 and pd.Timestamp("2026-08-02") <= d <= pd.Timestamp("2026-08-04"):
                a = "f"                                   # touches the lower edge (v2 + 1) -> censored
            v2.append((lid, d.date(), a))
    _write(tmp_path / "mk_2026-08-01_calendar.csv.gz", v2)
    return tmp_path


def test_stock_runs(cal):
    r = R.stock_runs("mk", "2026-06-01")
    assert r.len.tolist() == [3] and r.start.iloc[0] == pd.Timestamp("2026-06-10")


def test_flow_runs(cal):
    r = R.flow_runs("mk", "2026-06-01", "2026-08-01").sort_values(["listing_id", "start"]).reset_index(drop=True)
    assert r.len.tolist() == [5, 30, 3]
    assert r.edge.tolist() == [False, False, True]


def test_bucket_and_term():
    r = pd.DataFrame({"listing_id": [1, 1, 2], "len": [5, 30, 100]})
    s = B.bucket_stats(r, None)
    assert s["nights_lt7"] == 5 and s["nights_ge28"] == 30 and s["n_runs_over90"] == 1
    ms = pd.DataFrame([dict(market="m", region="na", side="late", **{f"nights_{b}": v for b, v in zip(C.BUCKETS, (60, 20, 20))}),
                       dict(market="m", region="na", side="old", **{f"nights_{b}": v for b, v in zip(C.BUCKETS, (50, 20, 30))})])
    t = B.los_term(ms, "")
    # d(lt7)=+0.10 * 0, d(7-27)=0, d(28+)=-0.10 * (0.852-1) -> +1.48pp
    assert t["global"] == pytest.approx(1.48)
