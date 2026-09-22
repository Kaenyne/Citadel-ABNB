import numpy as np, pandas as pd


def test_reproduces_e5_v1_cell_on_w2():
    import config as C, scoring as S
    qq = pd.read_csv(C.E / "index_quarterly.csv"); qq["qi"] = qq.year * 4 + qq.q - 1
    x = qq[(qq.region == "GLOBAL") & (qq.measure == "yoy_all")].set_index("qi").w_reviews * 100
    k = pd.read_csv(C.KPI); k["qi"] = k.year * 4 + k.q - 1; y = k.set_index("qi").nights_m_yoy_pct
    r2 = S.score_window(x, y, *C.WINDOWS["W2"])
    r1 = S.score_window(x, y, *C.WINDOWS["W1"])
    assert abs(r2["wf_ratio_vs_naive"] - 0.683209) < 1e-4 and r2["wf_n"] == 10
    assert abs(r1["wf_ratio_vs_naive"] - 0.837125) < 1e-4 and r1["wf_n"] == 14
    assert abs(r2["mean_err"] - 0.518452) < 1e-4


def test_dm_and_interval_behave():
    import scoring as S
    rng = np.random.default_rng(0); en = rng.normal(0, 2, 40); ef = en * 0.5
    stat, p = S.dm_test(ef, en); assert stat < 0 and p < 0.01
    lo, hi = S.ratio_interval(ef, en); assert lo <= 0.5 <= hi
