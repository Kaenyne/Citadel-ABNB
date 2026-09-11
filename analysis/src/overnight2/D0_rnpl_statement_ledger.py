"""WS D, deliverable 1: dated ledger of every management statement about Reserve Now
Pay Later, cancellation rates, cancellation-policy changes, simplified fees, and the
product bundle's contribution to nights and GBV growth.

Every quote whose source sits in the main tree is verified verbatim against the source
file at build time. Quotes recovered from the live Airbnb newsroom on 2026-09-11 carry
quote_verified = "web_2026-09-11" and cannot be machine-checked here.

Run:  py -3.13 analysis/src/overnight2/D0_rnpl_statement_ledger.py
Reads (read-only) the main tree at C:/Users/krish/citadel-abnb.
Writes data/processed/overnight2/D/rnpl_statement_ledger.csv in this worktree.
"""

from __future__ import annotations

import csv
import gzip
import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
WORKTREE = HERE.parents[3]
MAIN = Path("C:/Users/krish/citadel-abnb")
OUT = WORKTREE / "data/processed/overnight2/D/rnpl_statement_ledger.csv"

# Source files. Keys are the locator stems used in the rows below.
SOURCES = {
    "call_3Q25": "data/raw/transcripts/web/3Q25.html",
    "call_4Q25": "data/raw/transcripts/web/4Q25.html",
    "call_1Q26": "data/raw/transcripts/web/1Q26.html",
    "call_2Q26": "data/raw/transcripts/web/2Q26.html",
    "call_2Q25": "data/raw/transcripts/web/2Q25.html",
    "letter_3Q25": "data/raw/letters/3Q25_d40503dex991.htm",
    "letter_4Q25": "data/raw/letters/4Q25_d58192dex991.htm",
    "letter_1Q26": "data/raw/letters/1Q26_d23351dex991.htm",
    "letter_2Q26": "data/raw/letters/2Q26_d70413dex991.htm",
    "10k_FY2025": "data/raw/filings/abnb_10k_FY2025.htm",
    "10q_2Q26": "data/raw/regulatory/quantification/abnb_2026q2_10q.html",
    "news_uk": "data/raw/abnb_newsroom/https_news_airbnb_com_en_uk_introducing_reserve_now_pay_later_giving_guests_greater_flexibility.html.gz",
    "news_apac": "data/raw/abnb_newsroom/https_news_airbnb_com_introducing_reserve_now_pay_later_giving_guests_greater_flexibility.html.gz",
    "news_au": "data/raw/abnb_newsroom/https_news_airbnb_com_en_au_introducing_reserve_now_pay_later_giving_guests_greater_flexibility.html.gz",
    "news_ca": "data/raw/abnb_newsroom/https_news_airbnb_com_introducing_reserve_now_pay_later_giving_canadian_guests_greater_flexibility.html.gz",
}

# Published URL for each source, for the note and for reproduction.
URLS = {
    "call_3Q25": "https://stockanalysis.com/stocks/abnb/transcripts/371470-q3-2025/",
    "call_4Q25": "https://stockanalysis.com/stocks/abnb/transcripts/396495-q4-2025/",
    "call_1Q26": "https://stockanalysis.com/stocks/abnb/transcripts/556160-q1-2026/",
    "call_2Q26": "https://stockanalysis.com/stocks/abnb/transcripts/662687-q2-2026/",
    "call_2Q25": "https://stockanalysis.com/stocks/abnb/transcripts/q2-2025/",
    "letter_3Q25": "https://www.sec.gov/Archives/edgar/data/1559720/000119312525000000/d40503dex991.htm",
    "letter_4Q25": "https://www.sec.gov/Archives/edgar/data/1559720/000119312526000000/d58192dex991.htm",
    "letter_1Q26": "https://www.sec.gov/Archives/edgar/data/1559720/000119312526000000/d23351dex991.htm",
    "letter_2Q26": "https://www.sec.gov/Archives/edgar/data/1559720/000119312526337928/d70413dex991.htm",
    "10k_FY2025": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001559720&type=10-K",
    "10q_2Q26": "https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm",
    "news_uk": "https://news.airbnb.com/en-uk/introducing-reserve-now-pay-later-giving-guests-greater-flexibility",
    "news_apac": "https://news.airbnb.com/introducing-reserve-now-pay-later-giving-guests-greater-flexibility",
    "news_au": "https://news.airbnb.com/en-au/introducing-reserve-now-pay-later-giving-guests-greater-flexibility",
    "news_ca": "https://news.airbnb.com/introducing-reserve-now-pay-later-giving-canadian-guests-greater-flexibility",
    "news_us_launch": "https://news.airbnb.com/reserve-now-pay-later/",
    "news_global": "https://news.airbnb.com/reserve-now-pay-later-is-now-available-worldwide/",
}

FIELDS = [
    "statement_id", "date", "period_referenced", "event", "speaker", "role",
    "theme", "quote", "quantity", "quantity_num_low", "quantity_num_high",
    "unit", "basis", "scope", "night_weighted", "official_or_mirror",
    "quote_verified", "source_key", "source_file", "source_url", "access_date", "note",
]


def normalise(text: str) -> str:
    """Fold typographic variants and whitespace so quotes compare cleanly."""
    for bad, good in [
        ("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"'),
        ("\u2014", "-"), ("\u2013", "-"), ("\u2212", "-"), ("\u00a0", " "),
        ("\u00ad", ""), ("\ufeff", ""),
    ]:
        text = text.replace(bad, good)
    return re.sub(r"\s+", " ", text)


def to_text(path: Path) -> str:
    if path.suffix == ".gz":
        raw = gzip.open(path, "rt", encoding="utf-8", errors="replace").read()
    else:
        raw = path.read_text(encoding="utf-8", errors="replace")
    raw = re.sub(r"<(script|style).*?</\1>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return normalise(html.unescape(raw))


# --------------------------------------------------------------------------------------
# The ledger. One row per statement. "quantity" reproduces the figure as disclosed.
# "basis" states what the figure is a share OF. "night_weighted" is yes only where the
# disclosed denominator is nights; GBV shares and listing counts are no.
# --------------------------------------------------------------------------------------
ROWS: list[dict] = [
    # ---------------- US launch, 3Q25 ----------------
    dict(
        statement_id="D001", date="2025-08-14", period_referenced="3Q25",
        event="newsroom", speaker="Airbnb Newsroom", role="company",
        theme="rollout_us",
        quote="We've introduced a new way to pay, offering US guests the option to reserve a stay and pay $0 upfront when they book eligible domestic stays.",
        quantity="$0 upfront", unit="usd", basis="eligibility rule",
        scope="US guests, US domestic stays",
        night_weighted="n/a", official_or_mirror="official",
        quote_verified="web_2026-09-11", source_key="news_us_launch",
        note="Announcement date. Management separately dates the launch to the beginning of 3Q25, so the announcement is not the treatment start.",
    ),
    dict(
        statement_id="D002", date="2025-08-14", period_referenced="3Q25",
        event="newsroom", speaker="Airbnb Newsroom", role="company",
        theme="payment_timing",
        quote="Available for listings with a moderate or flexible cancellation policy, guests don't need to pay the full amount until shortly before the end of the listing's free cancellation period. Cancellation policies selected by hosts remain unchanged, and because the payment from guests is always due before the free cancellation period ends, hosts have time to secure another booking even if a guest cancels.",
        quantity="payment due shortly before end of free-cancellation window",
        unit="timing rule", basis="payment schedule per reservation",
        scope="eligible listings, moderate or flexible policy",
        night_weighted="n/a", official_or_mirror="official",
        quote_verified="web_2026-09-11", source_key="news_us_launch",
        note="The single most load-bearing timing fact in the ledger: the RNPL payment deadline, and therefore the decision point at which a payment-failure cancellation is recognised, sits days before check-in, not days after booking. It also states the rebooking mechanism Airbnb relies on.",
    ),
    dict(
        statement_id="D003", date="2025-11-06", period_referenced="3Q25",
        event="call", speaker="Brian Chesky", role="ceo", theme="bundle_contribution",
        quote="We introduced Reserve Now, Pay Later in the United States. Not unexpectedly, this helped drive night and seats booked in Q3. We're going to continue to roll this out more broadly next year.",
        quantity="", unit="qualitative", basis="reported nights and seats booked",
        scope="US", night_weighted="yes", official_or_mirror="mirror",
        quote_verified="file", source_key="call_3Q25",
        note="First nights attribution. No magnitude given.",
    ),
    dict(
        statement_id="D004", date="2025-11-06", period_referenced="3Q25",
        event="call", speaker="Ellie Mertz", role="cfo", theme="eligibility",
        quote="In terms of the Reserve Now, Pay Later offering, we launched it at the beginning of Q3. It is specifically something that is being offered to U.S. customers who are traveling domestically and are choosing listings that have a flexible or moderate cancellation policy. It is not offered to the entirety of the U.S. guest population.",
        quantity="", unit="qualitative", basis="eligibility definition",
        scope="US guests, domestic stays, flexible or moderate policy",
        night_weighted="no", official_or_mirror="mirror",
        quote_verified="file", source_key="call_3Q25",
        note="Treatment is guest origin x destination x host cancellation policy, not destination country. Dates launch to the beginning of 3Q25, i.e. July, not the 14 August announcement.",
    ),
    dict(
        statement_id="D005", date="2025-11-06", period_referenced="3Q25",
        event="call", speaker="Ellie Mertz", role="cfo", theme="take_up",
        quote="About 70% of people that we offer Reserve Now, Pay Later take us up on that offering.",
        quantity="~70%", quantity_num_low=70, quantity_num_high=70,
        unit="percent", basis="take-up among guests offered the product",
        scope="US eligible subset", night_weighted="no",
        official_or_mirror="mirror", quote_verified="file", source_key="call_3Q25",
        note="Conditional on being offered. Not platform penetration, not a nights or GBV share. Denominator is people, not nights.",
    ),
    dict(
        statement_id="D006", date="2025-11-06", period_referenced="3Q25",
        event="call", speaker="Ellie Mertz", role="cfo", theme="cancellation_effect",
        quote="Yes, there are increased cancellations, but we're highly confident that the net impact of the product is a lift to net bookings.",
        quantity="", unit="qualitative", basis="net bookings",
        scope="US", night_weighted="no", official_or_mirror="mirror",
        quote_verified="file", source_key="call_3Q25",
        note="First admission of higher cancellations. No rate, no denominator, no timing.",
    ),
    dict(
        statement_id="D007", date="2025-11-06", period_referenced="3Q25",
        event="call", speaker="Richard Clarke / Ellie Mertz", role="analyst_q",
        theme="declined_to_quantify",
        quote="Just what percentage of the acceleration in the U.S. has come from that? Any early signs of what cancellation rates might look like on those bookings or your expectations of what they might look like?",
        quantity="", unit="n/a", basis="question not answered with a figure",
        scope="US", night_weighted="n/a", official_or_mirror="mirror",
        quote_verified="file", source_key="call_3Q25",
        note="Logged in the main tree as data/processed/abnb_declined_to_quantify.csv row 2025Q3 Richard Clarke. The answer substituted the ~70% take-up figure for the requested share of the acceleration and gave no cancellation rate.",
    ),
    dict(
        statement_id="D008", date="2025-11-06", period_referenced="3Q25",
        event="letter", speaker="Airbnb (shareholder letter)", role="company",
        theme="rollout_us",
        quote="In August, we launched our Reserve Now, Pay Later payment option within the U.S., which allows guests to pay $0 upfront when they book eligible domestic stays. We are encouraged by the early results. The introduction of Reserve Now, Pay Later helped drive the acceleration of Nights and Seats Booked in North America during Q3 2025.",
        quantity="", unit="qualitative", basis="reported nights and seats booked, NA",
        scope="North America", night_weighted="yes", official_or_mirror="official",
        quote_verified="file", source_key="letter_3Q25",
        note="The official letter says August; the call says beginning of Q3. Treat the in-quarter ramp date as a range July to August 2025, not a point.",
    ),
    dict(
        statement_id="D009", date="2025-11-06", period_referenced="3Q25",
        event="letter", speaker="Airbnb (shareholder letter)", role="company",
        theme="cancellation_timing",
        quote="While we expect some cancellations closer to the date of stay, which may or may not occur in the same booking quarter, we expect a net benefit to overall bookings based on prior testing.",
        quantity="", unit="qualitative", basis="cancellation recognition quarter",
        scope="global", night_weighted="no", official_or_mirror="official",
        quote_verified="file", source_key="letter_3Q25",
        note="Airbnb itself flags the cross-quarter recognition problem that the cohort arithmetic exists to size. This is the strongest official support for a cancellation-tail mechanism.",
    ),
    dict(
        statement_id="D010", date="2025-11-06", period_referenced="3Q25",
        event="letter", speaker="Airbnb (shareholder letter)", role="company",
        theme="lead_time",
        quote="Average lead times were up slightly on a year-over-year basis, particularly in North America in part driven by the launch of our Reserve Now, Pay Later offering.",
        quantity="up slightly", unit="qualitative",
        basis="average booking-to-stay lead time, y/y",
        scope="global, NA emphasised", night_weighted="no",
        official_or_mirror="official", quote_verified="file", source_key="letter_3Q25",
        note="Only directional. Airbnb has never published a lead-time distribution. The one quantified lead-time datapoint in the whole record is D011.",
    ),
    dict(
        statement_id="D011", date="2025-08-06", period_referenced="2Q25",
        event="call", speaker="Ellie Mertz", role="cfo", theme="lead_time",
        quote="As you'll recall, back in April, lead times were heavily compressed. They were down about 7% year-over-year.",
        quantity="-7%", quantity_num_low=-7, quantity_num_high=-7,
        unit="percent", basis="average booking-to-stay lead time, y/y change",
        scope="global", night_weighted="no", official_or_mirror="mirror",
        quote_verified="file", source_key="call_2Q25",
        note="Pre-RNPL. The only quantified y/y lead-time move Airbnb has given, and it fixes the scale at which management calls a lead-time shift large: roughly 7%, not a doubling.",
    ),
    dict(
        statement_id="D012", date="2025-11-06", period_referenced="4Q25",
        event="letter", speaker="Airbnb (shareholder letter)", role="company",
        theme="cancellation_policy",
        quote="Updated cancellation policies-We're helping hosts earn more and guests make changes more easily by updating our cancellation policies. Hosts can now choose a new policy that allows guests to cancel for free up to 14 days before check-in. And for all stays under 28 nights, guests can cancel for a full refund up to 24 hours after their reservation is confirmed, if they book more than 7 days before check-in.",
        quantity="14 days / 24 hours / 7 days / 28 nights",
        unit="days", basis="cancellation policy parameters",
        scope="global", night_weighted="n/a", official_or_mirror="official",
        quote_verified="file", source_key="letter_3Q25",
        note="The cancellation-redesign leg of the bundle. Two distinct mechanisms: a new 14-day free-cancel host policy, and a universal 24-hour grace period for bookings made more than 7 days out. The grace period mechanically creates a within-days cancellation spike in the booking quarter itself, unlike the RNPL payment-deadline cancellations which land near check-in.",
    ),
    dict(
        statement_id="D013", date="2025-11-06", period_referenced="4Q25",
        event="letter", speaker="Airbnb (shareholder letter)", role="company",
        theme="simplified_fees",
        quote="In October, we took steps to simplify our fee structure, which we",
        quantity="October 2025", unit="date", basis="fee migration start",
        scope="software-connected / PMS hosts", night_weighted="n/a",
        official_or_mirror="official", quote_verified="file", source_key="letter_3Q25",
        note="Tranche 1 start date. The 2Q26 call instead says 'September of last year'; the 1Q26 letter says 'Beginning in Q4 2025'. The simplified-fee start is therefore a September to October 2025 range, not a point.",
    ),

    # ---------------- 4Q25 print, February 2026 ----------------
    dict(
        statement_id="D014", date="2026-02-12", period_referenced="4Q25",
        event="call", speaker="Ellie Mertz", role="cfo", theme="bundle_contribution",
        quote="In total, we estimate these three features delivered over 200 basis points of growth in nights booked and roughly 300 basis points of growth in GBV in Q4.",
        quantity=">200bp nights / ~300bp GBV",
        quantity_num_low=2.0, quantity_num_high=3.0,
        unit="growth points",
        basis="y/y growth contribution of RNPL plus updated cancellation policies plus simplified fees, combined",
        scope="global", night_weighted="yes",
        official_or_mirror="mirror", quote_verified="file", source_key="call_4Q25",
        note="A second, earlier bundle attribution that the RNPL handoff does not carry. It puts the 1Q26 ~3pt figure on a trajectory: >2pts in 4Q25 rising to ~3pts in 1Q26. Three features, global, nights and GBV legs differ by ~1 point, which is the ADR/mix wedge.",
    ),
    dict(
        statement_id="D015", date="2026-02-12", period_referenced="4Q25",
        event="call", speaker="Ellie Mertz", role="cfo", theme="bundle_contribution",
        quote="In Q4, a few updates in particular helped drive our acceleration. The launch of Reserve Now, Pay Later, updates to our cancellation policy, and the beginning of our migration to a simplified fee structure.",
        quantity="3 features", unit="count", basis="composition of the bundle",
        scope="global", night_weighted="n/a", official_or_mirror="mirror",
        quote_verified="file", source_key="call_4Q25",
        note="Names the three features. No per-feature split has ever been disclosed for any quarter.",
    ),
    dict(
        statement_id="D016", date="2026-02-12", period_referenced="4Q25",
        event="call", speaker="Ellie Mertz", role="cfo", theme="adr_mix",
        quote="Reserve Now, Pay Later saw significant adoption among eligible guests in Q4. It's also led to longer booking lead times and a mix shift towards larger entire homes, especially those with four more bedrooms, contributing to",
        quantity="4+ bedrooms", unit="qualitative",
        basis="mix of booked listings",
        scope="global", night_weighted="no", official_or_mirror="mirror",
        quote_verified="file", source_key="call_4Q25",
        note="The mix shift is why RNPL ADR exceeds non-RNPL ADR, which is why an RNPL GBV share overstates its nights share. Direction is disclosed; the ratio is not.",
    ),
    dict(
        statement_id="D017", date="2026-02-12", period_referenced="4Q25",
        event="call", speaker="Ellie Mertz", role="cfo", theme="cancellation_rate",
        quote="I think one piece of perspective is that in terms of the aggregate nominal increase in cancellations rate, it's approximately 1%.",
        quantity="~1 point", quantity_num_low=1.0, quantity_num_high=1.0,
        unit="percentage points",
        basis="platform aggregate cancellation rate, increase, denominator not stated",
        scope="global platform, all bookings", night_weighted="no",
        official_or_mirror="mirror", quote_verified="file", source_key="call_4Q25",
        note="No denominator, no period, no unit of account. 'Nominal increase' is ambiguous between a level change in the rate and a change in cancellation volume.",
    ),
    dict(
        statement_id="D018", date="2026-02-12", period_referenced="4Q25",
        event="call", speaker="Ellie Mertz", role="cfo", theme="cancellation_rate",
        quote="So, you know, an average of maybe 16% cancellation rate historically going to 17% is obviously higher within the cohorts that chooses that product, but is not hugely material relative to the broader cancellations on the platform.",
        quantity="16% -> 17%", quantity_num_low=16.0, quantity_num_high=17.0,
        unit="percent",
        basis="platform-average cancellation rate, historical versus current; unit of account not stated",
        scope="global platform", night_weighted="no",
        official_or_mirror="mirror", quote_verified="file", source_key="call_4Q25",
        note="The anchor figure. Hedged three ways in one sentence: 'an average of maybe', 'historically' with no base period, and no statement of whether the rate is per booking, per night or per dollar. It is not an RNPL cohort rate and not a quarterly series.",
    ),
    dict(
        statement_id="D019", date="2026-02-12", period_referenced="4Q25",
        event="call", speaker="Ellie Mertz", role="cfo", theme="cancellation_timing",
        quote="we extensively tested the product to ensure that by the time the cohorts opting into the product had reached their check-in date, that it was net beneficial to the business, meaning that the growth lift in bookings was larger than the net increase in cancellations before check-in.",
        quantity="", unit="qualitative",
        basis="net benefit measured at check-in date, per booking cohort",
        scope="tested segments", night_weighted="no",
        official_or_mirror="mirror", quote_verified="file", source_key="call_4Q25",
        note="Decisive for the hypothesis. Management's net-benefit test is on a stay-date basis for a booking cohort. Reported Nights and Seats Booked is a transaction-period metric. A product can be net beneficial at check-in and still move nights between reported quarters, so this statement does not rule out a reported-nights timing drag.",
    ),
    dict(
        statement_id="D020", date="2026-02-12", period_referenced="4Q25",
        event="call", speaker="Ellie Mertz", role="cfo", theme="cancellation_effect",
        quote="in the segments that we have launched this offering, the cancellation curves have, been, you know, very close to what we saw from a tested perspective, and so we feel, you know, frankly, quite good about the progress and the performance of that offering.",
        quantity="", unit="qualitative", basis="realised versus tested cancellation curve",
        scope="launched segments", night_weighted="no",
        official_or_mirror="mirror", quote_verified="file", source_key="call_4Q25",
        note="Evidence against the hypothesis: management says realised cancellation timing matched the pre-launch tests. Confirms a cancellation curve exists internally and is undisclosed.",
    ),
    dict(
        statement_id="D021", date="2026-02-12", period_referenced="4Q25",
        event="call", speaker="Ellie Mertz", role="cfo", theme="cancellation_effect",
        quote="over the full year, obviously there is a bit of a pull forward in terms of when people make their booking, but we are already absorbing the elevated level of cancellations from that product.",
        quantity="", unit="qualitative", basis="reported results to date",
        scope="global", night_weighted="no", official_or_mirror="mirror",
        quote_verified="file", source_key="call_4Q25",
        note="Management's position is that the drag is already in the printed numbers, which is exactly the double-counting risk in applying a fresh haircut to a post-rollout baseline.",
    ),
    dict(
        statement_id="D022", date="2026-02-12", period_referenced="4Q25",
        event="letter", speaker="Airbnb (shareholder letter)", role="company",
        theme="take_up",
        quote="After a strong U.S. launch-with over 70% adoption by eligible bookings*-and testing in other markets, we're rolling it out to more guests in 2026.",
        quantity=">70%", quantity_num_low=70, quantity_num_high=70,
        unit="percent", basis="adoption among eligible bookings, measured on global GBV in 4Q25",
        scope="global eligible subset", night_weighted="no",
        official_or_mirror="official", quote_verified="file", source_key="letter_4Q25",
        note="The letter footnote reads '*Adoption percentage based on global GBV in Q4 2025.' That is a different basis from the 3Q25 call's 70% of people offered: one is GBV-weighted and global, the other is headcount and US. The two 70s are not the same statistic and must not be chained into a series.",
    ),
    dict(
        statement_id="D023", date="2026-02-12", period_referenced="4Q25",
        event="letter", speaker="Airbnb (shareholder letter)", role="company",
        theme="rollout_international",
        quote="In February 2026, we completed testing Reserve Now, Pay Later across additional markets, and currently plan to make it available to even more guests globally in 2026.",
        quantity="February 2026", unit="date",
        basis="completion of international testing",
        scope="additional markets", night_weighted="n/a",
        official_or_mirror="official", quote_verified="file", source_key="letter_4Q25",
        note="Official corroboration that international go-live begins in 1Q26, not 4Q25.",
    ),
    dict(
        statement_id="D024", date="2026-02-12", period_referenced="4Q25",
        event="letter", speaker="Airbnb (shareholder letter)", role="company",
        theme="simplified_fees",
        quote="We began migrating property management software (\"PMS\") hosts on our split fee structure (where hosts paid a 3% fee and guests paid a separate service fee) to a 15.5% single service fee. Additionally, most non-PMS hosts on our platform that were previously subject to our single fee structure are now subject to the 15.5% fee as of December.",
        quantity="15.5%", quantity_num_low=15.5, quantity_num_high=15.5,
        unit="percent", basis="host service fee rate",
        scope="PMS hosts from October 2025, most non-PMS single-fee hosts from December 2025",
        night_weighted="n/a", official_or_mirror="official",
        quote_verified="file", source_key="letter_4Q25",
        note="Two dated tranches inside 4Q25, not one. PR #32 models a single October tranche.",
    ),

    # ---------------- International rollout, February to March 2026 ----------------
    dict(
        statement_id="D025", date="2026-02-17", period_referenced="1Q26",
        event="newsroom", speaker="Airbnb Newsroom", role="company",
        theme="rollout_international",
        quote="Reserve Now, Pay Later is now available to guests globally for domestic and international trips, giving guests even more flexibility to reserve eligible stays with nothing due at booking.",
        quantity="global", unit="qualitative", basis="availability by guest location",
        scope="global, excluding BRL / INR / TRY payers",
        night_weighted="n/a", official_or_mirror="official",
        quote_verified="web_2026-09-11", source_key="news_global",
        note="The worldwide announcement. Fetched 2026-09-11. The same page states 'Reservations paid in Brazilian Real (BRL), Indian Rupee (INR), or Turkish Lira (TRY) are ineligible.' Exclusion is by payment currency, so it is not a clean country assignment.",
    ),
    dict(
        statement_id="D026", date="2026-02-18", period_referenced="1Q26",
        event="newsroom", speaker="Airbnb Newsroom (UK)", role="company",
        theme="rollout_international",
        quote="Reserve Now, Pay Later is available for UK guests booking eligible listings around the world with a flexible or moderate cancellation policy now.",
        quantity="2026-02-18", unit="date", basis="market go-live announcement",
        scope="UK guests, destinations worldwide", night_weighted="n/a",
        official_or_mirror="official", quote_verified="file", source_key="news_uk",
        note="Local archive copy, datePublished 2026-02-18T16:26:49Z. Note the scope inversion versus the US launch: international guests get worldwide destinations, while US guests originally got domestic only.",
    ),
    dict(
        statement_id="D027", date="2026-02-23", period_referenced="1Q26",
        event="newsroom", speaker="Airbnb Newsroom (Asia Pacific)", role="company",
        theme="rollout_international",
        quote="Reserve Now, Pay Later will be available to all users, excluding those paying in Brazilian Real (BRL), Indian Rupee (INR), or Turkish Lira (TRY).",
        quantity="3 excluded currencies", quantity_num_low=3, quantity_num_high=3,
        unit="count", basis="currency-level exclusion from eligibility",
        scope="global, excluding BRL / INR / TRY payers",
        night_weighted="n/a", official_or_mirror="official",
        quote_verified="file", source_key="news_apac",
        note="Footnote 1 of the Asia Pacific post, datePublished 2026-02-24T02:56:49Z, byline February 23, 2026. Identical footnote appears on the AU and CA posts. Brazil and India are two of Airbnb's fastest-growing markets, so the exclusion is material to any ex-NA lap assumption.",
    ),
    dict(
        statement_id="D028", date="2026-02-23", period_referenced="1Q26",
        event="newsroom", speaker="Airbnb Newsroom (Australia)", role="company",
        theme="rollout_international",
        quote="Reserve Now, Pay Later is available now for Australian guests booking eligible listings around the world with a flexible or moderate cancellation policy.",
        quantity="2026-02-23", unit="date", basis="market go-live announcement",
        scope="Australian guests, destinations worldwide", night_weighted="n/a",
        official_or_mirror="official", quote_verified="file", source_key="news_au",
        note="Local archive copy, datePublished 2026-02-23T01:19:43Z.",
    ),
    dict(
        statement_id="D029", date="2026-03-04", period_referenced="1Q26",
        event="newsroom", speaker="Airbnb Newsroom (Canada)", role="company",
        theme="rollout_international",
        quote="Reserve Now, Pay Later complements Airbnb's suite of flexible payment options, helping make travel more affordable, including Pay Part Now, Part Later -where guests can pay a portion at checkout and the remainder closer to check-in-as well as Pay Over Time with Klarna .",
        quantity="2026-03-04", unit="date", basis="market go-live announcement",
        scope="Canadian guests, destinations worldwide", night_weighted="n/a",
        official_or_mirror="official", quote_verified="file", source_key="news_ca",
        note="Local archive copy, datePublished 2026-03-04T19:33:11Z, the latest dated market post in the archive. Canada is in North America but got RNPL only in 1Q26, so 'NA only' in PR #32 is really 'US only' for the 2025 cohort. Also records two other flexible-payment products whose effects overlap RNPL's.",
    ),
    dict(
        statement_id="D030", date="2026-02-18", period_referenced="4Q25",
        event="newsroom", speaker="Airbnb Newsroom (UK)", role="company",
        theme="bundle_contribution",
        quote="The recent launch of Reserve Now, Pay Later in the US helped drive the acceleration of nights and seats booked in Q4 2025 from Q3 2025.",
        quantity="", unit="qualitative",
        basis="sequential acceleration in reported nights and seats booked",
        scope="US launch, global KPI", night_weighted="yes",
        official_or_mirror="official", quote_verified="file", source_key="news_uk",
        note="Airbnb's marketing attributes the 3Q25 to 4Q25 nights acceleration to the US launch, which is a stronger claim than the letters make.",
    ),

    # ---------------- 1Q26 print, May 2026 ----------------
    dict(
        statement_id="D031", date="2026-05-07", period_referenced="1Q26",
        event="letter", speaker="Airbnb (shareholder letter)", role="company",
        theme="gbv_share",
        quote="We're giving guests more flexibility in how they pay with Reserve Now, Pay Later. And in Q1, roughly 20% of global GBV came from Reserve Now, Pay Later bookings.",
        quantity="~20%", quantity_num_low=20, quantity_num_high=20,
        unit="percent", basis="share of global GBV booked in the quarter",
        scope="global", night_weighted="no",
        official_or_mirror="official", quote_verified="file", source_key="letter_1Q26",
        note="In the official letter, not only the call. GBV share, not nights share: converting it needs an RNPL-to-non-RNPL ADR ratio, and management has said the RNPL mix skews to larger higher-priced homes, so the nights share is lower than 20%.",
    ),
    dict(
        statement_id="D032", date="2026-05-07", period_referenced="1Q26",
        event="call", speaker="Ellie Mertz", role="cfo", theme="bundle_contribution",
        quote="In total, we estimate these three features delivered approximately three points of nights booked growth and approximately four points of GBV growth in Q1.",
        quantity="~3 pts nights / ~4 pts GBV",
        quantity_num_low=3.0, quantity_num_high=4.0,
        unit="growth points",
        basis="y/y growth contribution of RNPL plus updated cancellation policies plus simplified fees, combined",
        scope="global", night_weighted="yes",
        official_or_mirror="mirror", quote_verified="file", source_key="call_1Q26",
        note="The headline bundle figure. Three features, global, net of cancellations already recognised. Not RNPL-only and not US-only. Pairs with D014: >2pts in 4Q25, ~3pts in 1Q26.",
    ),
    dict(
        statement_id="D033", date="2026-05-07", period_referenced="1Q26",
        event="call", speaker="Ellie Mertz", role="cfo", theme="bundle_contribution",
        quote="First, we expanded Reserve Now, Pay Later to more markets, and adoption continued to increase. In addition to driving longer booking lead times and contributing to the increase in ADR, Reserve Now, Pay Later is driving a meaningful lift to all booking metrics, net of cancellation.",
        quantity="", unit="qualitative", basis="booking metrics net of cancellation",
        scope="global", night_weighted="no", official_or_mirror="mirror",
        quote_verified="file", source_key="call_1Q26",
        note="'net of cancellation' is management's own framing and is the phrase that makes a further cancellation haircut on the same quarters a double count.",
    ),
    dict(
        statement_id="D034", date="2026-05-07", period_referenced="1Q26",
        event="call", speaker="Ellie Mertz", role="cfo", theme="rollout_international",
        quote="if you look at the timeline of last year, we initially launched Reserve Now, Pay Later in the U.S. in Q3 to great results. Over the course of Q4, we began merchandising up funnel so that there was broader awareness to the consumer before they got to checkout. We saw that that was incremental to lift as well. Most recently in Q1, we rolled out RNPL to most of the rest of the world.",
        quantity="4 dated steps", quantity_num_low=4, quantity_num_high=4,
        unit="count", basis="rollout chronology as stated by management",
        scope="US 3Q25, US merchandising 4Q25, rest of world 1Q26",
        night_weighted="n/a", official_or_mirror="mirror",
        quote_verified="file", source_key="call_1Q26",
        note="Management's own four-step timeline, and the direct answer to PR #32's top open question: the ex-US rollout is 1Q26, so the international lap falls in 1Q27, not 2026. It also shows the US effect itself ramped across two quarters through up-funnel merchandising, so the 3Q25 base is not a clean step.",
    ),
    dict(
        statement_id="D035", date="2026-05-07", period_referenced="1Q26",
        event="call", speaker="Ellie Mertz", role="cfo", theme="cancellation_effect",
        quote="What I would say is that in every market that we have launched Reserve Now, Pay Later, there is a material lift to gross bookings. In all cases, we tested extensively to ensure that the net lift to bookings was positive. Certainly with the offering, there's a very elevated level of cancellations that come with the program. Across all regions, what we see is that the net impact is positive to the business.",
        quantity="", unit="qualitative", basis="gross bookings and net bookings",
        scope="all launched regions", night_weighted="no",
        official_or_mirror="mirror", quote_verified="file", source_key="call_1Q26",
        note="'Very elevated level of cancellations' is the strongest cancellation language on record, and it sits in the same sentence as a positive net claim. Both halves belong in the ledger.",
    ),
    dict(
        statement_id="D036", date="2026-05-07", period_referenced="1Q26",
        event="call", speaker="Ellie Mertz", role="cfo", theme="take_up",
        quote="In terms of relative adoption, the U.S. we are seeing the highest level of adoption, but the other markets are not far behind.",
        quantity="", unit="qualitative", basis="relative take-up by region",
        scope="US versus other markets", night_weighted="no",
        official_or_mirror="mirror", quote_verified="file", source_key="call_1Q26",
        note="Implies ex-US take-up converges quickly, which argues the 1Q27 international lap is closer in size to the US lap than a slow-ramp assumption would give.",
    ),
    dict(
        statement_id="D037", date="2026-05-07", period_referenced="1Q26",
        event="letter", speaker="Airbnb (shareholder letter)", role="company",
        theme="unearned_fees",
        quote="Absent the impact of Reserve Now, Pay Later bookings, which defer guest payments from the time of booking closer to the date of stay, we expect that unearned fees and FCF would have grown year-over-year.",
        quantity="", unit="qualitative", basis="unearned fees and FCF, y/y",
        scope="global", night_weighted="no",
        official_or_mirror="official", quote_verified="file", source_key="letter_1Q26",
        note="1Q26 unearned fees were +0.4% y/y against GBV +19.2%, per data/processed/overnight/02_kpi_panel_quarterly.csv in the main tree.",
    ),
    dict(
        statement_id="D038", date="2026-05-07", period_referenced="3Q26",
        event="letter", speaker="Airbnb (shareholder letter)", role="company",
        theme="unearned_fees",
        quote="Specifically, Reserve Now, Pay Later shifts the timing of guest payments closer to the date of stay, resulting in lower unearned fees in Q1 and Q2 and higher unearned fees in Q3.",
        quantity="lower Q1 and Q2, higher Q3", unit="qualitative",
        basis="unearned fees by quarter, RNPL timing effect",
        scope="global", night_weighted="no",
        official_or_mirror="official", quote_verified="file", source_key="letter_1Q26",
        note="The single most useful forward-testable statement in the ledger. It is a dated, official, directional prediction about 3Q26 that can be scored on 5 November, and it runs against the FY2025 10-K's baseline seasonality, which says unearned fees normally fall in Q3 as check-ins peak. See the pre-registered thresholds in the note.",
    ),
    dict(
        statement_id="D039", date="2026-05-07", period_referenced="1Q26",
        event="letter", speaker="Airbnb (shareholder letter)", role="company",
        theme="lead_time",
        quote="In Q1 2026, we observed relatively consistent year-over-year trends in terms of market type and travel corridor, and saw a lengthening of lead times across all regions, driven in part by the continued expansion of our Reserve Now, Pay Later payment offering.",
        quantity="lengthening, all regions", unit="qualitative",
        basis="average booking-to-stay lead time, y/y",
        scope="all regions", night_weighted="no",
        official_or_mirror="official", quote_verified="file", source_key="letter_1Q26",
        note="Longer lead times push a given booking cohort's stay dates, and therefore its payment-deadline cancellations, further into later quarters. That is the mechanism by which 1H26 bookings can deposit cancellations into 3Q26 and 4Q26.",
    ),
    dict(
        statement_id="D040", date="2026-05-07", period_referenced="2H26",
        event="letter", speaker="Airbnb (shareholder letter)", role="company",
        theme="lap",
        quote="We remain optimistic about our continued momentum, even as we face tougher comparisons in the back half of this year against the rollout of Reserve Now, Pay Later in 2025 and current headwinds from the Middle East conflict.",
        quantity="", unit="qualitative", basis="y/y comparison difficulty, 2H26",
        scope="global, against the 2025 US rollout", night_weighted="no",
        official_or_mirror="official", quote_verified="file", source_key="letter_1Q26",
        note="Management itself flags the 2H26 lap. This is the disclosure PR #32 builds its lap schedule on.",
    ),
    dict(
        statement_id="D041", date="2026-05-07", period_referenced="1Q26",
        event="call", speaker="Ellie Mertz", role="cfo", theme="simplified_fees",
        quote="Over a quarter of our active listings is now subject to the single service fee.",
        quantity=">25%", quantity_num_low=25, quantity_num_high=25,
        unit="percent", basis="share of active listings on the single service fee",
        scope="global supply", night_weighted="no",
        official_or_mirror="mirror", quote_verified="file", source_key="call_1Q26",
        note="Call only; the 1Q26 letter's fee paragraph carries no percentage. The main tree's data/processed/overnight/06_fee_timeline.csv attributes this to the 1Q26 letter, which is a misattribution.",
    ),
    dict(
        statement_id="D042", date="2026-05-07", period_referenced="1Q26",
        event="letter", speaker="Airbnb (shareholder letter)", role="company",
        theme="cancellation_rate",
        quote="In Q1 2026, Nights and Seats Booked grew over 9% year-over-year, despite increased cancellations from the Middle East conflict. Absent the impact of the conflict, we estimate growth of Nights and Seats Booked would have been approximately 10% year-over-year, an acceleration compared to Q1 2025.",
        quantity="~1 growth point", quantity_num_low=0.85, quantity_num_high=1.0,
        unit="growth points",
        basis="reported nights growth reduction attributed to conflict-driven cancellations",
        scope="EMEA and APAC cancellations, global KPI", night_weighted="yes",
        official_or_mirror="official", quote_verified="file", source_key="letter_1Q26",
        note="The only case where Airbnb has sized a cancellation shock in reported-nights growth points. It calibrates the materiality arithmetic: roughly one growth point, which on the 1Q25 denominator of 143.1mm is about 1.4mm nights. That is the order of magnitude a cancellation event has to reach to be visible.",
    ),

    # ---------------- 2Q26 print, August 2026 ----------------
    dict(
        statement_id="D043", date="2026-08-06", period_referenced="2Q26",
        event="call", speaker="Ellie Mertz", role="cfo", theme="gbv_share",
        quote="Specifically in Q2, over 20% of our total GBV was booked using this flexible payment option.",
        quantity=">20%", quantity_num_low=20, quantity_num_high=20,
        unit="percent", basis="share of total GBV booked in the quarter",
        scope="global", night_weighted="no",
        official_or_mirror="mirror", quote_verified="file", source_key="call_2Q26",
        note="Call mirror only. The official 2Q26 letter confirms wider availability but carries no GBV share. 'Over 20%' against 1Q26's 'roughly 20%' is not a measurable increase.",
    ),
    dict(
        statement_id="D044", date="2026-08-06", period_referenced="3Q26",
        event="call", speaker="Ellie Mertz", role="cfo", theme="eligibility",
        quote="Given the strong results that it's delivered, in July, we expanded the types of bookings eligible for Reserve Now, Pay Later.",
        quantity="July 2026", unit="date",
        basis="expansion of eligible booking types",
        scope="not specified", night_weighted="n/a",
        official_or_mirror="mirror", quote_verified="file", source_key="call_2Q26",
        note="Call mirror only, and the new booking types are not named. This is fresh treatment landing inside 3Q26, working against the US anniversary in the same quarter. Its size is unknown, which is the main reason the 3Q26 lap cannot be signed from disclosure alone.",
    ),
    dict(
        statement_id="D045", date="2026-08-06", period_referenced="2Q26",
        event="call", speaker="Ellie Mertz", role="cfo", theme="bundle_contribution",
        quote="First, we continue to see Reserve Now, Pay Later benefit the business. It drove more bookings, longer booking lead times, and contributed to the increase in ADR.",
        quantity="", unit="qualitative", basis="bookings, lead times, ADR",
        scope="global", night_weighted="no",
        official_or_mirror="mirror", quote_verified="file", source_key="call_2Q26",
        note="2Q26 is the first print since 3Q25 with no quantified bundle growth contribution. Management updated two of the three features qualitatively and dropped the points figure.",
    ),
    dict(
        statement_id="D046", date="2026-08-06", period_referenced="2Q26",
        event="call", speaker="Ellie Mertz", role="cfo", theme="rebooking",
        quote="Now, beyond the immediate uplift in nights booked, we believe this provides a longer-term competitive benefit, enabling hosts to lock in earlier calendar share and better aligning our payment options with guest preferences.",
        quantity="", unit="qualitative", basis="calendar share held by hosts",
        scope="global", night_weighted="no",
        official_or_mirror="mirror", quote_verified="file", source_key="call_2Q26",
        note="'Lock in earlier calendar share' is the mechanism by which an RNPL cancellation does not return the night to the market immediately; it also supports the newsroom's claim that hosts have time to secure a replacement booking.",
    ),
    dict(
        statement_id="D047", date="2026-08-06", period_referenced="2Q26",
        event="call", speaker="Ellie Mertz", role="cfo", theme="simplified_fees",
        quote="Approximately half of our active listings are now subject to the single service fee.",
        quantity="~50%", quantity_num_low=50, quantity_num_high=50,
        unit="percent", basis="share of active listings on the single service fee",
        scope="global supply", night_weighted="no",
        official_or_mirror="mirror", quote_verified="file", source_key="call_2Q26",
        note="Call only. Supply on the single fee roughly doubled from 1Q26 to 2Q26 and is guided to the whole base by year-end, so the fee leg of the bundle is still ramping while its 2025 tranche laps. The two offset inside the same quarter.",
    ),
    dict(
        statement_id="D048", date="2026-08-06", period_referenced="2Q26",
        event="letter", speaker="Airbnb (shareholder letter)", role="company",
        theme="cancellation_policy",
        quote="Updated cancellation policies: We migrated eligible listings from Strict to Firm cancellation policies, helping hosts attract more bookings.",
        quantity="", unit="qualitative", basis="host cancellation policy mix",
        scope="eligible listings", night_weighted="n/a",
        official_or_mirror="official", quote_verified="file", source_key="letter_2Q26",
        note="A 2026 cancellation-policy change that PR #32 does not model. Neither Strict nor Firm is flexible or moderate, so this migration does not by itself enlarge the RNPL-eligible pool, but it does raise the platform-wide refundable share and therefore the cancellation rate independently of RNPL. It is a confound for attributing any 2026 cancellation-rate rise to RNPL.",
    ),
    dict(
        statement_id="D049", date="2026-08-06", period_referenced="2Q26",
        event="letter", speaker="Airbnb (shareholder letter)", role="company",
        theme="take_rate",
        quote="Factors impacting the Q2 2026 take rate included FX and the timing of when guests booked their travel and when guests stayed-a dynamic that reflects the growth of Reserve Now, Pay Later, which has",
        quantity="13.2%", quantity_num_low=13.2, quantity_num_high=13.2,
        unit="percent", basis="implied take rate, revenue over GBV",
        scope="global", night_weighted="no",
        official_or_mirror="official", quote_verified="file", source_key="letter_2Q26",
        note="Official confirmation that RNPL widens the gap between the booking quarter and the stay quarter enough to move the reported take rate. If the booking-to-stay wedge is large enough to show in take rate, it is large enough to move cancellations across reported quarters.",
    ),
    dict(
        statement_id="D050", date="2026-08-06", period_referenced="FY26",
        event="call", speaker="Ellie Mertz", role="cfo", theme="take_rate",
        quote="For the full year, we expect our implied take rate to be relatively flat compared to 2025, accounting for the timing of bookings versus check-in with Reserve Now, Pay Later, as well as higher customer incentives related to new businesses during 2026.",
        quantity="flat y/y", unit="qualitative", basis="FY26 implied take rate",
        scope="global", night_weighted="no",
        official_or_mirror="mirror", quote_verified="file", source_key="call_2Q26",
        note="Reverses the 1Q26 guidance of modest take-rate upside, and names RNPL booking-versus-check-in timing as one of the two reasons. Logged in the main tree as data/processed/overnight/03_forward_claims.csv rows C076 and C080.",
    ),
    dict(
        statement_id="D051", date="2026-08-06", period_referenced="2Q26",
        event="letter", speaker="Airbnb (shareholder letter)", role="company",
        theme="unearned_fees",
        quote="Absent the impact of Reserve Now, Pay Later bookings, which defer guest payments from the time of booking closer to the date of stay, we expect that unearned fees would have grown year-over-year.",
        quantity="", unit="qualitative", basis="unearned fees, y/y",
        scope="global", night_weighted="no",
        official_or_mirror="official", quote_verified="file", source_key="letter_2Q26",
        note="2Q26 unearned fees -0.9% y/y against GBV +15.7%. Note the 1Q26 version of this sentence covered unearned fees and FCF; the 2Q26 version covers unearned fees only.",
    ),
    dict(
        statement_id="D052", date="2026-08-06", period_referenced="3Q26",
        event="letter", speaker="Airbnb (shareholder letter)", role="company",
        theme="guide",
        quote="We expect year-over-year GBV growth to be in the mid teens, driven by low double-digit growth in Nights and Seats Booked and a moderate increase in ADR due to mix shift and price appreciation.",
        quantity="low double digit nights", quantity_num_low=10, quantity_num_high=12,
        unit="percent", basis="3Q26 reported nights and seats booked growth guide",
        scope="global", night_weighted="yes",
        official_or_mirror="official", quote_verified="file", source_key="letter_2Q26",
        note="Issued 6 August 2026 with July in hand, and with the July eligibility expansion already live. The 10 to 12 reading of 'low double digits' is a researcher mapping, not a company range.",
    ),
    dict(
        statement_id="D053", date="2026-08-06", period_referenced="2Q26",
        event="call", speaker="Brian Chesky", role="ceo", theme="relative_size",
        quote="On pricing, I think this is one of the biggest single levers for growth that we have. I think it's significantly greater than Reserve Now, Pay Later. If you want to just put it in perspective, it is, I don't know, I don't want to say a multiple, but many multiples bigger than RNPL.",
        quantity="many multiples", unit="qualitative",
        basis="relative growth contribution, pricing roadmap versus RNPL",
        scope="global", night_weighted="no",
        official_or_mirror="mirror", quote_verified="file", source_key="call_2Q26",
        note="Management's own sizing puts RNPL well below the AI pricing work. Evidence that the 2027 story is not mainly an RNPL lap.",
    ),

    # ---------------- Filings ----------------
    dict(
        statement_id="D054", date="2026-02-12", period_referenced="FY25",
        event="10-K", speaker="Airbnb (Form 10-K FY2025)", role="company",
        theme="kpi_definition",
        quote="For example, a booking made on February 15 would be reflected in Nights and Seats Booked for our quarter ended March 31. If, in the example, the booking were canceled on May 15, Nights and Seats Booked would be reduced by the cancellation for our quarter ended June 30.",
        quantity="", unit="definition",
        basis="transaction-period recognition of bookings and cancellations",
        scope="global KPI", night_weighted="yes",
        official_or_mirror="official", quote_verified="file", source_key="10k_FY2025",
        note="The definitional basis for the whole cohort exercise. A cancellation reduces the quarter in which it occurs, not the quarter of the original booking.",
    ),
    dict(
        statement_id="D055", date="2026-02-12", period_referenced="FY25",
        event="10-K", speaker="Airbnb (Form 10-K FY2025)", role="company",
        theme="unearned_fees",
        quote="Seasonality in GBV also affects Free Cash Flow (\"FCF\"). Higher GBV in the first half of the year typically results in increased unearned fees and higher FCF. During the third quarter, GBV is typically lower and check-ins reach their peak, resulting in decreased unearned fees.",
        quantity="", unit="qualitative", basis="normal seasonal path of unearned fees",
        scope="global", night_weighted="no",
        official_or_mirror="official", quote_verified="file", source_key="10k_FY2025",
        note="The baseline against which D038 must be scored. Unearned fees normally fall sequentially in Q3; management's RNPL claim is that RNPL pushes them up relative to that path. The test is therefore a y/y change in the Q3 level, not a sequential direction.",
    ),
    dict(
        statement_id="D056", date="2026-02-12", period_referenced="FY25",
        event="10-K", speaker="Airbnb (Form 10-K FY2025)", role="company",
        theme="backlog",
        quote="unbilled amounts for confirmed bookings under the terms of our payment programs (Pay Less Upfront and Reserve Now, Pay Later); and",
        quantity="", unit="qualitative",
        basis="FX exposure line naming the unbilled RNPL booking balance",
        scope="global", night_weighted="no",
        official_or_mirror="official", quote_verified="file", source_key="10k_FY2025",
        note="Proof that Airbnb measures and hedges a confirmed-but-unbilled RNPL balance. That balance is the live RNPL exposure the materiality arithmetic needs, and it is never disclosed. It is the single highest-value IR ask.",
    ),
    dict(
        statement_id="D057", date="2026-08-06", period_referenced="2Q26",
        event="10-Q", speaker="Airbnb (Form 10-Q 2Q26)", role="company",
        theme="unearned_fees",
        quote="Seasonality in GBV also affects FCF. Unearned fees typically rise when GBV rises since guests pay at the time of booking. As such, FCF is typically highest in the first quarter and lowest in the fourth quarter. However, increasing adoption of RNPL, which shifts payment and unearned fees closer to the date of stay, is changing the typical seasonal dynamics between GBV and FCF.",
        quantity="", unit="qualitative",
        basis="seasonal relationship between GBV and unearned fees",
        scope="global", night_weighted="no",
        official_or_mirror="official", quote_verified="file", source_key="10q_2Q26",
        note="Audited-filing confirmation that the payment-timing shift is large enough to break the historical seasonal relationship, which is the same break Jessie's backlog-conversion table measures at about +4 points in 1Q26 and 2Q26.",
    ),
    dict(
        statement_id="D058", date="2026-08-06", period_referenced="1H26",
        event="10-Q", speaker="Airbnb (Form 10-Q 2Q26)", role="company",
        theme="unearned_fees",
        quote="This reflected unearned fees growing at a rate less than the GBV growth rate during the six months ended June 30, 2026, compared to the same period in the prior year, which was primarily due to the increased guest adoption of our flexible payment options, which allow guests to pay closer to check-in dates rather than at time of booking, shifting the timing of cash collection and its recognition in operating activities. For example, under our RNPL option, payment is collected closer to check-in rather than at booking. Accordingly, unearned fees are not recorded, and operating cash flows are not generated until payment is received.",
        quantity="", unit="qualitative",
        basis="unearned fees growth versus GBV growth, 1H26",
        scope="global", night_weighted="no",
        official_or_mirror="official", quote_verified="file", source_key="10q_2Q26",
        note="States the mechanism precisely: an RNPL booking creates no unearned fee at all until the guest pays. So the unearned-fee line is a direct, if noisy, read on how much of the booked base is still unpaid, which is the population at risk of a payment-deadline cancellation.",
    ),
    dict(
        statement_id="D060", date="2026-02-12", period_referenced="4Q25",
        event="letter", speaker="Airbnb (shareholder letter)", role="company",
        theme="cancellation_policy",
        quote="Updated cancellation policies-In October, we announced new cancellation policies to make it easier for guests to book a stay, even if their plans change. Hosts can now offer free cancellation up to 14 days before check-in under a new Limited policy.",
        quantity="October 2025", unit="date",
        basis="announcement date of the cancellation redesign",
        scope="global", night_weighted="n/a",
        official_or_mirror="official", quote_verified="file", source_key="letter_4Q25",
        note="This dates the cancellation redesign, which PR #32 lists as undisclosed and models on the fee tranche-1 window. The letter puts it in October 2025, global, which vindicates PR #32's timing assumption and closes its caveat 2. It also names the new policy: Limited, free cancellation to 14 days before check-in.",
    ),
    dict(
        statement_id="D059", date="2026-08-06", period_referenced="2Q26",
        event="10-Q", speaker="Airbnb (Form 10-Q 2Q26)", role="company",
        theme="risk_language",
        quote="our expectations regarding future operating performance, including Nights and Seats Booked, Gross Booking Value (\"GBV\"), Average Daily Rate, and GBV per Nights and Seats Booked, and the potential impact of Reserve Now, Pay Later;",
        quantity="", unit="qualitative",
        basis="forward-looking-statement scope",
        scope="global", night_weighted="n/a",
        official_or_mirror="official", quote_verified="file", source_key="10q_2Q26",
        note="RNPL is named as a forward-looking risk to Nights and Seats Booked specifically, which is the KPI the trade is on.",
    ),
]


def main() -> int:
    texts = {}
    for key, rel in SOURCES.items():
        path = MAIN / rel
        if not path.exists():
            print(f"MISSING SOURCE {key}: {path}", file=sys.stderr)
            continue
        texts[key] = to_text(path)

    failures = []
    for row in ROWS:
        row.setdefault("quantity_num_low", "")
        row.setdefault("quantity_num_high", "")
        row["source_file"] = SOURCES.get(row["source_key"], "")
        row["source_url"] = URLS.get(row["source_key"], "")
        row["access_date"] = "2026-09-11"
        if row["quote_verified"] == "file":
            body = texts.get(row["source_key"], "")
            if normalise(row["quote"]) not in body:
                failures.append((row["statement_id"], row["source_key"]))
        for field in FIELDS:
            row.setdefault(field, "")

    if failures:
        for sid, key in failures:
            print(f"QUOTE NOT FOUND VERBATIM: {sid} in {key}", file=sys.stderr)
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in ROWS:
            writer.writerow(row)

    official = sum(1 for r in ROWS if r["official_or_mirror"] == "official")
    mirror = len(ROWS) - official
    quantified = sum(1 for r in ROWS if r["quantity"])
    night_weighted = sum(1 for r in ROWS if r["night_weighted"] == "yes")
    print(f"Wrote {OUT.relative_to(WORKTREE)}: {len(ROWS)} statements.")
    print(f"  official sources {official}, transcript mirror {mirror}")
    print(f"  carry a figure {quantified}, night-weighted basis {night_weighted}")
    print("  all file-sourced quotes verified verbatim against the main tree.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
