"""Rebuild X entirely from git summaries and small attributed public numeric extracts."""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'data/processed/forecast_methods/regional_kernel_v1'
sys.path.insert(0, str(HERE.parent))
from regional_kernel_v1.engine import (REGIONS, CCYS, AS_OF, canonical, annual_ratios,
    origin_matrix, exposure_mix, validate_exposure, translation, engine_order, interval_fit, admissible_pass_scales)


def read(path):
    return pd.read_csv(ROOT / path, comment='#')


def save(d, name):
    d.to_csv(OUT / (name+'.csv'), index=False)


def quarterly_inputs(annual, exact, panel):
    adr = read('data/processed/adr/04_regional_quarterly.csv')
    d = adr.pivot(index=['quarter','region'], columns='metric', values='value').reset_index()
    d['quarter'] = d.quarter.map(canonical)
    d['raw_gbv_musd'] = d.nights_m * d.adr_usd_anchored
    total = panel.set_index('quarter').gbv_musd
    d['gbv_musd'] = d.raw_gbv_musd * d.quarter.map(total) / d.groupby('quarter').raw_gbv_musd.transform('sum')
    bands = read('data/processed/overnight/10_regional_panel_quarterly.csv')
    bands['quarter'] = bands.quarter.map(canonical)
    bands = bands.set_index('quarter')
    widths=[]
    for row in d.itertuples():
        try:
            lo, hi = bands.loc[row.quarter, [row.region+'_nights_yoy_lo', row.region+'_nights_yoy_hi']]
            width=(hi-lo)/2/(100+(hi+lo)/2) if np.isfinite([lo,hi]).all() else .05
        except KeyError:
            width=.05
        widths.append(max(0.,width))
    d['nights_band_fraction'] = widths
    # ADR level uncertainty is undisclosed. +/-10% is sensitivity, not a fitted/identified interval.
    d['gbv_sensitivity_lo'] = d.gbv_musd*(1-d.nights_band_fraction)*.90
    d['gbv_sensitivity_hi'] = d.gbv_musd*(1+d.nights_band_fraction)*1.10
    d['print_date']=AS_OF
    d['basis']='retrospective reconstructed quarterly GBV; not disclosed; current research vintage'
    d['interval_basis']='letter nights band and assumed +/-10% ADR; not confidence interval'
    d=d.sort_values(['quarter','region']).reset_index(drop=True)
    rows=[]
    for row in exact.itertuples():
        q=pd.Period(row.quarter,freq='Q')
        lags=d[d.quarter.isin([str(q-1),str(q-2)]) & (d.region==row.region)].set_index('quarter')
        if len(lags)!=2:
            continue
        b=2/3*lags.loc[str(q-1),'gbv_musd']+1/3*lags.loc[str(q-2),'gbv_musd']
        blo=2/3*lags.loc[str(q-1),'gbv_sensitivity_lo']+1/3*lags.loc[str(q-2),'gbv_sensitivity_lo']
        bhi=2/3*lags.loc[str(q-1),'gbv_sensitivity_hi']+1/3*lags.loc[str(q-2),'gbv_sensitivity_hi']
        a=annual[(annual.region==row.region)&(annual.year==min(q.year,2025))].iloc[0]
        rows.append(dict(quarter=str(q),region=row.region,season=q.quarter,revenue_musd=row.revenue_musd,
            kernel_base_musd=b,lambda_pct=100*row.revenue_musd/b,lambda_sensitivity_lo=100*row.revenue_musd/bhi,
            lambda_sensitivity_hi=100*row.revenue_musd/blo,annual_anchor_pct=a.lambda_pct,
            annual_anchor_year=a.year,revenue_knowable_from=row.knowable_from,print_date=AS_OF,
            basis='same-cell accounting ratio; not predictive validation'))
    return d, pd.DataFrame(rows)


def currency_baskets():
    b=read('data/processed/overnight/10_fx_basket.csv')
    b=b[b.region.isin(REGIONS)&(b.currency!='BASKET')].copy()
    b['ccy']=b.proxy_series.fillna(b.currency)
    return b.groupby(['region','ccy']).weight.sum().unstack(fill_value=0).reindex(index=REGIONS,columns=CCYS,fill_value=0)


def public_proxies(public, dest, nights):
    mix={}; currency={}; coverage=[]
    for provider, region, total in [('NTTO','na',68288000),('JNTO','apac',3442100)]:
        part=public[public.provider==provider]
        known=part[part.origin_region.isin(REGIONS)].groupby('origin_region').visitors_or_nights.sum().reindex(REGIONS,fill_value=0)/total
        missing=1-known.sum()
        mix[region]=known+missing*nights/nights.sum()
        # Unknown country currencies remain a labelled destination-basket allocation, not USD.
        if provider=='JNTO':
            cpart=pd.concat([public[public.provider=='JNTO_CCY'], part[part.currency.isin(CCYS)]])
        else:
            cpart=part[part.currency.isin(CCYS)]
        observed=cpart.groupby('currency').visitors_or_nights.sum().reindex(CCYS,fill_value=0)/total
        remainder=1-observed.sum()
        currency[region]=observed+remainder*dest.loc[region]
        coverage.append(dict(destination_proxy=region,provider=provider,arrivals_total=total,
            classified_region_fraction=1-missing,matched_fx_currency_fraction=1-remainder,
            airbnb_od_measured_fraction=0.,basis='tourism proxy only; unresolved residual allocated by explicit assumption'))
    return mix,currency,pd.DataFrame(coverage)


def build_exposures(gbv, dest, pubmix, pubccy, guest):
    odrows=[];erows=[]
    for quarter,d in gbv.groupby('quarter'):
        n=d.set_index('region').nights_m.reindex(REGIONS)
        matrix=origin_matrix(n,pubmix)
        for destination in REGIONS:
            oweights=matrix[destination]/n[destination]
            origin_ccy=sum(oweights[o]*dest.loc[o] for o in REGIONS)
            if destination in pubccy:
                origin_ccy=.54*dest.loc[destination]+.46*pubccy[destination]
            gweights,rweights=exposure_mix(dest.loc[destination],origin_ccy,guest)
            for origin in REGIONS:
                odrows.append(dict(quarter=quarter,origin=origin,destination=destination,nights_m=matrix.loc[origin,destination],
                    origin_share_of_destination=oweights[origin],cross_border_country_assumption=.46,
                    print_date=AS_OF,basis='current reconstruction; tourism proxies plus assumptions; not PIT history'))
            for i,ccy in enumerate(CCYS):
                erows.append(dict(quarter=quarter,geography=destination,region=destination,level='region',currency=ccy,
                    gbv_share=gweights[i],revenue_share=rweights[i],guest_fee_share=guest,print_date=AS_OF,
                    reference_basis='quarterly booking-date USD; FX scenario; origin does not identify payment currency',
                    weight_basis='assumed destination basket / partial public tourism origin proxy'))
    e=pd.DataFrame(erows);validate_exposure(e)
    return pd.DataFrame(odrows),e


def fx_rates():
    daily=read('data/processed/forecast_methods/fx_lag_v2/fx_daily_2026-09-11.csv')
    daily=daily[daily.ccy.isin(CCYS)].copy();daily['date']=pd.to_datetime(daily.date)
    wide=daily.pivot(index='date',columns='ccy',values='usd_per_unit').sort_index()
    observed_through=wide.index.max()
    # Holidays carry the preceding available quote. Future business days hold 4-Sep spot.
    dates=pd.bdate_range(wide.index.min(),'2026-12-31')
    wide=wide.reindex(dates).ffill();wide['USD']=1.
    quarterly=wide.groupby(wide.index.to_period('Q')).mean()
    growth=100*(quarterly/quarterly.shift(4)-1)
    growth.index=growth.index.astype(str)
    growth=growth.reindex(columns=CCYS)
    fractions=[]
    for q in ['2026Q3','2026Q4']:
        p=pd.Period(q,freq='Q');days=pd.bdate_range(p.start_time,p.end_time)
        fractions.append(dict(quarter=q,fx_date_share_observed=float((days<=observed_through).mean()),
                              through=str(observed_through.date()),basis='business-day share; not volume-determined share'))
    return growth,pd.DataFrame(fractions)


def add_nowcast(gbv):
    d=gbv.copy();rows=[]
    for region in REGIONS:
        r=d[d.region==region].set_index('quarter')
        recent=[r.loc[q,'gbv_musd']/r.loc[str(pd.Period(q,freq='Q')-4),'gbv_musd']-1 for q in ['2026Q1','2026Q2']]
        g=np.mean(recent)
        for q in ['2026Q3','2026Q4']:
            old=r.loc[str(pd.Period(q,freq='Q')-4)]
            # Current run estimates a scenario. It is never smuggled in as a printed quarterly GBV.
            rows.append(dict(quarter=q,region=region,gbv_musd=old.gbv_musd*(1+g),nights_m=old.nights_m*(1+g),
                adr_usd_anchored=old.adr_usd_anchored,print_date=AS_OF,
                basis='conditional same-season GBV; mean of two latest measured-total/reconstructed-regional y/y rates'))
    return pd.concat([d,pd.DataFrame(rows)],ignore_index=True)


def main():
    start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    public=pd.read_csv(HERE/'public_inputs.csv');save(public,'public_source_extracts')
    annual=annual_ratios(read('data/processed/adr/01_regional_annual.csv'));save(annual,'lambda_annual')
    exact=read('data/processed/forecast_methods/L0/L0_exact_regional_revenue.csv')
    exact['quarter']=exact.quarter.map(canonical)
    panel=read('data/processed/forecast_methods/fx_lag_v2/04_analysis_panel.csv')
    panel['quarter']=panel.quarter_canon.map(canonical)
    gbv,lam=quarterly_inputs(annual,exact,panel);save(gbv,'regional_gbv_reconstruction');save(lam,'lambda_regional')
    recon=lam.groupby('quarter').apply(lambda d:pd.Series({'reconstructed_musd':float((d.lambda_pct*d.kernel_base_musd/100).sum()),
                       'regional_actual_musd':d.revenue_musd.sum(),'n_regions':len(d)}),include_groups=False).reset_index()
    recon['consolidated_actual_musd']=recon.quarter.map(panel.set_index('quarter').revenue_musd)
    recon['relative_error_pct']=100*(recon.reconstructed_musd/recon.consolidated_actual_musd-1)
    recon['basis']='algebraic same-cell reconstruction; zero out-of-sample forecast observations';save(recon,'reconciliation')
    # Freeze annual-anchored seasonal coefficients from currently available reconstructed observations.
    fitlam=lam[lam.quarter>='2023Q1'].copy()
    fitlam['seasonal_factor']=fitlam.lambda_pct/fitlam.annual_anchor_pct
    live=fitlam.groupby(['region','season']).agg(factor=('seasonal_factor','mean'),n=('lambda_pct','size'),
        sensitivity_lo=('lambda_sensitivity_lo','mean'),sensitivity_hi=('lambda_sensitivity_hi','mean'),
        lambda_sd_pct=('lambda_pct','std')).reset_index()
    anchor=annual[annual.year==2025].set_index('region').lambda_pct
    live['lambda_pct']=live.factor*live.region.map(anchor);live['print_date']=AS_OF
    live['basis']='2025 annual anchor times mean 2023+ same-season factor; current research vintage';save(live,'regional_lambdas_k0')
    # Same-season decomposition: lambda_total = sum(weight_region * lambda_region).
    drift=[]
    for window,first in [('W1','2023Q1'),('W2','2024Q1')]:
        z=lam[lam.quarter>=first].copy()
        z['weight']=z.kernel_base_musd/z.groupby('quarter').kernel_base_musd.transform('sum')
        center=z.groupby(['region','season']).lambda_pct.mean()
        z['mix_only']=z.apply(lambda r:r.weight*center.loc[(r.region,r.season)],axis=1)
        agg=z.groupby(['quarter','season']).agg(total=('revenue_musd','sum'),base=('kernel_base_musd','sum'),mix=('mix_only','sum')).reset_index()
        agg['lambda']=100*agg.total/agg.base
        for col in ['lambda','mix']:
            agg[col+'_demean']=agg[col]-agg.groupby('season')[col].transform('mean')
        var=float(agg.lambda_demean.var(ddof=1));mixvar=float(agg.mix_demean.var(ddof=1));cov=float(agg[['lambda_demean','mix_demean']].cov().iloc[0,1])
        drift.append(dict(window=window,n_quarters=len(agg),lambda_variance=var,mix_variance=mixvar,
            mix_variance_ratio=mixvar/var,ols_mix_r2=float(agg.lambda_demean.corr(agg.mix_demean)**2),
            covariance_allocation_share=cov/var,basis='retrospective decomposition of modelled GBV; not causally explained variance'))
    save(pd.DataFrame(drift),'mix_variance_decomposition')
    changes=[]
    for region in REGIONS:
        z=lam[(lam.region==region)&lam.quarter.between('2023Q1','2025Q4')]
        for season in range(1,5):
            s=z[z.season==season].sort_values('quarter')
            changes.append(dict(region=region,season=season,first_quarter=s.quarter.iloc[0],last_quarter=s.quarter.iloc[-1],
                lambda_change_pp=s.lambda_pct.iloc[-1]-s.lambda_pct.iloc[0],n=len(s)))
    save(pd.DataFrame(changes),'regional_drift')
    dest=currency_baskets();nights=gbv[gbv.quarter=='2026Q2'].set_index('region').nights_m.reindex(REGIONS)
    pmix,pccy,coverage=public_proxies(public,dest,nights);save(coverage,'od_source_coverage')
    forward=add_nowcast(gbv);save(forward,'gbv_with_conditional_horizons')
    fx,obs=fx_rates();save(fx.rename_axis('quarter').reset_index(),'currency_yoy_spot_held');save(obs,'fx_observed_share')
    results=[];profiles=[];fitresults=[];demand=[];weights=[];passrows=[]
    pass_scales=admissible_pass_scales(read('data/processed/overnight/10_regional_fx_passthrough.csv'))
    for guest in [0.,.5,14.1/17.1]:
        od,exposure=build_exposures(forward,dest,pmix,pccy,guest)
        if guest==.5:
            save(od,'od_nights_matrix');save(exposure,'exposure')
        latest=exposure[exposure.quarter=='2026Q2'].copy()
        revw=latest.pivot(index='geography',columns='currency',values='revenue_share').reindex(index=REGIONS,columns=CCYS)
        gbvw=latest.pivot(index='geography',columns='currency',values='gbv_share').reindex(index=REGIONS,columns=CCYS)
        rfx=fx @ revw.T;gfx=fx @ gbvw.T
        for region in REGIONS:
            for c in CCYS:
                weights.append(dict(guest_fee_share=guest,region=region,currency=c,judgement_destination_weight=dest.loc[region,c],
                    scenario_revenue_weight=revw.loc[region,c],scenario_gbv_weight=gbvw.loc[region,c],
                    measured_airbnb_weight=np.nan,status='not identified; scenario must not replace original basket'))
        for q in ['2026Q3','2026Q4']:
            p=pd.Period(q,freq='Q');coeff=live[live.season==p.quarter].set_index('region').lambda_pct.reindex(REGIONS)
            g1=forward[forward.quarter==str(p-1)].set_index('region').gbv_musd.reindex(REGIONS)
            g2=forward[forward.quarter==str(p-2)].set_index('region').gbv_musd.reindex(REGIONS)
            prior=panel.set_index('quarter').loc[str(p-4),'revenue_musd']
            dollars,fxpp=translation(g1,g2,coeff,rfx.loc[str(p-1)],rfx.loc[str(p-2)],prior)
            # Separate sensitivity: replace the destination's unit translation with the supplied
            # ADR pass-through, while retaining only the incremental origin-minus-destination fee shift.
            # The slopes already embed old judgement baskets and are not independently measured exposure.
            adjusted1=rfx.loc[str(p-1)]+(pass_scales-1)*gfx.loc[str(p-1)]
            adjusted2=rfx.loc[str(p-2)]+(pass_scales-1)*gfx.loc[str(p-2)]
            _,passpp=translation(g1,g2,coeff,adjusted1,adjusted2,prior)
            for i,region in enumerate(REGIONS):
                passrows.append(dict(quarter=q,region=region,guest_fee_share=guest,
                    assumed_or_fitted_adr_scale=pass_scales[region],gross_fx_contribution_pp=passpp[i],
                    after_hedge_fx_contribution_pp=passpp[i]-.21*dollars[i]/dollars.sum(),
                    basis='sensitivity: reported-ADR pass-through replaces unit destination translation; incremental guest-origin shift only; not a second FX addition'))
            # Demand is a zero-sum geographic reallocation of nights, separately reported.
            ipp={}
            for region in REGIONS:
                origin_rate=sum(pmix.get(region,nights/nights.sum()).loc[o]*gfx.loc[str(p-2),o] for o in REGIONS)
                ipp[region]=origin_rate-gfx.loc[str(p-2),region]
            raw=pd.Series(ipp)*.11
            future_nights=forward[forward.quarter==q].set_index('region').nights_m.reindex(REGIONS)
            future_adr=forward[forward.quarter==q].set_index('region').adr_usd_anchored.reindex(REGIONS)
            centered=raw-float((raw*future_nights/future_nights.sum()).sum())
            for i,region in enumerate(REGIONS):
                prior_region=exact[(exact.quarter==str(p-4))&(exact.region==region)].revenue_musd.iloc[0]
                results.append(dict(guest_fee_share=guest,quarter=q,region=region,revenue_scenario_musd=dollars[i],
                    gross_fx_contribution_pp=fxpp[i],hedge_pp_allocated=-.21*dollars[i]/dollars.sum(),
                    after_hedge_fx_contribution_pp=fxpp[i]-.21*dollars[i]/dollars.sum(),
                    management_q3_comparator_allocated_pp=3*prior_region/prior if q=='2026Q3' else np.nan,
                    difference_from_allocated_management_pp=fxpp[i]-.21*dollars[i]/dollars.sum()-3*prior_region/prior if q=='2026Q3' else np.nan,
                    allocation_basis='management discloses no regional guide FX; total 3pp comparator allocated by prior-year regional revenue only',
                    source_basis='current reconstructed weights; fixed 2/3 lag1 + 1/3 lag2; conditional GBV for Q4',
                    management_q3_afterhedge_pp=3. if q=='2026Q3' else np.nan))
                demand.append(dict(quarter=q,region=region,guest_fee_share=guest,inbound_purchasing_power_pp=ipp[region],
                    raw_nights_differential_pp=raw[region],centered_nights_differential_pp=centered[region],
                    base_nights_m=future_nights[region],scenario_nights_m=future_nights[region]*(1+centered[region]/100),
                    nights_delta_m=future_nights[region]*centered[region]/100,
                    gbv_mix_delta_musd=future_nights[region]*centered[region]/100*future_adr[region],
                    base_gbv_musd=future_nights[region]*future_adr[region],
                    weighted_nights_total_contribution_pp=centered[region]*future_nights[region]/future_nights.sum(),
                    basis='0.11 imposed scenario elasticity; zero-sum regional reallocation; not fitted total demand'))
        # Retrospective interval fit. USD-inclusive driver divided by non-USD share for comparable scale units.
        rows=[]
        for q in panel.quarter:
            p=pd.Period(q,freq='Q')
            z=lam[lam.quarter==q].set_index('region')
            if len(z)!=4 or any(str(p-j) not in rfx.index for j in range(3)):
                continue
            shares=z.revenue_musd/z.revenue_musd.sum()
            nusd=float((shares*(1-revw.USD)).sum())
            target=panel[panel.quarter==q].iloc[0]
            if pd.isna(target.gross_fx_ex_hedge_pp):continue
            row=dict(quarter=q,y=target.gross_fx_ex_hedge_pp,non_usd_share=nusd)
            row.update({f'x{j}':float((rfx.loc[str(p-j)]*shares).sum()/nusd) for j in range(3)})
            rows.append(row)
        f=pd.DataFrame(rows);save(f,f'fx_fit_inputs_guest{guest:.4f}')
        for window,first in [('W1','2023Q1'),('W2','2024Q1')]:
            z=f[f.quarter>=first].copy()
            for driver_basis in ['nonUSD_normalized','USD_inclusive_comparable_B4']:
                X=z[['x0','x1','x2']]
                if driver_basis=='USD_inclusive_comparable_B4':
                    X=X.mul(z.non_usd_share,axis=0)
                estimate,profile=interval_fit(X,z.y)
                estimate.update(guest_fee_share=guest,window=window,driver_basis=driver_basis,
                    mean_assumed_non_usd_share=z.non_usd_share.mean(),
                    basis='retrospective; current weights on past outcomes; NOT historical forecast accuracy')
                fitresults.append(estimate);profile['window']=window;profile['guest_fee_share']=guest
                profile['driver_basis']=driver_basis;profiles.append(profile)
    out=pd.DataFrame(results);save(out,'fx_regional_recompute');save(pd.DataFrame(demand),'demand_channel_scenario')
    save(pd.DataFrame(passrows),'adr_passthrough_sensitivity')
    save(pd.DataFrame(weights),'fx_basket_scenario');save(pd.DataFrame(weights)[['guest_fee_share','region','currency','measured_airbnb_weight','status']],'fx_basket_measured')
    save(pd.concat(profiles,ignore_index=True),'gross_scale_profile');save(pd.DataFrame(fitresults),'gross_scale_fits')
    # Publication-time FX-share receipt. Future November fractions are labelled assumptions, not observed FX today.
    observed_triple=[]
    fit_frame=pd.DataFrame(fitresults)
    for origin,through,basis in [(AS_OF,'2026-09-04','actually observed FX through supplied FRED snapshot'),
        ('2026-11-05','2026-11-04','future calendar ceiling; publication date and actual currency path not observed'),
        ('2026-11-05','2026-10-30','future weekly-publication-lag scenario; not observed today')]:
        q=pd.Period('2026Q4',freq='Q')
        frac=[]
        for j in range(3):
            days=pd.bdate_range((q-j).start_time,(q-j).end_time)
            frac.append(float((days<=pd.Timestamp(through)).mean()))
        for guest in [0.,.5,14.1/17.1]:
            row=fit_frame[(fit_frame.guest_fee_share==guest)&(fit_frame.window=='W1')&
                          (fit_frame.driver_basis=='USD_inclusive_comparable_B4')].iloc[0]
            beta=np.asarray(row.beta);weights=beta/beta.sum()
            for spec,w in [('free_current_retrospective_fit',weights),('fixed_Phi',[0,2/3,1/3]),('contemporaneous',[1,0,0])]:
                observed_triple.append(dict(as_of=origin,target_quarter='2026Q4',guest_fee_share=guest,spec=spec,
                    assumed_fx_publication_cutoff=through,driver_share=float(np.dot(w,frac)),
                    volume_determined_share=np.nan,basis=basis+'; conditional on current exposure and volume weights'))
    save(pd.DataFrame(observed_triple),'observed_share_triple')
    totals=out.groupby(['guest_fee_share','quarter'])[['revenue_scenario_musd','gross_fx_contribution_pp','after_hedge_fx_contribution_pp']].sum().reset_index()
    save(totals,'fx_consolidated_recompute')
    # R-engine geographic handoff. These are booking-date USD levels, so both incremental FX scales are zero.
    # Applying either exposure factor again to these levels would double count FX already in the kernel output.
    rrows=[]
    for row in out[out.guest_fee_share==.5].itertuples():
        f=forward[(forward.quarter==row.quarter)&(forward.region==row.region)].iloc[0]
        take_rate=row.revenue_scenario_musd/f.gbv_musd
        reference_adr=f.gbv_musd/f.nights_m
        check=engine_order(f.nights_m*1e6,reference_adr,take_rate,0.,0.,0.,0.,0.)
        assert np.isclose(float(check['revenue_prehedge'])/1e6,row.revenue_scenario_musd)
        rrows.append(dict(quarter=row.quarter,geography=row.region,region=row.region,level='region',
            nights=f.nights_m*1e6,adr=reference_adr,adr_basis='booking-date USD; FX already embedded',currency='USD',
            take_rate=take_rate,reference_basis='kernel revenue divided by current conditional GBV; interface roundtrip not independent forecast',
            adr_scale=0.,revenue_scale=0.,revenue_prehedge_musd=row.revenue_scenario_musd,
            python_roundtrip_revenue_musd=float(check['revenue_prehedge'])/1e6))
    save(pd.DataFrame(rrows),'r_engine_handoff')
    steps=[]
    b4=read('data/processed/forecast_methods/fx_lag_v2/26_exfx_acceleration_v2.csv')
    b4=b4.drop_duplicates('gbv_3Q26_musd')
    for guest,d in totals.groupby('guest_fee_share'):
        d=d.set_index('quarter');step=d.loc['2026Q4','after_hedge_fx_contribution_pp']-d.loc['2026Q3','after_hedge_fx_contribution_pp']
        for r in b4.itertuples():
            steps.append(dict(guest_fee_share=guest,gbv_3Q26_musd=r.gbv_3Q26_musd,base_growth_step_pp=r.gbv_base_growth_step_pp,
                regional_fx_step_pp=step,ex_fx_step_pp=r.gbv_base_growth_step_pp-step,
                basis='conditional FX scenario paired with B4 GBV sensitivity; not adopted guide bridge'))
    save(pd.DataFrame(steps),'q4_step_sensitivity')
    save(pd.DataFrame([dict(window=w,expected_cells=n,eligible_pit_od_cells=0,eligible_pit_lambda_forecasts=0,
                reason='regional GBV and O-D research vintage is 2026-09-12; historical replays refused') for w,n in [('W1',14),('W2',10)]]),'window_coverage')
    # Explicit abstention receipts, not fabricated frozen-harness dates or header-only registry files.
    save(pd.DataFrame([dict(method='regional-kernel-v1',object=o,status='not registered',n_rows=0,
        reason='current reconstruction date 2026-09-12 not allowed by frozen FORMAT 1.0; no PIT historical exposure vintage')
        for o in ['fx_pts_revenue_2026Q4','revenue_next_q']]),'registration_abstentions')
    handoff=gbv[['quarter','region','gbv_musd','print_date']].copy()
    handoff['gbv_usd_booking_dated']=handoff.pop('gbv_musd')*1e6;save(handoff,'regional_gbv_k0')
    from kernel_engine_v2.engine import kernel_forecast
    k0=kernel_forecast('2026Q3','2026-09-13',regional_gbv=handoff,regional_lambdas=live[['region','season','lambda_pct','lambda_sd_pct','print_date']])
    assert np.isclose(k0['point'],totals.loc[(totals.guest_fee_share==0)&(totals.quarter=='2026Q3'),'revenue_scenario_musd'].iloc[0])
    (OUT/'k0_handoff_check.json').write_text(json.dumps(k0,default=str,indent=2),encoding='utf-8')
    # Contract check from a non-FX reference base: revenue scale zero avoids applying the embedded FX again.
    contract=engine_order(np.array([10.]),np.array([100.]),.15,np.array([2.]),np.array([3.]),1.,0.,-.2)
    (OUT/'r_engine_contract_check.json').write_text(json.dumps({k:np.asarray(v).tolist() for k,v in contract.items()},indent=2),encoding='utf-8')
    assert np.allclose(annual.lambda_pct,annual.take_rate_pct,atol=1e-10,rtol=0)
    assert len(lam)==72 and len(recon)==18 and recon.relative_error_pct.abs().max()<=.3
    summary=dict(verdict='underpowered',annual_measured_cells=len(annual),annual_ratio_max_error_pp=float((annual.lambda_pct-annual.take_rate_pct).abs().max()),quarterly_exact_cells=len(exact),
        reconstructed_cells=len(lam),reconciliation_quarters=len(recon),max_reconciliation_error_pct=float(recon.relative_error_pct.abs().max()),
        measured_airbnb_od_cells=0,pit_w1_cells=0,pit_w2_cells=0,b4_superseded=False,
        rscript_available=bool(shutil.which('Rscript')),runtime_seconds=time.perf_counter()-start,
        proposed_memo_sentence='The regional FX reconstruction does not yet justify replacing B4: no measured Airbnb origin–destination currency matrix is identified, and the current reconstruction has 0/14 W1 and 0/10 W2 point-in-time guide observations.')
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2));print(totals.to_string(index=False));print(pd.DataFrame(fitresults).to_string(index=False))


if __name__=='__main__':
    main()
