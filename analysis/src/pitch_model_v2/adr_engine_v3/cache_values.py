"""adr_engine / cache_values.py — make a *complete* copy of the workbook: every formula evaluated and stored
as a cached value, so the file reads correctly in Excel, Numbers, Sheets or a viewer without a recalculation pass,
while the formulas, charts, styles and links are left exactly as the builder wrote them.

openpyxl writes <f> but never <v>, so a freshly built workbook shows blanks until Excel opens it. This module
computes every formula with the `formulas` engine and writes the results back into the sheet XML as <v>, which is
the cache Excel itself would write. It also sets fullCalcOnLoad so Excel still recalculates on open and the cache
can never go stale silently.

Run: PYTHONPATH=analysis/src python3 -m pitch_model_v2.adr_engine.cache_values            # default: build the copy
     PYTHONPATH=analysis/src python3 -m pitch_model_v2.adr_engine.cache_values <file>     # cache in place
"""
import formulas, numpy as np, re, shutil, zipfile, sys
from pathlib import Path
import xml.etree.ElementTree as ET

if len(sys.argv) > 1:
    SRC = Path(sys.argv[1])
else:                                      # default: copy the official model, then cache the copy
    from . import config as C
    SRC = C.XLSX.with_name(C.XLSX.stem + "_complete.xlsx")
    shutil.copy(C.XLSX, SRC)
    print(f"copied {C.XLSX.name} -> {SRC.name}")
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
ET.register_namespace("", NS)

def scalar(v):
    try:
        a = np.asarray(getattr(v, "value", v), dtype=object).ravel()
    except Exception:
        return None
    return a[0] if a.size else None

xl = formulas.ExcelModel().loads(str(SRC)).finish()
sol = xl.calculate()
vals = {}
for k, v in sol.items():
    m = re.match(r"'\[.*?\]([^']+)'!([A-Z]+\d+)$", k)
    if m:
        vals[(m.group(1).upper(), m.group(2))] = scalar(v)
print(f"engine produced {len(vals)} cell values")

# map sheet xml part -> sheet name
with zipfile.ZipFile(SRC) as z:
    wbx = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid2tgt = {r.get("Id"): r.get("Target") for r in rels}
    RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    part2name = {}
    for sh in wbx.find(f"{{{NS}}}sheets"):
        tgt = rid2tgt[sh.get(RNS)].lstrip("/")
        part2name[tgt if tgt.startswith("xl/") else "xl/" + tgt] = sh.get("name")
    parts = {n: z.read(n) for n in z.namelist()}

written = skipped = 0
missing = []
for part, name in part2name.items():
    root = ET.fromstring(parts[part])
    key = name.upper()
    for c in root.iter(f"{{{NS}}}c"):
        f = c.find(f"{{{NS}}}f")
        if f is None:
            continue
        val = vals.get((key, c.get("r")))
        if val is None or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
            missing.append(f"{name}!{c.get('r')}"); skipped += 1; continue
        for old in c.findall(f"{{{NS}}}v"):
            c.remove(old)
        v = ET.SubElement(c, f"{{{NS}}}v")
        if isinstance(val, (bool, np.bool_)):
            c.set("t", "b"); v.text = "1" if val else "0"
        elif isinstance(val, (int, float, np.integer, np.floating)):
            c.attrib.pop("t", None); v.text = repr(float(val))
        else:
            s = str(val)
            if s.startswith("#"):
                c.set("t", "e")
            else:
                c.set("t", "str")
            v.text = s
        c.remove(f); c.insert(0, f)          # schema order: <f> then <v>
        written += 1
    parts[part] = ET.tostring(root, xml_declaration=True, encoding="UTF-8")

# make Excel recalculate on open as well, so the cache can never go stale silently
wb_root = ET.fromstring(parts["xl/workbook.xml"])
calc = wb_root.find(f"{{{NS}}}calcPr")
if calc is None:
    calc = ET.SubElement(wb_root, f"{{{NS}}}calcPr")
calc.set("fullCalcOnLoad", "1")
parts["xl/workbook.xml"] = ET.tostring(wb_root, xml_declaration=True, encoding="UTF-8")

tmp = SRC.with_suffix(".tmp.xlsx")
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
    for n, data in parts.items():
        out.writestr(n, data)
shutil.move(tmp, SRC)
print(f"cached {written} formula results, skipped {skipped}")
if missing:
    print("unresolved:", missing[:12], "..." if len(missing) > 12 else "")
