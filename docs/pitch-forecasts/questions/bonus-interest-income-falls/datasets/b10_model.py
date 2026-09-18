"""B10 bonus-interest-income-falls: P(4Q26 interest income <= 0.90 x 4Q25 $162M = $145.8M).
M7 rule: II = beta x r x avg(cash + STI + restricted + funds held) / 4. numpy/pandas only, seed 20260917.
  py -3.13 docs/pitch-forecasts/questions/bonus-interest-income-falls/datasets/b10_model.py
"""
import pathlib
import numpy as np
import pandas as pd

rng = np.random.default_rng(20260917)
N = 400_000
here = pathlib.Path(__file__).resolve().parent
thr = 0.90 * 162
rows = [("threshold_musd", thr)]

# history (02_panel_quarterly: interest_income, cash_and_investments_total incl. restricted, funds_held_on_behalf; FRED DTB3 quarter means)
h = pd.DataFrame({
    "quarter": ["1Q24", "2Q24", "3Q24", "4Q24", "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"],
    "ii": [202, 226, 207, 183, 173, 190, 180, 162, 155, 183],
    "tbill": [5.234, 5.246, 4.998, 4.401, 4.208, 4.230, 4.099, 3.726, 3.594, 3.624],
    "cash_inv_restricted": [11128, 11286, 11280, 10636, 11532, 11400, 11719, 11049, 12065, 12136],
    "funds_held": [8737, 10342, 6573, 5931, 9175, 11067, 7209, 6959, 10550, 12224]})
h["base_end"] = h["cash_inv_restricted"] + h["funds_held"]
h["avg_base"] = (h["base_end"] + h["base_end"].shift(1)) / 2
h["rule_0.876"] = 0.876 * h["tbill"] / 100 * h["avg_base"] / 4
h["resid_pct"] = (h["ii"] / h["rule_0.876"] - 1) * 100
h["beta_realised"] = h["ii"] / (h["tbill"] / 100 * h["avg_base"] / 4)
h.to_csv(here / "b10_history.csv", index=False)
print(h.to_string())
res = h["resid_pct"].dropna()
rows += [("resid_pct_mean_since_2Q24", res.mean()), ("resid_pct_sd_since_2Q24", res.std(ddof=1)),
         ("beta_realised_mean_last4", h["beta_realised"].iloc[-4:].mean())]


def run(r_mu=4.10, r_sd=0.15, beta_mu=0.88, beta_sd=0.045, cash3=12100, cash4=12000, cash_sd=500,
        fh_gbv=0.127, fh_gbv_sd=0.03, rnpl_hi=0.10, resid_sd_pct=5.0, extra_cash_draw=0.0):
    r = rng.normal(r_mu, r_sd, N)
    beta = rng.normal(beta_mu, beta_sd, N)
    g = rng.normal(fh_gbv, fh_gbv_sd, N)
    rn = rng.uniform(0, rnpl_hi, N)
    fh3 = 7209 * (1 + g) * (1 - rn)
    fh4 = 6959 * (1 + g) * (1 - rn)
    c3 = rng.normal(cash3, cash_sd, N) - extra_cash_draw
    c4 = rng.normal(cash4, cash_sd, N) - extra_cash_draw
    base = ((c3 + fh3) + (c4 + fh4)) / 2
    ii = beta * r / 100 * base / 4 * (1 + rng.normal(0, resid_sd_pct / 100, N))
    return ii, (ii <= thr).mean()


ii, p = run()
rows += [("p_base", p), ("ii_median", np.median(ii)), ("ii_p10", np.quantile(ii, .1)), ("ii_p90", np.quantile(ii, .9)),
         ("ii_yoy_median_pct", (np.median(ii) / 162 - 1) * 100)]
for name, kw in [("rate_3.97_no_more_hikes", dict(r_mu=3.97, r_sd=0.08)), ("rate_4.30_two_hikes", dict(r_mu=4.30)),
                 ("rate_3.25_emergency_cuts", dict(r_mu=3.25, r_sd=0.2)), ("beta_0.83", dict(beta_mu=0.83)),
                 ("beta_0.94_4Q25_realised", dict(beta_mu=0.94)), ("funds_held_flat_yoy", dict(fh_gbv=0.0)),
                 ("rnpl_overlay_20pct", dict(rnpl_hi=0.20)), ("rnpl_overlay_0", dict(rnpl_hi=0.0)),
                 ("cash_minus_3bn_buyback_upsize", dict(extra_cash_draw=3000)),
                 ("cash_minus_3bn_and_rate_3.97", dict(extra_cash_draw=3000, r_mu=3.97)),
                 ("resid_sd_10pct", dict(resid_sd_pct=10.0)),
                 ("all_bear_joint", dict(r_mu=3.75, beta_mu=0.83, fh_gbv=0.0, rnpl_hi=0.20, extra_cash_draw=2000))]:
    _, pp = run(**kw)
    rows.append(("p_" + name, pp))
for name, kw in [("cash_minus_1.5bn", dict(extra_cash_draw=1500)), ("cash_minus_2bn_rate_3.97", dict(extra_cash_draw=2000, r_mu=3.97))]:
    _, pp = run(**kw)
    rows.append(("p_" + name, pp))
# scenario mixture: base regime; moderate buyback upsize (extra $1.5bn drawn, R06-type); large upsize ($3bn); emergency cutting cycle by 4Q26 (Kalshi Oct/Dec cut <= 0.02)
d = dict(rows)
mix = [("base", 0.88, d["p_base"]), ("upsize_1.5bn", 0.07, d["p_cash_minus_1.5bn"]), ("upsize_3bn", 0.03, d["p_cash_minus_3bn_buyback_upsize"]),
       ("emergency_cuts", 0.02, d["p_rate_3.25_emergency_cuts"])]
for lab, w, pp in mix:
    rows.append((f"mix_w_{lab}", w))
    rows.append((f"mix_p_{lab}", pp))
rows.append(("p_mixture", sum(w * pp for _, w, pp in mix)))
rows.append(("avg_base_needed_at_4.10_0.88", thr * 4 / (0.88 * 0.041)))
rows.append(("rate_needed_at_base_19650_beta_0.88", thr * 4 / (0.88 * 19650) * 100))
out = pd.DataFrame(rows, columns=["item", "value"])
out.to_csv(here / "b10_results.csv", index=False)
print(out.to_string())
