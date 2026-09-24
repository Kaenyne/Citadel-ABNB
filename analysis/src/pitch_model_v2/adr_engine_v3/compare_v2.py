"""adr_engine_v3 / compare_v2.py — the v3 line against adr_engine (v2) as filed: every ladder row and the path, for
3Q26 and 4Q26 (and FY27 on the path). Reads v2's outputs read-only; writes v3_vs_v2_*.csv into v3's output folder."""
from __future__ import annotations
import pandas as pd
from . import config as C


def main() -> dict[str, pd.DataFrame]:
    v2s = pd.read_csv(C.SEED_FROM / "adr_scenarios.csv"); v3s = pd.read_csv(C.OUT / "adr_scenarios.csv")
    rename = {"AR(1) on core (K4 rho 0.747)": "AR(1) fitted on core"}          # fix (d) renamed the row
    v2s["rule"] = v2s.rule.replace(rename)
    keep = ["3Q26", "4Q26"]
    a = v2s[v2s.quarter.isin(keep)].pivot(index="rule", columns="quarter", values="adr_usd").add_prefix("v2_")
    b = v3s[v3s.quarter.isin(keep)].pivot(index="rule", columns="quarter", values="adr_usd").add_prefix("v3_")
    c = v3s[v3s.quarter.isin(keep)].pivot(index="rule", columns="quarter", values="adr_usd_fx_v1").add_prefix("v3_fxV1_")
    d = v3s[v3s.quarter.isin(keep)].pivot(index="rule", columns="quarter", values="adr_usd_fx_identity").add_prefix("v3_fxV0_")
    lad = a.join(b, how="outer").join(c, how="outer").join(d, how="outer")
    for q in keep:
        lad[f"d_{q}"] = lad[f"v3_{q}"] - lad[f"v2_{q}"]
        lad[f"v3_vs_street_{q}"] = lad[f"v3_{q}"] - C.STREET_ADR[q][0]
    lad = lad.sort_values("v3_4Q26")
    p2 = pd.read_csv(C.SEED_FROM / "adr_path.csv", index_col=0); p3 = pd.read_csv(C.OUT / "adr_path.csv", index_col=0)
    rows = ["3Q26", "4Q26", "1Q27", "2Q27", "3Q27", "4Q27", "FY27"]
    path = pd.DataFrame({"v2_adr_usd": p2.loc[rows, "adr_usd"], "v3_adr_usd": p3.loc[rows, "adr_usd"],
                         "v3_adr_usd_fx_v1": p3.loc[rows, "adr_usd_fx_v1"], "v3_adr_usd_fx_identity": p3.loc[rows, "adr_usd_fx_identity"],
                         "v2_band_half_pp": p2.loc[rows, "band_half_pp"], "v3_band_half_pp": p3.loc[rows, "band_half_pp"],
                         "v2_p_ge_street": p2.loc[rows, "p_print_ge_street"], "v3_p_ge_street": p3.loc[rows, "p_print_ge_street"],
                         "v3_p_ge_street_fx_v1": p3.loc[rows, "p_print_ge_street_fx_v1"],
                         "v3_p_ge_street_fx_identity": p3.loc[rows, "p_print_ge_street_fx_identity"]})
    path["d_usd"] = path.v3_adr_usd - path.v2_adr_usd
    lad.to_csv(C.OUT / "v3_vs_v2_ladder.csv"); path.to_csv(C.OUT / "v3_vs_v2_path.csv")
    return {"ladder": lad, "path": path}


if __name__ == "__main__":
    r = main(); pd.set_option("display.width", 250)
    print(r["path"].round(3).to_string()); print(r["ladder"].round(2).to_string())
