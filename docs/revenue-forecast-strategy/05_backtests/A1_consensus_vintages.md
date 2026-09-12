# A1 — Today's sell-side consensus for ABNB, and the point-in-time history hunt

Captured Friday **11 Sep 2026, 15:44–15:55 ET**. Ticker ABNB (NASDAQ), CUSIP 009066101.
Raw captures + one screenshot per vendor page: `data/raw/consensus/2026-09-11/`.
Register: `data/processed/forecast_methods/L0/L0_vintage_register.csv`
(backup taken first: `L0_vintage_register.backup_2026-09-11.csv`).

**The hard rule is intact and was re-verified after the append:** the 6 Aug 2026 pre-guide 3Q26 Street is
**LSEG $4,610M** (`PG-2026Q3-revenue`, role `pre_guide`). Zacks $4,740M is a September vintage and is not that number.

---

## 1. Every value captured today

Revenue in $M. "As of" is the **vendor's own stated date** where the page gives one, otherwise the capture time in ET.

### Revenue consensus (mean)

| Vendor | 3Q26 | 4Q26 | FY2026 | FY2027 | As of |
|---|---|---|---|---|---|
| Alpha Vantage (MCP) | **4,737.5** (n=36) | **3,158.1** (n=36) | **14,155.1** (n=43) | **15,757.8** (n=44) | 11 Sep, capture time¹ |
| Zacks | **4,740** (n=7) | **3,200** (n=10) | **14,100** (n=8) | **15,740** (n=13) | 11 Sep 15:44 ET² |
| Yahoo Finance | **4,740** (n=35) | **3,160** (n=35) | **14,160** (n=43) | **15,790** (n=43) | 11 Sep 15:47 ET² |
| S&P Global MI (via StockAnalysis) | **4,740** (n=35) | **3,160** (n=35) | **14,160** (n=43) | **15,770** (n/a³) | **10 Sep** (vendor-stated) |
| MarketBeat / Fiscal.ai | ~~4,600~~ (n=2) ⚠ | — | — | — | 11 Sep 15:50 ET² |

¹ Alpha Vantage returns no as-of field at all; capture time in ET is used.
² These vendors date only their price quote, not the estimate table; the quote stamp is the best available.
³ S&P's FY2027 detail column is paywalled; 15,770 is readable from the free "Revenue Next Year" tile, without n.

High / low (same order, $M): AV 3Q 4,792/4,649 · 4Q 3,223/3,052 · FY26 14,296/13,833 · FY27 16,381/14,987.
Zacks 3Q 4,770/4,720 · 4Q 3,700/3,050 · FY26 14,210/13,960 · FY27 16,290/14,990.
Yahoo 3Q 4,790/4,680 · 4Q 3,220/3,050 · FY26 14,300/13,830 · FY27 16,380/14,990.

### Adjusted EPS (non-GAAP), same vintages

| Vendor | 3Q26 | 4Q26 | FY2026 | FY2027 |
|---|---|---|---|---|
| Alpha Vantage | 2.8511 (n=33) | 0.8196 (n=32) | 5.2933 (n=38) | 6.1858 (n=41) |
| Zacks | 2.88 (n=11) | 0.83 (n=10) | 5.24 (n=13) | 6.04 (n=13) |
| Yahoo | 2.86 (n=33) | 0.83 (n=32) | 5.31 (n=38) | 6.22 (n=40) |
| S&P Global MI | 2.88 (n=35) | 0.84 (n=35) | 5.30 (n=43) | 6.17 (n/a) |

### Other metrics found

| Metric | Value | Vendor | As of |
|---|---|---|---|
| 3Q26 operating income | 1,890 | S&P Global MI | 10 Sep |
| 4Q26 operating income | 443.4 | S&P Global MI | 10 Sep |
| FY2026 operating income | 3,170 | S&P Global MI | 10 Sep |
| FY2026 free cash flow | 5,350 | S&P Global MI | 10 Sep |
| NTM price target (mean) | 180.57 (n=46) | S&P Global / TipRanks | 10 Sep |
| NTM price target (**median**) | **185.00** (n=46) | S&P Global / TipRanks | 10 Sep |
| NTM price target (mean) | 179.97 (n=40) | MarketBeat / Benzinga | 11 Sep |

**No vendor publishes a revenue median.** The only median available anywhere today is a *price target*.
That alone is an argument for the IBES pull in §4 — IBES `MEDEST` carries the consensus median per period per vintage.

### 1Q27 and FY2028
Not published by any free source reached. Alpha Vantage stops at FY2027; Zacks and Yahoo show exactly four columns
(current qtr / next qtr / current yr / next yr); StockAnalysis *lists* Q1 2027–Q4 2028 and FY2028 columns but every
cell is paywalled. **No 1Q27 or FY2028 consensus was obtainable.**

---

## 2. Vendor disagreement on 4Q26 revenue

4Q26 is where the vendors actually part company:

| | Value ($M) | n |
|---|---|---|
| Zacks (high) | 3,200.0 | 10 |
| Yahoo / S&P Global MI | 3,160.0 | 35 |
| Alpha Vantage (low) | 3,158.1 | 36 |

**Spread = $41.9M**, i.e. **~$42M**, or **1.33%** of the ~$3,160M level.
Zacks is the outlier and it is the *thinnest* panel (n=10 vs 35–36). Excluding Alpha Vantage (see the caveat below),
the disagreement is a clean **$40M: Zacks 3,200 vs everyone else 3,160.**

For contrast, the other periods are near-unanimous: 3Q26 spans only **$2.5M** (4,737.5–4,740),
FY2026 **$60M**, FY2027 **$50M**.

**Two caveats that matter for any dispersion work:**

1. **Yahoo and Alpha Vantage are not independent.** Their high/low agree to the dollar (FY26 low 13.83B vs
   13,833,000,000; FY27 high 16.38B vs 16,381,000,000; 4Q26 low 3.05B vs 3,051,979,740), and their 30-day EPS
   revision counts are identical (FY26 30 up/4 down; FY27 25 up/9 down). They are one LSEG/Refinitiv-family panel
   surfaced twice. Counting them as two vendors would understate agreement.
   Effectively today there are **three** panels: LSEG-family (AV+Yahoo), S&P Global MI, and Zacks.
2. **MarketBeat's 3Q26 $4,600M is quarantined, not a data point.** It rests on 2 analysts, is rounded to 0.1B,
   sits ~$140M below every other vendor, and — decisively — sits *below Airbnb's own 3Q26 guide floor of $4.7B*,
   which MarketBeat prints in the adjacent column of the same row. A Street mean below the guide floor eight weeks
   after the guide is not a coherent position. The same table also misprints 4Q24 actual revenue as $1.90B
   (true: $2.48B). It is in the register with `pit_usable=False` — note that here that flag is doing double duty:
   the register header defines `False` as "vintage unknown or value missing", and these rows are excluded for
   **data quality** instead. The note field on each row says so explicitly.

---

## 3. Nights / ADR / GBV consensus — still does not exist

**No forward consensus for nights booked, ADR, or GBV was found on any source reached today.**
Checked and came up empty: Alpha Vantage `EARNINGS_ESTIMATES` (revenue + EPS only), Zacks detailed estimates
(Sales + EPS tables only), Yahoo analysis tab, StockAnalysis/S&P Global MI forecast page (revenue, EPS, gross
profit, operating income, net income, FCF — no operating KPIs), MarketBeat/Fiscal.ai earnings page.
Aiera's KPI endpoint was the one genuinely promising route and it **failed on an expired OAuth token**
(`MCP server "claude.ai Aiera" requires re-authorization`) — worth retrying once Theo reauthorises, since Aiera
does carry company-specific KPI/segment series.

Nor is there an **adjusted-EBITDA** consensus anywhere free. The closest available is S&P Global's *operating
income* line (3Q26 1,890 / FY26 3,170), which is not the same measure and should not be substituted for it.
Company FY guide remains adj-EBITDA margin ≥35.5%.

The register does already hold 19 `nights` and 13 `gbv` rows, but they are all `role=at_print` historical marks
with `vendor_not_recorded` — they are not forward consensus and cannot serve the guide-vs-Street test.

> ### 📅 Calendar reminder — set this
> **Mon 2 Nov and Tue 3 Nov 2026**: re-pull Zacks (and Yahoo/S&P) for **nights / ADR / GBV** consensus.
> Zacks typically posts these 2–3 days ahead of the print. **3Q26 earnings: Thursday 5 Nov 2026, after market close**
> — confirmed independently today by Zacks ("Exp Earnings Date 11/5/26"), Yahoo ("Q3 FY26 — Nov 05") and
> MarketBeat ("Thursday, November 5, 2026, after market closes").

---

## 4. Point-in-time history: **not obtained.** Here is exactly why, and exactly what to click

No PIT consensus series was exported today. Every candidate is gated behind a *personal* account — not an
institutional proxy — so none of it could be done without Theo typing credentials.

One useful thing was learned: **UF SSO itself is live and passes silently.** The OpenAthens institution
handshake at Mergent completed with no password prompt and no Duo push. The blocker everywhere is per-vendor
account provisioning, not UF authentication.

| Database | Status at UF | Blocker |
|---|---|---|
| **WRDS** (I/B/E/S Summary History) | Licensed | **Faculty & PhD students only**, by application, **~3 business days** to approve |
| **LSEG/Refinitiv Workspace** | Licensed, "Gators register for a free personal account" | Personal Refinitiv login (username + password); no UF SSO on the sign-in page |
| **S&P Capital IQ** | Available to UF **Business School masters** students via personal account | Personal CapIQ login |
| **FactSet** | **Not licensed** — 0 results in the UF A-Z list | n/a |
| **Value Line** | **Not licensed** — 0 results in the UF A-Z list | n/a |
| **Mergent Online** | Listed but **dead** | SSO succeeded, then *"User entitlement not found."* Banner: "Mergent Online will be discontinued soon." |

### The five-minute path (best first)

**Option A — LSEG Workspace. Fastest thing that can work today.**
1. Go to **https://businesslibrary.uflib.ufl.edu/refinitivworkspace** → click **"Register for Refinitiv Workspace"** (self-registration, free, UF email).
2. Once the account email arrives, sign in at **https://workspace.refinitiv.com/web**.
   *This is the step I stopped at: it redirects to `amers2.identity.ciam.refinitiv.net` and asks for a password.*
3. In Workspace, open the ABNB **Estimates** app → **Estimates History / Detailed Estimates**, set measure
   **Revenue**, periods FY2021–FY2028 + quarterlies, and export to CSV.
4. Drop the CSV in `data/raw/consensus/ibes/` and tell me — the loader in §5 takes it from there.
   *(Note: Chrome's Claude extension is not permitted on `workspace.refinitiv.com`; grant site permission if I'm to drive it.)*

**Option B — WRDS. The right dataset, but start it now because of the lag.**
1. **https://wrds-www.wharton.upenn.edu/** → **"Register for a WRDS Account"** → institution **University of Florida**.
2. Pick the account type; submit. It routes to UF's local administrator (Warrington), plus a usage-terms form.
   Approval is **usually ~3 business days** — so this cannot help this week, but it is the only source that gives
   a clean monthly PIT panel back to 2021.
3. Eligibility caveat: UF's own FAQ restricts WRDS to **faculty and PhD students**. If Theo is not in that group,
   this route is closed and Option A is the answer — worth one email to the Business Library to confirm.
4. Once in: **Get Data → I/B/E/S → I/B/E/S Academic → Summary History → Summary Statistics (unadjusted)**.
   - Identify ABNB by **CUSIP 009066101** (IBES carries the 8-digit form `00906610`) and confirm the IBES ticker,
     which is not guaranteed to equal the exchange ticker.
   - Measures: **`SAL`** (sales/revenue) and **`EBS`** (EBITDA). ⚠ **Correction to the runbook:** IBES has no
     measure `REV`, and **`EBI` is EBIT, not EBITDA**. Asking for REV/EBI returns the wrong thing or nothing.
   - Fiscal periods: annual FY2021–FY2028 and quarterly; statistics dates **2021-01 → today**; output CSV.
   - The Detail History file (individual broker estimates) is a second, larger pull worth doing if quick.

**Option C — Capital IQ**, if Theo already holds a CapIQ login: ABNB → Estimates → **Estimates History**,
export revenue by period. UF FAQ on recovering a CapIQ password:
`https://answers.businesslibrary.uflib.ufl.edu/search/?t=0&q=Capital+IQ`.

---

## 5. The loader is written and tested, waiting on the file

`analysis/src/forecast_methods/L0/consensus_history_loader.py`

Turns a WRDS IBES Summary-Statistics export into register rows with
`as_of_timestamp = STATPERS` (the monthly statistics date — the actual vintage), `url = "WRDS IBES export"`,
`role = pit_history`, and emits the **median** alongside the mean. Maps `FPEDATS` → period label (not `FPI`,
which drifts as quarters roll), accepts both `YYYY-MM-DD` and SAS `31DEC2026` date formats, and refuses to guess
on a non-December fiscal year end. Append-only: it never rewrites existing rows and skips `register_id`s already present.

```
# dry run (writes nothing)
python analysis/src/forecast_methods/L0/consensus_history_loader.py --export data/raw/consensus/ibes/<file>.csv
# then
python analysis/src/forecast_methods/L0/consensus_history_loader.py --export ... --append
```

It ships with a fixture self-test that passes today, with no export present:
`python analysis/src/forecast_methods/L0/consensus_history_loader.py --self-test` → *self-test OK*.

**Unit check to run on the first real export:** IBES reports US sales in **millions**, matching the register's
`musd`. Confirm FY2025 `SAL` lands near **12,240** — not 12.24 and not 1.224e10.

---

## 6. Register row counts

| | Data rows |
|---|---|
| Before | **127** |
| Appended today | **34** |
| After | **161** |

Verified after writing: existing 127 rows **byte-identical** to the backup, **0 duplicate `register_id`s**, and the
LSEG $4,610M pre-guide hard-rule row still present.

Appended: Zacks ×8 (4 revenue, 4 EPS), Yahoo ×8, S&P Global MI ×12 (4 revenue, 4 EPS, 3 operating income, 1 FCF),
MarketBeat/Fiscal.ai ×3 (quarantined, `pit_usable=False`), price targets ×3.
Alpha Vantage was **not** re-appended: its four 11 Sep revenue rows were already in the register from an earlier
pull today, and this run reproduced them exactly (4,737 / 3,158 / 14,155 / 15,758 at n=36/36/43/44) — a clean
reproducibility check rather than a duplicate.
