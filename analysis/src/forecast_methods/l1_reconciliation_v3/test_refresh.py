from pathlib import Path
import sys
import json
import shutil
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from l1_reconciliation_v3.refresh import strict_slice, complete_quarter_arrivals, covariate_fit
from l1_reconciliation_v3.run import inputs, factor, forward_scenario
from l1_reconciliation_v3.refresh import AnchoredRecon
from l1_reconciliation_v3 import run as runner


def test_strict_cutoff_and_missing_date():
    frame=pd.DataFrame({"knowable_from":["2024-02-01","2024-02-02","2024-02-03"],"value":[1,2,3]})
    assert strict_slice(frame,"2024-02-02").value.tolist()==[1]
    frame.loc[0,"knowable_from"]=None
    with pytest.raises(ValueError,match="Undated"):strict_slice(frame,"2024-02-02")


def test_partial_quarter_is_never_extrapolated():
    d=pd.DataFrame(dict(series=["x"]*5,region=["na"]*5,month=["2024-01","2024-02","2024-03","2024-04","2024-05"],value=[10]*5,knowable_from=["2024-06-01"]*5))
    out=complete_quarter_arrivals(d)
    assert out.quarter.tolist()==["2024Q1"]
    assert out.value.tolist()==[30]
    assert complete_quarter_arrivals(d,"2024-06-01").empty
    with pytest.raises(ValueError,match="Duplicate"):complete_quarter_arrivals(pd.concat([d,d.iloc[[0]]]))


def test_current_revisions_cannot_produce_historical_coefficients():
    d=pd.DataFrame(dict(series=["x"]*12,region=["na"]*12,month=pd.date_range("2022-01-01",periods=12,freq="MS").strftime("%Y-%m"),value=np.arange(1,13),knowable_from=["2026-09-13"]*12))
    panel=pd.DataFrame(columns=["quarter","region","nights_m","knowable_from"])
    assert covariate_fit(panel,d,"2024-02-01").empty


def test_annual_anchors_and_input_cells_are_pit():
    qs,ex,iv,kpi,den,fx=inputs("2024-02-16")
    assert pd.to_datetime(ex.knowable_from).max()<pd.Timestamp("2024-02-16")
    assert pd.to_datetime(iv.knowable_from).max()<pd.Timestamp("2024-02-16")
    assert fx.loc[fx.source != "disclosed_pair", "fx_pp"].isna().all()
    rec=AnchoredRecon(qs,ex,den,iv,fx,as_of="2024-02-16")
    assert rec.anchor_frame.year.max()==2022
    assert np.all(rec.theta0()==0)


def test_exact_revenue_identity_at_arbitrary_positive_parameters():
    qs,ex,iv,kpi,den,fx=inputs()
    rec=AnchoredRecon(qs,ex,den,iv,fx)
    theta=np.random.default_rng(30).normal(0,.1,rec.n_params)
    s,n,tr,g,a=rec.forward(theta)
    assert np.allclose(g*tr[:,None]*rec.unpack(theta)[1],rec.REV,atol=1e-10)
    assert np.allclose(g.sum(axis=1),rec.gbv_tot)
    assert np.allclose(n.sum(axis=1),rec.units)
    panel=rec.panel(theta)
    fac=factor(forward_scenario(panel))
    assert np.isclose((1+fac['nights_growth_pp']/100)*(1+fac['adr_growth_pp']/100)-1,fac['gbv_growth_pp']/100)
    assert np.isclose(fac['geo_mix_pp']+fac['within_pp']+fac['cross_mix_price_pp'],fac['adr_growth_pp'])


def test_local_candidates_do_not_assert_a_backdated_vintage():
    kpi=pd.DataFrame({"quarter":["2025Q3","2025Q4","2026Q1","2026Q2"],
                      "revenue_musd":[100.,100.,100.,100.]})
    revenue={"2026Q1":100.,"2026Q2":100.,"2026Q3":120.,"2026Q4":130.,
             "2027Q1":110.,"2027Q2":115.,"2027Q3":132.,"2027Q4":143.}
    before=pd.Timestamp.now(tz="UTC")
    result=runner.local_candidate_rows(revenue,kpi,61,18)
    after=pd.Timestamp.now(tz="UTC")
    assert len(result)==12
    assert "vintage_date" not in result and "knowable_from" not in result
    assert result.registration_status.eq("UNREGISTERED_LOCAL_CANDIDATE").all()
    created=pd.to_datetime(result.reconstruction_created_at_utc,utc=True)
    assert created.between(before,after).all()
    assert result.analysis_input_cutoff.eq(runner.ASOF).all()
    growth=result[(result.object=="fy27_growth") & (result.quarter=="2027Q3")].point.iloc[0]
    assert growth==pytest.approx(10.)


def test_candidates_only_path_never_refits_or_writes_outside_its_outputs(tmp_path,monkeypatch):
    original=runner.OUT
    for name in ["fy27_regional_scenario.csv","diagnostics.json"]:
        shutil.copyfile(original/name,tmp_path/name)
    frozen={p.name:p.read_bytes() for p in tmp_path.iterdir()}
    def forbidden_fit(*args,**kwargs):
        raise AssertionError("Candidates-only path must not refit the regional model")
    monkeypatch.setattr(AnchoredRecon,"fit",forbidden_fit)
    monkeypatch.setattr(runner,"OUT",tmp_path)
    csv_writer=pd.DataFrame.to_csv
    def confined_csv(frame,path,*args,**kwargs):
        assert Path(path).resolve().is_relative_to(tmp_path.resolve()), "Unexpected write outside R output directory"
        return csv_writer(frame,path,*args,**kwargs)
    monkeypatch.setattr(pd.DataFrame,"to_csv",confined_csv)
    assert runner.main(["--candidates-only"])==0
    assert all((tmp_path/name).read_bytes()==raw for name,raw in frozen.items())
    actual=pd.read_csv(tmp_path/"UNREGISTERED_fy27_candidates.csv")
    rejected=original/"UNREGISTERED_rejected_registry_20260913"
    old=pd.concat([pd.read_csv(rejected/f"l1-reconciliation-v3__{obj}.csv")
                   for obj in ["fy27_revenue","fy27_growth"]])
    paired=actual.merge(old,on=["method","object","target","quarter"],suffixes=("_new","_old"),validate="one_to_one")
    assert len(paired)==12
    assert np.allclose(paired.point_new,paired.point_old,rtol=0,atol=1e-10)
    status=json.loads((tmp_path/"registration_status.json").read_text(encoding="utf8"))
    assert status["rows"]==12 and status["shared_registry_files_written"]==0
    assert set(p.name for p in tmp_path.iterdir())==set(frozen)|{"UNREGISTERED_fy27_candidates.csv","registration_status.json"}
