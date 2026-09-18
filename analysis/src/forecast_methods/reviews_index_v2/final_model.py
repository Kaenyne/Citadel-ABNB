"""Final nights model: stays (the business) vs print (what Airbnb reports) vs Street.
   print_t = stays_t + I_t,   I_t = net option inflation = options written that will later cancel - cancellations landing
   Stays: v2 read for 3Q26; forward = the mechanism path (DEC-0019/0025) which carries the filed laps.
   I_t: observed 3Q25-2Q26 (Stage C gaps); 3Q26 scenarios {0, +0.72 mean gap, +1.59 wave}; base 3Q26 = DEC-0029 print 9.886
        minus stays 9.35 = +0.54; 4Q26 base 0 (plateau after the July expansion), short = the record's cancellation drag
        (base 8.12 -> short 7.61, final_nights.md section 4.4); 2027 short not sized (DEC-0020 defers the short).
   Nothing fitted; every input cited."""
import json
import numpy as np, pandas as pd
import config as C

SHORT_4Q26_PRINT = 7.61     # final_nights.md section 4.4: base 8.12 less the cancellation drag = short 7.61
CEILING = "no further RNPL access growth after the July 2026 eligibility expansion (UK/AU/CA done Feb-Mar 2026; BRL/INR/TRY excluded; Europe not in the rollout list)"
EXERCISE_AT = "stay date: payment is due shortly before the free-cancellation window closes (ledger D002: flexible 24h, moderate 5 days before check-in)"


def landing_table(M):
    """Level channel. A cohort's exercised options land at its STAY dates, so each writing wave's cancellations are
    timed by the K2 kernel (share of a cohort's stays landing 0..3 quarters after booking). Cohort sizes are the
    observed gaps (pp of nights, at the historical exercise rate); 3Q26 uses the base writing term (+0.54)."""
    def landing(bq):
        w = np.array([M[((bq - 1 + k) % 4) + 1][k] for k in range(4)]); return w / w.sum()
    qs = ["3Q25", "4Q25", "1Q26", "2Q26", "3Q26", "4Q26", "1Q27", "2Q27", "3Q27"]
    g = pd.read_csv(C.OUT / "stage_c_gap.csv"); g = g[g.variant == "primary"].set_index("qi").gap_pp
    waves = [("3Q25 US launch", 3, 0, float(g[C.qi(2025, 3)])), ("4Q25", 4, 1, float(g[C.qi(2025, 4)])),
             ("1Q26", 1, 2, float(g[C.qi(2026, 1)])), ("2Q26 international wave", 2, 3, float(g[C.qi(2026, 2)])),
             ("3Q26 July expansion (base +0.54)", 3, 4, 0.54)]
    tab = pd.DataFrame(0.0, index=[w[0] for w in waves], columns=qs)
    for name, bq, start, size in waves:
        for k, share in enumerate(landing(bq)):
            if start + k < len(qs): tab.loc[name, qs[start + k]] = max(size, 0.0) * share
    tab.loc["cancellations landing, pp"] = tab.sum()
    tab.to_csv(C.OUT / "final_model_landing.csv"); return tab


def build():
    c3 = json.loads((C.OUT / "stage_c3_3q26.json").read_text()); g = pd.read_csv(C.OUT / "stage_c_gap.csv"); g = g[g.variant == "primary"]
    stays_3q26, band = c3["implied_nights_yoy"], c3["band_pp"]
    rows = []
    for _, r in g.iterrows():
        rows.append(dict(quarter=f"{int(r.qi)%4+1}Q{str(int(r.qi)//4)[2:]}", phase="observed", stays_yoy=r.mapped_pct, print_yoy=r.actual_pct, I_pp=r.gap_pp,
                         street_yoy=np.nan, source="Stage C: mapped = stays-implied, actual = print"))
    base = {b["q"]: b for b in C.BASE_PATH}
    I3 = dict(zero=0.0, mean_gap=float(g.gap_pp.mean()), wave=float(g.gap_pp.max()), base=base["3Q26"]["base_yoy"] - stays_3q26)
    rows.append(dict(quarter="3Q26", phase="nets: July writing laps the US launch", stays_yoy=stays_3q26, print_yoy=base["3Q26"]["base_yoy"], I_pp=I3["base"],
                     street_yoy=(C.STREET["3Q26"]["mean_m"] / C.BASE_3Q25_M - 1) * 100,
                     source=f"stays = v2 read +/-{band:.2f}; print base = DEC-0029; print range {stays_3q26 + I3['zero']:.2f}-{stays_3q26 + I3['wave']:.2f} under I in {{0, +{I3['mean_gap']:.2f}, +{I3['wave']:.2f}}}"))
    rows.append(dict(quarter="4Q26", phase="small hit: laps 4Q25 writing, little new access", stays_yoy=base["4Q26"]["base_yoy"], print_yoy=base["4Q26"]["base_yoy"], I_pp=0.0,
                     street_yoy=(C.STREET["4Q26"]["mean_m"] / C.BASE_4Q25_M - 1) * 100,
                     source=f"base carries the -0.78 lap, no drag; short print {SHORT_4Q26_PRINT} (drag -{base['4Q26']['base_yoy'] - SHORT_4Q26_PRINT:.2f}, DEC-0020 deferred)"))
    for q in ["1Q27", "2Q27", "3Q27", "4Q27"]:
        rows.append(dict(quarter=q, phase={"1Q27": "flat: laps the -0.07", "2Q27": "THE HIT: laps the 2Q26 wave at the ceiling"}.get(q, "laps land"), stays_yoy=base[q]["base_yoy"], print_yoy=base[q]["base_yoy"], I_pp=0.0, street_yoy=np.nan,
                         source=base[q]["decomposition"] + f" ({base[q]['dec']})"))
    df = pd.DataFrame(rows)
    # the option term in y/y form: this quarter's net writing minus the year-ago quarter's (what the KPI laps)
    gap_by_q = {r["quarter"]: r["I_pp"] for r in rows}
    def lap(q):
        yq = f"{q[0]}Q{int(q[2:]) - 1}"; return gap_by_q.get(yq, np.nan)
    df["I_yoy_pp"] = [r.I_pp - lap(r.quarter) if r.quarter in ("3Q26", "4Q26", "1Q27", "2Q27") else np.nan for _, r in df.iterrows()]
    df["I_yoy_wave_pp"] = [(meta_wave - lap(r.quarter)) if r.quarter == "3Q26" else np.nan for _, r in df.iterrows()] if (meta_wave := float(g.gap_pp.max())) else np.nan
    df["stays_level_m"] = np.nan; df["print_level_m"] = np.nan
    prev = {"3Q26": C.BASE_3Q25_M, "4Q26": C.BASE_4Q25_M}
    for i, r in df.iterrows():
        if r.quarter in prev:
            df.loc[i, "stays_level_m"] = prev[r.quarter] * (1 + r.stays_yoy / 100); df.loc[i, "print_level_m"] = prev[r.quarter] * (1 + r.print_yoy / 100)
        elif r.quarter in base:
            df.loc[i, "print_level_m"] = base[r.quarter]["base_m"]; df.loc[i, "stays_level_m"] = base[r.quarter]["base_m"]
    import data as D
    landing = landing_table(D.load_kernel())
    meta = dict(stays_3q26=stays_3q26, band=band, ceiling=CEILING, exercise_at=EXERCISE_AT,
                landing_pp={q: float(landing.loc["cancellations landing, pp", q]) for q in landing.columns}, I_3q26=I3, short_4q26_print=SHORT_4Q26_PRINT, base_4q26_print=base["4Q26"]["base_yoy"],
                filed_laps={"4Q26": -0.78, "1Q27": -1.105, "2Q27": -1.649, "3Q27": -1.649, "4Q27": -1.649},
                ceiling_assumption="no further access growth after the July 2026 expansion; a European launch would defer the 2Q27 hit")
    df.to_csv(C.OUT / "final_model_paths.csv", index=False); (C.OUT / "final_model_meta.json").write_text(json.dumps(meta, indent=2))
    return df, meta


if __name__ == "__main__":
    import sys; sys.path.insert(0, ".")
    pd.set_option("display.width", 220)
    df, meta = build(); print(pd.read_csv(C.OUT / "final_model_landing.csv", index_col=0).round(2).to_string()); print(df[["quarter", "phase", "stays_yoy", "print_yoy", "I_pp", "I_yoy_pp", "street_yoy", "print_level_m"]].round(2).to_string(index=False)); print(meta)
