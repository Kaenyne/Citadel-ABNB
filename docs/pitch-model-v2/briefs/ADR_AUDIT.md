# Brief — adversarial audit of the ADR line (line 2 of pitch model v2)

You are auditing one line of the ABNB pitch model: **ADR, the average daily rate (GBV ÷ Nights and Seats
Booked)**. This work will be judged by a hedge-fund travel-and-lodging analyst at the Citadel Intercollegiate
Stock Pitch Competition. The preliminary memo is due **2 October 2026**; finals are 22–24 October; the 3Q26
print lands 5 November, after finals.

**Your job is to break it, or to certify that you could not.** Confirming it is a valid and useful outcome, but
only after a genuine attempt to falsify it. Do not be agreeable. The authors of this line would rather be
corrected now than in front of a judge.

Workspace: `~/Citadel-ABNB`, branch `theo/pitch-model-v2`. Run every command from that root with `python3`.

---

## 1. Read first, in this order

1. `CLAUDE.md` — the repo rules. They bind you.
2. `docs/pitch-model-v2/lines/final_adr.md` — **the governing document.** The complete rationale, 13 sections.
3. `docs/pitch-model-v2/lines/adr_fx_prereg.md` — the pre-registration (blob `0495e5f3`), written before any fit.
4. `docs/pitch-model-v2/lines/adr_v1_design.md` — the construction in full.
5. `docs/pitch-model-v2/lines/adr_v2_geomix_prereg.md` and the four upgrade notes `adr_v2_upgrade*.md`.
6. `docs/pitch-model-v2/lines/adr_v2_mitigation_A/B/C/D_*.md` — the four mitigations of 22 Sep.
7. `docs/pitch-model-v2/DECISIONS.md`, entries **DEC-0016, DEC-0020, DEC-0034 through DEC-0041**.

Where a later note contradicts an earlier one, the later governs — but **say which superseded which**, because a
stale number surviving in one document is itself a finding.

## 2. Reproduce before you argue

```bash
cd ~/Citadel-ABNB
PYTHONPATH=analysis/src python3 -m pitch_model_v2.adr_engine.run                       # ~3 min with the posterior
PYTHONPATH=analysis/src python3 -m pitch_model_v2.adr_engine.run --no-posterior --no-workbook   # ~20 s
PYTHONPATH=analysis/src python3 -m pytest analysis/src/pitch_model_v2/adr_engine/tests -q        # 27 tests
```

Outputs land in `data/processed/pitch_model_v2/adr_engine/`. If a number in a document does not appear in an
output file, that is a finding. Report exit codes.

## 3. The claims, ranked by how much weight they carry

Attack in this order. The first three decide whether the line survives.

**C1 — The core is 3.849pp, carried flat, and unexplained.** It is roughly 40% of the ex-FX number and 1.58pp
above its own 2023–25 mean of 2.272, with no filed mechanism. Everything in the line that matters for the pitch
rests on it. Ask: is carrying it flat defensible for six quarters? Does its 0.88pp one-quarter error understate
the risk at h=4 or h=6? Is there anything in the repo that identifies it that the authors missed?

**C2 — The composition case does not reach below the Street, and the document says so.** 4Q26 alternatives run
$172.18 to $173.19 against a Street of $171.33; only core assumptions cross ($171.71 lap-only, $170.60 mean
reversion). Verify this ladder from `adr_scenarios.csv`. **If you can find a defensible composition route below
the Street that respects DEC-0016, that is the single most valuable finding you can return.** If you cannot,
say so plainly.

**C3 — The FX identity is promoted although a comparator scores better.** The euro-only OLS has the lowest RMSE
ratio in all four promotion cells (0.27–0.28 against the identity's 0.30–0.38). The defence is threefold: the
pre-registration excluded V2/V3 before any variant ran; the euro fit's bias is −0.27 to −0.34pp in every cell
against the identity's near-zero; and it is blind to the peso, real and Australian dollar, which contribute
+1.08pp of the +0.42pp 3Q26 effect. **Test that defence.** Is the bias stable out of sample or an artefact of
the window? Would a two- or three-currency fit beat both? Note this is live money: the committed card's −0.43
FX leg is built on the same euro fit and inherits the bias.

**C4 — The reconciliation rests on one region.** Pooled slope 1.127 across 23 disclosed regional prints
(cluster-by-region p 0.042, 90% interval 0.349–1.905, cannot reject 1.0), but dropping Latin America takes it to
−0.302, and the EMEA-only reading is window-dependent (1.085 on n 7, −0.381 on n 9). Latin America's comparator
is Brazil alone at 24–33% coverage. **Pulling INEGI (Mexico) and INE Chile accommodation series to broaden that
comparator is a named open item — if you can do it, do it.**

**C5 — The bundle's ~1pp is transcript-only.** The authors claim the search is exhaustive across the FY25 10-K,
the 1Q26 and 2Q26 10-Qs and both shareholder letters. **Try to falsify that claim.** One filed magnitude would
change the evidence label on a term that swings 4Q26 by half a point.

**C6 — The sub-regional term failed its own forecast test** (H2 ratios 0.909 W1 / 0.719 W2 against a 0.75 line
on both) and is carried as attribution only. Check that it is nowhere in the base. Check the panel's blind
spots are stated honestly: no Indian, Emirati, Malaysian, Indonesian or Vietnamese market; Australia is 57% of
the panel's APAC stays.

**C7 — The market-level utilisation panel failed** (elasticity +0.083, p 0.794). Confirm it is reported as a
failure and not quietly reused.

## 4. Two issues the authors already flagged — verify and extend

- **Mean-reversion uses the wrong mean.** `exfx.CORE_MEAN_2023_25 = 2.398` is the 2023–25 mean of the
  **residual**; the **core's** own mean is 2.272. A like-for-like reversion gives 4Q26 ≈ $170.39 rather than the
  filed $170.60. Worth $0.21, runs against the short. Flagged, not corrected, because $170.60 sits inside
  proposed DEC-0035. **Decide whether it should be corrected and say so.**
- **4Q27 FX is exactly 0.000** because both it and its base quarter are spot-held. Confirm the document labels
  this an artefact everywhere it appears, and that no downstream line quotes the point.

## 5. Specific numbers to verify

Recompute, do not accept:

| object | claimed |
|---|---|
| identity vs disclosed FX effect | closes ≤ 0.042pp on 14 quarters |
| walk-forward ratio, four promotion cells | 0.344 / 0.303 (W1 O2/O3), 0.383 / 0.317 (W2 O2/O3) |
| bootstrap 90% upper, same cells | 0.438 / 0.369 / 0.509 / 0.418 |
| 3Q26 / 4Q26 FX | +0.415pp / +0.514pp |
| 3Q26 / 4Q26 ADR | $177.68 / $173.03 |
| bands (half-width) | ±0.978pp / ±1.932pp |
| P(print ≥ Street) | 0.645 / 0.701 |
| geo-mix method vs the H term | within 0.13pp on 2Q24–2Q26 |
| annual mix vs the 10-K, 2023–25 | −1.10 / −1.33 / −1.67 vs −1.08 / −1.24 / −1.58 |
| sub-regional term | mean −0.453 (1Q23–2Q26), −0.152 (last four to 2Q26), forward −0.137 / −0.147 |
| origin rotation | non-English +81.0% vs English +40.0%; 13.4% cheaper within market; −0.35%/yr |
| size-mix 2025, hedonic route | +0.739pp, inside the filed bracket [+0.42, +1.29] |

Watch for two traps the authors hit and fixed, because similar files exist elsewhere:

- **Long-format tables that mix aggregate levels with leaf rows.** `origin_lang_rotation_ltm.csv` carries a
  `GLOBAL` row *and* four region rows, plus `TOTAL` and `ALL_NON_EN` pseudo-languages. A naive `groupby().sum()`
  triple counts and returns +66% where the truth is +81%.
- **Partial quarter-to-date rows past the history cutoff.** `geomix_subregional_term.csv` carries a partial
  3Q26 row; a positional `iloc[-4:]` picks it up and drops 3Q25.

## 6. Hard rules

1. **Do not scrape beyond the sanctioned sources.** Inside Airbnb dumps and the existing fee-panel capture only.
   Anything else touching `airbnb.com` is a terms-of-service decision for a human — **stop and ask**. Public
   SEC filings and press releases are fine; at most five web fetches, each logged.
2. **Never type credentials.** SSO button clicks are fine; passwords and two-factor codes are not.
3. **Do not commit, and do not push.** Write your audit to
   `docs/pitch-model-v2/dossiers/ADR_AUDIT_<yourname>.md` and nothing else. Receipts may go under
   `data/processed/pitch_model_v2/receipts/ADR_AUDIT/`.
4. **Nothing on a kill list may be quoted as ours** — see `AGENT_BRIEF.md` §6 and the README of
   `model/ABNB_margin_model.xlsx`.
5. **DEC-0016 binds you too.** Do not propose an input chosen to reach a price or a target. If you find a route
   below the Street, it must be the mechanical consequence of a stated assumption, and you must state the
   assumption first.
6. **You do not decide.** List choices for the humans with options and a recommendation.
7. Do not modify anything under `analysis/src/forecast_methods/`, `data/processed/forecast_methods/`,
   `docs/revenue-forecast-strategy/` or `model/`.

## 7. What to return

A dossier with, in this order:

1. **Verdict in one sentence.** Does the ADR line survive a hostile read, yes or no.
2. **Reproduction**: what you ran, exit codes, which claimed numbers reproduced and which did not, with the two
   values side by side for every mismatch.
3. **Findings, ranked by how much they move 3Q26 or 4Q26 ADR in dollars.** For each: the claim, the evidence
   against it, the size of the error, and whether it helps or hurts the short. A finding that helps the short is
   not more valuable than one that hurts it — report both the same way.
4. **The C2 question answered explicitly**: is there a defensible composition route below the Street, or not.
5. **Anything the documents assert that the output files do not support.**
6. **Open choices for the humans**, numbered, each with options and your recommendation.

Be specific. "The core is weak" is not a finding; "the core carry's h=4 error is 2.1pp, not 0.88pp, so the
1Q27 band is understated by X" is. Quote file paths and line numbers. If you cannot break something, say that
clearly — a clean bill of health from a real attempt is worth more than a list of quibbles.
