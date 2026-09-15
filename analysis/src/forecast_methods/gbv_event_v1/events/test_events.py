"""Boundary tests for temporal eligibility, simple-return legs and proxy definitions."""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

spec = importlib.util.spec_from_file_location("ge_event_run", Path(__file__).with_name("run.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def prices():
    rows=[]
    for ticker, values in (("ABNB",[(100,100),(110,121),(90,91)]),("QQQ",[(200,200),(190,199.5),(202,200)])):
        for d,(op,cl) in zip(("2026-01-09","2026-01-12","2026-01-13"),values):
            rows.append(dict(date=pd.Timestamp(d),ticker=ticker,open=op,close=cl,high=max(op,cl)+1,low=min(op,cl)-1))
    return pd.DataFrame(rows)


def test_exact_compounding_per_security_not_excess():
    result=mod.price_legs(prices(),"2026-01-09")
    assert result["entry_date"]==pd.Timestamp("2026-01-12")
    assert result["gap_excess_pct"]==pytest.approx(15)
    assert result["session_excess_pct"]==pytest.approx(5)
    assert result["cc_excess_pct"]==pytest.approx(21.25)
    assert result["cross_term_excess_pp"]==pytest.approx(1.25)
    assert result["compounding_identity_error_pp"]==pytest.approx(0,abs=1e-12)
    assert result["cc_excess_pct"]!=pytest.approx(100*((1+.15)*(1+.05)-1))
    assert np.isnan(result["open_5d_excess_pct"])


def test_mismatched_benchmark_session_refused():
    p=prices()
    p=p.loc[~(p.ticker.eq("QQQ") & p.date.eq("2026-01-12"))]
    with pytest.raises(ValueError,match="do not match"):
        mod.price_legs(p,"2026-01-09")


def register():
    return pd.DataFrame([dict(register_id="PG-2026Q4-revenue",period="2026Q4",role="pre_guide",metric="revenue",
                             value=3000,as_of=pd.Timestamp("2026-11-05"),as_of_timestamp="2026-11-05",pit_usable=True,vendor_attributed=True,vendor="LSEG"),
                         dict(register_id="PIT-2026Q4-revenue-DHPNP",period="2026Q4",role="pit_history",metric="revenue",
                             value=2990,as_of=pd.Timestamp("2026-11-05"),as_of_timestamp="2026-11-05",pit_usable=True,vendor_attributed=True,
                             vendor="DoltHub post-no-preference/earnings")])


def test_no_future_consensus_and_no_mirror_fallback():
    r=register()
    assert mod.select_primary(r,"2026Q4","pre_guide","2026-11-04")[0] is None
    assert mod.select_primary(r,"2026Q4","pre_guide","2026-11-05")[0].vendor=="LSEG"
    r.loc[0,"pit_usable"]=False
    assert mod.select_primary(r,"2026Q4","pre_guide","2026-11-06")[0] is None
    assert mod.select_dolthub(r,"2026Q4","2026-11-05") is None
    assert mod.select_dolthub(r,"2026Q4","2026-11-06").value==2990


def test_ambiguous_original_vendor_refused_even_flag_true():
    r=register()
    r.loc[0,"vendor"]="vendor_not_recorded"
    assert mod.select_primary(r,"2026Q4","pre_guide","2026-11-06")[0] is None


@pytest.mark.parametrize("stamp,admissible",[("2026-11-05T20:59:59Z",True),
    ("2026-11-05T21:00:00Z",False),("2026-11-05T21:01:00Z",False),
    ("2026-11-05 10:00:00",False),("2026-11-05T10:00:00-05:00",True)])
def test_explicit_timestamp_does_not_inherit_date_only_exception(stamp,admissible):
    r=register()
    r.loc[0,"as_of_timestamp"]=stamp
    assert (mod.select_primary(r,"2026Q4","pre_guide","2026-11-05")[0] is not None)==admissible


def test_cushion_excludes_same_event_print_and_future_poison():
    h=pd.DataFrame(dict(quarter=["a","b","c","d","e"],guide_mid=[100]*5,actual=[101,102,103,99999,99999],
                        actual_publication=pd.to_datetime(["2025-01-01","2025-04-01","2025-07-01","2025-10-01","2026-01-01"])))
    cushion,train=mod.preevent_cushion(h,"2025-10-01")
    assert cushion==pytest.approx(.02)
    assert list(train.quarter)==["a","b","c"]
    assert np.isnan(mod.preevent_cushion(h,"2025-07-01")[0])


def test_guide_comparison_is_not_revenue_comparison():
    raw,adjusted,implied=mod.guide_surprises(100,102,.02)
    assert raw==pytest.approx(-1.9607843137254901)
    assert adjusted==pytest.approx(0)
    assert implied==pytest.approx(100)
    raw,adjusted,implied=mod.guide_surprises(100,102,np.nan)
    assert np.isfinite(raw) and np.isnan(adjusted) and np.isnan(implied)


def test_holm_and_degenerate_slopes():
    assert mod.holm([.04,.01,.50]).tolist()==pytest.approx([.08,.03,.50])
    assert mod.fit_slope([1,1,1,1],[1,2,3,4])["status"]=="insufficient_or_degenerate"
