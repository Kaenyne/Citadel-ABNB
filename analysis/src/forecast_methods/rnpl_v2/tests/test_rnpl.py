import importlib.util
from pathlib import Path

import numpy as np
import pytest

spec=importlib.util.spec_from_file_location("rnpl_run",Path(__file__).resolve().parents[1]/"run.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_gbv_share_inverse():
    for g in (0,.1,.22,.23,1):
        for a in (1,1.25,1.5):
            nights=g/(a*(1-g)+g)
            assert m.gbv_share(100*nights,a) == pytest.approx(g)


@pytest.mark.parametrize("share,pp",[(-.1,2),(1.1,2),(.2,-1),(.2,101),(np.nan,4)])
def test_invalid_leakage(share,pp):
    with pytest.raises(ValueError): m.leakage(share,pp)


def test_zero_leakage_and_fraction_units():
    assert m.leakage(.22,0)==0
    assert m.leakage(.22,4)==pytest.approx(.0088)


def test_joint_diagnostic_is_not_identification():
    first=m.rejected_joint(.86,.95,1)
    second=m.rejected_joint(.86,.95,1.1)
    assert first[1] == pytest.approx(second[1])
    assert first[0] != pytest.approx(second[0])
    assert m.rejected_joint(1,.98,1)[1]<0


def test_fixed_threshold_boundaries_and_rounding():
    base=(2*27200+29200)/3
    assert m.classify_lambda(17.09*base/100,base,False)=="NO ALARM"
    assert m.classify_lambda(16.93*base/100,base,False)=="WARN"
    assert m.classify_lambda(4762,base)=="AMBIGUOUS"
    assert m.classify_lambda(4717,base)=="ESCALATE"
    assert m.classify_lambda(4718,base)=="AMBIGUOUS"


def test_stock_reconstruction_matches_independent_K1_outputs():
    d,_=m.backlog(m.panel())
    old=m.pd.read_csv(m.ROOT/"data/processed/forecast_methods/kernel_phi_v2/B1_paid_backlog_panel.csv")
    joined=d.merge(old[["q","kernel_fee_stock_musd"]],left_on="quarter",right_on="q",suffixes=("_new","_old"))
    j=joined.dropna(subset=["kernel_fee_stock_musd_new","kernel_fee_stock_musd_old"])
    assert len(j)>=14
    np.testing.assert_allclose(j.kernel_fee_stock_musd_new,j.kernel_fee_stock_musd_old,rtol=1e-11)
    frozen=m.pd.read_csv(m.ROOT/"data/processed/forecast_methods/kernel_phi_v2/B3_coverage_deviations.csv")
    for q in ("2025Q4","2026Q1","2026Q2"):
        result=float(d.set_index("quarter").loc[q,"excess_unpaid_pp"])
        old=frozen[(frozen.q==q)&(frozen.metric=="unpaid_share_stock_u")].iloc[0]
        assert result==pytest.approx(100*old.dev_abs,abs=1e-10)
    # Headline +8.1pp is a source rounding discrepancy, preserved in acceptance.json.
    assert round(float(d.set_index("quarter").loc["2026Q1","excess_unpaid_pp"]),1)==8.0


def test_late_scenario_cannot_be_backdated():
    with pytest.raises(ValueError,match="unavailable"):
        m.live_paths(m.panel(),"2026-08-06",m.pd.read_csv(m.D1))


def test_live_paths_preserve_lag_and_overlap_policy():
    rows,reg=m.live_paths(m.panel(),"2026-09-13",m.pd.read_csv(m.D1))
    assert len(rows)==6 and len(reg)==12
    assert set(reg.window)=={"LIVE"}
    assert set(reg.prior_basis)=={"PIT","full_sample"}
    assert rows[rows.quarter=="2026Q3"].registered_revenue_musd.nunique()==1
    r=rows[(rows.nights_variant=="theo")&(rows.quarter=="2026Q4")].iloc[0]
    assert r.applied_L==0
    assert r.registered_revenue_musd==r.pure_kernel_revenue_musd
    assert rows[rows.quarter=="2026Q4"].q3_gbv_musd.nunique()==2
