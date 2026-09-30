"""Memo v4.3 captions: two charts. Graph 1 = graph1_history.R (nights, 1Q23-4Q27); Graph 2 = the team's STYLE.md margin
bridge (model v2, unchanged). v4.2's stays/ADR chart is dropped: everything on it is in the text.
Reuses compose() from compose_v4_1.py without re-running its outputs.
Run from the repo root: python analysis/src/pitch_charts_pm/compose_v4_3.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "deck/Graphs/pm_feedback_v4_3"
OUT.mkdir(parents=True, exist_ok=True)

src = (Path(__file__).parent / "compose_v4_1.py").read_text(encoding="utf8").split("\ncompose(")[0]
ns = {"__file__": str(Path(__file__).parent / "compose_v4_1.py")}
exec(compile(src, "compose_v4_1.py", "exec"), ns)
compose = ns["compose"]

compose(ROOT / "deck/Graphs/pm_feedback_v4_1/graph1_nights_history.png", OUT / "graph1_captioned.png",
        "Graph 1: Nights growth has slowed since 2023; the bundle bought 2026's bump; 2027 fades to ~6% vs the "
        "Street's 8.9%",
        "Source: Airbnb letters and calls; Bloomberg consensus; team model v2. Shaded = forecast; dashed boxes are "
        "subtracted. Bundle = RNPL, 14-day free cancellation, host-only fee. World Cup +0.5pt is a team assumption.")
compose(ROOT / "deck/Graphs/caimanes_model_v2/stylemd/graph3_margin_bridges.png", OUT / "graph2_captioned.png",
        "Graph 2: Lower revenue, S&M and AI compute take our margin below the Street; AI savings claw back only 20-32bp",
        "Source: LSEG consensus (13 Sep 2026); Airbnb filings; team model v2. Other costs = payments, support payroll, "
        "product development, G&A.")
