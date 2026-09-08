# Statistics Canada NTS data request — party size × accommodation type

**Status: drafted 8 Sep 2026, NOT YET SENT.** Owner: Jessie.

## Why we want it

The nights model's split mix-drift (`MIX_DRIFT_ABNB` vs `MIX_DRIFT_HOTEL` in `analysis/src/choice_nights_driver.py`) assumes rental-type parties grow faster than hotel parties. That rests on Hawaii alone. Spain's INE microdata says the ratio is flat over 11 years and the UK's GBTS says the gap narrowed — so the scoreboard is **1 market for, 2 against**, and the strongest dataset is one of the two against. See `choice_nights_driver.md` § "Beyond Hawaii".

Canada is a top-5 Airbnb market and the NTS is quarterly with long history, so it would be the **fourth two-sided market** and would likely settle the question either way. It is the cheapest remaining way to move the divergence from contested to resolved.

## What we already checked

Public tables in the 24-10 series carry party size and accommodation type as **separate marginals**; the cross-tab is not published. StatCan's own NTS documentation directs cross-tab requests to `tourism@statcan.gc.ca`.

## Two routes, cheapest first

1. **NTS Public Use Microdata File (PUMF)** — carries both variables at record level. Free at any Data Liberation Initiative member university. **If anyone on the team has a university affiliation, try this first and skip the email entirely.**
2. **Custom tabulation** via `tourism@statcan.gc.ca` — cost-recoverable, quote first, typically a few weeks. Use the draft below.

## Draft email

> **To:** tourism@statcan.gc.ca
> **Subject:** Custom tabulation request — National Travel Survey: travel party size by type of accommodation

Hello,

I'm looking for National Travel Survey data that cross-tabulates two variables I can only find published separately, and I'd be grateful for your guidance on the best route to it.

**What I'm after**

Domestic overnight trips by Canadian residents, annual, 2016–2025 (or the longest span available on a consistent basis):

- **Rows:** type of accommodation used — specifically distinguishing hotel/motel from commercial cottage/cabin and private cottage or vacation home
- **Columns:** size of travel party
- **Measures:** person-trips and person-nights, weighted

A mean party size by accommodation type would serve just as well as a full distribution if that's simpler to produce.

**Why I'm asking this way**

I've been through the public tables in the 24-10 series and can find each variable separately, but not crossed. Before commissioning anything, I'd genuinely welcome being told if:

1. An existing public table already covers this and I've missed it, or
2. The NTS Public Use Microdata File carries both variables at record level, in which case I'd rather work from the PUMF directly than ask you to run a tabulation.

If a custom tabulation is the only route, could you let me know the estimated cost and turnaround before any work begins? I understand these are cost-recoverable.

**Context and format**

This is for private-sector market research on the Canadian accommodation sector — I'd note that in case it affects licensing terms, and I'm happy to comply with whatever attribution or redistribution conditions apply. CSV or Excel is ideal; a flat file with the weights included is perfect.

Thank you very much for your help.

Best regards,
[Name] · [Title / firm] · [Phone]

## Notes on the draft

- **The two escape hatches are the most valuable part.** Custom tabs cost money and take weeks; the PUMF is free and has what we need. Inviting StatCan to redirect us is the fastest path to a cheap answer.
- **Commercial purpose is disclosed deliberately.** StatCan serves commercial users routinely, but licensing conditions can differ from academic use, and saying so up front avoids a problem if the output reaches a client-facing deck.
- **Timing:** a few weeks' turnaround means this is only useful for the pitch if it goes out now.

## What to do with the answer

If Canada shows rental parties growing faster than hotel parties, the divergence goes to 2–2 and the model's split mix-drift is defensible as a central case. If it shows flat — as Spain does — then zero both vectors: that costs 2.2% of 2030 U.S. nights (CAGR 2.84% → 2.38%) and the party-size story becomes a **level** argument only, which is where the four confirmed sources already point.
