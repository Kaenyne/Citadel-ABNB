import numpy as np, pandas as pd


def test_frozen_mapping_uses_only_pre_freeze_quarters():
    import stages as T, config as C
    qi = np.arange(C.qi(2023, 1), C.qi(2026, 2) + 1)
    idx = pd.DataFrame({"qi": qi, "yoy_vmatch": np.linspace(30, 5, len(qi))})
    y = pd.Series(2 + 0.3 * idx.yoy_vmatch.to_numpy(), index=qi)
    y[C.POST_QIS] += 5.0                                             # a post-RNPL jump must not move the fit
    a, b, n = T.frozen_mapping(idx.set_index("qi").yoy_vmatch, y)
    assert n == C.FREEZE_QI - C.qi(2023, 1) + 1 and abs(b - 0.3) < 1e-9 and abs(a - 2) < 1e-9
