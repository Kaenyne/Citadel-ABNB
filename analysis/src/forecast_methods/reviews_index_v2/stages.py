"""Stage B (walk-forward calibration on the record's windows) and Stage C (the post-RNPL gap against the
pre-RNPL band, the cohort-consistent variant, the exercised-share bound, the 3Q26 read)."""
import numpy as np, pandas as pd
import config as C, index as I, kernel as K, scoring as S


def build_index(my):
    """Two aggregations of every measure: FY25 annual weights (v2, suffix none) and stay-quarter mix weights (v2.1, suffix _mix)."""
    import mix as MX
    w = MX.seasonal_weights(); cols = {}
    for meas in I.MEASURES:
        g, reg = I.global_quarterly(my, meas); cols[meas] = g * 100.0
        cols[meas + "_mix"] = MX.global_from_regional(reg * 100.0, w)
    return pd.DataFrame(cols).rename_axis("qi").reset_index()


def run_stage_b(idx, kpi):
    y = kpi.set_index("qi").nights_m_yoy_pct
    rows, paths = [], []
    for meas in [C.PRIMARY, "yoy_vmatch", "yoy_all", "yoy_mature", "yoy_all_mix"]:
        x = idx.set_index("qi")[meas]
        for wname, (ws, ss) in C.WINDOWS.items():
            for sub, end in [("full", None), ("pre_rnpl", C.FREEZE_QI)]:
                r = S.score_window(x, y, ws, ss, score_end=end)
                if r is None:
                    continue
                pth = r.pop("path"); lo, hi = S.ratio_interval(pth.err_feature, pth.err_naive)
                dm, pdm = S.dm_test(pth.err_feature, pth.err_naive)
                rows.append(dict(measure=meas, window=wname, subset=sub, target="level", **r, ratio_lo90=lo, ratio_hi90=hi,
                                 dm_stat=dm, dm_p=pdm,
                                 passed=(bool(r["wf_ratio_vs_naive"] <= C.PREREG["B1_ratio_max"]) if sub == "full" else np.nan)))
                pth.insert(0, "subset", sub); pth.insert(0, "window", wname); pth.insert(0, "measure", meas); paths.append(pth)
            # B5: acceleration
            ra = S.score_window(x.diff(), y.diff(), ws, ss)
            if ra is not None:
                pa = ra.pop("path"); rows.append(dict(measure=meas, window=wname, subset="full", target="acceleration", **ra,
                                                    ratio_lo90=np.nan, ratio_hi90=np.nan, dm_stat=np.nan, dm_p=np.nan, passed=np.nan))
    res = pd.DataFrame(rows)
    # B1 verdict on the primary
    prim = res[(res.measure == C.PRIMARY) & (res.subset == "full") & (res.target == "level")]
    res.attrs["B1_passed"] = bool((prim.wf_ratio_vs_naive <= C.PREREG["B1_ratio_max"]).all() and len(prim) == 2)
    return res, pd.concat(paths, ignore_index=True)


def loco_slopes(x, y, start_qi=C.qi(2023, 1), end_qi=C.qi(2026, 2)):
    d = pd.DataFrame({"x": x, "y": y}).dropna(); d = d[(d.index >= start_qi) & (d.index <= end_qi)]
    full_b, full_a = S.ols(d.x, d.y)
    rows = [dict(left_out=None, slope=full_b, intercept=full_a)]
    for q in d.index:
        b, a = S.ols(d.drop(q).x, d.drop(q).y); rows.append(dict(left_out=int(q), slope=b, intercept=a))
    return pd.DataFrame(rows)


def frozen_mapping(x, y, start_qi=C.qi(2023, 1), freeze_qi=C.FREEZE_QI):
    d = pd.DataFrame({"x": x, "y": y}).dropna(); d = d[(d.index >= start_qi) & (d.index <= freeze_qi)]
    b, a = S.ols(d.x, d.y)
    return float(a), float(b), int(len(d))


def cohort_index(my, M):
    """Cohort-consistent vmatch: deconvolve quarterly stays levels within each vintage per region, then the
    same-relative-age ratio, then FY25 weights. Returns percent series by booking quarter with realised share."""
    d = my.copy(); d["qi"] = d.ymi // 3
    cnt = d.groupby(["market_key", "qi"]).ymi.transform("count"); d = d[cnt == 3]
    reg_rows = {}
    for reg, g in d.groupby("region"):
        cur = g.groupby("qi").n_vm_cur.sum(); pri = g.groupby("qi").n_vm_prior.sum()
        ok = (cur > 0) & (pri > 0); cur, pri = cur[ok], pri[ok]
        full = range(int(cur.index.min()), int(cur.index.max()) + 1)
        Gc = K.deconvolve(cur.reindex(full).interpolate(), M); Gp = K.deconvolve(pri.reindex(full).interpolate(), M)
        reg_rows[reg] = (Gc / Gp - 1.0)
    reg = pd.DataFrame(reg_rows)
    w = pd.Series(C.FY25_NIGHTS_SHARE).reindex(reg.columns).fillna(0); ok = reg.notna()
    glob = (reg.fillna(0) * w).sum(axis=1) / (ok * w).sum(axis=1)
    last = int(reg.index.max())
    out = pd.DataFrame({"qi": glob.index, "yoy_cohort_vmatch": glob.to_numpy() * 100.0,
                        "realised_share": [K.realised_share(q, last, M) for q in glob.index]})
    return out


def run_stage_c(idx, kpi, my, M):
    y = kpi.set_index("qi").nights_m_yoy_pct
    rows, gaps = [], []
    # primary: same-quarter vmatch under the primary aggregation (v2.1 stay-quarter mix)
    x = idx.set_index("qi")[C.PRIMARY]
    a, b, n = frozen_mapping(x, y)
    band_res = S.score_window(x, y, *C.WINDOWS["W2"], score_end=C.FREEZE_QI)
    band = float(band_res["wf_rmse"]) if band_res else np.nan
    for q in C.POST_QIS:
        if q in x.index and q in y.index and np.isfinite(x[q]):
            g = float(y[q] - (a + b * x[q]))
            gaps.append(dict(variant="primary", qi=q, index_pct=float(x[q]), mapped_pct=a + b * x[q], actual_pct=float(y[q]),
                             gap_pp=g, band_pp=band, gap_in_bands=g / band if band else np.nan, realised_share=1.0))
    gp = pd.DataFrame([r for r in gaps if r["variant"] == "primary"])
    mean_gap = float(gp.gap_pp.mean()); nq = int((gp.gap_in_bands > C.PREREG["C1_quarter_min_bands"]).sum())
    c1 = bool(mean_gap > C.PREREG["C1_mean_gap_min_bands"] * band and nq >= C.PREREG["C1_quarters_min"])
    reading = ("pass: KPI above stays-implied beyond the band" if c1 else
               "no measurable RNPL signature in stays" if abs(mean_gap) <= band else
               "bookings below stays-implied (contradicts the mechanism)" if mean_gap < -band else "positive but inside the pass line")
    rows.append(dict(test="C1_primary_gap", value=mean_gap, band_pp=band, quarters_over_half_band=nq, n_quarters=len(gp),
                     frozen_a=a, frozen_b=b, n_fit=n, passed=c1, reading=reading))
    # cohort-consistent variant
    ci = cohort_index(my, M).set_index("qi").yoy_cohort_vmatch
    ac, bc, ncn = frozen_mapping(ci, y)
    bres = S.score_window(ci, y, *C.WINDOWS["W2"], score_end=C.FREEZE_QI); bandc = float(bres["wf_rmse"]) if bres else np.nan
    rs = cohort_index(my, M).set_index("qi").realised_share
    for q in C.POST_QIS[:3]:
        if q in ci.index and np.isfinite(ci[q]):
            g = float(y[q] - (ac + bc * ci[q]))
            gaps.append(dict(variant="cohort", qi=q, index_pct=float(ci[q]), mapped_pct=ac + bc * ci[q], actual_pct=float(y[q]),
                             gap_pp=g, band_pp=bandc, gap_in_bands=g / bandc if bandc else np.nan, realised_share=float(rs[q])))
    gc = pd.DataFrame([r for r in gaps if r["variant"] == "cohort"])
    if len(gc):
        mg = float(gc.gap_pp.mean()); nqc = int((gc.gap_in_bands > 0.5).sum())
        rows.append(dict(test="C1_cohort_gap", value=mg, band_pp=bandc, quarters_over_half_band=nqc, n_quarters=len(gc),
                         frozen_a=ac, frozen_b=bc, n_fit=ncn, passed=bool(mg > bandc and nqc >= 2), reading="reported beside primary"))
    # C2: exercised-share bound
    for bB in C.PREREG["beta_B_bundle_pts"]:
        rows.append(dict(test=f"C2_exercised_share_betaB_{bB:.0f}", value=mean_gap / bB, band_pp=band / bB,
                         quarters_over_half_band=np.nan, n_quarters=len(gp), frozen_a=a, frozen_b=b, n_fit=n, passed=np.nan,
                         reading="share of the disclosed bundle lift that did not become stays, +/- band"))
    return pd.DataFrame(rows), pd.DataFrame(gaps)


def stage_c3_3q26(a, b, band):
    """3Q26 partial read through the frozen mapping. Primary: E6's per-region vintage-matched, review-weighted
    quarter-to-date y/y (vintage_matched_nowcast.csv, period 3q26_to_date) combined with FY25 nights shares —
    the same construction as the v2 index — lifted by E6's measured review-weighted partial-to-full gap.
    Sensitivity: E6's own GLOBAL w_reviews cell (construction mismatch). Band = pre-RNPL walk-forward RMSE and
    the gap sd in quadrature."""
    q = pd.read_csv(C.E6_NOWCAST)
    r = q[(q.measure == "yoy_vmatch") & (q.weighting == "w_reviews") & (q.region == "GLOBAL")].iloc[0]
    vm = pd.read_csv(C.E / "vintage_matched_nowcast.csv")
    reg = vm[(vm.period == "3q26_to_date") & (vm.region.isin(C.FY25_NIGHTS_SHARE))].set_index("region").vmatch_cw
    if C.PRIMARY.endswith("_mix"):
        import mix as MX
        w = MX.seasonal_weights().loc[C.qi(2026, 3)].reindex(reg.index)          # v2.1: 3Q26 stay-quarter mix
    else:
        w = pd.Series(C.FY25_NIGHTS_SHARE).reindex(reg.index)                    # v2: FY25 annual shares
    partial_v2 = float((reg * w).sum() / w.sum() * 100)
    gap = float(r.gap_mean_pp); gsd = float(r.gap_sd_pp) if np.isfinite(r.gap_sd_pp) else 0.0
    full_v2 = partial_v2 + gap; pt = a + b * full_v2
    sd = float(np.sqrt(band ** 2 + (b * gsd) ** 2))
    full_e6 = float(r.full_index_3q26_pct)
    return dict(index_3q26_partial_pct=partial_v2, partial_to_full_gap_pp=gap, index_3q26_full_pct=full_v2,
                implied_nights_yoy=float(pt), band_pp=sd, lo=float(pt - sd), hi=float(pt + sd),
                regional_partial_pct={k: float(v * 100) for k, v in reg.items()}, weights_used={k: float(v) for k, v in w.items()}, primary=C.PRIMARY,
                sensitivity_e6_global_cw=dict(index_full_pct=full_e6, implied_nights_yoy=float(a + b * full_e6)),
                note="primary uses E6 per-region vmatch_cw x FY25 shares (v2 construction); sensitivity is E6's GLOBAL w_reviews cell")
