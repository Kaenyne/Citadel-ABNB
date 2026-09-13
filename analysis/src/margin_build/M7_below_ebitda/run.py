"""M7: below-EBITDA bridge and FCF bridge for ABNB. Method `below-ebitda`.

Objects (see docs/margin-build/notes/M7_below_ebitda.md, pre-registration):
  interest_income, sbc, da, tax, share_count, eps, fcf.
Point-in-time refits at every frozen guide date, both replays, both weightings, registered through
the margin harness; LIVE 3Q26-4Q27 and FY26-28 waterfall with a parameter sheet.

Run (from the worktree root):  py -3.13 analysis/src/margin_build/M7_below_ebitda/run.py
"""
from __future__ import annotations

import datetime as dt
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "analysis" / "src" / "margin_build" / "10_harness_margin"))
from harness_margin import (  # noqa: E402
    Q, GUIDE_DATES_ALL, GUIDE_DATES_W1, GUIDE_DATES_W2, GUIDE_DATE_LIVE, TODAY, LIVE_VINTAGES,
    load_targets, windows_for, register, revenue_forecast_pit, load_registry,
)

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

METHOD = "below-ebitda"
OUT = REPO / "data" / "processed" / "margin_build" / "M7_below_ebitda"
OUT.mkdir(parents=True, exist_ok=True)
RAW = REPO / "data" / "raw" / "margin_build" / "M7_below_ebitda"
MB = REPO / "data" / "processed" / "margin_build"
HALF_LIFE = 4.0
RESID_MAX_N = 12
MIN_RESID = 3
ZQ = dict(q05=-1.6448536269514722, q10=-1.2815515655446004, q25=-0.6744897501960817, q50=0.0,
          q75=0.6744897501960817, q90=1.2815515655446004, q95=1.6448536269514722)
QCOLS = list(ZQ)
LIVE_IE_MUSD = 37.0          # 2Q26 printed interest expense on the March 2026 notes (10-Q 2Q26), run-rate
LIVE_ETR = {2026: 18.0, 2027: 17.5, 2028: 17.5}   # WS05 S157 (FY26 high teens), S148 (long-term mid-to-high teens)
OTHER_CF_DISCRETE_CUT = 1000.0   # |CFO residual| above this is a discrete non-cash item (3Q23 VA release), excluded from the pool
FY28_MARGIN_NOTE = "FY28 adj EBITDA = FY27 margin of the same source x FY28 base revenue (flat margin, labelled)"

# ----------------------------------------------------------------------------------------------- helpers

def canon(q: str) -> str:
    return Q.canon(q)


def qidx(q: str) -> int:
    q = canon(q)
    return int(q[:4]) * 4 + int(q[-1]) - 1


def qoy(q: str) -> int:
    return int(canon(q)[-1])


def fy(q: str) -> int:
    return int(canon(q)[:4])


def shift(q: str, k: int) -> str:
    return Q.shift(canon(q), k)


def rw_weights(n: int, weighting: str) -> np.ndarray:
    if n <= 0:
        return np.array([])
    if weighting == "eq":
        return np.ones(n)
    return 0.5 ** (np.arange(n)[::-1] / HALF_LIFE)


def wmean(x, weighting: str) -> float:
    x = np.asarray([v for v in x if pd.notna(v)], dtype=float)
    if len(x) == 0:
        return np.nan
    w = rw_weights(len(x), weighting)
    return float(np.sum(w * x) / np.sum(w))


def qdays(q: str):
    y, k = int(canon(q)[:4]), qoy(q)
    start = dt.date(y, 3 * (k - 1) + 1, 1)
    end = dt.date(y + (k == 4), (3 * k) % 12 + 1, 1) - dt.timedelta(days=1)
    return start, end


# ----------------------------------------------------------------------------------------------- inputs

def load_panel() -> pd.DataFrame:
    p = pd.read_csv(MB / "02_financial_panel" / "02_panel_quarterly.csv")
    p["q"] = p["quarter"].map(canon)
    p = p.set_index("q").sort_index()
    t = load_targets()
    pdm = dict(zip(t["quarter"], t["print_date"]))
    p["print_date"] = p.index.map(lambda q: pdm.get(q))
    p["earning_base"] = p["cash_and_equivalents"] + p["short_term_investments"] + p["funds_held_on_behalf"]
    p["buyback_musd"] = p["buybacks_cash"].fillna(p["buybacks"]).fillna(0.0)
    p["gbv_musd"] = p["gbv_busd"] * 1000.0
    return p


def load_daily(series: str) -> pd.Series:
    d = pd.read_csv(RAW / f"fred_{series}.csv")
    d.columns = ["date", "v"]
    d["v"] = pd.to_numeric(d["v"], errors="coerce")
    d = d.dropna()
    d["date"] = pd.to_datetime(d["date"]).dt.date
    return d.set_index("date")["v"].sort_index()


def load_price() -> pd.Series:
    d = pd.read_csv(REPO / "data" / "processed" / "abnb_daily_close.csv")
    d["Date"] = pd.to_datetime(d["Date"]).dt.date
    return d.set_index("Date")["Close"].sort_index()


class Rates:
    def __init__(self, s: pd.Series):
        self.s = s
        self.idx = np.array(list(s.index))
        self.val = s.to_numpy(dtype=float)

    def at(self, d: dt.date) -> float:
        i = np.searchsorted(self.idx, d, side="right") - 1
        return float(self.val[i]) if i >= 0 else np.nan

    def quarter_mean(self, q: str) -> float:
        a, b = qdays(q)
        m = (self.idx >= a) & (self.idx <= b)
        return float(self.val[m].mean()) if m.any() else np.nan

    def quarter_hat(self, q: str, vd: dt.date) -> float:
        """Realised daily values of the quarter up to vd, spot at vd for the remaining business days."""
        a, b = qdays(q)
        if vd < a:
            return self.at(vd)
        m = (self.idx >= a) & (self.idx <= min(b, vd))
        n_real = int(m.sum())
        n_rem = int(np.busday_count(min(b, vd) + dt.timedelta(days=1), b + dt.timedelta(days=1))) if vd < b else 0
        if n_real + n_rem == 0:
            return self.at(vd)
        return float((self.val[m].sum() + n_rem * self.at(vd)) / (n_real + n_rem))


# ----------------------------------------------------------------------------------------------- tax guide ledger
# hand ledger from WS05 05_statements.csv (ids in the note); value = point ETR read from the sentence
TAX_GUIDES = pd.DataFrame([
    dict(date="2024-02-13", fy_from=2024, fy_to=2025, value=17.5, sid="S077", quote="ETR to approximate the mid-to-high teens in the near-term"),
    dict(date="2024-02-13", fy_from=2026, fy_to=2099, value=21.0, sid="S077", quote="approximate the low 20% range in the long term"),
    dict(date="2024-11-07", fy_from=2024, fy_to=2024, value=20.0, sid="S103", quote="FY2024 ETR approximately 20%"),
    dict(date="2025-02-13", fy_from=2025, fy_to=2025, value=19.5, sid="S115", quote="FY2025 ETR slightly below the long-term ~20%"),
    dict(date="2026-02-12", fy_from=2026, fy_to=2099, value=17.5, sid="S148", quote="long-term ETR to decline to the mid-to-high teens (OBBBA)"),
    dict(date="2026-05-07", fy_from=2026, fy_to=2026, value=18.0, sid="S157", quote="FY2026 ETR in the high teens"),
])
TAX_GUIDES["date"] = pd.to_datetime(TAX_GUIDES["date"]).dt.date


def etr_guide_in_force(vd: dt.date, year: int):
    g = TAX_GUIDES[(TAX_GUIDES["date"] <= vd) & (TAX_GUIDES["fy_from"] <= year) & (TAX_GUIDES["fy_to"] >= year)]
    if len(g) == 0:
        return None, None
    # the most recent sentence wins; a FY-specific sentence beats a long-term one of the same date
    g = g.sort_values(["date", "fy_to"], ascending=[True, True])
    r = g.iloc[-1]
    return float(r["value"]), r["sid"]


# ----------------------------------------------------------------------------------------------- the model

class M7:
    def __init__(self):
        self.P = load_panel()
        self.T = load_targets()
        self.tbill = Rates(load_daily("DTB3"))
        self.dgs1 = Rates(load_daily("DGS1"))
        self.price = Rates(load_price())
        self.grid = pd.read_csv(MB / "10_harness_margin" / "baseline_grid_all_vintages.csv")
        self.grid["vintage_date"] = pd.to_datetime(self.grid["vintage_date"]).dt.date
        self.log = []
        self.full = self.P[self.P["print_date"].notna()]        # the full history (2Q26 vintage)

    # ---- PIT slice
    def hist(self, vd: dt.date) -> pd.DataFrame:
        h = self.P[self.P["print_date"].notna() & (self.P["print_date"] <= vd)]
        return h

    # ---- component: interest income
    def fit_beta(self, h: pd.DataFrame, weighting: str) -> tuple:
        rows = []
        for q in h.index:
            qm1 = shift(q, -1)
            if qm1 not in h.index:
                continue
            r = self.tbill.quarter_mean(q)
            if not np.isfinite(r) or r < 0.5:
                continue
            avgb = 0.5 * (h.at[q, "earning_base"] + h.at[qm1, "earning_base"])
            ii = h.at[q, "interest_income"]
            if pd.isna(avgb) or pd.isna(ii):
                continue
            rows.append(ii / (r / 100.0 * avgb / 4.0))
        rows = rows[-8:]
        return (wmean(rows, weighting) if rows else 1.0), len(rows)     # no post-ZIRP quarter yet: beta 1.0 (labelled n 0)

    def gbv_growth_last(self, h: pd.DataFrame) -> float:
        q = h.index[-1]
        q4 = shift(q, -4)
        if q4 in h.index and pd.notna(h.at[q4, "gbv_musd"]) and h.at[q4, "gbv_musd"] > 0:
            return float(h.at[q, "gbv_musd"] / h.at[q4, "gbv_musd"] - 1.0)
        return 0.0

    def path_series(self, h: pd.DataFrame, col: str, q: str, growth_fn) -> float:
        """Value of a same-quarter-last-year-scaled series at q, chained when q-4 is itself unknown."""
        if q in h.index and pd.notna(h.at[q, col]):
            return float(h.at[q, col])
        q4 = shift(q, -4)
        base = self.path_series(h, col, q4, growth_fn)
        return base * (1.0 + growth_fn(q))

    def interest_income(self, vd, q, h, beta, growth_fn, rate_shift_bp=0.0):
        last = h.index[-1]
        cash_sti = float(h.at[last, "cash_and_equivalents"] + h.at[last, "short_term_investments"])
        def base_at(qq):
            if qq in h.index:
                return float(h.at[qq, "earning_base"])
            return cash_sti + self.path_series(h, "funds_held_on_behalf", qq, growth_fn)
        avgb = 0.5 * (base_at(q) + base_at(shift(q, -1)))
        r = self.tbill.quarter_hat(q, vd) + rate_shift_bp / 100.0
        return beta * max(r, 0.0) / 100.0 * avgb / 4.0, r, avgb

    # ---- component: SBC
    def fit_sbc_growth(self, h: pd.DataFrame, weighting: str) -> float:
        s = h["sbc_total_is"]
        g = [s.iloc[i] / s.loc[shift(s.index[i], -4)] - 1.0 for i in range(len(s))
             if shift(s.index[i], -4) in s.index and pd.notna(s.iloc[i]) and s.loc[shift(s.index[i], -4)] > 0]
        return wmean(g[-4:], weighting)

    def sbc(self, h, q, g):
        return self.path_series(h, "sbc_total_is", q, lambda _q: g)

    # ---- component: D&A
    def da(self, h, weighting, spec="mean4"):
        s = h["da"].dropna()
        if spec == "last_value":
            return float(s.iloc[-1])
        return wmean(s.iloc[-4:], weighting)

    # ---- component: tax
    def etr(self, vd, h, q, spec="guide_or_ttm"):
        if spec == "guide_or_ttm":
            g, sid = etr_guide_in_force(vd, fy(q))
            if g is not None:
                return g, f"guide:{sid}"
        s = h[["tax_provision", "pretax_income"]].dropna().iloc[-4:]
        if len(s) < 4 or s["pretax_income"].sum() <= 0:
            return 21.0, "ttm_fallback_statutory"
        r = 100.0 * s["tax_provision"].sum() / s["pretax_income"].sum()
        r = float(np.clip(r, 10.0, 30.0))
        return r, "ttm"

    # ---- component: shares
    def fit_share_delta(self, h, weighting):
        s = h["shares_diluted_m"].dropna()
        d = s.diff().dropna().iloc[-4:]
        return wmean(d, weighting)

    def fit_share_structural(self, vd, h, weighting):
        s = h["shares_diluted_m"].dropna()
        rows = []
        for i in range(1, len(s)):
            q = s.index[i]
            pavg = self.price.quarter_mean(q)
            bb = float(h.at[q, "buyback_musd"]) if pd.notna(h.at[q, "buyback_musd"]) else 0.0
            if not np.isfinite(pavg):
                continue
            rows.append((s.iloc[i] - s.iloc[i - 1]) + bb / pavg)
        iss = wmean(rows[-4:], weighting)
        bb_rate = float(h["buyback_musd"].iloc[-4:].mean())
        p_vd = self.price.at(vd)
        return dict(issuance_m=iss, buyback_musd_q=bb_rate, price=p_vd, delta=-bb_rate / p_vd + iss)

    def shares(self, h, q, delta):
        s = h["shares_diluted_m"].dropna()
        steps = qidx(q) - qidx(s.index[-1])
        return float(s.iloc[-1] + steps * delta)

    # ---- component: interest expense, other income
    def ie(self, vd, h):
        if vd >= GUIDE_DATE_LIVE:
            return LIVE_IE_MUSD
        s = h["interest_expense"].dropna().iloc[-4:]
        return float(s.median()) if len(s) else 5.0

    def other(self, h, weighting):
        return wmean(h["other_income_expense"].dropna().iloc[-8:], weighting)

    # ---- EBITDA input (PIT baseline in force at the vintage)
    def ebitda_pit(self, vd, q):
        g = self.grid[(self.grid["target"] == "adj_ebitda_musd") & (self.grid["quarter"] == canon(q))
                      & (self.grid["vintage_date"] == vd) & (self.grid["prior_basis"] == "PIT")]
        for obj in ["q_guide_implied", "guide_implied", "seasonal_naive_drift"]:
            r = g[g["object"] == obj]
            if len(r) and np.isfinite(r["point"].iloc[0]):
                return float(r["point"].iloc[0]), obj
        # not in the grid (h >= 3 at a guide date): the drift rule on the PIT history, chained if q-4 is unknown
        h = self.hist(vd)
        y = h["adj_ebitda_reported"].dropna()
        last, last4 = y.index[-1], shift(y.index[-1], -4)
        drift = float(y.loc[last] - y.loc[last4]) if last4 in y.index else 0.0
        def val(qq):
            if qq in y.index:
                return float(y.loc[qq])
            return val(shift(qq, -4)) + drift
        return val(canon(q)), "seasonal_naive_drift_direct"

    # ---- working capital
    def wc_swing(self, h, col, q, growth_fn):
        return self.path_series(h, col, q, growth_fn)

    def wc_balance_ratio(self, h, bal_col, q, gbv_fn, weighting):
        k = qoy(q)
        same = [t for t in h.index if qoy(t) == k and pd.notna(h.at[t, bal_col]) and pd.notna(h.at[t, "gbv_musd"])][-3:]
        ratio = wmean([h.at[t, bal_col] / h.at[t, "gbv_musd"] for t in same], weighting)
        return ratio * gbv_fn(q)

    def other_cf(self, h, weighting):
        """CFO - NI - D&A - SBC - change in unearned fees. Funds payable is NOT subtracted: its change is offset one-for-one
        by the change in funds receivable / held on behalf of customers (panel change_funds_receivable_xbrl = -change_funds_payable),
        so it nets to ~0 inside CFO (correction to the pre-registration, see note)."""
        r = (h["cfo"] - h["net_income"] - h["da"] - h["sbc_total_is"] - h["change_unearned_fees"]).dropna()
        r = r[r.abs() <= OTHER_CF_DISCRETE_CUT]      # 3Q23: -$2,464m = the non-cash valuation-allowance release inside NI (excluded, see note)
        return wmean(r.iloc[-8:], weighting), r

    def other_cf_seasonal(self, h, q, weighting):
        _, r = self.other_cf(h, weighting)
        same = [r.loc[t] for t in r.index if qoy(t) == qoy(q)][-3:]
        return wmean(same, weighting)

    def capex(self, h, weighting):
        return wmean(h["capex"].dropna().iloc[-4:], weighting)

    # ------------------------------------------------------------------ one vintage, one quarter, one spec set
    def forecast(self, vd: dt.date, q: str, weighting: str, prior_basis: str, live_path: dict | None = None,
                 ebitda_override: float | None = None, ebitda_label: str | None = None,
                 rate_shift_bp: float = 0.0, buyback_override: float | None = None, etr_override: float | None = None):
        h = self.hist(vd)
        fit_h = self.full if prior_basis == "full_sample" else h
        q = canon(q)
        out = dict(vintage_date=vd, quarter=q, weighting=weighting, prior_basis=prior_basis, n_train=len(h))
        # growth of GBV for the funds-held / working-capital paths
        if live_path is not None:
            def growth_fn(qq):
                qq4 = shift(qq, -4)
                g_q = live_path["gbv"].get(qq)
                g_4 = live_path["gbv"].get(qq4, float(h.at[qq4, "gbv_musd"]) if qq4 in h.index else np.nan)
                return (g_q / g_4 - 1.0) if (g_q is not None and np.isfinite(g_4) and g_4 > 0) else self.gbv_growth_last(h)
            def gbv_fn(qq):
                return live_path["gbv"].get(qq, self.path_series(h, "gbv_musd", qq, growth_fn))
        else:
            g_last = self.gbv_growth_last(h)
            def growth_fn(qq):
                return g_last
            def gbv_fn(qq):
                return self.path_series(h, "gbv_musd", qq, growth_fn)
        # interest income
        beta, nb = self.fit_beta(fit_h, weighting)
        ii, r_hat, avgb = self.interest_income(vd, q, h, beta, growth_fn, rate_shift_bp)
        out.update(beta=beta, beta_n=nb, tbill_hat=r_hat, avg_base=avgb, interest_income_musd=ii)
        # SBC
        g_sbc = self.fit_sbc_growth(fit_h, weighting)
        sbc = self.sbc(h, q, g_sbc)
        s_ = fit_h["sbc_total_is"].dropna()
        g_last = float(s_.iloc[-1] / s_.loc[shift(s_.index[-1], -4)] - 1.0) if shift(s_.index[-1], -4) in s_.index else g_sbc
        out.update(sbc_growth=g_sbc, sbc_musd=sbc, sbc_growth_last=g_last, sbc_musd_yoy_last=self.sbc(h, q, g_last))
        # D&A
        da = self.da(fit_h if prior_basis == "full_sample" else h, weighting)
        da_last = self.da(h, weighting, "last_value")
        out.update(da_musd=da, da_last_value=da_last)
        # tax
        etr, etr_src = self.etr(vd, h, q)
        etr_ttm, _ = self.etr(vd, h, q, spec="ttm")
        if etr_override is not None:
            etr, etr_src = etr_override, "override"
        out.update(tax_rate_pct=etr, tax_rate_src=etr_src, tax_rate_ttm=etr_ttm)
        # shares
        d_sh = self.fit_share_delta(fit_h, weighting)
        st = self.fit_share_structural(vd, fit_h if prior_basis == "full_sample" else h, weighting)
        if buyback_override is not None:
            st = dict(st, buyback_musd_q=buyback_override, delta=-buyback_override / st["price"] + st["issuance_m"])
        sh = self.shares(h, q, d_sh)
        sh_st = self.shares(h, q, st["delta"])
        out.update(share_delta=d_sh, diluted_shares_m=sh, diluted_shares_structural_m=sh_st, **{f"st_{k}": v for k, v in st.items()})
        # revenue leg
        if live_path is not None:
            rev = live_path["rev"].get(q, np.nan)
            leg = "live_path"
        else:
            rev, leg = revenue_forecast_pit(vd, q, prior_basis)
        out.update(revenue_leg=rev, revenue_leg_kind=leg, sbc_pct_rev=100.0 * sbc / rev if rev else np.nan)
        # EBITDA inputs
        if ebitda_override is not None:
            e_pit, e_src = ebitda_override, ebitda_label or "override"
        else:
            e_pit, e_src = self.ebitda_pit(vd, q)
        e_known = float(self.P.at[q, "adj_ebitda_reported"]) if (q in self.P.index and pd.notna(self.P.at[q, "adj_ebitda_reported"])) else np.nan
        ie = self.ie(vd, h)
        oth = self.other(h, weighting)
        out.update(ebitda_pit=e_pit, ebitda_pit_src=e_src, ebitda_known=e_known, interest_expense_musd=ie, other_income_musd=oth)
        # waterfall for each EBITDA input
        for tag, e in [("pit", e_pit), ("known", e_known)]:
            op = e - da - sbc
            pretax = op + ii - ie + oth
            tax = etr / 100.0 * pretax
            ni = pretax - tax
            out.update({f"op_income_{tag}": op, f"pretax_{tag}": pretax, f"tax_provision_{tag}": tax,
                        f"net_income_{tag}": ni, f"eps_{tag}": ni / sh, f"eps_{tag}_structural": ni / sh_st})
        # FCF
        duf_s = self.wc_swing(h, "change_unearned_fees", q, growth_fn)
        dfp_s = self.wc_swing(h, "change_funds_payable", q, growth_fn)
        uf_bal = self.wc_balance_ratio(h, "unearned_fees_balance", q, gbv_fn, weighting)
        fh_bal = self.wc_balance_ratio(h, "funds_held_on_behalf", q, gbv_fn, weighting)
        qm1 = shift(q, -1)
        uf_prev = float(h.at[qm1, "unearned_fees_balance"]) if qm1 in h.index else self.wc_balance_ratio(h, "unearned_fees_balance", qm1, gbv_fn, weighting)
        fh_prev = float(h.at[qm1, "funds_held_on_behalf"]) if qm1 in h.index else self.wc_balance_ratio(h, "funds_held_on_behalf", qm1, gbv_fn, weighting)
        duf_b, dfp_b = uf_bal - uf_prev, fh_bal - fh_prev
        oth_cf, _ = self.other_cf(fit_h if prior_basis == "full_sample" else h, weighting)
        oth_cf_s = self.other_cf_seasonal(fit_h if prior_basis == "full_sample" else h, q, weighting)
        cpx = self.capex(h, weighting)
        out.update(duf_swing=duf_s, dfp_swing_memo=dfp_s, duf_balance=duf_b, dfp_balance_memo=dfp_b, other_cf_musd=oth_cf,
                   other_cf_seasonal_musd=oth_cf_s, capex_musd=cpx)
        for wc_tag, duf, oth in [("swing", duf_s, oth_cf), ("balance", duf_b, oth_cf), ("seasonal", duf_s, oth_cf_s)]:
            for e_tag in ["pit", "known"]:
                cfo = out[f"net_income_{e_tag}"] + da + sbc + duf + oth
                out[f"cfo_{wc_tag}_{e_tag}"] = cfo
                out[f"fcf_{wc_tag}_{e_tag}"] = cfo - cpx
                out[f"fcf_margin_{wc_tag}_{e_tag}"] = 100.0 * (cfo - cpx) / rev if rev else np.nan
        return out


# ----------------------------------------------------------------------------------------------- registry assembly
# (object, target, spec_id, column in the forecast dict, relative-or-additive residuals, n_params)
SPECS = [
    ("interest_income", "interest_income_musd", "rate_x_base", "interest_income_musd", True, 2),
    ("sbc", "sbc_musd", "yoy", "sbc_musd", True, 2),
    ("sbc", "sbc_pct_rev", "yoy", "sbc_pct_rev", False, 2),
    ("sbc", "sbc_musd", "yoy_last", "sbc_musd_yoy_last", True, 1),
    ("da", "da_musd", "mean4", "da_musd", True, 2),
    ("da", "da_musd", "last_value", "da_last_value", True, 1),
    ("tax", "tax_rate_pct", "guide_or_ttm", "tax_rate_pct", False, 2),
    ("tax", "tax_rate_pct", "ttm", "tax_rate_ttm", False, 2),
    ("share_count", "diluted_shares_m", "delta", "diluted_shares_m", True, 2),
    ("share_count", "diluted_shares_m", "structural", "diluted_shares_structural_m", True, 3),
    ("eps", "eps_diluted", "ebitda_pit", "eps_pit", False, 6),
    ("eps", "eps_diluted", "ebitda_known", "eps_known", False, 6),
    ("eps", "net_income_musd", "ebitda_pit", "net_income_pit", False, 6),
    ("eps", "net_income_musd", "ebitda_known", "net_income_known", False, 6),
    ("eps", "op_income_musd", "ebitda_pit", "op_income_pit", False, 6),
    ("eps", "op_income_musd", "ebitda_known", "op_income_known", False, 6),
    ("eps", "pretax_income_musd", "ebitda_pit", "pretax_pit", False, 6),
    ("eps", "pretax_income_musd", "ebitda_known", "pretax_known", False, 6),
    ("eps", "tax_provision_musd", "ebitda_pit", "tax_provision_pit", False, 6),
    ("eps", "tax_provision_musd", "ebitda_known", "tax_provision_known", False, 6),
    ("fcf", "fcf_musd", "swing_x_gbv", "fcf_swing_pit", False, 3),
    ("fcf", "fcf_musd", "swing_x_gbv_ebitda_known", "fcf_swing_known", False, 3),
    ("fcf", "fcf_musd", "balance_ratio", "fcf_balance_pit", False, 5),
    ("fcf", "fcf_musd", "swing_x_gbv_seasonal_other", "fcf_seasonal_pit", False, 3),
    ("fcf", "fcf_musd", "swing_x_gbv_seasonal_other_ebitda_known", "fcf_seasonal_known", False, 3),
    ("fcf", "cfo_musd", "swing_x_gbv_seasonal_other", "cfo_seasonal_pit", False, 3),
    ("fcf", "fcf_margin_pct", "swing_x_gbv_seasonal_other", "fcf_margin_seasonal_pit", False, 3),
    ("fcf", "cfo_musd", "swing_x_gbv", "cfo_swing_pit", False, 3),
    ("fcf", "cfo_musd", "balance_ratio", "cfo_balance_pit", False, 5),
    ("fcf", "fcf_margin_pct", "swing_x_gbv", "fcf_margin_swing_pit", False, 3),
    ("fcf", "fcf_margin_pct", "balance_ratio", "fcf_margin_balance_pit", False, 5),
    ("fcf", "capex_musd", "mean4", "capex_musd", True, 2),
]
FALLBACK_SD = {"eps_diluted": 0.30, "tax_rate_pct": 8.0, "sbc_pct_rev": 1.0, "fcf_margin_pct": 8.0}
FALLBACK_REL = 0.15
# quarters with a discrete tax / reserve item that no below-the-line model forecasts: excluded from the residual POOLS of the
# tax-dependent targets only (the points and errors stay scored; the bands are for ordinary quarters)
DISCRETE_QUARTERS = {"2023Q3": "valuation-allowance release -$2,695m", "2023Q4": "Italian lodging-tax reserve $931m in GAAP G&A"}
DISCRETE_TARGETS = {"eps_diluted", "net_income_musd", "pretax_income_musd", "tax_provision_musd", "tax_rate_pct", "op_income_musd"}


def attach_quantiles(reg: pd.DataFrame, errs: pd.DataFrame, T: pd.DataFrame) -> pd.DataFrame:
    """Gaussian quantiles from the walk-forward residual pool of the same object/target/spec/replay/horizon."""
    pdm = dict(zip(T["quarter"], T["print_date"]))
    errs = errs.copy()
    errs["target_print"] = errs["quarter"].map(pdm)
    out = []
    for r in reg.itertuples():
        h_pool = min(int(r.horizon_q), 2)
        e = errs[(errs["object"] == r.object) & (errs["target"] == r.target) & (errs["spec_id"] == r.spec_id)
                 & (errs["prior_basis"] == r.prior_basis) & (errs["horizon_q"] == h_pool)]
        if r.target in DISCRETE_TARGETS:
            e = e[~e["quarter"].isin(DISCRETE_QUARTERS)]
        if r.prior_basis == "PIT":
            e = e[e["target_print"].map(lambda d: pd.notna(d) and d <= r.vintage_date)].sort_values("quarter").iloc[-RESID_MAX_N:]
        vals = e["rel_err"] if r.relative else e["err"]
        vals = vals.dropna().to_numpy(dtype=float)
        note_extra = ""
        if len(vals) >= MIN_RESID:
            sd = float(np.sqrt(np.mean(vals ** 2)))
            kind = f"{'relative' if r.relative else 'additive'}{'_borrowed_h2' if r.horizon_q > 2 else ''} n={len(vals)} ({r.prior_basis})"
        else:
            sd = FALLBACK_REL if r.relative else FALLBACK_SD.get(r.target, 0.15 * abs(r.point) if r.point else 1.0)
            kind = f"{'relative' if r.relative else 'additive'}_fallback n={len(vals)}"
            note_extra = "_fallback"
        d = r._asdict()
        for k, z in ZQ.items():
            d[k] = r.point * (1.0 + z * sd) if r.relative else r.point + z * sd
        d["sd"] = r.point * sd if r.relative else sd
        d["notes"] = f"{r.notes}; sigma {kind}" + ("; pool ex 2023Q3/2023Q4 discrete items" if r.target in DISCRETE_TARGETS else "")
        out.append(d)
    return pd.DataFrame(out)


def build_registry(m: M7):
    vintages = list(GUIDE_DATES_ALL) + [TODAY]
    rows, raw = [], []
    live_path = load_live_path("base")
    for vd in vintages:
        q0 = Q.quarter_of_date(vd)
        is_live = vd in LIVE_VINTAGES
        H = 5 if is_live else 2
        for hz in range(0, H + 1):
            q = shift(q0, hz)
            for weighting in ["rw", "eq"]:
                for pb in ["PIT", "full_sample"]:
                    lp = live_path if (is_live and canon(q) >= "2026Q3") else None
                    f = m.forecast(vd, q, weighting, pb, live_path=lp)
                    f["horizon_q"] = hz
                    raw.append(f)
                    wins = windows_for(vd, q)
                    for (obj, tgt, spec, col, rel, npar) in SPECS:
                        point = f.get(col, np.nan)
                        if not np.isfinite(point):
                            continue
                        sid = f"{spec}|{weighting}"
                        base = dict(method=METHOD, object=obj, target=tgt, quarter=canon(q), vintage_date=vd, horizon_q=hz,
                                    point=point, q50=point, prior_basis=pb, n_params=npar, n_train=f["n_train"],
                                    knowable_from=vd, spec_id=sid, relative=rel,
                                    notes=_note(obj, spec, f))
                        for win in wins:
                            rows.append(dict(base, window=win))
    raw = pd.DataFrame(raw)
    raw.to_csv(OUT / "M7_forecast_grid_all_vintages.csv", index=False)
    reg = pd.DataFrame(rows)
    # realised errors for every (row, quarter) with an actual, over ALL vintages (the pools)
    act = m.T.set_index("quarter")
    allrows = []
    for r in raw.itertuples():
        f = r._asdict()
        for (obj, tgt, spec, col, rel, npar) in SPECS:
            point = f.get(col, np.nan)
            a = act.at[canon(r.quarter), tgt] if canon(r.quarter) in act.index else np.nan
            if not (np.isfinite(point) and pd.notna(a)):
                continue
            allrows.append(dict(object=obj, target=tgt, spec_id=f"{spec}|{r.weighting}", prior_basis=r.prior_basis,
                                horizon_q=r.horizon_q, quarter=canon(r.quarter), vintage_date=r.vintage_date,
                                point=point, actual=float(a), err=point - float(a),
                                rel_err=(point - float(a)) / float(a) if float(a) != 0 else np.nan))
    errs = pd.DataFrame(allrows)
    errs.to_csv(OUT / "M7_errors_all_vintages.csv", index=False)
    reg = attach_quantiles(reg, errs, m.T)
    reg["actual"] = [act.at[q, t] if q in act.index else np.nan for q, t in zip(reg["quarter"], reg["target"])]
    reg.to_csv(OUT / "M7_registry_preview.csv", index=False)
    cols = ["method", "object", "target", "quarter", "vintage_date", "horizon_q", "point", "q50", "window", "prior_basis",
            "n_params", "n_train"] + QCOLS[:3] + QCOLS[4:] + ["sd", "knowable_from", "spec_id", "notes"]
    for obj, g in reg.groupby("object"):
        register(g[cols].reset_index(drop=True), quiet=False)
    return reg, errs, raw


def _note(obj, spec, f):
    if obj == "interest_income":
        return f"beta {f['beta']:.3f} (n {f['beta_n']}); tbill_hat {f['tbill_hat']:.2f}; avg base {f['avg_base']:.0f}"
    if obj == "sbc":
        return (f"y/y growth {100 * f['sbc_growth']:.1f}% on SBC[q-4]" if spec != "yoy_last"
                else f"last y/y growth {100 * f['sbc_growth_last']:.1f}% on SBC[q-4]")
    if obj == "da":
        return f"D&A rule {spec}"
    if obj == "tax":
        return f"ETR {f['tax_rate_pct']:.1f} src {f['tax_rate_src']}" if spec == "guide_or_ttm" else f"ETR ttm {f['tax_rate_ttm']:.1f}"
    if obj == "share_count":
        return (f"delta {f['share_delta']:.2f} m/q" if spec == "delta"
                else f"buyback {f['st_buyback_musd_q']:.0f}/q at price {f['st_price']:.0f}, issuance {f['st_issuance_m']:.2f} m/q")
    if obj == "eps":
        return (f"EBITDA {f['ebitda_pit']:.0f} from {f['ebitda_pit_src']}" if spec == "ebitda_pit" else "EBITDA actual (below-line error only)") + \
            f"; ETR {f['tax_rate_pct']:.1f}; IE {f['interest_expense_musd']:.0f}; other {f['other_income_musd']:.0f}; shares {f['diluted_shares_m']:.0f}"
    if obj == "fcf":
        return f"NI from {'EBITDA actual' if 'known' in spec else f['ebitda_pit_src']}; wc {'balance ratio' if 'balance' in spec else 'swing x GBV'}; other_cf {(f['other_cf_seasonal_musd'] if 'seasonal' in spec else f['other_cf_musd']):.0f}{' (seasonal)' if 'seasonal' in spec else ''}; capex {f['capex_musd']:.0f}; rev leg {f['revenue_leg_kind']}"
    return spec


# ----------------------------------------------------------------------------------------------- LIVE path and EBITDA sources

def load_live_path(scenario: str) -> dict:
    w = pd.read_csv(MB / "06_fy27_path_v2" / "06_revenue_path_wide.csv")
    v2b = MB / "06_fy27_path_v2" / "06_revenue_path_3q26_4q27_v2b.csv"
    src = "06_revenue_path_wide.csv"
    if v2b.exists():
        src = "06_revenue_path_3q26_4q27_v2b.csv (checker) for 3Q26-4Q27, wide file for 1Q28+"
        b = pd.read_csv(v2b)
        b = b[b["line"].isin(["revenue_musd", "gbv_busd"])].pivot_table(index=["quarter", "scenario"], columns="line", values="value").reset_index()
        w = w[~w["quarter"].isin(b["quarter"].unique())]
        w = pd.concat([w, b], ignore_index=True)
    x = w[w["scenario"] == scenario].copy()
    if scenario != "base":   # FY28 quarters exist for base only; use base for 2028 in the other scenarios
        x = pd.concat([x, w[(w["scenario"] == "base") & (w["quarter"].str.endswith("28"))]], ignore_index=True)
    x["q"] = x["quarter"].map(canon)
    return dict(rev=dict(zip(x["q"], x["revenue_musd"])), gbv=dict(zip(x["q"], x["gbv_busd"] * 1000.0)), source=src, scenario=scenario)


def live_ebitda_sources(m: M7) -> dict:
    """adj EBITDA $M by quarter 3Q26-4Q27 from: the M1 driver-lines LIVE base if registered, else M2 margin-ts, else the
    harness seasonal_naive_drift; plus guide_implied and the LSEG Street as comparison sources."""
    out = {}
    for meth in ["driver-lines", "margin-ts"]:
        r = load_registry(meth)
        if r is None or len(r) == 0:
            continue
        r = r[(r["target"] == "adj_ebitda_musd") & (r["window"] == "LIVE") & (r["prior_basis"] == "PIT")]
        r["vintage_date"] = pd.to_datetime(r["vintage_date"]).dt.date
        r = r[r["vintage_date"] == r["vintage_date"].max()]
        if len(r) == 0:
            continue
        spec = sorted(r["spec_id"].unique(), key=lambda s: (("rw" not in str(s)), str(s)))[0]
        obj = sorted(r["object"].unique())[0]
        rr = r[(r["spec_id"] == spec) & (r["object"] == obj)]
        out[f"{meth}"] = dict(values=dict(zip(rr["quarter"], rr["point"])), label=f"{meth}/{obj} spec {spec} vintage {rr['vintage_date'].iloc[0]}")
        break
    b = pd.read_csv(MB / "registry" / "baselines-margin__seasonal_naive_drift.csv")
    b = b[(b["target"] == "adj_ebitda_musd") & (b["window"] == "LIVE") & (b["prior_basis"] == "PIT") & (b["vintage_date"] == str(TODAY))]
    out["seasonal_naive_drift"] = dict(values=dict(zip(b["quarter"], b["point"])), label="harness baseline seasonal_naive_drift at 2026-09-11 (fallback, labelled)")
    g = pd.read_csv(MB / "registry" / "baselines-margin__guide_implied.csv")
    g = g[(g["target"] == "adj_ebitda_musd") & (g["window"] == "LIVE") & (g["prior_basis"] == "PIT") & (g["vintage_date"] == str(TODAY))]
    out["guide_implied"] = dict(values=dict(zip(g["quarter"], g["point"])), label="harness baseline guide_implied (FY26 floor 35.5%) at 2026-09-11; 3Q26/4Q26 only")
    c = pd.read_csv(MB / "03_consensus_pit" / "03_current_consensus.csv")
    c = c[c["vendor"] == "LSEG"]
    sv = {canon(p): v for p, v in zip(c["period"], c["ebitda_mean"]) if str(p)[0].isdigit()}
    out["street"] = dict(values=sv, label="LSEG TR.EBITDAMean, row 2026-09-11 (comparison only; 3Q26/4Q26)")
    return out


def load_street_current() -> pd.DataFrame:
    c = pd.read_csv(MB / "03_consensus_pit" / "03_current_consensus.csv")
    c = c[c["vendor"] == "LSEG"].copy()
    c["period"] = c["period"].astype(str)
    return c.set_index("period")


def build_live(m: M7, reg: pd.DataFrame):
    srcs = live_ebitda_sources(m)
    base_key = next(k for k in ["driver-lines", "margin-ts", "seasonal_naive_drift"] if k in srcs)
    m.log.append(f"LIVE adj EBITDA base source: {srcs[base_key]['label']}")
    street = load_street_current()
    quarters = [shift("2026Q3", k) for k in range(0, 6)]
    q28 = [shift("2028Q1", k) for k in range(0, 4)]
    rows = []
    scen_list = [
        ("base", dict()), ("bear", dict()), ("bull", dict()),
        ("rates_+100bp", dict(rate_shift_bp=100.0)), ("rates_-100bp", dict(rate_shift_bp=-100.0)),
        ("no_buyback_renewal", dict()), ("etr_16", dict(etr_override=16.0)), ("etr_19", dict(etr_override=19.0)),
    ]
    for src_key in [base_key, "guide_implied", "street"]:
        for scen, kw in scen_list:
            if src_key != base_key and scen != "base":
                continue
            path = load_live_path(scen if scen in ("base", "bear", "bull") else "base")
            ev = dict(srcs[src_key]["values"])
            # FY28 quarters: FY27 margin of the source x FY28 revenue (flat margin); also fills any missing 2027 quarter for the comparison sources
            fy27_rev = sum(path["rev"][q] for q in quarters[2:])
            fy27_e = sum(ev.get(q, np.nan) for q in quarters[2:])
            marg27 = fy27_e / fy27_rev if np.isfinite(fy27_e) else np.nan
            for q in q28:
                ev[q] = marg27 * path["rev"][q] if np.isfinite(marg27) else np.nan
            for q in quarters + q28:
                e = ev.get(q, np.nan)
                if not np.isfinite(e):
                    continue
                kw2 = dict(kw)
                if scen == "no_buyback_renewal" and q >= "2027Q2":
                    kw2["buyback_override"] = 0.0
                f = m.forecast(TODAY, q, "rw", "PIT", live_path=path, ebitda_override=e, ebitda_label=src_key, **kw2)
                f = _live_row(f, q, src_key, scen, path)
                rows.append(f)
    live = pd.DataFrame(rows)
    # annual aggregation FY26-28
    act = m.P
    ann = []
    for (src_key, scen), g in live.groupby(["ebitda_source", "scenario"]):
        g = g.set_index("quarter")
        for year in [2026, 2027, 2028]:
            qs = [f"{year}Q{k}" for k in range(1, 5)]
            parts = []
            for q in qs:
                if q in act.index and pd.notna(act.at[q, "adj_ebitda_reported"]) and year == 2026:
                    a = act.loc[q]
                    parts.append(dict(revenue_musd=a["revenue"], adj_ebitda_musd=a["adj_ebitda_reported"], da_musd=a["da"], sbc_musd=a["sbc_total_is"],
                                      op_income_musd=a["op_income"], interest_income_musd=a["interest_income"], interest_expense_musd=a["interest_expense"],
                                      other_income_musd=a["other_income_expense"], pretax_income_musd=a["pretax_income"], tax_provision_musd=a["tax_provision"],
                                      net_income_musd=a["net_income"], diluted_shares_m=a["shares_diluted_m"], cfo_musd=a["cfo"], capex_musd=a["capex"], fcf_musd=a["fcf_reported"],
                                      fcf_seasonal_other_musd=a["fcf_reported"], eps_diluted=a["eps_diluted"], is_actual=1))
                elif q in g.index:
                    parts.append(dict(g.loc[q].to_dict(), is_actual=0))
            if len(parts) < 4:
                continue
            s = pd.DataFrame(parts)
            tot = s.drop(columns=["is_actual"]).select_dtypes("number").sum(numeric_only=True)
            row = dict(period=f"FY{year}", ebitda_source=src_key, scenario=scen, n_actual_quarters=int(s["is_actual"].sum()))
            for k in ["revenue_musd", "adj_ebitda_musd", "da_musd", "sbc_musd", "op_income_musd", "interest_income_musd", "interest_expense_musd",
                      "other_income_musd", "pretax_income_musd", "tax_provision_musd", "net_income_musd", "cfo_musd", "capex_musd", "fcf_musd",
                      "fcf_seasonal_other_musd"]:
                row[k] = float(tot[k]) if k in tot else np.nan
            row["diluted_shares_m"] = float(s["diluted_shares_m"].mean())
            row["adj_ebitda_margin_pct"] = 100 * row["adj_ebitda_musd"] / row["revenue_musd"]
            row["op_margin_pct"] = 100 * row["op_income_musd"] / row["revenue_musd"]
            row["tax_rate_pct"] = 100 * row["tax_provision_musd"] / row["pretax_income_musd"]
            row["eps_diluted"] = row["net_income_musd"] / row["diluted_shares_m"]
            row["eps_sum_of_quarters"] = float(s["eps_diluted"].sum()) if "eps_diluted" in s else np.nan
            row["fcf_margin_pct"] = 100 * row["fcf_musd"] / row["revenue_musd"]
            row["fcf_margin_seasonal_other_pct"] = 100 * row["fcf_seasonal_other_musd"] / row["revenue_musd"]
            row["sbc_pct_rev"] = 100 * row["sbc_musd"] / row["revenue_musd"]
            p = f"FY{str(year)[2:]}"
            if p in street.index:
                sr = street.loc[p]
                row.update(street_ebitda_musd=sr["ebitda_mean"], street_revenue_musd=sr["revenue_mean"], street_eps=sr["eps_mean"],
                           street_net_income_musd=sr["netprofit_mean"], street_fcf_musd=sr["fcf_mean"], street_ebit_musd=sr["ebit_mean"],
                           street_pretax_musd=sr["pretaxprofit_mean"], street_as_of="2026-09-11")
            ann.append(row)
    ann = pd.DataFrame(ann)
    live.to_csv(OUT / "M7_live_waterfall_quarterly.csv", index=False)
    ann.to_csv(OUT / "M7_below_ebitda_annual_forecasts.csv", index=False)
    return live, ann, srcs, base_key


def _live_row(f: dict, q: str, src_key: str, scen: str, path: dict) -> dict:
    street = load_street_current()
    e = f["ebitda_pit"]
    r = dict(quarter=q, ebitda_source=src_key, scenario=scen, revenue_musd=f["revenue_leg"], adj_ebitda_musd=e,
             adj_ebitda_margin_pct=100 * e / f["revenue_leg"], da_musd=f["da_musd"], sbc_musd=f["sbc_musd"], sbc_pct_rev=f["sbc_pct_rev"],
             op_income_musd=f["op_income_pit"], op_margin_pct=100 * f["op_income_pit"] / f["revenue_leg"],
             interest_income_musd=f["interest_income_musd"], tbill_hat=f["tbill_hat"], avg_base_musd=f["avg_base"], beta=f["beta"],
             interest_expense_musd=f["interest_expense_musd"], other_income_musd=f["other_income_musd"],
             pretax_income_musd=f["pretax_pit"], tax_rate_pct=f["tax_rate_pct"], tax_rate_src=f["tax_rate_src"], tax_provision_musd=f["tax_provision_pit"],
             net_income_musd=f["net_income_pit"], diluted_shares_m=f["diluted_shares_structural_m"], diluted_shares_delta_rule_m=f["diluted_shares_m"],
             buyback_musd_q=f["st_buyback_musd_q"], price_used=f["st_price"], issuance_m_q=f["st_issuance_m"],
             eps_diluted=f["net_income_pit"] / f["diluted_shares_structural_m"], eps_delta_rule=f["eps_pit"],
             duf_musd=f["duf_swing"], dfp_memo_musd=f["dfp_swing_memo"], other_cf_musd=f["other_cf_musd"], other_cf_seasonal_musd=f["other_cf_seasonal_musd"],
             cfo_musd=f["cfo_swing_pit"], capex_musd=f["capex_musd"], fcf_musd=f["fcf_swing_pit"], fcf_margin_pct=f["fcf_margin_swing_pit"],
             cfo_seasonal_other_musd=f["cfo_seasonal_pit"], fcf_seasonal_other_musd=f["fcf_seasonal_pit"], fcf_margin_seasonal_other_pct=f["fcf_margin_seasonal_pit"],
             fcf_balance_ratio_musd=f["fcf_balance_pit"], revenue_path_source=path["source"])
    p = f"{q[-1]}Q{q[2:4]}"
    if p in street.index:
        s = street.loc[p]
        r.update(street_ebitda_musd=s["ebitda_mean"], street_revenue_musd=s["revenue_mean"], street_eps=s["eps_mean"], street_net_income_musd=s["netprofit_mean"],
                 street_fcf_musd=s["fcf_mean"], street_ebit_musd=s["ebit_mean"], street_pretax_musd=s["pretaxprofit_mean"], street_capex_musd=s["capex_mean"], street_as_of="2026-09-11")
    return r


# ----------------------------------------------------------------------------------------------- tests and tables

def eps_decomposition(raw: pd.DataFrame, m: M7) -> pd.DataFrame:
    """Last 8 prints (3Q24-2Q26), h=0 at the guide date: EPS error with the PIT EBITDA input vs with the actual EBITDA, vs pre-guide Street."""
    cons = pd.read_csv(MB / "03_consensus_pit" / "03_consensus_at_dates.csv")
    cons = cons[(cons["target_role"] == "guided_q_pre_guide") & (cons["found"] == True)]  # noqa: E712
    cons["q"] = cons["target_period"].map(canon)
    cons["date"] = pd.to_datetime(cons["date"]).dt.date
    act = m.T.set_index("quarter")
    rows = []
    g = raw[(raw["horizon_q"] == 0) & (raw["weighting"] == "rw") & (raw["prior_basis"] == "PIT")]
    for r in g.itertuples():
        q = canon(r.quarter)
        if q not in act.index or pd.isna(act.at[q, "eps_diluted"]):
            continue
        a = float(act.at[q, "eps_diluted"])
        c = cons[(cons["q"] == q) & (cons["date"] == r.vintage_date)]
        s_eps = float(c["eps_mean"].iloc[0]) if len(c) else np.nan
        e_act = float(act.at[q, "adj_ebitda_musd"])
        rows.append(dict(quarter=q, vintage_date=r.vintage_date, eps_actual=a, eps_hat_ebitda_pit=r.eps_pit, eps_hat_ebitda_known=r.eps_known,
                         street_eps_pre_guide=s_eps, ebitda_pit=r.ebitda_pit, ebitda_pit_src=r.ebitda_pit_src, ebitda_actual=e_act,
                         err_pit=r.eps_pit - a, err_known=r.eps_known - a, err_street=s_eps - a,
                         err_from_ebitda=(r.ebitda_pit - e_act) * (1 - r.tax_rate_pct / 100) / r.diluted_shares_m,
                         err_below_line=r.eps_known - a,
                         ni_err_from_sbc=-(r.sbc_musd - float(m.P.at[q, "sbc_total_is"])) * (1 - r.tax_rate_pct / 100) / r.diluted_shares_m,
                         ni_err_from_ii=(r.interest_income_musd - float(m.P.at[q, "interest_income"])) * (1 - r.tax_rate_pct / 100) / r.diluted_shares_m,
                         ni_err_from_tax=-(r.tax_rate_pct - float(m.P.at[q, "effective_tax_rate_pct"])) / 100 * float(m.P.at[q, "pretax_income"]) / r.diluted_shares_m,
                         ni_err_from_shares=float(m.P.at[q, "net_income"]) * (1 / r.diluted_shares_m - 1 / float(m.P.at[q, "shares_diluted_m"]))))
    d = pd.DataFrame(rows).sort_values("quarter")
    d.to_csv(OUT / "M7_eps_error_decomposition.csv", index=False)
    return d


def fy_fcf_test(raw: pd.DataFrame, m: M7) -> pd.DataFrame:
    """FY FCF from the February vintage (h=0..3 sum), vs the seasonal naive (prior FY actual) and the actual."""
    ann = m.P.groupby(m.P.index.str[:4])["fcf_reported"].agg(["sum", "count"])
    rows = []
    for vd in GUIDE_DATES_ALL:
        if vd.month != 2:
            continue
        year = vd.year
        g = raw[(raw["vintage_date"] == vd) & (raw["weighting"] == "rw") & (raw["prior_basis"] == "PIT") & (raw["quarter"].str[:4] == str(year))]
        if len(g) < 4:
            # extend to h=3 for the test (the grid holds h<=2 at guide dates): compute directly
            f3 = m.forecast(vd, f"{year}Q4", "rw", "PIT"); f3["horizon_q"] = 3
            g = pd.concat([g, pd.DataFrame([f3])], ignore_index=True)
        fc_swing = float(g["fcf_swing_pit"].sum(skipna=False)); fc_bal = float(g["fcf_balance_pit"].sum(skipna=False))
        fc_known = float(g["fcf_swing_known"].sum(skipna=False)); fc_seas = float(g["fcf_seasonal_pit"].sum(skipna=False))
        act = float(ann.at[str(year), "sum"]) if (str(year) in ann.index and ann.at[str(year), "count"] == 4) else np.nan
        naive = float(ann.at[str(year - 1), "sum"]) if str(year - 1) in ann.index else np.nan
        rows.append(dict(fy=year, vintage_date=vd, fcf_hat_swing=fc_swing, fcf_hat_seasonal_other=fc_seas, fcf_hat_balance=fc_bal,
                         fcf_hat_swing_ebitda_known=fc_known, seasonal_naive=naive, actual=act, err_swing=fc_swing - act, err_seasonal=fc_seas - act,
                         err_balance=fc_bal - act, err_known=fc_known - act, err_naive=naive - act,
                         swing_beats_naive=abs(fc_swing - act) < abs(naive - act) if np.isfinite(act) else np.nan,
                         seasonal_beats_naive=abs(fc_seas - act) < abs(naive - act) if np.isfinite(act) else np.nan,
                         ebitda_pit_src=";".join(sorted(set(g["ebitda_pit_src"].astype(str))))))
    d = pd.DataFrame(rows)
    d.to_csv(OUT / "M7_fy_fcf_test.csv", index=False)
    return d


def parameter_sheet(m: M7, live: pd.DataFrame, base_key: str, srcs: dict) -> pd.DataFrame:
    b = live[(live["ebitda_source"] == base_key) & (live["scenario"] == "base")].set_index("quarter")
    f = m.forecast(TODAY, "2026Q3", "rw", "PIT", live_path=load_live_path("base"))
    p = m.P
    rows = [
        ("interest_income_beta", f["beta"], "ratio of realised yield to 3m T-bill", f"recency-weighted mean of the last {f['beta_n']} quarters with DTB3 >= 0.5% (WS02 panel, FRED DTB3); WS04 equal-weight 0.86"),
        ("interest_income_rule", "beta x DTB3 x avg(cash + STI + funds held)/4", "USD m per quarter", "WS04 04_interest_income_yield_diagnostic.csv; this note"),
        ("tbill_3m_spot_2026-09-10", m.tbill.at(TODAY), "% (spot held constant beyond the vintage)", "FRED DTB3, raw file data/raw/margin_build/M7_below_ebitda/fred_DTB3.csv"),
        ("tbill_3m_3q26_hat", f["tbill_hat"], "% quarter average (realised to 10 Sep + spot)", "same"),
        ("ust_1y_spot_2026-09-10", m.dgs1.at(TODAY), "% (market-implied 12m path proxy, sensitivity only)", "FRED DGS1"),
        ("cash_plus_sti_2q26", float(p.at["2026Q2", "cash_and_equivalents"] + p.at["2026Q2", "short_term_investments"]), "USD m, held flat", "WS02 panel 2Q26"),
        ("funds_held_2q26", float(p.at["2026Q2", "funds_held_on_behalf"]), "USD m; forward = same quarter last year x (1 + GBV y/y from the adopted path)", "WS02 panel; WS06 path"),
        ("interest_income_rate_sensitivity", "+/-100bp = +/- ~$55m per quarter on a ~$22bn base", "USD m", "rule arithmetic (0.86 x 1% x 22,000/4 = 47; with base growth ~55)"),
        ("sbc_yoy_growth", f["sbc_growth"], "fraction, applied to SBC[q-4]", "recency-weighted mean of the last 4 y/y rates (1Q26 +14.5%, 2Q26 +14.9%, 4Q25 +11.7%, 3Q25 +10.2%; WS02 sbc_total_is)"),
        ("sbc_by_line_shares_ttm", json.dumps({k: round(float(p[f"sbc_{k}"].iloc[-4:].sum() / p["sbc_total_is"].iloc[-4:].sum()), 3) for k in ["ops", "pd", "sm", "ga"]}), "share of total SBC, trailing 4 quarters", "WS02 sbc_ops/pd/sm/ga"),
        ("da_musd_q", f["da_musd"], "USD m per quarter (recency-weighted last-4 mean)", "WS02 da; FY2025 D&A $91m, capex $33m (10-K)"),
        ("interest_expense_musd_q", LIVE_IE_MUSD, "USD m per quarter, 3Q26-4Q28", "2Q26 10-Q: $37m printed; $2.5bn notes 4.40/4.65/5.25% = $119m/yr coupon + issuance-cost amortisation + swap carry ($1.7bn swapped to SOFR; +/-100bp = +/-$17m/yr)"),
        ("other_income_musd_q", f["other_income_musd"], "USD m per quarter (recency-weighted mean of last 8)", "WS02 other_income_expense (FX and other, excludes interest expense)"),
        ("other_addbacks_expected", 0.0, "USD m (lodging-tax reserves, acquisition marks, IPO settlement)", "expected value 0; FY2025 realised $83m in 4Q25 (WS02)"),
        ("etr_fy26", LIVE_ETR[2026], "% (1H26 printed 17.1%)", "WS05 S157 'high teens' (1Q26 letter, 7 May 2026)"),
        ("etr_fy27_fy28", LIVE_ETR[2027], "%", "WS05 S148 long-term mid-to-high teens (OBBBA), 4Q25 letter; range 16-19"),
        ("buyback_musd_q", f["st_buyback_musd_q"], "USD m per quarter (trailing-4 mean: 3Q25 877, 4Q25 1,095, 1Q26 1,088, 2Q26 1,051)", "WS02 buybacks_cash; 2Q26 10-Q: $3.4bn authorisation left at 30 Jun 2026 -> exhausted ~1Q27 at this pace; base assumes renewal (Aug 2022, Feb 2024, Aug 2025 all renewed before exhaustion)"),
        ("share_price_used", f["st_price"], "USD (last close <= vintage in data/processed/abnb_daily_close.csv, 4 Sep 2026)", "abnb_daily_close.csv"),
        ("award_issuance_m_q", f["st_issuance_m"], "m shares per quarter (net RSU/option issuance implied by the diluted count and buybacks)", "WS02 shares_diluted_m, buybacks_cash, quarter-average close"),
        ("diluted_shares_delta_m_q", f["st_delta"], "m per quarter = -buyback/price + issuance", "this note"),
        ("diluted_shares_2q26", float(p.at["2026Q2", "shares_diluted_m"]), "m weighted-average diluted (basic 592; A+B outstanding 589.6m at 15 Jul 2026; 9.2m Class H excluded)", "2Q26 10-Q cover and EPS note"),
        ("wc_rule", "change in unearned fees and in funds payable = same quarter last year x (1 + GBV y/y from the path)", "USD m", "this note (0 fitted parameters)"),
        ("other_cf_musd_q", f["other_cf_musd"], "USD m per quarter (recency-weighted mean of last 8 residuals: CFO - NI - D&A - SBC - dUF; funds payable nets against funds receivable)", "WS02 cash-flow lines"),
        ("other_cf_seasonal_3q26", f["other_cf_seasonal_musd"], "USD m (same-quarter residual, recency-weighted mean of the last 3 years; variant)", "WS02 cash-flow lines"),
        ("capex_musd_q", f["capex_musd"], "USD m per quarter (recency-weighted last-4 mean)", "WS02 capex"),
        ("adj_ebitda_source_live", srcs[base_key]["label"], "USD m by quarter", "registry"),
        ("fy28_ebitda_rule", FY28_MARGIN_NOTE, "", "this note"),
        ("revenue_gbv_path", load_live_path("base")["source"], "3Q26/4Q26 bridge v3, 1Q27-4Q27 WS06 v2, FY28 WS06 base", "WS06"),
    ]
    d = pd.DataFrame(rows, columns=["name", "value", "unit", "source"])
    d.to_csv(OUT / "M7_parameter_sheet.csv", index=False)
    return d


def scoreboard_rows() -> pd.DataFrame:
    import subprocess
    subprocess.run([sys.executable, str(REPO / "analysis" / "src" / "margin_build" / "10_harness_margin" / "score.py")], check=True, cwd=str(REPO))
    s = pd.read_csv(MB / "10_harness_margin" / "scoreboard_margin.csv")
    s = s[s["method"] == METHOD]
    s.to_csv(OUT / "M7_scoreboard_rows.csv", index=False)
    return s


def main():
    m = M7()
    print("M7 below-EBITDA: building the PIT grid ...")
    reg, errs, raw = build_registry(m)
    print(f"registered {len(reg)} rows across {reg['object'].nunique()} objects")
    dec = eps_decomposition(raw, m)
    fyt = fy_fcf_test(raw, m)
    live, ann, srcs, base_key = build_live(m, reg)
    ps = parameter_sheet(m, live, base_key, srcs)
    sb = scoreboard_rows()
    # interest-income diagnostic table (fit history)
    ii = []
    for q in m.full.index:
        qm1 = shift(q, -1)
        if qm1 not in m.full.index:
            continue
        r = m.tbill.quarter_mean(q)
        avgb = 0.5 * (m.full.at[q, "earning_base"] + m.full.at[qm1, "earning_base"])
        ii.append(dict(quarter=q, interest_income=m.full.at[q, "interest_income"], tbill_qmean=r, avg_base=avgb,
                       implied_yield_pct=100 * 4 * m.full.at[q, "interest_income"] / avgb if avgb else np.nan,
                       ratio_to_tbill=(4 * m.full.at[q, "interest_income"] / avgb) / (r / 100) if (avgb and r and r >= 0.5) else np.nan))
    pd.DataFrame(ii).to_csv(OUT / "M7_interest_income_fit_history.csv", index=False)
    _, resid = m.other_cf(m.full, "rw")
    resid.rename("other_cf_residual").to_csv(OUT / "M7_cfo_other_residual_history.csv")
    (OUT / "M7_build_log.txt").write_text("\n".join(m.log + [
        f"rows registered: {len(reg)}", f"objects: {sorted(reg['object'].unique())}",
        f"EPS decomposition rows: {len(dec)}", f"FY FCF test rows: {len(fyt)}", f"LIVE rows: {len(live)}; annual rows: {len(ann)}",
        f"scoreboard rows for {METHOD}: {len(sb)}", f"run at {dt.datetime.now().isoformat(timespec='seconds')}"]), encoding="utf-8")
    print("\n".join(m.log))
    try:
        import subprocess
        subprocess.run([sys.executable, str(HERE / "figures.py")], check=True, cwd=str(REPO))
    except Exception as ex:      # figures are non-fatal
        print("figures failed:", ex)
    print("done")


if __name__ == "__main__":
    main()
