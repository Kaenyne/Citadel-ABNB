# 44. Short case v2: the two audit fixes

Krish with Claude (Opus 5.5), 23 Sep 2026, branch `krish/cost-leg`. Script `analysis/src/margin_build/44_short_case_v2/run.py`
(`py -3.13`, exit 0), outputs `data/processed/margin_build/44_short_case_v2/`. A copy of `40_line_build/run.py` with two fixes; 40 is
untouched and the base build is asserted identical (max difference 5e-13).

## The fixes

- **C-03 (GBV chaining).** In 40, 3Q27 and 4Q27 short-case revenue and GBV applied the short growth rates to the *base* path's 3Q26 and
  4Q26, so the short case's weaker 2026 was forgotten a year later (implied 3Q27 / 4Q27 ADR growth +2.7% / +6.9% against the stated
  ~0%). v2 chains them from the short case's own 3Q26 and 4Q26.
- **C-04 (RNPL overlay).** In 40, the +4% ops & support uplift was stored in the history and applied again in 2H27 (1.04 x 1.04). v2
  keeps an unoverlaid history and applies the uplift once, as a level.

## Results (`44_vs_40_short_case.csv`, `44_short_case_price.csv`)

| Short case, costs at budget | v40 | v44 | Change |
|---|---|---|---|
| FY26 margin | 34.2% | 34.2% | none (2026 untouched) |
| FY27 revenue | $14,914M | $14,563M | −$350M |
| FY27 growth on the short case's own FY26 | +7.0% | +4.5% | now matches the memo's "+4.5%" |
| FY27 adj. EBITDA / margin | $4,761M / 31.9% | $4,481M / 30.8% | −$280M |
| FY27 EPS | $4.58 | $4.18 | −$0.41 |
| Price at 13.5x (memo v3 convention) | $123.7 | $117.4 | −$6.3 |
| Price, spot-anchored growth-linked multiple (43b) | $123.3 | $107.8 (12.2x) | −$15.5 |

The two effects net: C-03 alone lowers FY27 EBITDA by ~$310M, C-04 raises it by ~$30M. The memo's "short case $125" should read $117
on its own 13.5x convention, or $108 on the growth-linked convention the $143 target now uses (`43_thesis3_integration.md` §3). Pick the
convention with the target.

## Limits

The short case remains a scenario: nights and ADR paths are the team's judgement (+8.5 / +5 / +4 / +2 / +3 / +4% nights, ADR ex-FX flat
after 3Q26), costs at management's budget, RNPL overlays unsourced as magnitudes. Zero fitted parameters.

## RESUME

Done. If the memo keeps a short-case price, take it from `44_short_case_price.csv` on the same multiple convention as the target.
