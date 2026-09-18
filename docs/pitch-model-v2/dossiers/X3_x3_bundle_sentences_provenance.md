# X3 — SEC-filed provenance for the two bundle-contribution sentences

## 1. Header
- Line: X3 · Judge's question: "You're hanging the entire bundle magnitude on one CFO sentence from a transcript mirror — where's the SEC filing?"
- Digger: sonnet · Date: 2026-09-18 · Commit: 5d6c577 (branch `theo/pitch-model-v2`)

## 2. The number

| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| disclosed | 4Q25 | 2.0 (nights) | | | growth points | 2026-02-12 call |
| disclosed | 4Q25 | 3.0 (GBV) | | | growth points | 2026-02-12 call |
| disclosed | 1Q26 | 3.0 (nights) | | | growth points | 2026-05-07 call |
| disclosed | 1Q26 | 4.0 (GBV) | | | growth points | 2026-05-07 call |

These four numbers are unchanged from D014/D032 as they sit in the ledger. X3 does not re-derive them; it re-derives
their **provenance**, which is what changes below.

### 2a. Model inputs (machine-readable)

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| bundle_nights_pts | disclosed | 4Q25 | 2.0 | growth points | mirror only (no filed source found; searched 4Q25 8-K Ex 99.1 shareholder letter [d58192dex991.htm], FY2025 10-K, 2Q26 10-Q MD&A) |
| bundle_gbv_pts | disclosed | 4Q25 | 3.0 | growth points | mirror only (no filed source found; searched 4Q25 8-K Ex 99.1 shareholder letter [d58192dex991.htm], FY2025 10-K, 2Q26 10-Q MD&A) |
| bundle_nights_pts | disclosed | 1Q26 | 3.0 | growth points | mirror only (no filed source found; searched 1Q26 8-K Ex 99.1 shareholder letter [d23351dex991.htm], 2Q26 10-Q MD&A; 1Q26 10-Q accession identified but document not fetched, see §3/§8) |
| bundle_gbv_pts | disclosed | 1Q26 | 4.0 | growth points | mirror only (no filed source found; searched 1Q26 8-K Ex 99.1 shareholder letter [d23351dex991.htm], 2Q26 10-Q MD&A; 1Q26 10-Q accession identified but document not fetched, see §3/§8) |

## 3. Derivation chain

This is a provenance search, not a numeric derivation. The chain is: **statement → filing that carries it (if any)**.

1. Ledger claim → `data/processed/overnight2/D/rnpl_statement_ledger.csv`, rows **D014** (4Q25, `official_or_mirror=mirror`,
   `source_key=call_4Q25`, `source_url=https://stockanalysis.com/stocks/abnb/transcripts/396495-q4-2025/`) and **D032**
   (1Q26, `official_or_mirror=mirror`, `source_key=call_1Q26`,
   `source_url=https://stockanalysis.com/stocks/abnb/transcripts/556160-q1-2026/`). Both built by
   `analysis/src/overnight2/D0_rnpl_statement_ledger.py`, whose header states quotes sourced from `data/raw/transcripts/web/*.html`
   are verified verbatim against the cached page only, not against a filing.
2. The two 8-Ks that bracket these calls, on EDGAR:
   - 4Q25 print: 8-K filed **2026-02-12**, accession **0001193125-26-048670**. Directory listing (fetch #3, §4) shows exactly
     one substantive exhibit — **Exhibit 99.1**, `d58192dex991.htm` (the shareholder letter, same file named in ledger rows
     D024/D060 as `letter_4Q25`) — plus 26 JPG page images of that same letter. No transcript, no prepared-remarks exhibit,
     no press release beyond the letter.
   - 1Q26 print: 8-K filed **2026-05-07**, accession **0001193125-26-211816**. Directory listing (fetch #4, §4) shows the
     identical pattern — one Exhibit 99.1, `d23351dex991.htm` (the shareholder letter named in ledger row D031/D042 as
     `letter_1Q26`), plus 27 JPG page images. No other exhibit.
3. Full-text search of those two letters for the bundle sentence. The letters themselves are gitignored out of this
   worktree (`.gitignore:28`, per `nights_v2_design.md` §3.1), but a prior RNPL-keyword full-text extraction of the same
   two files (identical filenames, identical SEC URLs) survives at
   `/Users/theomachado/Citadel-ABNB-untracked/docs/pitch-forecasts/questions/bundle-attribution-quantified/sources/letters_calls_3Q25-2Q26_rnpl_passages.txt`.
   It reports **12 hits** in the 4Q25 letter and **24 hits** in the 1Q26 letter for RNPL-adjacent language, all of them
   shown; none contains "basis points," "points of," or any construction resembling "these three features delivered."
   The 4Q25 letter's RNPL paragraph reads only: *"The positive response from guests was immediate, and this feature
   contributed to the acceleration of bookings we saw in Q4."* — qualitative, no magnitude. The 1Q26 letter's equivalent
   passage gives a different, non-growth statistic: *"roughly 20% of global GBV came from Reserve Now, Pay Later
   bookings"* (a GBV *share*, not a *growth contribution* — this is ledger row D031, already correctly flagged in
   `nights_v2_design.md` §3.1 as a different metric from D014/D032 that cannot be chained to them).
4. FY2025 10-K, `data/raw/regulatory/quantification/abnb_2025_10k.json` (already on disk, official, no fetch needed).
   Its only "basis point" occurrence is interest-rate risk on the investment portfolio (unrelated). Its MD&A driver
   language for GBV is one qualitative sentence: *"The increase in our GBV was primarily due to an increase in Nights
   and Seats Booked, combined with a modest increase in ADR."* No product-level, no points-level attribution.
5. 2Q26 10-Q, `data/raw/regulatory/quantification/abnb_2026q2_10q.html` (already on disk, official, no fetch needed;
   this is the filing `nights_v2_design.md` §3.5 already quotes for the RNPL cancellation-rate risk sentence). Its MD&A
   GBV section: *"the increase in GBV... was primarily due to an increase in Nights and Seats Booked and ADR... The
   increase in ADR was driven in part by the continued adoption of RNPL."* Again qualitative — "driven in part by,"
   no points.
6. 1Q26 10-Q: accession **0001559720-26-000014**, filed 2026-05-07, located via EDGAR (fetch #5, §4), but the document
   itself was **not fetched** — the five-fetch budget was exhausted locating it. This is the one filing named in the
   digger brief that X3 did not directly check; §8 flags it as the next lead if a B-grade upgrade is ever sought.

Conclusion of the chain: at every point where the ledger's `official_or_mirror=official` rows (D012, D013, D024, D031,
D042, D060, the 2Q26 10-Q risk language) could plausibly have carried a bundle-magnitude figure, they carry something
else instead — a date, a policy parameter, a fee rate, a GBV *share*, or a qualitative driver sentence. The magnitude
figures in D014 and D032 exist **only** on the earnings calls, which Airbnb does not file with the SEC in any form
(confirmed structurally by step 2: the 8-K exhibit list has no transcript exhibit for either quarter).

## 4. Governing sources

| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| 2026-09-11 | `data/processed/overnight2/D/rnpl_statement_ledger.csv` (D014, D032) | bundle sentences are `official_or_mirror = mirror`, sourced to stockanalysis.com | governs the raw ledger fact; X3 does not change it |
| 2026-09-18 (est.) | `docs/pitch-model-v2/lines/nights_v2_design.md` §3.1 | states the provenance asymmetry plainly: dates official, magnitudes mirror-only | **governs** the framing X3 confirms; X3 is confirmatory, not corrective |
| 2026-09-18 | `docs/pitch-model-v2/DECISIONS.md` DEC-0031 | tasks a digger to check EDGAR 8-K exhibits; if not found, "the mirror provenance stays flagged in the memo" | X3 is the digger output DEC-0031 asked for; **outcome: not found, flag stands** |
| 2026-09-18 (EDGAR, fetched today) | 4Q25 8-K, accession 0001193125-26-048670, Ex 99.1 `d58192dex991.htm` | no bundle-points sentence present | official, checked, **absent** |
| 2026-09-18 (EDGAR, fetched today) | 1Q26 8-K, accession 0001193125-26-211816, Ex 99.1 `d23351dex991.htm` | no bundle-points sentence present | official, checked, **absent** |
| filed 2026-08-06 | 2Q26 10-Q, `data/raw/regulatory/quantification/abnb_2026q2_10q.html` | qualitative RNPL/ADR driver language only, no points | official, checked, **absent** (confirms D044/nights_v2_design §3.5's characterization) |
| filed ~Feb 2026 | FY2025 10-K, `data/raw/regulatory/quantification/abnb_2025_10k.json` | qualitative GBV driver language only, no points | official, checked, **absent** |
| filed 2026-05-07 | 1Q26 10-Q, accession 0001559720-26-000014 | not checked (fetch budget exhausted) | **open — see §8** |

No note supersedes another here; every governing source independently confirms the same absence.

## 5. Reproduction receipt

- Receipt: `data/processed/pitch_model_v2/receipts/X3/receipt.json`
- Command: `manual EDGAR provenance search` (no script exists for this line — the digger brief itself says so) · Exit: 0 · Wall: n/a (manual) · Interpreter: n/a
- Output: no CSV/artifact is produced; the receipt records the five EDGAR fetches (URL, date, purpose) and the three
  already-on-disk local sources checked in place of a fetch. **Match: n/a** — there is no committed numeric cell to
  reproduce; this line's deliverable is the provenance verdict itself.
- If no: not applicable — see the "Match: n/a" note above; the object under test is a search outcome, not a computed value.

## 6. Test record

No test applies. This line does not produce a forecast object scored against W1/W2 or a pre-registered pass line —
it is a source-provenance check on two already-existing ledger rows (D014, D032). The bundle-contribution *points*
themselves (2.0/3.0 for 4Q25, 3.0/4.0 for 1Q26) are unchanged and continue to be whatever role they already play
upstream in the nights mechanism (see `nights_v2_design.md`); X3 only changes what can be said about where they came
from.

Strongest known failure: none to report in the test-record sense — the search itself failed to find the hoped-for
filed source, which is the substantive finding, not a test failure.

## 7. Kill list and consistency

- Kill-list check: **none.** Neither D014's nor D032's point values, nor any restated version of them, appears on the
  `AGENT_BRIEF.md` §6 kill list or in `RED_TEAM.md`. X3 introduces no new number to check against the kill list — it
  only changes the provenance label already carried honestly as `mirror` in the ledger and in `nights_v2_design.md`.
- Conflicts: none. X3 **confirms** `nights_v2_design.md` §3.1's own framing ("the provenance asymmetry, stated before
  a judge finds it") rather than contradicting it. It also confirms DEC-0031's own contingency: "if not in a filing,
  the mirror provenance stays flagged in the memo." That is the operative outcome.
- Consequence for the memo, by outcome:
  - **If the memo quotes D014/D032 as bundle magnitudes** (as `nights_v2_design.md` currently does), it must keep
    the `mirror` flag visible next to them, or a judge who checks EDGAR (a five-minute check, as this dossier shows)
    will find exactly what X3 found and can fairly characterize the whole bundle-nights mechanism as one unfiled
    quarter of a CFO's rounded mental math, repeated once.
  - The **dates and mechanism categories** (RNPL launch timing, cancellation-policy redesign, fee-tranche dates,
    global scope) remain fully SEC-filed and verbatim-quotable without caveat — X3 does not weaken those legs, only
    the two summary numbers layered on top of them.
  - The **RNPL GBV-share figures** (D031 "~20%," D043 "over 20%") are official but are not substitutes for D014/D032:
    they measure a different quantity (share of GBV transacted via RNPL, not the bundle's incremental growth
    contribution) and cannot be converted into growth points without an undisclosed RNPL-vs-non-RNPL ADR ratio
    (already noted in `nights_v2_design.md` §3.1).

## 8. Open choices

1. **How the memo words the provenance if only a mirror exists.** Options: (a) keep quoting D014/D032 verbatim with
   an explicit inline caveat ("per the earnings call, not filed with the SEC") every time either number appears;
   (b) drop the point figures from the memo's headline claims entirely and cite only the SEC-filed qualitative
   language plus the RNPL GBV-share figures (D031/D043), keeping D014/D032 as background color in an appendix; (c) use
   the numbers to size the mechanism internally (as the model already does) but keep them out of any slide or sentence
   a judge could challenge cold. Recommendation: **(a)**, because the memo's own kernel narrative needs the specific
   magnitude, and a labelled mirror citation is defensible — an unlabelled one is not, and it is the labelling, not
   the number, that a judge is actually testing. Why: DEC-0031 already anticipated this outcome and pre-committed to
   keeping the flag visible; X3's finding just confirms the flag must stay, not that the number must go.
2. **Whether to quote the letters' qualitative language instead, as a hedge.** Options: (a) lead with the SEC-filed
   qualitative sentence ("contributed to the acceleration of bookings we saw in Q4" / "driven in part by the continued
   adoption of RNPL") and treat the call's points figure as color; (b) lead with the points figure and use the filed
   qualitative sentence as the "and it's filed too" corroboration; (c) present both side by side, filed-quote first.
   Recommendation: **(c)** — it is the only option that is both fully defensible and does not throw away the magnitude
   the model needs; it also pre-empts the judge's obvious follow-up ("so what does the 10-Q actually say?") with an
   answer already in hand.
3. **Whether to spend a follow-up fetch on the 1Q26 10-Q MD&A.** The 1Q26 10-Q (accession 0001559720-26-000014, filed
   2026-05-07) was located but not read — X3's EDGAR fetch budget (5) was spent locating and confirming the two 8-K
   exhibit lists and the two 8-K/10-Q accession numbers before a sixth fetch would have been needed to read the 1Q26
   10-Q body. Given the FY2025 10-K and 2Q26 10-Q both show the same qualitative-only pattern, a filed points figure
   in the 1Q26 10-Q would be a genuine surprise, not the expected case — but it is the one unchecked filing named in
   the digger brief. Recommendation: a follow-up digger run (fresh 5-fetch budget) fetching
   `https://www.sec.gov/Archives/edgar/data/1559720/000155972026000014/` directly, before the memo is finalized, to
   close this one gap.

## 9. Judge Q&A

1. Q: "Where is the 8-K that carries the '>200bp nights / ~300bp GBV' and '~3pt nights / ~4pt GBV' sentences?"
   A: There isn't one. Both 8-Ks (accession 0001193125-26-048670 for 4Q25, 0001193125-26-211816 for 1Q26) carry exactly
   one substantive exhibit each — the shareholder letter — and neither letter contains the sentence. Airbnb does not
   file a transcript or prepared-remarks exhibit with either 8-K.
2. Q: "Then why trust the number at all?"
   A: Because it is the same CFO, on the record, on a call the company itself hosts and later relies on in guidance
   language (e.g., the 1Q26 letter's forward-looking references to "the rollout of Reserve Now, Pay Later" as a
   headwind comp) — but the memo should say exactly this, not imply it is filed. The dates, scope (global), and
   underlying mechanism categories (RNPL, cancellation redesign, fee simplification) are independently SEC-filed;
   only the specific point-magnitude of the combined effect is call-only.
3. Q: "Could the ~20% GBV-share figure substitute for the magnitude number?"
   A: No — it measures a different quantity (RNPL's share of GBV transacted, not the three-feature bundle's
   incremental contribution to growth) and the model would need an undisclosed RNPL-vs-non-RNPL ADR ratio to convert
   between them (`nights_v2_design.md` §3.1). It is official corroboration that RNPL is large, not a replacement
   number.

## 10. Grade
Grade: C — no SEC-filed document, of the five checked (two 8-K Ex 99.1 letters, the FY2025 10-K, and the 2Q26 10-Q
MD&A), carries the bundle-contribution figure or an equivalent/directly-supporting quantified statement; both D014
and D032 remain mirror-only. One filing named in the brief (the 1Q26 10-Q) was located but not read before the
fetch budget ran out, and is flagged in §8 as the one remaining lead.
