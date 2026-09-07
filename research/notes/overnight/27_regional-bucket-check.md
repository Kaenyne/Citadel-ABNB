# 27. Which end of the regional nights bucket, and the FY27 nights band

Krish with Claude Code, 7 Sep 2026. Script `analysis/src/overnight/27_regional_bucket_check.py`; outputs `data/processed/overnight/27_regional_bucket_check.csv`, `27_nights_band.csv`. Follows workstream 10.

## Why

From 4Q24 Airbnb reports regional nights growth only as buckets ("mid-single digits", "low-20s"). Workstream 10 uses the midpoints. In 1Q26 and 2Q26 the share-weighted midpoints overshoot reported total growth by 0.6 and 0.9pp, so at least one region sits at the bottom of its bucket. Regional revenue (XBRL geography) and regional reported ADR are hard numbers, so they can arbitrate.

## Method

Revenue-implied nights y/y = (1 + regional revenue y/y) / (1 + regional reported ADR y/y) / (1 + global quarterly take-rate y/y) / (1 + global FX timing wedge) − 1. The take-rate and wedge adjustments are global, and regional revenue carries hotels, Experiences and recognition timing, so the implied value is a noisy read (2Q26 LatAm and APAC come out 8pp below their buckets). Each region is then placed inside its bucket as close as possible to the implied value, with the constraint that prior-year-share-weighted growth reproduces reported total growth. The picked values therefore sum exactly; the implied values are the evidence for which end.

## Result: where each region sits

| Quarter | NA | EMEA | LatAm | APAC | Midpoint residual |
|---|---|---|---|---|---|
| 4Q24 | inside (5.6) | high (12.0) | low (20.0) | inside | −0.5pp |
| 1Q25 | high (3.0) | inside | inside | low (14.0) | −0.2 |
| 2Q25 | low (1.0) | inside | high (19.0) | high (16.0) | −0.2 |
| 3Q25 | low (4.1) | high (6.0) | inside | high (16.0) | −0.2 |
| 4Q25 | low (4.2) | high (9.0) | high (19.0) | high (16.0) | −0.4 |
| 1Q26 | low (7.0) | inside (4.4) | high (19.0) | low (17.0) | +0.6 |
| 2Q26 | low (7.0) | inside (7.4) | low (19.0) | low (17.0) | +0.9 |

Two things hold up across quarters. North America has sat at the bottom of its bucket in five of the last six quarters: its revenue growth is explained by ADR and FX, not by nights. Through 2025 EMEA, LatAm and APAC sat at the top, which is why the midpoint sum undershot. In 2026 the sign flipped: the midpoints now overshoot, and the constrained pick puts NA, LatAm and APAC at their low ends.

For the model this means the 2Q26 base for NA is 7%, not 8%, and the 3Q26 base-case NA growth of 7% is flat on the run-rate rather than a step down. The LatAm and APAC 2Q26 reads (revenue-implied 12%) are too far below the bucket to be timing alone and are worth a question on the 5 Nov call.

## Result: the band

Every 2Q26 bucket is ±1pp wide. Carrying that half-width through the workstream 10 forward rates for every region, with the driver model's mechanics (prior-year regional nights × growth less regulatory drag, 1H26 actual):

| Case | 3Q26 nights y/y | 4Q26 | FY26 | FY27 y/y | FY27 nights (M) |
|---|---|---|---|---|---|
| bucket low | 9.3% | 9.1% | 9.5% | 8.1% | 630.4 |
| base | 10.3% | 10.1% | 9.9% | 9.1% | 639.1 |
| bucket high | 11.3% | 11.1% | 10.4% | 10.1% | 647.7 |

So the disclosure width alone puts ±1pp on FY27 nights growth, about ±8.6M nights, before any judgement about the growth rates themselves. This replication of the base gives 639.1M against the driver model's 637.6M (0.2% apart, from the model's handling of the 3Q26 and 4Q26 regional split); the band, not the level, is the deliverable.

## For the model

- Carry `bucket_low` and `bucket_high` from `27_nights_band.csv` as a memo range next to the bear/base/bull nights rows.
- Set the 2Q26 NA base to the bottom of its bucket when the regional shares are next re-anchored.
- Re-run after the 3Q26 letter (5 Nov): if the midpoint residual stays positive, the growth engine outside NA is running below its bucket midpoints and the FY27 LatAm/APAC rates (16/15%) are the ones to cut.
