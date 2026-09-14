"""State check, batch/job generation and catalogue merge for the GitHub alt-data cataloguing run.

Usage (from anywhere; paths resolve relative to this file):
    python state.py                 # print the state summary (JSON)
    python state.py --batches       # also write reviews/batches_pending.json (unreviewed candidates, 5 per batch)
    python state.py --jobs          # also write samples/sample_jobs_pending.json (verdict=sample, no manifest yet)
    python state.py --merge         # write research/notes/github_altdata/catalog.csv and CATALOG_SUMMARY.md

Ground truth is on disk, never the workflow cache:
    scouts/scout_NNN.json      one per Sonnet scout (N_SCOUTS expected)
    reviews/review_NNN.json    one per Opus review batch; verdicts keyed by repo URL
    samples/<slug>/manifest.json   one per Fable sample pull (sampled true/false)
"""
from __future__ import annotations

import csv
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]                      # worktree root
BASE = ROOT / "data" / "processed" / "github_altdata"
SCOUTS = BASE / "scouts"
REVIEWS = BASE / "reviews"
SAMPLES = BASE / "samples"
NOTES = ROOT / "research" / "notes" / "github_altdata"
N_SCOUTS = 262                              # 123 themes x 2 modalities + 16 wildcard lenses
BATCH = 25                                  # scope cut 14 Sep 08:50: was 5 with per-repo verification
REVIEW_TIERS = {"high", "medium"}           # scout 'low' candidates are catalogued from scout metadata only, never sent to Opus
SAMPLE_PRIORITY_MAX = 1                     # only priority-1 'sample' verdicts get a Fable pull, one per source_family
RANK = {"high": 3, "medium": 2, "low": 1}


def key_of(url: str) -> str:
    m = re.search(r"github\.com/([^/\s#?]+)/([^/\s#?]+)", (url or "").lower())
    if m:
        repo = re.sub(r"\.git$", "", m.group(2))
        return f"github:{m.group(1)}/{repo}"
    return "other:" + (url or "").lower().rstrip("/")


def load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return {"_error": str(e)}


def scout_state():
    present, bad = {}, []
    for p in sorted(SCOUTS.glob("scout_*.json")):
        idx = int(p.stem.split("_")[1])
        d = load_json(p)
        if "_error" in d or not isinstance(d.get("candidates"), list):
            bad.append(idx)
            continue
        present[idx] = d
    missing = [i for i in range(N_SCOUTS) if i not in present]
    return present, missing, bad


def unique_candidates(present):
    merged = {}
    raw = 0
    for idx, s in present.items():
        theme = s.get("theme", f"scout {idx}")
        for c in s.get("candidates", []):
            if not isinstance(c, dict) or not c.get("url"):
                continue
            raw += 1
            k = key_of(c["url"])
            prev = merged.get(k)
            if prev is None:
                merged[k] = {"key": k, **c, "hits": 1, "themes": [theme], "why_all": [c.get("why_useful", "")]}
            else:
                prev["hits"] += 1
                if theme not in prev["themes"]:
                    prev["themes"].append(theme)
                prev["why_all"].append(c.get("why_useful", ""))
                if RANK.get(c.get("potential"), 0) > RANK.get(prev.get("potential"), 0):
                    prev["potential"] = c.get("potential")
                if len(c.get("what_it_holds") or "") > len(prev.get("what_it_holds") or ""):
                    prev["what_it_holds"] = c.get("what_it_holds")
    return merged, raw


def review_state():
    verdicts, files = {}, 0
    for p in sorted(REVIEWS.glob("review_*.json")):
        d = load_json(p)
        if isinstance(d, list):                 # some agents wrote the bare verdict array
            d = {"verdicts": d}
        if not isinstance(d, dict) or "_error" in d:
            continue
        files += 1
        for v in d.get("verdicts", []):
            if isinstance(v, dict) and v.get("url"):
                verdicts.setdefault(key_of(v["url"]), {**v, "_file": p.name})
    return verdicts, files


def review_tier_of(v) -> str:
    """Batches < 500: Opus per-repo verification (pre-cut); 500-504: Opus metadata triage (high tier);
    505+: Sonnet metadata triage (medium tier). Derived from the review file name."""
    try:
        b = int(str(v.get("_file", "")).split("_")[1].split(".")[0])
    except (IndexError, ValueError):
        return "unknown"
    return "opus-verified (pre-cut)" if b < 500 else ("opus-triage (high tier)" if b < 505 else "sonnet-triage (medium tier)")


def safe_slug(s: str, fallback: str) -> str:
    s = re.sub(r"[^a-z0-9_-]+", "-", (s or "").lower()).strip("-")[:60]
    return s or fallback


def sample_jobs(verdicts):
    """Priority-1 'sample' verdicts, one per source_family (first seen wins). Verdicts from the pre-cut
    per-repo review (no priority field) count as priority 1 only if usefulness is possibly_useful."""
    jobs, seen, families = [], set(), set()
    for k, v in verdicts.items():
        if v.get("verdict") != "sample":
            continue
        pr = v.get("priority")
        if pr is None:
            pr = 1 if v.get("usefulness") == "possibly_useful" else 2
        if pr > SAMPLE_PRIORITY_MAX:
            continue
        fam = (v.get("source_family") or "").strip().lower()
        if fam:
            if fam in families:
                continue
            families.add(fam)
        slug = safe_slug(v.get("slug"), re.sub(r"[^a-z0-9]+", "-", k.split(":", 1)[1]))
        if slug in seen:
            slug = slug[:50] + "-" + re.sub(r"[^a-z0-9]+", "-", k.split(":", 1)[1])[-9:]
        seen.add(slug)
        jobs.append({"slug": slug, "url": v["url"], "category": v.get("category"), "data_kind": v.get("data_kind"),
                     "one_line": v.get("one_line"), "abnb_use": v.get("abnb_use"), "sample_plan": v.get("sample_plan"),
                     "tos_or_license_flag": v.get("tos_or_license_flag")})
    return jobs


def sample_state(jobs):
    done, pending = [], []
    for j in jobs:
        man = SAMPLES / j["slug"] / "manifest.json"
        (done if man.exists() else pending).append(j)
    return done, pending


def newest_mtime():
    ts = [p.stat().st_mtime for d in (SCOUTS, REVIEWS, SAMPLES) if d.exists() for p in d.rglob("*") if p.is_file()]
    return max(ts) if ts else None


def main(argv):
    present, missing, bad = scout_state()
    merged, raw = unique_candidates(present)
    verdicts, review_files = review_state()
    unreviewed_all = [c for k, c in merged.items() if k not in verdicts]
    unreviewed = [c for c in unreviewed_all if c.get("potential") in REVIEW_TIERS]     # the Opus pool
    n_sample_verdicts = sum(1 for v in verdicts.values() if v.get("verdict") == "sample")
    jobs = sample_jobs(verdicts)
    done, pending = sample_state(jobs)
    nm = newest_mtime()
    counts = {}
    for v in verdicts.values():
        counts[v.get("verdict")] = counts.get(v.get("verdict"), 0) + 1
    state = {
        "scouts_present": len(present), "scouts_expected": N_SCOUTS, "scouts_missing": missing, "scouts_bad_json": bad,
        "raw_candidates": raw, "unique_candidates": len(merged),
        "review_files": review_files, "verdicts": len(verdicts), "verdict_counts": counts,
        "unreviewed_candidates_total": len(unreviewed_all),
        "unreviewed_in_opus_pool_high_medium": len(unreviewed),
        "sample_verdicts_all": n_sample_verdicts,
        "sample_jobs_priority1_deduped": len(jobs), "samples_done": len(done), "samples_pending": len(pending),
        "minutes_since_last_file_write": None if nm is None else round((time.time() - nm) / 60, 1),
    }
    next_step = ("run wf_scouts.js with args.only=scouts_missing" if missing or bad else
                 "run wf_reviews.js on reviews/batches_pending.json" if unreviewed else
                 "run wf_samples.js on samples/sample_jobs_pending.json" if pending else
                 "all stages complete: run --merge, write the note, notify the user, delete the cron")
    state["next_step"] = next_step
    if bad:
        state["scouts_missing"] = sorted(set(missing) | set(bad))
    # keep the printed state compact: the full index list goes to a file the resume workflow reads
    (SCOUTS / "scouts_missing.json").write_text(json.dumps(state["scouts_missing"]), encoding="utf-8")
    state["scouts_missing"] = f"{len(state['scouts_missing'])} missing (list in scouts/scouts_missing.json)"
    print(json.dumps(state, indent=2))

    if "--batches" in argv:
        # high tier -> Opus batches first, then medium tier -> Sonnet batches (Krish, 14 Sep 09:00)
        existing = [int(p.stem.split("_")[1]) for p in REVIEWS.glob("review_*.json")]
        start = max(existing + [-1]) + 1
        start = max(start, 500) if existing and max(existing) < 500 else start   # keep resume batches in a distinct range
        batches, tiers = [], {"opus": [], "sonnet": []}
        for tier, model in (("high", "opus"), ("medium", "sonnet")):
            pool = sorted((c for c in unreviewed if c.get("potential") == tier), key=lambda c: (c.get("category") or ""))
            for j in range(0, len(pool), BATCH):
                b = start + len(batches)
                batches.append({"b": b, "items": pool[j:j + BATCH]})
                tiers[model].append(b)
        # one small file per batch; the workflow only receives the id list (keeps the tool-call args tiny)
        pend = REVIEWS / "pending"
        pend.mkdir(exist_ok=True)
        for bt in batches:
            (pend / f"batch_{bt['b']:03d}.json").write_text(json.dumps(bt["items"], indent=1), encoding="utf-8")
        (REVIEWS / "batches_pending_ids.json").write_text(json.dumps(tiers), encoding="utf-8")
        print(f"wrote {len(batches)} batch files to {pend} (b {start}..{start + len(batches) - 1}); ids in reviews/batches_pending_ids.json")
        print("ARGS=" + json.dumps({"opus_batch_ids": tiers["opus"], "sonnet_batch_ids": tiers["sonnet"]}))

    if "--jobs" in argv:
        jd = SAMPLES / "_jobs"
        jd.mkdir(exist_ok=True)
        for j in pending:
            (jd / f"{j['slug']}.json").write_text(json.dumps(j, indent=1), encoding="utf-8")
        slugs = [j["slug"] for j in pending]
        (SAMPLES / "sample_jobs_pending_slugs.json").write_text(json.dumps(slugs), encoding="utf-8")
        print(f"wrote {len(pending)} pending job files to {jd}; slugs in samples/sample_jobs_pending_slugs.json")
        print("SLUGS=" + json.dumps(slugs))

    if "--merge" in argv:
        NOTES.mkdir(parents=True, exist_ok=True)
        manifests = {p.parent.name: load_json(p) for p in SAMPLES.glob("*/manifest.json")}
        slug_by_key = {key_of(j["url"]): j["slug"] for j in jobs}
        rows = []
        for k, c in merged.items():
            v = verdicts.get(k, {})
            slug = slug_by_key.get(k)
            man = manifests.get(slug, {}) if slug else {}
            rows.append({
                "url": c.get("url"), "name": c.get("name"), "category": v.get("category") or c.get("category"),
                "data_kind": v.get("data_kind") or c.get("data_kind"), "scout_potential": c.get("potential"),
                "scout_hits": c.get("hits"), "themes": " | ".join(c.get("themes", []))[:300],
                "review_tier": (review_tier_of(v) if v else ("scout-only (low potential, not sent to Opus)" if c.get("potential") == "low" else "unreviewed")),
                "usefulness": v.get("usefulness"), "verdict": v.get("verdict"), "priority": v.get("priority"),
                "source_family": v.get("source_family"), "one_line": v.get("one_line"),
                "abnb_use": v.get("abnb_use"), "sample_plan": v.get("sample_plan"),
                "tos_or_license_flag": v.get("tos_or_license_flag"), "duplicate_of_existing": v.get("duplicate_of_existing"),
                "geography": c.get("geography"), "time_coverage": c.get("time_coverage"), "license": c.get("license"),
                "what_it_holds": c.get("what_it_holds"), "review_reasoning": v.get("reasoning"),
                "sample_slug": slug, "sampled": man.get("sampled"), "sample_bytes": man.get("total_bytes"),
                "sample_rows": man.get("rows"), "sample_date_range": man.get("date_range"), "sample_issues": man.get("issues"),
            })
        order = {"sample": 0, "catalog_only": 1, "discard": 2, None: 3}
        rows.sort(key=lambda r: (order.get(r["verdict"], 3), r["category"] or "", -(r["scout_hits"] or 0)))
        out = NOTES / "catalog.csv"
        with out.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["url"])
            w.writeheader()
            w.writerows(rows)
        by_cat = {}
        for r in rows:
            by_cat.setdefault(r["category"], {"sample": 0, "catalog_only": 0, "discard": 0, "unreviewed": 0})
            by_cat[r["category"]][r["verdict"] or "unreviewed"] += 1
        lines = ["# GitHub alt-data catalogue: summary counts", "", f"Generated by state.py --merge. {len(rows)} unique repositories, "
                 f"{raw} raw scout hits, {len(verdicts)} reviewed, {len(jobs)} sample jobs ({len(done)} with a manifest).", "",
                 "| category | sample | catalog_only | discard | unreviewed |", "|---|---|---|---|---|"]
        for cat, d in sorted(by_cat.items(), key=lambda kv: -kv[1]["sample"]):
            lines.append(f"| {cat} | {d['sample']} | {d['catalog_only']} | {d['discard']} | {d['unreviewed']} |")
        (NOTES / "CATALOG_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"wrote {out} ({len(rows)} rows) and CATALOG_SUMMARY.md")


if __name__ == "__main__":
    main(sys.argv[1:])
