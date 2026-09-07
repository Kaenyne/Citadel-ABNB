# WS22: fixing the regulatory Monte Carlo's conditional dependencies (audit A06)

**Bottom line.** All three defects the audit found in `analysis/src/abnb_regulatory_forecast.py` were reproduced
exactly, then repaired. They were mechanics, not assumptions: not one probability, loss range, correlation
parameter or exposure anchor in the event register was changed. The centre of the distribution is unchanged
(2027 median 0.45%, mean 0.75%; 2030 mean 2.20%); the upper tail changes shape because the EU binding-caps
scenario can no longer happen without the EU act happening, and Barcelona's partial phase-out now carries the
30.25% the note always claimed rather than the 23.05% the code delivered. 2030 median 1.71% → 1.66%, 2030 95th
6.38% → 6.69%. **No investment conclusion moves.** One driver-model input moves by 4bp (FY28 EMEA nights drag
1.00 → 0.96pp) and three files written by other workstreams now quote stale numbers; both are listed below for a
later agent, since I did not edit WS08/13/15/16 files.

**Compiled:** 2026-09-06. Author: Claude Code (WS22), for Krishang.
**Inputs:** `docs/overnight/00_BRIEF.md`; `docs/2026-09-06_audit_findings_ai_handoff.md` section 8 (A06a/b/c,
read-only in the MAIN tree); the event register in `analysis/src/abnb_regulatory_forecast.py`; the WS11 overlay
builder `analysis/src/overnight/11_competition_supply_overlays.py`.
**Files written**

| File | What it is |
|---|---|
| `analysis/src/abnb_regulatory_forecast.py` | the simulator, repaired (this is the only pre-existing file whose *code* I changed) |
| `research/notes/2026-09-05_regulatory-forecast-profile.md` | new section 0 "Correction, 6 September 2026" plus every affected prose number re-run |
| `analysis/src/overnight/22_regulatory_before.py` → `data/processed/overnight/22_regulatory_before.csv` | frozen pre-fix sampler; reproduces the audit's diagnostics to 4 decimal places |
| `analysis/src/overnight/22_regulatory_checks.py` → `data/processed/overnight/22_regulatory_checks.csv` | 77 acceptance checks, 0 failures, non-zero exit on failure |
| `analysis/src/overnight/22_regulatory_delta.py` → `data/processed/overnight/22_regulatory_delta.csv` | before/after median, mean, p95 by year and region, and per-event |
| `data/processed/abnb_regulatory_profile.csv`, `abnb_regulatory_contributions.csv`, `abnb_regulatory_events.csv` | regenerated |
| `analysis/figures/abnb_regulatory_profile.png` | regenerated |
| `data/processed/overnight/11_regulatory_overlay.csv`, `11_regulatory_pending_items.csv` | regenerated **in place** by re-running `11_competition_supply_overlays.py` (see "Concurrency" below) |

---

## 1. Reproducing the audit first

`22_regulatory_before.py` embeds a frozen copy of the pre-fix sampling logic (same seed 20260905, same 200,000
draws, same RNG consumption order) so the defect stays reproducible after the fix lands. It matches every number
the audit reported:

| Diagnostic | Audit | Reproduced |
|---|---|---|
| 2027: EU-TAIL fires without EU-AHA, % of all draws | 1.0845% | **1.0845%** |
| 2027: ... as % of tail occurrences | 54.02% | **54.02%** |
| 2030: EU-TAIL without EU-AHA, % of all draws | 1.731% | **1.7310%** |
| 2030: ... as % of tail occurrences | 21.72% | **21.72%** |
| 2030: Barcelona partial effective probability (stated 30.25%) | 23.05% | **23.047%** |
| EU-AHA in force by 2027 but absent by 2030 | 3.01% | **3.0075%** |

Two findings the audit did not quantify and the frozen run does:

- **Reversals were pervasive, not marginal.** EU-AHA's 3.01% was the smallest case. Across the register, **72.4%
  of draws reversed at least one event** between the 2027 and 2030 columns (CHI-SUIT 12.3%, NYC-LOOSEN 10.3%,
  US-CITY 10.0%, ES-FINE 9.9% — mechanically, any event whose 2027 and 2030 probabilities are both near 0.5
  reverses in roughly p27 x (1 − p30) of draws). So the two columns were never a path; they were two
  independent marginal scenarios, described in the note as a longitudinal profile.
- Full/partial Barcelona overlap was already zero in the old code. That acceptance check was passing before; the
  defect was the *level* of the partial probability, not overlap.

The frozen run also reproduces the published profile exactly (2027 median 0.4510%, mean 0.7523%, p95 2.7443%;
2030 median 1.7084%, mean 2.1970%, p95 6.3825%), which confirms `abnb_regulatory_profile.csv` as shipped came
from this defective sampler and not from some other version.

## 2. A06a — is the 2% / 8% tail conditional or unconditional? **Unconditional.**

The decision matters: read as conditional, the tail's marginal probability collapses to 0.24% by 2027 and 3.6% by
2030 and the whole upper tail of the profile thins; read as unconditional, the marginal is preserved and only the
joint structure changes.

The register's own text settles it in favour of **unconditional (marginal)**:

1. The column definition above `EVENTS` reads "p27 / p30: probability the loss-bearing outcome is **in force by**
   end-2027 / end-2030", stated once for the whole table with no per-row exception. That is a marginal
   definition.
2. The note's section 2 preamble repeats it: "Probabilities are for the loss-bearing outcome to be *in force* by
   the horizon."
3. The `gates` string for EU-TAIL — "conditional on EU-AHA branch; requires Council appetite for caps against
   member-state competence objections" — is a *logical prerequisite plus a merits argument*, which is exactly how
   every other `gates` string in the table reads (they describe what must happen, not how the number was
   normalised). Where the author did mean a conditional number, he wrote the arithmetic out: BCN-PARTIAL's gates
   say "0.55 x (1 − 0.45) = 0.30 effective". EU-TAIL's gates contain no such product.
4. The implied conditional rates are stable and plausible under the unconditional reading: 0.02/0.12 = **16.7%**
   by 2027 and 0.08/0.45 = **17.8%** by 2030 — a near-constant ~1-in-6 escalation rate conditional on the act
   existing, which is what a coherent forecaster would hold across horizons. Under the conditional reading the
   author would have been asserting a 2% escalation rate in 2027 rising to 8% by 2030, and separately would have
   had to believe a marginal tail probability of 0.24%, below his own stated "extreme probability gate" of 2%
   ("no event under 2% except the EU tail at 2% for 2027").

**Implementation.** EU-TAIL is now nested inside EU-AHA and fires on the parent's most extreme draws — a severity
ladder on the parent's own uniform: `occurs = U[EU-AHA] < p_tail`. This makes tail ⊂ parent by construction,
preserves the marginal exactly (2.00% and 8.00% realised, table below), and reads correctly as economics: the
tail *is* the same legislative file going further, so the harder the European housing-politics push, the further
it goes. The generic machinery is a `parent=` field on any event, with an assertion that a child's marginal never
exceeds its parent's.

**Reported both ways, as the audit asked:**

| | Declared marginal | Realised marginal | Implied conditional P(tail \| act) | Realised conditional |
|---|---|---|---|---|
| by end-2027 | 2.00% | 1.989% | 16.67% | 16.52% |
| by end-2030 | 8.00% | 8.001% | 17.78% | 17.80% |

**The alternative nesting does not matter much.** A second admissible construction preserves the same marginal:
an independent Bernoulli inside the parent (`parent & (V < p_tail/p_parent)`), which decorrelates the tail from
the rest of the EU block instead of maximally correlating it. Check 5 in `22_regulatory_checks.csv` runs it: the
2030 95th percentile is 6.44% instead of 6.69% and the median 1.67% instead of 1.66%. I shipped the severity
ladder because a Europe-wide binding-caps regime plainly coincides with national crackdowns rather than arriving
independently of them, and because it is the more conservative (fatter-tailed) of the two. Either way the
conclusion is unchanged, and the choice is now explicit rather than accidental.

## 3. A06b — Barcelona: the stated product is now the implemented product

The two Barcelona branches are one ordinal outcome of one decision, so they are now drawn as one ordinal ladder
on a single Barcelona uniform:

- `u < 0.45` → full phase-out (≥70% of the 10,101 licences lapse and are enforced);
- `0.45 ≤ u < 0.45 + 0.55 x (1 − 0.45) = 0.7525` → partial (30–70%, or grandfathering past 2029);
- `u ≥ 0.7525` → blocked or delayed past 2030 (24.75%).

This delivers **exactly** the rationale's arithmetic: P(partial) = 0.55 x (1 − 0.45) = **30.25%** (realised
30.26%), P(partial | not full) = **55.0%** (realised 55.13%), and zero overlap by construction rather than by a
post-hoc mask. `BCN-PARTIAL`'s `p30` is now explicitly labelled `p_kind="conditional"` in the register so the
0.55 is never mistaken for a marginal. So: **option (i)** — I fixed the sampler to match the stated rationale,
rather than revising the rationale to match the old correlated construction.

Worth stating plainly because it is counter-intuitive: on this ladder the partial outcome sits in the *middle* of
the European-politics intensity range, so it is negatively associated with extreme EU intensity. That is right —
a maximal EU push produces the full phase-out, not a partial one — and it is why `BCN-PARTIAL`'s variance
contribution is now slightly negative (−0.003).

Effect: `BCN-PARTIAL` P(in force by 2030) 23.05% → 30.26%, expected loss 0.025% → 0.033% of revenue.

## 4. A06c — 2027 and 2030 are now one path

Each trial now draws **one** correlated uniform and **one** triangular loss size per event, and thresholds the
uniform at `p27` and at `p30`. Because `p30 ≥ p27` for all twenty events (now asserted at run time), the 2027
event set is a subset of the 2030 event set on every path. The loss size is drawn once and multiplied by
`scale30` at the later horizon, so a path's 2030 loss is the same shock grown, not a fresh shock.

**No reversal state is named anywhere in the register**, so none is modelled. If someone later wants one —
Portugal's 2024 national liberalisation is the real-world example — it needs an explicit named transition
(a `p_lapse` on the event, or a separate reversal event with its own probability), not a silently renewed
residual draw. I have left that as a documented gap rather than inventing a number.

Diagnostic worth keeping: 0.33% of paths still show a *smaller* total net loss at 2030 than at 2027. Every one of
them is `NYC-LOOSEN`, the register's single upside event (a New York loosening that arrives between 2027 and 2030
adds a revenue gain). Excluding it, the net loss is monotone on 100.0% of paths. That is recorded as a check, not
suppressed.

## 5. Acceptance checks

`analysis/src/overnight/22_regulatory_checks.py` re-imports the live simulator, re-runs 200k draws and writes
`22_regulatory_checks.csv`. **77 checks, 0 failures**, exit status 0 (it returns 1 on any failure, per audit
finding A13 about validation scripts that fail silently).

| Check family | n | Result |
|---|---|---|
| 1. child without parent | 2 | 0.000000 of draws at both horizons |
| 2. mutually exclusive branch overlap | 2 | 0.000000 at both horizons |
| 3. marginal probabilities vs declared targets | 40 | all inside a 4-sigma binomial band (±0.18pp at p=0.5, N=200k) |
| 3. conditional probabilities vs declared targets | 4 | P(tail\|act) 16.52% vs 16.67% and 17.80% vs 17.78%; P(partial\|no full) 55.13% vs 55.0% |
| 4. monotone by-date event sets | 22 | zero reversals on any event; zero paths where net loss ex-NYC-LOOSEN falls |
| 5. sensitivity to the nesting choice | 6 | reported, not asserted (see section 2) |

The tolerance is a genuine Monte Carlo band computed per check, not a hand-picked epsilon: `4 x sqrt(p(1-p)/N)`,
and for conditionals `N` is the number of parent draws, not 200k.

## 6. Before / after

Full table in `data/processed/overnight/22_regulatory_delta.csv` (horizon, overlay year x region, and per event).
Revenue loss, the compliance cost and one-off cash are kept as three separate lines throughout — the compliance
line is an EBITDA expense expressed as a % of revenue, never lost revenue, and the cash line is one-off.

**Revenue loss, % of global revenue**

| | 2027 median | 2027 mean | 2027 p90 | 2027 p95 | 2027 p99 | 2030 median | 2030 mean | 2030 p90 | 2030 p95 | 2030 p99 |
|---|---|---|---|---|---|---|---|---|---|---|
| Before | 0.451 | 0.752 | 1.947 | 2.744 | 5.440 | 1.708 | 2.197 | 4.144 | 6.383 | 8.231 |
| After | 0.450 | 0.752 | 1.786 | 2.673 | 6.278 | 1.664 | 2.203 | 4.151 | 6.689 | 8.352 |
| Delta | −0.001 | −0.000 | −0.162 | −0.072 | **+0.837** | −0.044 | +0.006 | +0.008 | **+0.306** | +0.121 |

The pattern is the whole story of A06a. Removing 1.08% (2027) and 1.73% (2030) of draws in which a 2–6% tail loss
occurred *with no parent act* takes mass out of the p90 region; those draws do not disappear, they move to where
the tail sits on top of the act's own 0.4–3.0% loss, which is past the 99th percentile at 2027. The distribution
is now more sharply bimodal, which is the honest shape: either the EU act exists or it does not.

**Compliance cost (EBITDA, % of revenue) and one-off cash ($M)** are effectively unchanged — median compliance
0.130% / 0.160%, mean 0.126% / 0.160%; expected one-off cash $49.8M / $65.1M (was $49.8M / $65.3M). Neither is
affected by the repaired dependencies.

**Threshold probabilities:** P(revenue loss >1%) 19.5% → 18.9% (2027) and 70.7% → 71.0% (2030; 0.7073 → 0.7095); P(>2%) 9.7% →
8.9% (2027) and 44.5% → 43.1% (2030).

**Valuation translation** (70% contribution margin, 22x EV/EBITDA, 567M shares): 2027 EBITDA hit median $71.9M →
$71.7M (mean $104.2M → $104.1M); 2030 median $217.5M → $212.6M (mean $270.9M → $271.6M). Per share: 2027 $2.79 →
$2.78 (mean $4.04); 2030 $8.44 → $8.25 (mean $10.51 → $10.54), and the 2030 95th $28.71 → $30.04.

**WS11 overlay, drag by year and region** (`11_regulatory_overlay.csv`, regenerated in place):

| Year | median before → after | mean before → after | p95 before → after | EMEA nights, median before → after | NA nights, median |
|---|---|---|---|---|---|
| 2026 | 0.150 → 0.150 | 0.251 → 0.251 | 0.915 → 0.891 | 0.36 → 0.36 | 0.03 (unch.) |
| 2027 | 0.451 → 0.450 | 0.752 → 0.752 | 2.744 → 2.672 | 1.07 → 1.07 | 0.08 (unch.) |
| 2028 | 0.870 → 0.855 | 1.234 → 1.235 | 3.957 → 4.011 | 2.07 → 2.03 | 0.15 (unch.) |

Europe's share of the drag is 93% in both versions.

## 7. Concurrency

`analysis/src/overnight/11_competition_supply_overlays.py` had not been touched since 01:50 on 6 Sep (mtime
checked immediately before and after my run at ~14:56), so I regenerated the WS11 overlay **in place** by
re-running that script unmodified rather than writing a parallel `22_regulatory_overlay_new.csv`. The script is
fully local (no network) and deterministic; the only file whose contents changed is `11_regulatory_overlay.csv`.
`11_regulatory_pending_items.csv` and the other five `11_*` outputs were rewritten byte-identical. I did not edit
that script.

## 8. For the model

Changes a later agent should apply. **I did not edit the WS08/13/15/16 files or `model/assumptions.md`.**

| # | Where | Current value | Should become | Why |
|---|---|---|---|---|
| 1 | `analysis/src/overnight/13_driver_model.py:262-265`, `REG_DRAG_PP` | FY28 EMEA incremental drag **1.00pp**; comment says "EMEA 0.36 / 1.07 / 2.07%" | FY28 EMEA **0.96pp**; comment "EMEA 0.36 / 1.07 / 2.03%" | cumulative EMEA drag at 2028 fell 2.07% → 2.03%. FY26 (0.36) and FY27 (0.71) and all NA values (0.03 / 0.05 / 0.07) are unchanged. Revenue effect is ~4bp on FY28 EMEA nights — immaterial, but the comment is now wrong either way |
| 2 | `model/assumptions.md`, row "Regulatory nights drag, incremental pp of growth (NA / EMEA)" | `0.03/0.36, 0.05/0.71, 0.07/1.00 pp` | `0.03/0.36, 0.05/0.71, 0.07/0.96 pp` | same source, same rule; only the FY28 EMEA figure moves |
| 3 | `analysis/src/overnight/15_claim_checks.py:116` (claim "11") | asserts `median 0.15 / 0.45 / 0.87%, mean 0.25 / 0.75 / 1.23%, p95 0.92 / 2.74 / 3.96%; EMEA nights −2.07% 2028` | `median 0.15 / 0.45 / 0.855%, mean 0.25 / 0.75 / 1.235%, p95 0.89 / 2.67 / 4.01%; EMEA nights −2.03% 2028` | the claim check will now report a mismatch against the regenerated CSV. This is the check doing its job, not a new error |
| 4 | `research/notes/overnight/11_competition-supply-and-overlays.md` line 234 and the "For the model" table line 306 | "P(revenue loss >1%) is 19.5% by 2027 and 70.7% by 2030. Two events carry 68% of the 2027 variance"; EMEA drag "−2.07% (2028)" | 18.9% and 71.0%; **77.9%** of the 2027 variance; "−2.03% (2028)" | see also "Corrections to existing work" below — the 68% was wrong before my change too |
| 5 | Any deck slide quoting the 2030 95th percentile | 6.4% of revenue / $28.71 per share | **6.7% / $30.04** | the tail is genuinely fatter once it is properly conditional |

Parameters this workstream supplies (unchanged in name, refreshed in value):

| Name | Value | Unit | Source |
|---|---|---|---|
| Regulatory revenue drag, median | 0.150 (2026) / 0.450 (2027) / 0.855 (2028) | % of global revenue | `11_regulatory_overlay.csv` |
| Regulatory revenue drag, mean | 0.251 / 0.752 / 1.235 | % of global revenue | same |
| Regulatory revenue drag, p95 | 0.891 / 2.672 / 4.011 | % of global revenue | same |
| EMEA nights drag, median, cumulative | 0.36 / 1.07 / 2.03 | % of EMEA nights | same |
| NA nights drag, median, cumulative | 0.03 / 0.08 / 0.15 | % of NA nights | same |
| Compliance cost (EBITDA), median | 0.130 (end-2027) / 0.160 (end-2030) | % of revenue | `abnb_regulatory_profile.csv` — **an expense, not lost revenue** |
| One-off cash (Spain fine + Chicago), expected | 49.8 (end-2027) / 65.1 (end-2030) | $M | same — **one-off, not run-rate** |

## 9. For the 5 Nov card

Nothing changes. The repair touches the 2027 and 2030 run-rate distributions, not any Q3 2026 line. The
monitoring item that matters before the print is still the 9 September EU Affordable Housing Act text, and the
pre-registered rule in the main note stands: binding quantitative caps or coverage of primary residences moves
EU-AHA's 2030 probability to 65% and the tail to 15% (which, on the corrected sampler, takes the 2030 median from
1.66% to 2.44% and the 90th percentile from 4.15% to 6.52%). Note that under the new nesting the tail's
probability can never be raised above the parent's — an assertion now enforces this, so a future edit that sets
the tail above EU-AHA will fail loudly instead of producing orphan tail draws again.

## 10. Corrections to existing work

- `research/notes/overnight/11_competition-supply-and-overlays.md` line 234: "Two events carry 68% of the 2027
  variance — EU-AHA ... and the EU tail". The pre-fix contributions file gave 38.2% + 37.0% = **75.2%**, not 68%;
  post-fix it is 39.5% + 38.4% = **77.9%**. The 68% appears to be a transcription error predating my change.
- The same note's P(revenue loss >1%) figures (19.5% / 70.7%) are pre-fix values, now 18.9% / 71.0%.
- `research/notes/2026-09-05_regulatory-forecast-profile.md` section 1 previously said the 2030 distribution had
  "8% of mass past 4%". On the corrected sampler it is 11.0%, and 1.6% past 8%. Fixed in place, with the
  correction dated in the new section 0.
- The same note's sensitivity paragraph was labelled "re-run, 100k draws" while the profile it sat next to used
  200k. The refreshed sensitivities are all 200k and say so.

## 11. What I did not do

- I did not change any probability, loss range, correlation coefficient or exposure anchor. If the register's
  numbers are wrong, that is a separate and much harder problem: as the audit says, repairing probability
  mechanics does not create empirical calibration, and these remain single-analyst estimates with no market to
  score them against.
- I did not model within-horizon timing, a reversal/lapse state, or the acknowledged double-count between
  EU-AHA's loss and the national events it would operate through (caveat 3 of the main note). The double-count
  still biases the 2030 mean high.
- I did not touch `13_*`, WS08/15/16 files, or `model/assumptions.md`; section 8 lists what a later agent should
  change there.
