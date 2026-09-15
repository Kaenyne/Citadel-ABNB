"""Pull peer quarterly opex lines and headcount from LSEG Workspace (licensed; raw stays under data/raw).
Run: py -3.13 analysis/src/margin_build/04_alt_signals/pull_lseg_peers.py --pull   (Workspace desktop must be open)"""
import os, sys, pathlib, datetime as dt
ROOT = pathlib.Path(__file__).resolve().parents[4]
RAW = ROOT / "data/raw/margin_build/04_alt_signals/misc"; RAW.mkdir(parents=True, exist_ok=True)
FIELDS = ["TR.Revenue","TR.Revenue.periodenddate","TR.SellingGeneralAdminExpensesTotal","TR.SellingMarketingExpenses",
          "TR.ResearchAndDevelopment","TR.TotalOperatingExpense","TR.CostOfRevenueTotal","TR.EBITDA","TR.NumberOfEmployees"]
RICS = ["BKNG.O","EXPE.O","ABNB.O","TRIP.O"]
def main():
    import lseg.data as ld, pandas as pd
    s = ld.session.desktop.Definition(app_key=os.environ["LSEG_APP_KEY"]).get_session(); s.open(); ld.session.set_default(s)
    out = []
    for ric in RICS:
        try:
            df = ld.get_data(ric, FIELDS, {"SDate":"2019-01-01","EDate":"2026-09-13","Frq":"FQ","Period":"FQ0"})
            df["ric"] = ric; out.append(df); print(ric, df.shape)
        except Exception as e:
            print(ric, "fail", type(e).__name__, str(e)[:150])
    if out:
        d = pd.concat(out); d["pulled_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        d.to_csv(RAW / "lseg_peer_opex_quarterly.csv", index=False); print(d.tail(6).to_string())
    s.close()
if __name__ == "__main__":
    if "--pull" in sys.argv: main()
    else: print("pass --pull")
