# Nights by stay-length bucket: <7, 7–27, 28+

Step 2 of the length-of-stay build. Script `analysis/src/adr/14b_los_bucket_shares.py`;
outputs `data/processed/adr/14b_los_{disclosures,bucket_shares,adr_term,adr_term_sensitivity}.csv`.

## What is disclosed

Airbnb disclosed **two** stay-length shares, not one, and the second is easy to miss:
the 28+ night share of **gross nights booked** (1Q21–1Q24, plus a retrospective 2019
baseline of 13–16%), and the **7+ night share** of gross nights booked (1Q21–2Q23:
50, ~49, 45, 47 / 48, 45, ~45, ~46 / ~45, ~45). Where they overlap the three-bucket
nights split is **fully disclosed and needs no assumption**. Definition is stable
throughout — nights *booked*, gross, prior to cancellations and alterations. 2Q21 (19%)
exists only on the call, so the repo's letter-sourced KPI panel has a hole there;
patched. Trip Length was dropped after the 1Q24 letter.

## The solve

Identity: `1/ALOS = s1/m1 + s2/m2 + s3/m3`, bookings ∝ nights share ÷ bucket mean.
Because 2021–22 give all three shares, the identity runs **backwards** to solve the
short-bucket mean: **m1 = 2.43 (2021), 2.50 (2022)** → 2.47 used, and only 2.41–2.55
across m2 ∈ [9,13] × m3 ∈ [35,60]. m2 = 11 is assumed from an Inside Airbnb refit;
m3 = 45 is assumed, loosely anchored by "~25% of long-term-stay nights are 3 months or
longer" (implies 43–53). Airbnb has **never** stated an average long-term-stay length.

Nights shares (%), global — booking shares in brackets:

| | <7 | 7–27 | 28+ | basis |
|---|---|---|---|---|
|2021|52.3 [88.2]|26.6 [9.9]|21.1 [1.9]|disclosed|
|2022|54.0 [88.6]|25.8 [9.6]|20.2 [1.8]|disclosed|
|2023|56.6 [89.5]|25.2 [8.9]|18.2 [1.6]|solved|
|2024|58.2 [89.7]|25.9 [8.9]|15.9 [1.3]|ALOS-only|
|2025|60.0 [89.9]|26.7 [9.0]|13.4 [1.1]|ALOS-only|

Three out-of-sample checks pass: the ALOS-only carry returns 1Q24 = 16.8% vs disclosed
17.0%; the regional solve returns NA 2024 = 22.6% vs the only regional figure ever
published, 3Q24 NA = 23%; FY23 solves to 56.6/25.2 vs 1H23 disclosed 55/27.

## Sensitivity, and what it cannot tell

2021–22 nights shares are assumption-free. 2023 moves ±1.5pp on m1 ∈ [2.41,2.55]. The
2024–25 rows are the weak segment: holding φ = s2/(s1+s2) is the only thing closing
them, and it assumes management's own claim that falling ALOS is bucket mix, not
within-bucket shortening. Against 1H24's disclosed 17%, the carry gives FY24 15.9% — it
runs ~1pp low, so the 2024–25 term is if anything overstated. Regionally the 28+ share
was never split; both allocation schemes are written out, and APAC is **infeasible**
in 2020–22 (ALOS 2.7–3.2 is shorter than the global sub-28 harmonic mean of 3.24), which
is itself the finding.

## LOS ADR-mix term (pp of ADR y/y, ratios 0.90 / 0.75 — PLACEHOLDERS)

| | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|
|global mix|+0.32|+0.61|+0.56|+0.58|
|within-region agg|+0.52|+0.96|+0.40|+0.10|
|existing −0.15 elasticity|+0.26|+0.62|+0.21|+0.04|

The global term is *not* comparable to `of_which_los_pp` — it carries the geographic
part of the ALOS drift, which `07_full_decomposition` books under `geo_mix_pp`. The
within-region aggregate is the like-for-like object, and it brackets the elasticity term
within 0.1–0.35pp in every year. Full grid range at the central ratios: +0.18 to +0.94.
