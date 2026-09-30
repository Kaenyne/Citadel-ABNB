"""Memo v4.1: put the doc caption on each chart image (takeaway above, source below), as compose.py does for v4.
Graph 1 is the new history chart (graph1_history.R); Graph 2 is v4's stays-index proof chart, unchanged.
Font search covers Windows Calibri as well as the Linux Carlito/Liberation paths compose.py used (compose.py falls back to
PIL's bitmap font on Windows). Output: deck/Graphs/pm_feedback_v4_1/graph{1,2}_captioned.png.
Run from the repo root: python analysis/src/pitch_charts_pm/compose_v4_1.py
"""
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "deck/Graphs/pm_feedback_v4_1"


def font(bold=False, size=60):
    for p in (f"C:/Windows/Fonts/calibri{'b' if bold else ''}.ttf",
              f"/usr/share/fonts/truetype/crosextra/Carlito-{'Bold' if bold else 'Regular'}.ttf",
              f"/usr/share/fonts/truetype/liberation/LiberationSans-{'Bold' if bold else 'Regular'}.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    raise FileNotFoundError("no Calibri/Carlito/Liberation font found")


def compose(src, dst, takeaway, source, top_size=64, src_size=44, wrap_top=66, wrap_src=112):
    chart = Image.open(src).convert("RGB")
    w = chart.width
    ft, fs = font(True, top_size), font(False, src_size)
    top = textwrap.wrap(takeaway, wrap_top)
    bot = textwrap.wrap(source, wrap_src)
    lh_t, lh_s = int(top_size * 1.18), int(src_size * 1.2)
    h = 20 + lh_t * len(top) + 10 + chart.height + 14 + lh_s * len(bot) + 16
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    y = 20
    for line in top:
        d.text((20, y), line, font=ft, fill="#000000")
        y += lh_t
    y += 10
    img.paste(chart, (0, y))
    y += chart.height + 14
    for line in bot:
        d.text((20, y), line, font=fs, fill="#595959")
        y += lh_s
    img.save(dst, dpi=(300, 300))
    print("wrote", dst, img.size)


compose(OUT / "graph1_nights_history.png", OUT / "graph1_captioned.png",
        "Graph 1: Nights growth has slowed since 2023; the bundle bought 2026's bump; 2027 fades to ~6% vs the "
        "Street's 8.9%",
        "Source: Airbnb letters and calls; Bloomberg consensus; team model v2. Shaded = forecast; dashed boxes are "
        "subtracted. Bundle = RNPL, 14-day free cancellation, host-only fee. World Cup +0.5pt is a team assumption.")
compose(ROOT / "deck/Graphs/pm_feedback_v4/graph2_stays_index_proof.png", OUT / "graph2_captioned.png",
        "Graph 2: Counting completed stays, 3Q26 nights grow ~9%, below every Street estimate",
        "Source: Inside Airbnb reviews (123 cities); Airbnb letters; Bloomberg (12 Sep 2026); team model v2. Circles: "
        "walk-forward predictions, refit each quarter (n 10). 3Q26: mapping frozen on 1Q23-2Q25; bar = ±1 RMSE.")
