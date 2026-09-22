"""adr_engine / posterior.py — full posterior of the regional pass-through (V1) on all 17 disclosed quarters.
Descriptive: the promoted leg is decided by the walk-forward, not by this fit. Writes fx_weights_posterior.csv."""
import numpy as np, pandas as pd, warnings
from . import config as C, fx_data as F, walkforward as W, exposure as E

def main():
    warnings.filterwarnings("ignore")
    daily = F.load_daily(); shares = F.gbv_shares(); tg = F.disclosed_targets()
    full = W.build_full_design(daily, shares, tg)
    X = full[C.REGIONS].values; y = full.y.values; h = full.h.values
    mp = E.fit_v1_map(X, y, h)
    post = E.fit_v1_nuts(X, y, h)
    rows = [{"region": r, "map": mp["beta"][i]} for i, r in enumerate(C.REGIONS)]
    if post is not None:
        b = post["beta_draws"]
        for i, r in enumerate(C.REGIONS):
            rows[i].update({"post_mean": float(b[:, i].mean()), "hdi90_lo": float(np.percentile(b[:, i], 5)),
                            "hdi90_hi": float(np.percentile(b[:, i], 95)), "p_gt_1": float((b[:, i] > 1).mean())})
        rows.append({"region": "sigma_pp", "map": mp["sigma"], "post_mean": float(post["sigma_draws"].mean()),
                     "hdi90_lo": float(np.percentile(post["sigma_draws"], 5)), "hdi90_hi": float(np.percentile(post["sigma_draws"], 95))})
        print(post["summary"])
        np.save(C.OUT / "fx_beta_draws.npy", b)
    out = pd.DataFrame(rows); out["n"] = len(y); out["prior"] = "Normal(1, 0.25^2); sigma HalfNormal(1); interval likelihood"
    out.to_csv(C.OUT / "fx_weights_posterior.csv", index=False); print(out.round(3).to_string(index=False))

if __name__ == "__main__":
    main()
