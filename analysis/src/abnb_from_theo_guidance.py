"""Rebuild two processed tables from Theo's guidance dataset (theos-past-research/).

Inputs (tracked in git, built by Theo's abnb_guidance toolkit from SEC-filed shareholder letters
and Nasdaq historical closes):
  theos-past-research/research/guidance/data/normalized/guidance_events.csv
  theos-past-research/research/guidance/data/normalized/guidance_items.csv
  theos-past-research/research/guidance/data/normalized/quarterly_actuals.csv
  theos-past-research/research/guidance/data/normalized/market_returns.csv

Outputs:
  data/processed/abnb_earnings_reactions.csv        1/5/20-session ABNB, QQQ and excess returns per print
  data/processed/abnb_revenue_guidance_vs_actual.csv next-quarter revenue guide vs reported actual

Run: python analysis/src/abnb_from_theo_guidance.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "theos-past-research/research/guidance/data/normalized"
OUT = ROOT / "data/processed"


def read(name):
    with open(SRC / name, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def build_reactions(events):
    rows = {}
    for r in read("market_returns.csv"):
        q = events[r["guidance_event_id"]]["reported_period"]
        d = rows.setdefault(q, {"quarter": q, "reaction_date": r["reaction_session_date"]})
        w = r["window_sessions"]
        if r["value_status"] == "observed":
            d[f"abnb_{w}d_pct"] = round(float(r["raw_total_return"]) * 100, 1)
            d[f"qqq_{w}d_pct"] = round(float(r["benchmark_total_return"]) * 100, 1)
            d[f"excess_{w}d_pct"] = round(float(r["excess_return"]) * 100, 1)
    cols = ["quarter", "reaction_date"] + [f"{k}_{w}d_pct" for w in (1, 5, 20) for k in ("abnb", "qqq", "excess")]
    with open(OUT / "abnb_earnings_reactions.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for q in sorted(rows):
            w.writerow({c: rows[q].get(c, "") for c in cols})
    return len(rows)


def build_guidance(events):
    actual = {r["fiscal_period"]: float(r["value"]) for r in read("quarterly_actuals.csv")}
    items = [r for r in read("guidance_items.csv") if r["metric_code"] == "revenue" and r["measure_type"] == "absolute_range"]
    with open(OUT / "abnb_revenue_guidance_vs_actual.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["guided_quarter", "issued_on_call", "guide_low_musd", "guide_high_musd", "guide_mid_musd",
                    "range_width_pct_of_mid", "actual_musd", "actual_vs_mid_pct", "actual_vs_high_pct"])
        for r in items:
            lo, hi, mid = float(r["value_low"]), float(r["value_high"]), float(r["value_mid"])
            a = actual.get(r["target_period"])
            w.writerow([r["target_period"], events[r["guidance_event_id"]]["reported_period"], int(lo), int(hi), int(mid),
                        round((hi - lo) / mid * 100, 1), int(a) if a else "",
                        round((a / mid - 1) * 100, 1) if a else "", round((a / hi - 1) * 100, 1) if a else ""])
    return len(items)


if __name__ == "__main__":
    events = {r["guidance_event_id"]: r for r in read("guidance_events.csv")}
    print("earnings reactions:", build_reactions(events), "prints")
    print("revenue guidance rows:", build_guidance(events))
