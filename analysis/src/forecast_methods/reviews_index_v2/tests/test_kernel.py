import numpy as np, pandas as pd


def test_roundtrip_and_realisation():
    import kernel as K, data as D
    M = D.load_kernel()
    rng = np.random.default_rng(3)
    G = pd.Series(100 + rng.normal(0, 5, 24).cumsum(), index=range(8080, 8104))
    S = K.convolve(G, M)
    G2 = K.deconvolve(S, M)
    assert np.allclose(G2.iloc[3:], G.iloc[3:], atol=1e-9)
    assert abs(K.realised_share(8102, 8105, M) - 1.0) < 1e-9            # 3Q25 fully landed by 2Q26
    assert 0.85 < K.realised_share(8104, 8105, M) < 0.95                  # 1Q26 ~87% by 2Q26
