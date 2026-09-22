import numpy as np, pandas as pd


def test_fe_ols_recovers_beta_and_wild_p_small():
    import panel as P
    rng = np.random.default_rng(7); rows = []
    for g in range(18):
        fe = rng.normal(0, 0.3); x = rng.normal(0, 0.2, 39); y = fe + 0.5 * x + rng.normal(0, 0.05, 39)
        rows += [dict(code=f"C{g}", ymi=i, x=x[i], y=y[i]) for i in range(39)]
    df = pd.DataFrame(rows)
    beta, se, d, xd, yd, resid = P.fe_ols(df, "y", "x", "code")
    assert abs(beta - 0.5) < 0.05
    p, t = P.wild_cluster_p(d, xd, yd, "code", B=299)
    assert p < 0.02
