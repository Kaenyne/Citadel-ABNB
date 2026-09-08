"""Three charts for deck v2 (built 2026-09-03; layout pass the same day): S9 bridal-AUR strip, S11 print-day move
distribution, A13 bear scoreboard. Outputs: exhibit_bridal_aur_strip.png, exhibit_print_day_moves.png
(+ print_day_moves.csv), exhibit_bear_scoreboard.png (+ bear_scoreboard.csv).
Palette: dataviz reference slots 1-3 + red pole (validated)."""
import os, textwrap, numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
BLUE, ORANGE, AQUA, RED, BLUE_L, ORANGE_L = "#2a78d6", "#eb6834", "#1baf7a", "#e34948", "#9ec5f4", "#f7b899"

def esc(s):
    return str(s).replace("$", r"\$")   # matplotlib reads $...$ as mathtext

def style(ax, ylabel=None):
    ax.set_facecolor(SURFACE)
    for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_alpha(0.4); ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0); ax.tick_params(length=0, labelsize=9)
    if ylabel: ax.set_ylabel(ylabel, fontsize=9, color=INK2)

# ---------------- 1. Bridal / fashion / total AUR strip (six quarters of disclosure) ----------------
q = ["FY25 Q4", "FY26 Q1", "FY26 Q2", "FY26 Q3", "FY26 Q4", "FY27 Q1"]
bridal = [(2.0, "+2%", True), (1.0, "up slightly", False), (4.0, "+4%", True), (6.0, "+6%", True), (4.0, "up", False), (8.0, "+HSD", False)]
fashion = [(8.0, "+8%", True), (10.0, "+10%", True), (12.0, "+12%", True), (8.0, "+8%", True), (5.0, "up", False), (4.0, "up", False)]
merch = [7.0, 8.0, 9.0, 7.0, 5.0, 4.5]
src = ["FY2025_Q4.txt:240-242", "FY2026_Q1.txt:184-186", "FY2026_Q2.txt:198", "FY2026_Q3.txt:144-153", "FY2026_Q4.txt:214", "FY2027_Q1.txt:208-209 / 10-Q"]
fig, ax = plt.subplots(figsize=(12, 5), dpi=200); fig.patch.set_facecolor(SURFACE); style(ax, "AUR growth, % y/y")
x = np.arange(len(q)); w = 0.32
for i, ((bv, bl, bn), (fv, fl, fn)) in enumerate(zip(bridal, fashion)):
    ax.bar(x[i] - w / 2, bv, width=w * 0.92, color=BLUE if bn else BLUE_L, hatch=None if bn else "///", edgecolor=SURFACE if bn else BLUE, linewidth=0 if bn else 1.0, zorder=3)
    ax.bar(x[i] + w / 2, fv, width=w * 0.92, color=ORANGE if fn else ORANGE_L, hatch=None if fn else "///", edgecolor=SURFACE if fn else ORANGE, linewidth=0 if fn else 1.0, zorder=3)
    ax.text(x[i] - w / 2, bv + 0.3, bl, ha="center", va="bottom", fontsize=8.5, color=INK, fontweight="bold" if bn else "normal")
    ax.text(x[i] + w / 2, fv + 0.3, fl, ha="center", va="bottom", fontsize=8.5, color=INK, fontweight="bold" if fn else "normal")
ax.plot(x, merch, color=INK2, linewidth=1.6, marker="o", markersize=5, markeredgecolor=SURFACE, markeredgewidth=1.2, zorder=4, label="total merchandise AUR (disclosed %)")
for i, v in enumerate(merch):
    lab = f"{v:+.1f}%" if v == 4.5 else f"{v:+.0f}%"
    if i == 4:   # FY26 Q4: the fashion 'up' label sits at the same height just to the right, so label on the left
        ax.text(x[i] - 0.05, v + 0.55, lab, fontsize=7.5, color=INK2, ha="right")
    else:
        ax.text(x[i] + 0.02, v + 0.55, lab, fontsize=7.5, color=INK2, ha="left")
ax.set_xticks(x); ax.set_xticklabels(q, fontsize=9.5); ax.set_ylim(0, 14.5)
handles = [Patch(color=BLUE, label="bridal AUR (disclosed %)"), Patch(facecolor=BLUE_L, edgecolor=BLUE, hatch="///", label="bridal AUR (qualitative — plotted at an assumed value)"),
           Patch(color=ORANGE, label="fashion AUR (disclosed %)"), Patch(facecolor=ORANGE_L, edgecolor=ORANGE, hatch="///", label="fashion AUR (qualitative)"),
           plt.Line2D([], [], color=INK2, marker="o", label="total merchandise AUR")]
ax.legend(handles=handles, loc="upper left", fontsize=7.8, frameon=False, ncol=2)
ax.set_title("Six straight quarters of bridal AUR growth — accelerating into FY27 while fashion and total AUR decelerate", loc="left", fontsize=11.5, fontweight="bold", color=INK, pad=10)
fig.text(0.125, -0.01, "Source: Signet earnings calls (" + "; ".join(src) + "). Hatched bars are quarters where management gave direction only ('up slightly', 'up', 'high single digit') and are drawn at +1 / +4 / +8 for the bridal series and +5 / +4 for fashion; do not read their heights as data. Q1 FY27 total AUR = 4.5% per the 10-Q (call: 'nearly 5%').",
         fontsize=7.2, color=INK2, wrap=True)
fig.savefig(os.path.join(HERE, "exhibit_bridal_aur_strip.png"), facecolor=SURFACE, bbox_inches="tight", pad_inches=0.25); plt.close(fig)

# ---------------- 2. Print-day move distribution vs the implied move ----------------
px = pd.read_csv(os.path.join(HERE, "sig_prices_daily.csv")); px["Date"] = pd.to_datetime(px["Date"]); px = px.set_index("Date")["Close"]
calls = pd.read_csv(os.path.join(HERE, "analyst_call_blocks.csv"))[["date", "fy", "qtr"]].drop_duplicates("date")
calls["date"] = pd.to_datetime(calls["date"])
rows = []
for _, r in calls.iterrows():
    d = r["date"]
    if d not in px.index:
        nxt = px.index[px.index >= d]
        if len(nxt) == 0: continue
        d = nxt[0]
    prev = px.index[px.index < d][-1]
    rows.append(dict(date=d.date(), fy=r["fy"], qtr=int(r["qtr"]), move_pct=(px.loc[d] / px.loc[prev] - 1) * 100))
m = pd.DataFrame(rows).sort_values("date"); m.to_csv(os.path.join(HERE, "print_day_moves.csv"), index=False)
implied = 10.95
n = len(m); n_exceed = int((m["move_pct"].abs() > implied).sum()); mean_abs = m["move_pct"].abs().mean(); q2 = m[m["qtr"] == 2]
print(f"prints={n} mean|move|={mean_abs:.1f}% exceed {implied}%: {n_exceed} ({n_exceed/n:.0%}); Q2 prints n={len(q2)} mean signed {q2['move_pct'].mean():+.1f}% mean abs {q2['move_pct'].abs().mean():.1f}% exceed {(q2['move_pct'].abs()>implied).sum()}")
ms = m.sort_values("move_pct").reset_index(drop=True)
fig, ax = plt.subplots(figsize=(12.5, 5.2), dpi=200); fig.patch.set_facecolor(SURFACE); style(ax, "close-to-close move on the print day, %")
cols = [BLUE if v >= 0 else RED for v in ms["move_pct"]]
ax.bar(range(n), ms["move_pct"], color=cols, width=0.8, zorder=3, linewidth=0)
for i, (v, qq) in enumerate(zip(ms["move_pct"], ms["qtr"])):
    if qq == 2: ax.plot(i, v + (1.2 if v >= 0 else -1.2), marker="v" if v >= 0 else "^", color=INK, markersize=4, zorder=4)
ax.axhline(implied, color=INK2, linewidth=1.2, linestyle="--", zorder=2); ax.axhline(-implied, color=INK2, linewidth=1.2, linestyle="--", zorder=2)
ax.axhline(0, color=INK2, linewidth=0.8, alpha=0.6)
# label on the left, where the bars are negative and the +implied line is clear
ax.text(-0.5, implied + 0.8, f"Sept 18 straddle prices ±{implied:.1f}%", ha="left", fontsize=8.5, color=INK2)
# annotation block in the middle of the axis, where bars are within a few percent of zero
q2_exceed = int((q2["move_pct"].abs() > implied).sum())
note = (f"{n_exceed} of {n} prints since 2014 moved more than the current implied move ({n_exceed/n:.0%}); mean absolute move {mean_abs:.1f}%\n"
        f"Q2 prints (▲▼): mean signed {q2['move_pct'].mean():+.1f}%, {q2_exceed} of {len(q2)} exceeded ±{implied:.1f}%")
ax.text(n * 0.27, -implied - 2.2, note, fontsize=8.5, color=INK, va="top", ha="left")
ax.set_xticks([]); ax.set_xlim(-1, n)
ax.set_title("Signet's print-day moves are fat-tailed and skew up: the options market's ±11% has been exceeded on two prints in five", loc="left", fontsize=11.5, fontweight="bold", color=INK, pad=10)
fig.text(0.125, -0.01, "Source: 50 earnings-call dates FY2014 Q4–FY2027 Q1 (Bloomberg transcripts) × Yahoo daily closes (sig_prices_daily.csv); move = close on the call day vs prior close (calls are pre-market). Implied move = ATM straddle for the Sept 18 expiry as % of spot on 9/2/26 (options_ledger.csv). Bars sorted by size; red = down, blue = up.",
         fontsize=7.2, color=INK2, wrap=True)
fig.savefig(os.path.join(HERE, "exhibit_print_day_moves.png"), facecolor=SURFACE, bbox_inches="tight", pad_inches=0.25); plt.close(fig)

# ---------------- 3. Bear scoreboard (VIC rows on the right fiscal year) ----------------
hdr = ["KPI", "VIC (Feb 18 2026, right fiscal year)", "Our number", "Latest actual", "Next print / tracker"]
raw = [
 ("Bridal revenue y/y", "−12.7% (FY27E) → −9.2% (FY28E)", "flat to +LSD (units −LSD/MSD, AUR +HSD)", "Q1 FY27: bridal $ +0.4%, AUR +HSD", "Sept 9 (Q2 colour) · Dec 1–2 · Mar-27"),
 ("LGD unit price (1ct-equivalent)", "−8.4% FY27 → −10.0% FY28", "≥ flat (Tenoris spend/unit flat ~18 months)", "Tenoris Jul-26: flat", "Tenoris monthly · Golan Q3 list (Oct)"),
 ("LGD carat per ring", "flat at 2.26 from FY26", "still rising (market 1.9ct; 3ct 'the standard')", "2.14 (FY25, VIC's own base)", "Knot Feb-27 · BriteCo"),
 ("Natural bridal units", "−26.2% FY27 → −30.0% FY28", "−LSD/MSD (guide, total bridal)", "FY27 guide: bridal units down LSD–MSD", "every print · Tenoris natural units"),
 ("LGD share of bridal $", "50.6% FY27 → 65.5% FY28", "~40% → 'under 50%', converging slowly", "'under 50%' (holiday FY26)", "10-K LGD % (Mar-27) · call colour"),
 ("Total revenue", "$6,555M (−4.4%) FY27", "$6.7–6.9B (guide)", "FY26 $6,814M; Q1 FY27 comp +1.8%", "Sept 9 guide · Mar-27"),
 ("Gross margin", "40.1% FY27 (−60 bps)", "merch margin down H1, flat-to-up H2", "Q1 FY27 merch margin −70 bps (gold)", "Sept 9 (Q2, calibration) · Dec 1–2 (test)"),
 ("SG&A % of sales", "32.6% (+100 bps deleverage)", "leverage at guide midpoint", "Q1 FY27 SG&A −3% y/y, 32.8% of sales", "every print"),
 ("Adjusted operating income", "$494M FY27", "$480–560M (guide)", "FY26 $515M; Q1 FY27 $78.6M (above the high end)", "Sept 9 raise? · Mar-27"),
 ("Adjusted EPS FY27", "$9.08 (below the $9.20 guide floor)", "~$10.4 (consensus $10.65–10.92; UBS $10.90)", "FY26 $9.60; Q1 FY27 $1.56", "Mar-27"),
 ("Adjusted EPS FY28", "$7.85 (→ '$5 by FY30')", "~$10.95 (organic +2%, shares −6%)", "—", "initial FY28 guide, Mar-27"),
 ("Diluted shares", "42M, static", "~37M base case (−6%); ~35M if the $355M authorization is fully used (guide: 39.5M, no buyback)", "40.0M basic (Q1 FY27)", "each 10-Q cover page"),
 ("Services revenue", "+2.4%/yr (conceded by the bear)", "+MSD; ESP plans sold +10.1% FY26, +2.9% Q1 FY27", "Q1 FY27 services +5.2%", "10-Q Note 3 each quarter"),
 ("'Earnings begin declining'", "within 12–24 months of Feb-26 (by Feb-28)", "FY28 guide up y/y", "two beat-and-raises since the post", "Mar-27 initial FY28 guide"),
]
sb = pd.DataFrame(raw, columns=hdr); sb.to_csv(os.path.join(HERE, "bear_scoreboard.csv"), index=False)
colw = [0.15, 0.20, 0.25, 0.21, 0.19]; wrapw = [30, 44, 56, 46, 40]
cells = [[textwrap.fill(esc(v), wrapw[j]) for j, v in enumerate(r)] for r in raw]
lines = [max(c.count("\n") + 1 for c in r) for r in cells]
tot_lines = 1 + sum(lines)
fig_h = 1.5 + 0.17 * tot_lines + 0.08 * (len(raw) + 1)
fig = plt.figure(figsize=(15, fig_h), dpi=200); fig.patch.set_facecolor(SURFACE)
ax = fig.add_axes([0.03, 0.02, 0.94, 0.86]); ax.axis("off")
tbl = ax.table(cellText=cells, colLabels=hdr, cellLoc="left", colLoc="left", colWidths=colw, bbox=[0, 0, 1, 1])
tbl.auto_set_font_size(False); tbl.set_fontsize(7.4)
for (r, c), cell in tbl.get_celld().items():
    nl = 1 if r == 0 else lines[r - 1]
    cell.set_height(0.55 + nl); cell.PAD = 0.025
    cell.set_edgecolor(GRID); cell.set_linewidth(0.6); cell.set_facecolor(SURFACE)
    if r == 0: cell.set_text_props(color=INK, fontweight="bold"); cell.set_facecolor("#f0efec")
    elif c == 1: cell.set_text_props(color=RED)
    elif c == 2: cell.set_text_props(color=BLUE)
    if r > 0 and r % 2 == 0 and c not in (1, 2): cell.set_facecolor("#f7f6f3")
ax.set_title("The bear's model is a dated scoreboard: what VIC needs each line to print, what we expect, and when it resolves", loc="left", fontsize=12, fontweight="bold", color=INK, pad=12)
fig.text(0.03, -0.01, esc("Source: VIC short (greenshoes93, 18 Feb 2026 @ $95, PT $60 = 8–10x FY28E $7.85) exhibit tables transcribed in vic_short_fulltext.md; VIC's '2025' column is Signet FY2025 actuals, so '2026E/27E/28E' are FY2026 (printed $9.60 adj EPS) / FY2027 / FY2028. Our numbers from deck_draft_2026-09-03.md; actuals from the Q1 FY27 10-Q and call. Update after every print."),
         fontsize=7.2, color=INK2, wrap=True, va="top")
fig.savefig(os.path.join(HERE, "exhibit_bear_scoreboard.png"), facecolor=SURFACE, bbox_inches="tight", pad_inches=0.25); plt.close(fig)
print(f"scoreboard: {tot_lines} text lines, fig height {fig_h:.1f} in; saved 3 exhibits")
