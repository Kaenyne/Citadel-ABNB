"""Memo v4.2 captions: Graph 2 (graph2_triangulation.R) and Graph 3 (the team's STYLE.md margin bridge, model v2, unchanged).
Graph 1 is v4.1's captioned image, unchanged. Reuses compose() from compose_v4_1.py without re-running its outputs.
Run from the repo root: python analysis/src/pitch_charts_pm/compose_v4_2.py
"""
import importlib.util
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "deck/Graphs/pm_feedback_v4_2"

# load font() from compose_v4_1.py without executing its compose() calls
src = (Path(__file__).parent / "compose_v4_1.py").read_text(encoding="utf8").split("\ncompose(")[0]
ns = {"__file__": str(Path(__file__).parent / "compose_v4_1.py")}
exec(compile(src, "compose_v4_1.py", "exec"), ns)
compose = ns["compose"]

compose(OUT / "graph2_triangulation.png", OUT / "graph2_captioned.png",
        "Graph 2: Every read of 3Q26 nights sits below the Street's lowest estimate, and our ADR comes in below too",
        "Source: Inside Airbnb reviews; STR, Eurostat, BLS, INE, EUROCONTROL; Bloomberg consensus (12 Sep 2026); team model "
        "v2. Stays index bar = ±1 walk-forward RMSE.")
compose(ROOT / "deck/Graphs/caimanes_model_v2/stylemd/graph3_margin_bridges.png", OUT / "graph3_captioned.png",
        "Graph 3: Lower revenue, S&M and AI compute take our margin below the Street; AI savings claw back only 20-32bp",
        "Source: LSEG consensus (13 Sep 2026); Airbnb filings; team model v2. Other costs = payments, support payroll, "
        "product development, G&A.")
