"""Put the doc caption on the image (takeaway above, source below) for the Word memo, where floating images carry no
paragraphs of their own. Chart bodies are unchanged: Graph 1 is the team's STYLE.md nights chart (model v2), Graph 2 is
proof_chart.py. Output: deck/Graphs/pm_feedback_v4/graph{1,2}_captioned.png.
Run from the repo root: python analysis/src/pitch_charts_pm/compose.py
"""
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "deck/Graphs/pm_feedback_v4"


def font(bold=False, size=60):
    for p in (f"/usr/share/fonts/truetype/crosextra/Carlito-{'Bold' if bold else 'Regular'}.ttf",
              f"/usr/share/fonts/truetype/liberation/LiberationSans-{'Bold' if bold else 'Regular'}.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


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


compose(ROOT / "deck/Graphs/caimanes_model_v2/stylemd/graph2_nights_bundle_separated.png", OUT / "graph1_captioned.png",
        "Graph 1: Ex the bundle, nights grow ~7%, heading to ~6%; 2026's re-acceleration was the bundle, and it laps from 3Q26",
        "Source: Airbnb letters and earnings calls; Bloomberg consensus (12 Sep 2026); team model v2. Dashed boxes are "
        "subtracted; each bar ends at net growth. Bundle = RNPL, 14-day free cancellation, host-only fee. World Cup +0.5pt "
        "in 2Q26 is a team assumption.")
compose(OUT / "graph2_stays_index_proof.png", OUT / "graph2_captioned.png",
        "Graph 2: Counting completed stays, 3Q26 nights grow ~9%, below every Street estimate",
        "Source: Inside Airbnb review dumps (123 cities); Airbnb letters; Bloomberg consensus (12 Sep 2026); team model v2. "
        "Circles to 2Q26: walk-forward predictions, refit each quarter (1Q24-2Q26, n 10). 3Q26: mapping frozen on "
        "1Q23-2Q25; bar = ±1 walk-forward RMSE.")
