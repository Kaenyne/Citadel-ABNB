"""Stock Chart tab: annotated ABNB price history showing what drives the large earnings-day moves.

Contents (top to bottom): title; annotated matplotlib PNG (daily close, 11 earnings big-move days labelled, other
7%+ days as light markers, every print as a green/red tick, 5 Nov 2026 print as a dashed line); the 23-print
reaction table with a summary block; the earnings-day big-move detail; the 7%+ moves by driver and the full
41-row list; the read-across to 5 Nov 2026; sources.

Data: data/processed/abnb_daily_close.csv, abnb_big_moves_7pct.csv, abnb_earnings_reactions.csv,
abnb_big_move_stats_by_driver.csv, reverse_dcf/{B,C,E}/*.csv. The PNG is written to
model/figures/abnb_annotated_stock_chart.png.
"""
from __future__ import annotations
import math
from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter

import style as S

SHEET = "Stock Chart"
FIG_DIR = S.REPO / "model" / "figures"
PNG = FIG_DIR / "abnb_annotated_stock_chart.png"
UPCOMING_PRINT = datetime(2026, 11, 5)

# Short cause per earnings big-move day (3-6 words, condensed from the `trigger` column of abnb_big_moves_7pct.csv).
SHORT_CAUSE = {
    "2021-02-26": "first print; revenue beat",
    "2021-11-05": "record quarter, +67% revenue",
    "2022-05-04": "first profitable Q1; Fed rally",
    "2022-11-02": "beat, Q4 nights guided slower",
    "2023-02-15": "first profitable year; Q1 guide beat",
    "2023-05-10": "nights guided below revenue",
    "2024-08-07": "shorter lead times, US slowing",
    "2024-11-08": "EPS miss, expense growth",
    "2025-02-14": "nights beat; best day on record",
    "2025-08-07": "H2 nights to moderate; $200M spend",
    "2026-08-07": "beat on every KPI; FY guide raised",
}
# Label offsets (points) and alignment per earnings day; up-moves above the line, down-moves below, staggered.
LABEL_POS = {
    "2021-02-26": (-24, 62, "left"),
    "2021-11-05": (-6, 48, "center"),
    "2022-05-04": (28, 44, "left"),
    "2022-11-02": (-60, -40, "center"),
    "2023-02-15": (44, 70, "left"),
    "2023-05-10": (10, -58, "center"),
    "2024-08-07": (-10, -44, "center"),
    "2024-11-08": (30, -70, "left"),
    "2025-02-14": (-10, 56, "center"),
    "2025-08-07": (30, -40, "left"),
    "2026-08-07": (-36, 46, "center"),
}
NON_EARNINGS_STYLE = {
    "Macro/market": dict(marker="o", color="9DB3D1", label="Macro/market (7%+ day)"),
    "Company/other": dict(marker="s", color="B5B5B5", label="Company/other (7%+ day)"),
    "Competitor/industry": dict(marker="D", color="C9A7D9", label="Competitor/industry (7%+ day)"),
}


# ----------------------------------------------------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------------------------------------------------
def _load():
    px = S.read("abnb_daily_close.csv", parse_dates=["Date"]).sort_values("Date")
    moves = S.read("abnb_big_moves_7pct.csv", parse_dates=["date"]).sort_values("date")
    rx = S.read("abnb_earnings_reactions.csv", parse_dates=["reaction_date"]).sort_values("reaction_date")
    stats = S.read("abnb_big_move_stats_by_driver.csv")
    stats = stats.rename(columns={stats.columns[0]: "driver"})
    return px, moves, rx, stats


def _quarter_label(trigger: str) -> str:
    """'Q2'26: beat on ...' -> Q2'26 (the trigger text starts with the quarter tag)."""
    return trigger.split(":")[0].split(" ")[0].strip()


# ----------------------------------------------------------------------------------------------------------------
# Chart
# ----------------------------------------------------------------------------------------------------------------
def _draw_chart(px: pd.DataFrame, moves: pd.DataFrame, rx: pd.DataFrame) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.lines import Line2D

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    navy, orange, green, red = "#1F3864", "#E07B00", "#2E8B57", "#C0392B"
    close = px.set_index("Date")["Close"]

    def price_on(d):
        # last close on or before d (big-move dates are trading days, so this is the same-day close)
        return float(close.loc[:d].iloc[-1])

    fig, ax = plt.subplots(figsize=(14, 6), dpi=100)
    ax.plot(px["Date"], px["Close"], color=navy, lw=1.2, label="ABNB daily close", zorder=2)

    # Non-earnings 7%+ days: small light markers, unlabelled
    for drv, st in NON_EARNINGS_STYLE.items():
        sub = moves[moves["driver"] == drv]
        ax.scatter(sub["date"], [price_on(d) for d in sub["date"]], marker=st["marker"], s=34,
                   color="#" + st["color"], edgecolor="white", linewidth=0.5, zorder=3, label=st["label"])

    # Every print as a green/red tick along the bottom
    y0, y1 = 52, 62
    for _, r in rx.iterrows():
        ax.plot([r["reaction_date"], r["reaction_date"]], [y0, y1],
                color=green if r["abnb_1d_pct"] >= 0 else red, lw=1.6, zorder=3)

    # Earnings big-move days: orange markers + labels
    earn = moves[moves["driver"] == "Earnings"]
    ax.scatter(earn["date"], [price_on(d) for d in earn["date"]], marker="o", s=70, color=orange,
               edgecolor="white", linewidth=0.8, zorder=4, label="Earnings day, |move| >= 7%")
    for _, r in earn.iterrows():
        key = r["date"].strftime("%Y-%m-%d")
        mv = r["abnb_move_pct"]
        cause = SHORT_CAUSE.get(key) or r["trigger"][:36]
        text = f"{_quarter_label(r['trigger'])} {mv:+.1f}%\n{cause}"
        dx, dy, ha = LABEL_POS.get(key, (0, 45 if mv > 0 else -45, "center"))
        ax.annotate(text, xy=(r["date"], price_on(r["date"])), xytext=(dx, dy), textcoords="offset points",
                    ha=ha, va="bottom" if dy > 0 else "top", fontsize=8.2, color="#222222", zorder=5,
                    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#D0D0D0", lw=0.6, alpha=0.95),
                    arrowprops=dict(arrowstyle="-", color=orange, lw=0.9, shrinkA=0, shrinkB=3))

    # Upcoming print
    ax.axvline(UPCOMING_PRINT, color="#555555", ls="--", lw=1.0, zorder=1)
    ax.annotate("5 Nov 2026\n3Q26 print", xy=(UPCOMING_PRINT, 68), xytext=(-6, 0), textcoords="offset points",
                ha="right", va="center", fontsize=8.5, color="#333333")

    ax.set_xlim(datetime(2020, 11, 15), datetime(2026, 12, 20))
    ax.set_ylim(45, 262)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[4, 7, 10]))
    ax.set_ylabel("Close (USD)")
    ax.set_xlabel("")
    ax.grid(True, which="major", color="#E6E6E6", lw=0.6)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.set_title("ABNB since IPO: the 11 earnings days that moved the stock 7% or more, and what caused them",
                 fontsize=12, color=navy, loc="left", pad=10)

    handles, labels = ax.get_legend_handles_labels()
    handles += [Line2D([0], [0], color=green, lw=2), Line2D([0], [0], color=red, lw=2),
                Line2D([0], [0], color="#555555", ls="--", lw=1)]
    labels += ["Print, stock up next day (tick)", "Print, stock down next day (tick)", "Next print, 5 Nov 2026"]
    ax.legend(handles, labels, loc="upper right", fontsize=8, frameon=True, framealpha=0.95, edgecolor="#D0D0D0",
              ncol=2, bbox_to_anchor=(0.995, 0.995))
    fig.text(0.008, 0.012, "Source: data/processed/abnb_daily_close.csv, abnb_big_moves_7pct.csv, "
             "abnb_earnings_reactions.csv. Ticks mark all 23 prints (reaction day, close-to-close).",
             fontsize=7.5, color="#6E6E6E")
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(PNG, dpi=100)
    plt.close(fig)
    return PNG


# ----------------------------------------------------------------------------------------------------------------
# Sheet helpers
# ----------------------------------------------------------------------------------------------------------------
def _date_col(ws, first_row: int, last_row: int, col: int):
    for r in range(first_row, last_row + 1):
        ws.cell(row=r, column=col).number_format = S.FMT_DATE


def _text_table(ws, row: int, df: pd.DataFrame, num_cols: list, num_fmts: dict, text_cols: list, spans: dict,
                width_chars: dict):
    """Numeric columns in A.., then each text column merged across `spans[name]` = (first_col, last_col) with wrap.
    width_chars[name] = approximate characters per line for the row-height estimate. Returns next free row."""
    # header
    for j, name in enumerate(num_cols):
        c = ws.cell(row=row, column=1 + j, value=name)
        c.font = S.f_hdr(); c.fill = S.FILL_HEADER
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for name in text_cols:
        a, b = spans[name]
        c = ws.cell(row=row, column=a, value=name)
        c.font = S.f_hdr(); c.fill = S.FILL_HEADER
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        for k in range(a + 1, b + 1):
            ws.cell(row=row, column=k).fill = S.FILL_HEADER
        ws.merge_cells(start_row=row, start_column=a, end_row=row, end_column=b)
    ws.row_dimensions[row].height = 30
    row += 1
    for _, r in df.iterrows():
        lines = 1
        for j, name in enumerate(num_cols):
            v = r[name]
            if S._isnan(v):
                continue
            if hasattr(v, "item"):
                v = v.item()
            c = ws.cell(row=row, column=1 + j, value=v)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                c.font = S.f_input(); c.number_format = num_fmts.get(name, S.FMT_M1)
                c.alignment = Alignment(horizontal="right", vertical="top")
            else:
                c.font = S.f_label(); c.alignment = Alignment(vertical="top")
                if isinstance(v, datetime):
                    c.number_format = S.FMT_DATE
        for name in text_cols:
            a, b = spans[name]
            v = r[name]
            txt = "" if S._isnan(v) else str(v)
            c = ws.cell(row=row, column=a, value=txt)
            c.font = S.f_label(); c.alignment = Alignment(wrap_text=True, vertical="top")
            ws.merge_cells(start_row=row, start_column=a, end_row=row, end_column=b)
            lines = max(lines, math.ceil(len(txt) / width_chars[name]))
        ws.row_dimensions[row].height = 13.5 * lines + 2
        row += 1
    return row


def _first_float(s) -> float:
    return float(str(s).split()[0])


# ----------------------------------------------------------------------------------------------------------------
# Build
# ----------------------------------------------------------------------------------------------------------------
def build(wb):
    px, moves, rx, stats = _load()
    png = _draw_chart(px, moves, rx)

    ws = wb.create_sheet(SHEET)
    widths = {get_column_letter(c): 11.5 for c in range(2, 19)}
    row = S.setup(
        ws,
        "ABNB stock chart: what moves the stock, Dec 2020 IPO to Sep 2026",
        "Earnings prints are the dominant driver of ABNB's largest days: 11 of the 41 moves of 7% or more since "
        "IPO are earnings days, and they are the biggest (mean 12.1% absolute vs 8.6% for macro days). "
        "The chart labels which prints moved the stock and why; the tables below give every print and every "
        "7%+ day, and the read-across to the 5 Nov 2026 print.",
        widths=widths, label_width=20)
    ws["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells("A2:R2")
    ws.row_dimensions[2].height = 28

    img = XLImage(str(png))
    img.width, img.height = 1400, 600
    ws.add_image(img, "B4")
    row = 4 + math.ceil(600 / 20) + 2  # default row height ~20 px

    # ------------------------------------------------------------------ a. all 23 prints
    row = S.section(ws, row, "Earnings-day reactions, all 23 prints", ncols=18,
                    note="reaction day = first session after the print; close-to-close; excess = ABNB minus QQQ")
    pct_cols = ["abnb_1d_pct", "qqq_1d_pct", "excess_1d_pct", "abnb_5d_pct", "excess_5d_pct",
                "abnb_20d_pct", "excess_20d_pct"]
    a = rx[["quarter", "reaction_date"] + pct_cols].copy()
    for c in pct_cols:
        a[c] = a[c] / 100.0
    n = len(a)
    hdr_row = row + 5                        # summary block (4 rows) + blank, then the table header
    first, last = hdr_row + 1, hdr_row + n
    rng = f"C{first}:C{last}"               # abnb_1d_pct sits in column C (A quarter, B date)
    row = S.write_row(ws, row, "Mean absolute 1-day move (n = 23)", [f"=SUMPRODUCT(ABS({rng}))/COUNT({rng})"],
                      fmt=S.FMT_PCT, kind="formula", bold=True)
    row = S.write_row(ws, row, "Share of prints with |move| >= 7%",
                      [f"=SUMPRODUCT(--(ABS({rng})>=0.07))/COUNT({rng})"], fmt=S.FMT_PCT, kind="formula")
    row = S.write_row(ws, row, "Prints up / down (1-day)",
                      [f'=COUNTIF({rng},">0")', f'=COUNTIF({rng},"<0")'], fmt=S.FMT_INT, kind="formula")
    row = S.write_row(ws, row, "Mean 1-day excess vs QQQ", [f"=AVERAGE(E{first}:E{last})"],
                      fmt=S.FMT_PCT, kind="formula")
    row += 1
    assert row == hdr_row
    fm = {c: S.FMT_PCT for c in pct_cols}
    row = S.table(ws, row, a, first_col=1, fmts=fm, header_height=30)
    _date_col(ws, first, last, 2)
    row = S.text_row(ws, row, "Missing: 20-day returns for the 7 Aug 2026 print (2026Q2) were not yet available in "
                              "the source file. Row highlighting is not applied; large moves are readable from the "
                              "values.", wrap_cols=12)
    row += 1

    # ------------------------------------------------------------------ b. what moved the stock on each earnings day
    row = S.section(ws, row, "What moved the stock on each earnings day (the 11 prints with a 7%+ move)", ncols=18,
                    note="same-day moves of QQQ, BKNG, EXPE for context; trigger and notes from the big-moves file")
    e = moves[moves["driver"] == "Earnings"].copy()
    e["move"] = e["abnb_move_pct"] / 100.0
    for c in ("qqq_pct", "bkng_pct", "expe_pct"):
        e[c] = e[c] / 100.0
    e = e.rename(columns={"date": "date", "qqq_pct": "QQQ same day", "bkng_pct": "BKNG same day",
                          "expe_pct": "EXPE same day", "move": "ABNB move"})
    row = _text_table(
        ws, row, e,
        num_cols=["date", "ABNB move", "QQQ same day", "BKNG same day", "EXPE same day"],
        num_fmts={"ABNB move": S.FMT_PCT, "QQQ same day": S.FMT_PCT, "BKNG same day": S.FMT_PCT,
                  "EXPE same day": S.FMT_PCT},
        text_cols=["trigger", "notes"], spans={"trigger": (6, 9), "notes": (10, 18)},
        width_chars={"trigger": 50, "notes": 118})
    row += 1

    # ------------------------------------------------------------------ c. all 7%+ moves by driver
    row = S.section(ws, row, "All moves of 7% or more since IPO, by driver", ncols=18,
                    note="41 days; percentages are absolute close-to-close moves; excess = ABNB minus the peer")
    st = stats.copy()
    pcols = ["mean_abs_move", "median_abs_move", "max_up", "max_down", "mean_abs_qqq_same_day",
             "mean_abs_excess_vs_qqq", "mean_abs_excess_vs_bkng", "mean_abs_excess_vs_expe"]
    for c in pcols:
        st[c] = st[c] / 100.0
    fm = {c: S.FMT_PCT for c in pcols}
    fm.update({c: S.FMT_INT for c in ("n", "n_up", "n_down", "n_since_2023")})
    row = S.table(ws, row, st, first_col=1, fmts=fm, header_height=42)
    row = S.text_row(ws, row, "Earnings days are fewer than macro days but larger on average, and almost all of the "
                              "move is stock-specific (mean absolute excess vs QQQ 11.3% on earnings days vs 5.1% "
                              "on macro days).", wrap_cols=12)
    row += 1

    full = moves[["date", "abnb_move_pct", "driver", "qqq_pct", "bkng_pct", "expe_pct", "trigger"]].copy()
    full["abnb_move_pct"] = full["abnb_move_pct"] / 100.0
    for c in ("qqq_pct", "bkng_pct", "expe_pct"):
        full[c] = full[c] / 100.0
    full = full.rename(columns={"abnb_move_pct": "ABNB move", "qqq_pct": "QQQ same day",
                                "bkng_pct": "BKNG same day", "expe_pct": "EXPE same day"})
    row = S.text_row(ws, row, "Full list, 41 days (chronological)", font=S.f_label(bold=True))
    row = _text_table(
        ws, row, full,
        num_cols=["date", "ABNB move", "driver", "QQQ same day", "BKNG same day", "EXPE same day"],
        num_fmts={"ABNB move": S.FMT_PCT, "QQQ same day": S.FMT_PCT, "BKNG same day": S.FMT_PCT,
                  "EXPE same day": S.FMT_PCT},
        text_cols=["trigger"], spans={"trigger": (7, 18)}, width_chars={"trigger": 150})
    row += 1

    # ------------------------------------------------------------------ d. read-across to 5 Nov 2026
    row = S.section(ws, row, "Read-across to 5 Nov 2026 (3Q26 print)", ncols=18,
                    note="numbers from data/processed/reverse_dcf/{B,C,E} and docs/reverse_dcf/SYNTHESIS.md section 1")
    dead = S.read("reverse_dcf/C/C_deadband_sensitivity.csv")
    d = dead[(dead["dead_band_pts"] == 0.25) & (dead["sample"] == "post2022")].iloc[0]
    coef = S.read("reverse_dcf/C/C_coefficients_used.csv").set_index("spec_id").loc["S1_post2022"]
    ess = S.read("reverse_dcf/E/E_street_sign_summary.csv").set_index("street_positioned_for")
    esh = S.read("reverse_dcf/E/E_street_sign_history.csv")
    e3q = esh[esh["print"] == "3Q26E"].iloc[0]
    hist = esh[~esh["print"].str.contains("E")]
    n_street_accel_hist = int((hist["street_positioned_for"] == "acceleration").sum())
    bh = S.read("reverse_dcf/B/B_headline.csv").set_index("item")["value"]
    ev_sd = _first_float(bh["event_sd_central_pct"])
    ev_abs = _first_float(bh["event_exp_abs_move_central_pct"])
    raw_rms = float(bh["hist_realised_raw_rms_pct"])
    raw_ge7 = float(bh["hist_realised_raw_share_abs_ge_7pct"])
    raw_ud = str(bh["hist_realised_raw_up_down"])
    spot = float(bh["spot"])
    pull = str(bh["pull_time_utc"])[:10]
    split_excess = str(bh["nights_accel_split_excess"])

    lines = [
        f"Sign rule on printed nights acceleration (workstream C, post-2022 prints, n = {int(coef['n'])}, "
        f"+/-0.25pt dead band): accelerating prints average {d['accel_mean']:+.1f}% day-1 excess vs QQQ "
        f"({int(d['accel_positive'])} of {int(d['accel_n'])} positive); decelerating prints average "
        f"{d['decel_mean']:+.1f}% ({int(d['decel_positive'])} of {int(d['decel_n'])} positive); flat: {d['flat_prints']}; "
        f"Fisher p {d['fisher_p']:.3f}. Regression form: excess = {coef['c']:.2f} + {coef['b_sign']:.2f} x sign, "
        f"R2 {coef['r2']:.2f} (C_coefficients_used.csv, S1_post2022; C_deadband_sensitivity.csv).",
        f"On the raw (not QQQ-excess) return the split is {bh['nights_accel_split_raw']}; on excess it is "
        f"{split_excess} (B_headline.csv). The rule gives the sign of the reaction, not its size, and does not clear "
        "a multiplicity correction (C_multiplicity_holm.csv): 14 prints.",
        f"Where the Street sits for 3Q26: the consensus nights bar is {e3q['street_nights_m']:.1f}M "
        f"({e3q['street_implied_growth_pct']:+.2f}% y/y vs {e3q['prior_quarter_growth_pct']:+.2f}% in 2Q26), i.e. "
        f"positioned for acceleration, for only the {n_street_accel_hist + 1}th time in {len(hist) + 1} prints. The "
        f"{int(ess.loc['acceleration', 'n'])} prior times the Street was positioned for acceleration, all "
        f"{int(ess.loc['acceleration', 'printed_accel'])} printed acceleration, mean day-1 excess "
        f"{ess.loc['acceleration', 'mean_day1_excess']:+.1f}%; the {int(ess.loc['deceleration', 'n'])} times it was "
        f"positioned for deceleration averaged {ess.loc['deceleration', 'mean_day1_excess']:+.2f}% "
        "(E_street_sign_summary.csv, E_street_sign_history.csv).",
        f"Options-implied 5 Nov event: standard deviation {ev_sd:.1f}% ({str(bh['event_sd_central_pct'])[4:].strip('() ')}), "
        f"expected absolute move {ev_abs:.1f}%; spot ${spot:.2f} on {pull} (B_headline.csv, JUDGEMENT rows built from "
        "the measured 16 Oct / 20 Nov straddle pair 9.88% and least-squares 9.16-9.73%).",
        f"Realised print history for scale: raw close-to-close rms {raw_rms:.2f}%, {raw_ge7:.0%} of the 23 prints "
        f"moved 7% or more, {raw_ud} (B_headline.csv, hist_realised_raw_* rows); this tab's table above gives the same "
        "23 prints.",
        "Team read (SYNTHESIS.md section 1): the team's nowcast is a decelerating 3Q26 nights print (+9.5 to 10.0%) "
        "against a Street bar that implies acceleration; on the sign rule that implies a -4 to -6% day conditional on "
        "deceleration and -2 to -3.5% unconditionally, against a 9.5% options-implied dispersion. The trade is the "
        "print reaction, not an estimate revision.",
    ]
    row = S.bullets(ws, row, lines, wrap_cols=18, height=30)
    row += 1

    # ------------------------------------------------------------------ sources
    row = S.sources_block(ws, row, [
        ("Daily close (Yahoo, Dec 2020 to 4 Sep 2026)", "data/processed/abnb_daily_close.csv"),
        ("7%+ days with driver, trigger, notes, peer moves (41 rows)", "data/processed/abnb_big_moves_7pct.csv"),
        ("Earnings-day reactions, 23 prints", "data/processed/abnb_earnings_reactions.csv"),
        ("7%+ move statistics by driver", "data/processed/abnb_big_move_stats_by_driver.csv"),
        ("Sign rule, dead-band sensitivity (post-2022, 0.25pt row)", "data/processed/reverse_dcf/C/C_deadband_sensitivity.csv"),
        ("Sign rule, coefficients used (S1_post2022)", "data/processed/reverse_dcf/C/C_coefficients_used.csv"),
        ("Multiplicity check", "data/processed/reverse_dcf/C/C_multiplicity_holm.csv"),
        ("Street positioning summary", "data/processed/reverse_dcf/E/E_street_sign_summary.csv"),
        ("Street positioning history (16 prints + 3Q26E)", "data/processed/reverse_dcf/E/E_street_sign_history.csv"),
        ("Options headline (event sd, realised history)", "data/processed/reverse_dcf/B/B_headline.csv"),
        ("Reverse DCF synthesis, section 1", "docs/reverse_dcf/SYNTHESIS.md"),
        ("Chart image", "model/figures/abnb_annotated_stock_chart.png"),
    ], ncols=18)
    return ws
