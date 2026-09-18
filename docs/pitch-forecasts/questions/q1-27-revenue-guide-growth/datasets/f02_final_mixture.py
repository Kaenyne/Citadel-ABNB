"""F02 final mixture: 0.70 x base (team GBV path, RNPL-tilted lambda, Q1 cushion 2.5%)
+ 0.30 x pre-registration convention (lambda_Q1 12.66 ewm, unbiased residual, cushion 2.2%).
Run after f02_model.py from the same folder: python f02_final_mixture.py (writes f02_final_mixture.csv)."""
import numpy as np, csv, os
from f02_model import run, summ, N
HERE = os.path.dirname(os.path.abspath(__file__))
rA = run(); rB = run(seed=20260918, lam=12.66, eps_mu=0.0, c_mu=2.2)
k = int(0.7 * N)
gF = np.concatenate([rA['g'][:k], rB['g'][:N - k]]); guideF = np.concatenate([rA['guide'][:k], rB['guide'][:N - k]])
sF = summ(gF)
print('FINAL MIXTURE: guide median $%.0fM' % np.median(guideF))
for k_, v in sF.items(): print('  %s: %.3f' % (k_, v))
with open(os.path.join(HERE, 'f02_final_mixture.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['stat', 'value'])
    for k_, v in sF.items(): w.writerow([k_, round(v, 4)])
    for p in [5, 10, 25, 50, 75, 90, 95]: w.writerow(['guide_musd_p%d' % p, round(float(np.percentile(guideF, p)), 0)])
    w.writerow(['mass_below_0pct', round(float((gF < 0).mean()), 4)]); w.writerow(['mass_above_20pct', round(float((gF > 20).mean()), 4)])
hist, edges = np.histogram(gF, bins=np.arange(-2, 24, 1.0))
with open(os.path.join(HERE, 'f02_final_hist.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['bin_lo', 'bin_hi', 'share'])
    for i in range(len(hist)): w.writerow([edges[i], edges[i + 1], round(hist[i] / N, 4)])
