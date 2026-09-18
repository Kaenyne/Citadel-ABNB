"""Monte Carlo of the true 3Q26 RNPL share of GBV (C06). Run: py -3.13 share_ramp_model_2026-09-17.py
Writes share_ramp_model_2026-09-17.csv next to this file. Inputs are stated in the CSV footer row."""
import random, csv, pathlib
random.seed(7)
N = 200000
ge25 = b2124 = le20 = 0
for _ in range(N):
    s2 = random.uniform(21, 23)                 # 2Q26 true share ("over 20%", call mirror D043)
    ramp = random.uniform(0, 2)                 # residual ex-US adoption ramp (D036: "not far behind")
    exp_ = min(6, random.expovariate(1 / 1.4))  # July 2026 eligibility expansion, size undisclosed (D044)
    seas = random.uniform(-2, 0)                # Q3 short-lead-time mix reduces deferral applicability (03_insider_mechanics §1.3; D002)
    s3 = s2 + ramp + exp_ + seas
    if s3 >= 24.5: ge25 += 1
    elif s3 >= 20.5: b2124 += 1
    else: le20 += 1
out = pathlib.Path(__file__).with_suffix('.csv')
with open(out, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['bucket_true_share', 'probability', 'definition'])
    w.writerow(['>=25 (rounds to 25 or more)', round(ge25 / N, 3), 's3>=24.5'])
    w.writerow(['21-24', round(b2124 / N, 3), '20.5<=s3<24.5'])
    w.writerow(['<=20', round(le20 / N, 3), 's3<20.5'])
    w.writerow(['inputs', '', '2Q26 share U(21,23); ex-US ramp U(0,2); July expansion Exp(mean 1.4) capped 6; Q3 lead-time seasonal U(-2,0); N=200000 seed 7'])
print(open(out).read())
