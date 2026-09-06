# BUILD.md — how to rebuild the ABNB pitch from a clean checkout

*Written by workstream 24 on 6 Sep 2026 for audit finding A07 ("canonical checkout, dependencies,
raw inputs and audit reproduction are not consolidated"). This file is the authoritative entry
point. Where another document disagrees with this one about how to run something, this one wins.*

---

## 1. The authoritative entry point

| | |
|---|---|
| **Repository / branch** | `C:\Users\krish\citadel-abnb-overnight`, branch `krish/overnight-synthesis` |
| **Authoritative model** | `model/ABNB_driver_model.xlsx`, built by `analysis/src/overnight/13_excel_builder.py`, mirrored by `13_driver_model.py` |
| **Authoritative analysis code** | `analysis/src/overnight/NN_*.py` — the numbered workstream scripts |
| **Authoritative outputs** | `data/processed/overnight/NN_*.csv`, `analysis/figures/overnight/NN_*.png`, `research/notes/overnight/NN_*.md` |
| **Reading order for a human** | `docs/overnight/FINAL_SUMMARY.md` → `research/notes/overnight/14_master-synthesis.md` → the individual workstream notes |

**Historical / reference only — do not treat as current:**

- `analysis/src/*.py` (unnumbered, in the repository root of `analysis/src`) and the notes in
  `research/notes/2026-09-0[45]_*.md`. These are the pre-overnight branch analyses. They were merged
  into this tree and remain useful as sources, but the numbered `overnight/` layer supersedes them
  wherever the two overlap. In particular the older `analysis/src/abnb_driver_model.py` is **not**
  the model; `13_driver_model.py` is.
- `C:\Users\krish\citadel-abnb` (MAIN). It carries an older, uncorrected cash and share-count
  treatment plus uncommitted files. Do not port fixes from this tree into it blind, and do not
  re-apply MAIN's known defects here (audit R01: the FY2026 share-count double-count is already
  fixed here by WS18).
- `theos-past-research/` — the acquisition layer and guidance dataset it documents are inputs, not
  outputs. Its bulk files live on an external volume; `data/manifests/` lists what was pulled.

---

## 2. Machine assumptions

This build is **not** portable as it stands. Everything below is a real prerequisite.

| Assumption | Detail | What breaks without it |
|---|---|---|
| **Python** | `py -3.13` (CPython 3.13.14, Windows launcher). The repo's `.venv` is **not** the build interpreter and lacks most dependencies. Install with `py -3.13 -m pip install -r requirements.txt`. | Everything |
| **Windows + desktop Excel (COM)** | Excel 16.0, reachable as the `Excel.Application` COM object. Used only by `17_recalc_dump.ps1`. | The native recalculation dump and therefore the WS17 reconciliation and the WS24 exit-code tests. The rest of the build (including the Python mirror) runs without Excel. |
| **PowerShell** | Windows PowerShell 5.1 is enough. Run the driver as `powershell -NoProfile -ExecutionPolicy Bypass -File ...`. | Same as above |
| **`data/raw` junctions** | `data/raw/{letters, regulatory, xbrl, eurostat, inside_airbnb, commoncrawl, licensed}` are NTFS **junctions** into `C:\Users\krish\citadel-abnb\data\raw\`. `data/raw/{fred, bea}` are real directories held in git. A fresh `git clone` gets neither the junctions nor their contents. Recreate with `mklink /J <link> <target>` or point the scripts at real copies. | Every panel built from raw inputs (02, 03, 06, 08, 10, 11) |
| **`pdftotext`** | The IR transcript text under `data/raw/transcripts/ir/*.txt` was produced by poppler's `pdftotext -layout`, an external binary, not a Python package. The `.txt` files are the input; the binary is only needed to regenerate them. | Re-extracting transcripts from PDF |
| **Network** | EDGAR (needs the User-Agent `citadel-abnb research ksurapaneni@ufl.edu`), FRED (keyless CSV), Eurostat, the Airbnb IR CDN, Yahoo via `yfinance`, Google Trends via `pytrends`. All are cached to `data/cache/` (git-ignored) on first use. | The acquisition steps only; every downstream step reads the cached/processed CSVs |
| **Download cache** | `data/cache/NN/`, overridable with `ABNB_SCRATCH` (and `XBRL_CACHE` for WS07). Before 6 Sep 2026 these defaulted to one user's session scratchpad; WS24 moved them into the project. A fresh checkout has an empty cache and will re-download. | Nothing, but the first run is slower and rate limits apply (fool.com ~20 requests; the Google Trends and Common Crawl index endpoints throttle) |
| **Project root** | Every script under `analysis/src/overnight/` resolves the root three levels up from its own file. Overrides: `--root` (16, 17_excel_audit, 17_scenario_switch), `ABNB_ROOT` (04_*). Two files still hard-code an absolute path — see §7. | — |

---

## 3. The ordered build graph

Run from the repository root. Each step's inputs are the previous steps' outputs.

```
 0. availability check        01_data_census.py
        |
 1. normalized panels         02_kpi_panel.py -> 02_guidance_ledger.py -> 02_guidance_analysis.py
        |                     03_call_features.py, 03_forward_claims.py
        |                     04_consensus_at_print.py
        |                     05_macro_transmission.py, 06_*, 07_*, 10_*, 11_*, 12_*
        v
 2. feature / reaction tests  03_reaction_tests.py, 03_event_study.py
        |                     04_reaction_vs_consensus.py
        |                     08_altdata_backtests.py, 09_stock_behaviour.py
        v
 3. model                     13_driver_model.py         (the Python mirror; writes 13_*.csv)
        |                     13_excel_builder.py        (writes model/ABNB_driver_model.xlsx +
        |                                                 13_reconciliation.csv)
        v
 4. workbook self-check       13_xlsx_eval.py            (pure-Python formula evaluator)
        v
 5. native Excel dump         17_recalc_dump.ps1         (REQUIRES Excel; writes the three dumps)
        v
 6. reconciliation            17_excel_audit.py          (exit != 0 on a real failure)
        |                     17_scenario_switch.py      (exit != 0 on a broken selector)
        |                     17_formula_review.py       (informational)
        v
 7. next-print append         16_merge_and_rerun.py [--append event.csv]
        v
 8. verification              15_claim_checks.py, 19_audit_triage.py,
        |                     24_test_merge_rerun.py, 24_exit_code_tests.py
        v
 9. notes / summary           research/notes/overnight/*.md, docs/overnight/FINAL_SUMMARY.md
```

### The commands, in order

```bash
# 0. what inputs exist, and are they the vintage the notes assume?
py -3.13 analysis/src/overnight/01_data_census.py

# 1-2. panels and tests: the numbered scripts are independent within a number and ordered across
#      numbers. 15_script_runs.py records a full sweep.
py -3.13 analysis/src/overnight/02_kpi_panel.py           # ... and the rest of 02-12

# 3. the model, Python first, then the workbook the Python mirrors
py -3.13 analysis/src/overnight/13_driver_model.py
py -3.13 analysis/src/overnight/13_excel_builder.py

# 5. native Excel recalculation (Windows + Excel). ALWAYS re-run after 13_excel_builder.py:
#    the dumps are snapshots of a specific workbook build and go stale silently otherwise.
powershell -NoProfile -ExecutionPolicy Bypass -File analysis/src/overnight/17_recalc_dump.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File analysis/src/overnight/17_recalc_dump.ps1 \
    -ScenarioValue 1 -OutCsv data\processed\overnight\17_dump_after_scen1.csv
powershell -NoProfile -ExecutionPolicy Bypass -File analysis/src/overnight/17_recalc_dump.ps1 \
    -ScenarioValue 3 -OutCsv data\processed\overnight\17_dump_after_scen3.csv

# 6. reconciliation. These now FAIL LOUDLY: check $LASTEXITCODE / $?, do not read the log only.
py -3.13 analysis/src/overnight/17_excel_audit.py         # 0 = reconciles, 1 = material failure, 2 = missing input
py -3.13 analysis/src/overnight/17_scenario_switch.py     # 0 = selector works, 1 = broken, 2 = missing dump

# 7. after the 5 Nov 2026 print (see §5)
py -3.13 analysis/src/overnight/16_merge_and_rerun.py
py -3.13 analysis/src/overnight/16_merge_and_rerun.py --append data/processed/overnight/16_2026Q3_event.csv

# 8. the tests that guard 6 and 7
py -3.13 analysis/src/overnight/24_test_merge_rerun.py    # 33 checks
py -3.13 analysis/src/overnight/24_exit_code_tests.py     # 7 exit-status cases
```

**Fail-fast contract.** No step falls back to a sibling worktree, a stale output, or another
machine's scratch directory. A missing input is an error, not a silently older number. If you see
a script reach outside this repository, that is a bug — report it against A07.

---

## 4. Inputs: what is in the repo, what is external, what is licensed

| Input | Where | How to obtain |
|---|---|---|
| Shareholder letters, 4Q20–2Q26 | `data/raw/letters/` (junction) | 8-K Exhibit 99.1 HTML from EDGAR (`https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001559720`), UA `citadel-abnb research ksurapaneni@ufl.edu` |
| IR call transcripts 2023Q1–2026Q2 | `data/raw/regulatory/transcripts/` (junction) | Airbnb IR CDN pattern in `analysis/src/download_abnb_transcripts.py`; pre-2023 from `https://stockanalysis.com/stocks/abnb/transcripts/` with a browser UA |
| XBRL company facts | `data/raw/xbrl/ABNB_companyfacts.json` (junction) | `https://data.sec.gov/api/xbrl/companyfacts/CIK0001559720.json` |
| FRED / BEA extracts | `data/raw/fred/`, `data/raw/bea/` — **in git** | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=SERIES` (keyless) |
| Eurostat platform nights | `data/raw/eurostat/` (junction) | Eurostat bulk download, `10_fetch_eurostat_latest.py` |
| Inside Airbnb dumps (337 files, 13 cities) | `data/raw/inside_airbnb/` (junction) | `insideairbnb.com/get-the-data` — **the CDN keeps only ~1 year**; older dumps must be restored from the local archive or requested. Read the price-basis and partial-snapshot caveats in `research/notes/2026-09-05_inside-airbnb-supply-panel.md` and audit finding A04 before using them. |
| Common Crawl listing panel | `data/raw/commoncrawl/` (junction) | cdx shards via `cluster.idx` on `data.commoncrawl.org`; the index API blocks after ~40 queries |
| **Third Bridge expert calls (LICENSED)** | `data/raw/licensed/third-bridge/` (junction), 5 PDFs | **Not redistributable. Do not commit, do not quote at length.** Access is through the team's Third Bridge subscription; the digest in `research/notes/2026-09-05_third-bridge-transcripts.md` is what downstream work is allowed to cite. |
| **Bloomberg / CapIQ / FactSet exports (LICENSED)** | none in this tree; `.gitignore` blocks `*bloomberg*`, `*capiq*`, `*factset*` | Terminal export by a licensed user. Consensus values sourced *through* press quoting FactSet/LSEG/Refinitiv are fine and are what `04_consensus_at_print.csv` and `16_consensus_additions.csv` use, each with a URL and a verbatim quote. |
| **Vendor consensus panels (Zacks / Visible Alpha / StreetAccount)** | not held | Retrieved as published quotes with source URLs; see `04_consensus_sources.csv`. There is no licensed feed in this repository. |
| Theo's bulk acquisition files | external volume | `data/manifests/` lists every file; `docs/CODEX_HANDOFF_V2.md` describes the layer |

---

## 5. What regenerates and what is frozen

**Regenerates deterministically** (same inputs → same bytes): every `data/processed/overnight/*.csv`
built by a numbered script, `model/ABNB_driver_model.xlsx`, and the figures.

**Regenerates but is timestamp- or network-bound:** anything under `data/cache/`, the yfinance and
Google Trends pulls (values as of the pull date), and `01_data_census.csv` (file inventory).

**Snapshots of a specific workbook build — regenerate whenever the workbook is rebuilt:**
`17_excel_recalc_dump.csv`, `17_dump_after_scen1.csv`, `17_dump_after_scen3.csv`. They come from
`17_recalc_dump.ps1` and cannot be produced without Excel.

**Frozen, never regenerate:**

- `16_frozen_pre_<quarter>_*.csv` — the pre-event forecast, written once by
  `16_merge_and_rerun.py --append` and refused thereafter. This is the prospective prediction the
  5 Nov print is scored against; a refit that has seen the actual is a different object and lands
  under the `16_post_<quarter>_` prefix.
- `17_scenario_switch.csv`'s two `build = "before ..."` rows. They describe the pre-WS17 workbook,
  which no longer exists; they are only reproduced when the pre-fix dumps are supplied via
  `--dump-dir`.
- Hand-curated evidence tables with per-cell sources and quotes: `16_consensus_additions.csv`,
  `04_consensus_sources.csv`, `06_*_evidence.csv`, `research/regulatory/*`. These are inputs.

---

## 6. Adding the next print (5 Nov 2026)

1. Build a one-quarter additions CSV with columns `print_quarter, print_date, column, new_value,
   vendor, source_publisher, source_date, source_url, quote, confidence, notes`. It must supply
   `print_date`, `actual_revenue_musd`, `cons_revenue_musd` and `next_q_guide_mid_musd`; every
   vendor-sourced row needs a `source_url` and a `source_date` (the vintage).
2. `py -3.13 analysis/src/overnight/16_merge_and_rerun.py --append <that file>`.
   The script freezes the pre-event artifacts, appends the quarter, recomputes **all** derived
   surprise and sign fields from their primitives, and writes the refit under
   `16_post_<quarter>_*`. It refuses duplicate keys, unseen columns, a quarter that already exists,
   and a new event missing an actual/consensus/guide.
3. Re-run `24_test_merge_rerun.py`. Then score the print against the frozen card.

---

## 7. Known gaps (open against A07)

- `15_script_runs.py` and `08_altdata_backtests.py` still hard-code
  `C:\Users\krish\...\scratchpad\NN` and, in the first case, absolute `OUT`/`SRC` paths. Both were
  owned by other agents during the 6 Sep run; they need the same `ABNB_SCRATCH`/root treatment the
  other scripts got.
- `17_scenario_switch.csv`'s "before" block is not reproducible from this repository (§5).
- Acceptance for A07 is not yet fully met: nobody has run this file's §3 end to end in an isolated
  checkout with only `requirements.txt` installed and the junction targets supplied explicitly.
  Until that is done, treat §3 as documented-but-untested for steps 0–2.
