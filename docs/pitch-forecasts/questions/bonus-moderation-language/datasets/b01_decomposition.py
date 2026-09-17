"""B01 - P(demand-softening language applied to forward demand/bookings at the 5 Nov print).
Standard library only. Run from the repo root:
py -3.13 docs/pitch-forecasts/questions/bonus-moderation-language/datasets/b01_decomposition.py
Inputs: C02 revision-2 joint table (questions/q4-nights-bucket/research-log.md section 6) and its format/content parameters;
the per-print letter classification in b01_letter_language_by_print.csv (this folder)."""
import csv, math
from pathlib import Path
HERE = Path(__file__).resolve().parent
rows = []
# --- 1. base rates from the letter classification
recs = list(csv.DictReader(open(HERE/"b01_letter_language_by_print.csv", encoding="utf-8")))
n = len(recs); strict = sum(int(r["yes_strict"]) for r in recs); syn = sum(int(r["yes_with_synonyms"]) for r in recs)
rows.append(("letters 3Q22-2Q26 n", n)); rows.append(("strict yes / share", f"{strict} / {strict/n:.3f}")); rows.append(("with synonyms yes / share", f"{syn} / {syn/n:.3f}"))
w1 = [r for r in recs if r["print_quarter"] not in ("3Q22","4Q22")]; w2 = [r for r in recs if r["print_quarter"][-2:] in ("24","25","26")]
rows.append(("W1 (1Q23+) strict / syn / n", f"{sum(int(r['yes_strict']) for r in w1)} / {sum(int(r['yes_with_synonyms']) for r in w1)} / {len(w1)}"))
rows.append(("W2 (1Q24+) strict / syn / n", f"{sum(int(r['yes_strict']) for r in w2)} / {sum(int(r['yes_with_synonyms']) for r in w2)} / {len(w2)}"))
down = [r for r in recs if r["descriptor_class"].startswith("down")]; nond = [r for r in recs if not r["descriptor_class"].startswith("down")]
rows.append(("P(strict word | down-class descriptor)", f"{sum(int(r['yes_strict']) for r in down)}/{len(down)} = {sum(int(r['yes_strict']) for r in down)/len(down):.3f}"))
rows.append(("P(strict word | non-down descriptor)", f"{sum(int(r['yes_strict']) for r in nond)}/{len(nond)}; with synonyms {sum(int(r['yes_with_synonyms']) for r in nond)}/{len(nond)}"))
# --- 2. decomposition on the C02 revision-2 tree
# branch masses (R01's N(9.67, 1.70)) and C02's format x content parameters by branch
branches = {">=10": 0.423, "9-10": 0.230, "<9": 0.347}
p_dir = {">=10": 0.25, "9-10": 0.28, "<9": 0.35}; p_none = 0.03
p_mod_given_dir = {">=10": 0.55, "9-10": 0.60, "<9": 0.75}
bucket = {">=10": dict(a=.45, b=.20, c=.30, d=.05), "9-10": dict(a=.08, b=.22, c=.57, d=.13), "<9": dict(a=.02, b=.07, c=.50, d=.41)}
# P(softening language | sentence type). Sources: strict-word share among directional-down sentences 6/8 (with synonyms 7/8) -> 0.85 for a
# directional 'moderate/decelerate' sentence (the word is the sentence, less the 'lower than'/'a few points below' forms);
# mid-single bucket 0.40 (3Q25 precedent 0/1: 'challenging comparison', no word; a bucket that low in a soft print usually carries a reason);
# high-single bucket 0.25 (4Q25 precedent 0/1; the prepared remarks can add 'growth to moderate to high single digits', 'tougher comps'); the
# non-down historical rate with synonyms is 1/8 = 0.125, which is the floor for (b)/(a); directional 'stable/higher' 0.10; no descriptor 0.30.
p_lang = dict(dir_mod=0.85, dir_other=0.10, bucket_a=0.05, bucket_b=0.15, bucket_c=0.25, bucket_d=0.40, none=0.30)
total = 0.0; by_branch = {}; by_option = dict(a=0.0, b=0.0, c=0.0, d=0.0, e=0.0); opt_mass = dict(a=0.0, b=0.0, c=0.0, d=0.0, e=0.0)
for br, m in branches.items():
    pd_, pn = p_dir[br], p_none; pb = 1 - pd_ - pn
    lang = 0.0
    # directional
    dm = pd_ * p_mod_given_dir[br]; do = pd_ * (1 - p_mod_given_dir[br])
    lang += dm * p_lang["dir_mod"] + do * p_lang["dir_other"]
    by_option["d"] += m * dm * p_lang["dir_mod"]; opt_mass["d"] += m * dm
    key = "a" if br == ">=10" else "b"; by_option[key] += m * do * p_lang["dir_other"]; opt_mass[key] += m * do
    # bucket
    for o, w in bucket[br].items():
        lang += pb * w * p_lang["bucket_" + o]; by_option[o] += m * pb * w * p_lang["bucket_" + o]; opt_mass[o] += m * pb * w
    lang += pn * p_lang["none"]; by_option["e"] += m * pn * p_lang["none"]; opt_mass["e"] += m * pn
    by_branch[br] = lang; total += m * lang
rows.append(("decomposition P(Yes)", round(total, 4)))
for br in branches: rows.append((f"P(Yes | 3Q26 print {br})", round(by_branch[br], 3)))
for o in "abcde": rows.append((f"P(Yes and C02={o}) / P(C02={o}) [tree]", f"{by_option[o]:.3f} / {opt_mass[o]:.3f} -> P(Yes|{o}) {by_option[o]/opt_mass[o]:.2f}"))
rows.append(("P(Yes and C02=d) [tree]", round(by_option["d"], 3))); rows.append(("P(Yes and C02!=d) [tree]", round(total - by_option["d"], 3)))
# on the C02 FINAL marginals (0.18/0.17/0.30/0.31/0.04) with the same conditionals (d split 0.19 directional-moderate, 0.12 mid-single)
final_marg = dict(a=0.18, b=0.17, c=0.30, d_dir=0.19, d_mid=0.12, e=0.04)
cond = dict(a=p_lang["bucket_a"], b=p_lang["bucket_b"], c=p_lang["bucket_c"], d_dir=p_lang["dir_mod"], d_mid=p_lang["bucket_d"], e=p_lang["none"])
tot2 = sum(final_marg[k] * cond[k] for k in final_marg); rows.append(("decomposition on C02 final marginals", round(tot2, 4)))
# sensitivities
def run(pl):
    t = 0.0
    for br, m in branches.items():
        pd_, pn = p_dir[br], p_none; pb = 1 - pd_ - pn
        dm = pd_ * p_mod_given_dir[br]; do = pd_ * (1 - p_mod_given_dir[br])
        l = dm * pl["dir_mod"] + do * pl["dir_other"] + sum(pb * w * pl["bucket_" + o] for o, w in bucket[br].items()) + pn * pl["none"]
        t += m * l
    return t
for lab, ch in [("dir_mod 0.70 (Laplace 7/10)", dict(dir_mod=0.70)), ("dir_mod 0.95", dict(dir_mod=0.95)), ("bucket_c 0.10", dict(bucket_c=0.10)), ("bucket_c 0.40", dict(bucket_c=0.40)),
                ("bucket_d 0.20", dict(bucket_d=0.20)), ("bucket_d 0.60", dict(bucket_d=0.60)), ("b/a at the non-down synonym rate 0.125", dict(bucket_b=0.125, bucket_a=0.125, dir_other=0.125))]:
    pl = dict(p_lang); pl.update(ch); rows.append((f"sens: {lab}", round(run(pl), 3)))
# branch-mass sensitivities (Street view / external stack), C02 section 7 row 1
for lab, bm in [("Street/Kalshi N(11.0,1.7): .72/.16/.12", {">=10": .72, "9-10": .16, "<9": .12}), ("external stack N(9.2,1.7): .32/.24/.44", {">=10": .32, "9-10": .24, "<9": .44}), ("team baseline N(9.9,1.48): .47/.26/.27", {">=10": .47, "9-10": .26, "<9": .27})]:
    rows.append((f"sens: {lab}", round(sum(bm[b] * by_branch[b] for b in bm), 3)))
# --- 3. impact arithmetic (conditional on Yes)
# E[3Q26 nights | Yes] from the branch posterior: P(branch | Yes) = m * P(Yes|branch) / total; branch means under N(9.67,1.70): >=10: 11.24, 9-10: 9.50, <9: 7.83 (truncated normal means)
def tn_mean(mu, sd, lo, hi):
    from math import erf, exp, pi, sqrt
    Phi = lambda z: 0.5 * (1 + erf(z / sqrt(2))); phi = lambda z: exp(-z * z / 2) / sqrt(2 * pi)
    a, b = (lo - mu) / sd, (hi - mu) / sd
    return mu + sd * (phi(a) - phi(b)) / (Phi(b) - Phi(a))
means = {">=10": tn_mean(9.67, 1.70, 10.0, 30), "9-10": tn_mean(9.67, 1.70, 9.0, 10.0), "<9": tn_mean(9.67, 1.70, -10, 9.0)}
post = {b: branches[b] * by_branch[b] / total for b in branches}
e_q3_yes = sum(post[b] * means[b] for b in branches); e_q3_unc = sum(branches[b] * means[b] for b in branches)
rows.append(("P(branch | Yes) >=10 / 9-10 / <9", " / ".join(f"{post[b]:.3f}" for b in branches)))
rows.append(("E[3Q26 nights y/y | Yes] vs unconditional vs team baseline 9.9", f"{e_q3_yes:.2f} vs {e_q3_unc:.2f} vs 9.90"))
d3 = e_q3_yes - 9.90; d4 = 0.6 * d3  # 60% persistence into the Q4 booking rate (R01 convention)
gbv = d3 * 1.34 * 176.8; rev4 = (2/3) * gbv * 0.1203 + d4 * 30.0; fy27 = 0.4 * d3 * 158.0
m26 = 0.59 * ((d3 * 48 + rev4) / 7982) * 100 * 0.5; m27 = 0.66 * (fy27 / 15829) * 100; eps27 = fy27 * 0.66 * 0.0014
rows.append(("impact: 3Q26 nights pts vs baseline", round(d3, 2))); rows.append(("impact: 4Q26 nights pts (0.6 persistence)", round(d4, 2)))
rows.append(("impact: 3Q26 GBV $M", round(gbv, 0))); rows.append(("impact: 4Q26 revenue $M (kernel 2/3 x 12.03% + 4Q26 nights x $30M)", round(rev4, 0)))
rows.append(("impact: FY27 revenue $M (0.4 persistence x $158M)", round(fy27, 0))); rows.append(("impact: FY26 margin pp (0.59 held, half-year weight)", round(m26, 2)))
rows.append(("impact: FY27 margin pp (0.66 held)", round(m27, 2))); rows.append(("impact: FY27 EPS $ (0.66 flow x $0.0014)", round(eps27, 3)))
# stock: language-state day-1 mean -5.4 (strict, n 6) / -6.6 (synonyms, n 8) vs S01 unconditional median -2.9 and base-case -8.6
for lab, cond_mean in [("strict-word prints (n 6)", -5.38), ("synonym prints (n 8)", -6.59)]:
    rows.append((f"impact: stock $/share vs S01 unconditional (-2.9), {lab}", round((cond_mean - (-2.9)) / 100 * 167.51, 2)))
    rows.append((f"impact: stock $/share vs S01 base case (-8.6), {lab}", round((cond_mean - (-8.6)) / 100 * 167.51, 2)))
with open(HERE/"b01_decomposition_output.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["item", "value"]); w.writerows(rows)
for r in rows: print(f"{r[0]}: {r[1]}")
