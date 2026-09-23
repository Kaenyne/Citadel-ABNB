"""
Build the thesis-3 margin bridge page from 46_bridge.json and the two-pager text below.

Run (after run.py):  py -3.13 analysis/src/margin_build/46_margin_bridge/build_page.py [extra_output_path.html]
Writes docs/explainers/2026-09-23_abnb_margin_bridge.html (and a copy to the optional path). Every number in COPY traces to
43_thesis3_integration.md, 45_ai_margin.md and 46_bridge_meta.csv on branch krish/cost-leg.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DATA = json.loads((ROOT / "data/processed/margin_build/46_margin_bridge/46_bridge.json").read_text(encoding="utf-8"))

COPY = [
    dict(where="Investment thesis, point (3)",
         text="(3) Operating leverage runs in reverse: Airbnb’s costs behave like a budget, so even if FY27 costs follow the Street’s own "
              "plan, our lower nights and ADR take the FY27 margin about 100bp below consensus and put the FY26 “at least 35.5%” floor at risk."),
    dict(where="Thesis Point 3: Costs",
         text="Sales and marketing has grown faster than revenue for nine straight quarters, rising from 16.5% of revenue in FY23 to 19.4% in FY25 "
              "(23.9% in 1H26), and when revenue growth slowed from 18% to 12% and then 10%, S&M growth rose to 21% and held at 20%. Management "
              "describes brand spend as “effectively a fixed amount of spend for each market” and plans to “reinvest most of these "
              "efficiencies into marketing, product and technology.” AI savings are real but small: the 2Q26 10-Q credits AI with a $17M fall in "
              "support costs, in a quarter when S&M rose $184M and ops and product payroll $89M, and the 2026 guide absorbs “a material increase” "
              "in AI spend. Our model already credits AI (ops, product and G&A fall from 29.2% to 26.2% of revenue by FY27), and the call does not "
              "rest on it: on our revenue, the Street’s own cost plan, flexed down at the historical rate, gives an FY27 margin of 35.4% against "
              "36.4%, and FY26 35.4%, below the floor. Holding consensus would take FY27 cost growth of 7.3%, slower than any year since the IPO. Our "
              "FY27: adjusted EBITDA $5.24bn (34.0%) against the Street’s $5.77bn."),
    dict(where="Valuation (cost leg)",
         text="Our $143.6 value is FY27 adjusted EBITDA of $5.24bn at 14.5x EV/EBITDA: today’s 15.6x on the Street’s FY27, less 0.49 turns per "
              "point of lower growth (95% CI 0.32–0.65, giving $140–147). Thesis 3 accounts for $3.4–5.8 of the $23 a share between $167 "
              "and $143.6, depending on the order of the steps; if FY27 costs grow at their FY24–25 pace (12.6%), the value is $140."),
    dict(where="Catalysts (cost lines)",
         text=["Nov 5, 2026: the Q4 margin sentence and the FY26 floor. In November 2024 a Q4 guide of margin “decline … due to higher "
               "marketing and product development expenses” cut Q4 EBITDA consensus 9.6% and the stock 8.7% on a beat.",
               "Feb 2027 (expected ~11 Feb): the FY27 margin framework. We put a down-year or “investment year” guide at 49%; each 100bp below "
               "the Street’s 36.4% is $158M of FY27 EBITDA."]),
    dict(where="Risk & mitigant (cost lines)",
         text=["Risk: management trims Q4 marketing to hold 35.5% (about $64M on our revenue). Mitigant: a one-quarter trim caps the FY26 miss but "
               "does not change FY27, where holding consensus would need $251M of cuts beyond the Street’s own plan.",
               "Risk: AI savings arrive faster than we model. Mitigant: a generous AI case (support costs per booking −10% across the whole line, "
               "slower product and G&A hiring, lower compute) still leaves FY27 at 35.8%, below the Street’s 36.4%."]),
]

html = (HERE / "page_template.html").read_text(encoding="utf-8")
html = html.replace("/*__DATA__*/null", json.dumps(DATA)).replace("/*__COPY__*/null", json.dumps(COPY, ensure_ascii=False))
assert "__DATA__" not in html and "__COPY__" not in html
out = ROOT / "docs/explainers/2026-09-23_abnb_margin_bridge.html"
out.write_text(html, encoding="utf-8")
for extra in sys.argv[1:]:
    Path(extra).write_text(html, encoding="utf-8")
print("wrote", out, *sys.argv[1:])
