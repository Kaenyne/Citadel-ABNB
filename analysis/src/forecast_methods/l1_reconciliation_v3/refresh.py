"""Annual-anchor reconciliation; all historical slices are strictly dated.

The inherited algebra is copied from v2. The annual ADR term is a soft anchor,
not an extra exact observation and not proof of quarterly identification.
"""
import numpy as np
import pandas as pd
from . import data as D
from .model import Recon


def strict_slice(frame, as_of, column="knowable_from"):
    dates = pd.to_datetime(frame[column], errors="raise")
    if dates.isna().any():
        raise ValueError("Undated observation")
    return frame.loc[dates < pd.Timestamp(as_of)].copy()


class AnchoredRecon(Recon):
    def __init__(self, *args, anchor_sigma=0.05, as_of="2026-09-12", **kwargs):
        super().__init__(*args, **kwargs)
        self.anchor_sigma = float(anchor_sigma)
        if self.anchor_sigma <= 0:
            raise ValueError("anchor_sigma must be positive")
        raw = pd.read_csv(D.DATA / "adr/01_regional_annual.csv")
        iv = strict_slice(D.load_intervals(), as_of)
        pub = iv[(iv.metric == "nights_m") & iv.is_annual].copy()
        pub["year"] = pub.quarter_or_year.str[2:].astype(int)
        pub = pub.groupby(["year", "region"]).knowable_from.max().reset_index()
        self.anchor_frame = raw.merge(pub, on=["year", "region"], how="inner")
        self.anchors = []
        for row in self.anchor_frame.itertuples():
            qs = [f"{row.year}Q{i}" for i in range(1, 5)]
            if row.region in D.REGIONS and all(q in self.qi for q in qs):
                self.anchors.append(([self.qi[q] for q in qs], D.REGIONS.index(row.region), float(row.adr_computed)))

    def residuals(self, theta, wt=None):
        residual = super().residuals(theta, wt)
        _, nights, _, gbv, _ = self.forward(theta)
        anchor = [np.log(gbv[qs, ri].sum() / nights[qs, ri].sum() / val) / self.anchor_sigma
                  for qs, ri, val in self.anchors]
        return np.r_[residual, anchor]

    def theta0(self):
        # Neutral start; unlike v2, no future annual share table initializes PIT fits.
        return np.zeros(self.n_params)


def annual_decomposition(panel, fx):
    p = panel.copy(); p["year"] = p.quarter.str[:4].astype(int)
    ann = p.groupby(["year", "region"])[["nights_m", "gbv_musd"]].sum()
    ann["adr"] = ann.gbv_musd / ann.nights_m
    refs = {2023: (3.10, -1.08), 2024: (3.44, -1.24), 2025: (3.41, -1.58)}
    rows = []
    for year, (ref_exfx, ref_mix) in refs.items():
        a, b = ann.loc[year-1], ann.loc[year]
        s0, s1 = a.nights_m/a.nights_m.sum(), b.nights_m/b.nights_m.sum()
        adr0, adr1 = a.gbv_musd.sum()/a.nights_m.sum(), b.gbv_musd.sum()/b.nights_m.sum()
        mix = 100*((s1-s0)*a.adr).sum()/adr0
        within = 100*(s0*(b.adr-a.adr)).sum()/adr0
        cells = p[p.year == year].merge(fx, on=["quarter", "region"], validate="one_to_one")
        # Prior-year regional dollar weights; current-year quarter nights weights.
        regfx = cells.groupby("region").apply(lambda x: np.average(x.fx_pp, weights=x.nights_m), include_groups=False)
        fxpp = float((a.gbv_musd/a.gbv_musd.sum()*regfx).sum())
        rows.append(dict(year=year, n_regions=4, n_quarters=4, blended_adr_yoy_pct=100*(adr1/adr0-1),
                         within_reported_pp=within, fx_pp=fxpp, within_exfx_pp=within-fxpp,
                         adr_note_exfx_pp=ref_exfx, residual_pp=within-fxpp-ref_exfx,
                         geo_mix_pp=mix, adr_note_mix_pp=ref_mix, mix_residual_pp=mix-ref_mix,
                         basis="full_sample_annual_identity_not_PIT"))
    return pd.DataFrame(rows)


def complete_quarter_arrivals(monthly, as_of=None):
    """No partial-quarter extrapolation; row vintage belongs to the entire download.

    Input fields: series, region, month, value, knowable_from. Output is a calendar
    quarter sum and y/y rate. An as_of applies *before* aggregation and y/y joins.
    """
    d = monthly.copy()
    if as_of is not None:
        d = strict_slice(d, as_of)
    if d.empty:
        return pd.DataFrame(columns=["series", "region", "quarter", "value", "n_months", "knowable_from", "yoy_pct"])
    if d.duplicated(["series", "month"]).any() or (d.value <= 0).any():
        raise ValueError("Duplicate or non-positive arrivals")
    d["quarter"] = pd.to_datetime(d.month).dt.to_period("Q").astype(str)
    a = d.groupby(["series", "region", "quarter"]).agg(value=("value", "sum"), n_months=("month", "nunique"), knowable_from=("knowable_from", "max")).reset_index()
    a = a[a.n_months == 3].copy()
    old = a[["series", "quarter", "value"]].copy()
    old["quarter"] = old.quarter.map(lambda q: D.qadd(q, 4))
    a = a.merge(old.rename(columns={"value":"prior_value"}), on=["series", "quarter"], how="left", validate="one_to_one")
    a["yoy_pct"] = 100*(a.value/a.prior_value-1)
    return a.drop(columns="prior_value")


def covariate_fit(panel, arrivals, as_of):
    """Optional PIT lag-one arrivals covariate for regional nights growth.

    Least squares intercept+slope, >=8 dated overlapping observations. Calling
    with a current download at a historical guide returns no coefficient.
    """
    a = complete_quarter_arrivals(arrivals, as_of)
    if a.empty:
        return pd.DataFrame(columns=["series", "region", "n", "intercept", "beta"])
    p = strict_slice(panel, as_of).copy()
    prev = p[["quarter", "region", "nights_m"]].copy()
    prev["quarter"] = prev.quarter.map(lambda q: D.qadd(q, 4))
    p = p.merge(prev, on=["quarter", "region"], suffixes=("", "_prev"))
    p["y"] = 100*(p.nights_m/p.nights_m_prev-1)
    a["quarter"] = a.quarter.map(lambda q: D.qadd(q, 1))
    rows = []
    for (series, region), group in a.groupby(["series", "region"]):
        matched = p[p.region == region].merge(group[["quarter", "yoy_pct"]], on="quarter").dropna(subset=["y", "yoy_pct"])
        if len(matched) >= 8 and matched.yoy_pct.std() > 1e-8:
            x = np.column_stack([np.ones(len(matched)), matched.yoy_pct])
            coef = np.linalg.lstsq(x, matched.y, rcond=None)[0]
            rows.append(dict(series=series, region=region, n=len(matched), intercept=coef[0], beta=coef[1]))
    return pd.DataFrame(rows, columns=["series", "region", "n", "intercept", "beta"])
