"""R15 revision 2 (A12 audit response, 2026-09-17): P(by the Feb 2027 print management quantifies the 2026 World Cup's contribution at <=1pt,
or states it was immaterial / not meaningful). Pure arithmetic. Writes r15_v2_event_record.csv, r15_v2_base_rate.csv, r15_v2_tree.csv, r15_v2_sensitivity.csv.
Revision-1 r15_model.py and its CSVs are left untouched.
Changes vs revision 1 (finding ids in research-log.md section 10):
  A12-08  base rate rebuilt from the coded record (no "1 - 0.95^2"); the record-implied rate is published, then cut for the reasons below
  A12-09  the slot argument: qualifying size language appeared only in the event's run-up / own-quarter letters (Paris: 1Q24, 2Q24); the World Cup's
          equivalent slots (4Q25 preview, 1Q26, 2Q26) have passed silently; the one post-event lap precedent (3Q25) was framed as a headwind
  missed  the 1Q24 letter carries a second, stronger line ("insignificant to the total nights booked in a region") the audit's phrase list did not catch:
          size language is 2 of 8 discussions, not 1 of 8
  A12-23  the 4Q25 "incremental but not primary growth" line is a site summary bullet, not a transcript quote (marked, kept out of the size-language count)
  A12-22  anchor null (no external anchor); C05 0.28 (rev 2), R08 0.15, R09 0.25 are labelled sibling comparisons
"""
import csv, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# print, event, slot (pre = run-up, own = event quarter, post = after / lap), points figure?, qualifying size language?, note
rec = [("1Q24 letter/call", "Paris 2024 / Euro Cup / eclipse", "pre", "no points", "YES: 'the impact of a single city for a limited duration is insignificant to the total nights booked in a region' (1Q24 letter, EMEA)", "nights booked 5x / 2x; 500k eclipse guests; listings +40%"),
       ("2Q24 letter/call", "Paris 2024", "own", "no points", "YES: 'relatively small compared to the total nights booked in a region' (2Q24 letter, EMEA)", "nights >2x; 400k-430k guests; listings +37%"),
       ("3Q24 letter/call", "Paris 2024", "post", "no points", "none", "'slight acceleration in EMEA buoyed by the Games'; 700k guests; supply +35%"),
       ("4Q24 call", "Paris 2024", "post", "no points", "none", "700k guests; 100k->150k homes"),
       ("3Q25 letter", "Paris lap", "post (lap)", "no points", "none (headwind framing: 'slightly unfavorable year-over-year comparison')", ""),
       ("4Q25 call", "World Cup / Milan preview", "pre", "no points", "none", "'biggest event on Earth'; Anmuth asked for event tailwinds, no size given; the 'incremental but not primary growth' phrase is a SITE SUMMARY bullet in the mirrored transcript, not management's words (A12-23)"),
       ("1Q26 letter/call", "Milan 2026 / World Cup", "pre", "no points", "none", "200k guests, supply +30%, GBV >3x in host markets; 'largest event in Airbnb's history'; Q&A (Nick Jones) qualitative"),
       ("2Q26 letter/call", "World Cup", "own", "no points", "none ('bookings from any single event may be temporary' is duration, not size: convention 3)", "'millions of guest arrivals', 150k first-time listings; 'no single product'")]
with open('r15_v2_event_record.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['print', 'event', 'slot', 'points_figure', 'size_language', 'other_statements']); w.writerows(rec)
n = len(rec); n_pts = sum(1 for r in rec if r[3] != 'no points'); n_size = sum(1 for r in rec if r[4].startswith('YES'))
pre_own = [r for r in rec if r[2] in ('pre', 'own')]; post = [r for r in rec if r[2].startswith('post')]
wc_pre_own = [r for r in pre_own if 'World Cup' in r[1]]
rows = []
def lap(k, m): return (k + 1) / (m + 2)
rows.append(('event discussions coded', n)); rows.append(('with a points figure', n_pts)); rows.append(('with qualifying size language', n_size))
rows.append(('Laplace points per discussion', round(lap(n_pts, n), 4))); rows.append(('Laplace size language per discussion', round(lap(n_size, n), 4)))
rows.append(('raw size-language rate per discussion', round(n_size / n, 4)))
p_raw2 = 1 - (1 - n_size / n) ** 2; p_lap2 = 1 - (1 - lap(n_size, n)) ** 2
rows.append(('record-implied over two prints, raw (A12-08)', round(p_raw2, 4))); rows.append(('record-implied over two prints, Laplace', round(p_lap2, 4)))
rows.append(('size language in pre/own-quarter slots', '%d of %d (Paris 1Q24, 2Q24)' % (sum(r[4].startswith('YES') for r in pre_own), len(pre_own))))
rows.append(('size language in post-event / lap slots', '%d of %d' % (sum(r[4].startswith('YES') for r in post), len(post))))
rows.append(('World Cup pre/own slots already passed without size language', '%d of %d (4Q25 preview, 1Q26, 2Q26)' % (sum(r[4].startswith('YES') for r in wc_pre_own), len(wc_pre_own))))
# slot-conditioned hazard for the two remaining (post-event) prints: post-event record 0 of 3, shrunk toward the pooled rate 2/8 with a prior weight of 2 discussions
h_post = (0 + (n_size / n) * 2) / (len(post) + 2)
p_base_size = 1 - (1 - h_post) ** 2
p_base_points = 1 - (1 - 0.02) * (1 - 0.03)   # a <=1pt points figure has never been given for any event (0 of 8); priced at 0.02 (Nov) / 0.03 (Feb)
p_base = 1 - (1 - p_base_size) * (1 - p_base_points)
rows.append(('post-event per-print size-language hazard (0/3 shrunk to pooled 2/8, prior weight 2)', round(h_post, 4)))
rows.append(('base rate: size language over two post-event prints', round(p_base_size, 4)))
rows.append(('base rate: points route over two prints (0.02 / 0.03)', round(p_base_points, 4)))
rows.append(('base_rate_estimate (either route)', round(p_base, 4)))
with open('r15_v2_base_rate.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['item', 'value']); w.writerows(rows)
# tree (decomposition), re-priced with the slot argument
p = {'A_nov_points_le1': 0.02,   # a <=1pt WC figure for 2Q/3Q26 at 5 Nov: never done for an event (0/8); management just closed the bundle attribution ('no single product')
     'A_feb_points_le1': 0.04,   # a quantified <=1pt 2Q27 lap in the Feb FY27 framing: laps have been qualitative; the Middle-East '~100bps' is the only exogenous-drag precedent
     'B_nov_immaterial': 0.06,   # 'not a meaningful driver' at 5 Nov: needs an analyst ask on the Q3 air pocket (team base case is a decelerating Q3, R01 rev 2 P(<10) 0.61) and the 2Q24 vocabulary; post-event record 0/3
     'B_feb_immaterial': 0.08}   # same at Feb, when the FY27 outlook and the 2Q27 comp are written: the incentive to defuse the comp before the May guide; the 3Q25 precedent chose 'headwind' over 'small'
def tot(**kw):
    q = dict(p); q.update(kw); v = 1.0
    for x in q.values(): v *= (1 - x)
    return 1 - v
p_any = tot()
with open('r15_v2_tree.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['route', 'p'])
    for k, v in p.items(): w.writerow([k, v])
    w.writerow(['P_yes_any_route', round(p_any, 4)]); w.writerow(['nov_print_any', round(1 - (1 - p['A_nov_points_le1']) * (1 - p['B_nov_immaterial']), 4)]); w.writerow(['feb_print_any', round(1 - (1 - p['A_feb_points_le1']) * (1 - p['B_feb_immaterial']), 4)])
sens = [('base', {}),
        ('lenient resolver: duration / "relatively small"-style repeats count (B routes x1.8)', dict(B_nov_immaterial=0.11, B_feb_immaterial=0.14)),
        ('strict resolver: only explicit "not material / meaningful to growth" (B routes /2)', dict(B_nov_immaterial=0.03, B_feb_immaterial=0.04)),
        ('management turns numeric on the 2027 laps (Feb points 0.10)', dict(A_feb_points_le1=0.10)),
        ('3Q26 decelerates sharply and analysts press for attribution (Nov routes x2)', dict(A_nov_points_le1=0.04, B_nov_immaterial=0.12)),
        ('3Q26 accelerates; no attribution pressure (Nov routes /2)', dict(A_nov_points_le1=0.01, B_nov_immaterial=0.03)),
        ('WC figure given but >1pt (resolves No; A routes 0)', dict(A_nov_points_le1=0.0, A_feb_points_le1=0.0)),
        ('Paris pre/own-quarter rate applied to both remaining prints (2 of 5 = 0.4 per print)', dict(B_nov_immaterial=0.40, B_feb_immaterial=0.40)),
        ('joint bull (lenient, numeric, pressed)', dict(A_nov_points_le1=0.04, A_feb_points_le1=0.10, B_nov_immaterial=0.14, B_feb_immaterial=0.16)),
        ('joint bear (strict, no numbers, no ask)', dict(A_nov_points_le1=0.01, A_feb_points_le1=0.02, B_nov_immaterial=0.02, B_feb_immaterial=0.04))]
with open('r15_v2_sensitivity.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['case', 'p_yes'])
    for name, kw in sens: w.writerow([name, round(tot(**kw), 4)])
for fn in ['r15_v2_base_rate.csv', 'r15_v2_tree.csv', 'r15_v2_sensitivity.csv']: print(open(fn).read())
