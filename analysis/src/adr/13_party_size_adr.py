"""13. Party size -> booked capacity -> ADR ex-FX: the unit-size term, driven by party size.

The chain
  Party size does not enter revenue directly (nights count stays, not guests). It reaches ADR
  because bigger parties book bigger homes, and price is concave in size. The hedonic on 1.4m
  quote-basis listings gives d ln(price) = 0.399 d ln(capacity) + 0.140 d bedrooms, and in
  the 29-market size panel bedrooms move 1.27 per unit of log capacity (nights-weighted), so
  the total elasticity of price to booked capacity is

      eps = 0.399 + 0.140 x 1.27 = 0.58        (listed basis: 0.332 + 0.178 x 1.27 = 0.56)

  size term (pp of ADR y/y) = 100 x eps x d ln(booked capacity)

The series
  Booked capacity is the capacity of the listing behind each review, from the party-size
  study (`abnb_party_size_reviews_quarterly.csv`, 123 markets, fixed 2019 market weights so
  Inside Airbnb adding cities cannot masquerade as a trend). A review is ~one booking, so
  this is booking-weighted capacity per stay, 2011-2026, global and four regions -- the same
  construct as the size panel's capacity per booked night, with fifteen years of history.
  Party size proper (the composition-implied index) is mapped onto capacity with a
  regression of annual log changes, so a people-per-booking forecast can drive the term.

Checks made here, all written to the outputs
  1. The review-based capacity y/y against the 29-market size panel for 2Q26, by region.
  2. The implied size term against the annual decomposition's measured size_mix_pp.
  3. Lead/lag correlation of the size term with ADR ex-FX y/y (global, usable quarters) and
     with disclosed regional ADR ex-FX. Reviews lag stays which lag bookings, so the term is
     tested at leads of 0-2 quarters. This is a small-n test and is reported as such.

Outputs
  data/processed/adr/13_party_size_adr_quarterly.csv   capacity, y/y, size term by region
  data/processed/adr/13_party_size_adr_annual.csv      annual, with party size and beta
  data/processed/adr/13_party_size_adr_checks.csv      the three checks
  data/processed/adr/13_party_size_adr_forecast.csv    bear/base/bull by region, 3Q26-FY27
Run
  py -3.13 analysis/src/adr/13_party_size_adr.py
"""
import numpy as np
import pandas as pd
from scipy import stats

OUT = "data/processed/adr"
PARTY = "data/processed/abnb_party_size_reviews_quarterly.csv"
HED = "data/processed/overnight/06_wtp_hedonic_coefs.csv"
SIZE = "data/processed/adr/08_size_mix_extended_summary.csv"
DEC = "data/processed/adr/07_full_decomposition.csv"
HIST = "data/processed/adr/02b_adr_history_extended.csv"
REGQ = "data/processed/adr/04_regional_quarterly.csv"
ANN = "data/processed/adr/01_regional_annual.csv"

REGMAP = {"north_america": "na", "emea": "emea", "latam": "latam", "apac": "apac", "global": "global"}
REG = ["na", "emea", "latam", "apac"]


def qlabel(q):  # '2025Q2' -> '2Q25'
    return f"{q[5]}Q{q[2:4]}"


def elasticities():
    h = pd.read_csv(HED).set_index(["price_basis", "term"])["coef"]
    s = pd.read_csv(SIZE)
    m = s[s.scope.str.contains("market") & s.market.notna() & s.n_pairs.ge(1)].dropna(subset=["d_bedrooms", "d_mean_log_capacity"])
    w = m.est_nights_b
    bed_per_logcap = float((m.d_bedrooms * w).sum() / (m.d_mean_log_capacity * w).sum())
    eps = {b: float(h[(b, "lacc")] + h[(b, "bedrooms_f")] * bed_per_logcap)
           for b in ("quote_per_night", "listed_nightly")}
    return eps, bed_per_logcap


def main():
    eps, bed_per_logcap = elasticities()
    e = eps["quote_per_night"]
    print(f"bedrooms per unit log capacity {bed_per_logcap:.3f}; total elasticity quote {e:.3f}, "
          f"listed {eps['listed_nightly']:.3f}")

    p = pd.read_csv(PARTY)
    p = p[p.weighting.eq("fixed_2019") & (p.q <= "2026Q2")].copy()
    p["region"] = p.region.map(REGMAP)
    p = p.sort_values(["region", "q"])
    p["ln_cap"] = np.log(p.accommodates_mean)
    p["ln_party"] = np.log(p.implied_party_size_conditional)
    p["cap_yoy_pct"] = p.groupby("region").ln_cap.diff(4) * 100
    p["party_yoy_pct"] = p.groupby("region").ln_party.diff(4) * 100
    p["size_term_pp"] = e * p.cap_yoy_pct
    p["quarter"] = p.q.map(qlabel)
    q = p[["region", "q", "quarter", "reviews", "accommodates_mean", "implied_party_size_conditional",
           "accommodates_ge5", "cap_yoy_pct", "party_yoy_pct", "size_term_pp"]]
    q.to_csv(f"{OUT}/13_party_size_adr_quarterly.csv", index=False)

    # ---- annual, and the party-size -> capacity mapping (beta) --------------------------
    p["year"] = p.q.str[:4].astype(int)
    a = p.groupby(["region", "year"]).agg(cap=("accommodates_mean", "mean"),
                                          party=("implied_party_size_conditional", "mean"),
                                          reviews=("reviews", "sum")).reset_index()
    a["cap_yoy_pct"] = a.groupby("region").cap.transform(lambda s: np.log(s).diff() * 100)
    a["party_yoy_pct"] = a.groupby("region").party.transform(lambda s: np.log(s).diff() * 100)
    a["size_term_pp"] = e * a.cap_yoy_pct
    # The composition-implied index moves AGAINST capacity within a home size (families
    # replacing friend-groups), so it is the wrong driver: regress and record it, then use
    # stated head-counts, whose ratio to booked capacity (the "fill") is what a people-per-
    # booking forecast has to hold constant to map 1:1 onto capacity.
    fit = a[(a.year.between(2013, 2025)) & ~a.year.isin([2020, 2021, 2022])].dropna()
    fit_g = fit[fit.region.eq("global")]
    beta = stats.linregress(fit_g.party_yoy_pct, fit_g.cap_yoy_pct)
    fit_r = fit[fit.region.ne("global")]
    beta_r = stats.linregress(fit_r.party_yoy_pct, fit_r.cap_yoy_pct)
    a["beta_composition_index_global"], a["beta_composition_index_pooled"] = beta.slope, beta_r.slope
    hc = pd.read_csv(PARTY)
    hc = hc[hc.weighting.eq("fixed_2019") & (hc.q <= "2026Q2")].copy()
    hc["region"] = hc.region.map(REGMAP)
    hc["year"] = hc.q.str[:4].astype(int)
    hc = hc.groupby(["region", "year"]).apply(
        lambda g: pd.Series(dict(headcount=np.average(g.headcount_mean.fillna(0), weights=g.headcount_n.fillna(0) + 1e-9),
                                 headcount_n=g.headcount_n.sum()))).reset_index()
    a = a.merge(hc, on=["region", "year"], how="left")
    a["fill_ratio"] = a.headcount / a.cap
    a["headcount_yoy_pct"] = a.groupby("region").headcount.transform(lambda s: np.log(s).diff() * 100)
    fit2 = a[(a.year.between(2013, 2025)) & ~a.year.isin([2020, 2021, 2022])].dropna(subset=["headcount_yoy_pct", "cap_yoy_pct"])
    fit2 = fit2[fit2.headcount_n.ge(2000)]
    beta_hc = stats.linregress(fit2.headcount_yoy_pct, fit2.cap_yoy_pct)
    a["beta_headcount_pooled"] = beta_hc.slope
    a.to_csv(f"{OUT}/13_party_size_adr_annual.csv", index=False)
    print(f"beta (d ln cap per d ln composition index), global annual n={len(fit_g)}: {beta.slope:.2f} "
          f"(r {beta.rvalue:.2f}, p {beta.pvalue:.3f}); regional pooled n={len(fit_r)}: "
          f"{beta_r.slope:.2f} (r {beta_r.rvalue:.2f})")
    print(f"beta (d ln cap per d ln stated head-count), pooled n={len(fit2)}: {beta_hc.slope:.2f} "
          f"(r {beta_hc.rvalue:.2f}, p {beta_hc.pvalue:.3f})")
    g_ = a[a.region.eq("global")].set_index("year")
    print("global fill ratio (stated heads / booked capacity):",
          g_.fill_ratio.loc[[2013, 2016, 2019, 2023, 2025]].round(3).to_dict())

    checks = []
    # ---- check 1: against the 29-market size panel, 2Q26 --------------------------------
    s = pd.read_csv(SIZE)
    panel = s[s.scope.eq("2Q26_region_extended")]
    # region order in that block follows 08's output; recover it from the wedge signature
    order = dict(zip(panel.n_pairs, panel.cap_per_booked_night_yoy_pct))
    lab = {41: "apac", 9: "emea", 13: "latam", 24: "na"}
    for n, v in order.items():
        rg = lab.get(n)
        if rg is None:
            continue
        rv = q[q.region.eq(rg) & q.quarter.eq("2Q26")].cap_yoy_pct.iloc[0]
        checks.append(dict(check="capacity y/y 2Q26: reviews vs size panel", region=rg,
                           reviews_pct=rv, panel_pct=v, panel_n_pairs=n))
    # ---- check 2: against the annual decomposition's measured size term ------------------
    d = pd.read_csv(DEC)
    for y in (2024, 2025):
        ours = a[a.region.eq("global") & a.year.eq(y)].size_term_pp.iloc[0]
        meas = float(d[d.year.eq(y)].size_mix_pp.iloc[0])
        checks.append(dict(check="size term, pp: reviews-based vs 07 decomposition", region="global",
                           year=y, reviews_pct=ours, panel_pct=meas))
    # ---- check 3: lead/lag against ADR ex-FX ------------------------------------------------
    hist = pd.read_csv(HIST)
    hist = hist[hist.usable_for_calibration & hist.adr_yoy_exfx_final.notna()]
    g = q[q.region.eq("global")].set_index("quarter").size_term_pp
    rq = pd.read_csv(REGQ)
    rq = rq[rq.metric.eq("adr_yoy_exfx_pct") & rq.basis.str.contains("disclosed")]
    reg = rq.pivot_table(index="quarter", columns="region", values="value")
    qs = list(q[q.region.eq("global")].quarter)
    for lead in (0, 1, 2):
        # size term at quarter t+lead against ADR at t
        shifted = {qs[i]: g.iloc[i + lead] for i in range(len(qs) - lead)}
        x = hist.quarter.map(shifted)
        m = x.notna()
        r_, p_ = stats.pearsonr(x[m], hist.adr_yoy_exfx_final[m])
        checks.append(dict(check=f"corr size term(t+{lead}) vs global ADR ex-FX(t)", region="global",
                           n=int(m.sum()), r=r_, p=p_))
        for rg in REG:
            gr = q[q.region.eq(rg)].set_index("quarter").size_term_pp
            sh = {qs[i]: gr.iloc[i + lead] for i in range(len(qs) - lead)}
            if rg not in reg.columns:
                continue
            y = reg[rg].dropna()
            x = y.index.map(sh)
            mm = pd.Series(x, index=y.index).notna()
            if mm.sum() < 5:
                continue
            r_, p_ = stats.pearsonr(pd.Series(x, index=y.index)[mm], y[mm])
            checks.append(dict(check=f"corr size term(t+{lead}) vs regional ADR ex-FX(t)", region=rg,
                               n=int(mm.sum()), r=r_, p=p_))
    pd.DataFrame(checks).to_csv(f"{OUT}/13_party_size_adr_checks.csv", index=False)

    # ---- forecast: capacity growth by region, three cases ----------------------------------
    ann = pd.read_csv(ANN)
    share = ann[ann.year.eq(2025)].set_index("region").nights_share_pct / 100
    rows = []
    for rg in REG:
        s8 = q[q.region.eq(rg) & (q.quarter.isin([qlabel(x) for x in
              ["2024Q3", "2024Q4", "2025Q1", "2025Q2", "2025Q3", "2025Q4", "2026Q1", "2026Q2"]]))]
        base = float(s8.cap_yoy_pct.mean())            # trailing 8-quarter capacity growth
        s4 = float(s8.tail(4).cap_yoy_pct.mean())       # last four quarters
        hi = max(base, s4, float(s8.cap_yoy_pct.max()))
        cases = dict(bear=0.0, base=base, bull=hi)     # bear: the mix shift has matured
        for case, cg in cases.items():
            rows.append(dict(region=rg, case=case, capacity_yoy_pct=cg, size_term_pp=e * cg,
                             nights_share_2025=float(share[rg]),
                             basis="bear: capacity mix flat (accommodates_ge5 share stalled 2025-26); "
                                   "base: trailing 8-quarter booked-capacity growth; "
                                   "bull: the stronger of the last 4 quarters and the 8-quarter peak"))
    f = pd.DataFrame(rows)
    for case in ("bear", "base", "bull"):
        sub = f[f.case.eq(case)]
        rows.append(dict(region="global_nights_weighted", case=case,
                         capacity_yoy_pct=float((sub.capacity_yoy_pct * sub.nights_share_2025).sum()),
                         size_term_pp=float((sub.size_term_pp * sub.nights_share_2025).sum()),
                         nights_share_2025=1.0, basis="10-K 2025 nights shares"))
    f = pd.DataFrame(rows)
    f["elasticity"] = e
    # Hook for the team's party-size forecast: at a constant fill ratio, d ln(capacity) =
    # d ln(people per booking), so a people-per-booking growth rate drops straight in here.
    f["party_size_yoy_pct_at_constant_fill"] = f.capacity_yoy_pct
    f.to_csv(f"{OUT}/13_party_size_adr_forecast.csv", index=False)

    pd.set_option("display.width", 250)
    print(q[q.quarter.isin(["2Q24", "2Q25", "4Q25", "1Q26", "2Q26"])].pivot_table(
        index="quarter", columns="region", values=["cap_yoy_pct", "size_term_pp"]).round(2).to_string())
    print(pd.DataFrame(checks).round(3).to_string())
    print(f.round(2).to_string())


if __name__ == "__main__":
    main()
