"""adr_engine / figure_geomix.py — the six-panel geographic-mix logic figure (adr_geomix_logic.png/svg)."""
import textwrap
import numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from . import config as C, figures as G

def T(ax, s, w=96): ax.set_title("\n".join(textwrap.wrap(s, w)), loc="left", fontsize=9)

def main():
    O = C.OUT; qs_h = ['1Q23','2Q23','3Q23','4Q23','1Q24','2Q24','3Q24','4Q24','1Q25','2Q25','3Q25','4Q25','1Q26','2Q26']; qf = C.FORWARD_QUARTERS
    fig = plt.figure(figsize=(17, 12.5)); gs = fig.add_gridspec(3, 2, hspace=0.75, wspace=0.22, top=0.93, bottom=0.05, left=0.05, right=0.99)
    ax = fig.add_subplot(gs[0, 0]); od = pd.read_csv(O/'od_geo_mix_measured_tilt.csv')
    base = od[od.pattern.str.startswith('base')].set_index('quarter').geo_mix_pp.loc[qf]; meas = od[od.pattern.str.startswith('measured OD tilt (central)')].set_index('quarter').geo_mix_pp.reindex(qf)
    tbv = od[od.pattern.str.startswith('tilt B')].set_index('quarter').geo_mix_pp.loc[qf]; x = np.arange(len(qf)); w = 0.27
    ax.bar(x - w, base, w, color=G.S1, label='base: letter buckets 8 / 20 / 18'); ax.bar(x, meas, w, color=G.S3, label='measured origin→destination 10.5 / 16.4 / 14.9'); ax.bar(x + w, tbv, w, color=G.S8, alpha=0.55, label='tilt B 5 / 30 / 25 (retired)')
    for i, q in enumerate(qf): ax.text(i - w, base[q] - 0.12, f"{base[q]:.2f}", ha='center', va='top', fontsize=7.5, color=G.INK)
    ax.set_xticks(x); ax.set_xticklabels(qf); ax.set_ylabel('four-region geo mix, pp of ADR'); ax.axhline(0, color=G.AXIS, lw=0.8); ax.legend(fontsize=7.5, loc='lower left'); ax.set_ylim(-2.4, 0.15)
    T(ax, "1. Between regions: growth lands where ADR is \\$95–159 vs \\$255 in North America. Annual check against the 10-K's own mix line, 2023–25: ours −1.10 / −1.33 / −1.67 vs 10-K −1.08 / −1.24 / −1.58")
    ax = fig.add_subplot(gs[0, 1]); sub = pd.read_csv(O/'geomix_subregional_term.csv').set_index('quarter').subgeo_pp.loc[qs_h]
    eu = pd.read_csv(O/'geomix_eurostat_subregional_term.csv'); euA = eu[(eu.variant.str.startswith('eurostat_shares/panel_growth/median')) & (eu.horizon=='history')].set_index('quarter').subgeo_pp.reindex(qs_h)
    fw = pd.read_csv(O/'geomix_subregional_term_forward.csv').set_index('quarter').subgeo_pp.loc[qf]; xx = np.arange(len(qs_h) + len(qf))
    ax.bar(xx[:len(qs_h)], sub, 0.6, color=G.S2, label='sub-regional mix, panel shares')
    if euA.notna().any(): ax.plot(xx[:len(qs_h)], euA, 'o', color=G.S7, ms=5, mfc=G.SURF, mew=1.5, label='same, Eurostat country weights in EMEA')
    ax.bar(xx[len(qs_h):], fw, 0.6, color=G.S2, alpha=0.45, label='forward rule (differentials carried)')
    ax.axhline(0, color=G.AXIS, lw=0.8); ax.axvspan(len(qs_h) - 0.5, len(xx) - 0.5, color='#e3eefb', lw=0, zorder=0)
    ax.set_xticks(xx); ax.set_xticklabels(qs_h + qf, rotation=45, fontsize=7.5); ax.set_ylabel('sub-regional mix, pp of ADR'); ax.legend(fontsize=7.5, loc='lower right')
    T(ax, "2. Inside regions: country mix from 123 markets × 30 priced countries, mean −0.45pp over 2023–26 and −0.15 over the last four quarters; Eurostat weights move it by 0.02pp")
    ax = fig.add_subplot(gs[1, 0]); r = pd.read_csv(O/'reconcile_emea_quarterly.csv'); r = r[r.in_disclosed_7 == True].set_index('quarter'); x3 = np.arange(len(r))
    ax.bar(x3, r.disclosed_exfx_emea_pct, 0.5, color=G.NEUTRAL, edgecolor=G.AXIS, label='disclosed EMEA ex-FX ADR y/y (whole points)')
    ax.bar(x3, r.hicp_emea_panelwtd_pct, 0.5, color=G.S1, alpha=0.75, label='panel-weighted accommodation CPI'); ax.bar(x3, r.our_emea_mix_pp, 0.5, bottom=r.hicp_emea_panelwtd_pct, color=G.S2, label='+ our within-EMEA country mix')
    ax.plot(x3, r.hicp_emea_panelwtd_pct + r.our_emea_mix_pp + r.global_unit_size_pp + r.global_los_pp, '_', color=G.INK, ms=18, mew=2, label='+ size + LOS (all measured terms)')
    ax.set_xticks(x3); ax.set_xticklabels(r.index); ax.set_ylabel('pp'); ax.legend(fontsize=7.5, loc='upper left'); ax.set_ylim(0, 8.8)
    T(ax, f"3. Reconciliation to the company's accounting: EMEA residual mean {r.resid_vs_panel_pp.mean():+.2f}pp, sd {r.resid_vs_panel_pp.std():.2f} (n {len(r)}); pooled on the 23 disclosed regional prints the gap on our mix has slope 1.13 (cluster-by-region p 0.04), cannot reject the identity's 1.0 \u2014 but LatAm carries it (\u22120.30 without it)")
    ax = fig.add_subplot(gs[1, 1]); it = pd.read_csv(O/'od_implied_tilt.csv'); cen = it[it.kind=='central'].iloc[0]; lo_ = it[['g_emea','g_latam','g_apac']].min(); hi_ = it[['g_emea','g_latam','g_apac']].max()
    x4 = np.arange(3); w = 0.26; ax.bar(x4 - w, [8, 20, 18], w, color=G.S1, label='letter buckets (2Q26)'); ax.bar(x4, [cen.g_emea, cen.g_latam, cen.g_apac], w, color=G.S3, label='measured origin→destination (central, band)')
    ax.errorbar(x4, [cen.g_emea, cen.g_latam, cen.g_apac], yerr=[[cen.g_emea-lo_.g_emea, cen.g_latam-lo_.g_latam, cen.g_apac-lo_.g_apac],[hi_.g_emea-cen.g_emea, hi_.g_latam-cen.g_latam, hi_.g_apac-cen.g_apac]], fmt='none', ecolor=G.INK, capsize=3)
    ax.bar(x4 + w, [5, 30, 25], w, color=G.S8, alpha=0.55, label='tilt B (needs named origins at 22% of nights; ceiling 16.5%)')
    ax.set_xticks(x4); ax.set_xticklabels(['EMEA','LatAm','APAC']); ax.set_ylabel('ex-NA nights growth split, % y/y'); ax.legend(fontsize=7.5, loc='upper left')
    T(ax, "4. Origins to destinations (NTTO, JNTO, ABS, StatCan): India +60% and Brazil +31% land entirely outside North America, but the implied split is flatter than the letters'; ordering test p 0.018")
    ax = fig.add_subplot(gs[2, 0]); sc = pd.read_csv(O/'adr_scenarios.csv'); sc = sc[sc.quarter=='4Q26']
    rules = [('base (mechanism)', 'base:'), ('+ sub-regional mix', 'base + sub-regional country mix'), ('+ measured O-D tilt', 'measured origin'), ('+ tilt B (retired)', 'tilt B'), ('lap-only residual steps', 'lap-only'), ('AR(1) on core', 'AR(1)'), ('core mean reversion', 'core mean')]
    vals, labs = [], []
    for lab, key in rules:
        m = sc[sc.rule.str.contains(key, regex=False)]
        if len(m): vals.append(float(m.adr_usd.iloc[0])); labs.append(lab)
    y5 = np.arange(len(vals)); cols = [G.S1 if l.startswith('base') else (G.S3 if l.startswith('+') else G.S7) for l in labs]
    ax.barh(y5, vals, color=cols, height=0.6); ax.axvline(C.STREET_ADR['4Q26'][0], color=G.S2, lw=2, ls='--'); ax.text(C.STREET_ADR['4Q26'][0] + 0.05, len(vals) - 0.55, f"Street ${C.STREET_ADR['4Q26'][0]:.2f} (n 25)", color=G.S2, fontsize=8)
    for i, v in enumerate(vals): ax.text(v + 0.05, i, f"${v:.2f}", va='center', fontsize=8)
    ax.set_yticks(y5); ax.set_yticklabels(labs, fontsize=8); ax.set_xlim(169.5, 175); ax.invert_yaxis(); ax.set_xlabel('4Q26 ADR, USD')
    T(ax, "5. What each construction gives for 4Q26 ADR: composition moves it by $0.2–0.4 either way; only the assumption on the unobserved core crosses the Street")
    ax = fig.add_subplot(gs[2, 1]); d = pd.read_csv(O/'origin_proxy_review_language_by_region_year.csv')
    for reg, ls in [('GLOBAL','-'), ('EMEA','--')]:
        xr = d[d.region==reg].pivot(index='year', columns='lang', values='share_pct').loc[2022:2026]
        for l, c in [('en', G.S1), ('es', G.S2), ('other', G.MUTED), ('pt', G.S4), ('zh_ja_ko', G.S3)]:
            ax.plot(xr.index, xr[l], ls, marker='o', ms=3.5, color=c, lw=1.5, label=f"{l}" if reg=='GLOBAL' else None)
    ax.set_xticks([2022,2023,2024,2025,2026]); ax.set_xticklabels(['22','23','24','25','26*']); ax.set_ylabel('share of reviews, %'); ax.legend(fontsize=7.5, ncol=5, loc='center right', title='solid = global, dashed = EMEA', title_fontsize=7.5)
    T(ax, "6. Guest-origin proxy from reviewer language: English 71% → 58% of reviews since 2022. Within a market a non-English-reviewed listing is 13% cheaper, so the origin rotation costs ≈0.35% a year")
    fig.suptitle("ADR line v2 — the geographic-mix logic, measured on Airbnb's own supply and reconciled to the company's accounting", x=0.01, ha='left', fontsize=12, color=G.INK)
    return G._save(fig, 'adr_geomix_logic')

if __name__ == "__main__":
    print(main())
