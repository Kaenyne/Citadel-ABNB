# Regulation and ABNB: a probability-weighted impact profile

**What this is:** the regulatory research package (`research/regulatory/`, 32 factors, catalyst calendar, illustrative sensitivities) deliberately stops short of probabilities. This note adds them, using the forecast skill's process (gates before merits, outside view, inside view with a same-day recency pass, market cross-reference, scenario tables), and rolls the events into a distribution of incremental net revenue loss with a Monte Carlo in `analysis/src/abnb_regulatory_forecast.py`. Research log for audit: `research/notes/research-log-abnb-regulatory-profile.md`.
**Compiled:** 2026-09-05 (four days before the EU Affordable Housing Act is due to be presented). Author: Krishang, with Claude Code. Outputs: `data/processed/abnb_regulatory_events.csv`, `abnb_regulatory_profile.csv`, `abnb_regulatory_contributions.csv`; figure `analysis/figures/abnb_regulatory_profile.png`.
**Depends on:** `research/regulatory/` (the other session's `krish/regulatory-db` branch) for the factor register; exposure anchors from PR #11 (Inside Airbnb city GBV shares) and PR #14 (Eurostat country shares); valuation translation from PR #13.

---

## 1. Bottom line

| | End-2027 run-rate | End-2030 run-rate |
|---|---|---|
| Incremental net revenue loss, median | 0.45% of revenue | 1.7% |
| Mean | 0.75% | 2.2% |
| 25th to 75th percentile | 0.2% to 0.85% | 0.9% to 3.1% |
| 90th / 95th / 99th percentile | 1.9% / 2.7% / 5.4% | 4.1% / 6.4% / 8.2% |
| P(loss over 1%) / P(over 2%) | 20% / 10% | 71% / 45% |
| Recurring compliance and mitigation cost (EBITDA), median | 0.13% of revenue | 0.16% |
| Total EBITDA hit at 70% contribution margin, median (mean) | $72M ($104M) | $218M ($271M) |
| Value per share at 22x EV/EBITDA, median (mean) | $2.8 ($4.0) | $8.4 ($10.5) |
| One-off cash (Spain fine, Chicago), expected | $50M | $65M |

Against a $182 share price, the median regulatory drag is about 1.5% of value by 2027 and 4.6% by 2030; the 95th percentile is 7% and 16%. Regulation is a valuation haircut and a growth-rate tax on Europe, not an existential risk within the pitch horizon. The distribution is right-skewed and bimodal at 2030: a "local rules keep grinding" mode near 1% and an "EU framework in force" mode near 3%, with 8% of mass past 4%.

Three findings matter for the pitch:

1. **One event carries the tail.** The EU Affordable Housing Act (presentation 9 September, adoption most likely 2028) is 45% likely to be in force with enforcement by 2030 and accounts for 33% of the variance in the 2030 distribution on its own, and 78% together with its binding-caps tail. Everything else in the register sums to a median 1.2% drag by 2030 (95th percentile 2.1%) with the EU act switched off. The prediction card for 9 September: if the proposal excludes primary residences and frames restrictions as proportionate local measures (as the leaked draft does), hold the number; if it contains binding quantitative caps or applies to primary residences, move EU-AHA's 2030 probability to 60% and the tail to 15%.
2. **What is priced already is not this.** The Street's regulatory bear case is NYC-style enforcement in more cities (Morgan Stanley's supply model) and Barcelona 2028; both are in here at 55% and 45% and together contribute a median 0.3%. NYC itself is a small *upside* (20% chance of loosening by 2027). The thing the Street is not pricing is a European framework that lets Paris, Rome, Lisbon and Amsterdam do what Barcelona did, at the same time; that is the mode at 3%.
3. **Management's "80% of top 200 markets already regulated" defence (Q3 2023, Q4 2024 calls) is true and not the point.** Regulation that exists can tighten (Paris three times since 2017, Amsterdam three times, Athens twice in two years), and the base rate for announced European phase-outs surviving in substantially original form four years later is about one in two.

## 2. The events, with probabilities

Probabilities are for the loss-bearing outcome to be *in force* by the horizon. Losses are net of demand recaptured on Airbnb (nearby homes, longer stays, hotels), as a share of global revenue, and incremental to today's run-rate: NYC's 2023 loss and Spain's July 2025 removals are already in reported numbers and are not deducted again. Full text, gates, base rates and anchors per event are in `abnb_regulatory_events.csv`.

| Event | P by end-2027 | P by end-2030 | Net loss if in force (low / mode / high, % revenue) | Expected loss 2030 | What decides it |
|---|---|---|---|---|---|
| EU Affordable Housing Act adopted as an enabling framework and enforced by 3+ large states | 12% | 45% | 0.4 / 1.2 / 3.0 | 0.69% | 9 Sep text; Council position 2027; first national transpositions 2028 |
| EU tail: binding caps, fast enforcement in FR/ES/IT/PT/NL | 2% | 8% | 2.0 / 3.5 / 6.0 | 0.31% | as above; competence objections |
| Spain: further mass removal or platform-verified registry (25k+ ads) | 35% | 55% | 0.10 / 0.20 / 0.45 | 0.16% | replacement law after the May 2026 annulment; EU data-sharing infrastructure |
| Spain regions: Canaries law, Balearics, Malaga, Andalusia | 45% | 65% | 0.05 / 0.15 / 0.35 | 0.15% | municipal implementation 2026 to 2028 |
| Another top-10 US market adopts NYC-style platform verification removing >30% of listings | 30% | 55% | 0.08 / 0.18 / 0.40 | 0.16% | Chicago suit; California SB 346 data sharing; DC bill |
| Paris quota or ban on professional (non-primary) rentals | 30% | 55% | 0.10 / 0.20 / 0.35 | 0.14% | new council's use of Le Meur powers; Council of State record favours the city |
| Italy: art-city caps or zone bans beyond CIN; Florence transition end May 2028 | 30% | 60% | 0.05 / 0.12 / 0.30 | 0.13% | one national measure a year since 2023 |
| Barcelona: 70%+ of 10,101 licences lapse Nov 2028 and enforced | 0% | 45% | 0.15 / 0.22 / 0.35 | 0.11% | May 2027 municipal election; Catalan renewal discretion |
| Barcelona partial (30% to 70%, or grandfathering past 2029) | 0% | ~25% | 0.05 / 0.10 / 0.18 | 0.03% | same |
| Greece: Athens and Thessaloniki freezes extended into 2027, one more area, transfer attrition | 70% | 80% | 0.02 / 0.05 / 0.12 (x1.8 by 2030) | 0.09% | joint ministerial decision before 31 Dec 2026 |
| England registration live and used by councils to cap supply in 2+ areas | 20% | 45% | 0.03 / 0.08 / 0.20 | 0.06% | scheme has slipped three times; not live Jul 2026 |
| Ireland register (Dec 2026) removes >20% of listings within a year | 35% | 55% | 0.04 / 0.07 / 0.15 | 0.05% | launch 0.80 x enforcement 0.45 |
| Paris co-ownership bans and 90-night cap attrition (law in force) | 90% | 95% | 0.01 / 0.03 / 0.06 | 0.05% | already happening |
| Portugal re-tightens nationally or Lisbon converts containment to removals | 20% | 35% | 0.04 / 0.08 / 0.18 | 0.04% | national policy reversed in 2024 |
| Maui Bill 9 West Maui phase-out Jan 2029 with <50% exempt | 0% | 40% | 0.04 / 0.07 / 0.12 | 0.03% | lawsuits (no injunction); rezoning needs 2/3 council |
| Chicago suit ends in injunction or fine >$10M | 40% | 60% | 0.01 / 0.03 / 0.08 (+$20M cash) | 0.02% | motion practice 2027 |
| Amsterdam 15-night cap citywide or national | 30% | 50% | 0.01 / 0.03 / 0.06 | 0.02% | council evaluation 2027 |
| Spain EUR64M fine upheld and paid (cash only) | 55% | 70% | one-off $76M | | merits appeal; CJEU platform-liability precedent |
| NYC loosens LL18 for owner-occupied 1-2 family homes (a gain) | 20% | 35% | -0.25 / -0.12 / -0.05 | -0.05% | Int 879-2026, no hearing yet |
| Recurring compliance and mitigation spend (EBITDA cost) | 90% | 95% | 0.05 / 0.12 / 0.25 | 0.16% | EU data-sharing since May 2026; $50M Spain rural commitment |

Correlation: EU events share a latent "European housing politics" factor (copula rho 0.45); US events a weaker one (0.25). Without the correlation the 2030 90th percentile would be 3.8% instead of 4.2% and the 95th 5.2% instead of 6.4%.

## 3. The forecast, in the skill's format (composite question)

**Question**: Incremental net annual revenue loss to Airbnb from housing-driven short-term-rental regulation, relative to the Q2 2026 run-rate, as a percentage of global revenue, measured (a) at the end-2027 run-rate and (b) at the end-2030 run-rate. Net of recapture on Airbnb; excludes one-off fines and excludes losses already in reported numbers (NYC 2023, Spain 2025).
**Scoring context**: internal pitch use; no tournament; no community prediction visible.
**Forecastability**: Goldilocks for 2027 (mostly dated local processes), pending-decision for 2030 (one discretionary EU act dominates), so the 2030 distribution is deliberately flatter and bimodal.
**Threshold gates**: EU act: presented 9 Sep (0.90), adopted by end-2027 (0.40) or end-2028 (0.75), enabling caps (0.70), enforcement in 3+ states by horizon (0.45 / 0.95). Barcelona: municipal election May 2027 before the Nov 2028 lapse. Maui: 2031 phase is outside the 2030 horizon by construction. Greece: ministerial decision needed before 31 Dec 2026. Ireland: launch 1 Dec 2026 already slipped once.
**Outside view**: EU ordinary legislative procedure median about 18 months (STR data regulation: 17 months). Announced European city-scale STR phase-outs surviving in substantially original form after four years: about one in two (NYC, Amsterdam, Paris enforced; Portugal reversed; Lisbon referendum blocked). One large US city per two years adopts platform-verified registration (NYC 2023, Houston 2026). Registration schemes with planning declarations removed 10% to 20% of supply in year one (Scotland).
**Inside view**: newest load-bearing sources are 4 and 5 September 2026 (Skift, The Local on the EU draft; NYC OSE host count 1 September); the remaining window to the first catalyst is four days, so research is current. The leaked EU draft excludes primary residences and targets commercial multi-property operators in areas failing a price-to-income stress test, which is what a proportionate enabling framework looks like and why the tail is 8% not 25%. Spain's High Court denied the stay but the merits are open and the platform-liability precedent (CJEU C-390/18) favours Airbnb. Maui's rezoning path is closing (Planning Commission denial, February 2026) which raises the phase-out probability, while the lawsuits have produced no injunction. England's scheme is not live after three slipped dates. Athens' 2027 extension is undecided as of mid-August.
**Market cross-reference**: no Polymarket, Kalshi or Metaculus market exists on any of these outcomes (searched 5 September 2026). Adjacent anchors: Airbnb's own disclosure that NYC was about 1% of revenue before LL18 (Q3 2023 letter) and the guidance record (every quarter since NYC enforcement beat its range); the sell-side supply-deceleration model (Morgan Stanley, underweight) is a qualitative anchor without a published probability. Designated anchor: none quantitative; the base-rate estimate stands in.
**Three independent estimates (2030 median)**: base-rate 1.4% (sum of event base rates x package sensitivities); decomposition 1.7% (this model); anchor n/a. Reconciliation: the gap is the EU act's conditional loss, which the base rate does not contain because there is no precedent.
**Causal forces**: for higher loss: coordinated Southern European housing politics (REG-29 to REG-32), EU data-sharing infrastructure lowering enforcement cost, municipal elections in Paris (2026) and Barcelona (2027). For lower: national reversals (Portugal 2024), court annulments (Spain registry 2026, Lisbon referendum), platform-liability law, Airbnb's hotel and nearby-city recapture, and the fact that no city exceeds 2% of revenue.
**Tail risk**: fat-tailed on the EU axis; thin-tailed on the local-rule axis. Pre-mortem: (1) the 9 September text contains binding caps and the act passes in 2027 under housing-emergency politics; (2) Spain enacts a replacement registry with platform verification in 2027 and removes 100k ads; (3) a US federal or state platform-liability ruling (Clark County line of cases cuts the other way) or California SB 346 data sharing turns into LA and San Diego enforcement in 2027. Asymmetry: the pitch pays more for missing a 3% loss than for over-pricing a 1% one, which is why the mean (2.2%) sits above the median (1.7%).
**Scenarios (2030)**: local grind only, 45%, 0.5% to 1.5%; EU framework in force with moderate enforcement, 37%, 2% to 4%; binding caps or coordinated enforcement, 8%, 4% to 8%; regulatory easing (NYC loosening, Portugal-style reversals dominate), 10%, 0% to 0.5%.
**Extreme probability gate**: no event under 2% except the EU tail at 2% for 2027, which is structural (adoption inside 15 months of proposal has no EU precedent for a contested file).
**Distribution**: see section 1; mass below 0%: 5% (2027) and 1% (2030), from NYC loosening; mass above 8%: 1% (2030).
**Sensitivity** (re-run, 100k draws): EU-AHA 2030 probability 45% to 65% with the tail at 15% moves the 2030 median from 1.7% to 2.5% and the 90th percentile from 4.2% to 6.4%; EU conditional loss mode 1.2% to 2.0% moves the mean from 2.2% to 2.5% (median 1.8%); scaling every conditional loss by 1.5x (less recapture) moves the median to 2.6% and the 95th percentile to 9.6%; removing the EU act entirely leaves a median of 1.2% and a 95th percentile of 2.1%; removing the correlation moves the 90th percentile to 3.8%.
**Confidence**: rough on magnitudes (conditional losses are analyst ranges on the package's illustrative sensitivities), better on probabilities for dated processes. The single fact that most changes it: the operative text of the 9 September proposal.
**Key assumptions most likely wrong**: (1) recapture of 35% to 50% on Airbnb; (2) EU share of revenue about 30%; (3) Spain about 6% of revenue; (4) the EU act's enforcement lag of two years after adoption; (5) independence of US events from European politics.
**Monitoring calendar**: 9 Sep 2026 EU proposal text (EU-AHA, EU-TAIL); Oct 2026 NYC registration renewals (NYC); 5 Nov 2026 Q3 call (management language on Spain, hotels recapture); 1 Dec 2026 Ireland register launch (IE-REG); 31 Dec 2026 Greek ministerial decision (GR-FREEZE); Q1 2027 Council/Parliament first readings; Mar 2027 Chicago motion rulings; May 2027 Barcelona election (BCN); mid-2027 Maui court rulings and rezoning vote; end-2027 hazard checkpoint: any event not in force snaps to its 2030-only branch. Re-check monthly until the EU text, then quarterly.

## 4. How to use this in the deck

- One slide: the left panel of `abnb_regulatory_profile.png` with the median and 95th percentile, and the sentence "regulation is a 1% to 2% growth tax on Europe with an 8% tail, not an existential risk". Pair with the Eurostat country chart (PR #14): Spain and Portugal already growing below the EU rate.
- The bear case for the model (PR #13, FY27 revenue +4%) already contains more than the 2027 median regulatory drag; the base case does not need a separate deduction beyond the compliance line.
- Re-run after 9 September with the EU-AHA probabilities updated per section 1; the script takes 30 seconds.

## 5. Caveats

- Conditional loss ranges are analyst judgment scaled from the package's illustrative sensitivities (Barcelona $24M, Maui $18M, 10,000 listings $23M) and exposure anchors; they are not measured city-level revenue.
- Probabilities are single-analyst point estimates with no external market to calibrate against; treat 10-point differences between events as meaningful and 5-point ones as noise.
- Events are not fully mutually exclusive in the real world (an EU framework would be *how* Paris and Italy act); the model treats EU-AHA's loss as incremental to the local events, which double counts at the margin and is one reason the 2030 mean should be read as conservative-high.
- Horizon losses are run-rates, not cumulative; timing within the horizon is not modelled.
