"""B01 revision 2 - P(demand-softening language applied to forward demand/bookings at the 5 Nov print). Audit A14 (A14-02, -03, -10, -13, -14, -17, -18, -23, -25).
Standard library only. Run from the repo root:
py -3.13 docs/pitch-forecasts/questions/bonus-moderation-language/datasets/b01_decomposition_v2.py
Changes vs b01_decomposition.py (left in place as the audit trail): branch masses from the run's adopted N(9.5, 1.70) (R01 rev 2,
adopted_print_states_v2.json); P(word | C02 directional-moderate) 0.85 -> 0.90; bucket conditionals 0.25/0.40 -> 0.20/0.35; a resolver path for
general 'macro conditions' framing; two base rates (unconditional by window; conditional on the descriptor class); impact deltas measured from the
tree's own unconditional on the adopted distribution with the kernel-lag term dropped; stock priced off S01 revision 2 (unconditional median -2.1,
base case -5.1). Also writes b01_prepared_remarks_scan.csv (regex scan of the prepared-remarks portion of the web transcript mirrors, A14-25)."""
import csv, glob, html, math, os, re
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[4]
rows = []
def Phi(z): return 0.5 * (1 + math.erf(z / math.sqrt(2)))
def tn_mean(mu, sd, lo, hi):
    phi = lambda z: math.exp(-z * z / 2) / math.sqrt(2 * math.pi)
    a, b = (lo - mu) / sd, (hi - mu) / sd
    return mu + sd * (phi(a) - phi(b)) / (Phi(b) - Phi(a))
# --- 1. base rates from the letter classification
recs = list(csv.DictReader(open(HERE/"b01_letter_language_by_print.csv", encoding="utf-8")))
n = len(recs); strict = sum(int(r["yes_strict"]) for r in recs); syn = sum(int(r["yes_with_synonyms"]) for r in recs)
w1 = [r for r in recs if r["print_quarter"] not in ("3Q22","4Q22")]; w2 = [r for r in recs if r["print_quarter"][-2:] in ("24","25","26")]
nov = [r for r in recs if r["print_quarter"].startswith("3Q")]; buck = [r for r in recs if "bucket" in r["descriptor_class"]]
rows.append(("letters n / strict / with synonyms", f"{n} / {strict} ({strict/n:.3f}) / {syn} ({syn/n:.3f})"))
rows.append(("W1 (1Q23+) strict / syn / n", f"{sum(int(r['yes_strict']) for r in w1)} / {sum(int(r['yes_with_synonyms']) for r in w1)} / {len(w1)}"))
rows.append(("W2 (1Q24+) strict / syn / n", f"{sum(int(r['yes_strict']) for r in w2)} / {sum(int(r['yes_with_synonyms']) for r in w2)} / {len(w2)}"))
rows.append(("November letters strict / n", f"{sum(int(r['yes_strict']) for r in nov)} / {len(nov)}"))
rows.append(("bucket-era letters (bucket descriptor) strict / n [A14-10: 0/3, not 1/4; 1Q26 is directional]", f"{sum(int(r['yes_strict']) for r in buck)} / {len(buck)} {[r['print_quarter'] for r in buck]}"))
down = [r for r in recs if r["descriptor_class"].startswith("down")]; nond = [r for r in recs if not r["descriptor_class"].startswith("down")]
p_w_down = sum(int(r['yes_strict']) for r in down)/len(down); p_w_nond_syn = sum(int(r['yes_with_synonyms']) for r in nond)/len(nond)
rows.append(("P(strict word | down-class descriptor)", f"{sum(int(r['yes_strict']) for r in down)}/{len(down)} = {p_w_down:.3f} (with synonyms {sum(int(r['yes_with_synonyms']) for r in down)}/{len(down)})"))
rows.append(("P(word | non-down descriptor) strict / with synonyms", f"{sum(int(r['yes_strict']) for r in nond)}/{len(nond)} / {sum(int(r['yes_with_synonyms']) for r in nond)}/{len(nond)}"))
# C02-(d)-directional class: down-class directional sentences that C02 would resolve (d) (excludes 4Q24's 'relatively stable ex Leap Day', a (b) form)
d_dir = [r for r in recs if r["descriptor_class"] == "down"]
rows.append(("P(word | C02 (d)-directional class) strict / with synonyms / Laplace(syn)", f"{sum(int(r['yes_strict']) for r in d_dir)}/{len(d_dir)} / {sum(int(r['yes_with_synonyms']) for r in d_dir)}/{len(d_dir)} / {(sum(int(r['yes_with_synonyms']) for r in d_dir)+1)/(len(d_dir)+2):.2f}"))
# unconditional base rate (two windows) and the conditional route
base_uncond = (5/14 + 3/10) / 2
P_DOWN = 0.40  # P(down-class descriptor) in the bucket regime: unconditional 8/16 = 0.50 (W2 4/10 = 0.40), shaded for the bucket format converting down-descriptors into buckets (3Q25, 4Q25)
base_cond = P_DOWN * p_w_down + (1 - P_DOWN) * 0.08   # non-down: 0/8 strict, 1/8 synonyms -> Laplace-ish 0.08
rows.append(("base rate (unconditional, mean of W1 0.357 and W2 0.300)", round(base_uncond, 3)))
rows.append(("base rate (conditional route: P(down-class) 0.40 x 6/8 + 0.60 x 0.08)", round(base_cond, 3)))
# --- 2. decomposition on the C02 revision-2 tree with the adopted print distribution
MU, SD = 9.5, 1.70
p10 = 1 - Phi((10 - MU) / SD); p9 = Phi((9 - MU) / SD)
branches = {">=10": round(p10, 3), "9-10": round(1 - p10 - p9, 3), "<9": round(p9, 3)}
rows.append(("branch masses from the adopted N(9.5, 1.70) [rev 1: 0.423/0.230/0.347 from N(9.67, 1.70)]", " / ".join(f"{v:.3f}" for v in branches.values())))
p_dir = {">=10": 0.25, "9-10": 0.28, "<9": 0.35}; p_none = 0.03
p_mod_given_dir = {">=10": 0.55, "9-10": 0.60, "<9": 0.75}
bucket = {">=10": dict(a=.45, b=.20, c=.30, d=.05), "9-10": dict(a=.08, b=.22, c=.57, d=.13), "<9": dict(a=.02, b=.07, c=.50, d=.41)}
# P(softening language | sentence type), revision 2:
#  dir_mod 0.90: C02's directional-'moderate' block is the word by definition, less the 'lower than revenue growth' form (6/7 strict, 7/7 with synonyms in the (d)-directional class; Laplace 0.89) [A14-13, accepted in part]
#  bucket_c 0.20 / bucket_d 0.35: 0 of 3 bucket letters used a softening word (comp language instead); shaded from 0.25/0.40 [A14-14]
#  resolver 0.025: a general 'macro conditions' framing sentence (4Q25 prepared remarks form) read loosely by a resolver [A14-23]
p_lang = dict(dir_mod=0.90, dir_other=0.10, bucket_a=0.05, bucket_b=0.15, bucket_c=0.20, bucket_d=0.35, none=0.30)
P_RESOLVER = 0.025
def tree(branches, pl):
    total = 0.0; by_branch = {}; by_option = dict(a=0., b=0., c=0., d=0., e=0.); opt_mass = dict(a=0., b=0., c=0., d=0., e=0.)
    for br, m in branches.items():
        pd_, pn = p_dir[br], p_none; pb = 1 - pd_ - pn
        dm = pd_ * p_mod_given_dir[br]; do = pd_ * (1 - p_mod_given_dir[br])
        lang = dm * pl["dir_mod"] + do * pl["dir_other"]
        by_option["d"] += m * dm * pl["dir_mod"]; opt_mass["d"] += m * dm
        key = "a" if br == ">=10" else "b"; by_option[key] += m * do * pl["dir_other"]; opt_mass[key] += m * do
        for o, w in bucket[br].items():
            lang += pb * w * pl["bucket_" + o]; by_option[o] += m * pb * w * pl["bucket_" + o]; opt_mass[o] += m * pb * w
        lang += pn * pl["none"]; by_option["e"] += m * pn * pl["none"]; opt_mass["e"] += m * pn
        by_branch[br] = lang; total += m * lang
    return total, by_branch, by_option, opt_mass
t_tree, by_branch, by_option, opt_mass = tree(branches, p_lang)
t_res = t_tree + P_RESOLVER * (1 - t_tree)
rows.append(("tree P(Yes) before the resolver path", round(t_tree, 4))); rows.append(("decomposition P(Yes) incl. resolver path 0.025 x P(No)", round(t_res, 4)))
for br in branches: rows.append((f"P(Yes | 3Q26 print {br}) [tree]", round(by_branch[br], 3)))
for o in "abcde": rows.append((f"P(Yes and C02={o}) / P(C02={o}) [tree]", f"{by_option[o]:.3f} / {opt_mass[o]:.3f} -> P(Yes|{o}) {by_option[o]/opt_mass[o]:.2f}"))
rows.append(("P(Yes and C02=d) [tree] / share of the Yes mass [A14-17]", f"{by_option['d']:.3f} / {by_option['d']/t_tree:.2f}"))
post = {b: branches[b] * by_branch[b] / t_tree for b in branches}
rows.append(("P(branch | Yes) >=10 / 9-10 / <9", " / ".join(f"{post[b]:.3f}" for b in branches)))
rows.append(("P(3Q26 < 9 | Yes)", round(post["<9"], 3)))
# reproduce the audit's variants
for lab, M, ch in [("rev-1 published (N(9.67,1.70), .85, .25/.40)", {">=10": 0.423, "9-10": 0.230, "<9": 0.347}, dict(dir_mod=.85, bucket_c=.25, bucket_d=.40)),
                   ("auditor (.95, .20/.35, adopted masses)", branches, dict(dir_mod=.95)),
                   ("dir_mod 0.85", branches, dict(dir_mod=.85)), ("dir_mod 0.95", branches, dict(dir_mod=.95)), ("dir_mod 0.70", branches, dict(dir_mod=.70)),
                   ("bucket_c/d 0.25/0.40 (rev 1)", branches, dict(bucket_c=.25, bucket_d=.40)), ("bucket_c/d 0.10/0.20 (literalism)", branches, dict(bucket_c=.10, bucket_d=.20)), ("bucket_c/d 0.30/0.50", branches, dict(bucket_c=.30, bucket_d=.50)),
                   ("b/a/dir_other at the non-down synonym rate 0.125", branches, dict(bucket_b=.125, bucket_a=.125, dir_other=.125))]:
    pl = dict(p_lang); pl.update(ch); t, _, _, _ = tree(M, pl)
    rows.append((f"sens tree: {lab} (tree / with resolver)", f"{t:.3f} / {t + P_RESOLVER*(1-t):.3f}"))
for lab, mu, sd in [("Street/Kalshi N(11.0,1.7)", 11.0, 1.7), ("external stack N(9.2,1.7)", 9.2, 1.7), ("team baseline N(9.9,1.48)", 9.9, 1.48), ("rev-1 R01 N(9.67,1.70)", 9.67, 1.70), ("adopted sd 1.0", 9.5, 1.0), ("adopted sd 2.16 (naive RMSE)", 9.5, 2.16)]:
    q10 = 1 - Phi((10 - mu) / sd); q9 = Phi((9 - mu) / sd); bm = {">=10": q10, "9-10": 1 - q10 - q9, "<9": q9}
    t = sum(bm[b] * by_branch[b] for b in bm); rows.append((f"sens masses: {lab} (tree / with resolver)", f"{t:.3f} / {t + P_RESOLVER*(1-t):.3f}"))
for lab, ch in [("C02 P(directional) 0.20 everywhere", 0.20), ("C02 P(directional) 0.40 everywhere", 0.40)]:
    save = dict(p_dir); p_dir.update({k: ch for k in p_dir}); t, _, _, _ = tree(branches, p_lang); p_dir.update(save)
    rows.append((f"sens: {lab} (tree / with resolver)", f"{t:.3f} / {t + P_RESOLVER*(1-t):.3f}"))
for lab, pr in [("resolver path 0", 0.0), ("resolver path 0.05", 0.05)]:
    rows.append((f"sens: {lab}", round(t_tree + pr * (1 - t_tree), 3)))
# --- 3. blend
anchor = 0.31
final = 0.5 * t_res + 0.3 * base_uncond + 0.2 * anchor
rows.append(("blend 0.5 x decomposition + 0.3 x base rate (unconditional) + 0.2 x anchor C02 (d) 0.31", round(final, 4)))
rows.append(("blend with the conditional base-rate route instead", round(0.5 * t_res + 0.3 * base_cond + 0.2 * anchor, 4)))
FINAL = 0.33
rows.append(("FINAL (rounded)", FINAL))
rows.append(("P(Yes and C02=d) scaled to the final / P(Yes and C02!=d)", f"{FINAL*by_option['d']/t_tree:.3f} / {FINAL*(1-by_option['d']/t_tree):.3f}"))
# --- 4. day-1 classes (A14-18)
d1s = sorted(float(r["day1_excess_pct"]) for r in recs if int(r["yes_strict"])); d1y = [float(r["day1_excess_pct"]) for r in recs if int(r["yes_with_synonyms"])]
d1n = [float(r["day1_excess_pct"]) for r in recs if not int(r["yes_strict"])]; d1all = [float(r["day1_excess_pct"]) for r in recs]
med = lambda v: (sorted(v)[len(v)//2 - 1] + sorted(v)[len(v)//2]) / 2 if len(v) % 2 == 0 else sorted(v)[len(v)//2]
rows.append(("day-1 excess, strict class n 6: values, mean, median, P(<=-8)", f"{d1s}, {sum(d1s)/6:+.2f}, {med(d1s):+.2f}, {sum(v<=-8 for v in d1s)}/6"))
rows.append(("day-1 excess, synonym class n 8: mean, median, P(<=-8)", f"{sum(d1y)/8:+.2f}, {med(d1y):+.2f}, {sum(v<=-8 for v in d1y)}/8"))
rows.append(("day-1 excess, no strict word n 10: mean, median; all 16: mean, median", f"{sum(d1n)/10:+.2f}, {med(d1n):+.2f}; {sum(d1all)/16:+.2f}, {med(d1all):+.2f}"))
# --- 5. impact on the adopted distribution (A14-02, A14-03)
means = {">=10": tn_mean(MU, SD, 10.0, 30), "9-10": tn_mean(MU, SD, 9.0, 10.0), "<9": tn_mean(MU, SD, -10, 9.0)}
e_yes = sum(post[b] * means[b] for b in branches); e_unc = sum(branches[b] * means[b] for b in branches)
d3 = e_yes - e_unc; d4 = 0.6 * d3
r3 = d3 * 48.0; r4 = d4 * 30.0; fy27 = 0.4 * d3 * 158.0
m26 = (r3 + r4) * (1 - 0.35727) / 14268.1 * 100; m27 = fy27 * 0.66 / 15828.6 * 100; eps27 = fy27 * 0.66 * 0.0014
rows.append(("E[3Q26 nights | Yes] vs the tree's unconditional (adopted N(9.5,1.70)) [rev 1 measured from the 9.90 team path]", f"{e_yes:.2f} vs {e_unc:.2f} -> {d3:+.2f}pt"))
rows.append(("impact: 3Q26 nights pts / 4Q26 nights pts (0.6 persistence)", f"{d3:+.2f} / {d4:+.2f}"))
rows.append(("impact: 3Q26 revenue $M (x48) / 4Q26 revenue $M (x30; kernel-lag term dropped, A14-02) / FY27 revenue $M (0.4 x 158)", f"{r3:+.0f} / {r4:+.0f} / {fy27:+.0f}"))
rows.append(("impact: FY26 margin pp (costs held) / FY27 margin pp (0.66) / FY27 EPS $", f"{m26:+.2f} / {m27:+.2f} / {eps27:+.3f}"))
PX = 167.51; S01_UNC_MED, S01_BASE_MED, S01_UNC_MEAN = -2.1, -5.1, -2.0
stock_med = (med(d1s) - S01_UNC_MED) / 100 * PX
shift_mean = (sum(d1s)/6 - sum(d1all)/16); stock_mean_shrunk = 0.6 * shift_mean / 100 * PX
rows.append(("stock route 1: strict-class median -3.95 vs S01 rev-2 unconditional median -2.1 -> pt, $/share", f"{med(d1s)-S01_UNC_MED:+.2f}, {stock_med:+.2f}"))
rows.append(("stock route 2: strict-class mean vs the 16-print mean, shrunk x0.6 (S01 kappa) -> pt, $/share", f"{0.6*shift_mean:+.2f}, {stock_mean_shrunk:+.2f}"))
rows.append(("stock vs the S01 rev-2 base case (median -5.1): strict-class median -3.95 -> pt, $/share", f"{med(d1s)-S01_BASE_MED:+.2f}, {(med(d1s)-S01_BASE_MED)/100*PX:+.2f}"))
rows.append(("EV at P 0.33: route 1 / route 2 ($/share vs the unconditional); incremental to the base case", f"{FINAL*stock_med:+.2f} / {FINAL*stock_mean_shrunk:+.2f}; ~0 (positive on the median route)"))
# --- 6. prepared-remarks scan of the web transcript mirrors (A14-25)
def text(p):
    s = Path(p).read_text(encoding="utf-8", errors="ignore")
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s); s = re.sub(r"(?s)<[^>]+>", " ", s); s = html.unescape(s)
    for a, b in [("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("–", "-"), ("—", "-"), ("\xa0", " ")]: s = s.replace(a, b)
    return re.sub(r"\s+", " ", s)
MARK = re.compile(r"question-and-answer session|questions and answers|q&a session|first question (comes|is) from|our first question|we'll take our first question|\[operator instructions\]", re.I)
STEM = re.compile(r"\bmoderat|lead time|soften|softer|softness|decelerat|macro(economic)? (uncertaint|condition|environment|trend)|slowing demand|pressure on growth", re.I)
scan = []
for f in sorted(glob.glob(str(ROOT/"data/raw/transcripts/web/*.html"))):
    qn = os.path.basename(f)[:4]
    if not re.match(r"[1-4]Q2[2-6]", qn): continue
    s = text(f); m = MARK.search(s); cut = m.start() if m else len(s)
    prepared = s[:cut]
    hits = [x.strip() for x in re.split(r"(?<=[.!?]) +", prepared) if STEM.search(x)]
    scan.append(dict(quarter=qn, qa_marker_found=int(m is not None), prepared_chars=cut, stem_hits_prepared=len(hits),
                     hits="; ".join(h[:220] for h in hits[:6])))
with open(HERE/"b01_prepared_remarks_scan.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(scan[0].keys())); w.writeheader(); w.writerows(scan)
rows.append(("prepared-remarks scan: transcripts scanned / Q&A marker found / with >=1 stem hit in prepared remarks", f"{len(scan)} / {sum(r['qa_marker_found'] for r in scan)} / {sum(r['stem_hits_prepared']>0 for r in scan)} -> b01_prepared_remarks_scan.csv"))
with open(HERE/"b01_decomposition_v2_output.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["item", "value"]); w.writerows(rows)
for r in rows: print(f"{r[0]}: {r[1]}")
