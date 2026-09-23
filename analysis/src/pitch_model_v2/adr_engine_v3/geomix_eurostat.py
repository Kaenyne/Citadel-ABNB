"""adr_engine / geomix_eurostat.py — upgrade 1 to the sub-regional geographic-mix term (adr_v2_geomix_prereg.md §4):
re-weight the within-EMEA country mix with Eurostat short-stay **platform** nights instead of the Inside Airbnb
panel's own market counts.

The term is unchanged in form
    mix_r(t) = [Σ_c s_c(t−4)(1+g_c(t)) P_c] / [(1+g_r(t)) Σ_c s_c(t−4) P_c] − 1,   subgeo(t) = Σ_r w_r mix_r(t)
Only the EMEA base-quarter share vector s_c(t−4) is replaced (and, in one variant, g_c too). Everything else —
the price levels P_c, the region GBV weights w_r, the three non-EMEA rows, the forward roll — is the frozen
geomix.py construction, so any move in the sub-regional term is attributable to the weights alone.

Weights. `data/processed/eurostat_platform_nights_monthly.csv` (Eurostat tour_ce_omn12, "nights spent in short-stay
accommodation offered via collaborative-economy platforms", monthly, 2018-01..2026-03, 31 geos, no gaps) is summed to
quarters. 18 of the panel's 21 EMEA countries are in it; the United Kingdom, Turkey and South Africa are not (they are
not in the EU/EEA reporting frame), so they **keep their Inside Airbnb panel share** and the Eurostat countries are
scaled to the remaining 1 − s_panel(UK+TR+ZA). Eurostat countries with no market in the panel (PL, HR, RO, BG, CY, EE,
FI, LT, LU, SI, SK, IS, LI) stay at zero weight, exactly as they are today — the reweighting moves weight *between*
panel countries, it cannot add countries the panel cannot grow.

Growth. Variant A keeps the panel's vintage-matched country growth g_c. Variant B uses Eurostat's own country nights
y/y where it exists (panel growth for UK/TR/ZA) — a different object: all platforms, all guests, and it stops at 1Q26.

Prices. Base = `country_price_levels_usd.csv` (n_listed-weighted mean of the June-2026 median listed entire-home price
per market, USD). Sensitivity = the same aggregation of `rw_mean_listed_usd` (review-weighted mean listed price), the
partial upgrade-4 price basis. Malta and Switzerland carry no price in either basis and take the EMEA median, as in
geomix.py.

Run:  cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -W ignore -m pitch_model_v2.adr_engine.geomix_eurostat
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from . import config as C, geomix as GM

EUROSTAT_MONTHLY = C.ROOT / "data/processed/eurostat_platform_nights_monthly.csv"

# Eurostat geo code -> Inside Airbnb panel country name (EL = Greece, UK/TR/ZA are outside the Eurostat frame)
ISO_TO_COUNTRY = {
    "AT": "austria", "BE": "belgium", "CH": "switzerland", "CZ": "czech-republic", "DE": "germany",
    "DK": "denmark", "EL": "greece", "ES": "spain", "FR": "france", "HU": "hungary", "IE": "ireland",
    "IT": "italy", "LV": "latvia", "MT": "malta", "NL": "the-netherlands", "NO": "norway",
    "PT": "portugal", "SE": "sweden",
}
NOT_IN_EUROSTAT = ["united-kingdom", "turkey", "south-africa"]
FWD = C.FORWARD_QUARTERS
DIFF_QUARTERS = ["2025Q3", "2025Q4", "2026Q1", "2026Q2"]     # 2H25-1H26, the registered differential window
LAST_BASE_Q = "2026Q2"                                        # last quarter with a complete panel cross-section


# ---------------------------------------------------------------- Eurostat nights

def eurostat_quarterly() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(quarterly platform nights by Eurostat geo, coverage of the panel's 18 countries within the EMEA frame).
    Only quarters with all three months present are kept."""
    m = pd.read_csv(EUROSTAT_MONTHLY, parse_dates=["month"])
    cols = [c for c in m.columns if c.endswith("_nights") and not c.startswith("eu27")]
    n = m.set_index("month")[cols].rename(columns=lambda c: c[:-7])
    n["q"] = n.index.to_period("Q")
    full = n.groupby("q").size() == 3
    qn = n.groupby("q").sum().loc[full[full].index]
    panel_iso = [i for i in ISO_TO_COUNTRY if i in qn.columns]
    cov = pd.DataFrame({
        "q": qn.index, "eurostat_nights_all": qn.sum(axis=1).values,
        "eurostat_nights_panel18": qn[panel_iso].sum(axis=1).values,
    })
    cov["panel18_share_of_eurostat"] = cov.eurostat_nights_panel18 / cov.eurostat_nights_all
    return qn, cov


def eurostat_growth(qn: pd.DataFrame) -> pd.DataFrame:
    """Country nights y/y (%) from the Eurostat quarterly table, columns renamed to panel country names."""
    g = (qn / qn.shift(4) - 1) * 100
    keep = [i for i in ISO_TO_COUNTRY if i in g.columns]
    return g[keep].rename(columns=ISO_TO_COUNTRY)


# ---------------------------------------------------------------- prices

MIN_USD = 5.0     # Geneva/Vaud/Zurich carry 0.20-0.30 USD in the capture store (broken price field); dropped, as in
                  # the build behind country_price_levels_usd.csv, which has no Switzerland row


def country_prices(basis: str = "median_listed_usd") -> pd.DataFrame:
    """One USD level per country: n_listed-weighted mean over its priced markets in the June-2026 capture store.
    basis='median_listed_usd' reproduces country_price_levels_usd.csv exactly; 'rw_mean_listed_usd' is the
    review-weighted-mean sensitivity (upgrade 4, partial)."""
    m = pd.read_csv(C.OUT / "market_price_levels_capture_2026.csv").dropna(subset=[basis])
    m = m[m[basis] >= MIN_USD]
    rows = []
    for (ctry, reg), x in m.groupby(["country", "region"]):
        rows.append({"country": ctry, "region": reg,
                     "usd_level": float(np.average(x[basis], weights=x.n_listed)), "n_markets_priced": len(x)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- shares

def emea_shares(panel_base: pd.Series, eur_base: pd.Series | None) -> tuple[pd.Series, float]:
    """Blend: UK/TR/ZA keep their panel share; the Eurostat countries share the rest in proportion to Eurostat
    nights in the same base quarter. Returns (share vector on the panel's country index, share kept from the panel)."""
    s = panel_base / panel_base.sum()
    if eur_base is None:
        return s, float("nan")
    keep = [c for c in NOT_IN_EUROSTAT if c in s.index]
    w_keep = float(s[keep].sum())
    e = eur_base.reindex([c for c in s.index if c not in keep]).dropna()
    out = pd.Series(0.0, index=s.index)
    out[keep] = s[keep]
    out[e.index] = (1 - w_keep) * e / e.sum()
    missing = [c for c in s.index if c not in keep and c not in e.index]
    if missing:                                   # a panel country with no Eurostat row in this quarter: keep panel
        out[missing] = s[missing]
        out = out / out.sum()
    return out, w_keep


def _mix(s: pd.Series, gr: pd.Series, P: pd.Series) -> tuple[float, float]:
    g_reg = float((s * gr).sum())
    num = float((s * (1 + gr) * P).sum()); den = (1 + g_reg) * float((s * P).sum())
    return (num / den - 1) * 100, g_reg * 100


# ---------------------------------------------------------------- history

def emea_history(cp: pd.DataFrame, share_src: str = "eurostat", growth_src: str = "panel") -> pd.DataFrame:
    """Within-EMEA mix by quarter. share_src in {'panel','eurostat'}; growth_src in {'panel','eurostat'}."""
    d = pd.read_csv(C.OUT / "stays_yoy_by_country_vmatch.csv")
    d = d[d.region == "EMEA"].copy()
    price = cp.set_index("country").usd_level
    reg_med = float(cp[cp.region == "EMEA"].usd_level.median())
    d["P"] = d.country.map(price); d["imputed"] = d.P.isna(); d.loc[d.imputed, "P"] = reg_med
    qn, _ = eurostat_quarterly(); eg = eurostat_growth(qn)
    eur_q = qn.rename(columns=ISO_TO_COUNTRY)[[c for c in ISO_TO_COUNTRY.values()]]
    rows = []
    for q, x in d.groupby("q"):
        x = x.dropna(subset=["P", "n_prior", "stays_yoy_pct"]).set_index("country")
        if len(x) < 2:
            continue
        per = pd.Period(q, freq="Q"); base = per - 4
        eur_base = eur_q.loc[base] if (share_src == "eurostat" and base in eur_q.index) else None
        if share_src == "eurostat" and eur_base is None:
            continue
        s, w_keep = emea_shares(x.n_prior, eur_base)
        gr = x.stays_yoy_pct / 100.0
        n_eur_g = 0
        if growth_src == "eurostat":
            if per not in eg.index:
                continue
            eu_g = eg.loc[per].reindex(x.index) / 100.0
            n_eur_g = int(eu_g.notna().sum())
            gr = eu_g.fillna(gr)
        mix, g_reg = _mix(s, gr, x.P)
        rows.append({"quarter": f"{per.quarter}Q{str(per.year)[2:]}", "q": str(per), "base_q": str(base),
                     "mix_pp": mix, "region_growth_pct": g_reg, "n_countries": len(x),
                     "share_src": share_src, "growth_src": growth_src,
                     "share_kept_from_panel": w_keep, "n_growth_eurostat": n_eur_g,
                     "share_imputed_price": float(s[x.imputed].sum())})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- forward (same rule as geomix_*_forward.csv)

def emea_forward(cp: pd.DataFrame, share_src: str = "eurostat", growth_src: str = "panel") -> pd.DataFrame:
    """Forward 3Q26-4Q27: g_c = region rate (regional_growth_forward.csv) + the country's 2H25-1H26 average
    differential to its region; base shares start at the last complete base quarter, are rolled once with that
    quarter's realised growth and then rolled each step. Reproduces geomix_within_region_forward.csv exactly when
    share_src='panel', growth_src='panel'."""
    d = pd.read_csv(C.OUT / "stays_yoy_by_country_vmatch.csv"); d = d[d.region == "EMEA"].copy()
    rg = pd.read_csv(C.OUT / "regional_growth_forward.csv").set_index("quarter")
    price = cp.set_index("country").usd_level
    reg_med = float(cp[cp.region == "EMEA"].usd_level.median())
    d["P"] = d.country.map(price); d["imputed"] = d.P.isna(); d.loc[d.imputed, "P"] = reg_med
    qn, _ = eurostat_quarterly(); eg = eurostat_growth(qn)
    eur_q = qn.rename(columns=ISO_TO_COUNTRY)[[c for c in ISO_TO_COUNTRY.values()]]

    diff_qs = DIFF_QUARTERS if growth_src == "panel" else [q for q in DIFF_QUARTERS if pd.Period(q, "Q") in eg.index]
    diffs: dict[str, list[float]] = {}
    for q in diff_qs:
        y = d[d.q == q].dropna(subset=["n_prior", "stays_yoy_pct"]).set_index("country")
        per = pd.Period(q, "Q")
        eur_base = eur_q.loc[per - 4] if (share_src == "eurostat" and (per - 4) in eur_q.index) else None
        s0, _ = emea_shares(y.n_prior, eur_base)
        gr = y.stays_yoy_pct / 100.0
        if growth_src == "eurostat":
            gr = (eg.loc[per].reindex(y.index) / 100.0).fillna(gr)
        g_reg = float((s0 * gr).sum())
        for c, g in gr.items():
            diffs.setdefault(c, []).append(float(g) - g_reg)
    dif = pd.Series({c: float(np.mean(v)) for c, v in diffs.items()})

    base = d[d.q == LAST_BASE_Q].dropna(subset=["n_prior", "stays_yoy_pct"]).set_index("country")
    per0 = pd.Period(LAST_BASE_Q, "Q")
    eur_base = eur_q.loc[per0 - 4] if (share_src == "eurostat" and (per0 - 4) in eur_q.index) else None
    s, w_keep = emea_shares(base.n_prior, eur_base)
    P, imp = base.P, base.imputed
    dif = dif.reindex(s.index).fillna(0.0)
    gr0 = base.stays_yoy_pct / 100.0                     # realised last quarter, one roll to reach the first base
    if growth_src == "eurostat" and per0 in eg.index:
        gr0 = (eg.loc[per0].reindex(base.index) / 100.0).fillna(gr0)
    s = s * (1 + gr0) / (1 + float((s * gr0).sum()))
    rows = []
    for q in FWD:
        gr = float(rg.loc[q, "g_emea"]) / 100.0 + dif
        mix, g_reg = _mix(s, gr, P)
        rows.append({"region": "EMEA", "quarter": q, "q": str(C.qlabel_to_period(q)), "mix_pp": mix,
                     "region_growth_pct": g_reg, "n_countries": len(s), "share_src": share_src,
                     "growth_src": growth_src, "share_kept_from_panel": w_keep,
                     "share_imputed_price": float(s[imp].sum())})
        s = s * (1 + gr) / (1 + g_reg / 100.0)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- term assembly

def term_with_emea(emea: pd.DataFrame, forward: bool = False) -> pd.DataFrame:
    """GBV-weighted sub-regional term with only the EMEA rows replaced by `emea` (quarter, mix_pp)."""
    f = "geomix_within_region_forward.csv" if forward else "geomix_within_region.csv"
    w = pd.read_csv(C.OUT / f)
    rep = emea.set_index("quarter").mix_pp
    keep = w[(w.region != "EMEA") | (~w.quarter.isin(rep.index))].copy()
    new = w[(w.region == "EMEA") & (w.quarter.isin(rep.index))].copy()
    new["mix_pp"] = new.quarter.map(rep)
    return GM.subregional_term(pd.concat([keep, new], ignore_index=True))


def main() -> None:
    qn, cov = eurostat_quarterly()
    cp_med, cp_rw = country_prices("median_listed_usd"), country_prices("rw_mean_listed_usd")
    cov.to_csv(C.OUT / "geomix_eurostat_coverage.csv", index=False)

    specs = [("panel", "panel", cp_med, "median"), ("eurostat", "panel", cp_med, "median"),
             ("eurostat", "eurostat", cp_med, "median"), ("eurostat", "panel", cp_rw, "rw_mean"),
             ("panel", "panel", cp_rw, "rw_mean"), ("eurostat", "eurostat", cp_rw, "rw_mean")]
    hist, fwd = [], []
    for ss, gs, cp, pb in specs:
        h = emea_history(cp, ss, gs); h["price_basis"] = pb; hist.append(h)
        f = emea_forward(cp, ss, gs); f["price_basis"] = pb; fwd.append(f)
    H = pd.concat(hist, ignore_index=True); F = pd.concat(fwd, ignore_index=True)
    H.to_csv(C.OUT / "geomix_eurostat_emea_mix.csv", index=False)
    F.to_csv(C.OUT / "geomix_eurostat_emea_forward.csv", index=False)

    # shares actually used, for the record (base quarters 1Q22-2Q25 plus the forward's starting base)
    srows = []
    d = pd.read_csv(C.OUT / "stays_yoy_by_country_vmatch.csv"); d = d[d.region == "EMEA"]
    eur_q = qn.rename(columns=ISO_TO_COUNTRY)[[c for c in ISO_TO_COUNTRY.values()]]
    for q, x in d.groupby("q"):
        per = pd.Period(q, "Q"); base = per - 4
        if base not in eur_q.index or base.year < 2021:
            continue
        x = x.dropna(subset=["n_prior", "stays_yoy_pct"]).set_index("country")
        sp = x.n_prior / x.n_prior.sum(); se, _ = emea_shares(x.n_prior, eur_q.loc[base])
        for c in sp.index:
            srows.append({"base_quarter": str(base), "country": c, "share_panel": float(sp[c]),
                          "share_eurostat": float(se[c]), "delta": float(se[c] - sp[c])})
    pd.DataFrame(srows).to_csv(C.OUT / "geomix_eurostat_shares.csv", index=False)

    # sub-regional terms
    trows = []
    for ss, gs, cp, pb in specs:
        h = H[(H.share_src == ss) & (H.growth_src == gs) & (H.price_basis == pb)]
        t = term_with_emea(h); t["variant"] = f"{ss}_shares/{gs}_growth/{pb}"; t["horizon"] = "history"
        f = F[(F.share_src == ss) & (F.growth_src == gs) & (F.price_basis == pb)]
        tf = term_with_emea(f, forward=True); tf["variant"] = t["variant"].iloc[0]; tf["horizon"] = "forward"
        trows += [t, tf]
    T = pd.concat(trows, ignore_index=True)
    T.to_csv(C.OUT / "geomix_eurostat_subregional_term.csv", index=False)

    # 4Q26 ADR effect, in $ on the base-year ADR
    ap = pd.read_csv(C.OUT / "adr_path.csv").drop_duplicates("quarter").set_index("quarter")
    cur = pd.read_csv(C.OUT / "geomix_subregional_term_forward.csv").set_index("quarter").subgeo_pp
    arows = []
    for v, x in T[T.horizon == "forward"].groupby("variant"):
        x = x.set_index("quarter")
        for q in FWD:
            if q not in x.index or q not in ap.index:
                continue
            base_adr = float(ap.loc[q, "adr_usd_base_year"])
            new, old = float(x.loc[q, "subgeo_pp"]), float(cur.get(q, np.nan))
            arows.append({"variant": v, "quarter": q, "subgeo_pp_current": old, "subgeo_pp_new": new,
                          "delta_pp": new - old, "adr_usd_base_year": base_adr,
                          "adr_usd_effect_current": base_adr * old / 100, "adr_usd_effect_new": base_adr * new / 100,
                          "adr_usd_delta": base_adr * (new - old) / 100})
    pd.DataFrame(arows).to_csv(C.OUT / "geomix_eurostat_adr_effect.csv", index=False)
    print("wrote geomix_eurostat_{coverage,emea_mix,emea_forward,shares,subregional_term,adr_effect}.csv")


if __name__ == "__main__":
    main()
