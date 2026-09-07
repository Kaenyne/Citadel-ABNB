"""Render the executed broad churn results and an audit-friendly research figure."""
from collections import defaultdict
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/"data/processed"


def read(path):
    with path.open(encoding="utf-8",newline="") as h: return list(csv.DictReader(h))


def n(value): return f"{int(value):,}"
def pct(value): return f"{float(value):.2%}" if value not in (None,"") else "Not identified"
def title(value): return value.replace("-"," ").title().replace("Nyc","NYC")


def pick(rows,cohort="all_listings",policy="coverage_screen",statistic="id_attrition",scope="all_eligible_markets"):
    found=[r for r in rows if r["cohort"]==cohort and r["policy"]==policy and r["statistic"]==statistic and r["scope"]==scope]
    if len(found)!=1: raise ValueError("Missing or duplicate report statistic")
    return found[0]


def figure(market_rows,pools,path):
    all_rows=[r for r in market_rows if r["cohort"]=="all_listings" and r["policy"]=="coverage_screen" and r["pair_eligible"]=="True"]
    home={r["market"]:r for r in market_rows if r["cohort"]=="reviewed_str_homes" and r["policy"]=="coverage_screen" and r["pair_eligible"]=="True"}
    largest=sorted(all_rows,key=lambda r:int(r["baseline_ids"]),reverse=True)[:15]
    regions=[r for r in pools if r["cohort"]=="all_listings" and r["policy"]=="coverage_screen" and r["statistic"]=="id_attrition" and r["scope"]!="all_eligible_markets"]
    regions.sort(key=lambda r:float(r["listing_weighted_rate"]),reverse=True)
    fig,(ax1,ax2)=plt.subplots(1,2,figsize=(13,8),gridspec_kw={"width_ratios":[.95,1.3]})
    fig.patch.set_facecolor("white")
    for ax in (ax1,ax2):
        ax.spines[["top","right","left"]].set_visible(False)
        ax.xaxis.set_major_formatter(PercentFormatter(1,decimals=0))
        ax.grid(axis="x",color="#e8edf1",zorder=0)
        ax.tick_params(axis="y",length=0)
        ax.set_xlabel("Starting IDs missing in June",labelpad=12)
    y=list(range(len(regions)))
    ax1.barh(y,[float(r["listing_weighted_rate"]) for r in regions],height=.5,color="#193c5b",zorder=3)
    ax1.set_yticks(y,[r["scope"] for r in regions]);ax1.invert_yaxis()
    for i,r in enumerate(regions):
        ax1.text(float(r["listing_weighted_rate"])+.008,i,pct(r["listing_weighted_rate"]),va="center",fontsize=10)
        ax1.text(.005,i+.35,f"{r['markets']} {'market' if r['markets']=='1' else 'markets'}; {n(r['baseline_ids'])} starting IDs",fontsize=8,color="#596775")
    ax1.set_xlim(0,max(float(r["listing_weighted_rate"]) for r in regions)+.11)
    ax1.set_ylim(len(regions)-.4,-.7)
    ax1.set_title("Sampled markets by region\nWeighted by starting listing count",loc="left",fontsize=12,pad=18)
    y=list(range(len(largest)))
    ax2.scatter([float(r["id_attrition"]) for r in largest],y,s=48,color="#193c5b",label="All observed listings",zorder=4)
    ax2.scatter([float(home[r["market"]]["id_attrition"]) for r in largest],y,s=40,color="#d17134",marker="D",label="Reviewed short-stay entire homes",zorder=4)
    ax2.set_yticks(y,[title(r["market"]) for r in largest]);ax2.invert_yaxis()
    ax2.set_xlim(0,max(max(float(r["id_attrition"]),float(home[r["market"]]["id_attrition"])) for r in largest)+.025)
    ax2.set_title("15 largest included markets\nA different mix of listings gives a different rate",loc="left",fontsize=12,pad=18)
    ax2.legend(loc="lower right",bbox_to_anchor=(1,-.2),frameon=False,fontsize=8)
    fig.suptitle("Airbnb listing-ID disappearance across the public market panel",x=.05,ha="left",fontsize=17,fontweight="bold")
    fig.text(.05,.915,"September 2025 to June 2026 snapshots. Each market uses its actual collection dates.",fontsize=10,color="#596775")
    fig.text(.05,.025,"Source: Inside Airbnb; Citadel-ABNB calculations. Coverage and geographic exclusions applied.\nThese are observed ID exits over about nine months, not annual permanent-property churn or an Airbnb-wide estimate.",fontsize=9,color="#596775")
    fig.subplots_adjust(left=.14,right=.96,top=.81,bottom=.17,wspace=.63)
    path.parent.mkdir(parents=True,exist_ok=True);fig.savefig(path,dpi=170,facecolor="white");plt.close(fig)


def main():
    broad=DATA/"listing_churn_archive";team=DATA/"listing_churn_panel"
    markets=read(broad/"market_rates.csv");pools=read(broad/"pooled_rates.csv")
    meta=json.loads((broad/"execution_metadata.json").read_text(encoding="utf-8"))
    coverage=read(broad/"market_coverage.csv");qa=read(broad/"snapshot_quality.csv")
    team_pools=read(team/"pooled_rates.csv");team_markets=read(team/"market_rates.csv")
    raw=pick(pools);homes=pick(pools,cohort="reviewed_str_homes")
    primary=pick(pools,statistic="persistent_90")
    conservative=pick(pools,statistic="persistent_90",policy="exclude_march_negatives")
    team_raw=pick(team_pools,policy="team_flags")
    team_primary=pick(team_pools,policy="team_flags",statistic="persistent_90")
    team_conservative=pick(team_pools,policy="exclude_feb_may_negatives",statistic="persistent_90")
    eligible=[r for r in markets if r["cohort"]=="all_listings" and r["policy"]=="coverage_screen" and r["pair_eligible"]=="True"]
    conservative_rows={r["market"]:r for r in markets if r["cohort"]=="all_listings" and r["policy"]=="exclude_march_negatives" and r["persistence_eligible"]=="True"}
    common=[r for r in eligible if r["persistence_eligible"]=="True" and r["market"] in conservative_rows]
    common_n=sum(int(r["baseline_ids"]) for r in common)
    common_primary=sum(int(r["persistent_90"]) for r in common)
    common_conservative=sum(int(conservative_rows[r["market"]]["persistent_90"]) for r in common)
    aliases=sum(int(r["alternative_id_candidates"]) for r in eligible)
    review_share=sum(float(r["missing_baseline_reviews"]) for r in eligible)/sum(float(r["baseline_review_total"]) for r in eligible)
    alias_markets=sum(int(r["alternative_id_candidates"])>0 for r in eligible)
    elsewhere=sum(int(r["same_id_observed_elsewhere_at_endpoint"]) for r in eligible)
    country_groups=defaultdict(list)
    for r in eligible:country_groups[r["country"]].append(r)
    country_rows=[]
    for country,rs in sorted(country_groups.items()):
        denominator=sum(int(r["baseline_ids"]) for r in rs);exits=sum(int(r["missing_ids"]) for r in rs)
        country_rows.append(dict(country=country,markets=len(rs),baseline_ids=denominator,missing_ids=exits,id_attrition=exits/denominator))
    with (broad/"country_rates.csv").open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=list(country_rows[0]));w.writeheader();w.writerows(country_rows)
    figpath=ROOT/"analysis/figures/listing_churn_broad_panel.png"
    figure(markets,pools,figpath)
    lines=["# Airbnb listing churn: broad panel execution", "", "Prepared 2026-09-07. This report supersedes the two-market pilot as the headline churn analysis.", "",
        f"**{n(raw['event_ids'])} of {n(raw['baseline_ids'])} starting listing IDs were absent at the June 2026 observations: {pct(raw['listing_weighted_rate'])}.** The measured panel includes **{raw['markets']} markets across {raw['countries']} country labels**, using September 2025 baselines. Actual observation intervals are **{raw['min_interval_days']}–{raw['max_interval_days']} days**. This is an observed listing-ID disappearance rate over about nine months. It is not an annualized or Airbnb-wide permanent-property churn estimate.", "",
        f"For the baseline subset of entire homes with minimum stay below 30 nights and at least one review in the prior year, disappearance is **{pct(homes['listing_weighted_rate'])}** ({n(homes['event_ids'])}/{n(homes['baseline_ids'])}). This subset is a proxy for commercially used short-stay inventory; the reviews do not verify current bookings or revenue.", "",
        f"The disappearing IDs account for **{pct(review_share)} of the cohort's prior-year reviews**, versus {pct(raw['listing_weighted_rate'])} of its IDs. Exiting listings therefore had less historical review activity on average. Reviews are not revenue or booked nights, so this is not an estimated revenue loss.", "",
        f"Repeated absence for at least 90 days is **{pct(common_conservative/common_n)}–{pct(common_primary/common_n)} on the same {len(common)}-market denominator of {n(common_n)} IDs**, depending on whether March 2026 can supply negative evidence. This is coverage sensitivity, not a confidence interval. All positive observations remain valid in both methods.", "",
        "![Regional and market disappearance rates](../../analysis/figures/listing_churn_broad_panel.png)", "",
        "## What was executed", "",
        f"1. Reacquired and verified all **132 historical listing snapshots across the team's 13 markets**, using immutable source commit [`df833f5`](https://github.com/Kaenyne/Citadel-ABNB/tree/df833f5f3980078beef09c1327940bfa58d57acf). All 132 row counts match the team's catalog.",
        f"2. Located the public archive metadata linked to [Inside Airbnb's data page](https://insideairbnb.com/get-the-data/). Selected the last indexed September, December, March and June observations, requiring both September 2025 and June 2026. The index has {meta['source']['catalogued_markets']} markets; {meta['source']['eligible_markets']} have these endpoints. No dates or markets were selected to produce a desired churn rate.",
        f"3. Acquired **{meta['successful_snapshots']} broad-panel files**. {sum(r['team_historical_count_verified']=='True' for r in qa)} match a historical team count; {sum(r['team_current_hash_verified']=='True' for r in qa)} match both the team's current-file count and SHA-256. Other files are newly acquired public history, with structural validation and stored hashes, rather than previously held team history.",
        "4. Applied the inherited partial-coverage flags and a large-count-break diagnostic: a file below half the largest selected count for its market cannot supply negative evidence. A flagged baseline or endpoint excludes the market's rate from pooling. These screens cannot certify that an unflagged file is complete.",
        "5. Removed nested geographic files when at least 90% of their baseline IDs overlap a larger file. Removed remaining cross-market duplicate baseline IDs. Presence anywhere in the acquired panel during a selected snapshot month prevents that ID being counted as absent for that month.", "",
        f"Nested geography exclusions: {', '.join(f'{title(k)} within {title(v)}' for k,v in meta['nested_geography_exclusions'].items()) or 'none'}. Remaining overlapping IDs excluded: **{n(meta['overlapping_unique_baseline_ids_excluded'])}**. **{n(elsewhere)}** IDs missing from their own endpoint file were retained because another geography observed the same ID that month.", "",
        "The headline pool is total missing IDs divided by total starting IDs. An equal-market average is reported separately as a weighting sensitivity. Rates are not annualized and no Airbnb-wide population weights are inferred from this availability-selected sample.", "",
        "## Geographic breadth and weighting", "", "| Region | Markets | Starting IDs | Missing IDs | Observed disappearance |", "|---|---:|---:|---:|---:|"]
    for r in pools:
        if r["cohort"]=="all_listings" and r["policy"]=="coverage_screen" and r["statistic"]=="id_attrition" and r["scope"]!="all_eligible_markets":
            lines.append(f"| {r['scope']} | {r['markets']} | {n(r['baseline_ids'])} | {n(r['event_ids'])} | {pct(r['listing_weighted_rate'])} |")
    lines += ["",f"The equal-market average is **{pct(raw['equal_market_weighted_rate'])}**, compared with the listing-weighted **{pct(raw['listing_weighted_rate'])}**. Dropping one market at a time produces **{pct(raw['leave_one_market_out_min'])}–{pct(raw['leave_one_market_out_max'])}**. The largest market contributes {pct(raw['max_market_baseline_weight'])} of starting IDs. These checks describe concentration; they do not repair selection bias or establish global representativeness.","",
        "Country labels and geography definitions follow the source. Markets include cities, regions and several country-wide files. Individual country results can still rest on one market. [Country counts and rates](../../data/processed/listing_churn_archive/country_rates.csv) make that explicit.","",
        "## Disappearance versus sustained absence", "",
        "A listing enters the fixed cohort when observed in September. It is an endpoint disappearance if its ID is absent from every acquired June file. It qualifies for 90-day terminal absence only after at least two usable negative observations span 90 actual days, with no observed return from the first negative month onward. Unknown or failed captures cannot create negative evidence. Quarterly observations can miss pauses and returns between captures.","",
        "| Measure | Eligible markets | Starting IDs | Event IDs | Rate |", "|---|---:|---:|---:|---:|",
        f"| June endpoint ID disappearance | {raw['markets']} | {n(raw['baseline_ids'])} | {n(raw['event_ids'])} | {pct(raw['listing_weighted_rate'])} |",
        f"| 90-day repeated absence, coverage screen | {primary['markets']} | {n(primary['baseline_ids'])} | {n(primary['event_ids'])} | {pct(primary['listing_weighted_rate'])} |",
        f"| 90-day repeated absence, March negatives excluded | {conservative['markets']} | {n(conservative['baseline_ids'])} | {n(conservative['event_ids'])} | {pct(conservative['listing_weighted_rate'])} |",
        f"| Coverage screen, common eligible markets | {len(common)} | {n(common_n)} | {n(common_primary)} | {pct(common_primary/common_n)} |",
        f"| March negatives excluded, common eligible markets | {len(common)} | {n(common_n)} | {n(common_conservative)} | {pct(common_conservative/common_n)} |","",
        "The common-market rows isolate the effect of the negative-evidence rule. A market without a usable early negative opportunity has an unidentified persistence rate, even if the endpoint comparison is usable. The zero event count in such an output is never pooled as evidence of zero churn.","",
        "## The team's longer historical panel", "",
        f"The team's separate September-to-late-summer panel gives **{pct(team_raw['listing_weighted_rate'])}** ID disappearance ({n(team_raw['event_ids'])}/{n(team_raw['baseline_ids'])}, {team_raw['markets']} markets, {team_raw['min_interval_days']}–{team_raw['max_interval_days']} actual days). Austin's starting file is flagged and excluded. Persistent 90-day absence is **{pct(team_conservative['listing_weighted_rate'])}–{pct(team_primary['listing_weighted_rate'])}**, measured on {team_primary['markets']} eligible markets and {n(team_primary['baseline_ids'])} starting IDs. Mexico City and Nashville lack enough usable follow-up for this persistence measure.","",
        "This longer panel and the broad September-to-June panel have different endpoints and geographic composition. Their raw rates should not be presented as a time-series change in churn.","",
        "## Where listings went", "",
        f"The broad endpoint comparison found **{n(aliases)} possible continuations under another Airbnb ID across {alias_markets} markets**. Each requires a unique exact full permit field, matching room type and bedroom count, location within 300 metres, and a candidate ID not seen anywhere in the starting panel. These are unvalidated property-link candidates, not proven identities. They are reported separately and are not silently removed from the headline ID-disappearance rate.","",
        "The externally traced destination evidence remains the 20-case random San Diego pilot, selected from 208 persistent-absence cases with usable unique permits. It is too small and geographically narrow to estimate population destination shares:","",
        "| Observed evidence | Cases | What it establishes |", "|---|---:|---|",
        "| MLS-reported sale | 1 | A sale was reported after disappearance; post-sale use and causal connection are unknown. |",
        "| MLS-reported residential rental | 1 | A residential tenancy was reported; lease duration is not established. |",
        "| Other destinations unresolved | 18 | Includes one matched other-platform catalog entry and three additional leads. Current operation and newly occurring migration are unverified. |","",
        "The sale case has a reported July 30, 2026 transaction in the [sale listing](https://www.redfin.com/CA/San-Diego/3540-Quimby-St-92106/home/5346170). The residential rental case has a February 3, 2026 rented event in the [rental history](https://www.rereader.com/rentals/2307-Meade-Ave-San-Diego-CA-92116-427221294). Exact match evidence, timing and caveats are recorded in the [destination evidence ledger](../../data/processed/listing_churn_execution/destination_review.csv). The sale is not independently deed-verified. A later event does not establish why the Airbnb listing disappeared.","",
        "**The existing data do not identify the percentage sold, moved to Vrbo/Booking, converted to residential rental, or paused.** More Airbnb snapshots improve the disappearance estimate; they do not supply the missing cross-platform identities, transaction histories, or booking evidence. An existing competitor listing can be prior cross-listing. An active STR permit does not prove current rental operation. Unknown destinations remain unknown.","",
        "The [platform-history follow-up](2026-09-07_listing-platform-history.md) adds independent before/after archive checks for four pilot leads, supported pre-existing direct advertising, a current photo match and a conflicting Vrbo permit. It preserves unknown operating states and does not estimate migration shares.", "",
        "The [fee-catalyst time-series study](2026-09-07_fee-churn-catalyst.md) measures rolling disappearance before and after the October 2025 software-host fee rollout. It adds earlier history, monthly observations and repeated-absence checks; the headline nine-month rate here is not a fee-attributed churn estimate.", "",
        "## Exclusions", "", "| Market | Reason |", "|---|---|"]
    for r in coverage:
        if r["status"]!="pair_eligible":lines.append(f"| {title(r['market'])} | {r['reason']} |")
    lines += ["","## Largest included markets","","| Market | Starting IDs | Missing IDs | Disappearance | 90-day absence, March negatives excluded |","|---|---:|---:|---:|---:|"]
    for r in sorted(eligible,key=lambda r:int(r["baseline_ids"]),reverse=True)[:20]:
        c=conservative_rows.get(r["market"])
        lines.append(f"| {title(r['market'])} | {n(r['baseline_ids'])} | {n(r['missing_ids'])} | {pct(r['id_attrition'])} | {pct(c['persistent_90_rate']) if c else 'Not identified'} |")
    lines += ["","## Audit and reproduction","",
        "- [All broad market rates](../../data/processed/listing_churn_archive/market_rates.csv), [pooled rates](../../data/processed/listing_churn_archive/pooled_rates.csv), [coverage decisions](../../data/processed/listing_churn_archive/market_coverage.csv), [snapshot quality and hashes](../../data/processed/listing_churn_archive/snapshot_quality.csv), [geographic overlaps](../../data/processed/listing_churn_archive/geographic_overlap.csv), [execution metadata](../../data/processed/listing_churn_archive/execution_metadata.json).",
        "- [Longer team panel rates](../../data/processed/listing_churn_panel/market_rates.csv) and [team panel pooled results](../../data/processed/listing_churn_panel/pooled_rates.csv).",
        "- Raw downloaded listing files, compact extracts and granular candidate-ID mappings remain under gitignored `data/raw/`. Public outputs contain market aggregates and evidence references.","",
        "From the repository root in PowerShell, with Git available on PATH:","","```powershell",
        ".\\.venv\\Scripts\\python.exe analysis/src/acquire_churn_panel.py --source-rev df833f5f3980078beef09c1327940bfa58d57acf",
        ".\\.venv\\Scripts\\python.exe analysis/src/measure_churn_panel.py",
        ".\\.venv\\Scripts\\python.exe analysis/src/acquire_churn_archive.py --metadata data/manifests/inside_airbnb_archive_index_2026-09-07.json",
        ".\\.venv\\Scripts\\python.exe analysis/src/measure_churn_archive.py",
        ".\\.venv\\Scripts\\python.exe analysis/src/report_listing_churn.py",
        ".\\.venv\\Scripts\\python.exe -m unittest discover -s analysis/tests -v","```","",
        "The archive metadata is a captured public input, hashed in execution metadata. If the public site changes its archive index, capture a new dated input and review the selection before rerunning. Download errors are recorded without automatic retries. An incomplete history is excluded, never treated as a delisted cohort.","",
        "Inside Airbnb data are attributed to [Inside Airbnb](https://insideairbnb.com/get-the-data/) and licensed CC BY 4.0. Geography, source coverage, listing-versus-property identity, seasonal exposure and unobserved destinations remain material limits. No global permanent churn estimate or destination split is asserted.",""]
    report=ROOT/"research/notes/2026-09-07_listing-churn-broad-panel.md"
    report.write_text("\n".join(lines),encoding="utf-8")
    print(report)


if __name__=="__main__": main()
