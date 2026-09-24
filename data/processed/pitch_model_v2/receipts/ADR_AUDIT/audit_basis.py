"""ADR audit: the mixed-basis construction, bounded. Read-only against the engine; writes only to receipts/ADR_AUDIT.
    PYTHONPATH=analysis/src py -3.13 data/processed/pitch_model_v2/receipts/ADR_AUDIT/audit_basis.py
The core is 2Q26 ex-FX minus the H decomposition's terms; the forward adds terms from other constructions. Measured on
ONE construction, each term's 2Q26 -> 3Q26 change is: geo (bucket arithmetic, both quarters), unit (I, both quarters).
LOS has no same-construction 2Q26 value: H's 2Q26 LOS is an assumed fill (0.30) and the forward LOS is I's blocked-run
measure (0.056). Two cases bound it: A, the switch is a basis offset (true change 0); B, LOS genuinely fell 0.244."""
from __future__ import annotations
import pathlib
import numpy as np
import pandas as pd
from scipy import stats
from pitch_model_v2.adr_engine import config as C, exfx as M

R = pathlib.Path(__file__).resolve().parent
h = M.history(); fwd = M.forward(); path = pd.read_csv(C.OUT / "adr_path.csv", index_col=0)
gm = pd.read_csv(C.OUT / "geo_mix_method_check.csv", index_col=0)
i = pd.read_csv(C.I_MIX_3Q26)
u_I = {q: float(i[(i.term == "unit_size") & (i.quarter == q)].point_pp.iloc[0]) for q in ("2Q26", "3Q26")}
off_geo = float(gm.loc["2Q26", "diff_pp"]); off_unit = u_I["2Q26"] - float(h.loc["2Q26", "unit_size"])
off_los = float(fwd.loc["3Q26", "los_mix"]) - float(h.loc["2Q26", "los_mix"])          # forward minus in-core
print(f"offsets (forward construction minus in-core construction at 2Q26): geo {off_geo:+.3f}, unit {off_unit:+.3f}; "
      f"LOS switch (I forward 3Q26 minus H 2Q26 fill) {off_los:+.3f}")
sub = pd.read_csv(C.OUT / "geomix_subregional_term.csv").set_index("quarter").subgeo_pp
subf = pd.read_csv(C.OUT / "geomix_subregional_term_forward.csv").set_index("quarter").subgeo_pp
fxv = pd.read_csv(R / "C3_adr_under_fx_variants.csv")
rows = []
for q in ("3Q26", "4Q26"):
    by = float(path.loc[q, "adr_usd_base_year"]); sd_usd = by * float(path.loc[q, "band_half_pp"]) / 100
    st = C.STREET_ADR[q][0]; base = float(path.loc[q, "adr_usd"])
    dsub = float(subf[q]) - float(sub["2Q26"])
    dv1 = float(fxv[(fxv.quarter == q) & (fxv.variant == "V1_MAP_all17")].fx_pp.iloc[0]) - float(path.loc[q, "fx_pp"])
    for case, dbasis in (("A: LOS switch is a basis offset", -(off_geo + off_unit + off_los)),
                         ("B: LOS genuinely fell", -(off_geo + off_unit))):
        for fxlab, dfx in (("V0 identity FX", 0.0), ("V1 FX weights", dv1)):
            adr = base + by * (dbasis + dsub + dfx) / 100
            rows.append({"quarter": q, "case": case, "fx": fxlab, "d_exfx_basis_pp": dbasis, "d_subregional_netted_pp": dsub, "d_fx_pp": dfx,
                         "adr_usd": adr, "vs_street": adr - st, "p_print_ge_street": float(1 - stats.norm.cdf((st - adr) / sd_usd))})
    rows.append({"quarter": q, "case": "filed base", "fx": "V0 identity FX", "d_exfx_basis_pp": 0.0, "d_subregional_netted_pp": 0.0, "d_fx_pp": 0.0,
                 "adr_usd": base, "vs_street": base - st, "p_print_ge_street": float(path.loc[q, "p_print_ge_street"])})
d = pd.DataFrame(rows); pd.set_option("display.width", 250)
print(d.round(3).to_string(index=False)); d.to_csv(R / "C2_basis_bounded.csv", index=False)
# lap-only under the same two cases (the ladder's $171.71 row sits $0.38 ABOVE the Street as filed)
lap = pd.read_csv(C.OUT / "adr_scenarios.csv"); lap = lap[lap.rule.str.startswith("lap-only") & (lap.quarter == "4Q26")].adr_usd.iloc[0]
by = float(path.loc["4Q26", "adr_usd_base_year"])
for case, dbasis in (("A", -(off_geo + off_unit + off_los)), ("B", -(off_geo + off_unit))):
    print(f"lap-only 4Q26 filed {lap:.2f} (Street 171.33, {lap-171.33:+.2f}); case {case} basis-consistent {lap + by*dbasis/100:.2f}")
