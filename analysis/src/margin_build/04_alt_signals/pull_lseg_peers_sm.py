"""Second LSEG pull: peer selling & marketing / SG&A field-name variants (licensed raw under data/raw).
Run: py -3.13 analysis/src/margin_build/04_alt_signals/pull_lseg_peers_sm.py --pull"""
import os, sys, pathlib, datetime as dt
ROOT = pathlib.Path(__file__).resolve().parents[4]
RAW = ROOT / "data/raw/margin_build/04_alt_signals/misc"; RAW.mkdir(parents=True, exist_ok=True)
FIELDS = ["TR.Revenue.periodenddate","TR.SGAExpenseTotal","TR.SellingGeneralAdminExpTotal","TR.SellingAndMarketingExpense","TR.AdvertisingExpense",
          "TR.F.SellingGenAdminExpTot","TR.F.AdvertisingExpn","TR.F.SalesMarketingExpn","TR.F.EmpFTEEquivPrdEnd","TR.F.CostOfRevTot","TR.F.TotOpExp"]
RICS = ["BKNG.O","EXPE.O","ABNB.O","TRIP.O"]
def main():
    import lseg.data as ld, pandas as pd
    s = ld.session.desktop.Definition(app_key=os.environ["LSEG_APP_KEY"]).get_session(); s.open(); ld.session.set_default(s)
    out = []
    for ric in RICS:
        try:
            df = ld.get_data(ric, FIELDS, {"SDate":"2019-01-01","EDate":"2026-09-13","Frq":"FQ","Period":"FQ0"})
            df["ric"] = ric; out.append(df); print(ric, df.shape, list(df.columns))
        except Exception as e:
            print(ric, "fail", type(e).__name__, str(e)[:200])
    if out:
        d = pd.concat(out); d["pulled_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        d.to_csv(RAW / "lseg_peer_sm_quarterly.csv", index=False); print(d.dropna(how="all", axis=1).tail(6).to_string())
    s.close()
if __name__ == "__main__":
    if "--pull" in sys.argv: main()
