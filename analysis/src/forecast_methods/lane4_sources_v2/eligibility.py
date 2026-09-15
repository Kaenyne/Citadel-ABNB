"""Evidence classifications and source-contract arithmetic; no new research fit."""
from collections import Counter, defaultdict
import json
import importlib.util
import math
from pathlib import Path

_spec = importlib.util.spec_from_file_location('_lane4_sources_v2_provenance', Path(__file__).with_name('run.py'))
provenance = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(provenance)

L4_BASE_COMMIT = '29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70'
L4_BASE_PATH = 'data/processed/forecast_methods/lane4_revenue_v1/snapshot_v1/forecast.csv'
DISPOSITIONS = {'observed','calculated','conditional','descriptive','comparator','unavailable','rejected'}


def number(value):
    if value is None or str(value).strip() == '':
        raise ValueError('Missing numeric input must remain unavailable')
    result = float(value)
    if not math.isfinite(result):
        raise ValueError('Nonfinite numeric input')
    return result


def prehedge_transform(revenue, hedge, new_hedge, multiplier, *, certified_prehedge,
                      matching_baseline, matching_cohort_denominator):
    """A guarded accounting identity for explicit future inputs, never an estimate."""
    if not (certified_prehedge and matching_baseline and matching_cohort_denominator):
        raise ValueError('Pre-hedge/baseline/cohort contract not satisfied')
    r, h, hn, m = map(number, (revenue, hedge, new_hedge, multiplier))
    if r-h <= 0 or m <= 0:
        raise ValueError('Pre-hedge revenue and multiplier must be positive')
    return m*(r-h)+hn


def classify(row):
    """Evidence status and applicability are distinct axes; fail on new schemas."""
    pkg, metric = row['package'], row['metric']
    if pkg == 'cohort_fx':
        metric_types = {
            'reference_normalized_kernel_revenue':('conditional','Conditional currency normalization, not observed constant-currency revenue'),
            'ordinary_booking_kernel_revenue':('calculated','Reconstructs the inherited Q3 kernel; baseline identity only, never an overlay'),
            'rnpl_retimed_kernel_revenue':('conditional','Retimed level under assumed currency, RNPL revenue-cohort share and fixing convention'),
            'rnpl_fx_incremental_replacement':('conditional','Retimed minus ordinary source level; conditional replacement, not expected revenue drag'),
            'rnpl_fx_replacement_multiplier':('conditional','T/B on normalized kernel with unresolved hedges; not certified m_pre'),
            'rnpl_fx_level_multiplier':('conditional','T/R0 reference-level factor; multiplying reported USD kernel would double-count booking FX')}
        if metric not in metric_types:
            raise ValueError('Unknown cohort FX metric')
        disposition, reason = metric_types[metric]
        return ('calculated_from_assumed_exposures_and_frozen_rates', disposition, reason,
                'ineligible_financial_application',
                'Q3 only; no certified pre-hedge denominator or H/H_new split; u/p/currency assumptions unmeasured; Q4/Q1 baseline absent')
    if pkg == 'conversion':
        if metric == 'free_to_fixed_PIT_RMSE_ratio':
            reason = 'Accepted chronological result; promotion fails both matched windows; overlapping W1/W2 and letter-close vintages'
        elif metric == 'shared_lag_w' or metric.startswith('seasonal_conversion_Q'):
            reason = 'Accepted all22 five-parameter descriptive fit; preserve joint draws; not operational replacement or measured recognition share'
        else:
            raise ValueError('Unknown conversion metric')
        return ('calculated_research_result','descriptive',reason,'evidence_only_no_parameter_replacement',
                'Existing fixed 2/3 K0 seasonal estimator retained; neither free-w nor all22 fixed OLS is promoted')
    if pkg == 'fee_panel':
        if metric != 'fee_theta_log' or row['value'] != '':
            raise ValueError('Fee theta availability changed; explicit new source review required')
        return ('unavailable','unavailable','Zero of six scheduled captures at the frozen September13 snapshot; theta unidentified',
                'unavailable_no_application','Null is not zero; imposed ADR fee mechanics do not estimate theta')
    if pkg == 'nclh':
        return ('calculated_cross_issuer_research_result','rejected','NCLH transfer test FAIL; retain negative research evidence',
                'rejected_ABNB_adjustment','Cross-issuer diagnostic supplies no ABNB revenue or valuation adjustment')
    if pkg == 'adr_hotel':
        if metric.startswith('hotel_comparator_'):
            if row['value'] == '':
                return ('unavailable','unavailable','Incomplete hotel quarter; actual hotel production unavailable',
                        'unavailable_no_application','No ABNB pricing or volume replacement')
            return ('calculated_from_observed_public_price_indices','comparator','Public hotel price index year-over-year comparator; not Airbnb or actual hotel production',
                    'comparator_only','Association/comparator does not identify causal ABNB pricing or supply')
        if metric == 'gbv_identity_comparison':
            return ('calculated_identity_on_conditional_inputs','calculated','Named nights times named ADR; coherent arithmetic comparison, not an independent forecast',
                    'conditional_scenario_only','Use one complete matched operating scenario; do not add identity or components to existing GBV')
        if metric in {'adr_usd','adr_reported_yoy','adr_exfx_yoy'}:
            return ('calculated_from_assumed_and_proxy_components','conditional','Named ADR scenario total; reported totals already contain their FX and imposed fee mechanics',
                    'conditional_replacement_only','Replace once on matched quarter/base and nights; ex-FX row needs exactly one ADR FX bridge; never stack components')
        if metric.startswith('adr_component_'):
            return ('assumed_or_proxy_component','conditional','Explanatory component already inside named ADR total; residual is not measured like-for-like pricing',
                    'component_explanation_only','No incremental application; fee K is imposed mechanics, not measured theta')
        raise ValueError('Unknown ADR/hotel metric')
    raise ValueError(f'Unknown source package {pkg}')


def dispositions(bundle):
    rows = provenance.read_csv(bundle/'l4_inputs.csv')
    metadata = json.loads((bundle/'bundle.json').read_text())
    if len(rows) != 1187 or Counter(r['package'] for r in rows) != metadata['packages']:
        raise ValueError('Research row/package count mismatch')
    seen = set()
    results = []
    payload_cache = {}
    for i, row in enumerate(rows, start=1):
        key = tuple(row[k] for k in ('package','quarter','metric','scenario'))
        if key in seen:
            raise ValueError(f'Duplicate source identity: {key}')
        seen.add(key)
        for field in ('value','lower','upper','lower_bound','upper_bound'):
            if row[field] != '':
                number(row[field])
        payload = row['bundle_payload_reference']
        if payload not in payload_cache:
            payload_cache[payload] = provenance.sha((bundle/provenance.safe_relative(payload)).read_bytes())
        measurement, disposition, reason, eligible, eligibility_reason = classify(row)
        assert disposition in DISPOSITIONS
        row_hash = provenance.sha(json.dumps(row, sort_keys=True, separators=(',',':')).encode())
        results.append({**row, 'row_id':f'L3-{i:04d}', 'source_row_number':i,
                        'source_row_sha256':row_hash,'source_measurement_class':measurement,
                        'integration_disposition':disposition,'disposition_reason':reason,
                        'financial_eligibility':eligible,'eligibility_reason':eligibility_reason,
                        'bundle_commit':provenance.BUNDLE_COMMIT,'research_commit':provenance.RESEARCH_COMMIT,
                        'bundle_payload_sha256':payload_cache[payload]})
    return results


def source_arithmetic(bundle):
    summaries = provenance.read_csv(bundle/'payload/cohort_fx/scenario_summary.csv')
    detail = provenance.read_csv(bundle/'payload/cohort_fx/cohort_currency_detail.csv')
    allocation = provenance.read_csv(bundle/'payload/cohort_fx/cohort_currency_recognition_weights.csv')
    dgroups, agroups = defaultdict(list), defaultdict(list)
    for row in detail:
        dgroups[row['scenario']].append(row)
    for row in allocation:
        agroups[(row['scenario'],row['booking_quarter'],row['currency'])].append(row)
    checks, diagnostics = [], []
    def close(actual, expected, label, tolerance=1.0):
        error = abs(actual-expected)
        if error > tolerance:
            raise ValueError(f'Source accounting identity failed {label}: {error}')
        return error
    for s in summaries:
        ds = dgroups[s['scenario']]
        if len(ds) != 14 or s['quarter'] != '2026Q3':
            raise ValueError('Unexpected source scenario scope')
        ref, booking, retimed, delta, multiplier = [number(s[k]) for k in
            ('reference_revenue_usd','booking_revenue_usd','retimed_revenue_usd','incremental_replacement_usd','replacement_multiplier')]
        errors = [close(sum(number(d['reference_contribution_usd']) for d in ds),ref,'reference'),
                  close(sum(number(d['booking_contribution_usd']) for d in ds),booking,'booking'),
                  close(sum(number(d['retimed_contribution_usd']) for d in ds),retimed,'retimed'),
                  close(retimed-booking,delta,'incremental'),
                  close(booking*multiplier,retimed,'T/B multiplier')]
        close(sum(number(d['w_reference']) for d in ds),1.,'reference weights',1e-9)
        close(sum(number(d['w_reference'])*number(d['rnpl_share']) for d in ds),number(s['rnpl_weight']),'RNPL weighted share',1e-9)
        for d in ds:
            c0, w, u, fb = [number(d[k]) for k in ('reference_contribution_usd','w_reference','rnpl_share','booking_fx_factor')]
            errors.extend([close(c0*fb,number(d['booking_contribution_usd']),'C0*f_booking'),
                           close(w*ref,c0,'w=C0/R0')])
            alloc = agroups[(s['scenario'],d['booking_quarter'],d['currency'])]
            close(sum(number(a['p']) for a in alloc),1.,'conditional p',1e-9)
            retime_factor = sum(number(a['p'])*number(a['timing_fx_factor']) for a in alloc)
            errors.append(close(c0*((1-u)*fb+u*retime_factor),number(d['retimed_contribution_usd']),'C0*((1-u)f_booking+u E[f])'))
        checks.append({'scenario':s['scenario'],'quarter':s['quarter'],'n_cohort_currency_rows':len(ds),
                       'n_allocation_rows':sum(len(agroups[(s['scenario'],d['booking_quarter'],d['currency'])]) for d in ds),
                       'maximum_identity_error_usd':max(errors),'tolerance_usd':1.,'result':'PASS',
                       'interpretation':'Reconciles rounded source exports only; no hedge or structural identification certification'})
        if number(s['foreign_usd_multiplier'])==1 and number(s['assumed_nonusd_reported_share'])==.56 and number(s['assumed_rnpl_revenue_share'])==.2:
            diagnostics.append({**s,'l4_disposition':'isolated_Q3_conditional_source_diagnostic_only',
                                'financial_application':'ineligible','m_pre':'','H_usd':'','H_new_usd':'',
                                'reason':'T/B is not certified pre-hedge; no H split; u20/nonUSD56/timing are assumptions; not a central effect'})
    return checks, diagnostics


def interface_rows():
    definitions = [
        ('reported_currency_contribution','C_bc=lambda*a_b*GBV_reported_b*s_bc','USD','Assumed reported-dollar currency shares; USD GBV already embeds booking FX','conditional'),
        ('reference_currency_GBV','GBV0_bc=GBV_reported_b*s_bc/(e_booking_bc/e0_c)','USD at fixed 2025 daily-average reference','Not observed company constant-currency GBV; s and booking fixing convention assumed','conditional'),
        ('reference_revenue','C0_bc=C_bc/f_booking_bc; R0=sum_bc C0_bc','USD at fixed reference','Lambda inherits reported revenue, including unidentified hedge effects','not_certified_prehedge'),
        ('backward_contribution_share','w_bc=C0_bc/sum_bc C0_bc','fraction of target reference revenue','Denominator is target-quarter reference revenue across all booking/currency cohorts; not reported GBV or forward cohort total','conditional'),
        ('rnpl_cohort_share','u_bc=C0_RNPL_bc/C0_bc','fraction of cohort/currency reference revenue','Surviving recognized-revenue contribution sensitivity; neither unpaid balance stock nor booked RNPL flow','unidentified'),
        ('rnpl_total_share','sum_bc w_bc*u_bc','fraction of target reference revenue','Reference-dollar denominator; not empirical recognition-cohort exposure','conditional'),
        ('recognition_allocation','sum_m p_bc,m=1 within each booking/currency RNPL group','fraction conditional on cohort/currency RNPL','Recognition-month fixing is a hypothesis; prior-month row is separate payment/fixing proxy','conditional'),
        ('source_denominator','B=sum_bc C0_bc*f_booking_bc','USD','Reconstructs reported-USD K0 Q3 baseline; embedded hedges unresolved','not_certified_prehedge'),
        ('source_numerator','T=sum_bc C0_bc*((1-u_bc)*f_booking_bc+u_bc*sum_m p_bc,m*f_m,c)','USD','Counterfactual fixing on unchanged survival/demand; no new hedge contribution','conditional'),
        ('source_multiplier','m_source=T/B','dimensionless','Can be checked arithmetically; cannot relabel as m_pre with unresolved hedge basis','ineligible_for_current_L4'),
        ('reference_level_factor','T/R0','dimensionless','Never multiply reported USD kernel by full reference factor; booking FX already included','rejected_reported_kernel_overlay'),
        ('required_prehedge_multiplier','m_pre=R_pre,new/R_pre,baseline','dimensionless','Numerator/denominator must be independently certified pre-hedge and match source cohorts/currencies','unavailable'),
        ('H','Revenue cash-flow hedge reclassification embedded in R at the target quarter','USD same quarter and accounting scope as R','Signed revenue contribution; not hedge notional, total AOCI or future-12-month disclosure','unavailable'),
        ('H_new','Revenue hedge contribution under the new same-quarter scenario','USD same quarter and accounting scope as R','Must be supplied explicitly; H_new=H is a named unchanged-hedge assumption','unavailable'),
        ('financial_application','R_new=m_pre*(R-H)+H_new','USD','Current accepted bundle lacks required pre-hedge/H inputs; missing is never zero','ineligible_for_current_L4'),
        ('unchanged_hedge_case','H_new=H; delta_R=(m_pre-1)*(R-H)','USD','Explicit assumption only after H and m_pre are known; multiplying R scales existing hedges incorrectly','conditional_future_contract'),
        ('forward_vs_backward_denominator','Backward C[b,t]/sum_b C[b,t] differs from forward C[b,t]/sum_t C[b,t]','fraction','No current global fee-weighted ledger maps these denominators; QVS support, no new fit','unidentified')]
    return [{'concept':name,'formula_or_definition':formula,'units':units,'limit':limit,
             'eligibility':status,'source':'bundle/research_notes/L3_COHORT_FX_ACCOUNTING.md; bundle/payload/cohort_fx/metadata.json; L4_INTEGRATION_PREREG_v2.md; qvs/QVS_VARIANCE_AND_PRESENTATION_ARGUMENTS_v1.md'}
            for name,formula,units,limit,status in definitions]


def baseline_compatibility(out, bundle):
    data = provenance.object_bytes(L4_BASE_COMMIT,[L4_BASE_PATH])[L4_BASE_PATH]
    provenance.bytes_new(out/'baseline/forecast.csv',data)
    provenance.json_new(out/'baseline/manifest.json',{'commit':L4_BASE_COMMIT,'path':L4_BASE_PATH,'sha256':provenance.sha(data)})
    baseline = provenance.read_csv(out/'baseline/forecast.csv')
    source = provenance.read_csv(bundle/'payload/cohort_fx/scenario_summary.csv')
    source_values = {number(s['booking_revenue_usd']) for s in source}
    if len(source_values)!=1:
        raise ValueError('Source ordinary baseline not unique')
    source_r = source_values.pop()
    kernel = provenance.read_csv(bundle/'payload/cohort_fx/kernel_inputs.csv')
    lagged = [k for k in kernel if k['quarter']=='2026Q3']
    weighted_gbv = sum(number(k['kernel_coefficient'])*number(k['gbv_reported_usd']) for k in lagged)
    source_lambda = number(lagged[0]['lambda_pct'])
    rows=[]
    for r in baseline:
        covered = r['quarter']=='2026Q3'
        r_usd = number(r['revenue_musd'])*1e6
        diff = r_usd-source_r if covered else None
        matched = covered and abs(diff)<1 and abs(number(r['kernel_base_musd'])*1e6-weighted_gbv)<1 and abs(number(r['lambda_pct'])-source_lambda)<1e-8
        rows.append({'l4_scenario':r['scenario'],'quarter':r['quarter'],'l4_revenue_usd':r_usd,
                     'source_ordinary_revenue_usd':source_r if covered else '',
                     'baseline_difference_usd':diff if covered else '',
                     'quarter_coverage':'MATCH_Q3' if covered else 'NO_SOURCE_TARGET',
                     'reported_kernel_identity_match':matched,'prehedge_match':False,'H_usd':'','H_new_usd':'',
                     'financial_application_eligible':False,
                     'reason':'Q3 reported kernel identity matches within source export precision, but no pre-hedge/H split and no measured cohort shares' if matched else
                     'Q4/Q1 source scenario, reference-GBV/currency cohorts and matching pre-hedge/hedge contract absent; no extrapolation',
                     'source':'bundle/payload/cohort_fx/kernel_inputs.csv; scenario_summary.csv; baseline/forecast.csv'})
    return rows


def audit(out):
    if (out/'accounting_eligibility.json').exists() or (out/'row_dispositions.csv').exists():
        raise FileExistsError('Audit output already exists; choose a new run')
    bundle=out/'bundle'
    provenance.verify_bundle(bundle)
    rows=dispositions(bundle)
    arithmetic,diagnostics=source_arithmetic(bundle)
    compatibility=baseline_compatibility(out,bundle)
    provenance.csv_new(out/'row_dispositions.csv',rows)
    provenance.csv_new(out/'fx_arithmetic_checks.csv',arithmetic)
    provenance.csv_new(out/'fx_isolated_diagnostics.csv',diagnostics)
    provenance.csv_new(out/'cohort_baseline_compatibility.csv',compatibility)
    provenance.csv_new(out/'accounting_interface.csv',interface_rows())
    status={
        'source_integrity':'ACCEPTED_VERIFIED_COMMITTED_BUNDLE',
        'conversion_validation':'COMPLETE_ACCEPTED_AFTER_INDEPENDENT_REVIEW',
        'free_weight_promotion':'FAIL_BOTH_MATCHED_W1_W2',
        'operational_conversion':'RETAIN_EXISTING_FIXED_2OVER3_K0_SEASONAL_POLICY',
        'all22_OLS_status':'DESCRIPTIVE_ONLY_FREE_AND_FIXED_JOINT_COEFFICIENTS_NOT_ADOPTED',
        'fx_research':'ACCEPTED_CONDITIONAL_IMPLEMENTATION_PARTIAL_IDENTIFICATION',
        'central_fx_financial_eligibility':False,
        'fx_integration_status':'ACCEPTED_SOURCE_NOT_ELIGIBLE_FOR_CURRENT_FINANCIAL_APPLICATION',
        'estimated_incremental_fx_musd':None,
        'retained_baseline':'Existing reported-USD kernel remains unchanged; this does not estimate economic FX effect as zero',
        'fx_source_current_target_quarters':['2026Q3'],
        'fx_source_historical_comparator_quarters':['2025Q3'],
        'fx_no_extrapolation_quarters':['2026Q4','2027Q1'],
        'failed_compatibility_conditions':['Source T/B denominator not certified pre-hedge',
           'Baseline signed revenue hedge H unavailable','Scenario H_new unavailable; H_new=H has not been silently assumed',
           'Reference GBV/currency contribution shares and RNPL recognition shares are conditional, not measured',
           'Q4/Q1 target-specific cohort, rate and replacement inputs absent'],
        'source_formula':'B=sum(C0*f_booking); T=sum(C0*((1-u)*f_booking+u*sum(p*f_recognition))); m_source=T/B',
        'required_application':'R_new=m_pre*(R-H)+H_new; only on matching certified pre-hedge, reference and cohort bases',
        'fee_theta':'UNAVAILABLE_0_OF_6_SCHEDULED_CAPTURES_AT_FROZEN_SNAPSHOT',
        'nclh':'TRANSFER_FAIL_NO_ABNB_ADJUSTMENT','hotel':'COMPARATOR_ONLY_ACTUAL_PRODUCTION_UNAVAILABLE',
        'adr':'COHERENT_REPLACEMENT_SCENARIOS_ONLY_FX_AND_FEE_ALREADY_EMBEDDED',
        'n_rows':len(rows),'disposition_counts':dict(Counter(r['integration_disposition'] for r in rows)),
        'source_measurement_counts':dict(Counter(r['source_measurement_class'] for r in rows)),
        'observed_row_note':'No l4_inputs row is a raw directly observed ABNB revenue-cohort parameter; observed raw rates/indices are separate payload inputs',
        'n_fx_scenario_arithmetic_checks':len(arithmetic),'n_isolated_Q3_timing_diagnostics':len(diagnostics),
        'n_baseline_rows':len(compatibility),'n_reported_Q3_identity_matches':sum(r['reported_kernel_identity_match'] for r in compatibility),
        'n_financially_eligible_fx_baselines':sum(r['financial_application_eligible'] for r in compatibility),
        'new_fitted_parameters':0,'statistical_refits':0,'optional_supplements_accepted':0,
        'source_claims_only':'Integrity and arithmetic checks do not repeat independent research validation or adopt investment conclusions'}
    provenance.json_new(out/'accounting_eligibility.json',status)
    files=[p for p in out.rglob('*') if p.is_file()]
    provenance.json_new(out/'snapshot_checksums.json',{p.relative_to(out).as_posix():provenance.sha(p.read_bytes()) for p in sorted(files)})
    return status
