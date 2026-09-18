"""Revision-2 supporting datasets for the A04 audit response (C05, C06, C07).
Run from repo root: py -3.13 docs/pitch-forecasts/audits/A04-response-datasets.py
Writes new *_v2 files into the three question folders' datasets/; reads only. Revision-1 files are left untouched."""
import json, csv, pathlib, math
Q = pathlib.Path('docs/pitch-forecasts/questions')
C05, C06, C07 = [Q / s for s in ['bundle-attribution-quantified', 'rnpl-gbv-share-disclosed', 'rnpl-negative-effect-acknowledged']]

# ---- A04-11: Kalshi fixed-point fields -------------------------------------------------------------
s = json.load(open(C05 / 'sources/kalshi_KXABNB-26NOVNEB_20260917T025351Z.json'))
rows = []
for r in sorted(s['markets'], key=lambda x: x['floor_strike']):
    strike = r['floor_strike'] / 1e6
    rows.append(dict(threshold_m=strike, yoy_pct=round((strike / 133.6 - 1) * 100, 2), yes_bid=r['yes_bid_dollars'],
                     yes_ask=r['yes_ask_dollars'], mid=round((float(r['yes_bid_dollars']) + float(r['yes_ask_dollars'])) / 2, 4),
                     last=r['last_price_dollars'], volume_fp=r['volume_fp'], open_interest_fp=r['open_interest_fp'],
                     volume_24h_fp=r['volume_24h_fp'], yes_bid_size_fp=r.get('yes_bid_size_fp'), yes_ask_size_fp=r.get('yes_ask_size_fp'),
                     updated_time=r['updated_time'], fetched_utc='2026-09-17T02:53:51Z',
                     note='updated_time is a batch metadata stamp identical across strikes; volume_24h 0 at every strike; quote freshness not proven either way'))
tot_v = sum(float(r['volume_fp']) for r in s['markets']); tot_oi = sum(float(r['open_interest_fp']) for r in s['markets'])
for d in (C05, C06, C07):
    with open(d / 'datasets/kalshi_q3_nights_implied_v2_2026-09-17.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
        f.write(f"# ladder totals: volume_fp {tot_v:.2f} contracts, open_interest_fp {tot_oi:.2f}; companion file KXABNBA-27FEBNEB is an FY2026 annual nights market (strikes 570-590m), not a Q4 market\n")
print('kalshi v2 written; totals', tot_v, tot_oi)

# ---- A04-05 / A04-06: paired-endpoint bundle bridge, bundle vs RNPL-only branches --------------------
rows = [
    ['branch', 'component', 'low_pts', 'high_pts', 'in_3Q26_yoy_window', 'status', 'source_note'],
    ['bundle', 'NA cancellation redesign + single fee tranche 1 (Oct-Dec 2025)', 0.66, 0.66, 'yes', 'PR #32 fitted allocation of the management net figure', 'D note s2.2: 2.29 NA-points = 0.66 total'],
    ['bundle', 'Ex-NA fee/cancellation leg (40-50% of the 1.75-pt ex-NA bundle)', 0.70, 0.88, 'yes', 'fitted allocation', 'D note s2.5; PAIRED with the next row: the two legs sum to 1.75 at either endpoint'],
    ['bundle', 'Ex-NA RNPL leg (the complement, 60-50% of 1.75)', 1.05, 0.87, 'yes', 'fitted allocation', 'rev-1 summed 0.70+0.87 and 0.88+1.05 (1.57-1.93), which is wrong; the paired sum is 1.75 always'],
    ['bundle', 'Partial-quarter US RNPL residual', 0.30, 0.35, 'yes', 'assumption from launch-date ambiguity', 'docs/rnpl-short-audit/00_SYNTHESIS.md point 2'],
    ['bundle', 'July 2026 eligibility expansion', 0.10, 0.30, 'yes (fresh)', 'assumption, deliberately small', 'D044 unquantified; research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md s2.4'],
    ['bundle', 'Gross legs in window (paired)', 2.81, 3.06, '', 'computed', '0.66+1.75+0.30+0.10 to 0.66+1.75+0.35+0.30'],
    ['bundle', 'Cancellation-propensity drag, y/y-differenced (scenario slice, not a bound)', -0.93, -0.15, 'yes', 'scenario; part may already sit inside the fitted net baseline (D033 is net of cancellation), so the subtraction is an upper bound on the drag', 'D note s2.3 central column; full grid to -1.37'],
    ['bundle', 'Net bundle contribution, scenario-implied under these assumptions', 1.88, 2.91, '', 'computed: 2.81-0.93 to 3.06-0.15; central 2.4-2.6', 'straddles the (a)/(b) boundary; NOT what management could truthfully state (its figure is its own attribution)'],
    ['rnpl_only', 'Ex-NA RNPL leg + US residual + July expansion, gross', 1.27, 1.70, 'yes', 'computed: 0.87+0.30+0.10 to 1.05+0.35+0.30', 'an RNPL-ALONE figure for 3Q26 lands in (c) or low (b) before any drag'],
    ['rnpl_only', 'Net of the same drag slice', 0.34, 1.55, '', 'computed', 'a stated RNPL-alone number would most likely resolve (c); only the three-feature bundle reaches (a)'],
    ['gbv_mapping', 'GBV contribution ran about 1 point above nights in both disclosures (300 vs >200 bp; ~4 vs ~3 pts)', '', '', '', 'descriptive', 'D014, D032; the option thresholds (3.5/2.0 GBV vs 2.5/1.5 nights) are consistent with that gap'],
]
with open(C05 / 'datasets/bundle_3q26_mechanical_contribution_v2.csv', 'w', newline='') as f:
    csv.writer(f).writerows(rows)

# ---- A04-10: C05 state decomposition under three print-state sources -------------------------------
Phi = lambda z: 0.5 * math.erfc(-z / math.sqrt(2))
mu, sd = 9.67, 1.70   # R01's implied distribution, calibrated to P(>=10.0) = 0.42
states = {
    'R01/R02 implied N(9.67,1.70), P(>=10)=0.42 (headline)': [0.42, 1 - 0.42 - Phi((9 - mu) / sd), Phi((9 - mu) / sd)],
    'team normal N(9.5,1.48) (brief rule 6)': [0.3677, 0.2645, 0.3677],
    'rev-1 team/Kalshi blend (withdrawn)': [0.42, 0.30, 0.28],
}
cond = (0.18, 0.30, 0.40)
split = ((0.45, 0.45, 0.10), (0.30, 0.45, 0.25), (0.10, 0.35, 0.55))
rows = [['print_state_source', 'p_ge10', 'p_9_10', 'p_lt9', 'p_quant_given_state', 'split_abc_given_state_and_quant', 'a', 'b', 'c', 'd', 'p_any_quantification']]
for k, st in states.items():
    a = b = c = 0
    for w, q, (sa, sb, sc) in zip(st, cond, split):
        m = w * q; a += m * sa; b += m * sb; c += m * sc
    rows.append([k] + [round(x, 4) for x in st] + [str(cond), str(split), round(a, 4), round(b, 4), round(c, 4), round(1 - a - b - c, 4), round(a + b + c, 4)])
with open(C05 / 'datasets/c05_state_decomposition_v2.csv', 'w', newline='') as f:
    csv.writer(f).writerows(rows)
for r in rows:
    print(r)

# ---- A04-01 / A04-12: C07 classification table and scenario partition ------------------------------
cls = [
    ['statement_type', 'example', 'resolves', 'clause', 'note'],
    ['qualitative tough-comparison / lap sentence', 'tougher comparisons in the back half against the rollout of RNPL (D040); we lapped RNPL in the US', 'No', 'no listed metric named as reduced; describes the prior-year base', 'rev-1 convention 2, kept'],
    ['quantified lap effect on a listed 3Q26/4Q26 metric', 'the RNPL comparison reduced Q3 nights growth by about 2 points', 'Yes', 'quantified negative effect (points) on a reported metric', 'NEW in rev 2 (A04-01): C05 already counts this as a 3Q26 quantification; the two logs now agree'],
    ['statement that the net benefit or lift has declined or moderated, even if still positive', 'the incremental lift from RNPL is smaller now that we have lapped the US launch', 'Yes', 'net benefit has declined', 'NEW in rev 2 (A04-01); a bare lap sentence with no decline in benefit stated is No'],
    ['repeated direction-only timing sentence', 'absent RNPL, unearned fees would have grown year-over-year (D037/D051); take-rate timing (D049/D050)', 'No', 'timing language already on the record before the 2Q26 10-Q; not promoted automatically', 'rev-1 convention 1, kept; resolver risk priced'],
    ['NEW dollar or point quantification of a timing effect', 'RNPL reduced unearned fees by roughly $150M; reduced FCF by about $X', 'Yes', 'quantified negative effect (dollars) on a listed metric', 'kept from rev 1'],
    ['cancellations exceeded expectations or the tested curve', 'cancellation rates have run above what we saw in testing', 'Yes', 'explicit clause', 'kept'],
    ['cancellation-rate figure alone', '17% to 18%', 'No', 'cancellation rate is not a listed metric', 'rev-1 convention 3, kept; Yes only if tied to a listed metric or to expectations'],
    ['terms change motivated by cancellations', 'deposit, shorter deferral, host opt-out, eligibility cut to reduce cancellations', 'Yes', 'explicit clause', 'kept'],
    ['net-positive reiteration; unchanged 10-Q boilerplate; timing described as neutral', 'D033/D035-style; the 2Q26 10-Q sentences verbatim', 'No', 'fine print baseline', 'kept'],
    ['10-Q adds a new clause tying higher cancellations to Nights/GBV (unquantified)', '...which reduced Nights and Seats Booked', 'Yes (weak)', 'statement that RNPL reduced a reported metric, beyond the baseline', 'rev-1 10-Q creep route, kept'],
]
with open(C07 / 'datasets/c07_classification_table_v2.csv', 'w', newline='') as f:
    csv.writer(f).writerows(cls)
p_decel = 0.64   # P(nights < 10.34%): interpolated between R01 P(>=10.0)=0.42 and R02 P(>=10.6)=0.32
part = [
    ['scenario', 'definition', 'p_scenario', 'source_of_p', 'p_yes_given', 'routes_inside', 'contribution'],
    ['S1 adverse RNPL performance', 'realised cancellation curves materially above tested; nights weak with a wide GBV-nights gap; management must explain', 0.15, 'R01 P(<9%) 0.347 x share attributed to RNPL rather than lap/macro/World Cup 0.45 = 0.156; the engine says the y/y drag is small (-0.15 to -0.93, grid to -1.37), so not higher', 0.65, 'above-tested admission 0.45; 10-Q escalation 0.35; quantified drag 0.25; terms change 0.10 (union about 0.65)', round(0.15 * 0.65, 4)],
    ['S2 ordinary performance, decelerating print (<10.34%), not S1', 'the lap explains a deceleration; management may size it or say the lift has moderated', 0.49, 'P(decel) 0.64 minus S1 0.15', 0.27, 'quantified lap 0.12; net-benefit-declined/moderated wording 0.15; new $ timing quantification 0.04; 10-Q creep 0.05; terms change 0.02; resolver counts a repeated timing sentence 0.03 (union about 0.30 before overlap; 0.27 with the lap/moderation overlap)', round(0.49 * 0.27, 4)],
    ['S3 routine or accelerating print (>=10.34%)', 'no explanatory pressure', 0.36, '1 - P(decel)', 0.10, '10-Q creep 0.05; terms change 0.02; resolver risk 0.03; moderation wording in a strong quarter 0.02', round(0.36 * 0.10, 4)],
    ['TOTAL', '', 1.00, '', '', '', round(0.15 * 0.65 + 0.49 * 0.27 + 0.36 * 0.10, 4)],
]
with open(C07 / 'datasets/c07_scenario_partition_v2.csv', 'w', newline='') as f:
    csv.writer(f).writerows(part)
print('C07 total', 0.15 * 0.65 + 0.49 * 0.27 + 0.36 * 0.10)
print('C05 log-score change if d resolves, .72->.70:', math.log(.70 / .72), '; .73->.70:', math.log(.70 / .73))
