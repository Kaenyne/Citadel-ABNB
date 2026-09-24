"""worldcup_premium / run.py — rebuild everything in docs/worldcup-premium/PREREG.md end to end (exit 0).
    PYTHONPATH=analysis/src py -3.13 -m worldcup_premium.run
Raw inputs are read from data/raw (this tree, $ABNB_RAW, or the main worktree). Outputs: data/processed/worldcup_premium/."""
from __future__ import annotations
import json
import subprocess
import time
import warnings
import numpy as np
import pandas as pd
from . import config as C, quotes as Q, availability as V, translate as T


def main() -> None:
    warnings.filterwarnings("ignore")
    t0 = time.time(); C.OUT.mkdir(parents=True, exist_ok=True)
    blob = subprocess.run(["git", "hash-object", str(C.PREREG)], capture_output=True, text=True).stdout.strip()
    print(f"PREREG blob {blob}; raw root {C.RAW}")
    sched = C.load_schedule()
    snaps = Q.snapshot_files()
    geo = Q.geography(snaps); geo.to_csv(C.OUT / "01_geography.csv", index=False)
    print("geography:", geo.cls.value_counts().to_dict())

    q1 = Q.p1_panel(geo, sched); p1 = Q.run_p1(q1, geo, sched)
    p1["coef"].to_csv(C.OUT / "10_p1_coef.csv", index=False); p1["p3"]["coef"].to_csv(C.OUT / "12_p3_coef.csv", index=False)
    q1.groupby(["market", "scrape"]).agg(n=("logp", "size"), T_share=("T_share", "mean"), M_share=("M_share", "mean")).to_csv(C.OUT / "10_p1_sample.csv")
    pd.DataFrame([{"pair": k, "stat": v} for k, v in p1["perm"].items()]).to_csv(C.OUT / "10_p1_permutation.csv", index=False)
    print(f"P1 n {p1['n']} listings {p1['clusters']}: pooled premium {p1['pooled']['premium']:+.4f} "
          f"[{p1['pooled']['premium_lo']:+.4f}, {p1['pooled']['premium_hi']:+.4f}]; perm rank {p1['perm_rank']}/15; LOCO {p1['loco']}")

    q2 = Q.p2_cross(geo, snaps, sched); p2 = Q.run_p2(q2)
    p2["coef"].to_csv(C.OUT / "11_p2_coef.csv", index=False)
    print(f"P2 n {p2['n']} markets {p2['clusters']}; host match quotes {p2['host_match_quotes']}")

    v = V.run_v(geo, sched)
    v["daily"].to_csv(C.OUT / "20_calendar_daily_U.csv", index=False); v["v1"].to_csv(C.OUT / "21_v1_X.csv", index=False)
    v["v1_did"].to_csv(C.OUT / "21_v1_did.csv", index=False); v["v2"].to_csv(C.OUT / "22_v2_match_spike.csv", index=False)
    v["v3"].to_csv(C.OUT / "23_v3_common.csv", index=False); v["timing"].to_csv(C.OUT / "23_v3_timing.csv", index=False)
    v["placebo_2025"]["table"].to_csv(C.OUT / "24_v3b_placebo_2025.csv", index=False)

    a_all, a_did = V.run_a1(); a_all.to_csv(C.OUT / "30_a1_paris_rome.csv", index=False); a_did.to_csv(C.OUT / "30_a1_did.csv", index=False)

    g4 = T.v4_reviews(geo); g4.to_csv(C.OUT / "40_v4_reviews.csv", index=False); v4 = T.v4_summary(g4)
    hn = T.host_nights(geo, snaps, sched); hn.to_csv(C.OUT / "50_host_nights.csv", index=False)
    tr = T.translate(hn, v["timing"], p1, sched); tr["effects"].to_csv(C.OUT / "51_translation.csv")

    summ = {"prereg_blob": blob, "run_at": pd.Timestamp.now().isoformat(timespec="seconds"), "seconds": round(time.time() - t0, 1),
            "p1": {"n": p1["n"], "listings": p1["clusters"], "pooled": p1["pooled"], "by_host": p1["by_host"], "loco": p1["loco"],
                   "perm_rank_of_15": p1["perm_rank"], "p3": {k: p1["p3"][k] for k in ("premium", "premium_lo", "premium_hi")}},
            "p2": {"n": p2["n"], "markets": p2["clusters"], "hosts": p2["hosts"], "controls": p2["controls"],
                   "host_match_quotes": p2["host_match_quotes"], "leave_one_host_out": p2["leave_one_host_out"]},
            "v1_did": v["v1_did"].to_dict("records"), "v3_timing": v["timing"].to_dict("records"),
            "v3b_placebo_2025": {k: v["placebo_2025"][k] for k in ("X_LA", "X_controls_mean", "excess_pp")},
            "a1_did": a_did.to_dict("records"), "v4": v4,
            "translation": {"matches_covered": tr["matches_covered"], "scale": tr["scale"], "f": tr["f"], "premium": tr["premium"],
                            "effects": tr["effects"].reset_index().to_dict("records"), "label": tr["label"],
                            "host_nights_share_nyc": float(hn[hn.market == "new-york-city"].N_T_central.sum() / hn.N_T_central.sum())}}
    (C.OUT / "00_summary.json").write_text(json.dumps(summ, indent=2, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o)))
    print(json.dumps(summ, indent=2, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o)))


if __name__ == "__main__":
    main()
