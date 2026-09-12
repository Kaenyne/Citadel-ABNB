"""Build the point-in-time spine: calendar.csv, targets.csv, windows.csv.

SOURCES (every derived column documents its origin here and in the note):

calendar.csv
  print_quarter, reaction_date          <- data/processed/abnb_earnings_reactions.csv
  print_date                            <- data/processed/overnight/02_guidance_ledger.csv (print_date,
                                           the date of the call; ABNB reports after the close, so the
                                           market reaction lands the next session = reaction_date)
  guide_date                            == print_date (the guide is in the same-evening letter)
  next_quarter_guided, guide_lo/hi/mid  <- 02_guidance_ledger.csv, metric == 'revenue_usd_m',
                                           guide_type == 'range'
  letter_date                           == print_date (8-K Ex.99.1 shareholder letter)
  filing_form, filing_date, accession   <- data/manifests/edgar_filings_log.csv, matched on
                                           report_date == quarter end of print_quarter.
                                           NOTE the 10-K can post-date the print (FY2023: print
                                           2024-02-13, 10-K 2024-02-16), which is why the PIT rule
                                           is written against print_date AND filing_date separately.

targets.csv
  revenue_musd, gbv_musd, nights_m, adr_usd, take_rate_pct,
  fx_pts_revenue, fx_pts_adr            <- 02_kpi_panel_quarterly.csv (same column names, gbv_musd
                                           already present; adr_usd and take_rate_pct are OUTPUTS of
                                           the identity in that file, carried as targets only because
                                           packages want to score them)
  revenue_yoy, gbv_yoy, nights_yoy, adr_yoy  <- computed here as 100*(y/y_lag4 - 1) from the levels,
                                           NOT taken from the panel's reported columns, so the
                                           baselines and the targets are arithmetically consistent.
                                           panel revenue_yoy_reported_pct is carried alongside for
                                           reconciliation as revenue_yoy_panel.
  guide_lo/hi/mid                       <- 02_guidance_ledger.csv revenue_usd_m ranges, indexed by
                                           TARGET quarter
  guide_date                            <- print_date of the call that issued that guide
  actual_over_guide_mid                 <- revenue_musd / guide_mid (ratio, not pct); cross-checked
                                           against 02_guidance_cushion_series.pct_distance_from_mid
  street_pre_guide_musd / _vendor / _as_of
                                        <- 16_consensus_at_print_merged.csv next_q_cons_revenue_musd
                                           on the ISSUING print row; as_of = that print date (the
                                           number is quoted in the print-morning article, before the
                                           after-close letter). For 2026Q4 and later: taken from the
                                           L0 vintage register if it exists, else 04_current_consensus.
  cons_at_print_musd / _vendor          <- 16_consensus_at_print_merged.csv cons_revenue_musd on the
                                           row for THIS quarter (the at-print consensus, i.e. the
                                           number the print is judged against; NOT usable at the guide
                                           date for this quarter)
  print_date                            <- calendar
"""
from __future__ import annotations

import datetime as _dt

import numpy as np
import pandas as pd

from . import quarters as Q
from . import paths as P

LEVEL_TARGETS = ["revenue_musd", "gbv_musd", "nights_m", "adr_usd", "take_rate_pct"]
GROWTH_TARGETS = ["revenue_yoy", "gbv_yoy", "nights_yoy", "adr_yoy"]
ALL_TARGETS = LEVEL_TARGETS + GROWTH_TARGETS + ["fx_pts_revenue", "fx_pts_adr"]

# Metrics whose natural naive is a random walk on the level (no y/y structure).
FLOW_PCT_TARGETS = {"take_rate_pct", "fx_pts_revenue", "fx_pts_adr"}

NEXT_EVENT_PRINT_DATE = _dt.date(2026, 11, 5)   # expected 3Q26 print; AFTER the 22-24 Oct finals


def _read_guide_rows() -> pd.DataFrame:
    g = pd.read_csv(P.SRC_GUIDANCE_LEDGER)
    g = g[(g["metric"] == "revenue_usd_m") & (g["guide_type"] == "range")].copy()
    g["target_period"] = g["target_period"].map(Q.canon)
    g["print_quarter"] = g["print_quarter"].map(Q.canon)
    g["print_date"] = pd.to_datetime(g["print_date"]).dt.date
    g = g.sort_values("target_period").reset_index(drop=True)
    return g[["print_quarter", "print_date", "target_period",
              "value_low", "value_high", "value_mid", "actual"]]


def build_calendar() -> pd.DataFrame:
    led = pd.read_csv(P.SRC_GUIDANCE_LEDGER)
    led["print_quarter"] = led["print_quarter"].map(Q.canon)
    led["print_date"] = pd.to_datetime(led["print_date"]).dt.date
    ev = (led.groupby("print_quarter", as_index=False)["print_date"].min()
             .rename(columns={"print_date": "print_date"}))

    rx = pd.read_csv(P.SRC_EARNINGS_REACTIONS)
    rx["print_quarter"] = rx["quarter"].map(Q.canon)
    rx["reaction_date"] = pd.to_datetime(rx["reaction_date"]).dt.date
    ev = ev.merge(rx[["print_quarter", "reaction_date"]], on="print_quarter", how="left")

    gr = _read_guide_rows()
    gmap = gr.set_index("print_quarter")
    ev["next_quarter_guided"] = ev["print_quarter"].map(gmap["target_period"])
    ev["guide_lo"] = ev["print_quarter"].map(gmap["value_low"])
    ev["guide_hi"] = ev["print_quarter"].map(gmap["value_high"])
    ev["guide_mid"] = ev["print_quarter"].map(gmap["value_mid"])

    ev["guide_date"] = ev["print_date"]
    ev["letter_date"] = ev["print_date"]
    ev["fiscal_quarter"] = ev["print_quarter"]
    ev["quarter_end"] = ev["print_quarter"].map(Q.quarter_end)

    # EDGAR periodic filing for the same report period
    fl = pd.read_csv(P.SRC_EDGAR_LOG)
    fl = fl[fl["form"].isin(["10-Q", "10-K"])].copy()
    fl["report_date"] = pd.to_datetime(fl["report_date"]).dt.date
    fl["filing_date"] = pd.to_datetime(fl["filing_date"]).dt.date
    fl = fl.sort_values("filing_date").drop_duplicates("report_date", keep="first")
    fm = fl.set_index("report_date")
    ev["filing_form"] = ev["quarter_end"].map(fm["form"])
    ev["filing_date"] = ev["quarter_end"].map(fm["filing_date"])
    ev["filing_accession"] = ev["quarter_end"].map(fm["accession"])

    ev["is_forecast_row"] = False
    ev["print_date_basis"] = "ledger"

    # Pre-ledger quarters (3Q20, 4Q20-) that the KPI panel carries but the guidance
    # ledger does not date. Their print dates are approximated as quarter end + 46 days
    # so that the 2023 origins can see 2020 history; the approximation is flagged in
    # print_date_basis and only ever decides whether a 2020 quarter is visible in 2023,
    # which is not a close call. No guide is attached to these rows.
    kq = pd.read_csv(P.SRC_KPI_QUARTERLY)["quarter"].map(Q.canon).tolist()
    earliest = ev["print_quarter"].min()
    pre = [q for q in kq if q < earliest]
    if pre:
        add = pd.DataFrame([{
            "print_quarter": q, "print_date": Q.quarter_end(q) + _dt.timedelta(days=46),
            "reaction_date": pd.NaT, "next_quarter_guided": pd.NA,
            "guide_lo": np.nan, "guide_hi": np.nan, "guide_mid": np.nan,
            "guide_date": pd.NaT, "letter_date": pd.NaT,
            "fiscal_quarter": q, "quarter_end": Q.quarter_end(q),
            "filing_form": pd.NA, "filing_date": pd.NA, "filing_accession": pd.NA,
            "is_forecast_row": False, "print_date_basis": "approx_qend_plus_46d",
        } for q in sorted(set(pre))])
        ev = pd.concat([add, ev], ignore_index=True)

    # upcoming event: the 3Q26 print / 4Q26 guide, 5 Nov 2026
    nxt = pd.DataFrame([{
        "print_quarter": "2026Q3",
        "print_date": NEXT_EVENT_PRINT_DATE,
        "reaction_date": _dt.date(2026, 11, 6),
        "next_quarter_guided": "2026Q4",
        "guide_lo": np.nan, "guide_hi": np.nan, "guide_mid": np.nan,
        "guide_date": NEXT_EVENT_PRINT_DATE,
        "letter_date": NEXT_EVENT_PRINT_DATE,
        "fiscal_quarter": "2026Q3",
        "quarter_end": _dt.date(2026, 9, 30),
        "filing_form": "10-Q", "filing_date": pd.NA, "filing_accession": pd.NA,
        "is_forecast_row": True, "print_date_basis": "scheduled_forecast",
    }])
    ev = pd.concat([ev, nxt], ignore_index=True).sort_values("print_quarter").reset_index(drop=True)
    cols = ["print_quarter", "fiscal_quarter", "quarter_end", "print_date", "guide_date",
            "letter_date", "reaction_date", "next_quarter_guided",
            "guide_lo", "guide_hi", "guide_mid",
            "filing_form", "filing_date", "filing_accession", "is_forecast_row",
            "print_date_basis"]
    return ev[cols]


def _yoy(s: pd.Series) -> pd.Series:
    return 100.0 * (s / s.shift(4) - 1.0)


def build_targets(cal: pd.DataFrame) -> pd.DataFrame:
    k = pd.read_csv(P.SRC_KPI_QUARTERLY)
    k["quarter"] = k["quarter"].map(Q.canon)
    k = k.sort_values("quarter").reset_index(drop=True)

    t = pd.DataFrame({"quarter": k["quarter"]})
    for c in ["revenue_musd", "gbv_musd", "nights_m", "adr_usd", "take_rate_pct",
              "fx_pts_revenue", "fx_pts_adr"]:
        t[c] = pd.to_numeric(k[c], errors="coerce") if c in k.columns else np.nan
    t["revenue_yoy"] = _yoy(t["revenue_musd"])
    t["gbv_yoy"] = _yoy(t["gbv_musd"])
    t["nights_yoy"] = _yoy(t["nights_m"])
    t["adr_yoy"] = _yoy(t["adr_usd"])
    t["revenue_yoy_panel"] = pd.to_numeric(k.get("revenue_yoy_reported_pct"), errors="coerce")
    t["gbv_yoy_panel"] = pd.to_numeric(k.get("gbv_yoy_reported_pct"), errors="coerce")

    # guides, indexed by TARGET quarter
    gr = _read_guide_rows().rename(columns={"target_period": "quarter",
                                            "value_low": "guide_lo",
                                            "value_high": "guide_hi",
                                            "value_mid": "guide_mid",
                                            "print_date": "guide_date",
                                            "print_quarter": "guide_issued_on"})
    t = t.merge(gr[["quarter", "guide_lo", "guide_hi", "guide_mid", "guide_date",
                    "guide_issued_on"]], on="quarter", how="outer")
    t = t.sort_values("quarter").reset_index(drop=True)

    t["actual_over_guide_mid"] = t["revenue_musd"] / t["guide_mid"]

    # print dates
    pd_map = cal.set_index("print_quarter")["print_date"]
    t["print_date"] = t["quarter"].map(pd_map)

    # pre-guide Street, stamped with the vintage of the ISSUING call
    cm = pd.read_csv(P.SRC_CONSENSUS_MERGED)
    cm["print_quarter"] = cm["print_quarter"].map(Q.canon)
    cm["print_date"] = pd.to_datetime(cm["print_date"]).dt.date
    cm["next_quarter"] = cm["next_quarter"].where(cm["next_quarter"].notna()).map(
        lambda x: Q.canon(x) if isinstance(x, str) else x)
    pre = cm.dropna(subset=["next_quarter"])[
        ["next_quarter", "next_q_cons_revenue_musd", "next_q_cons_vendor", "print_date"]
    ].rename(columns={"next_quarter": "quarter",
                      "next_q_cons_revenue_musd": "street_pre_guide_musd",
                      "next_q_cons_vendor": "street_pre_guide_vendor",
                      "print_date": "street_pre_guide_as_of"})
    t = t.merge(pre, on="quarter", how="left")

    atp = cm[["print_quarter", "cons_revenue_musd", "cons_revenue_vendor"]].rename(
        columns={"print_quarter": "quarter",
                 "cons_revenue_musd": "cons_at_print_musd",
                 "cons_revenue_vendor": "cons_at_print_vendor"})
    t = t.merge(atp, on="quarter", how="left")

    # forward quarters not covered by the at-print file: L0 register if present, else current consensus
    fwd = _forward_consensus()
    if fwd is not None and len(fwd):
        t = t.merge(fwd, on="quarter", how="left", suffixes=("", "_fwd"))
        for c in ["street_pre_guide_musd", "street_pre_guide_vendor", "street_pre_guide_as_of"]:
            t[c] = t[c].where(t[c].notna(), t.get(c + "_fwd"))
            if c + "_fwd" in t.columns:
                t = t.drop(columns=[c + "_fwd"])

    t["has_actual"] = t["revenue_musd"].notna()
    cols = ["quarter", "print_date", "revenue_musd", "gbv_musd", "nights_m", "adr_usd",
            "take_rate_pct", "fx_pts_revenue", "fx_pts_adr",
            "revenue_yoy", "gbv_yoy", "nights_yoy", "adr_yoy",
            "revenue_yoy_panel", "gbv_yoy_panel",
            "guide_lo", "guide_hi", "guide_mid", "guide_date", "guide_issued_on",
            "actual_over_guide_mid",
            "street_pre_guide_musd", "street_pre_guide_vendor", "street_pre_guide_as_of",
            "cons_at_print_musd", "cons_at_print_vendor", "has_actual"]
    return t[cols]


def _forward_consensus():
    """Consensus for quarters beyond the at-print file. L0 register preferred."""
    rows = []
    if P.SRC_L0_VINTAGE_REGISTER.exists():
        try:
            v = pd.read_csv(P.SRC_L0_VINTAGE_REGISTER)
            need = {"period", "metric", "value", "vendor", "as_of"}
            if need.issubset(set(v.columns)):
                v = v[v["metric"].astype(str).str.lower().str.startswith("revenue")]
                for _, r in v.iterrows():
                    try:
                        q = Q.canon(r["period"])
                    except ValueError:
                        continue
                    if not q.endswith(("Q1", "Q2", "Q3", "Q4")):
                        continue
                    rows.append({"quarter": q,
                                 "street_pre_guide_musd": float(r["value"]),
                                 "street_pre_guide_vendor": str(r["vendor"]),
                                 "street_pre_guide_as_of": pd.to_datetime(r["as_of"]).date()})
        except Exception:
            rows = []
    if not rows and P.SRC_CURRENT_CONSENSUS.exists():
        v = pd.read_csv(P.SRC_CURRENT_CONSENSUS)
        v = v[(v["metric"] == "revenue") & (v["unit"] == "musd")]
        for _, r in v.iterrows():
            try:
                q = Q.canon(r["period"])
            except ValueError:
                continue
            rows.append({"quarter": q,
                         "street_pre_guide_musd": float(r["value"]),
                         "street_pre_guide_vendor": str(r["vendor"]),
                         "street_pre_guide_as_of": pd.to_datetime(r["as_of"]).date()})
    if not rows:
        return None
    f = pd.DataFrame(rows).sort_values("street_pre_guide_as_of")
    return f.drop_duplicates("quarter", keep="last").reset_index(drop=True)
