# -*- coding: utf-8 -*-
"""Workstream 19: triage of the independent audit handoff, and the ledger of repairs applied.

READS   nothing at runtime. Every row records a check made by hand against the working tree at
        C:/Users/krish/citadel-abnb-overnight (branch krish/overnight-synthesis, HEAD 77037c2) on
        6 September 2026, against the handoff document
        C:/Users/krish/citadel-abnb/docs/2026-09-06_audit_findings_ai_handoff.md.

WRITES  data/processed/overnight/19_audit_triage.csv     one row per finding
        data/processed/overnight/19_repairs_applied.csv  one row per change made to the tree

CSV serialisation rules (the same two the WS19 pass applied to the WS15 files):
  - no cell may begin with = + - or @, because Excel parses such a cell as a formula. Cells that
    naturally start with a sign are written with ONE leading space; strip() them if you parse this
    with pandas.
  - the writer asserts the table is rectangular and free of embedded newlines before it returns.

RUN   py -3.13 analysis/src/overnight/19_audit_triage.py
"""
import csv
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
OUT = os.path.join(ROOT, "data", "processed", "overnight")
FORMULA_LEAD = ("=", "+", "-", "@")


def safe(v):
    v = "" if v is None else str(v)
    return " " + v if v[:1] in FORMULA_LEAD else v


def write_csv(name, header, rows):
    path = os.path.join(OUT, name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows([[safe(c) for c in r] for r in rows])
    with open(path, newline="", encoding="utf-8") as f:
        back = list(csv.reader(f))
    assert len(back) == len(rows) + 1, f"{name}: row count mismatch"
    for i, r in enumerate(back):
        assert len(r) == len(header), f"{name}: row {i + 1} has {len(r)} fields"
        for cell in r:
            assert "\n" not in cell and "\r" not in cell, f"{name}: embedded newline row {i + 1}"
            assert cell[:1] not in FORMULA_LEAD, f"{name}: formula-leading cell row {i + 1}"
    print(f"{name}: {len(rows)} rows x {len(header)} columns, integrity checks passed")


# ---------------------------------------------------------------------------------------- triage
# id | section | finding | files_affected | audit_proposed_repair | status_on_head | decision |
# owner | severity | effort | evidence_or_reasoning
TRIAGE = [
("A01", "3", "A purported pre-print backlog feature divides by the target quarter's ACTUAL revenue, so future revenue leaks into the predictive tests",
 "analysis/src/overnight/08_altdata_backtests.py backlog_features(); data/processed/overnight/08_feature_tests_all.csv, 08_backlog_tests.csv",
 "Remove the feature or replace its denominator with a value known at the decision cutoff; regenerate affected test tables",
 "still open (reproduced on HEAD 77037c2)", "fix now - DONE", "WS19", "high", "medium",
 "Confirmed: unearned_to_next_q_revenue at q is unearned[q]/revenue[q+1] (negative shift in analysis/src/abnb_eu_platform_and_backlog.py), so .shift(1) gives unearned[t-1]/revenue[t]. Fixture: perturbing 2025Q4 revenue moved the old feature at 2025Q4 and does not move the replacement. 6 of the 598 test rows used it; it was never a reported survivor (best wf_ratio_vs_ar1 0.951), so no headline number moves"),

("A02", "4", "Reaction tests use leave-one-out (future observations inform earlier fits) and a return window that starts before the released surprise exists, so they are not a tradable out-of-sample test",
 "analysis/src/overnight/04_reaction_vs_consensus.py loo_r2(); analysis/src/abnb_from_theo_guidance.py; theos-past-research/src/abnb_guidance/market.py; data/processed/overnight/16_reaction_tests.csv",
 "Split a pre-earnings forecast task from a post-release reaction task; expanding/rolling temporal validation; executable entry time",
 "still open (loo_r2 present at 04_reaction_vs_consensus.py:39)", "reassigned - agent 20", "agent 20", "high", "large",
 "Verified the code shape only. This changes a research conclusion, not a mechanical defect, so WS19 did not touch it"),

("A03", "5", "Window sensitivity, multiple testing and data-vintage controls are incomplete; the funds-held survivor flips from 0.59x to 1.85x AR(1) on a window change",
 "data/processed/overnight/08_feature_tests_all.csv, 08_survivor_robustness.csv, 08_backlog_tests.csv; research/notes/overnight/08_altdata-index-and-backtests.md",
 "Pre-register a limited candidate set, freeze transformations and windows, store vintage metadata, publish window sensitivity",
 "still open; WS15 CONF-07 already names it", "reassigned - agent 20", "agent 20", "high", "large",
 "Confirmed the two windows still coexist in 08_backlog_tests.csv. A research gate, not a repair"),

("A04", "6", "Partial Inside Airbnb snapshots contaminate year-ago retention and matched-review pairs (25 of 103 pairs touch a partial dump; Paris shows 33% retention against a partial snapshot)",
 "analysis/src/inside_airbnb_supply_panel.py; data/processed/inside_airbnb_like_for_like.csv, inside_airbnb_city_snapshots.csv",
 "Attach coverage flags to both pair endpoints and exclude or clearly label non-comparable pairs",
 "still open; the script is present in this tree", "reassigned - agent 21", "agent 21", "medium", "medium",
 "Not re-derived by WS19; outside the overnight folders"),

("A05", "7", "Common Crawl year-over-year uses a four-ROW shift on a quarterly series with missing quarters, so it is often not four calendar quarters",
 "analysis/src/overnight/08_altdata_backtests.py cc_features(); data/processed/overnight/08_panel_quarterly.csv, 08_supply_index_quarterly.csv, 08_test_scoreboard.csv",
 "Reindex to a contiguous quarterly PeriodIndex before the four-quarter difference; leave gaps missing",
 "still open (reproduced on HEAD)", "fix now - DONE", "WS19", "medium", "small",
 "Confirmed and quantified: informative crawls skip 2023Q3, 2024Q3 (as a t-4 partner), 2025Q4. 7 of the 12 shifted comparisons were not t vs t-4, including the audit's three examples exactly (2023Q4 vs 2022Q3, 2026Q1 vs 2024Q4, 2026Q3 vs 2025Q2)"),

("A06", "8", "The regulatory simulation samples the EU tail without gating it on its stated parent event, mis-states the Barcelona conditional probability, and renews residuals so 2027 and 2030 are not a coherent path",
 "analysis/src/abnb_regulatory_forecast.py EVENTS and draw(); data/processed/overnight/11_regulatory_overlay.csv",
 "Model the parent-child relationship explicitly, decide whether the quoted probabilities are conditional or marginal, and rerun the overlays",
 "still open; EU-TAIL gates text present but draw() does not gate", "reassigned - agent 22", "agent 22", "medium", "medium",
 "Confirmed by reading EVENTS (line 44, gates= is prose only) and draw() (line 108). Not re-simulated by WS19"),

("A07", "9", "Reproducibility: missing dependencies, absent builders, machine-specific paths, no documented build order",
 "requirements.txt; analysis/src/overnight/16_merge_and_rerun.py, 17_scenario_switch.py; data/README.md",
 "Declare dependencies, resolve paths from the project root or CLI, publish an ordered build graph, mark superseded notes",
 "PARTLY NOT REPRODUCIBLE in this tree: requirements.txt here already lists scipy, statsmodels and pyarrow (it has duplicate lines, which is cosmetic), and analysis/src/overnight/ is present. The dependency and missing-builder complaints are about MAIN",
 "reassigned - agent 24 (path items) / disagree in part (dependency items)", "agent 24", "medium", "medium",
 "Verified requirements.txt in the overnight tree: pandas numpy matplotlib openpyxl yfinance jupyter duckdb requests pyarrow statsmodels requests statsmodels scipy. The audit's own text scopes this finding to MAIN"),

("A08", "10", "The options event-variance estimator recovers E*(1-T_near/T_far), not E, and expiry selection does not require the expiry to follow the event",
 "analysis/src/abnb_options_ledger.py (MAIN only); data/processed/overnight/09_implied_move_live.json",
 "Require a verified event timestamp and an expiry after it, or downgrade to a labelled straddle/IV measure",
 "NOT REPRODUCIBLE in this tree: analysis/src/abnb_options_ledger.py does not exist under C:/Users/krish/citadel-abnb-overnight; it is uncommitted work in MAIN",
 "reassigned - agent 23", "agent 23", "medium", "medium",
 "Checked the path directly. The algebra in the handoff is correct on its face and WS19 does not dispute it"),

("A09", "11", "Two records of the WS16 news CSV have an unquoted publisher containing a comma, giving eight fields against a seven-field header; pandas.read_csv raises",
 "data/processed/overnight/16_news_since_5sep.csv (physical lines 15 and 16)",
 "Quote/serialise the publisher field properly, preserving all values",
 "still open (reproduced: csv.reader gives 8 fields on rows 15 and 16)", "fix now - DONE", "WS19", "medium", "small",
 "Confirmed byte-for-byte. Repaired by quoting the two publisher fields; the file now parses to 20 data rows x 7 fields in both csv.reader and pandas"),

("A10", "12", "The workbook's reverse-DCF ladder divides by (cost of equity minus growth), so it returns #DIV/0! when the assumed ten-year growth equals the discount rate, even though the finite stream has a value there",
 "analysis/src/overnight/13_excel_builder.py rdcf(); model/ABNB_driver_model.xlsx Valuation!B54:C63 and the staleness-check row",
 "Use an explicit finite sum or a stable limit branch in Excel; keep the Gordon terminal's invalid-input behaviour",
 "still open (reproduced in Excel: setting Inputs!D11 to 11% made Valuation!B59 and C59 read #DIV/0!)", "fix now - DONE", "WS19", "medium", "small",
 "Acceptance test in Excel 16.0 via COM. Old workbook: coe 10.5% -> B59 215.13; coe 11% -> #DIV/0!; coe 10.99999% -> 201.02. New workbook: coe 11% -> 201.02, matching both the neighbouring rate and the Python mirror dcf_constant(4827,0.11,10,0.11,0.03) -> 201.02"),

("A11", "13", "16_merge_and_rerun.py cannot append a new earnings quarter (it raises SystemExit) and only recomputes a derived surprise when the cell is already blank; it also runs at import time from a hard-coded root",
 "analysis/src/overnight/16_merge_and_rerun.py; data/processed/overnight/16_consensus_at_print_merged.csv, 16_reaction_tests.csv",
 "Add an append path with schema validation, recompute derived fields from primitives, move behind a main entry point and a project-relative root",
 "still open at the start of the run; WS19 had already rewritten the script before the scope change, so the SCRIPT in the tree now carries the fix while the DATA outputs were restored to their committed state",
 "reassigned - agent 24 (WS19 edit left in tree, outputs reverted)", "agent 24", "medium", "medium",
 "Measured effect of the rewrite before reverting the data: eps_surprise_pct is derived for 2020Q4 ( -33.81), 2021Q1 ( -82.243) and 2021Q2 ( 73.171), which WS16 had supplied consensus and actual for but never derived. That moves uni_eps_surprise_pct from n 17/17/16 to n 20/20/19 at 1d/5d/20d and shifts permutation p-values; no EPS spec becomes predictive either way (loo_r2 stays at or below +0.07)"),

("A12", "14", "Model conventions needing an explicit decision: forward-versus-present valuation date, and a share roll that starts from a weighted-average count but is labelled period-end",
 "analysis/src/overnight/13_driver_model.py valuation(); model/assumptions.md; research/notes/overnight/13_driver-model-build.md",
 "Choose and label the convention; document the share-count approximation or build a precise bridge",
 "open question, not an arithmetic error (WS19 agrees with the audit's framing)", "judgment call for Krish", "agent 25", "medium", "n/a",
 "Not a defect. Changing it changes the headline valuation, so it must be Krish's call"),

("A13", "15", "17_excel_audit.py and 17_scenario_switch.py print mismatch counts but always exit 0, so a passing process is not a passing model audit",
 "analysis/src/overnight/17_excel_audit.py, 17_scenario_switch.py",
 "Return a nonzero status for material reconciliation failures while keeping informational static-scan findings separate",
 "still open at the start of the run; WS19 had already patched both before the scope change and the edits are left in the tree",
 "reassigned - agent 24 (WS19 edit left in tree)", "agent 24", "medium", "small",
 "Both scripts now return 0/1 from main() and raise SystemExit(main()). Verified live: 17_excel_audit.py prints PASS 216/216 and 2349 formula cells, exit 0; 17_scenario_switch.py prints PASS 141 comparisons, exit 0"),

("R01", "16", "FY2026 share-count double-counting",
 "analysis/src/overnight/13_driver_model.py, 13_excel_builder.py; data/processed/overnight/18_share_fix_delta.csv",
 "Already repaired in commit 77037c2 - do not repair again",
 "already fixed - verified", "no action", "-", "n/a", "n/a",
 "Re-verified: SHARE_ROLL_NETS_1H26 present, 13_driver_model.py rebuild prints FY26 shares 589M, FY27 575M, FY28 562M, reconciliation 216 checks / 0 mismatches"),

("R02", "16", "Workbook mechanics and WS16 synthesis integration",
 "model/ABNB_driver_model.xlsx; data/processed/overnight/17_*.csv; research/notes/overnight/14_master-synthesis.md",
 "Already repaired in commit 77037c2 - preserve",
 "already fixed - verified", "no action", "-", "n/a", "n/a",
 "Re-verified after the WS19 rebuild: 5,547 cells dumped from Excel 16.0 with 0 error cells, 216/216 named outputs, 2,349/2,349 formula cells, scenario switch 141 comparisons and 0 mismatches"),

("S01", "16", "The red-team allegation that the ~50% single-service-fee coverage figure was invented is itself wrong; the figure is in the 2Q26 call",
 "data/processed/overnight/15_cross_note_conflicts.csv CONF-11; 15_claim_checks.csv; research/notes/overnight/15_red-team.md",
 "Withdraw the allegation (WS16 already did for the synthesis)",
 "still open in the WS15 files at the start of the run", "fix now - DONE", "WS19", "medium", "small",
 "Primary source checked: data/raw/regulatory/transcripts/2026-Q2.txt line 272, prepared remarks, 'Approximately half of our active listings are now subject to the single service fee.' Absent from the shareholder letter, which is a different claim"),

("S02", "17", "Stale metadata in FINAL_SUMMARY.md: file counts (39 scripts, 153 CSVs, 15 notes, 24 figures) and 'all eight prints where the guide came in below Street' after WS16 made it 9 of 9",
 "docs/overnight/FINAL_SUMMARY.md",
 "Fix metadata without erasing dated provenance",
 "still open; counted on HEAD as 44 scripts, 169 CSVs, 18 notes, 24 figures",
 "reassigned - agent 25 (WS19 did not edit the file)", "agent 25", "low", "small",
 "Counts taken directly from the tree. The 9-of-9 statement is in 14_master-synthesis.md line 262 and 16_web-gap-fill.md line 110 but FINAL_SUMMARY.md line 67 still says eight"),

("S03", "17", "The WS17 note is a pre-WS18 audit and still describes the share-count error as open; it needs a superseded-by marker",
 "research/notes/overnight/17_excel-audit.md",
 "Add a clear superseded marker so another reader does not reopen a repaired item",
 "still open", "reassigned - agent 25 (WS19 did not edit the file)", "agent 25", "low", "small",
 "The note's bottom line still reads 'The one that matters most and is not fixed: the FY2026 share-count roll-forward double-counts the 1H26 buyback'"),

("K01", "Krish", "'Listing 15_cross_note_conflicts seems to have paused' - reported symptom on data/processed/overnight/15_cross_note_conflicts.csv",
 "data/processed/overnight/15_cross_note_conflicts.csv, 15_claim_checks.csv; analysis/src/overnight/15_claim_checks.py; research/notes/overnight/15_red-team.md",
 "n/a - not in the audit document",
 "the CSV itself was NOT truncated: 16 data rows (CONF-01..CONF-16), 8 columns, every line quote-balanced, no embedded newline, no control character, parses in pandas. Three real defects found instead",
 "fix now - DONE", "WS19", "medium", "small",
 "See the note. (1) Excel silently evaluated formula-leading cells - in the companion 15_claim_checks.csv '+0.69 / 0.0005 / +0.72' became 1916.667 and '+4.0 / +2.6' became 1.538462. (2) Workstream ids '01'..'12' lost their leading zero in Excel. (3) The listing that genuinely stops short is the 'For the model' table in 15_red-team.md, which jumps from CONF-14 to CONF-16 and omits CONF-15"),
]

TRIAGE_HDR = ["id", "audit_section", "finding", "files_affected", "audit_proposed_repair",
              "status_on_head_77037c2", "decision", "owner", "severity", "effort",
              "evidence_or_reasoning"]

# ---------------------------------------------------------------------------------------- repairs
REPAIRS = [
("A01", "analysis/src/overnight/08_altdata_backtests.py",
 'F["bl_unearned_to_next_rev_lag1"] = b["unearned_to_next_q_revenue"].shift(1)  -> feature at t = unearned[t-1] / revenue[t]',
 'F["bl_unearned_to_prior_rev_lag1"] = (b["unearned_fees_musd"] / b["revenue_musd"]).shift(1)  -> feature at t = unearned[t-1] / revenue[t-1], both reported at the prior print'),
("A01", "data/processed/overnight/08_feature_tests_all.csv, 08_backlog_tests.csv",
 "6 rows on bl_unearned_to_next_rev_lag1 (pearson_r -0.143 to -0.465, best wf_ratio_vs_ar1 0.951)",
 "6 rows on bl_unearned_to_prior_rev_lag1 (pearson_r 0.020 to -0.318, best wf_ratio_vs_ar1 0.995). Row count unchanged at 598; 52 rows still beat AR(1), 31 beat naive, 26 beat both"),
("A05", "analysis/src/overnight/08_altdata_backtests.py cc_features()",
 "quarterly survival series differenced with .shift(4) on the observed rows; 7 of 12 comparisons were not t vs t-4",
 "series reindexed onto a contiguous quarterly PeriodIndex before .shift(4); gaps stay NaN, no forward fill"),
("A05", "data/processed/overnight/08_panel_quarterly.csv cc_survival_yoy_pts",
 "2023Q4 -4.816; 2024Q1 -3.100; 2024Q2 2.211; 2024Q3 2.095; 2026Q1 2.248; 2026Q2 1.553; 2026Q3 0.064",
 "2023Q4 -2.885; 2024Q1 2.767 (sign flip); 2024Q2 0.911; 2024Q3 NaN (2023Q3 has no informative crawl); 2026Q1 2.303; 2026Q2 -0.021; 2026Q3 -1.422"),
("A05", "data/processed/overnight/08_test_scoreboard.csv, 08_feature_tests_all.csv",
 "cc_survival_yoy_pts -> nights_yoy: n 11, pearson_r -0.581, wf_ratio_vs_naive 0.690, sign accuracy 0.571",
 "cc_survival_yoy_pts -> nights_yoy: n 10, pearson_r -0.544, wf_ratio_vs_naive 0.675, sign accuracy 0.833. No family count and no headline claim changes"),
("A09", "data/processed/overnight/16_news_since_5sep.csv lines 15 and 16",
 ",TipRanks (estimated, not company-confirmed),  -> 8 fields against a 7-field header; pandas raised ParserError",
 '"TipRanks (estimated, not company-confirmed)" quoted -> 20 data rows x 7 fields, all values preserved'),
("A10", "analysis/src/overnight/13_excel_builder.py rdcf()",
 "b*(1+g)/(coe-g)*(1-((1+g)/(1+coe))^10) - returns #DIV/0! when g equals coe",
 "b*(q^1+q^2+...+q^10) with q=(1+g)/(1+coe) - an explicit ten-term discounted sum with no division by (coe-g); continuous at equality, where it equals 10*b"),
("A10", "model/ABNB_driver_model.xlsx Valuation!B54:C63 plus the two staleness-check cells",
 "22 formula cells on the closed-form annuity; Valuation!B59 and C59 read #DIV/0! at a base cost of equity of 11%",
 "22 formula cells on the ten-term sum; at coe 11% B59 reads 201.02 and C59 136.04, matching the Python mirror. At the shipped coe of 10.5% every value is unchanged to 1e-12 and no model output moves"),
("A10", "data/processed/overnight/17_excel_vs_python.csv, 17_all_formula_cells.csv, 17_excel_recalc_dump.csv",
 "216/216 outputs, 2,349/2,349 formula cells, 5,547 cells, 0 error cells (pre-fix workbook)",
 "216/216 outputs, 2,349/2,349 formula cells, 5,547 cells, 0 error cells (post-fix workbook, re-dumped from Excel 16.0)"),
("A10", "data/processed/overnight/17_auto_scan.csv",
 "321 informational static-scan hits (3 hard-coded constants)",
 "343 hits (25 hard-coded constants). The 22 extra hits are the literal exponents ^1..^10 in the rewritten cells; they are not defects"),
("A10", "data/processed/overnight/17_scenario_switch.csv",
 "143 rows = 141 comparisons + 2 change-count summaries",
 "145 rows = 141 comparisons + 4 change-count summaries, 0 mismatches. The two extra summary rows are the pre-WS17-fix build, which the WS17 note already documents as 145 rows; the committed 143-row file was written before those dumps existed"),
("S01", "data/processed/overnight/15_cross_note_conflicts.csv CONF-11",
 "recommended: 'Neither: over a quarter at 1Q26 (disclosed), remainder in migration at 2Q26, complete by year-end'; reason: 'The ~50% figure appears in neither the 2Q26 letter nor the 2Q26 call transcript'",
 "recommended: 'NOT A CONFLICT - both notes are right'; reason records the verbatim 2Q26 call line and its location (data/raw/regulatory/transcripts/2026-Q2.txt line 272)"),
("S01", "data/processed/overnight/15_claim_checks.csv, WS06 single-fee row",
 "verdict 'unsupported', 'No ~50% figure exists'; file tally 83 confirmed / 9 wrong / 2 unsupported / 4 unverifiable",
 "verdict 'confirmed' with the transcript quote and line; tally 84 / 9 / 1 / 4"),
("S01", "research/notes/overnight/15_red-team.md",
 "bottom line '98 claims checked: 83 confirmed, 9 wrong, 2 unsupported, 4 unverifiable'; the WS06 paragraph asserts the figure is in neither source",
 "tally restated as 84 / 9 / 1 / 4 with the original in brackets; the WS06 sentence struck through and corrected; an amendment banner added at the top"),
("K01", "research/notes/overnight/15_red-team.md 'For the model' table",
 "table listed CONF-01..CONF-14 and CONF-16 - 15 of the 16 conflicts, jumping straight from CONF-14 to CONF-16",
 "CONF-15 row added (SBC as a share of FY25 revenue: state the basis, 12.92% P&L expense vs 13.1% cash-flow add-back)"),
("K01", "analysis/src/overnight/15_claim_checks.py",
 'OUT = r"C:\\Users\\krish\\citadel-abnb-overnight\\data\\processed\\overnight"',
 "ROOT resolved from __file__; OUT = ROOT/data/processed/overnight"),
("K01", "data/processed/overnight/15_cross_note_conflicts.csv, 15_claim_checks.csv - workstream id columns",
 "'01'..'12' - Excel drops the leading zero and shows 1..12, so the column reads as a number",
 "'WS01'..'WS12' - text in Excel and in pandas; non-numeric values such as 'driver model (pre-existing)' pass through unchanged"),
("K01", "data/processed/overnight/15_claim_checks.csv - cells beginning with a sign",
 "Excel evaluated them as formulas: '+0.69 / 0.0005 / +0.72' displayed as 1916.667, '+4.0 / +2.6' as 1.538462, '+11.11 / +2.56 / -1.56' as -2.78195, '+3.99 / +2.58' as 1.546512",
 "36 such cells written with one leading space; re-opened in Excel 16.0 via COM, every cell now matches the CSV text after strip()"),
("K01", "data/processed/overnight/15_cross_note_conflicts.csv - cells beginning with a sign",
 "6 cells led with + or - (CONF-01 value_a and value_b, CONF-05 value_a, CONF-06 value_a, value_b and recommended); '+12.4%' was coerced to the number 0.124",
 "written with one leading space; values preserved (Excel still renders percentages as 12.40%, which is the same number)"),
("K01", "analysis/src/overnight/15_claim_checks.py",
 "no post-write validation",
 "write_csv() reads the file back and asserts it is rectangular, has no embedded newline, has no formula-leading cell, and that the conflicts file holds exactly CONF-01..CONF-16"),
]

REPAIRS_HDR = ["finding_id", "file", "old", "new"]

# ------------------------------------------------------------------------- out-of-scope edits left
LEFT_IN_TREE = [
("A11", "analysis/src/overnight/16_merge_and_rerun.py",
 "module-scope execution, hard-coded ROOT, SystemExit on an unseen quarter, derived surprise recomputed only when blank",
 "main() entry point, ROOT from __file__, schema and uniqueness validation, an append path for a new quarter, derived fields recomputed from primitives with sourced-beats-calculated and a disagreement warning. THE DATA OUTPUTS WERE RESTORED to their committed state - agent 24 owns the decision on whether to adopt this"),
("A13", "analysis/src/overnight/17_excel_audit.py",
 "main() printed mismatch counts and always exited 0",
 "main() returns 1 on any failed named-output or formula-cell comparison, a wrong output count, or a missing required cell; the informational static scan does not affect the status. Prints PASS/FAIL"),
("A13", "analysis/src/overnight/17_scenario_switch.py",
 "main() printed mismatch counts and always exited 0; the dump directory defaulted to one session's scratch path with no existence check",
 "main() returns 1 on any scenario mismatch, on zero comparisons, or if the selector moves 0 cells for a scenario; dump directory resolves from argv[1], then ABNB_EXCEL_DUMP_DIR, then the historical default, and missing dumps raise a named error"),
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    write_csv("19_audit_triage.csv", TRIAGE_HDR, TRIAGE)
    write_csv("19_repairs_applied.csv", REPAIRS_HDR,
              REPAIRS + [(r[0] + " (out of scope, edit left in tree)",) + r[1:] for r in LEFT_IN_TREE])
    from collections import Counter
    print("decisions:", dict(Counter(r[6].split(" - ")[0] for r in TRIAGE)))
