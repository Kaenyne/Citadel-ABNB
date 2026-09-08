"""Build docs/nights_choice_driver.xlsx - the choice-probability nights driver as live Excel formulas.

Sheets: Inputs (blue = edit), Calibration_2025, Projection, Sensitivity (Python output, pasted).
Mirrors analysis/src/choice_nights_driver.py exactly; recalc with LibreOffice before shipping.
"""
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/nights_choice_driver.xlsx"
SEG = ["solo", "pair", "3-4", "5+"]
YEARS = [2025, 2026, 2027, 2028, 2029, 2030]

BLUE, BLACK, GREEN = Font(name="Arial", size=10, color="0000FF"), Font(name="Arial", size=10), Font(name="Arial", size=10, color="008000")
BOLD = Font(name="Arial", size=10, bold=True)
H1 = Font(name="Arial", size=12, bold=True)
YELLOW = PatternFill("solid", fgColor="FFFF00")
GREY = PatternFill("solid", fgColor="EEEEEE")
PCT, NUM, NUM1 = "0.0%", "#,##0.0", "0.000"

# Take rate. NOT flat, and the flat 0.134 this sheet used to carry was a hidden assumption.
# FY25 actual is 13.4% (revenue / GBV, Q4'25 shareholder letter). The 13 Oct 2026 move to a single
# 15.5% host fee is mechanically ~+58bp on guest spend, invariant to demand elasticity and to how far
# hosts re-price, because 15.5% is levied on the grossed-up price rather than 3% on the host subtotal
# plus 14% at checkout (research/notes/host_only_fee_history_and_elasticity.md). About half of listings
# had migrated by 2Q26 and all had by year end, so FY26 collects roughly a quarter of the step and FY27
# the rest. Pushing the other way, management guided FY26 "relatively flat" because customer incentives
# for Services, Experiences and hotels are booked as contra-revenue; the same note puts the no-migration
# path at 12.9-13.1%. Holding 13.4% flat therefore assumed the migration for FY26 and then declined to
# collect the FY27 step. Blue and yellow: override it if the team model disagrees.
TAKE_RATE_PATH = [0.134, 0.134, 0.136, 0.136, 0.136, 0.136]
TAKE_RATE_NOTE = ("FY2025 revenue ÷ GBV = 13.4% (Q4'25 letter). Steps to 13.6% by FY27: the single 15.5% host fee "
                  "is ~+58bp on guest spend (~half of listings migrated by 2Q26, all by year end); FY26 is held at "
                  "13.4% because incentives for Services/Experiences/hotels are contra-revenue and management guided "
                  "FY26 flat. Without the migration this line would drift to 12.9-13.1%.")

wb = Workbook()

# ------------------------------------------------------------------ Inputs
ws = wb.active
ws.title = "Inputs"
ws.column_dimensions["A"].width = 46
ws.column_dimensions["B"].width = 12
for c in "CDEF":
    ws.column_dimensions[c].width = 12
ws.column_dimensions["G"].width = 90
ws["A1"] = "Choice-probability nights driver — INPUTS"; ws["A1"].font = H1
ws["A2"] = "Blue = hardcoded input you can change. Black = formula. Green = link to another sheet. Yellow = key levers. Every input carries its source in column G."
ws["A2"].font = Font(name="Arial", size=9, italic=True)

rows = [
    ("AIRBNB 2025 (U.S.)", None, None),
    ("Airbnb North America nights 2025 (mm)", 158.0, "Airbnb FY2025 10-K, MD&A regional table — https://www.sec.gov/Archives/edgar/data/1559720/000155972026000004/abnb-20251231.htm"),
    ("U.S. share of North America (revenue proxy)", 0.92, "U.S. = 39% of FY2025 revenue ($4.76B of $12.2B) ÷ NA revenue $5.196B. A REVENUE share used as a NIGHTS share — exact only if revenue per night matches in the U.S. vs Canada/Mexico. It does not, so the U.S. ADR premium below corrects it. Resulting level is now supply-side validated — see the Validation sheet"),
    ("Nights per booking, North America", 4.1, "Airbnb FY2025 10-K"),
    ("Share of Airbnb guests who would have used a hotel absent Airbnb", 0.38, "Farronato & Fradkin (AER 2022): 62% would NOT have switched to a hotel — https://andreyfradkin.com/assets/airbnb_welfare_paper.pdf"),
    ("HOTELS 2025 (U.S.)", None, None),
    ("U.S. hotel room nights sold 2024 (mm)", 1300, "STR/CoStar via HospitalityNet — https://www.hospitalitynet.org/news/4127015.html"),
    ("Room-night growth 2025 (assumed)", 0.01, "Assumption; CoStar/TE 2026 forecast is +1.7%"),
    ("Business share of room nights", 439 / 1044, "AHLA 2024 State of the Industry: 439M business / 605M leisure (2023) — https://www.ahla.com/sites/default/files/SOTI.2024.Final_.Draft_.v4.pdf"),
    ("Corporate bookings single-occupancy share", 0.795, "Hotel Booking Demand dataset (Antonio et al. 2019), corporate segment, n=4,291 — https://www.sciencedirect.com/science/article/pii/S2352340918315191"),
    ("SHARE DYNAMICS", None, None),
    ("Switch rate: Airbnb-hotel switching per % price gap", 5.0, "Central 5.0; grid 2.5–10.3. Anchor: F&F (AER 2022) online Appendix Table E9 — Airbnb demand rises 3.76% when all hotel prices rise 1%; model reproduces that at beta 10.3 (= 3.76/(0.38×0.955)), discounted for tier-level, 10-city, city-night scope. 2.5 = bull floor (no evidential support as a central)"),
    ("Rest-of-world nights growth (placeholder, team input)", 0.10, "SUPERSEDED by the Global sheet: EMEA from the measured 4-country calibration, LatAm/APAC explicit fades from disclosed +18%/+15% (choice_nights_driver_global.py)"),
]
r = 4
addr = {}
for label, val, src in rows:
    ws.cell(r, 1, label)
    if val is None:
        ws.cell(r, 1).font = BOLD; ws.cell(r, 1).fill = GREY
    else:
        c = ws.cell(r, 2, val); c.font = BLUE
        c.number_format = PCT if (isinstance(val, float) and val < 1 and "Nights per booking" not in label and "Switch rate" not in label) else "0.00" if "Switch rate" in label or "Nights per booking" in label else "#,##0.0"
        ws.cell(r, 7, src).font = Font(name="Arial", size=9)
        addr[label] = f"Inputs!$B${r}"
    r += 1
ws.cell(addr["Switch rate: Airbnb-hotel switching per % price gap"].split("$")[-1] and int(addr["Switch rate: Airbnb-hotel switching per % price gap"].split("$")[-1]), 2).fill = YELLOW
ws.cell(int(addr["Share of Airbnb guests who would have used a hotel absent Airbnb"].split("$")[-1]), 2).fill = YELLOW

# segment table
r += 1
ws.cell(r, 1, "SEGMENT INPUTS (party size)").font = BOLD; ws.cell(r, 1).fill = GREY
r += 1
seg_hdr = ["Segment", "Airbnb booking share", "Airbnb relative stay length", "Hotel leisure party share", "Hotel leisure relative nights", "Hotel rooms per party", "Price ratio 2025 (Airbnb ÷ hotel)", "Mix drift / yr — Airbnb pool", "Mix drift / yr — hotel pool", "Product shift (logit pts/yr)"]
for j, h in enumerate(seg_hdr):
    c = ws.cell(r, 1 + j, h); c.font = BOLD; c.alignment = Alignment(wrap_text=True)
ws.row_dimensions[r].height = 42
seg_vals = {
    "solo": [0.16, 1.5, 0.20, 0.7, 1.0, 0.54, -0.0063, -0.0027, 0.0],
    "pair": [0.358, 0.95, 0.54, 1.0, 1.0, 1.03, 0.0, 0.0, 0.0],
    "3-4": [0.323, 0.9, 0.20, 1.0, 1.5, 0.69, 0.0127, 0.0054, 0.0],
    "5+": [0.159, 0.8, 0.06, 1.0, 2.5, 0.71, 0.0253, 0.0107, 0.0],
}
seg_row = {}
for g in SEG:
    r += 1
    seg_row[g] = r
    ws.cell(r, 1, g)
    for j, v in enumerate(seg_vals[g]):
        c = ws.cell(r, 2 + j, v); c.font = BLUE
        c.number_format = PCT if j in (0, 2, 6) else "0.00"
    ws.cell(r, 8).fill = YELLOW; ws.cell(r, 9).fill = YELLOW
r += 1
ws.cell(r, 1, "Sources: booking share = fitted party-size distribution (research/party_size_distribution.md; anchors: guest arrivals ÷ bookings 2.97, Airbnb '>80% of bookings are group trips'). "
        "Relative stay length: solo = 24% of nights ÷ 16% of bookings (Airbnb 2022); others from Inside Airbnb booked-run lengths by capacity. "
        "Hotel leisure party share = mean of Hawaii DBEDT 2024 hotel-only (Table 43) and Las Vegas Visitor Profile 2024. Relative nights: Portuguese ledger (solo 2.5 vs 3.6). "
        "Rooms per party: 2 people/room, families with small kids 1.5. Price ratio: party_size_cost_crossover.csv - the Jun-2026 Inside Airbnb `price` is a stay quote that ALREADY includes the guest service fee and amortised cleaning, so no fee is added (corrected 7 Sep 2026; the earlier 0.69/1.22/0.80/0.79 counted the 14% fee twice) vs rooms × $158.67 ADR. Descriptive - no formula reads this column. "
        "Mix drift SPLIT 8 Sep 2026 into two vectors (was one applied to both pools). Airbnb pool implies mean party size +0.62%/yr, from the Inside Airbnb review-text proxy (74m reviews, 123 markets, 2018-25); hotel pool +0.26%/yr, from the Hawaii DBEDT ratio (rental 2.28->2.49 = +0.80%/yr vs hotel 2.22->2.30 = +0.34%/yr, 2013-24 - the only source observing both in one market). The old single vector implied +0.98%/yr for both and flattered the forecast.").font = Font(name="Arial", size=9, italic=True)
ws.cell(r, 1).alignment = Alignment(wrap_text=True, vertical="top"); ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=10); ws.row_dimensions[r].height = 70

# year paths
r += 2
ws.cell(r, 1, "YEAR PATHS").font = BOLD; ws.cell(r, 1).fill = GREY
r += 1
ws.cell(r, 1, "Year").font = BOLD
for j, y in enumerate(YEARS):
    ws.cell(r, 2 + j, str(y)).font = BOLD
year_hdr_row = r
paths = [
    ("U.S. lodging demand growth (hotel-contestable pool)", [None, 0.017, 0.011, 0.015, 0.015, 0.015], "CoStar/Tourism Economics Aug-2026: demand +1.7% 2026, +1.1% 2027 — https://www.hospitalitynet.org/news/4133888/us-hotel-forecast-assumptions-august-2026.html; 1.5% after = assumption"),
    ("Hotel ADR growth", [None, 0.031, 0.016, 0.025, 0.025, 0.025], "CoStar/TE: ADR +3.1% 2026, +1.6% 2027 (+2.1% ex World Cup); 2.5% after = assumption"),
    ("Airbnb ADR growth (link to the team's ADR line)", [None, 0.035, 0.025, 0.025, 0.025, 0.025], "WIRED to model/assumptions.md WS13 base, ex-FX: 2H26 +3.0% (FY26 blends ~+3.5%), FY27/28 +2.5%, held after. Ex-FX is the right basis for the US share equation. Bear +2.0% / bull +4.0% 2H26"),
    ("Stay length, nights per booking (NA)", [4.1, 4.1, 4.1, 4.1, 4.1, 4.1], "EXPLICIT LEVER added 8 Sep 2026. FY20-25 10-Ks: NA 4.4/4.3/4.2/4.1/4.1/4.1 - FLAT since 2023, so the U.S. base carries no drag. Global fell 4.1->3.7 (-2.0%/yr, ~58mm nights forgone in 2025) but that is EMEA (4.4->3.8) and LatAm (4.4->3.6); APAC rose 2.8->3.3. Bear = the EMEA pattern reaches NA (-2%/yr -> 2030 nights 154.8mm, CAGR +1.3%); bull = +1%/yr (179.8mm, +4.4%). Caveat: the 2020-22 plateau was COVID long-stay inflation, so part of the global fall is self-limiting normalisation"),
    ("Own-category nights growth (category adoption)", [None, 0.04, 0.04, 0.035, 0.035, 0.03], "GROUNDED: inverting the model on disclosed NA nights (146/154/158mm FY23-25) implies own-category growth 7.9% (2024) -> 4.5% (2025); 4% entry = observed 2025 exit rate, fade extends the observed deceleration. category_adoption_evidence.csv"),
]
path_row = {}
for label, vals, src in paths:
    r += 1
    path_row[label] = r
    ws.cell(r, 1, label)
    # Growth-rate rows have no 2025 value and format as %; the stay-length row is a LEVEL in nights
    # and does have a 2025 value, so it must not be blanked or percent-formatted.
    is_level = "Stay length" in label
    for j, v in enumerate(vals):
        if v is not None:
            c = ws.cell(r, 2 + j, v); c.font = BLUE
            c.number_format = "0.00" if is_level else PCT
    if not is_level:
        ws.cell(r, 2).value = "—"
    ws.cell(r, 8, src).font = Font(name="Arial", size=9)
ws.cell(path_row["Airbnb ADR growth (link to the team's ADR line)"], 1).fill = YELLOW
ws.cell(path_row["Stay length, nights per booking (NA)"], 1).fill = YELLOW

# ------------------------------------------------------------------ Calibration_2025
cs = wb.create_sheet("Calibration_2025")
cs.column_dimensions["A"].width = 40
for c in "BCDEFGHIJ":
    cs.column_dimensions[c].width = 15
cs["A1"] = "2025 calibration (U.S.) — party-nights, millions"; cs["A1"].font = H1
hdr = ["Segment", "Airbnb nights", "Own-category Airbnb", "Contestable Airbnb", "Hotel party-nights", "Contestable pool", "P(Airbnb | pool)", "Airbnb share of all lodging"]
for j, h in enumerate(hdr):
    c = cs.cell(3, 1 + j, h); c.font = BOLD; c.alignment = Alignment(wrap_text=True)
cs.row_dimensions[3].height = 32
A = addr
us_nights = f"({A['Airbnb North America nights 2025 (mm)']}*{A['U.S. share of North America (revenue proxy)']})"
wsum = "+".join([f"Inputs!$B${seg_row[g]}*Inputs!$C${seg_row[g]}" for g in SEG])
hotel_rn = f"({A['U.S. hotel room nights sold 2024 (mm)']}*(1+{A['Room-night growth 2025 (assumed)']}))"
biz = f"({hotel_rn}*{A['Business share of room nights']})"
leis = f"({hotel_rn}*(1-{A['Business share of room nights']}))"
unit = "+".join([f"Inputs!$D${seg_row[g]}*Inputs!$E${seg_row[g]}*Inputs!$F${seg_row[g]}" for g in SEG])
cal_row = {}
for i, g in enumerate(SEG):
    rr = 4 + i
    cal_row[g] = rr
    sr = seg_row[g]
    cs.cell(rr, 1, g)
    cs.cell(rr, 2, f"={us_nights}*Inputs!$B${sr}*Inputs!$C${sr}/({wsum})").number_format = NUM
    cs.cell(rr, 3, f"=B{rr}*(1-{A['Share of Airbnb guests who would have used a hotel absent Airbnb']})").number_format = NUM
    cs.cell(rr, 4, f"=B{rr}-C{rr}").number_format = NUM
    extra = f"+{biz}*{A['Corporate bookings single-occupancy share']}" if g == "solo" else f"+{biz}*(1-{A['Corporate bookings single-occupancy share']})" if g == "pair" else ""
    cs.cell(rr, 5, f"={leis}/({unit})*Inputs!$D${sr}*Inputs!$E${sr}{extra}").number_format = NUM
    cs.cell(rr, 6, f"=D{rr}+E{rr}").number_format = NUM
    cs.cell(rr, 7, f"=D{rr}/F{rr}").number_format = PCT
    cs.cell(rr, 8, f"=B{rr}/(B{rr}+E{rr})").number_format = PCT
tr = 8
cs.cell(tr, 1, "TOTAL").font = BOLD
for col in "BCDEF":
    cs[f"{col}{tr}"] = f"=SUM({col}4:{col}7)"; cs[f"{col}{tr}"].number_format = NUM; cs[f"{col}{tr}"].font = BOLD
cs[f"G{tr}"] = f"=D{tr}/F{tr}"; cs[f"G{tr}"].number_format = PCT; cs[f"G{tr}"].font = BOLD
cs[f"H{tr}"] = f"=B{tr}/(B{tr}+E{tr})"; cs[f"H{tr}"].number_format = PCT; cs[f"H{tr}"].font = BOLD
cs["A10"] = "Check: Airbnb U.S. nights = NA nights × U.S. share"; cs["B10"] = f"={us_nights}"; cs["B10"].number_format = NUM
cs["A11"] = "Check: hotel room nights 2025 (mm)"; cs["B11"] = f"={hotel_rn}"; cs["B11"].number_format = NUM
cs["A12"] = "Hotel party-nights < room nights because parties of 3+ take 1.5–2.5 rooms. Business room nights are split solo/pair by the corporate single-occupancy share; leisure room nights are converted to parties with the leisure party mix, relative nights and rooms per party."
cs["A12"].font = Font(name="Arial", size=9, italic=True); cs["A12"].alignment = Alignment(wrap_text=True); cs.merge_cells("A12:H12"); cs.row_dimensions[12].height = 40

# ------------------------------------------------------------------ Projection
ps = wb.create_sheet("Projection")
ps.column_dimensions["A"].width = 46
for j in range(len(YEARS)):
    ps.column_dimensions[get_column_letter(2 + j)].width = 13
ps["A1"] = "Projection — U.S. Airbnb nights from choice probabilities (millions)"; ps["A1"].font = H1
ps["A2"] = "Nights = Σ segments [ own-category nights + contestable pool × P(Airbnb) ].  logit P(t) = logit P(t−1) − β·[ln(1+Airbnb ADR g) − ln(1+hotel ADR g)] + product shift."
ps["A2"].font = Font(name="Arial", size=9, italic=True)
ps["A3"] = "Year".upper(); ps["A3"].font = BOLD
for j, y in enumerate(YEARS):
    ps.cell(3, 2 + j, str(y)).font = BOLD
yc = lambda j: get_column_letter(2 + j)          # projection column for year index j
ic = lambda j: get_column_letter(2 + j)          # Inputs year column (same layout)
switch_rate = A["Switch rate: Airbnb-hotel switching per % price gap"]
rp = path_row
ADR_KEY = "Airbnb ADR growth (link to the team's ADR line)"
HOTEL_KEY = 'Hotel ADR growth'
DEM_KEY = 'U.S. lodging demand growth (hotel-contestable pool)'
CAT_KEY = 'Own-category nights growth (category adoption)'
row = 4
ps.cell(row, 1, "Relative price change: ln(1+Airbnb ADR g) − ln(1+hotel ADR g)").font = BOLD
for j in range(1, len(YEARS)):
    ps.cell(row, 2 + j, f"=LN(1+Inputs!{ic(j)}{rp[ADR_KEY]})-LN(1+Inputs!{ic(j)}{rp[HOTEL_KEY]})").number_format = "0.000"
dln_row = row
blocks = {}
for g in SEG:
    row += 2
    ps.cell(row, 1, f"Segment: {g}").font = BOLD; ps.cell(row, 1).fill = GREY
    sr, cr = seg_row[g], cal_row[g]
    # M
    row += 1; mrow = row
    ps.cell(row, 1, "Contestable pool M (hotel + contestable Airbnb)")
    ps.cell(row, 2, f"=Calibration_2025!F{cr}").font = GREEN; ps.cell(row, 2).number_format = NUM
    for j in range(1, len(YEARS)):
        ps.cell(row, 2 + j, f"={yc(j-1)}{row}*(1+Inputs!{ic(j)}{rp[DEM_KEY]})*(1+Inputs!$H${sr})").number_format = NUM
    # N
    row += 1; nrow = row
    ps.cell(row, 1, "Own-category Airbnb nights N")
    ps.cell(row, 2, f"=Calibration_2025!C{cr}").font = GREEN; ps.cell(row, 2).number_format = NUM
    for j in range(1, len(YEARS)):
        ps.cell(row, 2 + j, f"={yc(j-1)}{row}*(1+Inputs!$H${sr})*(1+Inputs!{ic(j)}{rp[CAT_KEY]})").number_format = NUM
    # P
    row += 1; prow = row
    ps.cell(row, 1, "P(Airbnb | contestable pool)")
    ps.cell(row, 2, f"=Calibration_2025!G{cr}").font = GREEN; ps.cell(row, 2).number_format = PCT
    for j in range(1, len(YEARS)):
        prev = f"{yc(j-1)}{row}"
        ps.cell(row, 2 + j, f"=1/(1+EXP(-(LN({prev}/(1-{prev}))-{switch_rate}*{yc(j)}${dln_row}+Inputs!$I${sr})))").number_format = PCT
    # nights
    row += 1; arow = row
    ps.cell(row, 1, f"Airbnb nights — {g}").font = BOLD
    for j in range(len(YEARS)):
        ps.cell(row, 2 + j, f"={yc(j)}{nrow}+{yc(j)}{mrow}*{yc(j)}{prow}").number_format = NUM
        ps.cell(row, 2 + j).font = BOLD
    blocks[g] = dict(M=mrow, N=nrow, P=prow, A=arow)
row += 2
ps.cell(row, 1, "U.S. AIRBNB NIGHTS (mm)").font = H1
tot_row = row
for j in range(len(YEARS)):
    ps.cell(row, 2 + j, "=" + "+".join(f"{yc(j)}{blocks[g]['A']}" for g in SEG)).number_format = NUM
    ps.cell(row, 2 + j).font = BOLD
row += 1
ps.cell(row, 1, "growth")
for j in range(1, len(YEARS)):
    ps.cell(row, 2 + j, f"={yc(j)}{tot_row}/{yc(j-1)}{tot_row}-1").number_format = PCT
growth_row = row
row += 1
ps.cell(row, 1, "Airbnb share of hotel-contestable pool")
for j in range(len(YEARS)):
    num = "+".join(f"{yc(j)}{blocks[g]['M']}*{yc(j)}{blocks[g]['P']}" for g in SEG)
    den = "+".join(f"{yc(j)}{blocks[g]['M']}" for g in SEG)
    ps.cell(row, 2 + j, f"=({num})/({den})").number_format = PCT
row += 1
ps.cell(row, 1, "Airbnb share of all U.S. lodging party-nights")
for j in range(len(YEARS)):
    num = f"{yc(j)}{tot_row}"
    den = "+".join(f"{yc(j)}{blocks[g]['N']}+{yc(j)}{blocks[g]['M']}" for g in SEG)
    ps.cell(row, 2 + j, f"={num}/({den})").number_format = PCT

# revenue plug
row += 2
ps.cell(row, 1, "PLUG INTO THE REVENUE MODEL (U.S. slice)").font = BOLD; ps.cell(row, 1).fill = GREY
row += 1; adr_row = row
ps.cell(row, 1, "Airbnb ADR ($, GBV per night) — team input")
ps.cell(row, 2, 255).font = BLUE; ps.cell(row, 2).number_format = "$#,##0"; ps.cell(row, 2).fill = YELLOW
ps.cell(row, 8, "2025 NA GBV $40.3B ÷ 158M nights = $255 (FY2025 10-K); grows with the Airbnb ADR path on Inputs").font = Font(name="Arial", size=9)
for j in range(1, len(YEARS)):
    ps.cell(row, 2 + j, f"={yc(j-1)}{row}*(1+Inputs!{ic(j)}{rp[ADR_KEY]})").number_format = "$#,##0"
row += 1; take_row = row
ps.cell(row, 1, "Take rate — team input (carries the host-only fee migration)")
ps.cell(row, 8, TAKE_RATE_NOTE).font = Font(name="Arial", size=9)
for j, v in enumerate(TAKE_RATE_PATH):
    c = ps.cell(row, 2 + j, v); c.font = BLUE; c.number_format = PCT; c.fill = YELLOW
row += 1; fx_row = row
ps.cell(row, 1, "FX factor (1.00 for USD) — team input")
for j in range(len(YEARS)):
    c = ps.cell(row, 2 + j, 1.0); c.font = BLUE; c.number_format = "0.00"
row += 1
ps.cell(row, 1, "U.S. GBV ($mm) = nights × ADR × FX").font = BOLD
for j in range(len(YEARS)):
    ps.cell(row, 2 + j, f"={yc(j)}{tot_row}*{yc(j)}{adr_row}*{yc(j)}{fx_row}").number_format = "$#,##0"
gbv_row = row
row += 1
ps.cell(row, 1, "U.S. revenue ($mm) = GBV × take rate").font = BOLD
for j in range(len(YEARS)):
    c = ps.cell(row, 2 + j, f"={yc(j)}{gbv_row}*{yc(j)}{take_row}"); c.number_format = "$#,##0"; c.font = BOLD
row += 2
ps.cell(row, 1, "How to wire it: replace the U.S./North-America nights growth plug in the team model with row " + str(tot_row) +
        " (or its growth in row " + str(growth_row) + "). Keep ADR and FX where they are — this sheet only explains NIGHTS. "
        "The take-rate row is NOT a constant: it steps 13.4% → 13.6% by FY27 for the host-only fee migration, so reconcile it with the team model rather than overwriting it blind. "
        "For other regions, either repeat the calibration with that region's hotel data or apply the rest-of-world growth input.").font = Font(name="Arial", size=9, italic=True)
ps.cell(row, 1).alignment = Alignment(wrap_text=True); ps.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7); ps.row_dimensions[row].height = 48

# ------------------------------------------------------------------ Sensitivity (python output)
ss = wb.create_sheet("Sensitivity")
ss.column_dimensions["A"].width = 12
for c in "BCDE":
    ss.column_dimensions[c].width = 22
ss["A1"] = "Sensitivity — 2030 U.S. Airbnb nights (mm) and 2025–30 CAGR"; ss["A1"].font = H1
ss["A2"] = "Values computed by analysis/src/choice_nights_driver.py (same model); rows = switch rate (share sensitivity to the % price gap; called beta in the F&F paper), columns = Airbnb ADR growth minus hotel ADR growth per year. Static output, not formulas."
ss["A2"].font = Font(name="Arial", size=9, italic=True)
sens = pd.read_csv(ROOT / "data/processed/choice_driver_sensitivity.csv")
piv = sens.pivot(index="switch_rate", columns="abnb_adr_premium_growth", values="us_nights_2030_mm")
cag = sens.pivot(index="switch_rate", columns="abnb_adr_premium_growth", values="cagr_2025_30")
ss["A4"] = "switch rate \\ ADR premium"; ss["A4"].font = BOLD
for j, col in enumerate(piv.columns):
    c = ss.cell(4, 2 + j, f"{col:+.0%}/yr"); c.font = BOLD
for i, b in enumerate(piv.index):
    ss.cell(5 + i, 1, b).font = BLUE
    for j, col in enumerate(piv.columns):
        ss.cell(5 + i, 2 + j, round(float(piv.loc[b, col]), 1)).number_format = NUM
r0 = 5 + len(piv.index) + 1
ss.cell(r0, 1, "CAGR 2025–30").font = BOLD
for i, b in enumerate(cag.index):
    ss.cell(r0 + 1 + i, 1, b).font = BLUE
    for j, col in enumerate(cag.columns):
        ss.cell(r0 + 1 + i, 2 + j, float(cag.loc[b, col])).number_format = PCT

# ------------------------------------------------------------------ Countries (python output)
cs2 = wb.create_sheet("Countries")
cs2.column_dimensions["A"].width = 11
for c in "BCDEFGH":
    cs2.column_dimensions[c].width = 17
cs2["A1"] = "Europe 2025 calibration — measured Eurostat data (vs U.S. revenue proxy)"; cs2["A1"].font = H1
cs2["A2"] = ("Computed by analysis/src/choice_nights_driver_countries.py. Platform guest-nights (Airbnb+Booking+Expedia, "
             "Eurostat tour_ce_omr) x Airbnb listing share (FR 69% / ES 50% / IT 53% / DE 51%, myDataValue/AirDNA) vs hotel "
             "guest-nights (Eurostat I551; ES & DE are 2024 vintage). Guest-nights are converted to party-nights by people "
             "per party, not rooms per party. Party mixes transplanted (Airbnb global fit; U.S. hotel travel-party est.); "
             "CONTESTABLE 38% is the U.S. F&F figure. Static output, not formulas.")
cs2["A2"].font = Font(name="Arial", size=9, italic=True)
cs2["A2"].alignment = Alignment(wrap_text=True); cs2.merge_cells("A2:H2"); cs2.row_dimensions[2].height = 60
ctry = pd.read_csv(ROOT / "data/processed/choice_driver_countries_calibration_2025.csv")
hdrs = ["country", "segment", "airbnb_party_nights_mm", "airbnb_contestable_mm", "hotel_party_nights_mm",
        "p_airbnb_in_pool", "airbnb_share_all_lodging"]
labels = ["Country", "Segment", "Airbnb party-nights (mm)", "of which contestable (mm)", "Hotel party-nights (mm)",
          "P(Airbnb | contestable pool)", "Airbnb share of all lodging"]
for j, h in enumerate(labels):
    cs2.cell(4, 1 + j, h).font = BOLD
for i, (_, r) in enumerate(ctry.iterrows()):
    rr = 5 + i
    cs2.cell(rr, 1, r["country"])
    cs2.cell(rr, 2, r["segment"]).font = BOLD if r["segment"] == "TOTAL" else Font(name="Arial", size=10)
    for j, h in enumerate(hdrs[2:5]):
        cs2.cell(rr, 3 + j, round(float(r[h]), 1)).number_format = NUM
    cs2.cell(rr, 6, float(r["p_airbnb_in_pool"])).number_format = PCT
    cs2.cell(rr, 7, float(r["airbnb_share_all_lodging"])).number_format = PCT
rr = 5 + len(ctry) + 1
cs2.cell(rr, 1, "U.S. comparison: 10.9% of lodging party-nights (Calibration_2025). France is the outlier (31%); Spain/Italy ~15% "
                "sit at U.S. levels; Germany 7%. Rest-of-world plug candidates: weight these by Airbnb regional nights.")
cs2.cell(rr, 1).font = Font(name="Arial", size=9, italic=True)
cs2.cell(rr, 1).alignment = Alignment(wrap_text=True); cs2.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=7)
cs2.row_dimensions[rr].height = 34

# ------------------------------------------------------------------ Global (python output)
gs = wb.create_sheet("Global")
gs.column_dimensions["A"].width = 10
for c in "BCDEFGH":
    gs.column_dimensions[c].width = 14
gs["A1"] = "Global nights build — replaces the 10% rest-of-world plug"; gs["A1"].font = H1
gs["A2"] = ("Computed by analysis/src/choice_nights_driver_global.py. US = full segment choice model (beta 5.0, team ADR "
            "line ex-FX from model/assumptions.md WS13 base). EMEA = measured 4-country Eurostat calibration scaled to "
            "EMEA's 215mm nights, same M/P/N machinery in aggregate (category growth 7%→5% vs ~10% implied). NA-ex-US "
            "tracks the US. LatAm/APAC = explicit fades from disclosed +18%/+15%. Static output, not formulas.")
gs["A2"].font = Font(name="Arial", size=9, italic=True)
gs["A2"].alignment = Alignment(wrap_text=True); gs.merge_cells("A2:H2"); gs.row_dimensions[2].height = 56
glob = pd.read_csv(ROOT / "data/processed/choice_driver_global_projection.csv")
gh = ["year", "us", "na_ex_us", "emea", "latam", "apac", "global_nights_mm", "global_growth"]
gl = ["Year", "US", "NA ex-US", "EMEA", "LatAm", "APAC", "Global nights (mm)", "Growth"]
for j, h in enumerate(gl):
    gs.cell(4, 1 + j, h).font = BOLD
for i, (_, r) in enumerate(glob.iterrows()):
    rr = 5 + i
    gs.cell(rr, 1, int(r["year"])).font = BOLD
    for j, h in enumerate(gh[1:7]):
        gs.cell(rr, 2 + j, round(float(r[h]), 1)).number_format = NUM
    if pd.notna(r["global_growth"]):
        gs.cell(rr, 8, float(r["global_growth"])).number_format = PCT
rr = 5 + len(glob) + 1
# regional block on the Global sheet
reg = pd.read_csv(ROOT / "data/processed/choice_driver_regional_projection.csv")
rr0 = 5 + len(glob) + 2
gs.cell(rr0, 1, "BY AIRBNB REPORTING SEGMENT (mm nights)").font = BOLD
for j, h in enumerate(["Year", "North America", "EMEA", "LatAm", "APAC", "Total"]):
    gs.cell(rr0 + 1, 1 + j, h).font = BOLD
for i, (_, r) in enumerate(reg.iterrows()):
    gs.cell(rr0 + 2 + i, 1, int(r["year"])).font = BOLD
    for j, c in enumerate(["north_america", "emea", "latam", "apac", "total"]):
        gs.cell(rr0 + 2 + i, 2 + j, round(float(r[c]), 1)).number_format = NUM
rr1 = rr0 + 2 + len(reg)
gs.cell(rr1, 1, "CAGR 2025-30").font = BOLD
for j, (c, v) in enumerate([("north_america", 0.0285), ("emea", 0.0418), ("latam", 0.1259),
                            ("apac", 0.1099), ("total", 0.0638)]):
    gs.cell(rr1, 2 + j, v).number_format = PCT
rr = rr1 + 2
gs.cell(rr, 1, "Confidence differs sharply by region. North America is the full segment choice model; EMEA is "
               "calibrated on measured Eurostat platform and hotel nights for FR/ES/IT/DE and scaled. LatAm and "
               "APAC are growth fades off disclosed 2025 rates with NO hotel-side data and no choice model - yet "
               "they are 30% of 2025 nights and 62% of the 2025-30 growth. That is the least evidenced part of "
               "the forecast and the first place to spend more research.")
gs.cell(rr, 1).font = Font(name="Arial", size=9, italic=True)
gs.cell(rr, 1).alignment = Alignment(wrap_text=True); gs.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=8)
gs.row_dimensions[rr].height = 58
rr += 2
gs.cell(rr, 1, "Reconciliation: team model WS13 base has total nights FY26 +9.9%, FY27 +8.9%, FY28 +7.4%; this build "
               "runs +7.1% / +7.2% / +7.1%. The gap is almost entirely North America (team 2H26 NA +7-8% vs this model's "
               "US +3.3% for 2026) — the choice model says NA growth at that pace needs share gains or category adoption "
               "above the 2025 exit rate.")
gs.cell(rr, 1).font = Font(name="Arial", size=9, italic=True)
gs.cell(rr, 1).alignment = Alignment(wrap_text=True); gs.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=8)
gs.row_dimensions[rr].height = 46

# ------------------------------------------------------------------ Validation (python output)
vs = wb.create_sheet("Validation")
vs.column_dimensions["A"].width = 34
for c in "BCDE":
    vs.column_dimensions[c].width = 15
vs.column_dimensions["F"].width = 78
vs["A1"] = "Independent checks on the model — what has been tested, and what survived"; vs["A1"].font = H1
vs["A2"] = ("Every row is a check run against data outside the model. 'Held' means the model's value survived; "
            "'contested' means a credible source disagrees and the disagreement is unresolved.")
vs["A2"].font = Font(name="Arial", size=9, italic=True)
vs["A2"].alignment = Alignment(wrap_text=True); vs.merge_cells("A2:F2"); vs.row_dimensions[2].height = 28
vhdr = ["What was tested", "Model value", "Check gave", "Verdict", "Evidence"]
for j, h in enumerate(vhdr):
    vs.cell(4, 1 + j, h).font = BOLD
VROWS = [
    ("U.S. nights level (supply side)", "138.4mm", "156 vs 87.3 n/listing", "HELD",
     "Bottom-up from raw Inside Airbnb across 8 cities at a calibrated 50% review rate gives 156 nights per active listing vs 87.3 implied nationally. The +78% gap is supply MIX: at ~30% large-urban, the other 70% need only ~58 nights/yr, which is seasonal rural/vacation-home supply. bottom_up_nights_from_raw.py"),
    ("Airbnb review rate", "n/a (input to the check)", "43-60%, centred 50%", "PINNED",
     "984,203 Inside Airbnb reviews against 3,304,396 Eurostat MEASURED platform stays for Vienna/Berlin/Brussels/Prague/Madrid. Rules out both literature extremes (30%, 72%). review_rate_calibration.py"),
    ("U.S. revenue reconciliation", "US_ADR_PREMIUM 1.05", "$4.97bn vs $4.76bn at 1.00", "CORRECTED",
     "A revenue share was being used as a nights share. Setting the premium to 1.05 clears it and moves U.S. nights 145.4 -> 138.4mm. Levels scale; growth is unaffected."),
    ("Switch rate anchor", "5.0 (grid 2.5-10.3)", "10.3 reproduces F&F exactly", "HELD",
     "F&F (AER 2022) Appendix Table E9: a uniform +1% on all hotel prices lifts Airbnb demand 3.76%. Discounted from 10.3 for tier-level, 10-city, 2014 scope. Note it is near-inert at the team's near-parity ADR path."),
    ("Substitution share", "CONTESTABLE 0.38", "NYC ADR +4.7-6.3% observed", "CONTESTED",
     "The model predicted +4.0-6.5% hotel ADR from LL18 and the EJPE 2025 diff-in-diff measured +4.7-6.3%. BUT Airbnb's own economists (CRA, Dec-2024) read the same event as 'limited substitution to hotels'. The disagreement is whether NYC hotels were capacity-constrained. Do not present as uncontested."),
    ("Rooms per party", "1 / 1 / 1.5 / 2.5", "2.01 guests/room (Japan)", "HELD",
     "Implies leisure guests-per-occupied-room of 2.0-2.27. Japan gives 2.01 blended (JTA guest-nights / MHLW room stock x occupancy), and the industry double-occupancy factor for holiday hotels is 1.8-2.5. Was the top uncited input."),
    ("Mix drift (party size)", "+0.62%/yr Airbnb side", "NA +0.66%/yr", "HELD FOR NA ONLY",
     "122 markets / 36 countries: North America +0.66%/yr with 52% of markets significant. But EMEA is FLAT (-0.01%), corroborated independently by Spain's INE microdata. The global +0.62% was really a North America number - do not carry it into EMEA or APAC."),
    ("Party-size divergence", "rental drifts 2.35x hotel", "1 market for, 2 against", "NOT ESTABLISHED",
     "Hawaii supports it over 11 years. Spain's INE microdata says the rental/hotel ratio is FLAT (t=+0.12) over 11 years and the UK gap narrowed 2022-24. The strongest dataset is one of the two against. Treat as the optimistic case."),
    ("Party-size LEVEL gap", "rentals host larger parties", "1.13-1.55x, 4 sources", "HELD",
     "Booking rectour24 39/40 countries (t=10.2), Spain INE 1.167x stable over 12 years, UK GBTS 1.5x on family share, Hawaii 1.08x. This is the solid half of the party-size story."),
]
for i, (what, mv, got, verdict, ev) in enumerate(VROWS):
    r_ = 5 + i
    vs.cell(r_, 1, what); vs.cell(r_, 2, mv); vs.cell(r_, 3, got)
    c = vs.cell(r_, 4, verdict); c.font = BOLD
    vs.cell(r_, 5, ev).alignment = Alignment(wrap_text=True, vertical="top")
    vs.row_dimensions[r_].height = 56
vs.column_dimensions["E"].width = 96

for sh in wb.worksheets:
    for rowc in sh.iter_rows():
        for c in rowc:
            if c.font is None or c.font.name != "Arial":
                c.font = Font(name="Arial", size=c.font.size or 10, bold=c.font.bold, italic=c.font.italic, color=c.font.color)
OUT.parent.mkdir(parents=True, exist_ok=True)
wb.save(OUT)
print("wrote", OUT)
