"""Find explicit competitor mentions in the baseline descriptions of persistent exits.

This is a lead generator, not a cross-platform property matcher. Selection is the
team panel's conservative 90-day absence cohort of reviewed short-stay entire homes.
Granular descriptions and IDs remain in ignored raw storage.
"""
import csv
import gzip
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
PATTERN=re.compile(r"\b(?:vrbo|homeaway|abritel|fewo-direkt|expedia|houfy)\b|booking\.com",re.I)


def read(path):
    with path.open(encoding="utf-8-sig",newline="") as h:return list(csv.DictReader(h))


def write(path,rows,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(rows)


def main():
    source=ROOT/"data/raw/listing_churn_panel"
    manifest=read(source/"download_manifest.csv")
    rates=[r for r in read(ROOT/"data/processed/listing_churn_panel/market_rates.csv")
           if r["cohort"]=="reviewed_str_homes" and r["policy"]=="exclude_feb_may_negatives" and r["persistence_eligible"]=="True"]
    matches,summary=[],[]
    for metric in rates:
        market=metric["market"]
        outcomes={r["listing_id"]:r for r in read(source/f"{market}_listing_outcomes.csv")
            if r["policy"]=="exclude_feb_may_negatives" and r["status"]=="persistent_absence"
            and r["baseline_room_type"]=="Entire home/apt" and float(r["baseline_reviews_ltm"])>0
            and r["baseline_minimum_nights"] and float(r["baseline_minimum_nights"])<30}
        assert len(outcomes)==int(metric["persistent_90"]),(market,len(outcomes),metric["persistent_90"])
        item=min((r for r in manifest if r["market"]==market),key=lambda r:r["snapshot_start"])
        count=0
        seen=set()
        nonempty=0
        with gzip.open(ROOT/item["local_path"],"rt",encoding="utf-8-sig",newline="") as h:
            reader=csv.DictReader(h)
            if "description" not in reader.fieldnames:
                raise ValueError(f"{market}: baseline lacks description column")
            for r in reader:
                if r["id"] not in outcomes:continue
                if r["id"] in seen:
                    raise ValueError(f"{market}: duplicate baseline ID in screen")
                seen.add(r["id"])
                text=r.get("description","");found=list(PATTERN.finditer(text))
                nonempty+=bool(text.strip())
                if not found:continue
                count+=1;o=outcomes[r["id"]]
                matches.append(dict(market=market,listing_id=r["id"],title=r["name"],license=r.get("license",""),
                    platforms=" | ".join(sorted({m.group().lower() for m in found})),
                    baseline_complete=item["snapshot_complete"],last_present=o["last_present"],first_terminal_absence=o["first_terminal_absence"],
                    excerpts=" | ".join(text[max(0,m.start()-120):m.end()+180] for m in found),
                    explicit_urls=" | ".join(re.findall(r'https?://[^\s<>"\x27]+',text)),picture_url=r.get("picture_url",""),
                    candidate_replacement_id=o["candidate_replacement_id"]))
        if seen!=set(outcomes):
            raise ValueError(f"{market}: not every selected exit was found in baseline")
        summary.append(dict(market=market,reviewed_str_home_baseline=int(metric["baseline_ids"]),
            persistent_90_ids=len(outcomes),nonempty_descriptions=nonempty,baseline_competitor_mentions=count,
            interpretation="Explicit description mentions only; not verified cross-platform presence or migration"))
        print(f"{market}: {count} description leads from {len(outcomes)} persistent IDs",flush=True)
    fields=["market","listing_id","title","license","platforms","baseline_complete","last_present","first_terminal_absence","excerpts","explicit_urls","picture_url","candidate_replacement_id"]
    write(ROOT/"data/raw/listing_platform_history/baseline_platform_mentions.csv",matches,fields)
    write(ROOT/"data/processed/listing_platform_history/mention_screen.csv",summary,list(summary[0]))


if __name__=="__main__":main()
