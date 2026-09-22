"""Stage E — the view. (1) Our nights numbers against the Street with the probability our read assigns to the
Street's number. (2) The RNPL evidence that exists: the unearned-fees-vs-GBV divergence (the option written),
the disclosed cancellation-rate step (the option exercised), the stays gap (consistent with). (3) The forward
path arithmetic, quarter by quarter, with the Street beside it. Reads the record; fits nothing."""
import json
import numpy as np, pandas as pd
from scipy import stats
import config as C


def _qi_from_label(s):
    return C.qi(2000 + int(s[2:4]), int(s[0]))


def view_vs_street():
    c3 = json.loads((C.OUT / "stage_c3_3q26.json").read_text())
    mu, sd = c3["implied_nights_yoy"], c3["band_pp"]
    rows = []
    for b in C.BASE_PATH:
        st = C.STREET.get(b["q"]); base_prev = None
        row = dict(quarter=b["q"], base_m=b["base_m"], base_yoy=b["base_yoy"], dec=b["dec"], decomposition=b["decomposition"])
        if st:
            prev = C.BASE_3Q25_M if b["q"] == "3Q26" else C.BASE_4Q25_M
            st_yoy = (st["mean_m"] / prev - 1) * 100
            row.update(street_m=st["mean_m"], street_yoy=st_yoy, street_low_m=st["low_m"], street_high_m=st["high_m"], street_n=st["n"],
                       base_minus_street_m=b["base_m"] - st["mean_m"], base_minus_street_pp=b["base_yoy"] - st_yoy)
            if b["q"] == "3Q26":
                row.update(v2_read_yoy=mu, v2_band_pp=sd, v2_read_m=prev * (1 + mu / 100),
                           v2_lo_m=prev * (1 + (mu - sd) / 100), v2_hi_m=prev * (1 + (mu + sd) / 100),
                           street_z_vs_v2=(st_yoy - mu) / sd,
                           p_print_at_or_above_street=float(1 - stats.norm.cdf((st_yoy - mu) / sd)),
                           p_print_at_or_above_street_low=float(1 - stats.norm.cdf(((st["low_m"] / prev - 1) * 100 - mu) / sd)),
                           p_print_at_or_above_base=float(1 - stats.norm.cdf((b["base_yoy"] - mu) / sd)))
            else:
                row.update(street_z_vs_v2_band=(st_yoy - b["base_yoy"]) / sd)
        rows.append(row)
    rows.append(dict(quarter="FY26", base_m=C.FY26_BASE_M, base_yoy=np.nan, dec="DEC-0029/0019", decomposition="1Q26 156.2 + 2Q26 148.3 + 3Q26 146.8 + 4Q26 131.8"))
    rows.append(dict(quarter="FY27", base_m=C.FY27_BASE_M, base_yoy=C.FY27_BASE_YOY, dec="DEC-0025", decomposition="sum of the four 2027 quarters over FY26 583.11"))
    return pd.DataFrame(rows)


def rnpl_evidence():
    k = pd.read_csv(C.KPI_PANEL); k["qi"] = k.quarter.map(_qi_from_label); k = k.set_index("qi").sort_index()
    out = []
    for gcol, label in [("gbv_yoy_pct", "GBV reported"), ("gbv_yoy_exfx_pct", "GBV ex-FX")]:
        sp = (k.unearned_fees_yoy_pct - k[gcol]).rename("spread")
        pre = sp.reindex(C.RNPL_PRE_QIS).dropna(); post = sp.reindex(C.RNPL_POST_QIS).dropna()
        t, p = stats.ttest_ind(post, pre, equal_var=False)
        for q in list(pre.index) + list(post.index):
            out.append(dict(comparator=label, qi=q, quarter=k.loc[q, "quarter"], period="pre" if q in pre.index else "post",
                            uf_yoy=k.loc[q, "unearned_fees_yoy_pct"], gbv_yoy=k.loc[q, gcol], spread_pp=sp[q],
                            z_vs_pre=(sp[q] - pre.mean()) / pre.std(ddof=1), pre_mean=pre.mean(), pre_sd=pre.std(ddof=1),
                            welch_t=t, welch_p_two_sided=p, n_pre=len(pre), n_post=len(post)))
    return pd.DataFrame(out)


def run_stage_e():
    v = view_vs_street(); v.to_csv(C.OUT / "stage_e_view_vs_street.csv", index=False)
    r = rnpl_evidence(); r.to_csv(C.OUT / "stage_e_rnpl_evidence.csv", index=False)
    return v, r
