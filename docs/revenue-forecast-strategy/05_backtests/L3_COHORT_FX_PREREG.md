# L3 cohort FX/RNPL — preregistration

2026-09-13 23:02 UTC. Agent cohort_fx, branch codex/lane3-full, base 1c87628.
Written before executing package tests or scenarios. Claim: WORKBOARD_L3_v1.md.

## Pass lines and decisions fixed before execution

Implementation passes only if exposure and RNPL allocations conserve to 1 within 1e-10; a reconstruction from reported USD GBV returns the inherited kernel within 1e-8 USD million; the specified boundary, currency direction, missing-rate, provenance, information-date and double-counting counterexamples pass; and a fresh output directory rebuild produces identical analytical files. Failures will be retained in the results note. Frozen modules and data remain untouched.

Research acceptance additionally requires observed, dated revenue-contributing RNPL cohort/currency shares, verified FX fixing/recognition mapping, a compatible pre-hedge basis, and evidence on both W1 and W2. Missing identification yields PARTIAL even if implementation passes. No backtest of fabricated cohort shares, probabilities, confidence interval or investment adoption is permitted. W1/W2 forecast claims start at n=0.

## Specification

Import kernel_engine_v2.engine unchanged. Reuse its public pit_lambda and kernel_forecast APIs at 2026-09-13; keep the 2/3, 1/3 coefficients. The executable real-input example is 2026Q3, using already reported Q1/Q2 GBV, with 2025Q3 as a retrospective same-basis YoY illustration. Earlier lambda calls occur after their guide-date letters as required by the K0 API; the current scenario shares are never labeled historical PIT.

For each booking cohort b and currency c, start from kernel-contributing reported dollars C_bc=lambda*a_b*GBV_b*s_bc, where s is an explicitly assumed reported-dollar currency share. At fixed reference FX e0_c, f_bc=e_bc/e0_c and C0_bc=C_bc/f_bc. R0=sum C0_bc and w_bc=C0_bc/R0. Reconstruct the ordinary baseline B=sum C0_bc*f_bc. Replace the RNPL component using T=sum C0_bc*((1-u_bc)*f_bc+u_bc*sum_m p_bc,m*f_mc). Export T-B and T/B as the incremental replacement; never multiply B by T/R0. This is conditional normalization, not a measured constant-currency company series. Lambda may embed historical FX and hedge economics; its absolute R0 is not established hedge-free revenue.

RNPL timing changes neither demand nor survival. No cancellation multiplier. u is a contributing-revenue exposure share, never unpaid stock or quarterly booking flow. Keep all exposure, including RNPL, in the denominator. p sums to one. In the recognition working hypothesis m is a month within the target recognition quarter. A separate payment/fixing sensitivity may use the preceding month but must not be described as revenue recognized outside the target quarter.

Currency weights: illustrative USD 0.44; EUR 0.32, GBP 0.07, CAD 0.05, AUD 0.04, BRL 0.04, MXN 0.04. Individual shares are assumptions; the aggregate 0.56 is only a FY2025 disclosed non-USD revenue anchor, not measured Q3 cohort exposure. Sensitivity non-USD shares 0.40/0.56/0.70, proportional foreign mix; u 0/0.10/0.20/0.30/1. Timing equal target months, first target month, last target month, and prior-month payment/fixing proxy. No scenario is selected as a forecast.

Use frozen public FRED USD-per-unit rates from fx_lag_v2 (preferred explicit units), inspect the external R bundle but do not deploy its synthetic inputs or aggregate EUR calibration. Fixed reference is each currency's 2025 daily average. Ordinary booking rate is each booking quarter's daily mean. Target monthly rates include known daily rates and then last available spot held flat; compare foreign currency multipliers 0.95/1/1.05 applied only after the actual last quote. Daily time averages are proxies for unavailable transaction weights. Use the actual cache cutoff, never claim live rates. Frozen source availability is 2026-09-11, so the assembled scenario is current-information only.

YoY is separate: growth=(current/prior)-1, level FX effect=F_t-1, and FX growth-gap pp=100*(T_t/T_y-R0_t/R0_y). Dollar bridge on prior ordinary baseline uses 100*(T_t-B_t)/B_y, with prior timing held at ordinary (u_y=0) unless separately supplied; this is a conditional incremental growth bridge, not management constant-currency guidance. Show the denominator and prior assumption.

Hedge policy: no hedge dollars inferred from notional or annual guidance. Core normalized-reference engine supports pre-hedge arithmetic only when basis explicitly certified; reported-kernel example exports an incremental sensitivity and forbids adding new hedge dollars because embedded hedge treatment is unresolved. L4 must reconcile baseline compatibility before adoption.

## Tests fixed now

Conservation, reference-dollar weights versus coefficients counterexample, zero/full RNPL, all USD, all equal FX, equal booking/recognition rates, opposite quote directions, missing positive-exposure rates, zero-weight missing rates, duplicate/mismatched keys, nonfinite/negative data, bad u/p/share bounds, reference mismatch, stale source, future information input, future quote mutation, p outside target quarter, cash-fixing timing label, no demand/cancellation addition, wrong full-factor double-counting counterexample, and distinct YoY/level/dollar units.

## RESUME

Implement only new cohort_fx_v1 code and outputs, then record every command, failures and results in L3_COHORT_FX_RESULTS.md and accounting/source distinctions in a separate new note. Lead owns independent review, integration, frozen score preservation and publication. No registry/scorer or team decision is authorized to this package.
