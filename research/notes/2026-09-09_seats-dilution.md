# Seats dilution: what Experiences, Services and hotels do to reported ADR

Krish with Claude Code, 9 Sep 2026, branch `krish/seats-dilution`. Script
`analysis/src/adr/15_seats_dilution.py`; outputs `data/processed/adr/15_seats_dilution_{annual,quarterly,sensitivity}.csv`;
row "New-business mix (seats + hotels)" in `model/ADR_decomposition.xlsx` 5_Forecast.

## The mechanism

Since the 2Q25 letter the KPI is Nights and Seats Booked: nights booked for stays plus seats
booked for experiences and services, net of cancellations. ADR is GBV divided by that number,
and the FY2025 10-K's regional table and the regional ADR sentences are on the same basis. The
1Q25 letter's "Nights and Experiences Booked" already carried experiences seats, so the rename
added Services and the May 2025 Experiences relaunch; the arithmetic did not change.

A seat is one unit of the denominator at a fraction of a night's GBV. A hotel night is one unit
at about 0.8x a home night. When those units grow faster than home nights, reported ADR falls
with no change in lodging pricing. Airbnb discloses no seat or hotel-night volumes, so this is a
scenario build off the overnight new-business revenue cases, not a measurement.

## Inputs

| Component | Volume source | Price relative to a home night (FY25) |
|---|---|---|
| Hotel nights | 18.7m FY25 (3.5% of nights, per 11's assumption), growth 35/30/25% base | 0.81 ($140 vs $174) |
| Experiences seats | GBV = revenue / 20% host fee; $75 per seat (assumption) | 0.43 |
| Services seats | GBV = revenue / 15% host fee; $120 per seat (assumption) | 0.69 |

Home-night price FY25 is backed out at $174 against the reported $171 blend. Price ratios are
held at FY25, so the drag is a pure unit-mix effect and independent of the pricing path.

## Result: pp of reported ADR y/y

| | FY25 | FY26 | FY27 | FY28 |
|---|---|---|---|---|
| ADR-bull (business bear) | −0.18 | −0.23 | −0.20 | −0.18 |
| **Base** | **−0.18** | **−0.48** | **−0.57** | **−0.62** |
| ADR-bear (business bull) | −0.18 | −0.75 | −1.05 | −1.32 |

FY25's −0.18pp is mostly hotels (−0.11) and was small enough that management never called it
out. From FY26 seats take over: base FY27 is −0.41pp from seats and −0.16pp from hotels. The
seats share of the denominator goes 1.3% (FY25) to 2.8% (FY27 base) to 4.1% (business bull).

Sensitivity (ticket grid $50-100 experiences, $80-180 services, FY24 experiences GBV $250-550m):
FY27 base drag −0.30 to −1.01pp, median −0.64. The ticket assumption is the whole uncertainty.

## What it changes

- It is the same size as the unit-size term with the opposite sign, and it hits the regional
  ADR figures too. Reported ADR ex-FX of +3-4% in 2026-27 is consistent with home pricing of
  +3.5-4.5%.
- The 5_Forecast row is tied to the new-business case: the ADR bear case is the business bull
  case. The revenue build and the ADR build must pick the same case.
- Quarterly: seats are probably summer-heavy (Experiences), so the uniform quarterly spread in
  `15_seats_dilution_quarterly.csv` understates 3Q and overstates 4Q. Not correctable without a
  disclosure.

## What would sharpen it

Any disclosure of seats, experiences GBV, or hotel nights share. The Q4'25 call's "single-digit
% of nights" for hotels and the 2Q26 "three times as fast as homes" are the only anchors. If the
5 Nov letter gives a seats number, replace the ticket assumption with it and rerun.
