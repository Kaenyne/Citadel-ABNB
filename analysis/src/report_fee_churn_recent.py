"""Build the follow-up memo from computed aggregates and reviewed public evidence."""
import json
from extend_fee_churn_recent import ROOT, OUT, read
from research_integrity import verify_frozen_report


def main():
    verify_frozen_report(ROOT, 'report_fee_churn_recent.py')
    pooled = read(OUT / "pooled_rates.csv")
    markets = read(OUT / "market_rates.csv")
    winter = read(OUT / "winter_reappearances.csv")
    profiles = read(OUT / "winter_baseline_profiles.csv")
    ledger = json.loads((ROOT / "research/sources/fee_churn_recent.json").read_text(encoding="utf-8"))
    index = json.loads((OUT / "latest_index_check.json").read_text(encoding="utf-8"))
    source_rows = json.loads((OUT / "winter_sources.json").read_text(encoding="utf-8"))
    table = []
    for row in pooled:
        group = [r for r in markets if r["cohort"] == row["cohort"] and r["start_month"] == row["start_month"]]
        n, d = int(row["baseline_ids"]), int(row["missing_ids"])
        if (len(group) != 13 or n <= 0 or
                sum(int(r["baseline_ids"]) for r in group) != n or
                sum(int(r["missing_ids"]) for r in group) != d or
                abs(d/n-float(row["disappearance_rate"])) >= 1e-12):
            raise ValueError('Recent fee report market counts and pooled rates do not reconcile')
        table.append(f"| {row['start_month']} → {row['end_month']} | {'All IDs' if row['cohort']=='all_listings' else 'Reviewed short-stay homes'} | {n:,} | {d:,} | {d/n:.2%} | {row['min_vintage_gap_days']}–{row['max_vintage_gap_days']} |")
    winter_table = []
    for market in ("toronto", "vaud", "new-zealand"):
        row = max((r for r in winter if r["market"] == market and r["cohort"] == "all_listings"), key=lambda r:r["followup_vintage"])
        lost = next(r for r in profiles if r["market"] == market and r["group"] == "missing")
        retained = next(r for r in profiles if r["market"] == market and r["group"] == "retained")
        old_previous = sum(json.loads(r["source_counts"]).get("previous scrape",0) for r in (lost,retained))
        january_previous = next(r for r in source_rows if r["market"]==market)["first_missing_source_counts"].get("previous scrape",0)
        winter_table.append(f"| {market.title()} | {int(row['january_missing']):,} | {int(row['cumulative_reobserved']):,} | {float(row['return_share']):.1%} | {old_previous:,} → {january_previous:,} |")
    recent_return = next(r for r in pooled if r["start_month"]=="2026-06" and r["cohort"]=="all_listings")
    evidence_table = [f"| {r['id']} | {r['date']} | {r['classification'].replace('_',' ')} | {r['claim']} | [Source]({r['url']}) |" for r in ledger["cases"]]
    text = f"""# Airbnb fee response: August observations and winter-spike diagnosis

Prepared September 7, 2026 by Codex for the Citadel-ABNB team. Sources: existing team and Inside Airbnb captures, official fee notices, and reviewed public host accounts.

**Decision:** There is direct evidence that the fee is provoking host responses, including an Airbnb listing steering visitors toward a competing platform and explicit decisions to stop hosting. We have not independently verified a completed delisting caused specifically by 15.5%, or estimated the incremental exit rate attributable to it. The earlier January spike is materially contaminated by changes in capture composition and subsequent reappearances; it should not be used as evidence of a fee-driven exodus.

## Newest measured observations

The same 13 team markets supply June, July and August captures: Austin, Barcelona, Chicago, London, Los Angeles, Mexico City, Nashville, New Orleans, New York City, Paris, Rome, San Diego and Sydney. These are available recent markets, not a probability sample of Airbnb globally. The older broad study still covers 94 balanced quarterly markets; it cannot be presented as an August panel.

| Snapshot interval | Starting cohort | Starting IDs | Missing next vintage | Observed disappearance | Days between vintage start dates |
|---|---|---:|---:|---:|---:|
{chr(10).join(table)}

Reviewed short-stay homes means entire homes with minimum nights below 30 and at least one review in the previous 12 months, evaluated at each baseline. This is an activity screen, not proof of current bookings. All IDs include rooms, hotels, longer-stay and unreviewed inventory. Neither rate is host-level, property-level, or fee-attributable churn.

**The apparent 3.63% → 4.14% increase does not establish acceleration:** intervals between vintage starts lengthen from 22–29 to 29–47 days. Between full-file completion dates they span 9–23 versus 38–50 days. Files are collected over multiple days; neither date is the exact departure date of an absent listing. No monthly normalization or annualization is used. August files completed between August 21 and September 3, so these observations are substantially more recent than January.

Of the {int(recent_return['missing_ids']):,} June IDs missing in July, {int(recent_return['reobserved_next_vintage']):,} ({int(recent_return['reobserved_next_vintage'])/int(recent_return['missing_ids']):.1%}) reappeared in the August vintage. The remainder have not yet had the required 90-day confirmation window. Blank persistence is unknown, not zero. Prior-review-weighted disappearance is 2.40% and 2.76%, respectively; reviews are not revenue or lost bookings.

London is particularly relevant because UK-resident hosts had a June 22 transition. London all-ID disappearance is 4,747/92,638 = 5.12% for June→July and 4,556/91,965 = 4.95% for July→August; reviewed-home rates are 5.63% and 6.38%. June London data straddle June 22. Listing location does not prove host residence or switching date; these are descriptive diagnostics, not treated-versus-control estimates. [Airbnb regional notice](https://www.airbnb.com/resources/hosting-homes/a/simplifying-service-fees-761).

The public archive index was checked again at {index['checked_at_utc']}. Its SHA-256 is unchanged, with {index['indexed_snapshots']} indexed snapshots, July data for 16 markets, August data for NYC only and no September vintages. Team-catalogued August URLs provide the wider recent panel. No unpublished future dates were guessed.

## Why the earlier winter spike occurred

The strongest observed explanation is a change in which listings entered the captures, combined with substantial temporary absence. This is more specific than simply invoking seasonality.

| Market | December IDs missing in January | Reobserved by July, same ID | Share reobserved | Files' previous-scrape rows: December → January |
|---|---:|---:|---:|---:|
{chr(10).join(winter_table)}

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
{chr(10).join(evidence_table)}

## Why the fee can cause a response even when total platform fees are similar

1. **Failure to reprice reduces payout.** At a $100 subtotal, a former 3% host keeps $97; under 15.5% they keep $84.50, down 12.9%. Raising the subtotal to $114.79 preserves $97. With an illustrative old $15 guest fee, the guest previously paid $115, so there need not be a meaningful increase in their total price. Taxes and other charges are excluded from this example.
2. **Other percentage charges can make the economics worse.** A July host specifically cites a landlord taking 25% of the nightly rate. If that share applies to the same gross subtotal before and after the switch, host residual changes from 72% to 59.5% of subtotal. Preserving $72 then requires $121.01, around 5.2% above an illustrative former $115 guest total. This is conditional contract arithmetic, not verification of that host's contract or their claimed 28% increase. Tax treatment can also differ; Airbnb itself discusses VAT/GST and gross-revenue thresholds. A general claim that every host's income tax necessarily rises would be wrong. [Fee mechanics and tax caveats](https://www.airbnb.com/resources/hosting-homes/a/simplifying-service-fees-on-airbnb-771).
3. **Visible commission can change channel choices.** Hosts see a larger deduction and may reassess whether Airbnb earns it, particularly when already dissatisfied with support. Direct-booking and competitor steering can reduce Airbnb's share of a property's bookings while the listing stays live. The case above demonstrates the behavior; it does not quantify the demand shifted.

The timing is staggered. PMS hosts were largely migrated in Q4 2025; Peru/South Korea resident cohorts switched May 25, 2026 and Germany/UK June 22. Remaining hosts have September 15 or October 13 deadlines, depending on residence, with early switching possible. As of September 7, our summer panel cannot measure the aftermath of those remaining deadlines. The official notices describe fee application to **new reservations after switching**, not check-in dates.

**Investment implication:** fee-related frustration and channel steering are observable. A material incremental loss of productive supply or bookings remains unproven. The winter spike is unsuitable evidence for that thesis. The decision-relevant outcomes are both sustained disappearance and Airbnb's booking share at properties that remain listed. Establishing the fee effect requires actual switching dates and matched pre/post booking outcomes, with comparable observation windows and unaffected or not-yet-affected controls; complaints and raw inventory losses cannot substitute for that comparison.

## Reproduce and audit

Run from repository root, after the existing acquisitions:

```powershell
.\\.venv\\Scripts\\python.exe analysis/src/extend_fee_churn_recent.py
.\\.venv\\Scripts\\python.exe analysis/src/report_fee_churn_recent.py
.\\.venv\\Scripts\\python.exe -m unittest discover -s analysis/tests -p 'test_fee_churn*.py'
```

The acquisition index check is preserved in `data/processed/fee_churn_recent/latest_index_check.json`. Source provenance is pinned to the existing team commit `df833f5f3980078beef09c1327940bfa58d57acf`. Every compact used for recent positives is hash checked; winter full raw profiles are also hash checked. Partial captures can refute absence with a positive ID but cannot supply negative observations. The latest complete eligible monthly vintage is selected per team market, including NYC June 14 rather than its partial June 8 capture. Cross-market duplicate baseline IDs are excluded, and any acquired positive in the endpoint vintage's month refutes disappearance conservatively.

Outputs: [market counts](../../data/processed/fee_churn_recent/market_rates.csv), [pooled counts](../../data/processed/fee_churn_recent/pooled_rates.csv), [winter returns](../../data/processed/fee_churn_recent/winter_reappearances.csv), [winter profiles](../../data/processed/fee_churn_recent/winter_baseline_profiles.csv), [public-account ledger](../sources/fee_churn_recent.json), and [figure](../../analysis/figures/fee_churn_recent.png). Aggregate totals reconcile across all 52 market/cohort/interval rows. Fourteen fee-analysis unit tests pass, including unknown follow-up handling and return-count edge cases. No host outreach was performed.
"""
    (ROOT / "research/notes/2026-09-07_fee-churn-recent-followup.md").write_text(text, encoding="utf-8")
    print("Recent fee/churn memo written; 52 market rows reconcile.")


if __name__ == "__main__":
    main()
