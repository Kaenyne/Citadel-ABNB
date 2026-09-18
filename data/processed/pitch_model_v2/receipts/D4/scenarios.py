"""D4 scenario arithmetic: ADR ex-FX and total ADR for base / short / breaker, 3Q26 and 4Q26.

Reads only committed outputs of the adrv3 P package (reproduced exit 0 through the wrapper,
receipt_P1_card_v3.json). Writes only into this receipt folder. It fits nothing.

Scenario device: the record has no named three-scenario ADR table. The one line that moves is
the unobserved like-for-like pricing residual plus its K mechanics increment. K4's residual
scenario table and K2's pre-stated coefficient range supply the three settings:

  short   residual at the K4 floor  (3Q26 2.398 = the 2023-25 mean, mean reversion;
                                     4Q26 3.056 = dated product steps lap at the anniversary)
          K line held at its central mechanics point (SYNTHESIS s4 point 2 convention)
  base    residual at last_q 4.849326 (the pre-registered v3 rule), K line at its point
  breaker residual at last_q 4.849326, K line at the top of K2's pre-stated coefficient
          range (0.038 per pp of share change)

Measured / assumed mix terms are held at their card points in every scenario; FX is N's
midpoint estimator in every scenario. Everything is descriptive, not a validated forecast.
"""
from __future__ import annotations
import os
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))

terms = pd.read_csv(os.path.join(ROOT, "data", "processed", "adrv3", "P", "P1_card_v3_terms.csv"))
card = pd.read_csv(os.path.join(ROOT, "data", "processed", "adrv3", "P", "adr_card_v3.csv"))

T = terms[(terms.variant == "v3_with_K") & (terms.in_point)].set_index(["quarter", "term"])

BASE_ADR = {"3Q26": 171.29, "4Q26": 167.51}          # 3Q25 and 4Q25 reported ADR, H history
FX_MID = {"3Q26": -0.43, "4Q26": 0.15}                # N midpoint estimator, card cells
MIX = ["geographic_mix", "unit_size_party", "length_of_stay_mix", "new_business_seats", "interaction"]

rows = []
for q in ("3Q26", "4Q26"):
    mix = {m: float(T.loc[(q, m), "point_pp"]) for m in MIX}
    res_pt = float(T.loc[(q, "like_for_like_pricing_residual"), "point_pp"])
    res_lo = float(T.loc[(q, "like_for_like_pricing_residual"), "lo_pp"])
    k_pt = float(T.loc[(q, "fee_migration_mechanics_K"), "point_pp"])
    k_hi = float(T.loc[(q, "fee_migration_mechanics_K"), "hi_pp"])
    settings = {
        "base":    (res_pt, k_pt),
        "short":   (res_lo, k_pt),
        "breaker": (res_pt, k_hi),
    }
    for scen, (res, k) in settings.items():
        exfx = res + k + sum(mix.values())
        rep = exfx + FX_MID[q]
        adr = BASE_ADR[q] * (1.0 + rep / 100.0)
        r = {"scenario": scen, "period": q, "residual_pp": round(res, 4), "k_line_pp": round(k, 4)}
        r.update({m + "_pp": round(v, 4) for m, v in mix.items()})
        r.update({"adr_exfx_yoy_pct": round(exfx, 3), "fx_pp": FX_MID[q],
                  "adr_reported_yoy_pct": round(rep, 3), "adr_usd": round(adr, 2)})
        rows.append(r)

out = pd.DataFrame(rows)
out.to_csv(os.path.join(HERE, "D4_scenarios.csv"), index=False)
print(out.to_string(index=False))

# ---- cross-checks against committed card cells -------------------------------------------
print("\ncross-checks vs adr_card_v3.csv (with_K, midpoint):")
for q in ("3Q26", "4Q26"):
    c = card[(card.quarter == q) & (card.variant == "v3_with_K") & (card.fx_estimator == "midpoint")].iloc[0]
    b = out[(out.period == q) & (out.scenario == "base")].iloc[0]
    print(f"  {q} base: exfx {b.adr_exfx_yoy_pct} vs card {c.adr_exfx_yoy_pp} | "
          f"reported {b.adr_reported_yoy_pct} vs card {c.adr_reported_yoy_pp} | "
          f"usd {b.adr_usd} vs card {c.adr_usd_point}")

# SYNTHESIS s4 point 2: 3Q26 mean reversion is "about +1.0% ($173.0)"
s3 = out[(out.period == "3Q26") & (out.scenario == "short")].iloc[0]
print(f"\nSYNTHESIS s4.2 check: 3Q26 short reported {s3.adr_reported_yoy_pct}% / ${s3.adr_usd} "
      f"(note says about +1.0% / $173.0)")
# SYNTHESIS s3: 4Q26 lap-only WITHOUT the K line is "+2.1% ($170.9)"
q4 = out[(out.period == "4Q26") & (out.scenario == "short")].iloc[0]
lap_no_k = q4.residual_pp + sum(float(T.loc[("4Q26", m), "point_pp"]) for m in MIX) + FX_MID["4Q26"]
print(f"SYNTHESIS s3 check: 4Q26 lap-only without K = {lap_no_k:.3f}% / "
      f"${BASE_ADR['4Q26'] * (1 + lap_no_k / 100):.2f} (note says +2.1% / $170.9)")

# the measured mix terms net, the assumed fills net (SYNTHESIS s4 point 1)
m3 = {m: float(T.loc[("3Q26", m), "point_pp"]) for m in MIX}
print(f"\n3Q26 measured mix (geo+size+LOS) = {m3['geographic_mix']+m3['unit_size_party']+m3['length_of_stay_mix']:.3f} pp; "
      f"assumed fills (seats+interaction) = {m3['new_business_seats']+m3['interaction']:.3f} pp "
      f"(SYNTHESIS s4.1 says -0.57 and -0.58)")

# R07 / B02 gates
print("\ngates: R07 risk-adr-residual-persists needs reported >= +4.4%; "
      "B02 bonus-adr-residual-reverts needs reported <= +2.0%")
for _, r in out[out.period == "3Q26"].iterrows():
    print(f"  3Q26 {r.scenario}: {r.adr_reported_yoy_pct}%  R07 {'YES' if r.adr_reported_yoy_pct >= 4.4 else 'no'}  "
          f"B02 {'YES' if r.adr_reported_yoy_pct <= 2.0 else 'no'}")
print("\nwritten:", os.path.join(HERE, "D4_scenarios.csv"))
