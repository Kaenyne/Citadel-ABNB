"""Bookings <-> stays through the K2 lead-time kernel: stays in calendar quarter q come from bookings in
q..q-3 with weights M[q][0..3]. Levels, lower-triangular; the first three bookings are set to stays."""
import numpy as np, pandas as pd


def _q(qi):
    return int(qi % 4) + 1


def convolve(G, M):
    qi = G.index.to_numpy(); g = G.to_numpy(float); S = np.full(len(g), np.nan)
    for t in range(len(g)):
        w = M[_q(qi[t])]
        S[t] = g[t] if t < 3 else sum(w[k] * g[t - k] for k in range(4))
    return pd.Series(S, index=G.index)


def deconvolve(S, M):
    qi = S.index.to_numpy(); s = S.to_numpy(float); G = np.full(len(s), np.nan)
    for t in range(len(s)):
        w = M[_q(qi[t])]
        G[t] = s[t] if t < 3 else (s[t] - sum(w[k] * G[t - k] for k in range(1, 4))) / w[0]
    return pd.Series(G, index=S.index)


def realised_share(qi_cohort, last_qi, M):
    """Share of cohort qi_cohort's eventual stays observed by last_qi. K2 rows are normalised per STAY quarter,
    so the four weights that belong to one booking cohort do not sum to exactly 1; normalise by their total."""
    total = sum(M[_q(qi_cohort + k)][k] for k in range(4))
    seen = sum(M[_q(qi_cohort + k)][k] for k in range(4) if qi_cohort + k <= last_qi)
    return float(seen / total)
