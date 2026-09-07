# Airbnb fee response: August observations and winter-spike diagnosis

Prepared September 7, 2026 by Codex for the Citadel-ABNB team. Sources: existing team and Inside Airbnb captures, official fee notices, and reviewed public host accounts.

**Decision:** There is direct evidence that the fee is provoking host responses, including an Airbnb listing steering visitors toward a competing platform and explicit decisions to stop hosting. We have not independently verified a completed delisting caused specifically by 15.5%, or estimated the incremental exit rate attributable to it. The earlier January spike is materially contaminated by changes in capture composition and subsequent reappearances; it should not be used as evidence of a fee-driven exodus.

## Newest measured observations

The same 13 team markets supply June, July and August captures: Austin, Barcelona, Chicago, London, Los Angeles, Mexico City, Nashville, New Orleans, New York City, Paris, Rome, San Diego and Sydney. These are available recent markets, not a probability sample of Airbnb globally. The older broad study still covers 94 balanced quarterly markets; it cannot be presented as an August panel.

| Snapshot interval | Starting cohort | Starting IDs | Missing next vintage | Observed disappearance | Days between vintage start dates |
|---|---|---:|---:|---:|---:|
| 2026-06 → 2026-07 | All IDs | 399,318 | 14,510 | 3.63% | 22–29 |
| 2026-06 → 2026-07 | Reviewed short-stay homes | 165,877 | 5,515 | 3.32% | 22–29 |
| 2026-07 → 2026-08 | All IDs | 399,285 | 16,534 | 4.14% | 29–47 |
| 2026-07 → 2026-08 | Reviewed short-stay homes | 166,557 | 6,999 | 4.20% | 29–47 |

Reviewed short-stay homes means entire homes with minimum nights below 30 and at least one review in the previous 12 months, evaluated at each baseline. This is an activity screen, not proof of current bookings. All IDs include rooms, hotels, longer-stay and unreviewed inventory. Neither rate is host-level, property-level, or fee-attributable churn.

**The apparent 3.63% → 4.14% increase does not establish acceleration:** intervals between vintage starts lengthen from 22–29 to 29–47 days. Between full-file completion dates they span 9–23 versus 38–50 days. Files are collected over multiple days; neither date is the exact departure date of an absent listing. No monthly normalization or annualization is used. August files completed between August 21 and September 3, so these observations are substantially more recent than January.

Of the 14,510 June IDs missing in July, 2,137 (14.7%) reappeared in the August vintage. The remainder have not yet had the required 90-day confirmation window. Blank persistence is unknown, not zero. Prior-review-weighted disappearance is 2.40% and 2.76%, respectively; reviews are not revenue or lost bookings.

London is particularly relevant because UK-resident hosts had a June 22 transition. London all-ID disappearance is 4,747/92,638 = 5.12% for June→July and 4,556/91,965 = 4.95% for July→August; reviewed-home rates are 5.63% and 6.38%. June London data straddle June 22. Listing location does not prove host residence or switching date; these are descriptive diagnostics, not treated-versus-control estimates. [Airbnb regional notice](https://www.airbnb.com/resources/hosting-homes/a/simplifying-service-fees-761).

The public archive index was checked again at 2026-09-07T22:17:23.275270+00:00. Its SHA-256 is unchanged, with 597 indexed snapshots, July data for 16 markets, August data for NYC only and no September vintages. Team-catalogued August URLs provide the wider recent panel. No unpublished future dates were guessed.

## Why the earlier winter spike occurred

The strongest observed explanation is a change in which listings entered the captures, combined with substantial temporary absence. This is more specific than simply invoking seasonality.

| Market | December IDs missing in January | Reobserved by July, same ID | Share reobserved | Files' previous-scrape rows: December → January |
|---|---:|---:|---:|---:|
| Toronto | 6,840 | 4,762 | 69.6% | 5,662 → 0 |
| Vaud | 1,855 | 1,669 | 90.0% | 1,744 → 0 |
| New-Zealand | 5,296 | 3,428 | 64.7% | 3,004 → 0 |

All three January files contain **zero previous-scrape rows**. Toronto's primary-search inventory barely changes (15,940→15,776), and Vaud's rises (3,775→3,851), while their total inventories fall sharply. Among January-missing IDs, 71.1% in Toronto and 78.7% in Vaud were previously sourced through previous-scrape discovery. In Vaud, 1,648 of 1,855 missing IDs are back in February alone.

Inside Airbnb defines previous-scrape discovery as revisiting a listing seen in an earlier capture and confirming its availability; it does not mean the listing was already inactive. Losing that capture component can generate false apparent exits. The raw counts and later ID returns support a capture-composition explanation; they do not establish whether a particular absence was a collection failure, a temporary pause, or a genuine exit followed by reentry. [Official data dictionary](https://docs.google.com/spreadsheets/d/1iWCNJcSutYqpULSQHlNyGInUvHg2BoUGoNRIGa6Szc4/edit?usp=sharing).

There are also many lower-activity listings in the missing cohorts: 74.7% in Toronto and 78.4% in Vaud had no reviews in the prior year. That makes gross listing counts a weak proxy for economically important lost supply. Median ratings among rated missing versus retained listings are very similar (Toronto 4.88 vs 4.90; Vaud both 4.88; New Zealand both 4.91), so these diagnostics do not establish a low-rating purge.

Airbnb separately disclosed more than 550,000 quality-related removals cumulatively since 2023. This establishes a real alternative source of disappearance but cannot be assigned to January, these cities, or these IDs. Regulation, seasonal pauses, sale and long-term conversion remain possible case-level reasons, not quantified explanations in this analysis. [Q4 2025 shareholder letter](https://s26.q4cdn.com/656283129/files/doc_financials/2025/q4/Airbnb_Q4-2025-Shareholder-Letter-Final.pdf).

The earlier coverage screen only excluded flagged captures and very large count collapses. It did **not** detect this source-composition discontinuity. Its January raw and persistence numbers remain reproducible descriptive outputs, but are not validated estimates of permanent or fee-caused exits. Reappearance after a 90-day confirmation can still occur, as the longer follow-up shows. This note updates the interpretation of the earlier study. All 39 selected recent team captures do retain previous-scrape rows, so this particular zero-component break is absent from the new June–August panel; that does not certify complete coverage.

## Did any hosts actually respond to the fee?

The clearest property-linked case is Airbnb **31054261**, a Carmel Valley treehouse. Its currently accessible description explicitly attributes repricing to the 15.5% fee and directs readers to competitor ID **1646687** for cheaper rates. This verifies published steering behavior, not a completed diverted booking. The Vrbo URL redirects to a regional search page, so current rival bookability is unconfirmed; the date the steering language first appeared is unknown. The Airbnb listing has not vanished. This is precisely the economic risk a delisting-only metric can miss. [Host's Airbnb listing](https://www.airbnb.com/rooms/31054261).

A September 1 Reddit discussion contains four accounts reporting a final stay, closure of one of two listings, or deactivation. These are first-person reports of actions, but none supplies an independently matched property and demonstrated 15.5%-specific cause. Separately, July accounts explicitly link decisions to stop hosting to the fee, but do not establish completed delisting. Search-selected accounts cannot estimate how common these behaviors are. Exact classifications and limitations are in the evidence ledger.

| Case | Date or observation date | Evidence class | What was reported or observed | Link |
|---|---|---|---|---|
| F01 | 2026-09-07 | observable fee linked competitor steering | Carmel Valley treehouse description blames 15.5% fee for repricing and directs guests to a specified competing listing for cheaper rates. | [Source](https://www.airbnb.com/rooms/31054261) |
| F02 | 2026-09-01 | self reported final stay | Reports hosting last Airbnb guest after eight years; cites poor host treatment. | [Source](https://www.reddit.com/r/airbnb_hosts/comments/1w4arg4/comment/p764smc/) |
| F03 | 2026-09-01 | self reported final stay | Reports last Airbnb booking the preceding week and no plan to return; complains of hosts being squeezed. | [Source](https://www.reddit.com/r/airbnb_hosts/comments/1w4arg4/comment/p78ytkw/) |
| F04 | 2026-09-01 | self reported partial exit | Reports pulling and closing the busier of two listings the preceding week after nine years hosting. | [Source](https://www.reddit.com/r/airbnb_hosts/comments/1w4arg4/comment/p76trfr/) |
| F05 | 2026-09-01 | self reported deactivation with planned destination | Reports deactivating one listing about a month earlier because effort was no longer worthwhile; plans Vrbo or midterm rental. | [Source](https://www.reddit.com/r/airbnb_hosts/comments/1w4arg4/comment/p778u6i/) |
| F06 | 2026-07-08 | explicit fee related exit intention | Host objects that a 25% landlord revenue share compounds the required repricing and calls the fee a dealbreaker. | [Source](https://community.withairbnb.com/t5/Help-with-your-business/New-15-5-Host-Service-fee-is-a-dealbreaker-We-re-out/m-p/2270349) |
| F07 | 2026-07-08 | explicit fee related exit decision | A commenter describes a $125 two-bedroom rate, objects to repricing and says the change led them to decide to stop hosting. | [Source](https://www.reddit.com/r/airbnb_hosts/comments/1uqyyqt/airbnb_155_fee_taxesservice_fee_being_shifted/) |
| F08 | 2026-09-01 | building direct channel and planning vrbo | Thread author formerly Airbnb-only, now building own website and adding Vrbo; follow-up says rough website and Stripe account built, integration remains. | [Source](https://www.reddit.com/r/airbnb_hosts/comments/1w4arg4/the_problem_right_now_isnt_switching_fees_to_the/) |
| F09 | 2026-07-09 | stayed switched and repriced | Author reports early switch and later new bookings with the same payout; initial calendar editing lock is temporary. | [Source](https://www.reddit.com/r/airbnb_hosts/comments/1urfruc/i_did_the_155_update/) |
| F10 | 2026-08 | exit decision other reasons | Author decides to remove investment-property listing and seek a long-term tenant, citing guest quality and complaint handling. | [Source](https://www.reddit.com/r/airbnb_hosts/comments/1vl2kje/throwing_in_the_towel_with_airbnb/) |

## Why the fee can cause a response even when total platform fees are similar

1. **Failure to reprice reduces payout.** At a $100 subtotal, a former 3% host keeps $97; under 15.5% they keep $84.50, down 12.9%. Raising the subtotal to $114.79 preserves $97. With an illustrative old $15 guest fee, the guest previously paid $115, so there need not be a meaningful increase in their total price. Taxes and other charges are excluded from this example.
2. **Other percentage charges can make the economics worse.** A July host specifically cites a landlord taking 25% of the nightly rate. If that share applies to the same gross subtotal before and after the switch, host residual changes from 72% to 59.5% of subtotal. Preserving $72 then requires $121.01, around 5.2% above an illustrative former $115 guest total. This is conditional contract arithmetic, not verification of that host's contract or their claimed 28% increase. Tax treatment can also differ; Airbnb itself discusses VAT/GST and gross-revenue thresholds. A general claim that every host's income tax necessarily rises would be wrong. [Fee mechanics and tax caveats](https://www.airbnb.com/resources/hosting-homes/a/simplifying-service-fees-on-airbnb-771).
3. **Visible commission can change channel choices.** Hosts see a larger deduction and may reassess whether Airbnb earns it, particularly when already dissatisfied with support. Direct-booking and competitor steering can reduce Airbnb's share of a property's bookings while the listing stays live. The case above demonstrates the behavior; it does not quantify the demand shifted.

The timing is staggered. PMS hosts were largely migrated in Q4 2025; Peru/South Korea resident cohorts switched May 25, 2026 and Germany/UK June 22. Remaining hosts have September 15 or October 13 deadlines, depending on residence, with early switching possible. As of September 7, our summer panel cannot measure the aftermath of those remaining deadlines. The official notices describe fee application to **new reservations after switching**, not check-in dates.

**Investment implication:** fee-related frustration and channel steering are observable. A material incremental loss of productive supply or bookings remains unproven. The winter spike is unsuitable evidence for that thesis. The decision-relevant outcomes are both sustained disappearance and Airbnb's booking share at properties that remain listed. Establishing the fee effect requires actual switching dates and matched pre/post booking outcomes, with comparable observation windows and unaffected or not-yet-affected controls; complaints and raw inventory losses cannot substitute for that comparison.

## Reproduce and audit

Run from repository root, after the existing acquisitions:

```powershell
.\.venv\Scripts\python.exe analysis/src/extend_fee_churn_recent.py
.\.venv\Scripts\python.exe analysis/src/report_fee_churn_recent.py
.\.venv\Scripts\python.exe -m unittest discover -s analysis/tests -p 'test_fee_churn*.py'
```

The acquisition index check is preserved in `data/processed/fee_churn_recent/latest_index_check.json`. Source provenance is pinned to the existing team commit `df833f5f3980078beef09c1327940bfa58d57acf`. Every compact used for recent positives is hash checked; winter full raw profiles are also hash checked. Partial captures can refute absence with a positive ID but cannot supply negative observations. The latest complete eligible monthly vintage is selected per team market, including NYC June 14 rather than its partial June 8 capture. Cross-market duplicate baseline IDs are excluded, and any acquired positive in the endpoint vintage's month refutes disappearance conservatively.

Outputs: [market counts](../../data/processed/fee_churn_recent/market_rates.csv), [pooled counts](../../data/processed/fee_churn_recent/pooled_rates.csv), [winter returns](../../data/processed/fee_churn_recent/winter_reappearances.csv), [winter profiles](../../data/processed/fee_churn_recent/winter_baseline_profiles.csv), [public-account ledger](../sources/fee_churn_recent.json), and [figure](../../analysis/figures/fee_churn_recent.png). Aggregate totals reconcile across all 52 market/cohort/interval rows. Fourteen fee-analysis unit tests pass, including unknown follow-up handling and return-count edge cases. No host outreach was performed.
