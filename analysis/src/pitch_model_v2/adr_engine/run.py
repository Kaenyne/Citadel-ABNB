"""adr_engine / run.py — rebuild the ADR line v1 end to end (exit 0). Offline once fx_daily_2026-09-21.csv exists;
`--fetch` refreshes FRED first (writes a new dated file; config.FX_DAILY must then be pointed at it).

    PYTHONPATH=analysis/src python3 -m pitch_model_v2.adr_engine.run [--fetch] [--no-posterior] [--no-workbook]
"""
from __future__ import annotations
import argparse, json, time, warnings
import pandas as pd
from . import config as C, fx_data as F, walkforward as W, forecast as X, exfx as M, assemble as A, figures as G


def main(argv=None):
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser(); ap.add_argument("--fetch", action="store_true"); ap.add_argument("--no-posterior", action="store_true"); ap.add_argument("--no-workbook", action="store_true")
    a = ap.parse_args(argv); t0 = time.time(); C.OUT.mkdir(parents=True, exist_ok=True)
    if a.fetch:
        from . import fetch_fx; fetch_fx.main()
    daily = F.load_daily(); shares = F.gbv_shares(); tg = F.disclosed_targets()
    wf, full = W.run(daily, shares, tg); sc = W.score(wf); promo = W.promotion(sc)
    wf.to_csv(C.OUT / "fx_pit_walkforward.csv", index=False); sc.to_csv(C.OUT / "fx_scores.csv", index=False); full.to_csv(C.OUT / "fx_design_full.csv")
    print("walk-forward:", promo)
    fc = X.run(daily, shares); fc.to_csv(C.OUT / "fx_forecast_asof.csv", index=False)
    X.currency_table(daily).to_csv(C.OUT / "fx_currency_contributions.csv", index=False)
    if not a.no_posterior:
        from . import posterior; posterior.main()
    sd = fc[fc["asof"] == "2026-09-21"].set_index("quarter").sd
    M.history().to_csv(C.OUT / "exfx_history.csv"); M.forward().to_csv(C.OUT / "exfx_forward_base.csv")
    M.alternatives().to_csv(C.OUT / "exfx_alternatives.csv", index=False); M.geo_mix_history_check().to_csv(C.OUT / "geo_mix_method_check.csv")
    M.regional_growth_forward().to_csv(C.OUT / "regional_growth_forward.csv"); M.geo_mix_forward().to_csv(C.OUT / "geo_mix_forward.csv")
    M.bundle_schedule().to_csv(C.OUT / "bundle_schedule.csv"); M.envelope(sd).to_csv(C.OUT / "exfx_envelope.csv")
    path = A.build(); path.to_csv(C.OUT / "adr_path.csv"); A.scenario_table().to_csv(C.OUT / "adr_scenarios.csv", index=False)
    G.main()
    if not a.no_workbook:
        from . import workbook; workbook.build()
    meta = {"run_at": pd.Timestamp.now().isoformat(timespec="seconds"), "fx_last_obs": str(daily.index.max().date()), "promotion": promo,
            "adr_3q26": float(path.loc["3Q26", "adr_usd"]), "adr_4q26": float(path.loc["4Q26", "adr_usd"]), "fx_3q26_pp": float(path.loc["3Q26", "fx_pp"]),
            "fx_4q26_pp": float(path.loc["4Q26", "fx_pp"]), "seconds": round(time.time() - t0, 1)}
    (C.OUT / "00_summary.json").write_text(json.dumps(meta, indent=2)); print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
