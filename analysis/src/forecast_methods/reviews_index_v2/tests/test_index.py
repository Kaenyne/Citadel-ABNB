import numpy as np, pandas as pd


def _toy():
    # two markets, one region each, 30 months, latest dump 2026-08, prior dump 2025-08
    rows = []
    for mkt, reg_c in [("united-states_x_a", "united-states"), ("france_x_b", "france")]:
        for dump, base in [("2026-08-15", 100), ("2025-08-15", 90)]:
            for i in range(2024 * 12, 2026 * 12 + 8):
                rows.append(dict(market_key=mkt, dump_date=dump, ymi=i, n_reviews=base + (i % 12),
                                 n_reviews_mature12=base // 2, n_listings=10))
    return pd.DataFrame(rows)


def test_vintage_selection_and_trim(monkeypatch):
    import data as D, config as C
    mv = D.load_counted.__wrapped__(_toy()) if hasattr(D.load_counted, "__wrapped__") else D.tag(_toy())
    latest, prior = D.select_vintages(mv)
    assert latest.dump_date.unique().tolist() == ["2026-08-15"] and prior.dump_date.unique().tolist() == ["2025-08-15"]
    assert latest.ymi.max() == C.ymi(2026, 6) and prior.ymi.max() == C.ymi(2025, 6)   # two months trimmed


def test_vmatch_arithmetic():
    import data as D, index as I
    latest, prior = D.select_vintages(D.tag(_toy()))
    my = I.market_monthly(latest, prior)
    r = my[(my.market_key == "france_x_b") & (my.ymi == 2026 * 12 + 3)].iloc[0]     # Apr 2026
    assert r.n_vm_cur == 100 + 3 and r.n_vm_prior == 90 + 3                         # prior dump, Apr 2025
    assert r.n_lag12 == 100 + 3                                                       # same dump, Apr 2025
    s, _ = I.ratio_of_sums(my[my.ymi == 2026 * 12 + 3], ["ymi"], "yoy_vmatch")
    assert abs(s.iloc[0] - (206 / 186 - 1)) < 1e-12


def test_global_quarterly_uses_fy25_weights():
    import data as D, index as I, config as C
    latest, prior = D.select_vintages(D.tag(_toy()))
    my = I.market_monthly(latest, prior)
    g, reg = I.global_quarterly(my, "yoy_vmatch")
    q = C.qi(2026, 1)
    w = C.FY25_NIGHTS_SHARE
    expect = (reg.loc[q, "NAM"] * w["NAM"] + reg.loc[q, "EMEA"] * w["EMEA"]) / (w["NAM"] + w["EMEA"])
    assert abs(g.loc[q] - expect) < 1e-12
