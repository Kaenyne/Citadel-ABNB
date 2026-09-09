"""14b. Airbnb nights by length-of-stay bucket: <7, 7-27, 28+ nights.

The question
  Both the ADR model and the nights model need the same object: the share of NIGHTS in
  each stay-length bucket, and its change over time. The ADR model needs it because a
  28-night stay is discounted (host monthly discounts) and a 7-night stay is discounted
  less, so a shift of nights between buckets moves realised ADR with no change in any
  posted price. The nights model needs it because nights per booking (ALOS) is the
  bridge from bookings to nights, and ALOS is nothing but the booking-weighted average
  of the bucket means.

What is disclosed (see 14b_los_disclosures.csv for the quotes)
  (a) 28+ NIGHTS SHARE. "Long-term stays of 28 days or more accounted for X% of GROSS
      NIGHTS BOOKED" -- quarterly 1Q21..1Q24 (24, 19, 20, 22 / 21, 19, 20, 21 /
      18, 18, 18, 19 / 17), plus a retrospective 2019 baseline (1Q19 13, 2Q19 13,
      3Q19 14, 4Q19 16, FY19 14).  Discontinued from the 2Q24 letter onward.
      2Q21 (19%) was given ONLY on the call, not in the letter, which is why the repo's
      letter-sourced KPI panel has a hole there; it is patched here.
  (b) 7+ NIGHTS SHARE.  "Approximately X% of gross nights booked were from stays of at
      least seven nights" -- quarterly 1Q21..2Q23 (50, ~49, 45, 47 / 48, 45, ~45, ~46 /
      ~45, ~45).  Discontinued after the 2Q23 letter.
      THIS IS THE KEY INPUT AND IT IS EASY TO MISS: where (a) and (b) overlap
      (1Q21-2Q23) the THREE-BUCKET NIGHTS SPLIT IS FULLY DISCLOSED and needs no
      assumption at all:  s1 = 1 - s7plus,  s2 = s7plus - s28,  s3 = s28.
  (c) ALOS -- "average nights per booking, excluding experiences" -- annual only,
      2020-2025, global and by region, from the 10-K.  Global 4.1, 4.1, 4.1, 3.9, 3.8,
      3.7.  Bookings themselves are never disclosed.
  (d) Sub-mix of the long tail: "roughly a quarter of our nights booked for long-term
      stays were for trip durations of three months or longer" (3Q23, 4Q23 letters;
      ~25% in Jun-2023 vs 18% in Apr-2023).  This is the ONLY quantitative handle on
      how long a long-term stay is -- Airbnb has never stated an average LTS length.
  (e) One regional 28+ figure ever published: North America 23% of gross nights booked
      in 3Q24 (3Q24 letter).  It is used below as an out-of-sample test, not an input.

Method
  Notation: s_b = share of NIGHTS in bucket b; m_b = mean nights per booking inside
  bucket b.  Bookings in bucket b are proportional to s_b / m_b, so

      1 / ALOS  =  s1/m1 + s2/m2 + s3/m3            (the ALOS identity)
      s1 + s2 + s3 = 1

  1. TIER A -- DISCLOSED (1Q21..2Q23 quarterly; annual 2021, 2022).  All three nights
     shares come straight from (a) and (b).  No bucket mean is needed for the shares,
     so for these periods the LOS ADR-mix term is assumption-free apart from the price
     ratios.  The ALOS identity is then RUN BACKWARDS to SOLVE the short-bucket mean:
         m1 = s1 / (1/ALOS - s2/m2 - s3/m3)
     which is the reverse of the usual framing and is the reason this build is stronger
     than a pure ALOS decomposition.  m1 comes out at 2.43 (2021) and 2.50 (2022) --
     stable to 0.07 nights across two very different years, and stable to ~0.1 nights
     when m2 is swung 9-13 and m3 is swung 35-60.  CALIBRATED m1 = mean of those.
     Cross-check on a year not used for calibration: 1H23 disclosed s1=0.55, s2=0.27
     against 0.561 / 0.257 solved below.

  2. TIER B -- SOLVED (3Q23, 4Q23, 1Q24; annual 2023).  s28 is disclosed but the 7+
     share is not.  Given ALOS, s3 and (m1, m2, m3), the identity is linear in (s1, s2):
         R = 1/ALOS - s3/m3 ,  S = 1 - s3
         s1 = (R - S/m2) / (1/m1 - 1/m2) ,  s2 = S - s1
     Feasibility (s1, s2 >= 0) requires m1 <= S/R <= m2.  S/R -- the harmonic-mean stay
     of all sub-28-night bookings -- is reported; it moves <0.04 nights when m3 swings
     35 to 60, so it is a near-assumption-free readout.

  3. TIER C -- ALOS-ONLY CARRY (2Q24..4Q25, and 2026 only if an ALOS is supplied).
     After 1Q24 there is no stay-length disclosure of any kind.  One extra assumption
     closes it: phi = s2 / (s1 + s2), the 7-27 share of non-long-term nights, is held at
     its last solved value.  With A = (1-phi)/m1 + phi/m2 and B = 1/m3,
         s3 = (A - 1/ALOS) / (A - B)
     VALIDATION: run on 1Q24 (which is disclosed but excluded from the calibration) this
     returns 17.4% against the disclosed 17%.  That is the whole justification for the
     carry, and it is a single-point test -- these rows stay flagged basis="alos_only".
     What the carry CANNOT do: distinguish a fall in the 28+ share from a shortening of
     ordinary sub-7 stays.  phi assumes that away by construction.  2026 has no
     disclosed ALOS at all, so 1Q26/2Q26 are emitted only under an explicitly flagged
     ALOS extrapolation (--alos-2026), never as a solved period.

  4. BUCKET MEANS.
     m1: SOLVED, 2.47 nights (see tier A).  Reported for contrast: the Inside Airbnb
     booked-run distribution (data/processed/kitchen_wholehome_pooled.csv, 273,522 runs,
     8 US cities, June 2026, capped at 30 nights) is refitted here by maximum entropy on
     its three surviving moments and gives E[L|L<7] = 3.42.  That is ~40% too long, in
     the expected direction: an Inside Airbnb "run" is a contiguous unavailable block,
     so it merges back-to-back bookings and swallows host blocks.  The IA data is used
     for SHAPE (it is what puts m2 near 11), not for level.
     m2: ASSUMED 11.0, range 9-13.  The IA refit gives E[L|7<=L<=27] = 11.08 and the
     bounded segment fits span 9.5-12.1.  Because s2 is disclosed in tier A, m2 does not
     touch the tier-A nights shares at all -- only the booking shares and m1.
     m3: ASSUMED 45.0, range 35-60.  Nothing measures it (IA caps runs at 30 nights).
     Disclosure (d) narrows it: if ~25% of 28+ NIGHTS sit in stays of 90+ nights and 75%
     in 28-89, then m3 = 1/(0.75/n_a + 0.25/n_b) is 43-53 for any plausible (n_a, n_b)
     -- e.g. (40, 120) -> 48, (35, 150) -> 43, (45, 110) -> 53.  45 is central; the
     35-60 grid is carried anyway because the sub-means are themselves guesses.

  5. REGIONS.  There is no regional 28+ series.  Two schemes, both written out
     (column `method`), because they disagree about what regional ALOS variation IS:
       phi_common   : common m1, m2, m3, phi; regional ALOS solves the regional 28+
                      share.  All regional variation is long-tail variation.
                      OUT-OF-SAMPLE TEST: this returns North America 2024 = 22.6%
                      against the only regional figure Airbnb ever published,
                      3Q24 NA = 23%.  Reported in the run log.
                      Infeasible (s3 < 0) wherever regional ALOS is shorter than the
                      global sub-28 harmonic mean -- APAC 2020-2022 on ALOS of 2.7-3.2.
                      Those rows are kept and flagged; the infeasibility is the finding.
       s3_prop_alos : the global 28+ share allocated proportional to regional ALOS and
                      renormalised; the region then solves for its own m1_r.  All
                      regional variation is short-bucket variation.
     CAVEAT written to the output: regional ALOS is disclosed to one decimal, and the
     nights-weighted harmonic mean of the four regional figures implies a global ALOS
     of 3.77 in 2025 against the disclosed 3.7.  That 0.07-night rounding wedge is worth
     ~1.8pp on the solved 28+ share, so the regional levels are softer than the global.

  6. LOS ADR-MIX TERM.  Bucket per-night price ratios r_b (bucket 1 = 1.00 numeraire).
     Mix index M_t = sum_b s_b,t * r_b; the term is 100*(M_t/M_{t-1} - 1) pp of ADR y/y.
     (The linear form sum_b ds_b (r_b - 1) is also written out; same to ~4%.)
     Ratios here are PLACEHOLDERS -- 0.90 for 7-27 and 0.75 for 28+ -- pending measured
     quote-based ratios; swap via --r2/--r3 or the R2/R3 constants.
     Comparison: 07_full_decomposition.csv column of_which_los_pp (+0.27, +0.26, +0.62,
     +0.21, +0.04 for 2021-2025) is a WITHIN-REGION term built from an ASSUMED -0.15
     elasticity of ADR to regional ALOS.  The global mix term here is not the same
     object -- it also carries the part of the global ALOS drift that is geographic mix,
     which that decomposition books under geo_mix_pp.  Both are computed (global, and a
     nights-weighted within-region aggregate) so the comparison is like for like.

Outputs
  data/processed/adr/14b_los_disclosures.csv          every dated stay-length disclosure
  data/processed/adr/14b_los_bucket_shares.csv        shares, booking shares, ALOS check
  data/processed/adr/14b_los_adr_term.csv             LOS ADR-mix term + within-region
  data/processed/adr/14b_los_adr_term_sensitivity.csv the (m1,m2,m3,r2,r3) grid
Run
  py -3.13 analysis/src/adr/14b_los_bucket_shares.py
  py -3.13 analysis/src/adr/14b_los_bucket_shares.py --m3 48 --r3 0.70 --alos-2026 3.6
"""
import argparse
import os

import numpy as np
import pandas as pd
from scipy.optimize import fsolve

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def P(*a):
    return os.path.join(ROOT, *a)


OUT = P("data", "processed", "adr")
REG_ANNUAL = P("data", "processed", "adr", "01_regional_annual.csv")
KPI_Q = P("data", "processed", "overnight", "02_kpi_panel_quarterly.csv")
DECOMP = P("data", "processed", "adr", "07_full_decomposition.csv")
IA_POOL = P("data", "processed", "kitchen_wholehome_pooled.csv")

M2, M2_LO, M2_HI = 11.0, 9.0, 13.0        # 7-27 nights   ASSUMED (Inside Airbnb shape)
M3, M3_LO, M3_HI = 45.0, 35.0, 60.0       # 28+ nights    ASSUMED (nothing measures it)
R2, R3 = 0.966, 0.852                     # 14a measured: host + platform discounts, nights-weighted, ex regulatory-minimum markets
CALIB_YEARS = [2021, 2022]                # years where both 28+ and 7+ cover all 4 qtrs
REGIONS = ["na", "emea", "latam", "apac"]

# ---------------------------------------------------------------- disclosure ledger --
# (period, metric, value, unit, source_doc, source_date, quote, definition_note, path)
L = "data/raw/letters/"
T = "data/raw/transcripts/web/"
F = "data/raw/filings/txt/"
S28 = "long_term_stays_28plus_share_of_gross_nights_booked"
S7 = "stays_7plus_nights_share_of_gross_nights_booked"
DISCLOSURES = [
    ("FY2019", S28, 14.0, "pct_of_nights_booked", "1Q21 shareholder letter", "2021-05",
     "Nearly a quarter (24%) of our nights booked (prior to cancellations and alterations) "
     "in Q1 were not for traditional travel, but for long-term stays (defined as stays of "
     "28 days or more). This was up from 14% in 2019.",
     "GROSS nights BOOKED (prior to cancellations and alterations); retrospective 2019 base",
     L + "1Q21_d476842dex991.htm"),
    ("1Q19", S28, 13.0, "pct_of_nights_booked", "1Q22 shareholder letter", "2022-05",
     "Long-term stays accounted for 21% of gross nights booked in Q1 2022, up from 13% in "
     "Q1 2019 and down from 24% in Q1 2021.", "GROSS nights BOOKED", L + "1Q22_d711122dex991.htm"),
    ("2Q19", S28, 13.0, "pct_of_nights_booked", "2Q22 shareholder letter", "2022-08",
     "Long-term stays accounted for 19% of gross nights booked in Q2 2022, up from 13% in "
     "Q2 2019 and flat with Q2 2021.", "GROSS nights BOOKED", L + "2Q22_d353427dex991.htm"),
    ("3Q19", S28, 14.0, "pct_of_nights_booked", "3Q21 shareholder letter", "2021-11",
     "Long-term stays accounted for 20% of gross nights booked in Q3 2021, up from 14% in "
     "Q3 2019.", "GROSS nights BOOKED", L + "3Q21_d245727dex991.htm"),
    ("4Q19", S28, 16.0, "pct_of_nights_booked", "4Q21 shareholder letter", "2022-02",
     "Long-term stays accounted for 22% of gross nights booked in Q4 2021, up from 16% in "
     "Q4 2019.", "GROSS nights BOOKED", L + "4Q21_d251410dex991.htm"),
    ("4Q20", S28, np.nan, "pct_of_nights_booked", "4Q20 shareholder letter", "2021-02",
     "we have seen steady growth in our long-term stays (stays of at least 28 nights). This "
     "continued in Q4 2020, with solid growth in nights booked ... relative to Q4 2019.",
     "QUALITATIVE ONLY -- no share disclosed for any 2020 quarter",
     L + "4Q20_d147144dex991.htm"),
    ("1Q21", S28, 24.0, "pct_of_nights_booked", "1Q21 shareholder letter", "2021-05",
     "In Q1 2021, long-term stays represented 24% of nights booked (prior to cancellations "
     "and alterations).", "GROSS nights BOOKED (longhand phrasing, this quarter only)",
     L + "1Q21_d476842dex991.htm"),
    ("2Q21", S28, 19.0, "pct_of_nights_booked", "2Q21 earnings call (NOT in the letter)",
     "2021-08",
     "stays of 28 days or longer remain being one of the largest and strongest growing parts "
     "of our business. That was 19% of our nights booked in Q2, following being 24% in Q1.",
     "GROSS nights BOOKED -- CALL ONLY; the repo's letter-sourced KPI panel omits this "
     "quarter, so it is patched in here", T + "2Q21.html"),
    ("3Q21", S28, 20.0, "pct_of_nights_booked", "3Q21 shareholder letter", "2021-11",
     "Long-term stays accounted for 20% of gross nights booked in Q3 2021.",
     "GROSS nights BOOKED", L + "3Q21_d245727dex991.htm"),
    ("4Q21", S28, 22.0, "pct_of_nights_booked", "4Q21 shareholder letter", "2022-02",
     "long-term stays of 28 nights or more remained our fastest growing category by trip "
     "length and accounted for 22% of gross nights booked in Q4.",
     "GROSS nights BOOKED", L + "4Q21_d251410dex991.htm"),
    ("1Q22", S28, 21.0, "pct_of_nights_booked", "1Q22 shareholder letter", "2022-05",
     "Long-term stays accounted for 21% of gross nights booked in Q1 2022.",
     "GROSS nights BOOKED", L + "1Q22_d711122dex991.htm"),
    ("2Q22", S28, 19.0, "pct_of_nights_booked", "2Q22 shareholder letter", "2022-08",
     "Long-term stays accounted for 19% of gross nights booked in Q2 2022.",
     "GROSS nights BOOKED", L + "2Q22_d353427dex991.htm"),
    ("3Q22", S28, 20.0, "pct_of_nights_booked", "3Q22 shareholder letter", "2022-11",
     "long-term stays of 28 days or more accounted for 20% of gross nights booked in "
     "Q3 2022, stable with Q3 2021.", "GROSS nights BOOKED", L + "3Q22_d408297dex991.htm"),
    ("4Q22", S28, 21.0, "pct_of_nights_booked", "4Q22 shareholder letter", "2023-02",
     "long-term stays of 28 days or more accounted for 21% of gross nights booked in "
     "Q4 2022, stable with Q4 2021.", "GROSS nights BOOKED", L + "4Q22_d451233dex991.htm"),
    ("1Q23", S28, 18.0, "pct_of_nights_booked", "1Q23 shareholder letter", "2023-05",
     "long-term stays of 28 days or more accounted for 18% of gross nights booked, a "
     "decrease from 21% in Q4 2022 as growth in short-term stays accelerated.",
     "GROSS nights BOOKED", L + "1Q23_d453262dex991.htm"),
    ("2Q23", S28, 18.0, "pct_of_nights_booked", "2Q23 shareholder letter", "2023-08",
     "long-term stays of 28 days or more accounted for 18% of gross nights booked, "
     "relatively consistent with Q1 2023 and Q2 2022.",
     "GROSS nights BOOKED ('total nights booked' on the call -- same number, looser wording)",
     L + "2Q23_d446942dex991.htm"),
    ("3Q23", S28, 18.0, "pct_of_nights_booked", "3Q23 shareholder letter", "2023-11",
     "long-term stays of 28 days or more remained steadfast, accounting for 18% of gross "
     "nights booked.", "GROSS nights BOOKED", L + "3Q23_d481318dex991.htm"),
    ("4Q23", S28, 19.0, "pct_of_nights_booked", "4Q23 shareholder letter", "2024-02",
     "long-term stays of 28 days accounted for 19% of gross nights booked, up slightly from "
     "the 18% level seen in Q3 2023.",
     "GROSS nights BOOKED ('or more' dropped -- typo, definition unchanged)",
     L + "4Q23_d646462dex991.htm"),
    ("1Q24", S28, 17.0, "pct_of_nights_booked", "1Q24 shareholder letter", "2024-05",
     "Trip Length -- In Q1 2024, long-term stays of 28 days or more accounted for 17% of "
     "gross nights booked, compared to 18% in Q1 2023.",
     "GROSS nights BOOKED -- LAST GLOBAL DISCLOSURE; the Trip Length section is dropped "
     "from every letter thereafter", L + "1Q24_d813800dex991.htm"),
    ("2Q24", S28, 17.0, "pct_of_nights_booked", "2Q24 earnings call (transcript only)",
     "2024-08",
     "we haven't really expanded beyond our core business, and we do have long-term stays, "
     "which are 17% of nights, but we haven't done very much.",
     "CALL ONLY, unaudited prose; the web transcript garbles this as '70% a night' -- use "
     "the FactSet corrected version", "data/raw/regulatory/transcripts/2024-Q2.json"),
    ("3Q24", "long_term_stays_28plus_share_NORTH_AMERICA", 23.0, "pct_of_nights_booked",
     "3Q24 shareholder letter", "2024-11",
     "long-term stays comprised 23% of gross nights booked in North America during Q3 2024, "
     "largely unchanged from the prior-year period.",
     "ONLY regional 28+ figure ever published; LAST quantified LTS share in any letter. "
     "Used here as an OUT-OF-SAMPLE TEST of the regional solve, not as an input.",
     L + "3Q24_d886752dex991.htm"),
    ("1Q21", S7, 50.0, "pct_of_nights_booked", "1Q21 shareholder letter", "2021-05",
     "50% of nights booked (prior to cancellations and alterations) were from stays of at "
     "least seven nights in Q1.", "GROSS nights BOOKED", L + "1Q21_d476842dex991.htm"),
    ("2Q21", S7, 49.0, "pct_of_nights_booked", "2Q21 shareholder letter", "2021-08",
     "Overall, nearly 50% of gross nights booked were from stays of at least seven nights "
     "in Q2 2021.", "GROSS nights BOOKED -- 'nearly 50%', coded 49 (APPROX)",
     L + "2Q21_d212971dex991.htm"),
    ("3Q21", S7, 45.0, "pct_of_nights_booked", "3Q21 shareholder letter", "2021-11",
     "Overall, 45% of gross nights booked were from stays of at least seven nights in "
     "Q3 2021.", "GROSS nights BOOKED", L + "3Q21_d245727dex991.htm"),
    ("4Q21", S7, 47.0, "pct_of_nights_booked", "4Q21 shareholder letter", "2022-02",
     "Overall, 47% of gross nights booked were from stays of at least seven nights in "
     "Q4 2021.", "GROSS nights BOOKED", L + "4Q21_d251410dex991.htm"),
    ("1Q22", S7, 48.0, "pct_of_nights_booked", "1Q22 shareholder letter", "2022-05",
     "Overall, 48% of gross nights booked were from stays of at least seven nights in "
     "Q1 2022.", "GROSS nights BOOKED", L + "1Q22_d711122dex991.htm"),
    ("2Q22", S7, 45.0, "pct_of_nights_booked", "2Q22 shareholder letter", "2022-08",
     "Overall, 45% of gross nights booked were from stays of at least seven nights in "
     "Q2 2022.", "GROSS nights BOOKED", L + "2Q22_d353427dex991.htm"),
    ("3Q22", S7, 45.0, "pct_of_nights_booked", "3Q22 shareholder letter", "2022-11",
     "Overall, approximately 45% of gross nights booked were from stays of at least seven "
     "nights in Q3 2022.", "GROSS nights BOOKED (APPROX)", L + "3Q22_d408297dex991.htm"),
    ("4Q22", S7, 46.0, "pct_of_nights_booked", "4Q22 shareholder letter", "2023-02",
     "Overall, approximately 46% of gross nights booked in Q4 2022 were from stays of at "
     "least seven nights.", "GROSS nights BOOKED (APPROX)", L + "4Q22_d451233dex991.htm"),
    ("1Q23", S7, 45.0, "pct_of_nights_booked", "1Q23 shareholder letter", "2023-05",
     "Overall, approximately 45% of gross nights booked in Q1 2023 were from stays of at "
     "least seven nights.", "GROSS nights BOOKED (APPROX)", L + "1Q23_d453262dex991.htm"),
    ("2Q23", S7, 45.0, "pct_of_nights_booked", "2Q23 shareholder letter", "2023-08",
     "Overall, approximately 45% of gross nights booked in Q2 2023 were from stays of at "
     "least seven nights.",
     "GROSS nights BOOKED (APPROX) -- LAST 7+ DISCLOSURE; discontinued thereafter",
     L + "2Q23_d446942dex991.htm"),
    ("4Q23", S7, 40.0, "pct_of_nights_booked", "4Q23 earnings call", "2024-02",
     "19% of our nights are monthly stays, and more than 40% are weekly.",
     "CALL ONLY, 'more than 40%' -- a LOWER BOUND, not used in the solve",
     "data/raw/regulatory/transcripts/2023-Q4.json"),
    ("2Q23", "three_month_plus_share_of_long_term_stay_nights", 25.0, "pct_of_LTS_nights",
     "2Q23 shareholder letter", "2023-08",
     "In June, nights booked for three months or longer grew to approximately 25% of total "
     "monthly stays, compared to 18% in April.",
     "share of 28+ nights that sit in 90+ night stays -- the ONLY handle on m3",
     L + "2Q23_d446942dex991.htm"),
    ("3Q23", "three_month_plus_share_of_long_term_stay_nights", 25.0, "pct_of_LTS_nights",
     "3Q23 shareholder letter", "2023-11",
     "roughly a quarter of our nights booked for long-term stays were for trip durations of "
     "three months or longer -- with nights booked for trips over three months increasing "
     "almost 20% compared to Q3 2022.", "handle on m3: implies m3 ~ 43-53 nights",
     L + "3Q23_d481318dex991.htm"),
    ("4Q23", "three_month_plus_share_of_long_term_stay_nights", 25.0, "pct_of_LTS_nights",
     "4Q23 shareholder letter", "2024-02",
     "roughly a quarter of our nights booked for long-term stays were for trip durations of "
     "three months or longer.", "handle on m3", L + "4Q23_d646462dex991.htm"),
    ("FY2021", "average_length_of_long_term_stay", np.nan, "nights",
     "all sources", "n/a",
     "NOT DISCLOSED. Airbnb has never stated an average length for long-term stays. The "
     "closest is the 3-month-or-longer share of LTS nights and the 4Q21 datapoint that "
     "~175,000 guests booked stays of three months or longer in 2021.",
     "m3 is therefore an ASSUMPTION (45 central, 35-60 carried)", ""),
    ("FY2021", "average_trip_length_change", 15.0, "pct_change_2y",
     "4Q21 shareholder letter", "2022-02",
     "Over the last two years, we have seen the average trip length increase by "
     "approximately 15%, with stays of more than 7 days now representing nearly half of all "
     "gross nights booked.", "directional only", L + "4Q21_d251410dex991.htm"),
    ("2Q24", "ALOS_commentary", np.nan, "", "2Q24 earnings call", "2024-08",
     "the average trip length has gone down, but that is really a function of the mix shift "
     "between short-term rentals growing more quickly than long-term rentals, less so people "
     "choosing a three-day trip versus a four-day trip.",
     "management's own attribution: the ALOS drift is BUCKET MIX, not within-bucket "
     "shortening -- which is exactly the assumption the tier-C carry makes",
     "data/raw/regulatory/transcripts/2024-Q2.json"),
    ("4Q21", "ADR_effect_of_long_term_stays", np.nan, "", "4Q21 earnings call", "2022-02",
     "the long-term stays ... have moderately lower take rate ... and the ADRs ... are just "
     "staying for longer, because Hosts often offer a discount. ... long-term stays are "
     "dilutive on the ADR as the percentage goes up.",
     "management confirms the SIGN of the LOS ADR-mix term but declines to quantify it; the "
     "0.75 / 0.90 price ratios here are placeholders", ""),
    ("2Q26", "trip_length_mix_commentary", np.nan, "", "2Q26 shareholder letter", "2026-08",
     "Growth in short-term stays and entire homes, particularly listings with four or more "
     "bedrooms, continued to outpace long-term stays (trips of 28 days or more) and private "
     "rooms, extending a mix-shift trend we have now seen for over a year.",
     "post-1Q24 the mix shift is confirmed QUALITATIVELY every quarter but never sized",
     L + "2Q26_d70413dex991.htm"),
]

# quarterly series pulled out of the ledger for the solve
Q28 = {r[0]: r[2] for r in DISCLOSURES if r[1] == S28 and not pd.isna(r[2])
       and len(r[0]) == 4 and r[0][0] in "1234"}
Q7 = {r[0]: r[2] for r in DISCLOSURES if r[1] == S7 and r[0] != "4Q23"}


# ------------------------------------------------------------------ bucket-mean fit --
def maxent_runlen(mean, p_ge3, p_ge7, cap=30):
    """Max-entropy pmf on 1..cap matching mean, P(L>=3), P(L>=7). Returns (k, p)."""
    k = np.arange(1, cap + 1)

    def pmf(x):
        z = x[0] * k + x[1] * (k >= 3) + x[2] * (k >= 7)
        z = z - z.max()
        p = np.exp(z)
        return p / p.sum()

    def eqs(x):
        p = pmf(x)
        return [(k * p).sum() - mean, p[k >= 3].sum() - p_ge3, p[k >= 7].sum() - p_ge7]

    for guess in ([-0.2, 1.0, 0.5], [-0.1, 0.5, 0.5], [-0.3, 2.0, 1.0], [0.0, 0.0, 0.0]):
        sol, _, ier, _ = fsolve(eqs, guess, full_output=True)
        if ier == 1:
            return k, pmf(sol)
    return None, None


def ia_bucket_means():
    """E[L|L<7], E[L|7<=L<=27] from the Inside Airbnb booked-run moments. Shape, not level."""
    rows = []
    for _, r in pd.read_csv(IA_POOL).iterrows():
        k, p = maxent_runlen(r.mean_nights_per_booked_run, r.share_ge3, r.share_ge7)
        if k is None:
            continue
        lo, mid = k < 7, (k >= 7) & (k <= 27)
        rows.append(dict(segment=r.segment, runs=int(r.runs),
                         ia_mean=r.mean_nights_per_booked_run,
                         m1_fit=(k[lo] * p[lo]).sum() / p[lo].sum(),
                         m2_fit=(k[mid] * p[mid]).sum() / p[mid].sum(),
                         ia_nights_share_lt7=(k[lo] * p[lo]).sum() / (k * p).sum()))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------- the solve --
def m1_from_identity(alos, s1, s2, s3, m2, m3):
    """Tier A: all three shares known -> run the ALOS identity backwards for m1."""
    denom = 1.0 / alos - s2 / m2 - s3 / m3
    return s1 / denom if denom > 0 else np.nan


def solve_shares(alos, s3, m1, m2, m3):
    """Tier B: ALOS + 28+ share -> the other two nights shares."""
    R = 1.0 / alos - s3 / m3
    S = 1.0 - s3
    s1 = (R - S / m2) / (1.0 / m1 - 1.0 / m2)
    return s1, S - s1, R, S


def solve_s3_from_alos(alos, phi, m1, m2, m3):
    """Tier C: hold phi = s2/(s1+s2); ALOS alone pins the 28+ share."""
    A = (1 - phi) / m1 + phi / m2
    B = 1.0 / m3
    s3 = (A - 1.0 / alos) / (A - B)
    return s3, (1 - s3) * (1 - phi), (1 - s3) * phi, A


def m1_region_from_alos(alos, s3, phi, m2, m3):
    rhs = (1.0 / alos - s3 / m3) / (1 - s3) - phi / m2
    return (1 - phi) / rhs if rhs > 0 else np.nan


def pack(alos, s1, s2, s3, m1, m2, m3):
    b = np.array([s1 / m1, s2 / m2, s3 / m3])
    tot = b.sum()
    return dict(nights_share_lt7=s1, nights_share_7_27=s2, nights_share_ge28=s3,
                booking_share_lt7=b[0] / tot, booking_share_7_27=b[1] / tot,
                booking_share_ge28=b[2] / tot, alos_input=alos, alos_check=1.0 / tot,
                alos_check_err=1.0 / tot - alos, m1_used=m1, m2_used=m2, m3_used=m3,
                feasible=bool(s1 >= 0 and s2 >= 0 and s3 >= 0 and s1 <= 1))


def mix_index(s1, s2, s3, r2, r3):
    return s1 * 1.0 + s2 * r2 + s3 * r3


def qnum(q):
    return int(q[-2:]) * 4 + int(q[0])


# --------------------------------------------------------------------------- loaders --
def load_inputs():
    ra = pd.read_csv(REG_ANNUAL)[["year", "region", "alos_nights", "nights_m"]]
    kpi = pd.read_csv(KPI_Q)[["quarter", "nights_m", "long_term_stays_share_pct"]].copy()
    kpi["qn"] = kpi.quarter.map(qnum)
    kpi = kpi.sort_values("qn").reset_index(drop=True)
    kpi["year"] = kpi.quarter.str[-2:].astype(int) + 2000
    # patch the ledger over the letter-sourced panel (2Q21 is call-only, hence missing)
    kpi["s28"] = kpi.quarter.map(Q28)
    kpi["s7"] = kpi.quarter.map(Q7)
    kpi["panel_s28"] = kpi.long_term_stays_share_pct
    return ra, kpi


def nights_weighted(kpi, col, year):
    g = kpi[(kpi.year == year) & kpi[col].notna()]
    if len(g) == 0:
        return np.nan, 0
    w = g.nights_m / g.nights_m.sum()
    return float((g[col] * w).sum()) / 100.0, len(g)


def interp_alos_quarterly(ra, kpi, alos_2026=None):
    """Annual ALOS is a full-year average: place it at the year centre and interpolate.
    Ignores ALOS seasonality entirely -- flagged on every quarterly row."""
    tot = ra[ra.region == "total"].sort_values("year")
    xa, ya = list(tot.year.values + 0.5), list(tot.alos_nights.values)
    if alos_2026 is not None:
        xa.append(2026.5)
        ya.append(alos_2026)
    yq = kpi.quarter.str[-2:].astype(int).values + 2000
    qq = kpi.quarter.str[0].astype(int).values
    x = yq + (qq - 0.5) / 4.0
    out = np.interp(x, xa, ya)          # np.interp CLAMPS beyond the last anchor
    out[yq >= 2026] = np.nan if alos_2026 is None else out[yq >= 2026]
    # flat beyond the last annual anchor (mid-2025): 3Q25/4Q25 carry the FY25 level
    return out, x > max(xa)


def build_disclosures(kpi):
    df = pd.DataFrame(DISCLOSURES, columns=["period", "metric", "value", "unit",
                                            "source_doc", "source_date", "quote",
                                            "definition_note", "source_path"])
    panel = kpi.set_index("quarter").panel_s28.to_dict()
    df["repo_panel_value"] = np.where(df.metric == S28, df.period.map(panel), np.nan)
    df["repo_panel_agrees"] = np.where(
        df.metric != S28, "",
        np.where(df.period.map(panel).isna(), "ABSENT FROM PANEL",
                 np.where(df.period.map(panel) == df.value, "yes", "NO")))
    df["repo_panel_source"] = np.where(
        df.metric == S28,
        "data/processed/overnight/02_kpi_panel_quarterly.csv:long_term_stays_share_pct", "")
    return df.sort_values(["metric", "period"])


# ------------------------------------------------------------------------------ main --
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m1", type=float, default=None, help="override the calibrated m1")
    ap.add_argument("--m2", type=float, default=M2)
    ap.add_argument("--m3", type=float, default=M3)
    ap.add_argument("--r2", type=float, default=R2)
    ap.add_argument("--r3", type=float, default=R3)
    ap.add_argument("--alos-2026", type=float, default=None,
                    help="ALOS to ASSUME for 2026 (not disclosed); enables 1Q26/2Q26 rows")
    a = ap.parse_args()
    m2, m3, r2, r3 = a.m2, a.m3, a.r2, a.r3

    ra, kpi = load_inputs()
    kpi["alos_interp"], kpi["alos_flat"] = interp_alos_quarterly(ra, kpi, a.alos_2026)
    build_disclosures(kpi).to_csv(os.path.join(OUT, "14b_los_disclosures.csv"), index=False)

    tot = ra[ra.region == "total"].sort_values("year")
    alos_a = dict(zip(tot.year.astype(int), tot.alos_nights))
    if a.alos_2026 is not None:
        alos_a[2026] = a.alos_2026

    # ---- annual disclosed shares -----------------------------------------------------
    ann = {}
    for y in sorted(set(kpi.year)):
        s28, n28 = nights_weighted(kpi, "s28", y)
        s7, n7 = nights_weighted(kpi, "s7", y)
        ann[y] = dict(s28=s28, n28=n28, s7=s7, n7=n7)

    # ---- TIER A: calibrate m1 on years where both series cover all four quarters ------
    calib = []
    for y in CALIB_YEARS:
        d = ann[y]
        if d["n28"] != 4 or d["n7"] != 4 or y not in alos_a:
            continue
        s1, s2, s3 = 1 - d["s7"], d["s7"] - d["s28"], d["s28"]
        calib.append(dict(year=y, alos=alos_a[y], s1=s1, s2=s2, s3=s3,
                          m1=m1_from_identity(alos_a[y], s1, s2, s3, m2, m3)))
    calib = pd.DataFrame(calib)
    m1 = a.m1 if a.m1 is not None else float(calib.m1.mean())

    ia = ia_bucket_means()
    print("Inside Airbnb booked-run bucket means (max-entropy refit of 3 moments) --")
    print("SHAPE ONLY: an IA 'run' merges back-to-back bookings and host blocks, so the")
    print("level is biased long. Compare m1_fit against the SOLVED m1 = %.3f below.\n" % m1)
    print(ia.round(3).to_string(index=False))
    print("\n--- m1 CALIBRATION (tier A: all three nights shares disclosed) ---")
    print(calib.round(4).to_string(index=False))
    print("m1 calibrated = %.3f nights (m2=%.1f, m3=%.1f assumed)" % (m1, m2, m3))
    sw = []
    for mm2 in [M2_LO, m2, M2_HI]:
        for mm3 in [M3_LO, m3, M3_HI]:
            v = [m1_from_identity(r.alos, r.s1, r.s2, r.s3, mm2, mm3)
                 for _, r in calib.iterrows()]
            sw.append((mm2, mm3, float(np.mean(v))))
    print("m1 sensitivity over m2 in [%s,%s] x m3 in [%s,%s]: %.3f to %.3f nights"
          % (M2_LO, M2_HI, M3_LO, M3_HI, min(x[2] for x in sw), max(x[2] for x in sw)))
    print("m3 implied by the '~25%% of LTS nights are 3 months or longer' disclosure: "
          "43-53 nights for plausible sub-means; %.0f used.\n" % m3)

    rows = []

    # ---- GLOBAL ANNUAL ---------------------------------------------------------------
    phi_last, last_year = None, None
    for y in sorted(alos_a):
        d, alos = ann.get(y, dict(s28=np.nan, n28=0, s7=np.nan, n7=0)), alos_a[y]
        if pd.isna(alos):
            continue
        if d["n7"] == 4 and d["n28"] == 4:                                    # tier A
            s1, s2, s3 = 1 - d["s7"], d["s7"] - d["s28"], d["s28"]
            m1u = m1_from_identity(alos, s1, s2, s3, m2, m3)
            e = pack(alos, s1, s2, s3, m1u, m2, m3)
            e.update(basis="disclosed (28+ AND 7+ shares both disclosed for all 4 quarters; "
                           "nights shares need NO bucket-mean assumption)",
                     tier="A_disclosed", s28_basis="disclosed x4",
                     s7_basis="disclosed x4", short_harmonic_mean=np.nan)
        elif d["n28"] >= 3:                                                    # tier B
            s3 = d["s28"]
            s1, s2, R, S = solve_shares(alos, s3, m1, m2, m3)
            e = pack(alos, s1, s2, s3, m1, m2, m3)
            e.update(basis="solved (28+ disclosed; 7+ NOT disclosed; s1/s2 split from the "
                           "ALOS identity with calibrated m1)",
                     tier="B_solved", s28_basis="disclosed x%d" % d["n28"],
                     s7_basis="disclosed x%d (not used)" % d["n7"],
                     short_harmonic_mean=S / R)
        elif phi_last is not None:                                             # tier C
            s3, s1, s2, A = solve_s3_from_alos(alos, phi_last, m1, m2, m3)
            e = pack(alos, s1, s2, s3, m1, m2, m3)
            e.update(basis="alos_only (no stay-length disclosure; phi held at its %d value)"
                           % last_year,
                     tier="C_alos_only", s28_basis="SOLVED from ALOS",
                     s7_basis="SOLVED from ALOS", short_harmonic_mean=1.0 / A)
        else:
            continue
        if a.alos_2026 is not None and y == 2026:
            e["basis"] += " -- ALOS ITSELF IS AN ASSUMPTION (2026 not disclosed)"
        e.update(period=str(y), freq="annual", region="total", method="global",
                 phi=e["nights_share_7_27"] / (1 - e["nights_share_ge28"]))
        rows.append(e)
        if e["tier"] in ("A_disclosed", "B_solved"):
            phi_last, last_year = e["phi"], y

    # ---- GLOBAL QUARTERLY -------------------------------------------------------------
    phi_q, last_q = None, None
    for _, r in kpi.iterrows():
        alos = r.alos_interp
        if pd.isna(alos):
            continue
        aflag = ("ALOS INTERPOLATED from annual (ignores ALOS seasonality)"
                 if r.year <= 2025 else "ALOS EXTRAPOLATED -- 2026 ALOS NOT DISCLOSED")
        if r.alos_flat and r.year <= 2025:
            aflag = ("ALOS HELD FLAT at the FY2025 level -- beyond the last annual anchor "
                     "(mid-2025), so this quarter carries no new ALOS information")
        if pd.notna(r.s7) and pd.notna(r.s28):                                 # tier A
            s1, s2, s3 = 1 - r.s7 / 100, (r.s7 - r.s28) / 100, r.s28 / 100
            m1u = m1_from_identity(alos, s1, s2, s3, m2, m3)
            e = pack(alos, s1, s2, s3, m1u if m1u == m1u else m1, m2, m3)
            e.update(basis="disclosed (28+ AND 7+ both disclosed; shares need NO assumption. "
                           "%s -- affects only the implied m1, not the shares)" % aflag,
                     tier="A_disclosed", s28_basis="disclosed", s7_basis="disclosed",
                     short_harmonic_mean=np.nan)
        elif pd.notna(r.s28):                                                  # tier B
            s3 = r.s28 / 100
            s1, s2, R, S = solve_shares(alos, s3, m1, m2, m3)
            e = pack(alos, s1, s2, s3, m1, m2, m3)
            e.update(basis="solved (28+ disclosed; 7+ not; %s)" % aflag, tier="B_solved",
                     s28_basis="disclosed", s7_basis="not disclosed",
                     short_harmonic_mean=S / R)
        elif phi_q is not None:                                                # tier C
            s3, s1, s2, A = solve_s3_from_alos(alos, phi_q, m1, m2, m3)
            e = pack(alos, s1, s2, s3, m1, m2, m3)
            e.update(basis="alos_only (28+ discontinued after 1Q24; phi held at %s; %s)"
                           % (last_q, aflag), tier="C_alos_only",
                     s28_basis="SOLVED from ALOS", s7_basis="SOLVED from ALOS",
                     short_harmonic_mean=1.0 / A)
        else:
            continue
        e.update(period=r.quarter, freq="quarterly", region="total", method="global",
                 nights_m=r.nights_m,
                 phi=e["nights_share_7_27"] / (1 - e["nights_share_ge28"]))
        rows.append(e)
        if e["tier"] in ("A_disclosed", "B_solved"):
            phi_q, last_q = e["phi"], r.quarter

    # ---- REGIONAL ANNUAL --------------------------------------------------------------
    glob = {x["period"]: x for x in rows if x["freq"] == "annual" and x["region"] == "total"}
    agg_check = []
    for y, g in ra[ra.region.isin(REGIONS)].groupby("year"):
        key = str(int(y))
        if key not in glob:
            continue
        phi_y, s3_g = glob[key]["phi"], glob[key]["nights_share_ge28"]
        w = (g.nights_m / g.nights_m.sum()).values
        alos_arith = float((g.alos_nights.values * w).sum())
        agg_check.append(dict(year=key, alos_disclosed_global=glob[key]["alos_input"],
                              alos_implied_from_regions=1.0 / (w / g.alos_nights.values).sum(),
                              note="regional ALOS is rounded to 1dp; the wedge is worth "
                                   "~1.8pp on the solved 28+ share"))
        for _, r in g.iterrows():
            s3, s1, s2, A = solve_s3_from_alos(r.alos_nights, phi_y, m1, m2, m3)
            e = pack(r.alos_nights, s1, s2, s3, m1, m2, m3)
            e.update(period=key, freq="annual", region=r.region, method="phi_common",
                     tier="regional_assumption",
                     basis=("assumed (common m1/m2/m3/phi; regional ALOS solves the regional "
                            "28+ share -- ALL regional variation booked as long-tail)"
                            if e["feasible"] else
                            "INFEASIBLE -- regional ALOS (%.1f) is SHORTER than the global "
                            "sub-28 harmonic mean (%.2f); the region cannot hold a positive "
                            "28+ share on global bucket means" % (r.alos_nights, 1.0 / A)),
                     s28_basis="SOLVED from regional ALOS (never disclosed by region)",
                     s7_basis="SOLVED", short_harmonic_mean=1.0 / A, phi=phi_y,
                     m1_implied_if_s3_zero=m1_region_from_alos(r.alos_nights, 0.0, phi_y, m2, m3))
            rows.append(e)
            s3r = s3_g * r.alos_nights / alos_arith
            m1r = m1_region_from_alos(r.alos_nights, s3r, phi_y, m2, m3)
            s1b, s2b = (1 - s3r) * (1 - phi_y), (1 - s3r) * phi_y
            e2 = pack(r.alos_nights, s1b, s2b, s3r, m1r, m2, m3)
            e2.update(period=key, freq="annual", region=r.region, method="s3_prop_alos",
                      tier="regional_assumption",
                      basis="assumed (28+ share allocated PROPORTIONAL TO REGIONAL ALOS and "
                            "renormalised to the global share; regional m1 solves -- ALL "
                            "regional variation booked as short-bucket)",
                      s28_basis="ALLOCATED from global (assumption)", s7_basis="assumed",
                      short_harmonic_mean=np.nan, phi=phi_y, m1_implied_if_s3_zero=np.nan)
            rows.append(e2)

    sh = pd.DataFrame(rows)
    ordr = ["period", "freq", "region", "method", "tier", "basis", "s28_basis", "s7_basis",
            "nights_share_lt7", "nights_share_7_27", "nights_share_ge28",
            "booking_share_lt7", "booking_share_7_27", "booking_share_ge28",
            "alos_input", "alos_check", "alos_check_err", "short_harmonic_mean", "phi",
            "m1_used", "m2_used", "m3_used", "m1_implied_if_s3_zero", "feasible", "nights_m"]
    for c in ordr:
        if c not in sh.columns:
            sh[c] = np.nan
    sh = sh[ordr]
    sh["_s"] = sh.freq.map({"annual": 0, "quarterly": 1})
    sh["_q"] = [qnum(p) if f == "quarterly" else int(p) for p, f in zip(sh.period, sh.freq)]
    sh = sh.sort_values(["_s", "region", "method", "_q"]).drop(columns=["_s", "_q"])
    sh.to_csv(os.path.join(OUT, "14b_los_bucket_shares.csv"), index=False)

    # ---- VALIDATIONS -----------------------------------------------------------------
    print("--- OUT-OF-SAMPLE TESTS of the tier-C carry and the regional solve ---")
    ph23 = glob.get("2023", {}).get("phi")
    if ph23:
        alos_1q24 = float(kpi.loc[kpi.quarter == "1Q24", "alos_interp"].iloc[0])
        s3_hat = solve_s3_from_alos(alos_1q24, ph23, m1, m2, m3)[0]
        print("  1Q24 28+ share: carry-forward on ALOS alone -> %.1f%%  vs DISCLOSED 17.0%%"
              % (100 * s3_hat))
        na24 = sh[(sh.period == "2024") & (sh.region == "na") & (sh.method == "phi_common")]
        if len(na24):
            print("  North America 2024 28+ share: solved -> %.1f%%  vs the only regional "
                  "figure Airbnb ever published, 3Q24 NA = 23.0%%"
                  % (100 * float(na24.nights_share_ge28.iloc[0])))
    h23 = sh[(sh.period == "2023") & (sh.region == "total") & (sh.freq == "annual")]
    if len(h23):
        print("  1H23 nights shares: solved FY23 -> lt7 %.1f%% / 7-27 %.1f%%  vs DISCLOSED "
              "1Q23+2Q23 -> 55.0%% / 27.0%%"
              % (100 * float(h23.nights_share_lt7.iloc[0]),
                 100 * float(h23.nights_share_7_27.iloc[0])))
    fy24 = sh[(sh.period == "2024") & (sh.region == "total") & (sh.freq == "annual")]
    if len(fy24) and ann.get(2024, {}).get("n28"):
        print("  FY2024 28+ share: ALOS-only carry -> %.1f%%  vs 1H24 DISCLOSED %.1f%% "
              "(1Q24 letter + 2Q24 call). The carry runs ~1pp LOW, so the 2024-25 mix term "
              "below is if anything OVERSTATED."
              % (100 * float(fy24.nights_share_ge28.iloc[0]), 100 * ann[2024]["s28"]))
    print("  regional ALOS aggregation check (rounding wedge):")
    print(pd.DataFrame(agg_check)[["year", "alos_disclosed_global",
                                   "alos_implied_from_regions"]].round(3).to_string(index=False))

    # ---- LOS ADR-MIX TERM ------------------------------------------------------------
    dec = pd.read_csv(DECOMP)[["year", "of_which_los_pp", "adr_yoy_pct"]]
    dec["period"] = dec.year.astype(str)

    def term_series(df, label, lag=1, r2_=r2, r3_=r3):
        M = mix_index(df.nights_share_lt7.values, df.nights_share_7_27.values,
                      df.nights_share_ge28.values, r2_, r3_)
        nan = [np.nan] * lag
        d = lambda v: np.r_[nan, v[lag:] - v[:-lag]]
        return pd.DataFrame(dict(
            scope=label, period=df.period.values, mix_index=M,
            los_mix_pp=np.r_[nan, 100 * (M[lag:] / M[:-lag] - 1)],
            los_mix_pp_linear=100 * (d(df.nights_share_7_27.values) * (r2_ - 1)
                                     + d(df.nights_share_ge28.values) * (r3_ - 1)),
            d_share_lt7_pp=100 * d(df.nights_share_lt7.values),
            d_share_7_27_pp=100 * d(df.nights_share_7_27.values),
            d_share_ge28_pp=100 * d(df.nights_share_ge28.values),
            tier=df.tier.values, basis=df.basis.values))

    gl_a = sh[(sh.freq == "annual") & (sh.region == "total")].sort_values("period")
    gl_q = sh[(sh.freq == "quarterly") & (sh.region == "total")].copy()
    gl_q["qn"] = gl_q.period.map(qnum)
    gl_q = gl_q.sort_values("qn")

    t = term_series(gl_a, "global_annual").merge(
        dec[["period", "of_which_los_pp", "adr_yoy_pct"]], on="period", how="left")
    t["gap_vs_elasticity_pp"] = t.los_mix_pp - t.of_which_los_pp
    tq = term_series(gl_q, "global_quarterly_yoy", lag=4)

    W = ra[ra.region.isin(REGIONS)].pivot(index="year", columns="region", values="nights_m")
    W.index = W.index.astype(int).astype(str)
    Wn = W.div(W.sum(axis=1), axis=0)
    wr, reg_terms = [], []
    for meth in ["phi_common", "s3_prop_alos"]:
        piv = {}
        for reg, g in sh[(sh.freq == "annual") & (sh.region != "total")
                         & (sh.method == meth)].groupby("region"):
            g = g.sort_values("period")
            ts = term_series(g, "region_%s__%s" % (reg, meth))
            # a term spanning an INFEASIBLE endpoint is meaningless -- drop, do not average
            bad = ~g.feasible.values
            ts.loc[bad | np.r_[True, bad[:-1]], "los_mix_pp"] = np.nan
            reg_terms.append(ts)
            piv[reg] = pd.Series(ts.los_mix_pp.values, index=g.period.values)
        Tt = pd.DataFrame(piv)
        Wq = Wn.reindex(Tt.index)[Tt.columns].where(Tt.notna())
        cover = Wq.sum(axis=1)
        agg = (Tt * Wq).sum(axis=1, min_count=1) / cover      # renormalise over feasible regions
        wr.append(pd.DataFrame(dict(scope="within_region_agg__" + meth, period=Tt.index,
                                    los_mix_pp=agg.values, nights_weight_covered=cover.values,
                                    basis="nights-weighted mean of the regional mix terms over "
                                          "the FEASIBLE regions (weights renormalised; see "
                                          "nights_weight_covered). This is the object "
                                          "comparable to of_which_los_pp.")))
    t_wr = pd.concat(wr, ignore_index=True).merge(dec[["period", "of_which_los_pp"]],
                                                  on="period", how="left")
    t_wr["gap_vs_elasticity_pp"] = t_wr.los_mix_pp - t_wr.of_which_los_pp

    # ---- sensitivity grid -------------------------------------------------------------
    sens = []
    for mm2 in sorted({M2_LO, m2, M2_HI}):
        for mm3 in sorted({M3_LO, m3, M3_HI}):
            mm1 = float(np.mean([m1_from_identity(r.alos, r.s1, r.s2, r.s3, mm2, mm3)
                                 for _, r in calib.iterrows()]))
            recs, phil, ok = [], None, True
            for y in sorted(alos_a):
                d, alos = ann.get(y, dict(n7=0, n28=0)), alos_a[y]
                if pd.isna(alos):
                    continue
                if d.get("n7") == 4 and d.get("n28") == 4:
                    s1, s2, s3 = 1 - d["s7"], d["s7"] - d["s28"], d["s28"]
                elif d.get("n28", 0) >= 3:
                    s3 = d["s28"]
                    s1, s2, _, _ = solve_shares(alos, s3, mm1, mm2, mm3)
                elif phil is not None:
                    s3, s1, s2, _ = solve_s3_from_alos(alos, phil, mm1, mm2, mm3)
                else:
                    continue
                ok = ok and s1 >= 0 and s2 >= 0 and s3 >= 0
                phil = s2 / (1 - s3)
                recs.append((str(y), s1, s2, s3))
            arr = np.array([[x[1], x[2], x[3]] for x in recs])
            for rr2 in sorted({0.85, r2, 0.95}):
                for rr3 in sorted({0.65, r3, 0.85}):
                    Mv = mix_index(arr[:, 0], arr[:, 1], arr[:, 2], rr2, rr3)
                    for j in range(1, len(recs)):
                        sens.append(dict(period=recs[j][0], m1_calibrated=mm1, m2=mm2, m3=mm3,
                                         r2=rr2, r3=rr3, feasible=ok,
                                         nights_share_ge28=arr[j, 2],
                                         los_mix_pp=100 * (Mv[j] / Mv[j - 1] - 1)))
    sens = pd.DataFrame(sens)
    sens.to_csv(os.path.join(OUT, "14b_los_adr_term_sensitivity.csv"), index=False)
    t = t.merge(sens[sens.feasible].groupby("period").los_mix_pp
                .agg(sens_lo="min", sens_hi="max", sens_med="median", sens_n="size")
                .reset_index(), on="period", how="left")
    t = t.merge(sens[sens.feasible & (sens.r2 == r2) & (sens.r3 == r3)]
                .groupby("period").los_mix_pp.agg(sens_lo_means_only="min",
                                                  sens_hi_means_only="max").reset_index(),
                on="period", how="left")

    term = pd.concat([t, t_wr, pd.concat(reg_terms, ignore_index=True), tq],
                     ignore_index=True)
    term["r2_used"], term["r3_used"] = r2, r3
    term["m1_used"], term["m2_used"], term["m3_used"] = m1, m2, m3
    term["ratios_are_placeholders"] = False  # 14a measured ratios are the defaults
    front = ["scope", "period", "tier", "los_mix_pp", "los_mix_pp_linear", "of_which_los_pp",
             "gap_vs_elasticity_pp", "sens_lo", "sens_hi", "sens_lo_means_only",
             "sens_hi_means_only", "d_share_lt7_pp", "d_share_7_27_pp", "d_share_ge28_pp",
             "mix_index", "adr_yoy_pct"]
    term = term[[c for c in front if c in term.columns]
                + [c for c in term.columns if c not in front]]
    term.to_csv(os.path.join(OUT, "14b_los_adr_term.csv"), index=False)

    # ------------------------------------------------------------------------- print --
    pd.set_option("display.width", 260)
    pct = ["nights_share_lt7", "nights_share_7_27", "nights_share_ge28",
           "booking_share_lt7", "booking_share_7_27", "booking_share_ge28"]
    print("\n=== NIGHTS / BOOKING SHARES, global (%) ===")
    g = sh[sh.region == "total"][["period", "freq", "tier"] + pct
                                 + ["alos_input", "alos_check", "m1_used",
                                    "short_harmonic_mean"]].copy()
    for c in pct:
        g[c] = (100 * g[c]).round(2)
    print(g.round(3).to_string(index=False))
    print("\n=== NIGHTS SHARES, regional annual (%) ===")
    rr = sh[sh.region != "total"][["period", "region", "method"] + pct[:3]
                                  + ["alos_input", "m1_used", "m1_implied_if_s3_zero",
                                     "feasible"]].copy()
    for c in pct[:3]:
        rr[c] = (100 * rr[c]).round(2)
    print(rr.round(3).to_string(index=False))
    print("\n=== LOS ADR-MIX TERM (pp of ADR y/y), r2=%.2f r3=%.2f PLACEHOLDERS ===" % (r2, r3))
    show = term[term.scope.isin(["global_annual", "within_region_agg__phi_common",
                                 "within_region_agg__s3_prop_alos", "global_quarterly_yoy"])]
    print(show[["scope", "period", "tier", "los_mix_pp", "los_mix_pp_linear",
                "d_share_ge28_pp", "of_which_los_pp", "gap_vs_elasticity_pp",
                "sens_lo", "sens_hi"]].round(3).to_string(index=False))
    print("\nwrote %s\\{14b_los_disclosures,14b_los_bucket_shares,14b_los_adr_term,"
          "14b_los_adr_term_sensitivity}.csv" % OUT)


if __name__ == "__main__":
    main()
