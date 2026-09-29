# Blind review: memo v4 vs the 24 Sep memo, against the PM's feedback (29 Sep 2026)

## How it was run

- A separate Opus agent reviewed the two memos with no repo access and no labels.
- It saw page images and extracted text of "Memo A" (v4) and "Memo B" (24 Sep, as sent), plus the PM's email verbatim. PDF metadata was removed so it could not tell which version was which.
- It was told that one memo was written before the feedback and one after, and asked to:
  1. turn the feedback into a checklist;
  2. score each memo 0/1/2 per item, with quotes;
  3. say which memo applies the feedback;
  4. rank the gaps that remain in the better memo;
  5. flag asks that would be a mistake to follow literally.

## Result

**Scores:**

| Memo | All 26 checklist items (max 52) | The PM's own 24 asks (max 48) |
|---|---|---|
| A (v4) | 41 | 38 |
| B (24 Sep) | 10 | 9 |

**Verdict:** A applies the feedback. Confidence about 95%, on content alone.

**Where A scored low:**
- FX missing from the "illusion" (0).
- Graph-1 logic kept in prose as "three largest falls" (1).
- Liquidity asserted, not shown (1).
- AI rebuttal self-contradicting: "next year" is inside a 12-month horizon (1).
- Meta/Vrbo conclusion left implicit (1).
- Partnering argued on cost only (1).
- Loyalty argued as a cost only (1).
- No bull price or stop (1).

## What was done with each ranked gap

| # | Reviewer's gap | Action |
|---|---|---|
| 1 | "Underlying ~7% heading to ~6%" vs the chart's 3Q26 underlying 7.8%; "five straight quarters" is wrong (4Q25 9.8 → 1Q26 9.2) | **Fixed.** The re-acceleration is now "to +10.3% in 2Q26". The thesis says "~7% … heading to ~6% by 2H27". The Graph 1 takeaway says "~7-8% in 2H26 and ~6% by 2H27". The 3Q26 residual itself stays an open team item (CHANGES §3.4). |
| 2 | AI rebuttal defeats itself; Meta conclusion implicit; partnering argued on cost only | **Fixed.** The agent is framed as another conversion feature: a one-time level shift launching in 2027 that reaches reported nights late in the window. "Muse is share risk for Airbnb, not upside" (Expedia, Vrbo's parent, is in). Partnering means paying for free traffic. Change-of-mind trigger: a distribution deal with disclosed volume. |
| 3 | The 4Q guide "miss" was defined against "low double digits", but the Street's 4Q26 is already +9.9% | **Fixed.** The miss is now a revenue guide below $3.16bn with nights guided to "high single digits" or lower. The cover rule is the mirror: 3Q26 nights ≥10.3% **and** the 4Q26 guide meets the Street. |
| 4 | No bull case, stop or reward/risk | **Partly.** Added the upside marker: the $178 post-print close (7 Aug), +18%. A stop and R/R are team decisions (CHANGES §3.7). |
| 5 | Target not decomposed; multiple anchor dropped; NTM applied to today's NTM | **Partly.** Added "our EBITDA is 12% below consensus and the multiple falls 10% (14.9x → 13.4x)". Arithmetic: 14.925/17.028 = 0.877; 13.425/14.925 = 0.899. **Not changed:** the Cover's method (current NTM at a compressed multiple), which is the team model's. See CHANGES §3.9. **Not added:** "near historical trough". The 13.3x trough (Nov 2025) is on a guide-proxy basis that the repo says reads ~1.5 turns below a consensus basis, so the claim would not survive a check. |
| 6 | Stays index: data cut-off; visible misses; thin margin; "use the 2Q26 gap as bundle-inflation evidence" | **Cut-off fixed:** "(reviews through August)". **"8%" softened** to "under a 10% chance". **2Q26 gap: not used.** The team's pre-registered Stage C test found "no measurable RNPL signature in stays" (mean gap inside the ±band; `docs/revenue-forecast-strategy/05_backtests/REVIEWS_INDEX_v2.md` lines 311–326), so the memo would contradict its own test. The visible misses stay on the chart, which is honest. |
| 7 | FX missing from the illusion | **Fixed.** Setup: "FX added 3–4pts to reported revenue growth in 1H26" (letters, via memo v3). Illusion paragraph: "FX, a tailwind all of 2026, fades from 4Q26". The 4Q26 FX step is not quantified, because of the kill list's −3.4pp item. |
| 8 | "Three largest post-print falls" is n=3, selected on the outcome | **Deleted.** |
| 9 | Density | **Partly.** RNPL spread, macro, external-series list, AI and buyback sentences shortened. Page 2 remains text-heavy; the two charts sit on page 1 by design. |
| 10 | Liquidity asserted | **Open.** ADV, days to cover and borrow are not in the workbook, and web values were unverifiable this session (CHANGES §3.1). |
| 11 | Arithmetic and labels | −20.6% → **−20.7%** ($120 / $151.39 − 1 = −20.73%; the pack's −20.6% is on $120.19). "$255" now labelled North America. The listing-flat vs same-listing-shrinking pair is reconciled in one clause. "$0.93bn" is kept: 5,826.4 − 4,894.7 = 931.7. "4.1pts" is now "~4pts": 11.65 − 7.51 = 4.14, where the reviewer's 4.2 came from rounded inputs. "34.5%" is labelled "on our costs". |
| 12 | Loyalty only as a cost | **Fixed.** Added "a launch at a print is a headline risk we size for". |
| 13 | Buyback: the PM's reload-with-the-guide scenario | **Fixed.** Added "a reload with the 5 Nov guide would cushion day 1, which is why we do not trade day 1". The n is not added for space: the four authorization-day returns are in CHANGES. |
| 14 | Regulation evidence stale or outside the horizon | **Fixed.** Now "Regulators cap supply where Airbnb is densest", i.e. long-run, not a 12-month driver. |

## The reviewer's "do not follow literally" notes (agreed)

- **Macro:** fuel cuts both ways (drive-to), and higher rates raise interest income. The memo says it does not lean on macro.
- **"EBITDA will drop 15%":** it is 16% below the Street, not an absolute fall (FY27 $4.89bn against FY26 $4.82bn). The memo says "below the Street's".
- **AI:** an option can be bounded, not dismissed. The rebuttal now bounds it by timing, size and a trigger.
- **"Attenuating, low-volatility short":** not promised. The memo says estimate cuts over several prints and does not trade day 1.
- **The PM's own figures ($122, ~22%, 15%):** replaced by the model's ($120, −20.7%, −16%).
