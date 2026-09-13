# M5: Consensus-anchored model: Street EBITDA at the guide date plus its systematic bias

Read `docs/margin-build/prompts/M_common.md` first. Slug: `M5_street_bias`. Method name: `street-bias`.
Inputs: WS03 (`03_consensus_at_dates.csv`, `03_surprise_history.csv`, `03_revision_paths.csv`, `03_current_consensus.csv`), WS02 panel,
the frozen harness `baselines__street` revenue object and the guide-cushion revenue object.

## Method

This is the one method allowed to use consensus as an input, because its object is the surprise.
1. `street_plus_bias`: EBITDA_q = Street_EBITDA_q(at vintage) + bias, bias = PIT recency-weighted mean surprise (in $ or margin points; test both),
   by quarter-of-year if the seasonal pattern of surprises is real (test it), shrunk toward zero.
2. `street_plus_flowthrough`: EBITDA_q = Street_EBITDA_q + m * (Rev_forecast_q - Street_Rev_q) + bias, where Rev_forecast is the team's PIT revenue
   forecast (frozen harness guide-cushion object; in LIVE, the bridge v3 / WS06 path) and m is the PIT incremental margin on revenue surprises
   estimated from WS03's history. This is the object that turns the team's revenue view into a margin surprise.
3. `dispersion_conditioned`: same as 1 but the bias and the quantiles scale with analyst dispersion (std / mean) at the vintage date.

## Tests (pre-register)

Beat `street` (the raw consensus) on adj EBITDA $ and margin MAE at h=0 and h=1 in W1 and W2, both weightings; n per cell (the consensus panel
may not cover every vintage; report coverage). Test whether the surprise is autocorrelated (Ljung-Box on n ~20; say the power is low) and whether
the FY-floor anchoring hypothesis holds (Street FY margin vs floor at each guide date).

## LIVE / for the 5 Nov card

3Q26 and 4Q26 EBITDA and margin vs the current consensus (LSEG and Bloomberg), the implied surprise under base/bear/bull revenue, the probability
of an EBITDA beat given the team's revenue view, and the FY26/FY27 consensus margin vs your view. This feeds the pitch's "what is the Street missing"
line, so be explicit about direction and size with the uncertainty.
