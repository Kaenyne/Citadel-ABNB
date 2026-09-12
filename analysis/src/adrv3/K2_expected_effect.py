"""WS-K, step 2: the expected sign and size of the residual effect per unit of migrated-cohort
share, from the fee mechanics, written down BEFORE the fit (K3). Timestamped.

Mechanics (per $100 of host subtotal on the split fee):
  split fee: host pays 3%, guest pays a separate service fee of about 14% (13.9 to 14.2% of the
  subtotal in the team's models; 15% illustrative in the fee-churn note). Guest total ~ $114.0,
  host nets $97.0, Airbnb $17.0.
  single fee: host pays 15.5% of the host price (4Q25 letter); no guest fee. To keep $97 net the
  host lists at 97 / 0.845 = $114.79, a +14.8% listed-price rise ("payout neutral").
ADR = GBV / nights and GBV counts what the guest pays (host earnings plus fees). So:
  payout-neutral reprice: guest pays 114.79 vs 114.0 -> +0.7% on the cohort's ADR (+0.5% if the
    old guest fee was 14.2%); this is the 0.6 pp take-rate gain, not a price change.
  no reprice: guest pays 100 vs 114 -> -12.3%.
  full "+18.34%" reprice (host forum advice): 118.34 vs 114 -> +3.8%.
  pre-existing single-fee cohort, 15% -> 15.5% on 1 Dec 2025: payout-neutral +0.6% on that
    cohort (0.85/0.845), no reprice -0.5%.
Per 1 pp of blended nights share migrated split -> single, the y/y ADR effect is therefore
  -0.123 pp (no reprice) / +0.005 to +0.007 pp (payout neutral) / +0.038 pp (full over-reprice).
The residual is y/y, so the regressor is the y/y change in the migrated share.

Cross-checks recorded: (a) H card section 4 / table 2.3: +0.16 pp on a 22.5 pp penetration rise
in 3Q26 = 0.0071 per pp; high +0.85 = 0.038; low -0.30 = -0.013. (b) quote-index addendum: the
no-reprice case is rejected by the prints (NA accelerated to +6.3/+6.8 while ~25% migrated), and
full over-repricing on the remaining half is under +2 pp. (c) 12_reprice_summary: the same-listing
quote step is not recoverable (excess mass 0.0 to 1.6% per pair against a ~10% noise floor).

Pre-stated expectation for the K3 coefficient (pp of residual per pp of y/y migrated nights
share): sign positive; central +0.007; plausible range 0.000 to +0.038; anything above +0.05 is
outside the mechanics (it would need listed prices up more than ~20% on the cohort) and anything
below -0.02 is rejected by the prints. Implied 1H26 contribution at the central cohort path
(y/y migrated share +16.6 pp in 1Q26, +21.5 pp in 2Q26): +0.12 and +0.15 pp central, +0.63 and
+0.82 pp at full over-reprice, against an observed step of +2.0 and +2.4 pp over the 2023-25
mean residual of 2.40. So, before fitting: the fee reprice can account for at most about a third
of the 1H26 step and about a twentieth of it in the central case.

py -3.13 analysis/src/adrv3/K2_expected_effect.py
"""
import os
from datetime import datetime
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "data", "processed", "adrv3", "K")
os.makedirs(OUT, exist_ok=True)
PRESTATED_AT = "2026-09-11 21:56:17"  # when the expectation was first recorded (first run of this script), before K3 existed; kept fixed on re-runs
RUN_AT = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
STAMP = PRESTATED_AT

GUEST_FEE = {"low": 0.139, "central": 0.140, "high": 0.142}   # guest service fee as a share of the host subtotal under the split fee
HOST_SPLIT = 0.03
SINGLE = 0.155          # 4Q25 letter, D024 (the task text says 15.3%; the letter says 15.5% and is used)
PRE_SINGLE = 0.15       # standard single fee before 1 Dec 2025 (host_only_fee_history note: 14 to 16%, standard 15%)

rows = []
for gf_label, gf in GUEST_FEE.items():
    guest_old = 100 * (1 + gf)
    host_net = 100 * (1 - HOST_SPLIT)
    p_neutral = host_net / (1 - SINGLE)
    for case, listed in [("no reprice (listed price unchanged)", 100.0),
                         ("half pass-through", 100 + 0.5 * (p_neutral - 100)),
                         ("payout neutral (+14.8% listed)", p_neutral),
                         ("full over-reprice (+18.34% listed, host-forum advice)", 118.34)]:
        eff = 100 * (listed / guest_old - 1)
        rows.append({"cohort": "split -> single 15.5%", "guest_fee_assumption": gf_label, "guest_fee_pct_of_subtotal": gf,
                     "case": case, "listed_price_index": round(listed, 3), "guest_paid_old": round(guest_old, 3),
                     "cohort_adr_effect_pct": round(eff, 3), "residual_pp_per_pp_of_yoy_cohort_share": round(eff / 100, 5),
                     "label": "descriptive arithmetic on sourced fee rates", "recorded_at": STAMP})
# pre-existing single-fee cohort, 15 -> 15.5
for case, listed in [("no reprice", 100.0), ("payout neutral", 100 * (1 - PRE_SINGLE) / (1 - SINGLE))]:
    eff = 100 * (listed / 100 - 1)
    rows.append({"cohort": "pre-existing single 15% -> 15.5% (1 Dec 2025)", "guest_fee_assumption": "n/a", "guest_fee_pct_of_subtotal": 0.0,
                 "case": case, "listed_price_index": round(listed, 3), "guest_paid_old": 100.0,
                 "cohort_adr_effect_pct": round(eff, 3), "residual_pp_per_pp_of_yoy_cohort_share": round(eff / 100, 5),
                 "label": "descriptive arithmetic on sourced fee rates", "recorded_at": STAMP})
# H card cross-check (section 4 / table 2.3): increments over a penetration rise of 0.60 - 0.375 = 0.225 (3Q26) and 0.75 - 0.375 = 0.375 (4Q26)
for q, lo, pt, hi, dpen in [("3Q26", -0.30, 0.16, 0.85, 0.225), ("4Q26", -0.50, 0.26, 1.42, 0.375)]:
    for lab, val in [("low", lo), ("point", pt), ("high", hi)]:
        rows.append({"cohort": f"H card fee-migration increment, {q}, {lab}", "guest_fee_assumption": "n/a", "guest_fee_pct_of_subtotal": 0.0,
                     "case": f"H table 2.3 {lab} {val:+.2f} pp over a {dpen:.3f} penetration rise", "listed_price_index": float("nan"),
                     "guest_paid_old": float("nan"), "cohort_adr_effect_pct": round(100 * val / dpen, 3),
                     "residual_pp_per_pp_of_yoy_cohort_share": round(val / dpen / 100 * 100, 5) if False else round(val / (dpen * 100), 5),
                     "label": "sourced (H note section 4, note 12 bounds)", "recorded_at": STAMP})
# the pre-stated expectation, one row each
share = pd.read_csv(os.path.join(OUT, "K1_migrated_cohort_share.csv"))
c = share[(share.region == "blended") & (share.basis == "nights") & (share.variant == "central")].set_index("quarter")
d1, d2 = float(c.loc["1Q26", "migrated_share_yoy_change"]), float(c.loc["2Q26", "migrated_share_yoy_change"])
exp = [
    {"item": "expected sign of the coefficient", "value": "positive", "basis": "hosts told they can reprice to hold net earnings; the no-reprice case is rejected by the prints (quote-index addendum)"},
    {"item": "expected coefficient, central (pp residual per pp of y/y migrated nights share)", "value": 0.007, "basis": "payout-neutral reprice, +0.7% on the cohort"},
    {"item": "expected coefficient, plausible range", "value": "0.000 to 0.038", "basis": "half pass-through to full +18.34% over-reprice"},
    {"item": "coefficient outside the mechanics", "value": "above 0.05 or below -0.02", "basis": "above 0.05 needs listed prices up more than ~20% on the cohort; below -0.02 is rejected by the 1H26 NA prints"},
    {"item": "implied 1H26 residual contribution, central", "value": f"{0.007 * d1 * 100:+.2f} pp (1Q26), {0.007 * d2 * 100:+.2f} pp (2Q26)", "basis": f"y/y migrated nights share {d1 * 100:+.1f} pp and {d2 * 100:+.1f} pp (K1 central)"},
    {"item": "implied 1H26 residual contribution, full over-reprice", "value": f"{0.038 * d1 * 100:+.2f} pp (1Q26), {0.038 * d2 * 100:+.2f} pp (2Q26)", "basis": "same shares at 0.038"},
    {"item": "observed 1H26 step over the 2023-25 mean residual (2.40)", "value": "+1.98 pp (1Q26), +2.45 pp (2Q26)", "basis": "adr_history_components.csv residual_pricing_pp"},
    {"item": "share of the step the fee reprice can explain", "value": "about 5% central, about 30% at full over-reprice", "basis": "ratio of the two lines above"},
    {"item": "pre-existing 15 -> 15.5 cohort", "value": "+0.006 per pp of that cohort's nights share, in the y/y window 4Q25 (one third) to 3Q26", "basis": "0.85/0.845 payout-neutral; about +0.1 pp blended at the central 16% cohort"},
    {"item": "recorded_at", "value": STAMP, "basis": "written before K3 was run"},
]
pd.DataFrame(rows).to_csv(os.path.join(OUT, "K2_expected_effect.csv"), index=False)
pd.DataFrame(exp).assign(recorded_at=STAMP, last_run_at=RUN_AT).to_csv(os.path.join(OUT, "K2_expected_effect_prestated.csv"), index=False)
print(pd.DataFrame(rows)[["cohort", "guest_fee_assumption", "case", "cohort_adr_effect_pct", "residual_pp_per_pp_of_yoy_cohort_share"]].to_string())
print()
print(pd.DataFrame(exp).to_string())
print("pre-stated at", STAMP, "| this run at", RUN_AT)
