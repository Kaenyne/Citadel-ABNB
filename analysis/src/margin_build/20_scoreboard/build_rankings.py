"""WS20 step 2: rankings, equal and recency weighted, both windows, h=0/1/2.

Pre-registered ranking rules (fixed before reading any table, see note section 2):
  R1 PIT replay only.
  R2 Oracle specs (spec_id containing 'revknown' / 'nightsknown' / 'ebitda_known') are DIAGNOSTIC, not
     forecasts: they substitute the realised revenue / nights / EBITDA. Excluded from headline
     rankings, reported separately.
  R3 Minimum n: 8 in W1, 6 in W2. Thinner cells are listed as 'thin' and never ranked.
  R4 Rank on MAE. Ties broken by n_params (fewer wins).
  R5 Objects that consume Street as an input (method 'street-bias', baseline 'street')
     are flagged consensus_anchored=True and also ranked separately.
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data" / "processed" / "margin_build" / "20_scoreboard"
DOCS = ROOT / "docs" / "margin-build" / "notes"

ORACLE = "revknown|nightsknown|ebitda_known"
MIN_N = {"W1": 8, "W2": 6}
LINES = ["cor_cash_musd", "ops_cash_musd", "pd_cash_musd", "sm_cash_musd",
         "ga_cash_ex_reserves_musd", "total_cash_costs_musd"]
BELOW = ["sbc_musd", "da_musd", "interest_income_musd", "tax_rate_pct",
         "diluted_shares_m", "eps_diluted", "net_income_musd", "op_income_musd",
         "fcf_musd", "cfo_musd", "capex_musd", "fcf_margin_pct"]
HEAD = ["adj_ebitda_margin_pct", "adj_ebitda_musd"]

RATIOS = ["ratio_seasonal_naive", "ratio_trailing4", "ratio_pct_rev_last4",
          "ratio_guide_implied", "ratio_street"]


def tag(m):
    m = m.copy()
    m["oracle"] = m["spec_id"].str.contains(ORACLE, case=False, na=False)
    m["consensus_anchored"] = (m["method"] == "street-bias") | (m["object"] == "street")
    m["thin"] = m.apply(lambda r: r["n"] < MIN_N.get(r["window"], 8), axis=1)
    m["baseline"] = m["method"] == "baselines-margin"
    return m


def rank_block(m, targets, horizons=(0, 1, 2)):
    out = []
    for tgt in targets:
        for h in horizons:
            for win in ["W1", "W2"]:
                for w in ["equal", "recency"]:
                    d = m[(m.target == tgt) & (m.horizon_q == h) & (m.window == win)
                          & (m.weighting == w) & (~m.oracle) & (~m.thin)].copy()
                    if d.empty:
                        continue
                    d = d.sort_values(["mae", "n_params"]).reset_index(drop=True)
                    d["rank"] = np.arange(1, len(d) + 1)
                    d_ind = d[~d.consensus_anchored].copy()
                    d_ind = d_ind.sort_values(["mae", "n_params"])
                    d.loc[d_ind.index, "rank_independent"] = np.arange(1, len(d_ind) + 1)
                    out.append(d)
    if not out:
        return pd.DataFrame()
    cols = (["target", "horizon_q", "window", "weighting", "rank", "rank_independent",
             "method", "object", "spec_id", "n", "mae", "rmse", "bias", "crps",
             "cov80", "cov90"] + RATIOS +
            ["survives_both_windows", "survives_both_windows_eq_and_rw",
             "consensus_anchored", "baseline", "n_params", "hindsight_share"])
    r = pd.concat(out, ignore_index=True)
    return r[[c for c in cols if c in r.columns]]


def main():
    m = tag(pd.read_csv(OUT / "20_scoreboard_master.csv"))

    head = rank_block(m, HEAD)
    head.to_csv(OUT / "20_rankings_headline.csv", index=False)
    lines = rank_block(m, LINES, horizons=(0, 1, 2))
    lines.to_csv(OUT / "20_rankings_lines.csv", index=False)
    below = rank_block(m, BELOW, horizons=(0, 1, 2))
    below.to_csv(OUT / "20_rankings_below_ebitda.csv", index=False)

    # oracle / thin register, so nothing is silently dropped
    excl = m[(m.oracle | m.thin) & m.target.isin(HEAD + LINES + BELOW)]
    excl_cols = ["target", "horizon_q", "window", "weighting", "method", "object",
                 "spec_id", "n", "mae", "oracle", "thin"]
    excl[excl_cols].sort_values(["target", "horizon_q", "window"]).to_csv(
        OUT / "20_excluded_oracle_and_thin.csv", index=False)

    # disagreement table: equal vs recency rank, and W1 vs W2 rank
    piv = head.pivot_table(index=["target", "horizon_q", "method", "object", "spec_id"],
                           columns=["window", "weighting"], values="rank")
    piv.columns = [f"rank_{a}_{b}" for a, b in piv.columns]
    piv = piv.reset_index()
    for win in ["W1", "W2"]:
        a, b = f"rank_{win}_equal", f"rank_{win}_recency"
        if a in piv and b in piv:
            piv[f"disagree_{win}_eq_vs_rw"] = piv[a] - piv[b]
    if "rank_W1_equal" in piv and "rank_W2_equal" in piv:
        piv["disagree_W1_vs_W2_equal"] = piv["rank_W1_equal"] - piv["rank_W2_equal"]
    piv.to_csv(OUT / "20_rank_disagreement.csv", index=False)

    print("headline", head.shape, "lines", lines.shape, "below", below.shape,
          "excluded", excl.shape, "disagree", piv.shape)


if __name__ == "__main__":
    main()
