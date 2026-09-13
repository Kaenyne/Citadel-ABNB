#!/usr/bin/env python
"""Unit tests for the margin harness.

  python analysis/src/margin_build/10_harness_margin/tests.py          # plain runner, exit 0 on pass
  python -m pytest analysis/src/margin_build/10_harness_margin/tests.py -q

Covers: PIT rule (history_as_of and the validator), window membership, baseline arithmetic on
hand-checked cases (seasonal naive / drift / trailing-4 / pct_rev_last4 / guide_implied identity),
the scorer on a toy registry with a known answer (equal and recency weights), the fallback panel.
"""
from __future__ import annotations

import datetime as dt
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

import harness_margin as HM                                          # noqa: E402
from harness_margin import panel, baselines as B, score as S         # noqa: E402
from harness_margin.registry import validate_margin_frame, RegistryError   # noqa: E402

D = dt.date


def _row(**kw):
    base = dict(method="toy", object="obj", target="adj_ebitda_margin_pct", quarter="2025Q3",
                vintage_date=D(2025, 8, 6), horizon_q=0, point=50.0, q50=50.0, window="W1",
                prior_basis="PIT", n_params=1, n_train=20)
    base.update(kw)
    return base


# ------------------------------------------------------------------ PIT rule
def test_history_as_of_includes_same_day_letter_and_excludes_later():
    h = HM.history_as_of(D(2025, 8, 6))
    assert "2025Q2" in set(h["quarter"]), "2Q25 printed 2025-08-06 (same-day letter) must be visible"
    assert "2025Q3" not in set(h["quarter"]), "3Q25 printed 2025-11-06 must NOT be visible"
    hs = HM.history_as_of(D(2025, 8, 6), include_same_day=False)
    assert "2025Q2" not in set(hs["quarter"])
    assert HM.history_as_of(D(2023, 2, 14))["quarter"].tolist()[0] == "2020Q1", "1Q20 knowable from the 424B4"
    assert "2020Q1" not in set(HM.history_as_of(D(2020, 11, 20))["quarter"]), "1Q20 not public before 2020-12-10"


def test_validator_rejects_forecast_made_on_or_after_print():
    bad = pd.DataFrame([_row(quarter="2025Q2", vintage_date=D(2025, 8, 6), window="W1")])
    try:
        validate_margin_frame(bad)
    except RegistryError as e:
        assert "POINT-IN-TIME" in str(e)
    else:
        raise AssertionError("PIT violation was not rejected")


def test_validator_rejects_unknown_target_and_bad_vintage():
    for kw, needle in ((dict(target="ebitda_margin"), "target must be"),
                       (dict(vintage_date=D(2025, 8, 7)), "vintage_date must be")):
        try:
            validate_margin_frame(pd.DataFrame([_row(**kw)]))
        except RegistryError as e:
            assert needle in str(e), str(e)
        else:
            raise AssertionError(f"{kw} was not rejected")


# ------------------------------------------------------------------ windows
def test_window_membership():
    assert len(HM.GUIDE_DATES_W1) == 14 and len(HM.GUIDE_DATES_W2) == 10
    assert HM.windows_for(D(2023, 2, 14), "2023Q1") == ["W1"]
    assert HM.windows_for(D(2024, 2, 13), "2024Q1") == ["W1", "W2"]
    assert HM.windows_for(D(2023, 11, 1), "2024Q1") == ["W1"], "a W1-only vintage never yields a W2 row"
    assert HM.windows_for(D(2026, 8, 6), "2026Q3") == ["LIVE"]
    assert HM.windows_for(HM.TODAY, "2027Q4") == ["LIVE"]
    assert HM.windows_for(D(2026, 5, 7), "2026Q3") == [], "a W1 vintage forecasting a LIVE quarter is dropped"
    try:
        validate_margin_frame(pd.DataFrame([_row(quarter="2023Q2", vintage_date=D(2023, 5, 9), window="W2")]))
    except RegistryError as e:
        assert "window inconsistent" in str(e)
    else:
        raise AssertionError("W2 row for 2023Q2 was not rejected")
    ok = validate_margin_frame(pd.DataFrame([_row(quarter="2026Q4", vintage_date=HM.TODAY, window="LIVE",
                                                  horizon_q=1)]))
    assert len(ok) == 1, "LIVE 2026Q4 must be accepted"


# ------------------------------------------------------------------ baseline arithmetic (hand-checked)
def test_seasonal_naive_drift_trailing4_hand_case():
    t = HM.load_targets().set_index("quarter")
    m = "adj_ebitda_margin_pct"
    vd = D(2025, 8, 6)
    pt, _, _ = B.rule_seasonal_naive(vd, "2025Q3", m)
    assert abs(pt - t.at["2024Q3", m]) < 1e-9                       # 52.47
    pt, _, _ = B.rule_seasonal_naive_drift(vd, "2025Q3", m)
    want = t.at["2024Q3", m] + (t.at["2025Q2", m] - t.at["2024Q2", m])   # 52.47 + (33.69 - 32.53)
    assert abs(pt - want) < 1e-9
    assert abs(want - 53.6210) < 0.01, want
    pt, _, _ = B.rule_trailing4(vd, "2025Q3", m)
    want = np.mean([t.at[q, m] for q in ("2024Q3", "2024Q4", "2025Q1", "2025Q2")])
    assert abs(pt - want) < 1e-9
    assert abs(want - 33.8397) < 0.01, want


def test_pct_rev_last4_hand_case():
    t = HM.load_targets().set_index("quarter")
    vd = D(2025, 8, 6)
    ratio = np.mean([t.at[q, "cor_cash_musd"] / t.at[q, "revenue_musd"]
                     for q in ("2024Q3", "2024Q4", "2025Q1", "2025Q2")])
    assert abs(ratio - 0.17379) < 5e-4, ratio                           # 12.46, 17.22, 22.27, 17.57 -> 17.38%
    rev, leg = B.revenue_forecast_pit(vd, "2025Q3", "PIT")
    assert leg == "guide_cushion" and 4060 < rev < 4200, (rev, leg)     # guide mid 4060 x median cushion
    pt, note, n, rev2, leg2 = B.rule_pct_rev_last4(vd, "2025Q3", "cor_cash_musd", "PIT")
    assert abs(pt - ratio * rev) < 1e-6 and rev2 == rev
    # h=1 uses the naive revenue rule (no guide for 4Q25 at 2025-08-06)
    rev_h1, leg_h1 = B.revenue_forecast_pit(vd, "2025Q4", "PIT")
    g_last = t.at["2025Q2", "revenue_musd"] / t.at["2024Q2", "revenue_musd"]
    assert leg_h1 == "naive" and abs(rev_h1 - t.at["2024Q4", "revenue_musd"] * g_last) < 1e-6


def test_guide_implied_identity_hand_case():
    """At 2025-08-06 the FY25 floor is 34.5%; 1H25 rev 5,368 / EBITDA 1,460; remaining 3Q25 + 4Q25.
    The two implied quarters plus YTD must reproduce exactly 34.5% of the FY revenue estimate."""
    vd = D(2025, 8, 6)
    res, why = B.rule_guide_implied(vd, "2025Q3", "PIT")
    assert res is not None, why
    assert set(res) == {"2025Q3", "2025Q4"}
    t = HM.load_targets().set_index("quarter")
    ytd_rev = t.at["2025Q1", "revenue_musd"] + t.at["2025Q2", "revenue_musd"]
    ytd_e = t.at["2025Q1", "adj_ebitda_musd"] + t.at["2025Q2", "adj_ebitda_musd"]
    assert abs(ytd_rev - 5368) < 1 and abs(ytd_e - 1460) < 1
    fy_rev = ytd_rev + sum(v[2] for v in res.values())
    fy_e = ytd_e + sum(v[0] for v in res.values())
    assert abs(100 * fy_e / fy_rev - 34.5) < 1e-6
    for q, (e, m, rev, note) in res.items():
        assert abs(m - 100 * e / rev) < 1e-9
    assert B.rule_guide_implied(D(2023, 11, 1), "2024Q1", "PIT")[0] is None, "no FY24 guide before 2024-02-13"


def test_seasonal_shares_pit_vs_full():
    s_full, lab = B.seasonal_ebitda_shares(None, "full_sample")
    assert lab == "FY2023-25" and abs(sum(s_full.values()) - 1) < 1e-9
    s_pit, lab_pit = B.seasonal_ebitda_shares(D(2024, 2, 13), "PIT")
    assert lab_pit == "FY2021-23", lab_pit
    s_pit2, lab_pit2 = B.seasonal_ebitda_shares(D(2023, 2, 14), "PIT")
    assert lab_pit2 == "FY2021-22", lab_pit2


# ------------------------------------------------------------------ scorer
def test_scorer_toy_known_answer():
    """Two objects on adj_ebitda_margin_pct, W2 h=0, quarters 2025Q3..2026Q2 (n=4).
    obj A errors +1,+1,+1,+1 -> MAE 1; obj 'seasonal_naive' errors 2,2,2,2 -> ratio 0.5.
    Recency weights anchored at 2026Q2 with half-life 4: 0.5^(3/4), 0.5^(2/4), 0.5^(1/4), 1."""
    t = HM.load_targets().set_index("quarter")
    qs = ["2025Q3", "2025Q4", "2026Q1", "2026Q2"]
    vds = [D(2025, 8, 6), D(2025, 11, 6), D(2026, 2, 12), D(2026, 5, 7)]
    rows = []
    for q, vd in zip(qs, vds):
        a = t.at[q, "adj_ebitda_margin_pct"]
        for obj, meth, e in (("obj", "toy", 1.0), ("seasonal_naive", "baselines-margin", 2.0)):
            rows.append(dict(method=meth, object=obj, target="adj_ebitda_margin_pct", quarter=q, vintage_date=vd,
                             horizon_q=0, point=a + e, q50=a + e, q10=a + e - 3, q90=a + e + 3, window="W2",
                             prior_basis="PIT", n_params=1, n_train=20, spec_id=""))
    reg = pd.DataFrame(rows)
    sb, by_q = S.score_registry(reg)
    a = sb[sb["object"] == "obj"].iloc[0]
    assert a["n"] == 4 and abs(a["mae"] - 1.0) < 1e-9 and abs(a["bias"] - 1.0) < 1e-9
    assert abs(a["mae_ratio_seasonal_naive"] - 0.5) < 1e-9
    assert abs(a["rw_mae"] - 1.0) < 1e-9 and abs(a["rw_mae_ratio_seasonal_naive"] - 0.5) < 1e-9
    assert a["cov80"] == 1.0
    w = S.recency_weights(qs, "2026Q2")
    want = np.array([0.5 ** (3 / 4), 0.5 ** 0.5, 0.5 ** 0.25, 1.0]); want /= want.sum()
    assert np.allclose(w, want)
    # a weighted MAE with unequal errors: errors 4,0,0,0 -> EW 1.0, RW = w[0]*4
    reg2 = reg[reg["object"] == "obj"].copy()
    reg2["point"] = reg2["point"] - 1.0 + np.array([4.0, 0, 0, 0])
    sb2, _ = S.score_registry(pd.concat([reg2, reg[reg["object"] != "obj"]]))
    b = sb2[sb2["object"] == "obj"].iloc[0]
    assert abs(b["mae"] - 1.0) < 1e-9 and abs(b["rw_mae"] - 4 * want[0]) < 1e-9
    assert abs(b["mae_ratio_seasonal_naive"] - 0.5) < 1e-9            # 1.0 / 2.0
    assert abs(b["rw_mae_ratio_seasonal_naive"] - 4 * want[0] / 2.0) < 1e-9
    assert b["beats_seasonal_naive"] and b["rw_beats_seasonal_naive"]


def test_scorer_survives_both_requires_w1_and_w2():
    t = HM.load_targets().set_index("quarter")
    rows = []
    for q, vd, win in (("2023Q1", D(2023, 2, 14), "W1"), ("2023Q2", D(2023, 5, 9), "W1"),
                       ("2024Q1", D(2024, 2, 13), "W1"), ("2024Q1", D(2024, 2, 13), "W2"),
                       ("2024Q2", D(2024, 5, 8), "W1"), ("2024Q2", D(2024, 5, 8), "W2")):
        a = t.at[q, "adj_ebitda_margin_pct"]
        # obj beats the naive in W2 rows but not in the 2023 W1 rows
        e_obj = 0.5 if q.startswith("2024") else 5.0
        rows.append(dict(method="toy", object="obj", target="adj_ebitda_margin_pct", quarter=q, vintage_date=vd,
                         horizon_q=0, point=a + e_obj, q50=a + e_obj, window=win, prior_basis="PIT",
                         n_params=1, n_train=10, spec_id=""))
        rows.append(dict(method="baselines-margin", object="seasonal_naive", target="adj_ebitda_margin_pct",
                         quarter=q, vintage_date=vd, horizon_q=0, point=a + 1.0, q50=a + 1.0, window=win,
                         prior_basis="PIT", n_params=1, n_train=10, spec_id=""))
    sb, _ = S.score_registry(pd.DataFrame(rows))
    o = sb[sb["object"] == "obj"].set_index("window")
    assert bool(o.at["W2", "beats_seasonal_naive"]) and not bool(o.at["W1", "beats_seasonal_naive"])
    assert not bool(o.at["W2", "survives_both_windows"])


# ------------------------------------------------------------------ fallback panel
def test_fallback_panel_agrees_with_ws02_on_adj_ebitda():
    os.environ["MARGIN_HARNESS_PANEL"] = "fallback"
    try:
        fb, info = panel.build_targets(write=False)
    finally:
        os.environ.pop("MARGIN_HARNESS_PANEL", None)
    assert info["source"] == "fallback_repo_panels"
    ws = HM.load_targets()
    m = fb.merge(ws, on="quarter", suffixes=("_fb", "_ws"))
    m = m[m["quarter"].between("2021Q1", "2026Q2") & m["adj_ebitda_musd_fb"].notna()]
    assert len(m) >= 20, len(m)
    d = (m["adj_ebitda_musd_fb"] - m["adj_ebitda_musd_ws"]).abs()
    assert d.max() < 1.5, m.loc[d.idxmax(), ["quarter", "adj_ebitda_musd_fb", "adj_ebitda_musd_ws"]].tolist()
    dm = (m["adj_ebitda_margin_pct_fb"] - m["adj_ebitda_margin_pct_ws"]).abs()
    assert dm.max() < 0.1


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]


def main() -> int:
    failed = 0
    for fn in TESTS:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(TESTS) - failed}/{len(TESTS)} tests passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
