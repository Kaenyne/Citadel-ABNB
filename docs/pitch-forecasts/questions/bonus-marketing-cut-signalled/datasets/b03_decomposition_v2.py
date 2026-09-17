"""B03 revision 2 - P(management states at the 5 Nov print that 4Q26/FY27 marketing will grow more slowly than revenue, be moderated/optimised/
reduced, or quantifies a reduction). Audit A14 (A14-01, -08, -09, -19, -20, -21, -24). Standard library + pandas. Run from the repo root:
py -3.13 docs/pitch-forecasts/questions/bonus-marketing-cut-signalled/datasets/b03_decomposition_v2.py
Reads the revision-2 C04 / C09 / R05 forecast JSONs (A14-01), rebuilds the four-path union, the anchor, the blend, the S&M streak (A14-24), the
statement ledger with the 4Q20 quotation re-sourced to the call and a literal-'optimise' column (A14-09, A14-21), and the impact arithmetic with
the stock line computed and its behavioural discount named (A14-08, A14-20). Writes b03_decomposition_v2.csv and b03_marketing_statement_by_print_v2.csv."""
import csv, json
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[4]; Q = HERE.parents[1]
rows = []
c04 = json.load(open(Q/"fy26-margin-sentence/forecasts/2026-09-17-forecast.json")); c09 = json.load(open(Q/"q4-margin-direction-sentence/forecasts/2026-09-17-forecast.json")); r05 = json.load(open(Q/"risk-q3-margin-sandbagged/forecasts/2026-09-17-forecast.json"))
pick = lambda d, k: [v for kk, v in d["final"]["vector"].items() if kk.startswith(k)][0]
A04, B04, D04 = pick(c04, "(a)"), pick(c04, "(b)"), pick(c04, "(d)"); UP09, DOWN09 = pick(c09, "(c)"), pick(c09, "(a)"); P05 = r05["final"]["p"]
rows.append(("inputs on disk: C04 rev, (a), (b), (d); C09 rev, (c) up, (a) down; R05 rev, p", f"{c04['revision']}, {A04}, {B04}, {D04}; {c09['revision']}, {UP09}, {DOWN09}; {r05['revision']}, {P05}"))
# --- four-path union
P_NAMED_GIVEN_UP = 0.30   # marketing named as the slower/lower line given a Q4 'up' sentence (kept; auditor 0.27 inside the sensitivity)
P_QA_2027 = 0.08          # a 2027 leverage answer in Q&A
P_STATED_GIVEN_HOLD = 0.20  # a stated Q4 cut given C04 (a) hold
P_RESOLVER = 0.07         # resolver reads 'optimised'/'efficient' literally (raised from 0.04, A14-09)
OVERLAP = 0.03            # shared floor-at-risk state across the paths
def union(ps):
    u = 1.0
    for p_ in ps: u *= (1 - p_)
    return 1 - u
paths = dict(A=UP09 * P_NAMED_GIVEN_UP, B=P_QA_2027, C=A04 * P_STATED_GIVEN_HOLD, D=P_RESOLVER)
U = union(paths.values()); DECOMP = U - OVERLAP
rows.append(("paths A (C09 up x named) / B (Q&A 2027) / C (C04 hold x stated) / D (resolver)", " / ".join(f"{k} {v:.3f}" for k, v in paths.items())))
rows.append(("union / less 0.03 shared-state overlap = decomposition", f"{U:.3f} / {DECOMP:.3f}"))
rows.append(("rev-1 union on rev-1 inputs (0.40 x 0.30, 0.08, 0.26 x 0.20, 0.04)", f"{union([0.12, 0.08, 0.052, 0.04]):.3f}"))
rows.append(("rev-2 inputs with rev-1 conditionals (0.47 x 0.30, 0.08, 0.33 x 0.20, 0.04)", f"{union([UP09*0.30, 0.08, A04*0.20, 0.04]):.3f}"))
# --- anchor and base rate
ANCHOR_RAW = 0.5 * A04 + 0.25 * B04; ANCHOR = 0.22
rows.append(("anchor: 0.5 x C04(a) + 0.25 x C04(b) raw; shaded for the no-line-names habit", f"{ANCHOR_RAW:.3f}; {ANCHOR}"))
BASE = 0.09
rows.append(("base rate: 4/23 (0.17), 1/18 since 1Q22 (Laplace 0.10), 0/10 since 1Q24 (Laplace 0.08), 0/5 Novembers; regime-conditioned", BASE))
# --- blend
W = (0.45, 0.35, 0.20); FINAL_RAW = W[0] * DECOMP + W[1] * BASE + W[2] * ANCHOR; FINAL = 0.20
rows.append(("blend 0.45 x decomposition + 0.35 x base rate + 0.20 x anchor", f"{FINAL_RAW:.4f} -> {FINAL}"))
scale = FINAL / DECOMP
# conditionals (decomposition conditionals scaled by final/decomposition)
rows.append(("P(Yes | C09 up) / (C09 down): decomposition union, scaled", f"{union([P_NAMED_GIVEN_UP, P_QA_2027, A04*P_STATED_GIVEN_HOLD, P_RESOLVER])-OVERLAP:.3f} -> {(union([P_NAMED_GIVEN_UP, P_QA_2027, A04*P_STATED_GIVEN_HOLD, P_RESOLVER])-OVERLAP)*scale:.2f} / {union([P_QA_2027, A04*P_STATED_GIVEN_HOLD, P_RESOLVER])-OVERLAP:.3f} -> {(union([P_QA_2027, A04*P_STATED_GIVEN_HOLD, P_RESOLVER])-OVERLAP)*scale:.2f}"))
rows.append(("P(Yes | C04 a hold) / (b) / (d): scaled", f"{(union([paths['A'], P_QA_2027, P_STATED_GIVEN_HOLD, P_RESOLVER])-OVERLAP)*scale:.2f} / {(union([paths['A'], P_QA_2027, 0.0, P_RESOLVER])-OVERLAP)*scale:.2f} / {(union([paths['A']*0.6, P_QA_2027, 0.0, P_RESOLVER])-OVERLAP)*scale:.2f}"))
rows.append(("P(Yes | R05 Yes, Q3 step slipped into Q4: C09 up 0.40 (C09 s7), named 0.20): scaled", f"{(union([0.40*0.20, P_QA_2027, A04*P_STATED_GIVEN_HOLD*0.5, P_RESOLVER])-OVERLAP)*scale:.2f}"))
# --- sensitivities (final = blend with the changed decomposition; base/anchor held)
def fin(dec, base=BASE, anchor=ANCHOR): return W[0] * dec + W[1] * base + W[2] * anchor
sens = [("P(named | up) 0.15", union([UP09*0.15, P_QA_2027, paths['C'], P_RESOLVER])-OVERLAP), ("P(named | up) 0.27 (auditor)", union([UP09*0.27, P_QA_2027, paths['C'], P_RESOLVER])-OVERLAP), ("P(named | up) 0.50", union([UP09*0.50, P_QA_2027, paths['C'], P_RESOLVER])-OVERLAP),
        ("C09 up 0.30", union([0.30*P_NAMED_GIVEN_UP, P_QA_2027, paths['C'], P_RESOLVER])-OVERLAP), ("C09 up 0.60", union([0.60*P_NAMED_GIVEN_UP, P_QA_2027, paths['C'], P_RESOLVER])-OVERLAP),
        ("Q&A 2027 path 0.03", union([paths['A'], 0.03, paths['C'], P_RESOLVER])-OVERLAP), ("Q&A 2027 path 0.15", union([paths['A'], 0.15, paths['C'], P_RESOLVER])-OVERLAP),
        ("resolver path 0.04 (rev 1)", union([paths['A'], P_QA_2027, paths['C'], 0.04])-OVERLAP), ("resolver path 0 (strict conventions)", union([paths['A'], P_QA_2027, paths['C'], 0.0])-OVERLAP), ("resolver path 0.30 (literal 'optimise/efficient' reading)", union([paths['A'], P_QA_2027, paths['C'], 0.30])-OVERLAP)]
for lab, dec in sens: rows.append((f"sens decomposition {lab}: decomposition / final", f"{dec:.3f} / {fin(dec):.3f}"))
rows.append(("sens base rate 4/23 = 0.17: final", f"{fin(DECOMP, base=0.17):.3f}")); rows.append(("sens base rate 0.05 (0/10 literal): final", f"{fin(DECOMP, base=0.05):.3f}"))
rows.append(("sens anchor unshaded 0.24: final", f"{fin(DECOMP, anchor=ANCHOR_RAW):.3f}")); rows.append(("sens weights 0.6/0.2/0.2: final", f"{0.6*DECOMP+0.2*BASE+0.2*ANCHOR:.3f}")); rows.append(("sens weights 0.3/0.5/0.2: final", f"{0.3*DECOMP+0.5*BASE+0.2*ANCHOR:.3f}"))
# --- S&M streak (A14-24)
cl = pd.read_csv(ROOT/"data/processed/abnb_quarterly_costlines.csv").set_index("quarter")
qs = ["3Q22","4Q22","1Q23","2Q23","3Q23","4Q23","1Q24","2Q24","3Q24","4Q24","1Q25","2Q25","3Q25","4Q25","1Q26","2Q26"]; run = 0; streak = []
for i in range(4, len(qs)):
    a, b = qs[i], qs[i-4]
    if a not in cl.index or b not in cl.index: continue
    s = 100*(cl.loc[a,"sales_and_marketing_musd"]/cl.loc[b,"sales_and_marketing_musd"]-1); r = 100*(cl.loc[a,"revenue_musd"]/cl.loc[b,"revenue_musd"]-1)
    run = run + 1 if s > r else 0; streak.append(f"{a} S&M {s:+.1f} rev {r:+.1f} {'F' if s>r else 's'}")
rows.append(("S&M faster than revenue: consecutive quarters to 2Q26 (rev 1 said eight)", run)); rows.append(("S&M vs revenue y/y 3Q23-2Q26", "; ".join(streak)))
# --- statement ledger v2 (A14-21: 4Q20 'below 2019' sentence is in the CALL; A14-09: literal optimise/moderate column)
led = list(csv.DictReader(open(HERE/"b03_marketing_statement_by_print.csv", encoding="utf-8")))
LITERAL = {"2Q23", "3Q23", "4Q23", "1Q24", "3Q24"}   # letters carrying 'as we optimize the channel and audience mix' (present tense, channel mix, not spend)
for r in led:
    r["literal_optimise_mention_letter"] = int(r["print_quarter"] in LITERAL)
    if r["print_quarter"] == "4Q20":
        r["statement_verbatim_or_paraphrase"] = ("LETTER: 'S&M as a percentage of revenue in the first half of 2021 will be higher than that of the second half'; "
                                                 "CALL (4Q20, verbatim): 'Our sales and marketing expenses as a percentage of revenue in 2021 will be below that of 2019'")
        r["note"] = "seasonal 1H>2H (letter) plus FY21 % of revenue below 2019 (call, verified verbatim A14-21): qualifies (slower than revenue over the year)"
with open(HERE/"b03_marketing_statement_by_print_v2.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(led[0].keys())); w.writeheader(); w.writerows(led)
rows.append(("ledger: Yes prints / distinct events (the 2021 sentence repeated 3x = 1) / literal 'optimize the channel and audience mix' letters / of the last 8", f"{sum(int(r['yes']) for r in led)} / 2 / {len(LITERAL)} / 0"))
# --- impact (A14-08, A14-20)
FY26_REV, FY27_REV, SH, EPS_PER_M = 14268.1, 15828.6, 591.7, 0.0014
cut_q4 = 177.0; m26_direct = cut_q4 / FY26_REV * 100
m27_mkt = 2 * 0.669308  # 2x linear extrapolation of the +5pt marketing-growth step (-0.669pp) - labelled
d_n4 = -0.3; r4 = d_n4 * 30; r27 = -50.0
ebitda27 = m27_mkt / 100 * FY27_REV + r27 * 0.66; m27_net = ebitda27 / FY27_REV * 100
eps27 = ebitda27 * EPS_PER_M
level_16x = ebitda27 * 16 / SH; pe27 = eps27 * 27; growth = d_n4 * 0.44 * 9.5
rows.append(("impact: FY26 margin pp direct ($177M Q4 cut) / FY27 marketing +5% vs +15% pp (2x extrapolation of 40_sensitivities) / FY27 EBITDA $M net of revenue / FY27 margin pp net / FY27 EPS $", f"{m26_direct:+.2f} / {m27_mkt:+.2f} / {ebitda27:+.0f} / {m27_net:+.2f} / {eps27:+.3f}"))
rows.append(("impact: 4Q26 nights pt (judgement) / 4Q26 revenue $M / FY27 revenue $M", f"{d_n4:+.1f} / {r4:+.0f} / {r27:+.0f}"))
rows.append(("stock: level 16x EV/EBITDA $ / P/E 27x route $ / growth read -0.3pt x 0.44 x 9.5 $ / mechanical net (16x route) $ / (27x route) $", f"{level_16x:+.2f} / {pe27:+.2f} / {growth:+.2f} / {level_16x+growth:+.2f} / {pe27+growth:+.2f}"))
STOCK = 3.5
rows.append(("stock published: mechanical +3.5 (16x route); named behavioural discount 'growth capitulation read' sized 0 to -5 -> range -1.5 to +5.6; EV at 0.20", f"{STOCK:+.1f}; EV {FINAL*STOCK:+.2f}; at 27x route {FINAL*(pe27+growth):+.2f}; at full capitulation discount {FINAL*(level_16x+growth-5):+.2f}"))
rows.append(("R05 rev-2 threshold for the monitoring rule: 3Q26 cash S&M <= $724M = +23.7% y/y (rev 1 quoted $706M / +20.7%, withdrawn)", "A14-19"))
with open(HERE/"b03_decomposition_v2.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["item", "value"]); w.writerows(rows)
for r in rows: print(f"{r[0]}: {r[1]}")
