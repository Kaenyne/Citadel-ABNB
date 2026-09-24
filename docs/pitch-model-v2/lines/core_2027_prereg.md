# The 2027 core rule (fix m): pre-registration

Krish with Claude Code, 23 Sep 2026, branch `krish/adr-audit-fixes` (PR #67). The blob hash is logged in
`data/processed/pitch_model_v2/adr_engine_v3/core_2027_prereg_hash.txt`. Later changes are appended, never deleted.

## 1. What is already known, and what is not

`adr_engine_v3` carries the 2Q26 core (like-for-like price growth, 3.849pp, or 3.799 net of the World Cup, fix l)
flat into every forecast quarter. The audit's walk-forward (`receipts/ADR_AUDIT/audit_core.py`,
`C1_core_pit_scores.csv`) compared that carry with the core's expanding mean. The expanding mean is the average of
every core observed up to the forecast date.

**Already seen, so this part is not pre-registered.** At 3 and 4 quarters ahead, the mean beats the carry in both
windows. The RMSE ratio of mean to carry is 0.784 / 0.839 at h = 3 and 0.679 / 0.782 at h = 4, on n 6–8. At 1–2
quarters ahead it does not: the windows split at h = 2, and the carry wins at h = 1 on 1Q25+. Adopting the mean at
h = 3 and 4 is therefore a post-hoc choice, and it is labelled that way. It lowers FY27 ADR, which helps the short.

**Not yet seen, and registered here.** The audit scored h = 1–4 only. Of the 2027 quarters from a 2Q26 origin:
- 1Q27 is h = 3;
- 2Q27 is h = 4;
- 3Q27 is h = 5;
- 4Q27 is h = 6.

The rule has never been scored at h = 5 or 6.

## 2. The test at h = 5 and 6 (registered before it is run)

**Construction.** The same as `audit_core.py`:
- the core history 1Q23–2Q26 from `exfx.history()`;
- origins from 4Q23 (at least 4 observations);
- carry = the last observed core, and mean = the expanding mean at the origin;
- the AR(1) refit is reported beside them, not used to decide;
- n is 6 at h = 5 and 5 at h = 6. Every target falls in 1Q25 or later, so the audit's two windows coincide at these
  horizons. That is stated, not hidden.

**Pass line.** The expanding mean's RMSE is below the carry's at h = 5 and, separately, at h = 6.

**Consequence.**

| quarter | h | rule |
|---|---:|---|
| 3Q26 | 1 | carry (unchanged) |
| 4Q26 | 2 | carry (unchanged) |
| 1Q27 | 3 | expanding mean (post-hoc, on the audit's two-window result) |
| 2Q27 | 4 | expanding mean (post-hoc, on the audit's two-window result) |
| 3Q27 | 5 | expanding mean if h = 5 passes, else carry |
| 4Q27 | 6 | expanding mean if h = 6 passes, else carry |

## 3. The rule's inputs, fixed here

**Expanding mean.** The mean of the core history 1Q23–2Q26, with 2Q26 taken net of the World Cup premium when fix
(l) is on (3.849 − 0.05). The 2Q27 World Cup lap (fix l) applies under any rule.

**LOS under the mean rule.**
- **Why it changes:** under the carry, the forward LOS term enters as a change against the in-core fill (fix k).
  Under the mean, the core no longer carries 2Q26's LOS fill, so LOS must enter as its own y/y level.
- **Rule:** for the quarters on the mean rule, LOS = the expanding mean of the LOS term through the latest measured
  quarter. That uses H's values for 1Q23–4Q25, the 0.30 fill for 1Q26 and 2Q26 (the fix (k) run measured 2Q26 at
  +0.26 to +0.32, which agrees), and fix (k)'s +0.047 for 3Q26.
- **Bound:** carrying +0.047 (the latest measurement) is reported as the labelled low bound.

**Other terms are unchanged.** Geo, unit size, seats, interaction, the bundle and basis_adj stay as they are.

**Band.** For the quarters on the mean rule, the core's half-width is the mean rule's own point-in-time RMSE at that
horizon (the larger of the two windows), in place of the carry's h-step sd. The LOS half-width is half the distance
between its mean and its bound.

## 4. Engine wiring

This goes into `adr_engine_v3` behind `exfx.CORE_HORIZON_RULE` (default True). False reverts to the carry for
every quarter. The ladder `los_wc_ladder.csv` gains a row for fix (m).

The test is `core_horizon.py`, written to `core_horizon_scores.csv` and `core_horizon_walkforward.csv`. Its pass or
fail is read by the engine, not typed in.
