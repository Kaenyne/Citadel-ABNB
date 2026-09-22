"""C8 recompute/cross-check script. Reads only committed CSVs; writes only into receipts/C8/.
No margin_build or forecast script is executed. Historical fcf_ex_sbc is recomputed from
abnb_fcf_bridge.csv; sbc_total (abnb_quarterly_cost_stack_exsbc.csv) is cross-checked against
fcf_bridge's letter-sourced sbc for an internal-consistency check.
"""
import csv, json

QUARTERS = ["1Q23","2Q23","3Q23","4Q23","1Q24","2Q24","3Q24","4Q24",
            "1Q25","2Q25","3Q25","4Q25","1Q26","2Q26"]

bridge = {r["period"]: r for r in csv.DictReader(open("data/processed/abnb_fcf_bridge.csv"))}
stack = {r["quarter"]: r for r in csv.DictReader(open("data/processed/abnb_quarterly_cost_stack_exsbc.csv"))}

rows = []
sbc_mismatches = []
gap_mismatches = []
for q in QUARTERS:
    b = bridge[q]
    fcf = float(b["fcf"])
    capex = abs(float(b["capex"]))
    sbc = float(b["sbc"])
    fcf_ex_sbc = fcf - sbc
    gap = float(b["fcf_check_gap"])
    rows.append({"period": q, "fcf_musd": fcf, "capex_musd": capex, "sbc_musd": sbc,
                 "fcf_ex_sbc_musd": fcf_ex_sbc, "fcf_check_gap": gap})
    if abs(gap) > 0.5:
        gap_mismatches.append((q, gap))
    s = stack.get(q)
    if s is not None:
        component_sum = float(s["sbc_ops"]) + float(s["sbc_pd"]) + float(s["sbc_sm"]) + float(s["sbc_ga"])
        stack_total = float(s["sbc_total"])
        stack_letter = float(s["sbc_total_letter"])
        if abs(stack_total - sbc) > 0.5:
            sbc_mismatches.append({"period": q, "fcf_bridge_sbc": sbc,
                                    "exsbc_sbc_total_field": stack_total,
                                    "exsbc_sbc_total_letter_field": stack_letter,
                                    "exsbc_component_sum_ops_pd_sm_ga": component_sum})

with open("data/processed/pitch_model_v2/receipts/C8/c8_history_fcf_exsbc.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["period","fcf_musd","capex_musd","sbc_musd","fcf_ex_sbc_musd","fcf_check_gap"])
    w.writeheader()
    w.writerows(rows)

with open("data/processed/pitch_model_v2/receipts/C8/c8_sbc_crosscheck.json", "w") as f:
    json.dump({"sbc_mismatches_vs_exsbc_stack": sbc_mismatches,
               "fcf_check_gap_over_0.5musd": gap_mismatches}, f, indent=2)

print(f"quarters checked: {len(rows)}")
print(f"fcf_check_gap > $0.5M in bridge (should be ~0 by construction): {gap_mismatches}")
print(f"sbc_total (exsbc_stack) vs sbc (fcf_bridge, letter-sourced) mismatches: {json.dumps(sbc_mismatches, indent=2)}")
