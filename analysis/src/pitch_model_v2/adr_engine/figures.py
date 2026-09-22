"""adr_engine / figures.py — the ADR line's figures (dataviz palette, matplotlib). Writes PNG + SVG under
docs/pitch-model-v2/lines/figures/adr_*. One y-axis per panel; legend for >= 2 series; thin marks."""
from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from . import config as C
from . import exfx as X

S1, S2, S3, S4, S5, S6, S7, S8 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"
INK, INK2, MUTED, GRID, AXIS, SURF, NEUTRAL = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb", "#f0efec"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.titlecolor": INK, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "savefig.facecolor": SURF, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "legend.frameon": False})


def _save(fig, name):
    C.FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(C.FIG / f"{name}.png", dpi=180, bbox_inches="tight"); fig.savefig(C.FIG / f"{name}.svg", bbox_inches="tight")
    plt.close(fig); return C.FIG / f"{name}.png"


def fig_fx_walkforward(ax=None, ax2=None):
    wf = pd.read_csv(C.OUT / "fx_pit_walkforward.csv"); sc = pd.read_csv(C.OUT / "fx_scores.csv")
    qs = C.WINDOWS["W1"]; x = np.arange(len(qs))
    d = wf[wf.variant == "V0_translation"].pivot(index="quarter", columns="origin", values="pred_pp").loc[qs]
    y = wf[(wf.variant == "V0_translation") & (wf.origin == "O3")].set_index("quarter").loc[qs].disclosed_pp
    nv = wf[(wf.variant == "naive_last_disclosed") & (wf.origin == "O3")].set_index("quarter").loc[qs].pred_pp
    own = ax is None
    if own:
        fig, (ax, ax2) = plt.subplots(2, 1, figsize=(9.5, 6.4), gridspec_kw={"height_ratios": [3, 2]}, sharex=True)
    ax.bar(x, y, width=0.55, color=NEUTRAL, edgecolor=AXIS, linewidth=0.6, label="disclosed ADR-FX (letter)")
    ax.errorbar(x, y, yerr=[0.25 if q in C.HALF_POINT_QUARTERS else 0.5 for q in qs], fmt="none", ecolor=MUTED, elinewidth=0.8, capsize=2)
    ax.plot(x, d["O1"], "o", mfc="none", mec=S1, ms=6, mew=1.4, label="identity at quarter start (O1)")
    ax.plot(x, d["O2"], "s", color=S3, ms=5, label="identity at day 60 (O2)")
    ax.plot(x, d["O3"], "o", color=S1, ms=6, label="identity pre-print (O3)")
    ax.plot(x, nv, "_", color=S2, ms=14, mew=2, label="naive: last disclosed")
    ax.axhline(0, color=AXIS, lw=0.8); ax.set_ylabel("FX effect on ADR y/y, pp"); ax.set_ylim(-7.5, 8.5); ax.legend(ncol=3, loc="upper left", fontsize=8)
    ax.set_title("FX on ADR, point in time: translation identity (0 fitted parameters) vs disclosed" if not own else "FX on ADR, point in time: the translation identity (0 fitted parameters) vs the disclosed effect, 1Q23–2Q26", loc="left", fontsize=10)
    e = wf[(wf.origin == "O3") & (wf.quarter.isin(qs))].pivot(index="quarter", columns="variant", values="err_pp").loc[qs]
    w = 0.26
    ax2.bar(x - w, e["V0_translation"], w, color=S1, label="identity (O3)")
    ax2.bar(x, e["V2_eur_ols"], w, color=S7, label="euro-only OLS (O3)")
    ax2.bar(x + w, e["naive_last_disclosed"], w, color=S2, label="naive")
    ax2.axhline(0, color=AXIS, lw=0.8); ax2.set_ylabel("error, pp"); ax2.set_xticks(x); ax2.set_xticklabels(qs, rotation=0, fontsize=8)
    ax2.legend(ncol=3, loc="lower left", fontsize=8)
    s = sc[(sc.variant == "V0_translation")].set_index(["window", "origin"]).ratio_vs_naive
    ax2.text(0.99, 0.95, f"RMSE ratio to naive — W1: O1 {s[('W1','O1')]:.2f} · O2 {s[('W1','O2')]:.2f} · O3 {s[('W1','O3')]:.2f}   |   W2: O1 {s[('W2','O1')]:.2f} · O2 {s[('W2','O2')]:.2f} · O3 {s[('W2','O3')]:.2f}   (pass line 0.75)",
             transform=ax2.transAxes, ha="right", va="top", fontsize=8, color=INK2)
    if own:
        return _save(fig, "adr_fx_walkforward")


def fig_currency_contributions(ax=None):
    ct = pd.read_csv(C.OUT / "fx_currency_contributions.csv"); fc = pd.read_csv(C.OUT / "fx_forecast_asof.csv")
    fc = fc[fc["asof"] == "2026-09-21"].set_index("quarter")
    qs = ["1Q26", "2Q26", "3Q26", "4Q26", "1Q27", "2Q27"]; x = np.arange(len(qs))
    piv = ct.pivot(index="quarter", columns="ccy", values="contribution_pp").loc[qs]
    order = ["EUR", "GBP", "MXN", "BRL", "AUD", "CAD", "JPY", "KRW", "INR"]
    cols = {"EUR": S1, "GBP": S7, "MXN": S2, "BRL": S4, "AUD": S3, "CAD": S5, "JPY": S8, "KRW": S6, "INR": MUTED}
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(9.5, 4.6))
    pos = np.zeros(len(qs)); neg = np.zeros(len(qs))
    for c in order:
        v = piv[c].values; base = np.where(v >= 0, pos, neg)
        ax.bar(x, v, 0.6, bottom=base, color=cols[c], edgecolor=SURF, linewidth=1.0, label=c)
        pos = pos + np.clip(v, 0, None); neg = neg + np.clip(v, None, 0)
    tot = piv.sum(axis=1).values
    ax.plot(x, tot, "_", color=INK, ms=22, mew=2.2, label="total (identity, spot held)")
    disc = {"1Q26": 5.0, "2Q26": 1.3}
    ax.plot([qs.index(q) for q in disc], list(disc.values()), "o", color=INK, ms=7, mfc=SURF, mew=1.8, label="disclosed")
    for q in ["3Q26", "4Q26", "1Q27", "2Q27"]:
        i = qs.index(q); ax.plot([i, i], [fc.loc[q, "p10"], fc.loc[q, "p90"]], color=INK, lw=1.2); ax.plot([i - 0.1, i + 0.1], [fc.loc[q, "p10"]] * 2, color=INK, lw=1); ax.plot([i - 0.1, i + 0.1], [fc.loc[q, "p90"]] * 2, color=INK, lw=1)
    ax.axhline(0, color=AXIS, lw=0.8); ax.set_xticks(x); ax.set_xticklabels([f"{q}\n{fc.loc[q,'obs_frac_at_asof']:.0%} printed" if q in fc.index else f"{q}\nprinted" for q in qs], fontsize=8)
    ax.set_ylabel("contribution to ADR-FX, pp"); ax.set_ylim(-4.8, 7.2); ax.legend(ncol=5, fontsize=8, loc="lower left")
    ax.set_title("Currency contributions to ADR-FX, FY2025 GBV weights, spot held from 18 Sep 2026 (P10–P90)" if not own else "Where the FX effect comes from: currency contributions at FY2025 GBV weights, spot held from 18 Sep 2026 (P10–P90 bars)", loc="left", fontsize=10)
    for i, q in enumerate(qs): ax.text(i, tot[i] + (0.35 if tot[i] >= 0 else -0.55), f"{tot[i]:+.2f}", ha="center", fontsize=8, color=INK)
    if own:
        return _save(fig, "adr_fx_currency_contributions")


def fig_exfx_mechanism(ax=None):
    h = X.history(); f = X.forward(); alts = X.alternatives()
    hq = list(h.index); fq = list(f.index); qs = hq + fq; x = np.arange(len(qs))
    comp = pd.DataFrame(index=qs)
    comp["core"] = list(h.core) + list(f.core); comp["bundle"] = list(h.bundle) + list(f.bundle)
    comp["geo mix"] = list(h.geo_mix) + list(f.geo_mix); comp["unit size"] = list(h.unit_size) + list(f.unit_size)
    comp["length of stay"] = list(h.los_mix) + list(f.los_mix); comp["seats / new business"] = list(h.seats) + list(f.seats)
    comp["interaction"] = list(h.interaction) + list(f.interaction)
    cols = {"core": S1, "bundle": S4, "geo mix": S2, "unit size": S3, "length of stay": S5, "seats / new business": S7, "interaction": MUTED}
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(11, 5))
    pos = np.zeros(len(qs)); neg = np.zeros(len(qs))
    for c in comp.columns:
        v = comp[c].values; base = np.where(v >= 0, pos, neg)
        ax.bar(x, v, 0.62, bottom=base, color=cols[c], edgecolor=SURF, linewidth=1.0, label=c)
        pos = pos + np.clip(v, 0, None); neg = neg + np.clip(v, None, 0)
    ax.plot(x[:len(hq)], h.exfx_yoy, "o", color=INK, ms=5, mfc=SURF, mew=1.5, label="disclosed ex-FX ADR y/y (whole points)")
    ax.plot(x[len(hq):], f.exfx_yoy, "o", color=INK, ms=6, label="mechanism ex-FX (base)")
    card = alts[alts.rule.str.startswith("card v3")].set_index("quarter").loc[fq].exfx_yoy_pct
    ax.plot(x[len(hq):], card, "_", color=S8, ms=16, mew=2, label="card v3 carry (no lap)")
    mr = alts[alts.rule.str.startswith("core mean")].set_index("quarter").loc[fq].exfx_yoy_pct
    ax.plot(x[len(hq):], mr, "_", color=S6, ms=16, mew=2, label="core mean reversion (downside)")
    ax.axvspan(len(hq) - 0.5, len(qs) - 0.5, color="#e3eefb", lw=0, zorder=0)
    ax.axhline(0, color=AXIS, lw=0.8); ax.set_xticks(x); ax.set_xticklabels(qs, fontsize=7 if not own else 8, rotation=45 if not own else 0)
    ax.set_ylabel("ex-FX ADR y/y, pp"); ax.set_ylim(-3.2, 7.4); ax.legend(ncol=4, fontsize=7.5, loc="upper left")
    ax.set_title("Ex-FX ADR decomposed: core + bundle (laps on filed dates) + mix; forward shaded" if not own else "Ex-FX ADR, decomposed: like-for-like core + the product bundle (lapping on filed dates) + mix terms; forward 3Q26–4Q27 shaded", loc="left", fontsize=10)
    if own:
        return _save(fig, "adr_exfx_mechanism")


def fig_path_vs_street(ax=None):
    p = pd.read_csv(C.OUT / "adr_path.csv").set_index("quarter"); h = X.history()
    hist_q = ["1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]; fq = C.FORWARD_QUARTERS; qs = hist_q + fq; x = np.arange(len(qs))
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(x[:len(hist_q)], h.loc[hist_q, "adr_usd"], "-o", color=INK, lw=1.6, ms=5, label="printed ADR")
    yf = p.loc[fq, "adr_usd"].values
    ax.fill_between(x[len(hist_q):], p.loc[fq, "adr_usd_lo"], p.loc[fq, "adr_usd_hi"], color=S1, alpha=0.18, lw=0, label="band (RSS envelope + FX P10–P90)")
    ax.plot(x[len(hist_q):], yf, "-o", color=S1, lw=2, ms=6, label="ADR line v1 (base)")
    ax.plot(x[len(hist_q):], p.loc[fq, "card_v3_adr_usd"], "s", color=S8, ms=6, mfc=SURF, mew=1.6, label="card v3 (DEC-0008)")
    st = p.loc[["3Q26", "4Q26"], "street_adr_usd"]
    ax.plot([qs.index("3Q26"), qs.index("4Q26")], st, "D", color=S2, ms=7, label="Street (Bloomberg MODL, 12 Sep; n 26 / 25)")
    ax.plot([qs.index("3Q26")] * 2, [C.STREET_ADR["3Q26"][1], C.STREET_ADR["3Q26"][2]], color=S2, lw=1.2)
    for q in fq:
        i = qs.index(q); ax.text(i, p.loc[q, "adr_usd_lo"] - 1.6, f"${p.loc[q,'adr_usd']:.0f}  {p.loc[q,'adr_yoy_reported_pct']:+.1f}%", ha="center", va="top", fontsize=7.5, color=INK)
    ax.text(qs.index("3Q26") - 0.15, C.STREET_ADR["3Q26"][2] + 0.8, f"Street ${p.loc['3Q26','street_adr_usd']:.2f} (n 26)\nP(print ≥ Street) {p.loc['3Q26','p_print_ge_street']:.0%}", fontsize=7.5, color=S2, ha="right", va="bottom")
    ax.text(qs.index("4Q26") + 0.15, p.loc["4Q26", "street_adr_usd"] - 0.6, f"Street ${p.loc['4Q26','street_adr_usd']:.2f} (n 25)\nP(print ≥ Street) {p.loc['4Q26','p_print_ge_street']:.0%}", fontsize=7.5, color=S2, ha="left", va="top")
    ax.set_xticks(x); ax.set_xticklabels(qs, fontsize=8); ax.set_ylabel("ADR, USD"); ax.set_ylim(160, 202); ax.legend(ncol=2, fontsize=7.5, loc="upper left")
    ax.set_title("ADR line vs the Street: year-ago ADR × (1 + ex-FX mechanism + ex-ante FX)" if not own else "The ADR line vs the Street: reported ADR = disclosed year-ago × (1 + ex-FX mechanism + ex-ante FX)", loc="left", fontsize=10)
    if own:
        return _save(fig, "adr_path_vs_street")


def fig_passthrough_posterior():
    draws = np.load(C.OUT / "fx_beta_draws.npy"); fig, ax = plt.subplots(figsize=(8, 3.8))
    names = ["North America", "EMEA", "Latin America", "Asia Pacific"]
    parts = ax.violinplot([draws[:, i] for i in range(4)], positions=np.arange(4), showmedians=False, showextrema=False)
    for b in parts["bodies"]: b.set_facecolor(S1); b.set_alpha(0.35); b.set_edgecolor(S1)
    for i in range(4):
        lo, md, hi = np.percentile(draws[:, i], [5, 50, 95]); ax.plot([i, i], [lo, hi], color=S1, lw=2); ax.plot(i, md, "o", color=INK, ms=5)
        ax.text(i + 0.12, md, f"{md:.2f} [{lo:.2f}, {hi:.2f}]", fontsize=8, va="center", color=INK)
    ax.axhline(1.0, color=S2, lw=1.2, ls="--", label="prior mean = pure translation (β = 1)")
    ax.set_xticks(range(4)); ax.set_xticklabels(names); ax.set_ylabel("pass-through scale β (posterior)"); ax.legend(fontsize=8, loc="upper right")
    ax.set_title("What 17 disclosed quarters say about exposure beyond the frozen baskets: regional pass-through, prior N(1, 0.25²), 90% intervals", loc="left", fontsize=10)
    return _save(fig, "adr_fx_passthrough_posterior")


def fig_constellation():
    j = pd.read_csv(C.ROOT / "data/processed/adrq3/J/J2_proxy_quarterly_panel.csv").set_index("quarter")
    w = pd.read_csv(C.ROOT / "data/processed/adr/04_regional_quarterly_wide.csv").set_index("quarter")
    h = X.history()
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.9))
    panels = [("EMEA ex-FX ADR vs euro-area HICP accommodation", w.adr_yoy_exfx_emea_pct, j.hicp_ea_accommodation, "HICP accommodation y/y", "EMEA ex-FX ADR y/y"),
              ("Global ex-FX ADR vs US lodging CPI (SA)", h.exfx_yoy, j.cpi_lodging_sa, "CPI lodging away from home y/y", "ex-FX ADR y/y"),
              ("Reported ADR vs Marriott / Hilton RevPAR", h.reported_yoy, j.mar_revpar, "MAR RevPAR y/y", "reported ADR y/y")]
    for ax, (title, ys, xs, xl, yl) in zip(axes, panels):
        d = pd.concat([xs.rename("x"), ys.rename("y")], axis=1).dropna(); d = d.loc[[q for q in d.index if q >= "1Q23" or q[-2:] in ("24", "25", "26")]]
        d = d[d.index.str[-2:].isin(["23", "24", "25", "26"])]
        r = float(np.corrcoef(d.x, d.y)[0, 1]) if len(d) > 2 else np.nan
        ax.scatter(d.x, d.y, color=S1, s=28, zorder=3)
        for q, row in d.iterrows(): ax.text(row.x, row.y + 0.15, q, fontsize=6.5, color=INK2, ha="center")
        ax.set_xlabel(xl); ax.set_ylabel(yl); ax.set_title(f"{title}\nr = {r:.2f}, n = {len(d)}", loc="left", fontsize=9)
    if "hlt_revpar" in j.columns:
        d = pd.concat([j.hlt_revpar.rename("x"), h.reported_yoy.rename("y")], axis=1).dropna(); d = d[d.index.str[-2:].isin(["23", "24", "25", "26"])]
        axes[2].scatter(d.x, d.y, color=S2, s=28, marker="s", zorder=3, label="HLT RevPAR"); axes[2].legend(fontsize=8, loc="upper left", handles=[Patch(color=S1, label="MAR RevPAR"), Patch(color=S2, label="HLT RevPAR")])
    fig.subplots_adjust(top=0.78, wspace=0.32); fig.suptitle("Cross-checks on the like-for-like line, honest: only EMEA vs HICP accommodation survives a walk-forward (L: 0.91); the US comps do not", x=0.01, y=0.99, ha="left", fontsize=10)
    return _save(fig, "adr_constellation")


def fig_full_logic():
    fig = plt.figure(figsize=(16, 11))
    gs = fig.add_gridspec(3, 2, height_ratios=[3, 2, 3.4], hspace=0.7, wspace=0.22, top=0.93, bottom=0.06, left=0.05, right=0.99)
    a1 = fig.add_subplot(gs[0, 0]); a2 = fig.add_subplot(gs[1, 0], sharex=a1); fig_fx_walkforward(a1, a2)
    a3 = fig.add_subplot(gs[0:2, 1]); fig_currency_contributions(a3)
    a4 = fig.add_subplot(gs[2, 0]); fig_exfx_mechanism(a4)
    a5 = fig.add_subplot(gs[2, 1]); fig_path_vs_street(a5)
    fig.suptitle("ADR line v1 — the full logic: reported ADR y/y = ex-FX mechanism (core + bundle laps + mix) + FX translation identity (ex ante, spot held)",
                 x=0.01, ha="left", fontsize=12, color=INK)
    return _save(fig, "adr_full_logic")


def main():
    out = [fig_fx_walkforward(), fig_currency_contributions(), fig_exfx_mechanism(), fig_path_vs_street(), fig_passthrough_posterior(), fig_constellation(), fig_full_logic()]
    for p in out: print(p)


if __name__ == "__main__":
    main()
