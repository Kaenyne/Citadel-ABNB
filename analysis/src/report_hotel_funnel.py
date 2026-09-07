"""Build the 25-market hotel operating audit from audited inputs and aggregates."""
import csv
import json
from pathlib import Path
from audit_hotel_funnel import REVIEW_FIELDS

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data/processed/hotel_funnel_audit'


def read(name):
    with (DATA / (name + '.csv')).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def pct(x):
    return f'{float(x)*100:+.1f}%'


def name(x):
    return x.replace('-', ' ').title()


def require_complete_review_data(rows):
    """This dated narrative assumes complete reviews; never publish it over gaps."""
    for row in rows:
        for key, value in row.items():
            if any(key.endswith(field+'_missing') for field in REVIEW_FIELDS) and int(value) != 0:
                location = row.get('market', 'pooled') + '/' + row.get('scope', '')
                raise ValueError(
                    f'Incomplete review data at {location}: {key}={value}. '
                    'Totals and growth remain unknown in the CSVs; review the gaps '
                    'before regenerating this narrative and chart.')


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    pooled = {r['scope']: r for r in read('archive25/hotel_panel_pooled')}
    old = {r['scope']: r for r in read('hotel_panel_pooled')}
    panel = read('archive25/hotel_listing_panel')
    require_complete_review_data([*pooled.values(), *old.values(), *panel])
    sources = {s['source_id']: s for s in json.loads((ROOT / 'research/sources/hotel_funnel_audit.json').read_text(encoding='utf-8'))}
    review = json.loads((DATA / 'overlap_review_metadata.json').read_text())
    capture_overlap = json.loads((DATA / 'panel_capture_overlap.json').read_text())
    choices = list(csv.DictReader((ROOT / 'analysis/config/hotel_markets_25.csv').open(encoding='utf-8')))
    def cite(s):
        r = sources[s]
        return f"[{r['title']}]({r['url']})"
    s, b = pooled['strict'], pooled['boutique']
    selected = [r for r in panel if r['scope'] == 'strict' and r['pair_eligible'] == 'True']
    def productivity(r):
        return float(r['ltm_reviews_per_listing_endpoint']) / float(r['ltm_reviews_per_listing_baseline']) - 1
    weak = [r for r in selected if productivity(r) < 0]
    dilution = [r for r in weak if float(r['listings_growth']) > 0]
    # Figure: 24 comparable cities, equal category spacing and readable labels.
    figs = ROOT / 'analysis/figures'
    figs.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                        'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(14, 9), gridspec_kw={'width_ratios': [1, 1.25]})
    for i, (key, label, color) in enumerate([
            ('listings_growth', 'Listing stock', '#244b6e'),
            ('number_of_reviews_ltm_growth', 'Trailing-year reviews', '#37a39c')]):
        axes[0].bar([x+i*.32 for x in range(2)], [100*float(pooled[x][key]) for x in ['strict', 'boutique']],
                    width=.30, label=label, color=color)
    axes[0].set_xticks([.16, 1.16], ['Hotel + boutique tags', 'Boutique tag only'])
    axes[0].axhline(0, color='#627482', lw=.8)
    axes[0].set_ylabel('Change between observed snapshots (%)')
    axes[0].set_title('Boutique-tagged supply fell between snapshots', loc='left', fontsize=12)
    axes[0].legend(frameon=False, loc='lower left')
    ordered = sorted(selected, key=productivity)
    changes = [100*productivity(r) for r in ordered]
    axes[1].barh([name(r['market']) for r in ordered], changes,
                 color=['#b36a51' if v < 0 else '#37a39c' for v in changes])
    axes[1].axvline(0, color='#627482', lw=.8)
    axes[1].set_xlabel('Change in trailing-year reviews per listing (%)')
    axes[1].set_title(f'{len(weak)} of 24 markets show lower activity per listing', loc='left', fontsize=12)
    fig.suptitle('Hotel supply is growing; productive conversion is not established', x=.045, ha='left',
                 fontsize=16, fontweight='bold')
    fig.text(.045, .035, 'Defined 25-market sample; 24 comparable pairs, Austin excluded. September 2025 to June 2026 capture starts.\n'
             'Reused Inside Airbnb data; unequal observation dates, no seasonal adjustment. Reviews are not booked nights; tags do not verify independence.',
             fontsize=9, color='#52606b')
    fig.subplots_adjust(left=.07, right=.97, top=.89, bottom=.13, wspace=.55)
    fig.savefig(figs / 'hotel_funnel_audit.png', dpi=170)
    plt.close(fig)
    panel_table = []
    for r in panel:
        if r['scope'] != 'strict':
            continue
        panel_table.append(f"| {name(r['market'])} | {r['baseline_date']} → {r['endpoint_date']} | "
                           f"{int(r['baseline_listings']):,} → {int(r['endpoint_listings']):,} | {pct(r['listings_growth'])} | "
                           f"{pct(r['number_of_reviews_ltm_growth'])} | {pct(productivity(r))} | "
                           f"{'Included' if r['pair_eligible'] == 'True' else 'Excluded: partial scope'} |")
    tam_table = []
    for r in read('hotel_market_capacity_anchors'):
        rooms = f"{float(r['hotel_rooms']):,.0f} rooms" if r['hotel_rooms'] else 'Not identified'
        independent = f"~{float(r['independent_rooms_derived_or_reported']):,.0f} independent rooms" if r['independent_rooms_derived_or_reported'] else 'Not identified'
        if r['market'] == 'milan':
            rooms = '491 hotel establishments; hotel rooms unknown'
        if r['market'] == 'buenos-aires':
            rooms = '307 hotel-category establishments, includes apart hotels'
            independent = '44 boutique hotels; 1,108 average daily available rooms'
        if r['market'] == 'cape-town':
            independent = '89 rooms/suites in 3 named examples; no city census'
        tam_table.append(f"| {name(r['market'])} | {rooms} | {independent} | {r['vintage']} | {r['geography']} | "
                         f"[{r['source_id']}]({sources[r['source_id']]['url']}) |")
    mix_table = [f"| {float(r['starting_hotel_share'])*100:.1f}% | {float(r['ending_hotel_share'])*100:.2f}% | "
                 f"{float(r['combined_growth'])*100:.1f}% | {float(r['growth_uplift_vs_all_nights_at_home_rate'])*100:.1f} pp |"
                 for r in read('hotel_mix_scenarios')]
    supply_table = [f"| {float(r['airbnb_channel_share'])*100:.0f}% | {float(r['nights_per_signed_property_first_year']):,.0f} | "
                    f"{float(r['properties_for_1m_nights']):,.0f} | {float(r['properties_for_target_revenue']):,.0f} |"
                    for r in read('hotel_supply_requirements')]
    add = int(s['new_to_panel_hotel_ids'])
    percentage = lambda numerator, denominator: f'{100*int(s[numerator])/int(s[denominator]):.1f}%'
    memo = f'''# Airbnb hotel acquisition funnel: preliminary supply and activity audit

As of September 7, 2026. Forward window: approximately September 2026–September 2027.

**Scope clarification:** the 25 cities were an analyst-selected extension of the repository's listing-churn panel, not Jessie's separate 13-market study or an agreed 25-country universe. The observed results below are hotel-tagged rows within Inside Airbnb; no physical-hotel match to external reservation records was performed. They cannot establish a demand surge caused by joining Airbnb. Read [the data explanation and corrected demand question](2026-09-07_hotel-demand-data-reset.md) first.

**Decision: measured scaling is possible; productive, profitable hotel acquisition is not yet demonstrated.** The addressable room stock is large enough that global TAM is unlikely to be the immediate constraint. Activation, room allotment, bookings per available room night, cannibalization and incentive costs determine the next year's result. The broader 25-market audit produces substantially weaker review productivity than the earlier 13-market supplement, so the smaller sample should not carry the investment conclusion.

## Scope and evidence boundary

Because the prior list could not be identified, this audit defines an explicit **25-market analytical sample across {len(set(r['country'] for r in choices))} countries**. It retains the original 13 markets, adds disclosed destinations Madrid and Singapore, and adds ten urban/geographic comparisons with existing history: Amsterdam, Berlin, Lisbon, Milan, San Francisco, Tokyo, Bangkok, Cape Town, Buenos Aires and Rio de Janeiro. Selection was fixed before measuring those additions' hotel outcomes. This is a judgment-selected sample, not a random world sample, a recovered prior team list or Airbnb's complete rollout universe. Selection reasons are in [the market configuration](../../analysis/config/hotel_markets_25.csv).

All 25 markets have an evidence row. **24 have comparable listing pairs; Austin's inherited partial-scope flag excludes its growth from the pool.** Rio's room-capacity denominator remains unverified; missing independence data remain missing throughout. The [combined 25-market table](../../data/processed/hotel_funnel_audit/hotel_25_market_audit.csv) joins capacity evidence, vintage, selection reason and listing outcomes without treating listings as physical rooms.

## What the earnings claim establishes

Airbnb says hotel nights are growing approximately three times as fast as home nights while remaining a single-digit share. It reports thousands of hotels in more than 20 destinations. This compares growth rates, not booking volumes. Absolute hotel nights, live rooms, hotel ADR and dedicated hotel commission are not disclosed sufficiently to reconcile an acquisition funnel. Platform Nights and Seats is not a pure lodging denominator. {cite('HOTEL-Q226')}

The reported 35% hotel-to-home return rate tracks first-time hotel guests from **July 2024–June 2025** for 365 days. That cohort predates the May 2026 expansion. It is neither a causal estimate for the new rollout nor a credit redemption rate. Eligible hotel bookings can earn up to 15% credit through December 31, 2026; credits last one year, so January 2027 is not a clean unsubsidized period. {cite('HOTEL-Q226')}

The curated boutique/independent positioning and short-stay use cases are already team evidence. Public data do not establish the new hotel's solo or business-travel mix, or how many guests would otherwise have booked an Airbnb home. {cite('HOTEL-RELEASE')}

## Can growth remain measured for the next 12 months?

Let `s` be hotel share of lodging nights, `gc` home growth and `gh` hotel growth:

`Next hotel share = s × (1 + gh) / [(1 − s) × (1 + gc) + s × (1 + gh)]`.

**Sensitivity, not guidance:** assume home nights grow 10% and hotel nights grow 30% for one year.

| Starting hotel share | Ending hotel share | Combined lodging growth | Uplift vs. all nights growing at home rate |
|---:|---:|---:|---:|
{chr(10).join(mix_table)}

A starting share below **8.59%** stays below 10% under this scenario. At a 5% starting share, hotels rise to **5.86%** and add only **1 percentage point** to combined growth versus a 10% counterfactual. At 9%, they cross 10%. Single-digit share alone therefore does not establish that scaling will remain measured. Management can pace contracting, activation and room allotments; public reporting does not prove those controls are working.

The appropriate supply balance is **booked room nights per time-weighted room night actually offered on Airbnb**. Productivity changes by `(1 + booked-night growth) / (1 + offered-room-night growth) − 1`. Nights growing 30% against offered capacity growing 20% improves productivity **8.3%**; capacity growing 50% reduces it **13.3%**. Signed hotels and endpoint listing counts miss activation timing and how much inventory each hotel allocates.

## Numerical TAM: what is established, and what is not

IHG's 2025 industry overview reports **23.7 million global hotel rooms**, **57% branded**, from STR data. The complement is approximately **10.2 million unbranded rooms** (`23.7m × 43% = 10.191m`). IHG and STR are one underlying industry estimate, not two confirmations. Unbranded is a defensible independent-supply proxy; it does not certify Airbnb-eligible boutique rooms. Independently owned franchises are branded, and soft-brand affiliations complicate the boutique distinction. {cite('HOTEL-IHG25')}

That stock represents **3.72 billion physical room nights annually**. At assumed 60–75% occupancy, it produces **2.23–2.79 billion all-channel occupied nights**. A hypothetical 1% Airbnb share is **22.3–27.9 million nights before** geographic eligibility, quality screening, contracting, activation and timing filters. These are capacity sensitivities, not a bookings or revenue forecast. No global estimate is extrapolated from our 25 cities.

Two historical city sources identify independent rooms: **New York ~38,000**, or 32% of inventory in September 2024; and **Paris ~51,040**, calculated from 55% of roughly 92,800 rooms at year-end 2023. Their approximately **89,040-room subtotal** is historical, rounded and geographically source-defined. It is not a current lower bound. {cite('HOTEL-NYC')}; {cite('HOTEL-PAR')}

Buenos Aires supplies a more precise boutique category: **44 establishments and 34,348 available room nights in March 2026**, equivalent to **1,108 rooms available per day on average**. The source multiplies rooms by days open; 34,348 must not be read as physical rooms, and boutique classification does not verify brand independence or Airbnb eligibility. Cape Town documents **89 rooms/suites across three named examples**; this proves examples exist, not the city TAM. {cite('HOTEL-BUE')}; {cite('HOTEL-CPT')}

| Market | Hotel/lodging capacity anchor | Independent or boutique evidence | Vintage | Source geography | Source |
|---|---|---|---|---|---|
{chr(10).join(tam_table)}

**Do not sum this table into a harmonized TAM or divide Airbnb listing IDs by room counts.** Unknown independent shares are never filled with the global 43%. Chicago and Mexico City are provisional search-index leads; Rio's historical bid returned 404 and its quoted count is excluded. London, Tokyo and Singapore have broader accommodation definitions; Lisbon is metropolitan, New Orleans downtown only, Sydney the local government area. Madrid's **39,656** hotel-category rooms exclude **8,422 hostal rooms** from its 48,078 total. Milan's **74,685** all-accommodation rooms and **57,295 hotel beds** do not identify hotel rooms. Detailed qualifiers are retained in [capacity anchors](../../data/processed/hotel_funnel_audit/hotel_market_capacity_anchors.csv).

The evidence establishes a large global unbranded-room pool, two city independent-room estimates and selected boutique-specific observations. **It does not establish a fully measured, current boutique/independent TAM across all 25 cities.** A defensible complete census requires property IDs, licensed room counts and brand/soft-brand affiliation matched within the same boundary and date; estimates should not conceal that missing join.

## Are additions producing activity?

The primary analysis reuses **50 existing team captures**, two per market, with September 2025 and June 2026 capture starts. Every stored SHA-256 and expected row count reconciled. Completion dates range from {min(r['baseline_date'] for r in selected)}–{max(r['baseline_date'] for r in selected)} at baseline and {min(r['endpoint_date'] for r in selected)}–{max(r['endpoint_date'] for r in selected)} at the endpoint. These unequal intervals are **not annual growth rates or seasonally adjusted comparisons**. The endpoint is only around five to seven weeks after the May 20 rollout; this is mainly evidence about existing hotel-tagged supply, not a clean evaluation of the new product.

![Hotel supply and review activity](../../analysis/figures/hotel_funnel_audit.png)

| 24-market pooled measure | Hotel + boutique tags | Boutique tag only |
|---|---:|---:|
| Listing IDs, starting → ending | {int(s['baseline_listings']):,} → {int(s['endpoint_listings']):,} | {int(b['baseline_listings']):,} → {int(b['endpoint_listings']):,} |
| Listing growth | {pct(s['listings_growth'])} | {pct(b['listings_growth'])} |
| Trailing-year review growth | {pct(s['number_of_reviews_ltm_growth'])} | {pct(b['number_of_reviews_ltm_growth'])} |
| Trailing-year reviews per listing | {pct(s['ltm_reviews_per_listing_growth'])} | {pct(b['ltm_reviews_per_listing_growth'])} |
| Prior-30-day reviews per listing | {pct(s['l30d_reviews_per_listing_growth'])} | {pct(b['l30d_reviews_per_listing_growth'])} |
| Trailing-year reviews, same retained IDs | {pct(s['retained_ltm_reviews_growth'])} | {pct(b['retained_ltm_reviews_growth'])} |
| Prior-30-day reviews, same retained IDs | {pct(s['retained_l30d_reviews_growth'])} | {pct(b['retained_l30d_reviews_growth'])} |

The hotel-tagged pool barely improved annual review activity per listing, while recent activity declined. **{len(weak)} of 24 markets** have lower annual reviews per listing; **{len(dilution)} combine that decline with higher listing stock**. The broader definition that also admits room type "Hotel room" gives **{pct(pooled['broad']['ltm_reviews_per_listing_growth'])}**, similar to the strict pool. It includes serviced apartments/B&Bs and does not solve independence measurement.

Listing flows reconcile exactly: `{int(s['baseline_listings']):,} + {add:,} new-to-panel IDs + {int(s['recategorized_into_hotel']):,} reclassifications in − {int(s['absent_baseline_hotel_ids']):,} absent IDs − {int(s['recategorized_out_of_hotel']):,} reclassifications out = {int(s['endpoint_listings']):,}`. No duplicate hotel IDs occurred across eligible markets at either endpoint. IDs are neither distinct physical hotels nor individual rooms; absence is not confirmed hotel churn.

Of {add:,} newly observed hotel IDs, **{int(s['new_to_panel_number_of_reviews_ltm_positive']):,} ({percentage('new_to_panel_number_of_reviews_ltm_positive', 'new_to_panel_hotel_ids')})** have a trailing-year review, and **{int(s['new_to_panel_number_of_reviews_l30d_positive']):,} ({percentage('new_to_panel_number_of_reviews_l30d_positive', 'new_to_panel_hotel_ids')})** have a prior-30-day review. They account for **{percentage('new_to_panel_number_of_reviews_l30d', 'endpoint_number_of_reviews_l30d')} of endpoint 30-day reviews** and **{percentage('new_to_panel_hotel_ids', 'endpoint_listings')} of listings**. **{int(s['new_ids_first_review_before_baseline']):,} already had first reviews before baseline**, so "newly observed" cannot mean "newly recruited." Only **{int(s['new_to_panel_boutique_tagged']):,} ({percentage('new_to_panel_boutique_tagged', 'new_to_panel_hotel_ids')})** are boutique-tagged.

Some additions clearly have guest activity, but this cannot establish the percentage with bookings, net nights per room or incremental Airbnb demand. Missing reviews do not prove zero bookings. Shorter stays and review propensity can change reviews per night; trailing-year windows overlap and contain pre-observation activity. Retained-ID results also have survivor bias. The **{int(s['retained_negative_review_delta_ids'])} retained IDs with declining lifetime reviews** are flagged instead of silently converting those revisions to negative bookings.

Missing review fields remain unknown: a total, growth rate or reviews-per-listing measure is blank if any required count is missing. Observed subtotals and missing-listing counts are exported separately. These rules also apply to pooled markets and retained IDs. Actual reported zeros remain zero. This dated narrative requires complete review inputs and stops before publishing if that condition changes.

At the endpoint, **{percentage('endpoint_min_nights_le2', 'endpoint_listings')}** have a minimum stay of at most two nights. This supports short-stay availability, not actual solo/business-trip mix. Legacy tags also do not establish coverage of Airbnb's dedicated hotel offering. The boutique-tag contraction is a taxonomy/cohort warning, not a refutation of reported corporate hotel growth.

| Market | Observations completed | Hotel IDs | Supply change | Annual review change | Reviews per listing change | Pool status |
|---|---|---:|---:|---:|---:|---|
{chr(10).join(panel_table)}

The original 13-market panel, extending to late August/early September 2026, remains a **separate sensitivity**: 12 eligible markets, hotel listings **{pct(old['strict']['listings_growth'])}**, annual reviews per listing **{pct(old['strict']['ltm_reviews_per_listing_growth'])}** and boutique listings **{pct(old['boutique']['listings_growth'])}**. Different dates and market composition explain why its stronger aggregate cannot be pooled with, or treated as an acceleration from, the 25-market results. Both views reuse the same source and overlap in captures; neither independently validates 3× booked-night growth.

## What must sign-ups convert into?

`Airbnb nights = signed properties × rooms/property × activation × average fraction of year live × 365 × physical hotel occupancy × Airbnb share of occupied room nights`.

Alternatively use Airbnb-allocated available room nights and occupancy of that allocation. **Do not apply the same inventory restriction twice.** A channel-manager connection supports distribution, but does not establish activation, allocation or conversion rates. {cite('HOTEL-CHANNEL')}

Illustrative assumptions: **50 rooms/property; 80% activation; half-year average live time; 70% all-channel occupancy; $140 ADR; 11% commission**. ADR and commission reuse WS11's estimates solely for comparability; all inputs remain analyst sensitivities.

| Airbnb share of hotel's occupied nights | First-year Airbnb nights per signed property | Sign-ups for 1m nights | Sign-ups for $100m gross hotel revenue |
|---:|---:|---:|---:|
{chr(10).join(supply_table)}

At 10% channel share, **2,000 sign-ups yield about 1.02 million first-year nights and $15.7 million gross hotel revenue**. This is how thousands of additions can coexist with measured financial impact. Reaching $100m under the same inputs requires approximately **12,707 signed properties**, substantially more than a "thousands of hotels" headline by itself demonstrates.

A booking diverted from another OTA or direct can generate Airbnb commission without increasing the operator's total occupancy. Airbnb incrementality instead requires subtracting displaced home contribution, existing hotel baseline business and migrations/relistings; add home cross-sell only above an appropriate counterfactual. **Do not add a second hotel overlay to the team's WS11 model.** Use these equations to test its existing room, night and revenue assumptions.

## Incentives and unit economics

`Credit cost / hotel GBV = eligible GBV share × awarded rate × redemption rate × Airbnb funding share`.

At assumed **11% commission**, **3% variable cost/GBV**, full eligibility/funding and a **15% award redeemed 50%** of the time, contribution is **0.5% of hotel GBV** before fixed acquisition/support costs and incremental home contribution. At full redemption it is **−7.0%**; break-even redemption is **53.3%**. Caps and partial eligibility reduce costs. These are economic sensitivities, not observed take rates, redemption or GAAP margins. The standard host fee page does not establish negotiated dedicated-hotel commission. {cite('HOTEL-FEE')}

Separate issued credits, expected redemption, actual cash/economic cost and accounting recognition. Raw hotel-to-home repeat rates cannot substitute for causal acquisition uplift. Follow credit and repeat-booking cohorts through 2027.

## Four-quarter operating decision rules

| Stage | Required measure | Test for productive, measured scaling |
|---|---|---|
| Eligible → signed | Licensed property IDs, rooms, affiliation, existing Airbnb/HotelTonight relationship | Exclude duplicate room-type listings and migrations from new acquisition |
| Signed → live | Activation within 90 days; days to first bookable inventory; offered room nights | Actual activation/timing supports the model's assumptions |
| Live → booked | Net room nights per time-weighted offered room night; cancellation rate; time to first booking; zero-booking cohort | If nights grow 30%, keep offered capacity growth at or below 30% to preserve aggregate productivity; compare matched cohorts too |
| Booked → retained | 180-day property survival and room allotment | Inventory remains bookable after initial promotional support |
| Booked → profit | Fees less credits, payments, service, CAC and displaced home contribution | Positive incremental contribution and payback under a stated horizon |
| Hotel → home | New guest cohorts, with matched or randomized untreated comparison | Incremental home contribution above the counterfactual |

For STR regulation, match neighborhoods, dates, prices and party sizes of constrained homes to **actually offered hotel inventory**. One hotel room is not one multi-bedroom home. Future regulatory deadlines are not automatically near-term transfers. Reuse the team's event register; this audit adds no unsupported regulatory revenue overlay. This makes hotels a plausible gap-filler while leaving the amount of recoverable demand unproven.

## Overlap controls and reproducibility

The frozen review covers **{review['github_files']} GitHub main files at commit {review['main_commit'][:7]}**, local research and text/tabular ZIP entries: **{review['reviewed_documents']} document instances, {review['unique_content_hashes']} unique hashes, {review['duplicate_content_instances']} duplicate instances**. Normalized URLs screen source reuse; semantic review handles repeated claims under different links. Zero exact matches is not proof that no teammate has encountered a source.

| Prior work | Treatment |
|---|---|
| Jessie/Jessica accommodation-choice study, Hawaii surveys, NTTO and Eurostat | Existing context; no duplicate visitor survey or hotel-versus-STR study |
| Hotel loyalty/news and revenue-model ZIP drops | Copies hashed; repeated documents count once as evidence |
| WS06 hotel-to-home/customer choice work | Existing management and survey claims acknowledged; cohort interpretation is added analysis |
| WS11 hotel revenue scenarios | Existing ADR/take-rate assumptions reused and labeled; no second revenue overlay |
| Theo/team Inside Airbnb captures and churn work | Existing raw files reused; only hotel-specific classification/cohort transformation is new |
| Global/city room evidence and activation/credit calculations | Added sources or analysis, with exact-match screening and measurement gaps preserved |

Across both panels there are **{capture_overlap['capture_references']} capture references but only {capture_overlap['unique_hashes']} unique input hashes**, with **{capture_overlap['shared_between_panels']} captures shared between panels**. No new Inside Airbnb downloads were made. The panels are never added together or called independent corroboration. New city rows similarly remain distinct from the global estimate rather than being added to it.

The review cannot certify private/unshared work or every branch. This is an explicit deduplication boundary, not a promise of zero overlap with everything anyone has found. Reviewable files: [team manifest](../../data/processed/hotel_funnel_audit/team_review_manifest.csv), [source overlap](../../data/processed/hotel_funnel_audit/public_source_overlap.csv), [31-source ledger](../sources/hotel_funnel_audit.json), [unique capture register](../../data/processed/hotel_funnel_audit/unique_reused_captures.csv) and [input assumptions](../../analysis/config/hotel_funnel_audit.json).

Reproduce using the existing local raw captures:

```powershell
.\\.venv\\Scripts\\python.exe analysis/src/audit_hotel_funnel.py --panel archive25
.\\.venv\\Scripts\\python.exe analysis/src/audit_hotel_funnel.py --panel historical13
.\\.venv\\Scripts\\python.exe analysis/src/model_hotel_funnel.py
.\\.venv\\Scripts\\python.exe analysis/src/audit_hotel_overlap.py --sources-only
.\\.venv\\Scripts\\python.exe analysis/src/verify_hotel_capacity.py
.\\.venv\\Scripts\\python.exe analysis/src/report_hotel_funnel.py
.\\.venv\\Scripts\\python.exe -m unittest discover -s analysis/tests -p 'test_hotel*.py' -v
```

`audit_hotel_overlap.py` without the flag refreshes the GitHub/local evidence review. Public spreadsheet/PDF verification files remain under ignored raw storage; CSVs preserve the relevant extracted inputs and source URLs. Tests cover classification, stock-flow reconciliation, revised/missing reviews, exact scope matching, room-night units, invalid rates, zero activation, timing and credit economics. No output claims observed hotel booked nights or a fully verified 25-city boutique census.
'''
    target = ROOT / 'research/notes/2026-09-07_hotel-funnel-audit.md'
    target.write_text(memo, encoding='utf-8')
    print(f'Wrote {target.relative_to(ROOT)}; {len(memo.split()):,} words')


if __name__ == '__main__':
    main()
