"""Recompute the numbers quoted in docs/pitch-model-v2/lines/final_adr.md from the
engine output CSVs (read-only). Run from the worktree root:
    py -3.13 data/processed/pitch_model_v2/receipts/ADR_AUDIT/doc_consistency_check.py
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
E = ROOT / "data/processed/pitch_model_v2/adr_engine"
QS = ["1Q23","2Q23","3Q23","4Q23","1Q24","2Q24","3Q24","4Q24","1Q25","2Q25","3Q25","4Q25","1Q26","2Q26"]

def p(title, *rows):
    print(f"\n## {title}")
    for r in rows:
        print("  ", r)

# 1. identity vs disclosed FX
h = pd.read_csv(ROOT / "data/processed/q3nowcast/H/adr_history_components.csv")
h14 = h[h.quarter.isin(QS)]
p("identity_check_pp (H file)", f"n={len(h14)}", f"max|id|={h14.identity_check_pp.abs().max():.4f}",
  f"quarters listed: {list(h14.quarter)}")
k = pd.read_csv(ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv")
k14 = k[k.quarter.isin(QS)].copy()
k14["id"] = k14.adr_yoy_reported_pct - k14.adr_yoy_exfx_pct - k14.fx_pts_adr
p("kpi panel: reported - exfx - fx_pts_adr", f"n={k14.id.notna().sum()}", f"max|id|={k14.id.abs().max():.4f}")

# 2. walk-forward
s = pd.read_csv(E / "fx_scores.csv")
def cell(v, w, o):
    r = s[(s.variant == v) & (s.window == w) & (s.origin == o)].iloc[0]
    return r
rows = []
for v in ["V0_translation", "V1_passthrough", "V2_eur_ols", "V3_usd_broad_ols", "naive_last_disclosed"]:
    rows.append(v + " ratio " + " / ".join(f"{cell(v,w,o).ratio_vs_naive:.3f}" for w in ["W1","W2"] for o in ["O2","O3"])
               + " | boot90hi " + " / ".join(f"{cell(v,w,o).ratio_boot90_hi:.3f}" for w in ["W1","W2"] for o in ["O2","O3"])
               + " | bias " + " / ".join(f"{cell(v,w,o).bias_pp:+.2f}" for w in ["W1","W2"] for o in ["O2","O3"])
               + " | interval " + " / ".join(f"{cell(v,w,o).interval_ratio:.3f}" for w in ["W1","W2"] for o in ["O2","O3"]))
p("fx_scores.csv ratios (W1O2/W1O3/W2O2/W2O3)", *rows)
p("O1 cells V0", *[f"{w} O1 n={cell('V0_translation',w,'O1').n} rmse={cell('V0_translation',w,'O1').rmse_pp:.3f} naive={cell('V0_translation',w,'O1').rmse_naive_pp:.3f} ratio={cell('V0_translation',w,'O1').ratio_vs_naive:.3f} boot={cell('V0_translation',w,'O1').ratio_boot90_hi:.3f} intr={cell('V0_translation',w,'O1').interval_ratio:.3f}" for w in ["W1","W2"]])
p("O2/O3 cells V0 full", *[f"{w} {o} n={cell('V0_translation',w,o).n} rmse={cell('V0_translation',w,o).rmse_pp:.3f} naive={cell('V0_translation',w,o).rmse_naive_pp:.3f}" for w in ["W1","W2"] for o in ["O2","O3"]])

# 3. adr_path
a = pd.read_csv(E / "adr_path.csv").set_index("quarter")
p("adr_path.csv", *[f"{q}: adr={a.loc[q,'adr_usd']:.2f} yoy={a.loc[q,'adr_yoy_reported_pct']:.3f} exfx={a.loc[q,'adr_yoy_exfx_pct']:.3f} fx={a.loc[q,'fx_pp']:.3f} band={a.loc[q,'band_half_pp']:.3f} lo={a.loc[q,'adr_usd_lo']:.2f} hi={a.loc[q,'adr_usd_hi']:.2f} street={a.loc[q,'street_adr_usd']} z={a.loc[q,'z_vs_street']} p={a.loc[q,'p_print_ge_street']} n={a.loc[q,'street_n']} gbv={a.loc[q,'gbv_busd']:.2f} nights={a.loc[q,'nights_m']} p10={a.loc[q,'fx_p10']} p90={a.loc[q,'fx_p90']} base={a.loc[q,'adr_usd_base_year']}" for q in a.index])
p("check: base * (1+yoy)", *[f"{q}: {a.loc[q,'adr_usd_base_year']*(1+a.loc[q,'adr_yoy_reported_pct']/100):.4f}" for q in ["3Q26","4Q26"]])

# 4. geo mix method check
g = pd.read_csv(E / "geo_mix_method_check.csv")
gw = g[g.quarter.isin(["2Q24","3Q24","4Q24","1Q25","2Q25","3Q25","4Q25","1Q26","2Q26"])]
p("geo_mix_method_check 2Q24-2Q26", f"n={len(gw)}", f"mean|diff|={gw.diff_pp.abs().mean():.4f}", f"max|diff|={gw.diff_pp.abs().max():.4f}",
  f"full 1Q23-2Q26 max|diff|={g.diff_pp.abs().max():.4f} (1Q23 {g.diff_pp.iloc[0]:.3f})")

# 5. annual reconcile
r = pd.read_csv(E / "reconcile_annual.csv").set_index("year")
p("reconcile_annual", *[f"{y}: ours={r.loc[y,'our_geo4_pp']:.3f} 10-K={r.loc[y,'geo_mix_pp_10k']:.3f} gap={r.loc[y,'our_geo4_pp']-r.loc[y,'geo_mix_pp_10k']:+.3f} | our_core={r.loc[y,'our_core_pp']:.3f} our_residual={r.loc[y,'our_residual_pp']:.3f} implied_price={r.loc[y,'implied_price_pp']:.3f} rebased={r.loc[y,'implied_price_rebased_pp']:.3f} size={r.loc[y,'our_size_pp']:.3f} size10k={r.loc[y,'size_mix_pp_10k']:.3f}" for y in r.index])

# 6. sub-regional term
t = pd.read_csv(E / "geomix_subregional_term.csv")
print("   sub-regional file tail:", t.tail(6)[["quarter","subgeo_pp"]].to_dict("records"))
hist = t[t.quarter.isin(QS)]
last4 = t[t.quarter.isin(["3Q25","4Q25","1Q26","2Q26"])]
pos4 = t.iloc[-4:]
tf = pd.read_csv(E / "geomix_subregional_term_forward.csv").set_index("quarter")
p("geomix_subregional_term", f"mean 1Q23-2Q26 n={len(hist)}: {hist.subgeo_pp.mean():.4f}",
  f"last four by label (3Q25..2Q26): {last4.subgeo_pp.mean():.4f}  values={[round(x,3) for x in last4.subgeo_pp]}",
  f"positional iloc[-4:] {list(pos4.quarter)}: {pos4.subgeo_pp.mean():.4f}  (trap)",
  f"2Q26 = {t[t.quarter=='2Q26'].subgeo_pp.iloc[0]:.3f}",
  f"forward 3Q26={tf.loc['3Q26','subgeo_pp']:.4f} 4Q26={tf.loc['4Q26','subgeo_pp']:.4f}",
  f"4Q26 $ effect on 173.03: {173.034*tf.loc['4Q26','subgeo_pp']/100:.3f}")
j = json.load(open(E / "00_summary.json"))
p("00_summary.json geomix", j["geomix"])

# 7. origin rotation
o = pd.read_csv(E / "origin_lang_rotation_ltm.csv")
print("   regions:", sorted(o.region.unique()), " langs:", sorted(o.lang.unique()))
gl = o[o.region == "GLOBAL"].set_index("lang")
p("origin_lang_rotation_ltm GLOBAL rows", f"ALL_NON_EN growth 24-26 = {gl.loc['ALL_NON_EN','growth_pct_24_26']:.2f}%",
  f"en growth 24-26 = {gl.loc['en','growth_pct_24_26']:.2f}%",
  f"en share 2024={gl.loc['en','share_pct_2024']:.1f} 2026={gl.loc['en','share_pct_2026']:.1f}",
  f"ALL_NON_EN growth 25-26 = {gl.loc['ALL_NON_EN','growth_pct_25_26']:.2f}%  en 25-26 = {gl.loc['en','growth_pct_25_26']:.2f}%")
# trap demo
naive = o[o.lang != "en"].groupby(lambda i: 0)[["reviews_ltm_2024","reviews_ltm_2026"]].sum().iloc[0]
p("trap (a): naive sum of non-en rows incl. GLOBAL/TOTAL/ALL_NON_EN", f"{(naive.reviews_ltm_2026/naive.reviews_ltm_2024-1)*100:.1f}%")
ps = pd.read_csv(E / "origin_lang_price_summary.csv")
w = ps.total_reviews_ltm_2026
p("origin_lang_price_summary", f"review-weighted median rel price = {np.average(ps.rel_price_vs_en_median, weights=w):.4f} -> {(1-np.average(ps.rel_price_vs_en_median, weights=w))*100:.1f}% cheaper",
  f"review-weighted wtd rel price = {np.average(ps.rel_price_vs_en_wtd, weights=w):.4f} -> {(1-np.average(ps.rel_price_vs_en_wtd, weights=w))*100:.1f}% cheaper",
  f"simple mean median = {(1-ps.rel_price_vs_en_median.mean())*100:.1f}%")
pm = pd.read_csv(E / "origin_lang_price_mix_effect.csv").set_index("region")
p("origin_lang_price_mix_effect GLOBAL", f"mix_pct_24_26_wtd={pm.loc['GLOBAL','mix_pct_24_26_wtd']:.3f} (per yr /2 = {pm.loc['GLOBAL','mix_pct_24_26_wtd']/2:.3f})",
  f"mix_pct_25_26_wtd={pm.loc['GLOBAL','mix_pct_25_26_wtd']:.3f}", f"median 24-26={pm.loc['GLOBAL','mix_pct_24_26_median']:.3f}")
gq = pd.read_csv(E / "origin_lang_global_quarter.csv")
en = gq[(gq.lang == "en")].set_index("period")
p("origin_lang_global_quarter en share_chg_pp last 6", en.share_chg_pp.tail(6).round(2).to_dict())
rq = pd.read_csv(E / "origin_lang_region_quarter.csv")
em = rq[(rq.region == "EMEA") & (rq.lang == "en")].set_index("period")
p("EMEA en share last 4", em.share_pct.tail(4).round(2).to_dict())
# annual en share 2022 vs 2026 from global quarter
gq["year"] = gq.period.str[:4]
ann = gq.groupby(["year","lang"]).reviews.sum().unstack()
p("annual en share", {y: round(ann.loc[y,"en"]/ann.loc[y].sum()*100,1) for y in ann.index})

# 8. size mix
sr = pd.read_csv(E / "sizemix_routes.csv")
p("sizemix_routes", *[f"{r.route} | {r.period} | size_pp={r.size_pp}" for r in sr.itertuples()])
sp = pd.read_csv(E / "sizemix_rebased_plug.csv")
p("sizemix_rebased_plug", *[f"{r.year} {r.variant}: size={r.size_pp} implied_lfl={r.implied_lfl_price_pp}" for r in sp.itertuples()])

# 9. currency contributions
c = pd.read_csv(E / "fx_currency_contributions.csv")
for q in ["3Q26","4Q26"]:
    cq = c[c.quarter == q].sort_values("contribution_pp", ascending=False)
    p(f"fx_currency_contributions {q}", *[f"{r.ccy}: yoy={r.yoy_pct:+.2f}% w={r.gbv_weight*100:.1f}% contrib={r.contribution_pp:+.3f}" for r in cq.itertuples()],
      f"sum={cq.contribution_pp.sum():+.4f}", f"AUD+MXN+BRL={cq[cq.ccy.isin(['AUD','MXN','BRL'])].contribution_pp.sum():+.3f}",
      f"obs_frac={cq.obs_frac.iloc[0]:.3f}")
p("4Q27 contributions", c[c.quarter=="4Q27"][["ccy","yoy_pct","contribution_pp"]].to_string(index=False))

# 10. scenarios ladder 4Q26
sc = pd.read_csv(E / "adr_scenarios.csv")
p("adr_scenarios 4Q26", *[f"{r.rule[:70]} | exfx={r.exfx_pct:.2f} adr={r.adr_usd:.2f} vs={r.vs_base_usd:+.2f}" for r in sc[sc.quarter=="4Q26"].itertuples()])
p("adr_scenarios 3Q26", *[f"{r.rule[:70]} | exfx={r.exfx_pct:.2f} adr={r.adr_usd:.2f} vs={r.vs_base_usd:+.2f}" for r in sc[sc.quarter=="3Q26"].itertuples()])

# 11. core stats
x = pd.read_csv(E / "exfx_history.csv").set_index("quarter")
core = x.core; res = x.residual
m = core.loc[[q for q in QS if q[-2:] in ("23","24","25")]]
mr = res.loc[m.index]
p("core / residual stats", f"core 2023-25 mean={m.mean():.4f} (n={len(m)}); residual 2023-25 mean={mr.mean():.4f}",
  f"2Q26 core={core.loc['2Q26']:.4f}; gap to core mean={core.loc['2Q26']-m.mean():.3f}; gap to residual mean={core.loc['2Q26']-mr.mean():.3f}",
  f"sd of quarterly core changes since 1Q23 = {core.diff().dropna().std(ddof=1):.3f} (ddof0 {core.diff().dropna().std(ddof=0):.3f})",
  f"sd of quarterly residual changes = {res.diff().dropna().std(ddof=1):.3f}",
  f"core steps 3Q25={res.loc['3Q25']-res.loc['2Q25']:+.3f} 4Q25={res.loc['4Q25']-res.loc['3Q25']:+.3f} 1Q26={res.loc['1Q26']-res.loc['4Q25']:+.3f} 2Q26={res.loc['2Q26']-res.loc['1Q26']:+.3f}",
  f"core share of exfx 4Q26 = {3.8493/2.7841*100:.0f}% ; of 3Q26 = {3.8493/3.3159*100:.0f}%")
fb = pd.read_csv(E / "exfx_forward_base.csv").set_index("quarter")
p("exfx_forward_base", fb[["core","bundle","geo_mix","unit_size","los_mix","seats","interaction","exfx_yoy"]].round(3).to_string())
# mean reversion with core mean vs residual mean
exfx_mr_res = fb.loc["4Q26","exfx_yoy"] - core.loc["2Q26"] + mr.mean()
exfx_mr_core = fb.loc["4Q26","exfx_yoy"] - core.loc["2Q26"] + m.mean()
fx4 = a.loc["4Q26","fx_pp"]
p("mean reversion 4Q26", f"exfx with residual mean {mr.mean():.3f}: {exfx_mr_res:.3f} -> ADR {167.51*(1+(exfx_mr_res+fx4)/100):.2f}",
  f"exfx with core mean {m.mean():.3f}: {exfx_mr_core:.3f} -> ADR {167.51*(1+(exfx_mr_core+fx4)/100):.2f}")

# 12. Australia share of APAC panel stays
sv = pd.read_csv(E / "stays_yoy_by_country_vmatch.csv")
ap = sv[sv.region == "APAC"]
print("\n## APAC panel countries:", sorted(ap.country.unique()))
for q in ["2Q26","1Q26","4Q25","3Q25","2Q25"]:
    aq = ap[ap.quarter == q]
    tot = aq.n_cur.sum()
    au = aq[aq.country == "australia"].n_cur.sum()
    print(f"   {q}: AU n_cur {au:.0f} / APAC {tot:.0f} = {au/tot*100:.1f}%  (countries {len(aq)})")
ltm = ap[ap.quarter.isin(["3Q25","4Q25","1Q26","2Q26"])]
print(f"   LTM 3Q25-2Q26: {ltm[ltm.country=='australia'].n_cur.sum()/ltm.n_cur.sum()*100:.1f}%")
cy = ap[ap.quarter.isin(["1Q25","2Q25","3Q25","4Q25"])]
print(f"   CY2025: {cy[cy.country=='australia'].n_cur.sum()/cy.n_cur.sum()*100:.1f}%")
h1 = ap[ap.quarter.isin(["1Q26","2Q26"])]
print(f"   1H26: {h1[h1.country=='australia'].n_cur.sum()/h1.n_cur.sum()*100:.1f}%")
all_countries = sorted(sv.country.unique())
print("   all panel countries:", all_countries)
for cc in ["india","united-arab-emirates","malaysia","indonesia","vietnam","thailand","singapore"]:
    print(f"   {cc}: present={cc in all_countries}")

# 13. H2 scores and market panel
p("geomix_h2_scores", pd.read_csv(E / "geomix_h2_scores.csv").round(3).to_string(index=False))
mp = pd.read_csv(E / "market_panel_scores.csv")
p("market_panel_scores primary rows", mp[mp.spec.str.contains("M2 ")|mp.spec.str.contains("M2-exUS")][["spec","n","n_markets","b","p","ci_lo","ci_hi"]].round(3).to_string(index=False))

# 14. FY ADR
p("FY", f"FY26={a.loc['FY26','adr_usd']:.2f} FY27={a.loc['FY27','adr_usd']:.2f} FY27 yoy={a.loc['FY27','adr_yoy_reported_pct']:.3f} nights={a.loc['FY27','nights_m']}")
