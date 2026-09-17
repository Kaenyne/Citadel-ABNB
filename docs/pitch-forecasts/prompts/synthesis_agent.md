# Synthesis and memo-update agent prompt (final stage; Fable)

You are the synthesis agent in Krish's pitch-forecasts run. Repository root `C:/Users/krish/citadel-abnb` (branch
`krish/pitch-forecasts`). You may write: `docs/pitch-forecasts/SYNTHESIS.md`, `docs/pitch-forecasts/MEMO_CHANGES.md`,
`deck/drafts/memo_v3_short_2026-09-17.md` (a NEW file; copy of memo_v2 with the audited numbers), `deck/drafts/memo_v3_short_2026-09-17.html`
(new; from the v2 HTML) and `deck/drafts/ABNB_short_memo_draft_2026-09-17.pdf` (new; rendered from the v3 HTML). Do not modify any
other file; do not touch memo_v2 files (copy, never overwrite).

## Read first

1. `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`, `RUN_STATE.md` (the ledger holds every SYNTHESIS NOTE, DATA NOTE, MEMO FIX and
   CONVENTION NOTE the orchestrator queued during the run: read them all).
2. `docs/pitch-forecasts/forecast_table.csv` (one row per question: final number, CI, anchor, EV, materiality, audit-only flag;
   regenerate with `py -3.13 analysis/src/pitch_forecasts/aggregate.py`).
3. Every `docs/pitch-forecasts/audits/<batch>-audit-response.md` (the final tables) and, for the audit-only batches A14 and A18, the
   audits themselves (`A14-research-audit.md`, `A18-research-audit.md`) plus the `.audit_only` markers (adopt the auditor's numbers).
4. The adopted objects: `questions/risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json`,
   `questions/risk-q4-nights-print-meets-street/datasets/adopted_q4_states_v2.json`, `questions/risk-q4-us-revpar-strong/datasets/r11_v2_joint_object.json`,
   `questions/scenario-probabilities/forecasts/2026-09-17-forecast.json` (X01, with its `scenario_table` block) and its audit response.
5. The memo: `deck/drafts/memo_v2_short_2026-09-16.md`, `memo_v2_short_2026-09-16.html`, and `docs/pitch-forecasts/examples/` is not needed.

## Write `docs/pitch-forecasts/SYNTHESIS.md`

- One-paragraph bottom line: what the flow changed in the pitch's numbers and what it did not.
- **Table 1, every question**: id | question (short) | final (rev) | CI or vector | auditor's independent number | anchor | |final − anchor| |
  audit verdict (one phrase) | notes. Use revision-2 numbers; for audit-only batches use the auditor's number and say so.
- **Table 2, risks and bonus items ranked by |EV|**: id | P | stock impact $/share | EV | material (≥ $1/share) | one-line mechanism.
  State how many of the 16 risks and 17 bonus items clear the bar (Krish's question: "surface 15, see how many are material").
  Use ONE stock convention for every row (joint-solve repricing only, no February reaction added; the R16/B13 mirror pair must be
  symmetric) and say so.
- **The 5 Nov scorecard**: the pre-registered tells with their probabilities (C01, C02, C04, C05–C08, C11, C12, R01/R02 states) in
  one table, plus the conditional day-1 and 15 Dec distributions per X01 scenario.
- **Coherence and data-defect notes**: the objects the run adopted late (print states, Q4 object, RevPAR object, ADR joint) and which
  logs still quote superseded values; the driver-history SBC series and the guidance ledger's `sbc_yoy_pct` (wrong); the Kalshi
  `updated_time` misreading; the capital-return cash-vs-trade basis; the C04 3Q26 margin sd; C11's implied ~0.73 on the joint ADR
  model. Do not edit tracked data; list them.
- **Open decisions for Krish before 2 Oct** (from the ledger and the responses): the X01 reading (literal vs material), B08's
  10-K purchase-obligation convention, the 4Q26 hosting line, F03's convention, the S02/S04 rev-2 vs A09 state vector, etc.
- **Method note**: the flow as run (Fable → Astra for A01–A09; Opus auditors for A10–A19 after Codex exhausted its credits; audit-only
  for A14/A18), the two session-limit outages, agent counts, and how to re-run when the September Inside Airbnb dumps land
  (re-run E, then `a09_v2_print_distribution.py`, then `x01_joint.py`).

## Update the memo (v3 files), with every change logged in `docs/pitch-forecasts/MEMO_CHANGES.md`

Change only numbers and the sentences that carry them; keep the structure, voice and length. Specifically:
1. Scenario table: replace 25/45/30 with X01's vector (state the reading you chose and why; add the "none of the above" row or fold
   it in and say so); replace the day-1 precedent cells with S01 rev 2's conditional cells (the base-case cell is a median of about
   −5%, P(≤ −8%) ≈ 0.37, not −8 to −13%; the unconditional median −2.1%, P(≤ −8%) 0.27); replace the price rows with S02 rev 2's
   conditional 15 Dec medians and P(≤$150)/P(≤$143); recompute the probability-weighted price; keep the memo's 12-month fundamental
   targets as a separate, labelled row ("joint-solve fundamental target") so the reaction-function numbers and the valuation targets
   are not mixed.
2. Header line: the target and PW price consistent with 1.
3. "Why nights and the guide": keep the historical facts; fix "6 of 6" to "5 of 6 positive, 3 of 6 ≥ +5%" wherever it appears
   (catalysts and risks too).
4. Estimates vs consensus: unchanged (they are the model's numbers), but the nights row's model path note stays.
5. Risks and mitigants: attach each risk's audited probability in parentheses (R01 0.39, R02 0.26, R03 0.11, R04 0.52, R05 0.22,
   R07 0.17, R14 0.26 …); drop or merge the immaterial ones per Table 2 (keep at most six risk bullets); the "12 of 13 guided
   prints" fact stays.
6. Bonus section: keep only the material items (B02, B08, B12, B13, B17 and the B05/B01 sentences if you judge them useful) with
   their probabilities and impacts; state the EV bar.
7. Anywhere the memo quotes a probability or a conditional (e.g., "P(EBITDA beat) 0.78", the Q4-guide-below-Street precedent), make
   sure it is consistent with the run's numbers or labelled as a historical base rate.
8. Keep the memo at roughly its current length; the PDF must stay ≤ 3 pages. Render with:
   `"C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="<abs pdf path>" "file:///<abs html path>"`
   then check page count with `py -3.13 -c "import pypdf; print(len(pypdf.PdfReader(r'<pdf>').pages))"` and rasterise page 1–3 with
   pypdfium2 to confirm the layout did not break.

`MEMO_CHANGES.md`: a table of every change (section | v2 text | v3 text | source question/response), plus the list of things you
deliberately did not change and why.

Reply with the X01 vector you adopted, the new PW price, the material risk/bonus lists, the PDF page count, and the three most
important things Krish should read first. Do not paste the documents.
