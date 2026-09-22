"""Figures for the note, drawn only from the lane's CSV/JSON outputs. Palette and mark rules follow the dataviz
skill's reference instance (categorical slots in fixed order, ink tokens for text, hairline grid, 2px lines,
>=8px markers with a surface ring, one axis per chart, legend whenever two series share a plot)."""
import json
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import config as C

S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"          # categorical slots 1-3
INK, INK2, MUTED, GRID, AXIS, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
NEUTRAL, RED = "#f0efec", "#e34948"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": AXIS, "axes.linewidth": 1,
                     "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 1, "axes.axisbelow": True, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "savefig.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False,
                     "legend.frameon": False, "legend.fontsize": 9})


def qlabel(qi):
    return f"{qi % 4 + 1}Q{str(qi // 4)[2:]}"


def _title(ax, t, sub=None):
    ax.set_title(t, loc="left", color=INK, fontsize=11, fontweight="bold", pad=14 if sub else 8)
    if sub:
        ax.text(0, 1.02, sub, transform=ax.transAxes, color=INK2, fontsize=9, va="bottom")


def fig1_panel():
    p = pd.read_csv(C.OUT / "panel_country_month.csv"); t = pd.read_csv(C.OUT / "stage_a_tests.csv")
    pc = pd.read_csv(C.OUT / "panel_per_country_walkforward.csv").sort_values("ratio_vs_naive")
    w = p[(p.ymi >= C.PANEL_START) & (p.ymi <= C.PANEL_END)].dropna(subset=["y_yoy", "x_yoy_vmatch"]).copy()
    w["xd"] = w.x_yoy_vmatch - w.groupby("code").x_yoy_vmatch.transform("mean")
    w["yd"] = w.y_yoy - w.groupby("code").y_yoy.transform("mean")
    a1 = t[(t.measure == "yoy_vmatch") & (t.test == "A1_elasticity")].iloc[0]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw=dict(width_ratios=[1.35, 1]))
    ax.scatter(w.xd * 100, w.yd * 100, s=16, color=S1, alpha=0.45, linewidths=0)
    xs = np.linspace(w.xd.min(), w.xd.max(), 50) * 100
    ax.plot(xs, a1.value * xs, color=INK, lw=2)
    ax.fill_between(xs, (a1.value - 1.96 * a1.se_cluster) * xs, (a1.value + 1.96 * a1.se_cluster) * xs, color=INK, alpha=0.08, lw=0)
    ax.axhline(0, color=AXIS, lw=1); ax.axvline(0, color=AXIS, lw=1)
    ax.set_xlabel("review-count y/y, log pp (within-country)"); ax.set_ylabel("observed platform nights y/y, log pp (within-country)")
    _title(ax, "Reviews measure stays", f"18 EU countries x month, 2023-01 to 2026-03, n = {int(a1.n):,};  beta = {a1.value:.2f} (cluster se {a1.se_cluster:.2f}, wild-cluster p {a1.p:.3f})")
    ax.text(0.98, 0.04, f"first differences: beta = {t[(t.measure=='yoy_vmatch')&(t.test=='A2_first_differences')].value.iloc[0]:.2f}, p {t[(t.measure=='yoy_vmatch')&(t.test=='A2_first_differences')].p.iloc[0]:.3f}",
            transform=ax.transAxes, ha="right", color=INK2, fontsize=9)
    bx.barh(pc.code, pc.ratio_vs_naive, color=S1, height=0.62)
    bx.axvline(0.75, color=INK, lw=1.5); bx.axvline(1.0, color=AXIS, lw=1)
    bx.text(0.76, 0.2, "pass line 0.75", color=INK, fontsize=9, va="center")
    bx.set_xlabel("walk-forward RMSE ratio vs naive (scored 2024-01 to 2026-03)", fontsize=9); bx.set_xlim(0, max(1.15, pc.ratio_vs_naive.max() + 0.05))
    bx.grid(axis="y", visible=False)
    _title(bx, "Out of sample, by country", f"median {pc.ratio_vs_naive.median():.2f};  {(pc.ratio_vs_naive <= 0.75).sum()} of {len(pc)} countries at or below 0.75")
    fig.tight_layout(); fig.savefig(C.FIG / "fig1_panel_measurement.png", dpi=160); plt.close(fig)


def fig2_walkforward():
    paths = pd.read_csv(C.OUT / "stage_b_paths.csv"); res = pd.read_csv(C.OUT / "stage_b_walkforward.csv")
    c3 = json.loads((C.OUT / "stage_c3_3q26.json").read_text())
    p = paths[(paths.measure == C.PRIMARY) & (paths.window == "W1") & (paths.subset == "full")].sort_values("t")
    r = res[(res.measure == C.PRIMARY) & (res.subset == "full") & (res.target == "level")].set_index("window")
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(11, 6.4), sharex=True, gridspec_kw=dict(height_ratios=[2.2, 1]))
    x = np.arange(len(p)); labels = [qlabel(q) for q in p.t]
    naive = (p.actual + p.err_naive).to_numpy()          # err_naive = y[t-1] - y[t], so y[t-1] = actual + err
    ax.plot(x, p.actual, color=S1, lw=2, marker="o", ms=8, mec=SURF, mew=2, label="printed nights y/y")
    ax.plot(x, p.pred, color=S2, lw=2, marker="o", ms=8, mec=SURF, mew=2, label="v2.1 index, walk-forward (refit before each quarter)")
    ax.plot(x, naive, color=MUTED, lw=1.5, ls=(0, (3, 2)), label="naive: last quarter's y/y")
    x3 = len(p); ax.errorbar([x3], [c3["implied_nights_yoy"]], yerr=[c3["band_pp"]], fmt="o", ms=9, mfc=SURF, mec=S2, mew=2, ecolor=S2, elinewidth=1.5, capsize=4)
    ax.text(x3, c3["hi"] + 0.25, f"3Q26 read\n{c3['implied_nights_yoy']:.1f}% +/- {c3['band_pp']:.1f}", ha="center", va="bottom", color=INK2, fontsize=9)
    ax.axvspan(len(p) - 4.5, x3 + 0.6, color=NEUTRAL, lw=0, zorder=0); ax.text(len(p) - 4.4, ax.get_ylim()[1] if False else 17.5, "post-RNPL quarters", color=INK2, fontsize=9, va="top")
    ax.set_ylabel("nights y/y, %"); ax.legend(loc="upper right", ncol=1)
    _title(ax, "The record's yardstick: expanding-window walk-forward, W1 scored 1Q23 to 2Q26",
           f"RMSE ratio vs naive  W1 {r.loc['W1','wf_ratio_vs_naive']:.3f} [{r.loc['W1','ratio_lo90']:.2f}, {r.loc['W1','ratio_hi90']:.2f}]   W2 {r.loc['W2','wf_ratio_vs_naive']:.3f} [{r.loc['W2','ratio_lo90']:.2f}, {r.loc['W2','ratio_hi90']:.2f}]   pass line 0.75 on both;  DM p {r.loc['W1','dm_p']:.2f} / {r.loc['W2','dm_p']:.2f}")
    wdt = 0.36
    bx.bar(x - wdt / 2, p.err_feature.abs(), width=wdt, color=S2, label="|error| v2.1 index")
    bx.bar(x + wdt / 2, p.err_naive.abs(), width=wdt, color=MUTED, label="|error| naive")
    bx.set_ylabel("abs. error, pp"); bx.legend(loc="upper right", ncol=2); bx.grid(axis="x", visible=False)
    bx.set_xticks(list(x) + [x3]); bx.set_xticklabels(labels + ["3Q26"])
    fig.tight_layout(); fig.savefig(C.FIG / "fig2_walkforward.png", dpi=160); plt.close(fig)


def fig3_gap():
    g = pd.read_csv(C.OUT / "stage_c_gap.csv"); g = g[g.variant == "primary"].sort_values("qi")
    t = pd.read_csv(C.OUT / "stage_c_tests.csv").set_index("test").loc["C1_primary_gap"]
    paths = pd.read_csv(C.OUT / "stage_b_paths.csv")
    cal = paths[(paths.measure == C.PRIMARY) & (paths.window == "W2") & (paths.subset == "pre_rnpl")].sort_values("t")
    band = float(t.band_pp)
    fig, ax = plt.subplots(figsize=(11, 4.8))
    xs_cal = np.arange(len(cal)); xs_post = np.arange(len(cal), len(cal) + len(g))
    ax.axhspan(-band, band, color=NEUTRAL, lw=0, zorder=0)
    ax.axhline(0, color=AXIS, lw=1)
    ax.bar(xs_cal, -cal.err_feature, width=0.6, color=MUTED, label="calibration residual (walk-forward, 1Q24 to 2Q25)")
    ax.bar(xs_post, g.gap_pp, width=0.6, color=S1, label="post-RNPL gap: printed minus mapped (mapping frozen at 2Q25)")
    ax.axhline(g.gap_pp.mean(), xmin=(len(cal) - 0.3) / (len(cal) + len(g)), xmax=1, color=INK, lw=1.5)
    ax.text(xs_post[-1] + 0.45, g.gap_pp.mean(), f" mean {g.gap_pp.mean():+.2f} pp\n = {g.gap_pp.mean()/band:.2f} bands", color=INK, fontsize=9, va="center")
    ax.text(len(cal) - 0.7, band, f" band +/-{band:.2f} pp (pre-RNPL walk-forward RMSE, 6 quarters)", color=INK2, fontsize=9, va="bottom")
    ax.set_xticks(list(xs_cal) + list(xs_post)); ax.set_xticklabels([qlabel(q) for q in cal.t] + [qlabel(q) for q in g.qi])
    ax.set_ylabel("printed nights y/y minus stays-implied, pp"); ax.grid(axis="x", visible=False)
    ax.set_xlim(-0.6, xs_post[-1] + 1.6)
    ax.legend(loc="upper left")
    verdict = "pre-registered C1: FAIL - " + t.reading if not bool(t.passed) else "pre-registered C1: PASS - " + t.reading
    _title(ax, "The post-RNPL gap: positive in three of four quarters, inside the band", verdict)
    fig.tight_layout(); fig.savefig(C.FIG / "fig3_post_rnpl_gap.png", dpi=160); plt.close(fig)


def fig4_power():
    pre = pd.read_csv(C.OUT / "stage_d_pretrend.csv"); pw = pd.read_csv(C.OUT / "stage_d_power.csv").set_index("item").value
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw=dict(width_ratios=[1.6, 1]))
    x = np.arange(len(pre)); lab = [f"{int(m)//12}-{int(m)%12+1:02d}" for m in pre.ymi]
    ax.axhline(0, color=AXIS, lw=1)
    ax.plot(x, pre.us_minus_controls_pp, color=S1, lw=2, marker="o", ms=7, mec=SURF, mew=2)
    i0 = int(np.where(pre.ymi == C.RNPL_US_LAUNCH_YMI)[0][0]); ax.axvline(i0 - 0.5, color=INK, lw=1.5)
    ax.text(i0 - 0.3, ax.get_ylim()[0] + 0.5, "US launch, Aug 2025", color=INK, fontsize=9, va="bottom")
    ax.text(1, ax.get_ylim()[1] - 1, f"pre-period mean {pw['US_minus_controls_pretrend_mean_pp']:+.1f} pp", color=INK2, fontsize=9, va="top")
    iw = int(np.where(pre.ymi == C.ymi(2026, 6))[0][0]); ax.annotate("World Cup opens\nin the US, 11 Jun", (iw, pre.us_minus_controls_pp.iloc[iw]), xytext=(iw - 7.5, pre.us_minus_controls_pp.iloc[iw] - 3.5), color=INK2, fontsize=9, arrowprops=dict(arrowstyle="-", color=AXIS))
    ax.set_xticks(x[::4]); ax.set_xticklabels(lab[::4], fontsize=9); ax.set_ylabel("US minus never-treated controls, y/y stays, pp")
    _title(ax, "Parallel trends fail before treatment", "US stays growth ran below the controls through 2024 and slid further in 2025")
    items = [("MDE\npermutation", pw["MDE_pp_permutation"]), ("MDE\nplacebo dates", pw["MDE_pp_placebo_dates"]), ("effect\nlooked for", pw["effect_looked_for_pp"])]
    bx.bar([i[0] for i in items], [i[1] for i in items], color=[S1, S1, S2], width=0.55)
    for i, (k, v) in enumerate(items): bx.text(i, v + 0.15, f"{v:.1f} pp", ha="center", color=INK2, fontsize=9)
    bx.set_ylabel("pp of y/y stays"); bx.grid(axis="x", visible=False)
    _title(bx, "The test cannot see the effect", "min. detectable effect, alpha .05, power .8")
    fig.tight_layout(); fig.savefig(C.FIG / "fig4_did_power.png", dpi=160); plt.close(fig)


def fig5_event_study():
    es = pd.read_csv(C.OUT / "stage_d_event_study_EXPLORATORY.csv")
    fig, ax = plt.subplots(figsize=(11, 4.4))
    ax.axhline(0, color=AXIS, lw=1); ax.axvline(-0.5, color=INK, lw=1.5)
    ax.fill_between(es.event_month, es.lo90, es.hi90, color=S1, alpha=0.15, lw=0)
    ax.plot(es.event_month, es.att_pp, color=S1, lw=2, marker="o", ms=7, mec=SURF, mew=2)
    ax.annotate("Jun 2026: World Cup", (es.event_month.iloc[-1], es.att_pp.iloc[-1]), xytext=(es.event_month.iloc[-1] - 4.5, es.att_pp.iloc[-1] + 1), color=INK2, fontsize=9)
    ax.set_xlabel("months since US launch (Aug 2025 = 0)"); ax.set_ylabel("US minus controls, deviation from own pre-mean, pp")
    ax.text(0.5, 0.5, "EXPLORATORY - no claim", transform=ax.transAxes, ha="center", va="center", color=MUTED, fontsize=34, alpha=0.25, rotation=20)
    _title(ax, "Event study, US arm vs never-treated controls (cluster-bootstrap 90% band)",
           "pre-launch coefficients swing +/-8 pp, so post-launch values are not interpretable; shown for transparency only")
    fig.tight_layout(); fig.savefig(C.FIG / "fig5_event_study_EXPLORATORY.png", dpi=160); plt.close(fig)


def render_all():
    C.FIG.mkdir(parents=True, exist_ok=True)
    for f in (fig1_panel, fig2_walkforward, fig3_gap, fig4_power, fig5_event_study, fig6_view_vs_street, fig7_rnpl_evidence, fig8_final_model, fig0_model_overview):
        f(); print("rendered", f.__name__)


def fig6_view_vs_street():
    import data as D
    v = pd.read_csv(C.OUT / "stage_e_view_vs_street.csv"); kpi = D.load_kpi()
    hist = kpi[(kpi.qi >= C.qi(2023, 1))].copy()
    fwd = v[v.quarter.str.contains("Q")].copy()
    fig, ax = plt.subplots(figsize=(12.5, 5.8))
    xs_h = np.arange(len(hist)); xs_f = np.arange(len(hist), len(hist) + len(fwd)); labels = [qlabel(q) for q in hist.qi] + list(fwd.quarter)
    ax.axvspan(len(hist) - 0.5, xs_f[-1] + 0.7, color=NEUTRAL, lw=0, zorder=0)
    ax.plot(xs_h, hist.nights_m_yoy_pct, color=S1, lw=2, marker="o", ms=8, mec=SURF, mew=2, label="printed nights y/y")
    ax.plot(np.r_[xs_h[-1], xs_f], np.r_[hist.nights_m_yoy_pct.iloc[-1], fwd.base_yoy], color=INK, lw=2, marker="o", ms=8, mec=SURF, mew=2, label="our base path (mechanism; DEC-0029 / 0019 / 0025)")
    r3 = fwd[fwd.quarter == "3Q26"].iloc[0]
    ax.errorbar([xs_f[0] - 0.22], [r3.v2_read_yoy], yerr=[r3.v2_band_pp], fmt="o", ms=9, mfc=SURF, mec=S2, mew=2, ecolor=S2, elinewidth=1.5, capsize=4, label="v2 stays-index read for 3Q26, +/- band", zorder=6)
    st = fwd.dropna(subset=["street_yoy"])
    ax.scatter(xs_f[:len(st)] + 0.22, st.street_yoy, marker="D", s=75, color=S3, edgecolor=SURF, linewidth=1.5, zorder=6, label="Street consensus nights (Bloomberg MODL)")
    ax.annotate(f"Street 149.0m, +{r3.street_yoy:.1f}%\nP(print >= Street | v2 read) = {r3.p_print_at_or_above_street:.0%}",
                (xs_f[0] + 0.22, r3.street_yoy), xytext=(xs_f[0] - 5.2, 14.6), color=INK2, fontsize=9, arrowprops=dict(arrowstyle="-", color=AXIS))
    ax.annotate("Street 134.0m, +9.9%", (xs_f[1] + 0.22, st.street_yoy.iloc[1]), xytext=(xs_f[1] + 0.6, 11.4), color=INK2, fontsize=9, arrowprops=dict(arrowstyle="-", color=AXIS))
    for i, q in enumerate(fwd.quarter):
        ax.text(xs_f[i] + (0.32 if i == 0 else 0), fwd.base_yoy.iloc[i] - 0.5, f"{fwd.base_m.iloc[i]:.1f}m", ha="left" if i == 0 else "center", va="top", color=INK2, fontsize=8.5)
    laps = {"3Q26": "US lap\n(in M1)", "4Q26": "lap\n-0.78", "1Q27": "laps -1.11\nevent +1.0", "2Q27": "laps -1.65\nWC -0.5", "3Q27": "laps\n-1.65", "4Q27": "laps\n-1.65"}
    for i, q in enumerate(fwd.quarter):
        ax.text(xs_f[i], 4.15, laps[q], ha="center", va="bottom", color=MUTED, fontsize=8)
    ax.text(xs_f[0] - 0.45, 3.35, "RNPL and fee laps, pp of y/y:", color=MUTED, fontsize=8, ha="right", va="bottom")
    ax.set_xticks(list(xs_h) + list(xs_f)); ax.set_xticklabels(labels, fontsize=8.5); ax.set_ylabel("nights y/y, %"); ax.set_ylim(3.2, 19.8); ax.set_xlim(-0.6, xs_f[-1] + 0.8)
    ax.text(len(hist) - 0.35, 3.35, "forward", color=INK2, fontsize=9, va="bottom")
    ax.legend(loc="upper right")
    _title(ax, "Our nights view against the Street", f"3Q26 base 146.8m (+9.9%); v2.1 read +{r3.v2_read_yoy:.2f} +/- {r3.v2_band_pp:.2f}; Street 149.0m (+11.5%) is {r3.street_z_vs_v2:.1f} bands above the read. 4Q26 base 131.8m vs Street 134.0m.")
    fig.tight_layout(); fig.savefig(C.FIG / "fig6_view_vs_street.png", dpi=160); plt.close(fig)


def fig7_rnpl_evidence():
    r = pd.read_csv(C.OUT / "stage_e_rnpl_evidence.csv"); g = pd.read_csv(C.OUT / "stage_c_gap.csv"); g = g[g.variant == "primary"]
    s = r[r.comparator == "GBV reported"].sort_values("qi"); sx = r[r.comparator == "GBV ex-FX"].sort_values("qi")
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(12.5, 5.0), gridspec_kw=dict(width_ratios=[1.7, 1]))
    x = np.arange(len(s)); i0 = int(np.where(s.period.to_numpy() == "post")[0][0])
    ax.axvspan(i0 - 0.5, len(s) - 0.5, color=NEUTRAL, lw=0, zorder=0)
    ax.plot(x, s.gbv_yoy, color=S1, lw=2, marker="o", ms=8, mec=SURF, mew=2, label="GBV y/y (reported)")
    ax.plot(x, s.uf_yoy, color=S2, lw=2, marker="o", ms=8, mec=SURF, mew=2, label="unearned fees y/y (fees collected on bookings not yet stayed)")
    ax.fill_between(x[i0 - 1:], s.uf_yoy.iloc[i0 - 1:], s.gbv_yoy.iloc[i0 - 1:], color=S2, alpha=0.12, lw=0)
    ax.axhline(0, color=AXIS, lw=1); ax.set_xticks(x); ax.set_xticklabels(s.quarter, fontsize=8); ax.set_ylabel("y/y, %")
    ax.text(i0 - 0.4, ax.get_ylim()[1] - 0.8, "US RNPL launch", color=INK2, fontsize=9, va="top")
    ax.text(len(s) - 1.55, 4.0, "bookings the balance\nsheet has not been\npaid for", ha="center", va="center", color=INK2, fontsize=8.5)
    ax.legend(loc="lower left")
    _title(ax, "The option is being written: unearned fees stall while GBV accelerates", f"UF minus GBV: {s.pre_mean.iloc[0]:+.1f} +/- {s.pre_sd.iloc[0]:.1f} pp pre-RNPL (10 q); post {', '.join(f'{v:+.0f}' for v in s[s.period=='post'].spread_pp)} pp; Welch p {s.welch_p_two_sided.iloc[0]:.3f} (ex-FX {sx.welch_p_two_sided.iloc[0]:.3f})")
    post = s[s.period == "post"]; xb = np.arange(len(post))
    bx.bar(xb - 0.2, post.z_vs_pre, width=0.38, color=S2, label="UF - GBV spread, z vs pre-RNPL")
    bx.bar(xb + 0.2, g.gap_in_bands.to_numpy(), width=0.38, color=S1, label="stays gap, in bands (Stage C)")
    bx.axhline(0, color=AXIS, lw=1); bx.axhline(-2, color=MUTED, lw=1, ls=(0, (3, 2))); bx.axhline(2, color=MUTED, lw=1, ls=(0, (3, 2)))
    bx.set_xticks(xb); bx.set_xticklabels(post.quarter); bx.set_ylabel("standardised"); bx.grid(axis="x", visible=False)
    bx.text(len(post) - 0.55, -2.15, "2 sd", color=MUTED, fontsize=8, va="top", ha="right")
    bx.legend(loc="lower left", fontsize=8)
    _title(bx, "Written vs exercised", "balance sheet 2-7 sd; stays gap right sign, < 1 band")
    fig.tight_layout(); fig.savefig(C.FIG / "fig7_rnpl_evidence.png", dpi=160); plt.close(fig)


def fig0_model_overview():
    """One picture of the model: measurement (fig1) -> calibration (fig2) -> RNPL gap (fig3) -> the view (fig6)."""
    import matplotlib.image as mpimg
    panels = [("fig1_panel_measurement.png", "1. Measurement: reviews measure stays (n 702 country-months, beta 0.49)"),
              ("fig2_walkforward.png", "2. Calibration: walk-forward on the record's windows (v2.1: 0.72 / 0.72 vs naive)"),
              ("fig3_post_rnpl_gap.png", "3. RNPL phase: printed minus stays-implied, frozen mapping (v2.1: +0.49 pp, inside band)"),
              ("fig8_final_model.png", "4. The final model: stays vs print vs Street; the RNPL hit lands 4Q26 (level) and 2Q27 (y/y)")]
    fig, axes = plt.subplots(2, 2, figsize=(22, 13))
    for ax, (f, t) in zip(axes.ravel(), panels):
        ax.imshow(mpimg.imread(C.FIG / f)); ax.axis("off")
        ax.set_title(t, loc="left", color=INK, fontsize=13, fontweight="bold", pad=6)
    fig.suptitle("Reviews index v2 - the model in one picture: stays are measured, mapped to the KPI, read after RNPL, and set against the Street",
                 x=0.01, ha="left", color=INK, fontsize=15, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.97)); fig.savefig(C.FIG / "fig0_model_overview.png", dpi=110); plt.close(fig)


def fig8_final_model():
    """The final model: stays (business) vs print (reported) vs Street, with the option-inflation term below."""
    import data as D
    f = pd.read_csv(C.OUT / "final_model_paths.csv"); meta = json.loads((C.OUT / "final_model_meta.json").read_text())
    kpi = D.load_kpi(); hist = kpi[(kpi.qi >= C.qi(2024, 1)) & (kpi.qi <= C.qi(2026, 2))]
    obs = f[f.phase == "observed"]; fwd = f[f.phase != "observed"]
    labels = [qlabel(q) for q in hist.qi] + list(fwd.quarter); n_h = len(hist); x_h = np.arange(n_h); x_f = np.arange(n_h, n_h + len(fwd))
    x_obs = np.array([labels.index(q) for q in obs.quarter])
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(13, 8.6), sharex=True, gridspec_kw=dict(height_ratios=[2.4, 1]))
    # phases (y/y view): 3Q26 nets, 4Q26 small, 1Q27 flat, 2Q27 the hit
    for a in (ax, bx):
        a.axvspan(x_obs[0] - 0.5, x_f[0] - 0.5, color="#fbe9e1", lw=0, zorder=0)        # writing waves observed
        a.axvspan(x_f[0] - 0.5, x_f[1] + 0.5, color=NEUTRAL, lw=0, zorder=0)            # 3Q26 nets, 4Q26 small
        a.axvspan(x_f[1] + 0.5, x_f[3] + 0.5, color="#e3eefb", lw=0, zorder=0)          # 1Q27 flat, 2Q27 the hit
    ax.text(x_obs[0] - 0.4, 12.9, "options written: print above stays", color=INK2, fontsize=9, va="top")
    ax.text(x_f[0] - 0.4, 12.9, "nets / small", color=INK2, fontsize=9, va="top")
    ax.text(x_f[2] - 0.4, 12.9, "ceiling: the 2Q26 wave laps with nothing to net it", color=INK2, fontsize=9, va="top")
    # printed history and forward print path (base)
    ax.plot(x_h, hist.nights_m_yoy_pct, color=S1, lw=2, marker="o", ms=8, mec=SURF, mew=2, label="printed nights y/y (booking-dated)")
    ax.plot(np.r_[x_h[-1], x_f], np.r_[hist.nights_m_yoy_pct.iloc[-1], fwd.print_yoy], color=INK, lw=2, marker="o", ms=8, mec=SURF, mew=2, label="print path, base (mechanism + filed laps)")
    # stays: observed stays-implied, and forward stays path
    ax.plot(x_obs, obs.stays_yoy, color=S2, lw=2, marker="o", ms=8, mec=SURF, mew=2, label="stays-implied (v2 index through the frozen mapping)")
    ax.plot(np.r_[x_obs[-1], x_f], np.r_[obs.stays_yoy.iloc[-1], fwd.stays_yoy], color=S2, lw=2, ls=(0, (4, 2)), marker="o", ms=7, mec=SURF, mew=2, label="stays path (the business)")
    ax.errorbar([x_f[0]], [meta["stays_3q26"]], yerr=[meta["band"]], fmt="none", ecolor=S2, elinewidth=1.5, capsize=5, zorder=4)
    # 3Q26 print range under the I scenarios
    lo, hi = meta["stays_3q26"] + meta["I_3q26"]["zero"], meta["stays_3q26"] + meta["I_3q26"]["wave"]
    ax.plot([x_f[0] + 0.28, x_f[0] + 0.28], [lo, hi], color=INK, lw=6, alpha=0.25, solid_capstyle="butt")
    ax.text(x_f[0] + 0.42, lo - 0.05, f"3Q26 print range\n{lo:.1f}-{hi:.1f}% (I = 0 to +1.6)", color=INK2, fontsize=8.5, va="top")
    # short 4Q26
    ax.scatter([x_f[1]], [meta["short_4q26_print"]], marker="v", s=80, color=RED, edgecolor=SURF, linewidth=1.5, zorder=6, label="4Q26 short: cancellation drag (DEC-0020, deferred)")
    # Street
    st = fwd.dropna(subset=["street_yoy"])
    ax.scatter(x_f[:len(st)], st.street_yoy, marker="D", s=80, color=S3, edgecolor=SURF, linewidth=1.5, zorder=6, label="Street consensus (Bloomberg MODL)")
    ax.annotate("Street 149.0m, +11.5%  (P = 12% on the stays read)", (x_f[0], st.street_yoy.iloc[0]), xytext=(x_f[0] - 5.6, 12.15), color=INK2, fontsize=9, arrowprops=dict(arrowstyle="-", color=AXIS))
    ax.annotate("Street 134.0m, +9.9%", (x_f[1], st.street_yoy.iloc[1]), xytext=(x_f[1] + 0.9, 11.15), color=INK2, fontsize=9, arrowprops=dict(arrowstyle="-", color=AXIS))
    for i, (q, lvl) in enumerate(zip(fwd.quarter, fwd.print_level_m)):
        dx, dy, ha = (-0.32, 0.35, "right") if i == 0 else ((0.3, -0.05, "left") if i == 1 else (0.0, -0.45, "center"))
        ax.text(x_f[i] + dx, fwd.print_yoy.iloc[i] + dy, f"{lvl:.1f}m", ha=ha, va="top", color=INK2, fontsize=8.5)
    ax.set_ylabel("nights y/y, %"); ax.set_ylim(4.6, 13.2); ax.legend(loc="lower left", fontsize=8.5, ncol=2)
    _title(ax, "Final nights model: the business (stays), the print (stays + written options), and the Street",
           f"3Q26: stays +{meta['stays_3q26']:.2f} +/- {meta['band']:.2f}, print {meta['stays_3q26']:.1f}-{meta['stays_3q26'] + meta['I_3q26']['wave']:.1f}, Street +11.5. The RNPL hit lands when access stops growing: 2Q27 (-1.6 lapped, base +5.9%). A European launch would defer it.")
    # bottom: the option term in y/y form (what the KPI laps)
    bx.axhline(0, color=AXIS, lw=1)
    bx.bar(x_obs, obs.I_pp, width=0.55, color=S2, label="observed gap: print minus stays-implied")
    fy = fwd.set_index("quarter")
    qs = ["3Q26", "4Q26", "1Q27", "2Q27"]; xs = [x_f[list(fwd.quarter).index(q)] for q in qs]
    vals = [fy.loc[q, "I_yoy_pp"] for q in qs]
    bx.bar(xs, vals, width=0.55, color=INK, alpha=0.35, label="y/y option term: this quarter's writing minus the lapped gap")
    bx.plot([xs[0], xs[0]], [fy.loc["3Q26", "I_yoy_pp"], fy.loc["3Q26", "I_yoy_wave_pp"]], color=INK, lw=2); bx.plot([xs[0]], [fy.loc["3Q26", "I_yoy_wave_pp"]], marker="_", ms=12, color=INK)
    laps = meta["filed_laps"]
    bx.scatter([x_f[list(fwd.quarter).index(q)] for q in laps], [laps[q] for q in laps], marker="D", s=45, color=S1, edgecolor=SURF, linewidth=1.2, zorder=6, label="filed laps carried in the base path (DEC-0019/0025)")
    bx.bar([x_f[1]], [meta["short_4q26_print"] - meta["base_4q26_print"]], width=0.55, color=RED, alpha=0.5, label="4Q26 short: exercise drag on top")
    land = meta["landing_pp"]; lx = [labels.index(q) for q in land if q in labels]; ly = [-land[q] for q in land if q in labels]
    bx.plot(lx, ly, color=S2, lw=1.5, ls=(0, (2, 2)), marker="o", ms=6, mfc=SURF, mec=S2, mew=1.5, label="level channel: cancellations landing by stay quarter (K2 kernel), shown negative")
    for q, v in zip(qs, vals): bx.text(x_f[list(fwd.quarter).index(q)], v - 0.12 if v < 0 else v + 0.08, f"{v:+.2f}", ha="center", va="top" if v < 0 else "bottom", color=INK2, fontsize=8.5)
    bx.set_ylabel("pp of y/y"); bx.set_ylim(-2.3, 2.1); bx.grid(axis="x", visible=False)
    bx.set_xticks(list(x_h) + list(x_f)); bx.set_xticklabels(labels, fontsize=9); bx.legend(loc="upper left", fontsize=8.5, ncol=2)
    _title(bx, "The option term, y/y: 3Q26 nets, 4Q26 small, 1Q27 flat, 2Q27 the hit — and it matches the filed laps", None)
    fig.tight_layout(); fig.savefig(C.FIG / "fig8_final_model.png", dpi=160); plt.close(fig)


def fig9_one_line():
    """One line (printed history continuing into our base view), ranges around the forward part, Airbnb's actual nights
    guidance as boxes, the Street as diamonds. Guidance from overnight/02_guidance_ledger.csv (read-only)."""
    import data as D
    kpi = D.load_kpi(); hist = kpi[(kpi.qi >= C.qi(2024, 1)) & (kpi.qi <= C.qi(2026, 2))]
    f = pd.read_csv(C.OUT / "final_model_paths.csv"); fwd = f[f.phase != "observed"]; meta = json.loads((C.OUT / "final_model_meta.json").read_text())
    g = pd.read_csv(C.ROOT / "data/processed/overnight/02_guidance_ledger.csv"); g = g[g.metric == "nights_yoy_pct"]
    labels = [qlabel(q) for q in hist.qi] + list(fwd.quarter); n_h = len(hist); x_h = np.arange(n_h); x_f = np.arange(n_h, n_h + len(fwd))
    # forward ranges (y/y): 3Q26 = stays read +/- band; 4Q26-4Q27 = the record's parameter envelopes (final_nights.md lines table) over the base's own prior-year levels
    env_m = {"4Q26": (131.6, 132.9, 121.9), "1Q27": (166.9, 170.9, 156.2), "2Q27": (156.3, 160.2, 148.3), "3Q27": (154.7, 159.4, 146.8), "4Q27": (139.1, 142.7, 131.8)}
    lo = [meta["stays_3q26"] - meta["band"]] + [(a / p - 1) * 100 for a, b, p in env_m.values()]
    hi = [meta["stays_3q26"] + meta["band"]] + [(b / p - 1) * 100 for a, b, p in env_m.values()]
    fig, ax = plt.subplots(figsize=(12.5, 6))
    ax.axvspan(n_h - 0.5, x_f[-1] + 0.6, color=NEUTRAL, lw=0, zorder=0)
    ax.fill_between(x_f, lo, hi, color=S1, alpha=0.13, lw=0, label="our range (3Q26: stays read +/- band; 2027: parameter envelope)")
    ax.fill_between([x_f[0] - 0.18, x_f[0] + 0.18], [meta["stays_3q26"]] * 2, [meta["stays_3q26"] + meta["I_3q26"]["wave"]] * 2, color=S1, alpha=0.35, lw=0, label=f"3Q26 print range: stays + written options ({meta['stays_3q26']:.1f}-{meta['stays_3q26'] + meta['I_3q26']['wave']:.1f})")
    ax.plot(x_h, hist.nights_m_yoy_pct, color=S1, lw=2.2, marker="o", ms=8, mec=SURF, mew=2, label="printed nights y/y")
    ax.plot(np.r_[x_h[-1], x_f], np.r_[hist.nights_m_yoy_pct.iloc[-1], fwd.print_yoy], color=S1, lw=2.2, ls=(0, (4, 2)), marker="o", ms=8, mec=SURF, mew=2, label="our view (base print path)")
    ax.scatter([x_f[1]], [meta["short_4q26_print"]], marker="v", s=70, color=RED, edgecolor=SURF, linewidth=1.5, zorder=6, label="4Q26 short (cancellation drag)")
    # guidance: numeric buckets only (the directional guides are in stage_e_guidance.csv)
    first = True
    for _, r in g[g.guide_type == "bucket"].iterrows():
        if r.target_period not in labels: continue
        xg = labels.index(r.target_period)
        ax.add_patch(plt.Rectangle((xg - 0.3, r.value_low), 0.6, r.value_high - r.value_low, facecolor=S3, alpha=0.28, edgecolor=S3, lw=1.5, zorder=3, label="Airbnb's nights guidance (shareholder letter)" if first else None)); first = False
        tag = f"guided {r.value_low:.0f}-{r.value_high:.0f}" + (f", printed {r.actual:.1f}" if np.isfinite(r.actual) else "")
        ax.text(xg, (r.value_high + 0.12) if r.target_period == "3Q26" else (r.value_low - 0.15), tag, ha="center", va=("bottom" if r.target_period == "3Q26" else "top"), color=INK2, fontsize=8.5)
    x2 = labels.index("2Q26"); ax.text(x2, hist.nights_m_yoy_pct.iloc[-1] + 0.35, "guided: decelerate\nfrom 9.1; printed 10.3", ha="center", va="bottom", color=INK2, fontsize=8)
    # Street
    st = fwd.dropna(subset=["street_yoy"]); ax.scatter(x_f[:len(st)], st.street_yoy, marker="D", s=85, color=S2, edgecolor=SURF, linewidth=1.5, zorder=6, label="Street consensus (Bloomberg MODL)")
    s3 = C.STREET["3Q26"]; ax.plot([x_f[0]] * 2, [(s3["low_m"] / C.BASE_3Q25_M - 1) * 100, (s3["high_m"] / C.BASE_3Q25_M - 1) * 100], color=S2, lw=2)
    ax.text(x_f[0] + 0.25, st.street_yoy.iloc[0], "Street 149.0m (147-151)", color=INK2, fontsize=9, va="center")
    ax.text(x_f[1] + 0.25, st.street_yoy.iloc[1], "Street 134.0m", color=INK2, fontsize=9, va="center")
    for i, (q, lvl) in enumerate(zip(fwd.quarter, fwd.print_level_m)):
        ax.text(x_f[i] + (0.35 if i == 1 else 0), lo[i] - 0.2, f"{lvl:.1f}m", ha="center", va="top", color=INK2, fontsize=8.5)
    ax.set_xticks(list(x_h) + list(x_f)); ax.set_xticklabels(labels, fontsize=9); ax.set_ylabel("nights y/y, %"); ax.set_ylim(2.8, 13.6)
    ax.legend(loc="upper left", fontsize=8.5, ncol=2)
    _title(ax, "Our view, Airbnb's guidance, and the Street",
           f"3Q26: guided 10-12% (147.0-149.6m), Street 149.0m at the top of it, the business {meta['stays_3q26']:.2f} +/- {meta['band']:.1f} below its floor. Airbnb beat its nights guide three quarters running.")
    fig.tight_layout(); fig.savefig(C.FIG / "fig9_view_guidance_street.png", dpi=160); plt.close(fig)
    g[g.target_period.isin(labels)][["print_quarter", "print_date", "target_period", "guide_type", "value_low", "value_high", "direction", "comparator_value", "actual", "outcome", "quote"]].to_csv(C.OUT / "stage_e_guidance.csv", index=False)
