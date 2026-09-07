





# Airbnb: housing-driven short-term rental regulation

**Research cutoff: 5 September 2026. Main period: 2023-2026, with earlier enactment dates where needed.**

This research package covers restrictions and political pressure arising from housing displacement, gentrification, neighbourhood nuisance and overtourism. New York, Spain, Portugal and Greece receive particular attention. It is a curated international research universe, not an exhaustive inventory of every local Airbnb rule. Generic tax, privacy, antitrust, safety and consumer rules are excluded unless closely connected to the housing/overtourism response; the Greek standards and Spanish consumer-enforcement cases are explicit boundary cases.

The investment question is **how much economically productive, legally bookable supply Airbnb can lose, and how much demand it can retain elsewhere on its platform**. Public anger is a leading indicator. Enforceable restrictions on transactions, existing units and licence replacement are the more direct transmission mechanisms.

## Use the package

- [Quantitative follow-up](quantification/README.md): listing counts, affected cohorts, observed supply changes, guidance comparisons and editable revenue/EBITDA sensitivities. Includes updated Spain bond, Lisbon cancellation and BC supply evidence.
- [Full factor register](factor_register.md): 32 factors, ranked within four tiers, with rules, dates, observed evidence, Airbnb implications, limitations and next catalysts.
- [Earnings digest](earnings_digest.md): nine regulatory observations and an index of 14 quarterly transcripts.
- [Source index](source_index.md): 48 source records, including official laws, court decisions, government guidance, news and company material. Quantitative source URLs also appear in the follow-up datasets and workbook.
- [SQLite database](../../data/processed/abnb_regulatory.sqlite): relational tables plus full-text search. It contains derived research and transcript metadata, not the full licensed texts.
- [Editable factor data](factors.json), [sources](sources.json), [earnings observations](earnings_observations.json) and [transcript manifest](transcript_manifest.json).

## Findings for the pitch

**1. New York proves that platform verification can sharply constrain a market; it does not establish an existential global loss.** Airbnb disclosed that the city represented approximately 1% of global revenue before September 2023 enforcement. This is the best company-sourced exposure anchor found here, but is neither current NYC exposure nor a measured consolidated loss. Compliant hosted stays remain possible, and Airbnb can retain some demand through nearby homes, longer stays and hotels. OSE's current release reports over 3,500 approved active hosts, so describing the legal rule as a total prohibition would be inaccurate. [Airbnb Q3 2023 shareholder letter](https://www.sec.gov/Archives/edgar/data/1559720/000119312523268164/d481318dex991.htm), [NYC registration update](https://www.nyc.gov/site/specialenforcement/news/new-yorkers-registered-to-host-surpassed-3500-for-first-time.page).

**2. Spain combines direct enforcement with legal reversals.** Consumer enforcement led to reported removals and a EUR64,055,311 fine. After denial of a payment stay in March 2026, Airbnb obtained a EUR70m surety bond in May to suspend enforcement pending resolution, according to its latest quarterly filing. The potential loss remains neither probable nor estimable in the filing. Separately, the Supreme Court annulled material parts of the national single-registration procedure in May 2026. These are different cases. [Q2 2026 filing](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm), [published Supreme Court judgment](https://www.boe.es/buscar/doc.php?id=BOE-A-2026-12300).

**3. The most immediate broad catalyst is a proposal, not an enacted European ban.** Reuters reported on 4 September that the Commission plans to present the Affordable Housing Act on 9 September. The reported framework addresses how authorities identify housing stress and justify proportionate restrictions. Its breadth makes it particularly relevant to Airbnb's geographic-diversification defence, but legislative negotiation remains ahead. The separate EU data-sharing regulation already applies. [Reuters draft report](https://www.marketscreener.com/news/proposed-eu-rules-would-curb-airbnb-short-term-rental-homes-draft-shows-ce785bdbd98cf526), [Commission implementation notice](https://single-market-economy.ec.europa.eu/news/new-rules-bring-increased-transparency-short-term-rentals-sector-2026-05-20_en).

**4. Portugal is a useful counterexample to one-directional tightening.** National policy partly reversed in 2024, while Lisbon's final December 2025 containment regulation preserves meaningful local constraints. The proposed blanket-cancellation referendum was blocked by the Constitutional Court. A Portugal-wide ban assumption would therefore misstate both the political path and current local variation. [2024 decree](https://info.portaldasfinancas.gov.pt/pt/atualidades/legislativa/Paginas/Decreto_Lei_76_2024.aspx), [Lisbon final regulation](https://diariodarepublica.pt/dr/detalhe/aviso/29926-a-2025-964380181), [referendum decision](https://www.tribunalconstitucional.pt/tc/acordaos/20250001.html).

**5. Greece shows that a freeze can gradually affect existing supply.** Central Athens' registration restriction continues through 2026 and now also applies to part of Thessaloniki. The government's current guidance states that covered properties transferred during life are removed from the registry and cannot re-register while the restriction lasts. That creates an attrition channel beyond simply stopping first-time hosts. [Government housing portal](https://stegasi.gov.gr/programs/prosorinoi-periorismoi-stis-vrachychronies-misthoseis/).

**6. Future phase-outs should be modeled on their actual timelines.** Barcelona's intended licence non-renewal is a 2028 event. Maui's signed law phases out covered apartment-zone use in 2029 in West Maui and 2031 elsewhere, with potential hotel rezoning reducing the net affected stock. Both deserve attention, but neither should be presented as all affected inventory already having disappeared. [Barcelona tourism measure](https://ajuntament.barcelona.cat/turisme/sites/default/files/2025-08/Gestio_turi%C3%BCstica_llarg_CAT-en-GB-WEB_compressed.pdf), [Maui passage](https://mauicounty.us/press-release/final-reading-brings-approval-to-bill-9/), [Maui signing and rezoning position](https://www.mauicounty.gov/m/newsflash/home/detail/18061).

## Priority map

Tier takes precedence over priority: a highly material uncertain proposal remains in Tier 3. Within each tier, priority is qualitative analyst judgment using direct evidence, geographic reach, severity, timing and relevance to the user's focus markets. It is not a predicted stock-price response.

| Tier | Meaning | Lead items | How to use |
|---|---|---|---|
| 1 | Implemented restrictions/enforcement, including later reversals | NYC; Spain enforcement and registry reversal; Athens; Lisbon; Paris; BC | Establish operative mechanisms and observed effects. Only some have quantified company/market evidence. |
| 2 | Adopted policy or scheduled future implementation | Barcelona; Maui; Ireland | Build dated scenarios; identify implementation and litigation dependencies. |
| 3 | Draft, uncertain or legally blocked initiative | EU Affordable Housing Act; further Paris curbs; England registration; Lisbon referendum | Monitor catalyst and legal probability; do not book the loss as certain. |
| 4 | Activism/social pressure | Spain coordinated protests; Canary Islands; Portugal; Greece | Track conversion into a specific bill, vote or enforcement decision. |

Tier 1 does **not** mean a measured Airbnb revenue decline exists for every row. Most official sources establish legal/compliance exposure, while company-level geographic impacts remain undisclosed. The `observed_evidence` and `limitations` fields make this distinction explicit. A rule historically implemented and subsequently reversed remains in Tier 1 so the historical event is not lost; its current status is prominent.

## What management says, and what it leaves unanswered

The call record moves from emphasising workable rules and New York as an outlier, to explicitly using hotels to fill gaps in supply-constrained destinations. In Q3 2025 Chesky named Madrid and New York as regulation-constrained hotel-pilot markets. Q1 2026 repeated the rationale. Q2 2026 framed policy as a continuing risk to manage. See the [earnings digest](earnings_digest.md) for speakers, dates and page/text locators.

These statements support plausible mitigation, not immunity. The fact that a city has rules already does not prevent tighter night caps or licence limits later. Successful event partnerships can coexist with permanent restrictions. Hotel recapture may retain bookings but change fees, acquisition spending, accommodation mix and contribution margins. Those are analytical implications, not disclosed city-level forecasts.

The reviewed passages do not provide a usable current revenue share for Spain, Portugal, Greece or Barcelona, nor a quantified net revenue loss from the specific restrictions. The database leaves unknown exposure as null rather than zero. The Q4 2025 call had no matches for the focused regulation/Spain/Barcelona screen; legal developments should therefore be sourced from filings and authorities rather than attributed to that call.

Useful management questions for the pitch discussion:

1. What share of booked nights and revenue comes from properties subject to primary-residence rules, restrictive night caps or expiring licences?
2. Of removed listings, how many were active, unique properties generating bookings, and how much demand rebooked on Airbnb?
3. In New York and Madrid, what are hotel booking recapture, net revenue and contribution margin relative to displaced home bookings?
4. How much growth in Spain/Italy depends on constrained urban destinations versus unconstrained rural or other markets?
5. What is the status of Spain's fine appeal, cash payment and compliance response after the registry rulings?
6. What incremental compliance cost and restriction risk does management expect from the EU initiative?

## Translating the research into financial scenarios

Use a mutually exclusive geography/property cohort, not one revenue haircut per headline. For cohort i:

`Gross revenue at risk = baseline destination revenue_i × share attributable to affected property/nights × effective enforcement fraction`

`Net revenue loss = gross revenue at risk × (1 − revenue recapture fraction on Airbnb)`

The revenue recapture fraction should reflect the revenue actually earned on substitute bookings, not simply the count of rebooked trips. Destination ADR and take rate can differ from a global average. For new-entry freezes, estimate the forgone supply/booked-night growth against a counterfactual; do not remove the whole incumbent base. For night caps, identify hosts who would exceed the new cap and the nights that would actually book. For licence phase-outs, reflect grandfathering, timing and legal stays.

The following is **illustrative sensitivity only**, not estimated exposure, probabilities, guidance or a price target. The rounded FY2025 revenue base is $12.2bn. [FY2025 shareholder letter](https://www.sec.gov/Archives/edgar/data/1559720/000119312526048670/d58192dex991.htm).

| Illustrative case                | Revenue in affected cohorts | Gross loss within those cohorts | Revenue recaptured | Net consolidated revenue loss | Dollars on $12.2bn base |
| -------------------------------- | --------------------------: | ------------------------------: | -----------------: | ----------------------------: | ----------------------: |
| Limited local shock              |                          2% |                             20% |                50% |                         0.20% |                  $24.4m |
| Several overlapping destinations |                          5% |                             40% |                35% |                         1.30% |                 $158.6m |
| Broad restrictive scenario       |                         10% |                             60% |                20% |                         4.80% |                 $585.6m |

Then apply an explicitly chosen incremental contribution margin to the net revenue change, add recurring legal/compliance spending, and keep fines separate as potentially non-recurring cash/legal items. Do not assume Airbnb's consolidated adjusted EBITDA margin equals the incremental margin on lost bookings. A valuation impact additionally requires persistence, discount rate/multiple, tax and share-count assumptions; none is fabricated here.

Avoid these errors:

- Adding city, national registry and EU enforcement effects on the same property.
- Treating an ad count, registration, licence, bed or host as one equivalent unit of bookable supply.
- Treating all delisted ads as active listings that generated revenue, or assuming all removed supply returns to resident housing.
- Converting a 120-to-90-day cap into a 25% city revenue decline, or 30-to-15 into a 50% decline.
- Treating observed rent increases/decreases after regulation as causal proof of success/failure. Tourism, housing construction, interest rates and income also change.
- Treating rural second homes, occasional home sharing, professional urban flats and hotels as identically exposed.
- Attributing a stock move to regulation without an event study controlling for earnings, markets and other news.

## Catalyst calendar

| Date/window | Factor | What would change the assessment |
|---|---|---|
| 9 September 2026, expected | REG-25 | Actual EU proposal text, covered operators and proportionality protections; reported date can change. |
| October 2026, expected | REG-01 | NYC renewals and enforcement evidence. |
| December 2026 | REG-24 | Ireland launch and legal/planning implementation. |
| End-2026 | REG-04/05 | Greek freeze extensions or expiry. |
| Ongoing | REG-02/03 | Spain fine appeal and post-annulment national framework. |
| 2028 | REG-14/22 | Florence transition end and Barcelona non-renewal implementation. |
| 2029 / 2031 | REG-23 | Maui phase-out, net of final rezoning and court outcomes. |

## Refinitiv access and archive audit

The project has `LSEG_APP_KEY` and `REFINITIV_APP_KEY` in the environment. The local desktop proxy reported ready on port 9000. An authenticated Eikon Data API query succeeded after running outside the network sandbox. No credential values were printed or stored in these artifacts.

Retrieval requested 1 January 2023 through 5 September 2026:

- `Source:TRANS AND R:ABNB.O` returned six records: five quarterly calls from Q2 2025 through Q2 2026, plus a September 2025 conference.
- `R:ABNB.O AND (regulation OR rental OR housing OR tourism) AND Language:LEN` returned 59 headline records. This includes duplicates, press releases and irrelevant matches; it is a discovery feed, not 59 distinct regulatory events.
- Retrieved all six transcript story bodies. They contain LSEG EventsViewer links, **not full transcript text**.
- Retrieved 11 selected regulatory-news story bodies, including the September 4 EU draft report and Spain's May court ruling. These include updated versions of stories and are not 11 independent factors.
- Downloaded 13 full company-hosted corrected PDF transcripts, Q1 2023-Q1 2026. The Q2 2026 company-CDN candidate returned 404; the full public Motley Fool HTML transcript was saved as a labelled fallback. Thus the complete working archive has 14 quarterly calls, with provider provenance preserved.

The API results do not cover the full requested history: the oldest returned news was June 2025 and oldest transcript August 2025. This may reflect news-history limits, available indexing and/or entitlements; the response alone does not prove which. Older news and legal history were researched on the public web. Full LSEG transcript-document download via its EventsViewer remains unverified; the successfully downloaded public alternatives supply the needed call text.

Raw archive: `data/raw/regulatory/` (already excluded from git by repository policy). `lseg/` contains query results and licensed story bodies; `transcripts/` contains PDF/HTML text and hashes; `documents/` contains four successfully downloaded official supporting pages. SEC page downloads returned HTTP errors, so the SEC sources are linked and were checked through web retrieval rather than claimed as local downloads. Do not commit or publicly redistribute the raw licensed exports. No files have been uploaded or sent to anyone.

Rebuild derived outputs:

```powershell
.venv/Scripts/python.exe analysis/src/build_regulatory_database.py
```

Refresh acquisition (requires a running, authenticated desktop for LSEG and network access):

```powershell
.venv/Scripts/python.exe -u analysis/src/pull_regulatory_documents.py
.venv/Scripts/python.exe -u analysis/src/download_abnb_transcripts.py
.venv/Scripts/python.exe -u analysis/src/complete_regulatory_archive.py
.venv/Scripts/python.exe analysis/src/build_regulatory_database.py
```

The acquisition scripts are a reproducible dated snapshot, not an unattended monitoring service. Review legal status manually when refreshing; retrieval timestamps do not establish that an older rule remains unchanged.

Example SQL:

```sql
SELECT id, jurisdiction, title, status, next_catalyst
FROM factors ORDER BY tier, priority;

SELECT f.id, f.title, f.status
FROM factors f JOIN factor_search q ON q.id = f.id
WHERE factor_search MATCH 'housing AND Spain'
ORDER BY f.tier, f.priority;

SELECT f.id, s.title, s.url
FROM factors f
JOIN factor_sources fs ON fs.factor_id = f.id
JOIN sources s ON s.id = fs.source_id
WHERE f.id = 'REG-02';
```

## Coverage limits and next research layer

This first database prioritises the named markets and major international analogues: France, the Netherlands, Italy, Hungary, British Columbia, Montreal, Scotland, England, Ireland and Maui. It does not yet catalogue every rule in Latin America, Asia-Pacific or US municipalities. The LSEG feed also surfaced Ocean Springs litigation and Indonesian restrictions; their current status and housing-specific relevance need verification before inclusion as factors. They are leads, not assumed operative restrictions in the model.

Most remaining investment work is measurement: match legally affected addresses to active listings and paid nights, deduplicate multi-platform supply, identify compliance status, and measure Airbnb recapture. Inside Airbnb/AirDNA and local registries could support that work, but availability calendars are not bookings and scraped inventory is not audited Airbnb revenue. This package supplies the legal/event inventory and management evidence needed to design that analysis.
