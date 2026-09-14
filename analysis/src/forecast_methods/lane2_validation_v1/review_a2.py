"""Independent parent checks of A2 outputs against frozen inputs and K0."""
import io
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'analysis/src/forecast_methods'))
from kernel_engine_v2 import kernel_guide,DataUnavailable
from harness_v1_1 import RUN_DATE


def main():
    folder=ROOT/'data/processed/forecast_methods/alpha_a2'
    c=pd.read_csv(folder/'cells.csv')
    s=pd.read_csv(folder/'statistics.csv')
    controls=pd.read_csv(folder/'controls.csv')
    reg=pd.read_csv(ROOT/'data/processed/forecast_methods/registry/alpha-a2__guide_mid_next_q.csv')
    l0=pd.read_csv(ROOT/'data/processed/forecast_methods/L0/L0_vintage_register.csv',comment='#').set_index('register_id')
    ret=pd.read_csv(ROOT/'data/processed/forecast_methods/returns_v1/earnings_reactions_open_v1.csv').set_index('event_date')
    note=(ROOT/'docs/revenue-forecast-strategy/05_backtests/ALPHA_A2_GUIDE_SURPRISE_V2.md').read_text(encoding='utf-8')
    brief=(ROOT/'docs/thesis-kernel-topdown/lane2/A2_GUIDE_SURPRISE_V2.md').read_text(encoding='utf-8')
    passline=brief.split('## Pass line (pre-registered — copy verbatim into the note before running)\n')[1].split('\n## Outputs')[0].strip()
    assert passline in note,'pre-registered pass line not verbatim'
    w1=c[c.quarter.between('2023Q1','2026Q2')].copy()
    assert len(w1)==14 and w1.quarter.is_unique
    checked=0
    for x in w1.itertuples():
        source=l0.loc['PG-'+x.quarter+'-revenue']
        if x.consensus_status=='available':
            assert bool(source.pit_usable) and bool(source.vendor_attributed) and source.role=='pre_guide'
            assert source.vendor==x.street_vendor and source.as_of_timestamp==x.street_as_of
            assert pd.Timestamp(source.as_of_timestamp)<=pd.Timestamp(x.guide_date)
            assert float(source['value'])==x.consensus_musd
        else:
            assert not x.evaluable
        try:
            f=kernel_guide(x.quarter,pd.Timestamp(x.guide_date)+pd.Timedelta(days=1))
            np.testing.assert_allclose(f['point'],x.default_kernel_guide_musd,atol=1e-9,rtol=0)
            checked+=1
        except DataUnavailable:
            assert pd.isna(x.default_kernel_guide_musd)
        assert pd.Timestamp(x.entry_date)>pd.Timestamp(x.guide_date)
        for h in (1,5,20,60):
            col=f'excess_open_{h}d_pct'
            np.testing.assert_allclose(getattr(x,col),ret.loc[x.guide_date,col],atol=1e-12,rtol=0,equal_nan=True)
    result={'candidate_rows_checked':14,'kernel_values_recomputed':checked,'returns_cells_checked':56,
            'verbatim_preregistration':True,'windows':{}}
    for window,lo in [('W1','2023Q1'),('W2','2024Q1')]:
        e=w1[(w1.quarter>=lo)&w1.evaluable]
        high=e[e.signal_pct.abs()>1]
        labels=np.where(high.actual_gap_lo>0,1,np.where(high.actual_gap_hi<0,-1,0))
        m=labels!=0
        n=int(m.sum()); hits=int((np.sign(high.signal_pct.to_numpy()[m])==labels[m]).sum())
        p=hits/n; z=norm.ppf(.975); den=1+z*z/n
        centre=(p+z*z/(2*n))/den
        half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
        mean=float((np.sign(high.signal_pct)*high.excess_open_20d_pct).mean())
        row=s[(s.variant=='default')&(s.window==window)].iloc[0]
        assert row.n_evaluable==len(e) and row.n_scored==n and row.hits==hits
        np.testing.assert_allclose([row.wilson95_lo,row.wilson95_hi,row.signed_return20_mean],[centre-half,centre+half,mean],atol=1e-12,rtol=0)
        cc=e[['signal_pct','excess_open_20d_pct','gbv_surprise_pct','actual_gap_pct']].dropna()
        X=np.column_stack([np.ones(len(cc)),cc[['gbv_surprise_pct','actual_gap_pct']]])
        Y=cc[['signal_pct','excess_open_20d_pct']].to_numpy()
        residual=Y-X@np.linalg.lstsq(X,Y,rcond=None)[0]
        partial=float(np.corrcoef(residual.T)[0,1])
        cr=controls[(controls.variant=='default')&(controls.window==window)&(controls.controls=='gbv_and_guide_gap')].iloc[0]
        assert cr.n==len(cc)
        np.testing.assert_allclose(partial,cr.partial_corr,atol=1e-12,rtol=0)
        result['windows'][window]={'evaluable':len(e),'high_signal_n':n,'hits':hits,'wilson95':[centre-half,centre+half],
                                  'signed_return20_mean':mean,'control_n':len(cc),'partial_corr':partial}
    live=reg[reg.window=='LIVE']
    assert len(live)==2 and live.quarter.eq('2026Q4').all()
    assert live.vintage_date.eq(str(RUN_DATE)).all()
    assert live.format_version.astype(str).eq('1.1').all()
    assert set(live.prior_basis)=={'PIT','full_sample'}
    result.update(registered_rows=len(reg),live_rows=len(live),live_vintage=str(RUN_DATE),verdict='PASS')
    out=ROOT/'data/processed/forecast_methods/lane2_validation_v1/after_a2_review.json'
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
