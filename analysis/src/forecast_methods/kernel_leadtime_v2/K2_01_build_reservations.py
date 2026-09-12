"""
K2 step 1 -- build a reservation-level lead-time table from the Melbourne STR daily panels.

Source: Harvard Dataverse doi:10.7910/DVN/1XPDEU ("To Airbnb: A Question of Revenues"),
        str_daily_1.tab (2014-10-01..2016-08-31) and str_daily_2.csv (2015-08-01..2017-02-28).
        Property x calendar-night grain with Status (A/B/R), Price, Booked Date, Reservation ID.

Read with DuckDB, never fully into pandas. Output: one row per reservation.
"""
import os
import duckdb
import pandas as pd

ROOT = "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB"
SRC = os.path.join(ROOT, "Theo Data/raw_expansion/v2_2026-09-05/harvard_dataverse/doi10.7910_DVN_1XPDEU")
OUT = os.path.join(ROOT, "Citadel-ABNB/data/processed/forecast_methods/kernel_leadtime_v2")
os.makedirs(OUT, exist_ok=True)

def q(path):
    """Single-quote a path for a SQL literal (the repo path contains an apostrophe)."""
    return path.replace("'", "''")

SRC_Q = q(SRC)
OUT_Q = q(OUT)

con = duckdb.connect()
con.execute("pragma threads=4")

con.execute(f"""
create or replace view s1 as
select "Property.ID" as pid, "Date" as dt, "Status" as st, "Price" as pr,
       "Booked.Date" as bd, "Reservation.ID" as rid, 1 as panel
from read_csv('{SRC_Q}/str_daily_1.tab', delim='\t', header=true, all_varchar=true, ignore_errors=true)
""")
con.execute(f"""
create or replace view s2 as
select "Property ID" as pid, "Date" as dt, "Status" as st, "Price" as pr,
       "Booked Date" as bd, "Reservation ID" as rid, 2 as panel
from read_csv('{SRC_Q}/str_daily_2.csv', delim=',', header=true, all_varchar=true, ignore_errors=true)
""")

# Union with an explicit version rule: on shared (pid, date) keys prefer panel 2 (the later,
# more complete vintage -- it has materially better Booked Date coverage). The audit notes the
# two panels disagree on price for 186,812 keys and booked date for 2,691; we quantify below.
con.execute("""
create or replace table daily as
select pid, dt, st, pr, bd, rid, panel from (
  select *, row_number() over (partition by pid, dt order by panel desc) as rn
  from (select * from s1 union all select * from s2)
) where rn = 1
""")

n_daily = con.execute("select count(*) from daily").fetchone()[0]
overlap = con.execute("""
select count(*) as shared_keys,
       sum(case when a.pr is distinct from b.pr then 1 else 0 end) as price_disagree,
       sum(case when a.bd is distinct from b.bd then 1 else 0 end) as booked_disagree,
       sum(case when a.st is distinct from b.st then 1 else 0 end) as status_disagree
from s1 a join s2 b using (pid, dt)
""").df()
print(f"[daily] union rows = {n_daily:,}")
print("[overlap]\n", overlap.to_string(index=False))

# Reservation grain. Booked Date is populated only on R rows.
con.execute("""
create or replace table resv as
select
  pid,
  rid,
  min(strptime(dt,'%Y-%m-%d')::date)                              as check_in,
  max(strptime(dt,'%Y-%m-%d')::date)                              as last_night,
  count(*)                                                        as nights,
  (max(strptime(dt,'%Y-%m-%d')::date)
     - min(strptime(dt,'%Y-%m-%d')::date) + 1)                    as span_days,
  min(strptime(bd,'%Y-%m-%d')::date)                              as booked_date,
  count(distinct bd)                                              as n_booked_vals,
  sum(try_cast(pr as double))                                     as value_total,
  avg(try_cast(pr as double))                                     as adr
from daily
where st = 'R' and rid is not null and rid <> '' and bd is not null and bd <> ''
group by pid, rid
""")

tot = con.execute("select count(*) from resv").fetchone()[0]
print(f"[resv] reservations with a booked date = {tot:,}")

diag = con.execute("""
select
  count(*)                                                       as n,
  sum(case when nights <> span_days then 1 else 0 end)           as non_contiguous,
  sum(case when n_booked_vals > 1 then 1 else 0 end)             as multi_booked_date,
  sum(case when booked_date > check_in then 1 else 0 end)        as booked_after_checkin,
  sum(case when booked_date = check_in then 1 else 0 end)        as same_day,
  sum(case when value_total is null then 1 else 0 end)           as null_value
from resv
""").df()
print("[diagnostics]\n", diag.to_string(index=False))

con.execute("""
create or replace table resv_clean as
select *,
  date_diff('day', booked_date, check_in) as lead_days,
  year(check_in)                          as stay_year,
  month(check_in)                         as stay_month,
  quarter(check_in)                       as stay_q
from resv
where nights = span_days              -- contiguous block only (one true stay)
  and n_booked_vals = 1               -- unambiguous booking date
  and booked_date <= check_in         -- drop vendor revision artifacts
  and value_total is not null
  and value_total > 0
""")

print("[clean]\n", con.execute("""
select count(*) as n_resv, min(check_in) as min_ci, max(check_in) as max_ci,
       min(booked_date) as min_bd, max(booked_date) as max_bd,
       median(lead_days) as med_lead, avg(lead_days) as mean_lead,
       median(nights) as med_nights, avg(nights) as mean_nights
from resv_clean""").df().to_string(index=False))

con.execute(f"copy (select * from resv_clean) to '{OUT_Q}/K2_reservations.parquet' (format parquet)")
print(f"\nwrote {OUT}/K2_reservations.parquet")

# Booked-date coverage by stay month, to document the left-truncation window.
cov = con.execute("""
select strftime(strptime(dt,'%Y-%m-%d'),'%Y-%m') as stay_ym,
       count(*) as r_nights,
       sum(case when bd is not null and bd<>'' then 1 else 0 end) as nights_with_booked_date,
       round(100.0*sum(case when bd is not null and bd<>'' then 1 else 0 end)/count(*),1) as pct_covered
from daily where st='R' group by 1 order by 1
""").df()
cov.to_csv(f"{OUT}/K2_booked_date_coverage_by_month.csv", index=False)
print("\n[coverage by stay month]\n", cov.to_string(index=False))
