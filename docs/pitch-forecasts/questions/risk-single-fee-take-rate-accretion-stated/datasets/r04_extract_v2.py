"""R04 revision 2 - extraction script for the statement record (audit A10-15) and the decomposition with the blending rule stated
(A10-14), 2Q26 rescored No (A10-04), two-print base rate as a dependence range (A10-05). stdlib + pandas. Run from the repo root:
py -3.13 docs/pitch-forecasts/questions/risk-single-fee-take-rate-accretion-stated/datasets/r04_extract_v2.py
Writes r04_statement_hits_v2.csv (verbatim sentence hits, machine-extracted), r04_statement_record_v2.csv (quoted, parseable,
hand-classified) and r04_decomposition_v2.csv. Revision-1 files are left in place."""
from pathlib import Path
import re, html, csv
import pandas as pd
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[4]
LET = {"3Q25":"3Q25_d40503dex991.htm","4Q25":"4Q25_d58192dex991.htm","1Q26":"1Q26_d23351dex991.htm","2Q26":"2Q26_d70413dex991.htm"}
KW = ["take rate","single service fee","single fee","simplified fee","fee structure","host-only","monetization initiative","downward pressure"]
def text(path):
    t = open(path, encoding="utf-8", errors="ignore").read()
    t = re.sub(r"<script.*?</script>", " ", t, flags=re.S); t = re.sub(r"<[^>]+>", " ", t); t = html.unescape(t); return re.sub(r"\s+", " ", t)
def sentences(t):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\"'])", t) if s.strip()]
hits = []
for q, f in LET.items():
    for venue, path in [("letter", ROOT/"data/raw/letters"/f), ("call", ROOT/"data/raw/transcripts/web"/f"{q}.html")]:
        seen = set()
        for s in sentences(text(path)):
            low = s.lower()
            if any(k in low for k in KW) and len(s) < 700 and s not in seen:
                seen.add(s); hits.append({"print": q, "venue": venue, "keywords": ";".join(k for k in KW if k in low), "sentence": s})
pd.DataFrame(hits).to_csv(HERE/"r04_statement_hits_v2.csv", index=False, quoting=csv.QUOTE_ALL)
# hand classification under conventions (1)-(5) of the log, 2Q26 rescored No per A10-04
rec = [
 {"print":"3Q25","date":"2025-11-06","venue":"letter","take_rate_forward_sentence":"implied take rate in Q4 2025 to be relatively flat year-over-year","driver_named":"none (Q3 decline attributed to FX and booking-vs-stay timing)","fee_migration_named_as_positive_to_take_rate_or_revenue":"no","counts_under_convention":"no","rev2_note":"unchanged"},
 {"print":"4Q25","date":"2026-02-12","venue":"letter+call","take_rate_forward_sentence":"implied take rate in Q1 2026 to be up slightly year-over-year; call: modestly above Q1 last year mostly due to some timing consideration","driver_named":"timing","fee_migration_named_as_positive_to_take_rate_or_revenue":"no (fee described as helping hosts price competitively)","counts_under_convention":"no","rev2_note":"unchanged"},
 {"print":"1Q26","date":"2026-05-07","venue":"letter+call","take_rate_forward_sentence":"improvements to monetization through a simplified fee structure and our insurance programs, which are expected to lift our full-year take rate; Q2 up slightly; call: modest upside to our take rate from both the migration to the single fee structure as well as our Insurance Program; slightly higher implied take rate in the back half","driver_named":"simplified fee structure; insurance","fee_migration_named_as_positive_to_take_rate_or_revenue":"yes (explicit, FY26)","counts_under_convention":"yes","rev2_note":"unchanged"},
 {"print":"2Q26","date":"2026-08-06","venue":"letter+call","take_rate_forward_sentence":"implied take rate to remain relatively in-line year-over-year (Q3); call: FY relatively flat, accounting for RNPL timing and higher customer incentives; absent these incentives, we would have anticipated our implied take rate to be slightly higher during the year, driven by our monetization initiatives and execution across our product roadmap","driver_named":"RNPL timing; incentives; monetization initiatives (not enumerated)","fee_migration_named_as_positive_to_take_rate_or_revenue":"no: the fee is named in the call only as 'helped our host price more competitively', a contributor to 'strong growth', and 'in aggregate, has a kind of downward pressure on pricing' - host-pricing and growth framings excluded by convention (5); the accretion sentence enumerates nothing","counts_under_convention":"no [rev 1: marginal yes; rescored per A10-04]","rev2_note":"rescored No"},
]
pd.DataFrame(rec).to_csv(HERE/"r04_statement_record_v2.csv", index=False, quoting=csv.QUOTE_ALL)
chk = pd.read_csv(HERE/"r04_statement_record_v2.csv"); assert len(chk)==4
# decomposition with the blending rule stated
a, b = 0.45, 0.50          # letter route: P(4Q26/FY26 take-rate sentence reads up) x P(fee named as the driver | up)
c, d = 0.75, 0.40          # call route: P(take-rate/fee question asked) x P(answer attributes a positive fee effect | asked); 1 of 3 observed, Laplace 0.40
rho, feb = 0.5, 0.30
L, C = a*b, c*d
ind = L*C; inter = ind + rho*(min(L,C)-ind)   # blending rule: intersection = independence + rho x (min - independence)
union = L + C - inter; total = union + (1-union)*feb
per_print = 1/4                                  # 1Q26 only, of the four prints since the migration began
dec = [("p_4q26_or_fy26_take_rate_sentence_up", a), ("p_fee_named_given_up", b), ("letter_route_5nov", L), ("p_call_question", c), ("p_call_answer_names_fee_positive", d),
       ("call_route_5nov", C), ("overlap_rho", rho), ("blending_rule", "intersection = L*C + rho*(min(L,C) - L*C); union = L + C - intersection"),
       ("independence_intersection", round(ind,6)), ("blended_intersection", round(inter,6)), ("p_yes_5nov", round(union,6)), ("p_yes_feb_given_no_nov", feb), ("p_yes_total_decomposition", round(total,6)),
       ("per_print_base_rate_since_migration (1 of 4, 2Q26 No)", per_print), ("per_print_laplace (1+1)/(4+2)", round(2/6,4)),
       ("two_print_base_perfectly_correlated", per_print), ("two_print_base_independent", round(1-(1-per_print)**2,4)), ("two_print_base_at_rho_0.5 (midpoint)", round(0.5*per_print+0.5*(1-(1-per_print)**2),4)),
       ("rev1_two_print_base_independent_on_0.375", round(1-0.625**2,4))]
pd.DataFrame(dec, columns=["item","value"]).to_csv(HERE/"r04_decomposition_v2.csv", index=False)
print(pd.DataFrame(dec, columns=["item","value"]).to_string()); print(f"\nstatement hits saved: {len(hits)}"); print(pd.DataFrame(hits).groupby(['print','venue']).size())
