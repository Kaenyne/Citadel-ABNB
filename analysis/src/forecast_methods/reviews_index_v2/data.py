"""Loaders. Reads only committed inputs (q3nowcast/E counted layer, KPI history, Eurostat, K2 kernel)."""
import numpy as np, pandas as pd
import config as C


def tag(mv):
    mv = mv.copy()
    mv["country"] = mv.market_key.str.split("_").str[0]
    mv["region"] = mv.country.map(C.REGION_OF_COUNTRY).fillna("EMEA")
    d = pd.to_datetime(mv.dump_date)
    mv["dump_ymi"] = d.dt.year * 12 + d.dt.month - 1
    return mv


def load_counted(path=None):
    return tag(pd.read_csv(path or C.E / "market_vintage_monthly.csv"))


def select_vintages(mv):
    """Per market: the latest dump, and the prior dump 300-430 days older (E4's rule). Both trimmed: the
    LAG_TRIM_MONTHS months up to and including the dump month are dropped (posting lag, truncation)."""
    lat = mv.sort_values("dump_date").groupby("market_key").dump_date.last().rename("latest")
    m = mv.merge(lat, on="market_key")
    latest = m[m.dump_date == m.latest].copy()
    parts = []
    for mkt, g in m.groupby("market_key"):
        late = pd.Timestamp(g.latest.iloc[0])
        olds = sorted(v for v in g.dump_date.unique()
                      if C.VMATCH_DAYS[0] <= (late - pd.Timestamp(v)).days <= C.VMATCH_DAYS[1])
        if olds:
            parts.append(g[g.dump_date == olds[-1]])
    prior = pd.concat(parts, ignore_index=True) if parts else latest.iloc[0:0].copy()
    trim = lambda d: d[d.ymi <= d.dump_ymi - C.LAG_TRIM_MONTHS].drop(columns=["latest"])
    return trim(latest), trim(prior)


def load_kpi():
    k = pd.read_csv(C.KPI).dropna(subset=["nights_m"])
    k["qi"] = k.year.astype(int) * 4 + k.q.astype(int) - 1
    return k[["year", "q", "qi", "nights_m", "nights_m_yoy_pct"]].sort_values("qi")


def load_eurostat_yoy():
    e = pd.read_csv(C.EUROSTAT)
    d = pd.to_datetime(e.month); e["ymi"] = d.dt.year * 12 + d.dt.month - 1
    cols = [c for c in e.columns if c.endswith("_nights") and not c.startswith("eu27")]
    wide = e.set_index("ymi")[cols]
    wide = wide.reindex(range(wide.index.min(), wide.index.max() + 1))
    yoy = np.log(wide / wide.shift(12))
    long = wide.stack().rename("nights").reset_index().rename(columns={"level_1": "code"})
    long["code"] = long.code.str[:2]
    ly = yoy.stack().rename("y_yoy").reset_index().rename(columns={"level_1": "code"}); ly["code"] = ly.code.str[:2]
    return long.merge(ly, on=["ymi", "code"], how="left")


def load_kernel():
    k = pd.read_csv(C.K2).set_index("northern_stay_quarter")
    return {int(q[1]): k.loc[q, [f"weight_on_GBV_q-{i}" for i in range(4)]].to_numpy(float) for q in k.index}
