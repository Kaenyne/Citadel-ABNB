"""Workstream 10. Fetches the external regional demand benchmarks that are reachable without a licence:

  JNTO   Japan monthly foreign visitor arrivals by market, 2003..latest (workbook linked from
         https://www.jnto.go.jp/statistics/data/visitors-statistics/ ; the file name carries the release date).
  StatCan  table 24-10-0053, Canada, monthly: Canadian residents returning from the United States
         (total / air / land) and from countries other than the US, plus US residents entering Canada.
         Via the WDS REST API (getDataFromCubePidCoordAndLatestNPeriods).

Writes
  data/processed/overnight/10_bench_japan_arrivals_monthly.csv
  data/processed/overnight/10_bench_canada_travel_monthly.csv
Run: py -3.13 analysis/src/overnight/10_fetch_benchmarks.py

Sources that could NOT be pulled programmatically in this session and are therefore absent from the
benchmark file (documented in the note): US NTTO monthly arrivals (trade.gov blocks scripted access),
STR/CoStar RevPAR (licensed), Korea KTO, Mexico DATATUR, Brazil Embratur.
"""
import io, os, re, json
import requests, pandas as pd, numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "data", "processed", "overnight")
os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (citadel-abnb research ksurapaneni@ufl.edu)"}

# ------------------------------------------------------------------ JNTO
idx = requests.get("https://www.jnto.go.jp/statistics/data/visitors-statistics/", headers=UA, timeout=60).text
xl = sorted(set(re.findall(r'href="(/statistics/data/_files/[^"]+\.xlsx)"', idx)))
assert xl, "no JNTO workbook link found"
url = "https://www.jnto.go.jp" + xl[-1]
release = re.search(r"_files/(\d{8})", url).group(1)
print("JNTO workbook", url, "release", release)
raw = requests.get(url, headers=UA, timeout=120).content
xls = pd.ExcelFile(io.BytesIO(raw))
rows = []
for sheet in xls.sheet_names:
    if not re.fullmatch(r"\d{4}", sheet):
        continue
    year = int(sheet)
    df = pd.read_excel(xls, sheet, header=None)
    hdr = df.index[df[0].astype(str).str.strip() == "総数"]  # exact: the sheet title also contains 総数
    if len(hdr) == 0:
        continue
    r = hdr[0]
    hrow = r - 1
    for c in range(2, df.shape[1]):
        lab = str(df.iat[hrow, c])
        m = re.match(r"(\d{1,2})月$", lab)
        if not m:
            continue
        month = int(m.group(1))
        v = df.iat[r, c]
        g = df.iat[r, c + 1] if c + 1 < df.shape[1] else np.nan
        if pd.isna(v):
            continue
        rows.append(dict(month=f"{year}-{month:02d}-01", visitors=float(v),
                         yoy_pct_reported=float(g) if pd.notna(g) and isinstance(g, (int, float)) else np.nan))
jp = pd.DataFrame(rows).drop_duplicates("month").sort_values("month")
jp["yoy_pct"] = (jp.visitors / jp.visitors.shift(12) - 1) * 100
jp["source"] = url
jp["release_date"] = release
jp.round(3).to_csv(os.path.join(OUT, "10_bench_japan_arrivals_monthly.csv"), index=False)
print("japan arrivals: last", jp.month.iloc[-1], "y/y", round(jp.yoy_pct.iloc[-1], 1))

# ------------------------------------------------------------------ StatCan 24-10-0053
MEMBERS = {  # dim-2 memberId -> column name
    42: "cdn_residents_returning_from_us",
    43: "cdn_residents_returning_from_us_air",
    46: "cdn_residents_returning_from_us_land",
    57: "cdn_residents_returning_from_other",
    3:  "us_residents_entering_canada",
}
frames = {}
for mid, name in MEMBERS.items():
    coord = f"1.{mid}.1." + ".".join(["0"] * 7)
    r = requests.post("https://www150.statcan.gc.ca/t1/wds/rest/getDataFromCubePidCoordAndLatestNPeriods",
                      json=[{"productId": 24100053, "coordinate": coord, "latestN": 120}], timeout=120)
    o = r.json()[0]
    assert o["status"] == "SUCCESS", (name, o)
    d = pd.DataFrame(o["object"]["vectorDataPoint"])[["refPer", "value"]]
    d["value"] = pd.to_numeric(d.value, errors="coerce")
    frames[name] = d.set_index("refPer")["value"]
ca = pd.DataFrame(frames)
ca.index = pd.to_datetime(ca.index)
ca = ca.sort_index()
for c in list(ca.columns):
    ca[c + "_yoy_pct"] = (ca[c] / ca[c].shift(12) - 1).mul(100).round(2)
ca.index.name = "month"
ca["source"] = "Statistics Canada table 24-10-0053 (WDS API), travellers, Canada total"
ca.to_csv(os.path.join(OUT, "10_bench_canada_travel_monthly.csv"))
print("canada: last", ca.index.max().date())
print(ca[[c for c in ca.columns if c.endswith("_yoy_pct")]].tail(18).to_string())
