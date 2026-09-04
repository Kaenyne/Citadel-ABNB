"""Run this LOCALLY (Inside Airbnb downloads are blocked from the sandbox this repo was built in).
Builds a consistent Airbnb-demand proxy for any set of cities: quarterly count of reviews
(Inside Airbnb publishes every review's date; reviews/quarter ~ stays/quarter x review rate).
Then computes YoY growth per city-quarter so it can be joined to airport passenger YoY.

Usage:
  pip install pandas requests
  python analysis/inside_airbnb_review_velocity.py
Edit CITIES below with the exact path segments from https://insideairbnb.com/get-the-data/
(country/region/city/date). Output: data/processed/inside_airbnb_review_velocity.csv
"""
import io, gzip, requests, pandas as pd
CITIES = {  # name: (country, region, city, snapshot_date)
    "Paris": ("france","ile-de-france","paris","2026-06-13"),
    "London": ("united-kingdom","england","london","2026-06-12"),
    "Rome": ("italy","lazio","rome","2026-06-19"),
    "Rio de Janeiro": ("brazil","rj","rio-de-janeiro","2026-06-25"),
    "Mexico City": ("mexico","distrito-federal","mexico-city","2026-06-26"),
    "Buenos Aires": ("argentina","ciudad-autónoma-de-buenos-aires","buenos-aires","2026-07-24"),
    "New York City": ("united-states","ny","new-york-city","2026-07-01"),
    "Los Angeles": ("united-states","ca","los-angeles","2026-06-05"),
    "Sydney": ("australia","nsw","sydney","2026-06-12"),
    "Barcelona": ("spain","catalonia","barcelona","2026-06-24"),
}
rows=[]
for name,(co,reg,city,date) in CITIES.items():
    url=f"https://data.insideairbnb.com/{co}/{reg}/{city}/{date}/data/reviews.csv.gz"
    print("fetching",name,url)
    r=requests.get(url,timeout=120); r.raise_for_status()
    df=pd.read_csv(io.BytesIO(gzip.decompress(r.content)),usecols=["date"])
    df["date"]=pd.to_datetime(df["date"]); df=df[df["date"]>="2022-01-01"]
    q=df.groupby(df["date"].dt.to_period("Q")).size()
    for per,n in q.items():
        prev=per-4
        rows.append({"city":name,"quarter":str(per),"reviews":int(n),"reviews_yoy_pct":(n/q[prev]-1)*100 if prev in q.index else None})
out=pd.DataFrame(rows); out.to_csv("data/processed/inside_airbnb_review_velocity.csv",index=False)
print(out.tail(20)); print("wrote data/processed/inside_airbnb_review_velocity.csv")
# NOTE: the last snapshot quarter is partial (snapshot mid-quarter) - drop it before correlating.
