# L3 cohort FX/RNPL — accounting, timing and identification

Agent cohort_fx · 2026-09-13 · codex/lane3-full · new cohort_fx_v1 only.

## Verdict

**PARTIAL research; usable conditional arithmetic.** The requested recognition-timed RNPL hypothesis is implemented. Public evidence does not establish that all RNPL revenue FX fixes at recognition or that ordinary bookings fix at booking. Payment delay alone cannot select the revenue FX rate. The inherited reported-USD kernel also lacks a reconciled pre-hedge basis, so the adapter provides a conditional replacement and no new hedge dollars. Investment adoption remains pending.

## Established facts and sources

The FY2025 filing says accommodation service obligations are satisfied at check-in. Guest and host currency choices can differ; payment timing creates currency risk. Confirmed unbilled RNPL bookings are already an FX exposure. Subsidiary income statements use period-average translation rates; monetary remeasurement and historical-rate nonmonetary accounting are distinct. Revenue cash-flow hedges can be reclassified from AOCI into revenue. These policies do not disclose a reservation-level FX fixing rule. The filing reports 56% non-USD revenue for 2025, not a quarterly cohort currency mix. [FY2025 10-K, Note 2 and Item 7A; filed 12 February 2026](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000004/abnb-20251231.htm).

RNPL delays payment and unearned-fee recording and has experienced higher cancellations. The Q2 filing separates payment timing from GBV and revenue and identifies cash-flow-hedge reclassifications. These facts establish neither a surviving RNPL revenue share nor an incremental cancellation hazard. [Q2 2026 10-Q, MD&A and Note 6; filed 6 August 2026](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm).

The local public filing extracts are hashed in `input_manifest.csv`; the 10-K extract includes distributor cover pages, so local extract page numbers differ from the filing's printed pages. The online primary filings were checked directly on 13 September. No Airbnb website, booking page, licensed database, credential or outreach route was used.

## Dates that must remain separate

| Event | Role in this package | Evidence status / what remains missing |
|---|---|---|
| Booking | Cohort indexed by the GBV reporting quarter; inherited two-lag kernel fixes its contribution coefficient | Public aggregate quarter; individual transaction dates absent |
| Guest payment | RNPL can move this after booking; paying does not define recognition in the model | Public mechanism; payment distribution by revenue cohort unavailable |
| Contract currency and FX conversion/fixing | Determines contractual currency and economic exchange-rate exposure | Currency choice/fixing matrix unavailable; not inferred from host destination |
| Check-in | Identifies the accommodation revenue event | Public accounting policy; reservation dates unavailable |
| Revenue recognition/translation | Requested RNPL scenario allocates FX across months inside the revenue quarter | Working hypothesis; does not claim cash and recognition coincide |
| Host payout | Separate settlement exposure; not added to revenue translation | Monetary currency/payment mismatch requires its own reconciliation |
| Hedge settlement/reclassification | Different line and timing; may affect reported revenue | Notional and next-12-month disclosures do not identify quarter hedge dollars |

The recognition scenarios assign all p mass within the fixed target quarter. The prior-month sensitivity is explicitly a **payment/fixing proxy**, not revenue recognized a quarter early. Because the input cohorts are quarterly, even that proxy does not assert reservation-level chronological ordering. Its purpose is to size a different fixing convention. The fixed 2/3 and 1/3 coefficients are never relabeled measured booking-to-stay probabilities.

## Reference basis and replacement identity

Use USD per foreign-currency unit throughout. With reference rate e0_c and booking-period rate e_bc, define f_bc=e_bc/e0_c. Start with the inherited contribution C_bc=lambda*a_b*reported_GBV_b*s_bc, with s an assumed **reported-dollar** currency contribution share. Compute C0_bc=C_bc/f_bc, R0=sum C0_bc and w_bc=C0_bc/R0. The normalization is conditional on currency shares and fixing conventions; it is not a company constant-currency disclosure.

```
B = sum_bc C0_bc * f_bc
T = sum_bc C0_bc * ((1-u_bc)*f_bc + u_bc*sum_m p_bc,m*f_mc)
F_booking = B/R0
F_RNPL = T/R0
incremental replacement dollars = T-B
replacement multiplier on matching reported baseline = T/B
```

Thus B exactly reconstructs the inherited kernel. RNPL remains within R0 and w; it is neither deleted nor added as demand. w sums to one, and each p sums to one. Applying F_RNPL directly to B would translate the ordinary booking component twice. The engine exports that incorrect construction nowhere as an accepted input, and a hand-calculated counterexample tests it.

For any admitted cohort/currency mix, the extension preserves lambda. It does **not** prove historical lambda is invariant to currency, fee or hedge changes. The conditional reference level and total retimed level therefore have weaker interpretation than the mechanical incremental replacement. The public API can accept `certified_prehedge_reference` for future genuinely compatible inputs; this package never asserts that certification for K0.

## Identification and rate conventions

The disclosed quarterly booking flow, unpaid backlog stock, surviving bookings and revenue-producing RNPL cohorts have different denominators. L2's excess-unpaid values and its rejected migration joint solve are not u. No denominator bridge exists here, so u=0/10/20/30/100% are explicit sensitivities, with 100% a boundary stress. RNPL cancellation/survival is held unchanged. Adding an L2 cancellation stress or a nights rebase would require checking overlap separately.

The illustrative seven-currency allocation is USD 44%, EUR 32%, GBP 7%, CAD 5%, AUD 4%, BRL 4%, MXN 4%. Its currency composition and applicability to Q1/Q2 contributors are assumptions. The 40/56/70% non-USD variations keep foreign composition proportional; the annual 56% disclosure is only a convenient scenario anchor. A future measured origin/destination or currency allocation must replace these inputs on the same reported/reference basis.

Frozen FRED rates are normalized by the existing `fx_lag_v2/fetch_fx_v2.py`: EUR, GBP and AUD quotes are direct; CAD, BRL and MXN are inverted **before averaging**. The broad dollar index is excluded. [FRED EUR units](https://fred.stlouisfed.org/series/DEXUSEU) are USD per euro; [FRED MXN units](https://fred.stlouisfed.org/series/DEXMXUS) are pesos per USD and require inversion. All six currencies end on 4 September 2026 in the frozen cache; the directly checked FRED EUR and MXN pages confirm that cutoff. The source vintage is 11 September, and this package's information date is 13 September.

The fixed reference is each currency's 2025 observed daily mean. Booking quarters use their observed daily means. Recognition-month rates combine observed daily quotes with later weekdays at the last cached quote; +/-5% foreign-currency scenarios apply only after the cache cutoff. This includes unobserved dates between the cutoff and 13 September, not secretly refreshed spot. Weighting observed quotes equally and projecting weekdays is a transparent time-average proxy, not transaction weighting. Missing positive-exposure rates fail; a zero exposure needs no rate. The rate builder rejects stale inputs older than 14 calendar days.

No unrelated currency levels are averaged together: each currency's scenario/reference ratio is formed first. Changes in inverse exchange rates are nonlinear; a 5% USD-per-foreign-unit change is not a 5% change in its inverse.

## YoY and hedge limits

`yoy_bridge.csv` compares current and year-ago **model** levels on the common reference basis, with year-ago RNPL u explicitly fixed at zero. It reports reference, ordinary-booking and retimed growth separately. FX growth-gap pp is 100*(T_t/T_y-R0_t/R0_y); timing growth-gap pp is 100*(T_t/T_y-B_t/B_y). Current incremental dollars as pp of prior booking revenue are 100*(T_t-B_t)/B_y. They coincide only where the specified prior timing adjustment is zero. None is management's reported-minus-constant-currency growth disclosure. A level multiplier less one is not a YoY contribution.

The inherited seasonal lambda is fitted to reported revenue, which can include hedge reclassifications. Its embedded hedge dollars cannot be separated using this package. Consequently no hedge amount is added, and `reported_revenue_including_hedges_usd` stays unavailable. The adapter must not be applied to guide+cushion, ADRv3, a baseline with another FX layer, or a different kernel unless L4 first reconciles the matching contribution basis and what is being replaced. A full forecast and guide composition remain L4's work.

## Existing R interface audit

Actual inspected signature: `apply_fx(forecasts, exposure, reference_rates, scenario_rates, parameters, hedges=NULL, prior=NULL)`. It accepts leaf geography/quarter operating rows, separate GBV and revenue currency shares, fixed reference and scenario rates, and aggregate lag0/lag1/lag2. Its timing multiplier is revenue_factor/adr_factor; it does not expose b/c/u/p cohort arrays. Its validator requires `feature_basis=exposure_basket_v1` and rejects aggregate EUR-proxy calibration as a deployable currency-basket coefficient. Examples are explicitly synthetic. The present engine reuses those unit, reference, hedge and replacement principles but does not call that interface as if it implemented RNPL. Five relevant external documentation/code files are hashed; the external bundle is not a runtime dependency and is not copied or staged.

## What remains unavailable

Observed cohort RNPL exposure and survival, transaction-currency splits, fixing dates, recognition-month exposure weights, a certified pre-hedge kernel basis, and historical PIT cohort vintages are absent. No research claim to forecast FX better than a baseline can pass with W1 n=0/W2 n=0. Implementation completeness does not change this.

## RESUME

L4 may carry the API, tests, immutable scenario tables and explicit replacement metadata as research inputs. Before adopting any number, replace assumed currency and u/p allocations with compatible dated evidence or retain their scenario labels, reconcile embedded baseline FX/hedges, and supply the relevant forward GBV inputs. The current real-data illustration intentionally stops at Q3 because both kernel GBV lags are already public; the generic engine accepts later targets without silently creating L4's missing GBV forecast. Do not import L2 unpaid-stock percentages, R synthetic exposures or aggregate EUR slopes as measured cohort inputs.
