"""
WP-K reviews index 2023 vintage, step 1: pull the 116-market Mar-May 2023 Inside Airbnb reviews mirror
from Hugging Face (alujjdnd/Airbnb-Mar-2022-2023, raw_dl/) into the gitignored raw store
C:/Users/krish/abnb_ia_capture/ia_reviews_vintage2023/ under the E3 naming convention
<market_key>_<dump_date>_reviews.csv.gz, then verify gzip integrity and write the manifest.

Never writes into MAIN/data/raw/inside_airbnb_reviews (that would silently change the v1 pipeline).
Resumable: a file whose size already equals bytes_gz in the HF index is skipped; partial files are
resumed with curl -C -. The two 75-byte china files are skipped.

Source: Inside Airbnb (https://insideairbnb.com/get-the-data/), CC BY 4.0, mirrored on Hugging Face.
Run: python analysis/src/q3nowcast_v2/E/V1_download_vintage2023.py [--priority-only] [--verify-only]
"""
import argparse, gzip, hashlib, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
import pandas as pd

WT = Path(__file__).resolve().parents[4]
RAW = Path(r"C:\Users\krish\abnb_ia_capture\ia_reviews_vintage2023")
OUT = WT / "data/processed/q3nowcast_v2/E"
IDX = WT / "data/processed/github_altdata/samples/hf-buenosaires-airbnb-reviews/hf_raw_dl_file_index.csv"
BASE = "https://huggingface.co/datasets/alujjdnd/Airbnb-Mar-2022-2023/resolve/main/"

# raw_dl stem (minus date) -> market_key in market_geo.csv where they differ
KEY_MAP = {
    "japan_kantō_tokyo": "japan_kanto_tokyo",
    "ireland_2023-03-30_data_reviews.csv.gz": "ireland",
    "malta_2023-03-31_data_reviews.csv.gz": "malta",
    "new-zealand_2023-05-13_data_reviews.csv.gz": "new-zealand",
}
SKIP = {"china_beijing_beijing", "china_shanghai_shanghai"}      # 75-byte empties
# NYC first, then the 13-city listings panel markets, then everything else largest first
PRIORITY = ["united-states_ny_new-york-city", "united-kingdom_england_london", "france_ile-de-france_paris",
            "italy_lazio_rome", "spain_catalonia_barcelona", "the-netherlands_north-holland_amsterdam",
            "germany_be_berlin", "united-states_ca_los-angeles", "australia_nsw_sydney",
            "australia_vic_melbourne", "canada_on_toronto", "mexico_df_mexico-city",
            "brazil_rj_rio-de-janeiro", "portugal_lisbon_lisbon", "japan_kanto_tokyo",
            "united-states_hi_hawaii", "argentina_ciudad-autónoma-de-buenos-aires_buenos-aires"]


def log(m):
    print(f"{time.strftime('%H:%M:%S')} {m}", flush=True)


def plan():
    idx = pd.read_csv(IDX)
    rows = []
    for r in idx.itertuples():
        fn = r.path.split("/")[-1]
        if fn.endswith(".csv.gz.csv.gz"):                       # mangled country-level names
            stem = fn[: -len(".csv.gz")]
            mk = KEY_MAP[stem]
        else:
            stem = fn[: -len(".csv.gz")]
            mk = stem[: -len("_" + r.dump_date)]
            mk = KEY_MAP.get(mk, mk)
        if mk in SKIP:
            continue
        rows.append(dict(market_key=mk, dump_date=r.dump_date, hf_path=r.path, bytes_expected=int(r.bytes_gz),
                         dest=RAW / f"{mk}_{r.dump_date}_reviews.csv.gz"))
    p = pd.DataFrame(rows)
    p["prio"] = p.market_key.map({k: i for i, k in enumerate(PRIORITY)}).fillna(999)
    return p.sort_values(["prio", "bytes_expected"], ascending=[True, False]).reset_index(drop=True)


def gz_ok(path: Path):
    """Read the whole gzip stream (integrity check) and return the row count of newlines seen."""
    try:
        n = 0
        with gzip.open(path, "rb") as f:
            while True:
                b = f.read(1 << 24)
                if not b:
                    break
                n += b.count(b"\n")
        return True, n
    except Exception as e:
        return False, str(e)


def sha256(path: Path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def fetch(row, tries=4):
    dest: Path = row.dest
    for t in range(tries):
        if dest.exists() and dest.stat().st_size == row.bytes_expected:
            return True
        url = BASE + quote(row.hf_path)
        cmd = ["curl", "-sSL", "--retry", "3", "--retry-delay", "5", "-C", "-", "-o", str(dest), url]
        rc = subprocess.run(cmd, capture_output=True, text=True)
        if dest.exists() and dest.stat().st_size == row.bytes_expected:
            return True
        if dest.exists() and dest.stat().st_size > row.bytes_expected:
            dest.unlink()                                       # a range error appended garbage: restart
        log(f"  retry {t + 1} {dest.name} rc={rc.returncode} size={dest.stat().st_size if dest.exists() else 0} "
            f"{rc.stderr.strip()[:200]}")
        time.sleep(10)
    return False


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--priority-only", action="store_true")
    ap.add_argument("--verify-only", action="store_true")
    a = ap.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    p = plan()
    if a.priority_only:
        p = p[p.prio < 999]
    log(f"{len(p)} files planned, {p.bytes_expected.sum() / 1e9:.2f} GB")
    if not a.verify_only:
        done = 0
        for i, r in enumerate(p.itertuples(), 1):
            ok = fetch(r)
            done += ok
            log(f"[{i}/{len(p)}] {'ok ' if ok else 'FAIL'} {r.dest.name} {r.bytes_expected / 1e6:.1f} MB")
        log(f"download pass complete: {done}/{len(p)}")
    # verify + manifest (resumable: reuse rows already in the manifest with a matching size)
    mp = OUT / "raw_manifest_vintage2023.csv"
    prev = pd.read_csv(mp) if mp.exists() else pd.DataFrame()
    rows = []
    for r in p.itertuples():
        if not r.dest.exists():
            log(f"MISSING {r.dest.name}")
            continue
        b = r.dest.stat().st_size
        if len(prev) and (prev.path == str(r.dest)).any() and int(prev[prev.path == str(r.dest)].bytes.iloc[0]) == b:
            rows.append(prev[prev.path == str(r.dest)].iloc[0].to_dict())
            continue
        ok, n = gz_ok(r.dest)
        if not ok:
            log(f"GZIP FAIL {r.dest.name}: {n}")
            continue
        rows.append(dict(market_key=r.market_key, dump_date=r.dump_date, path=str(r.dest), bytes=b,
                         bytes_expected=r.bytes_expected, size_match=(b == r.bytes_expected),
                         sha256=sha256(r.dest), n_lines=n,
                         url=BASE + r.hf_path, pulled_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")))
        log(f"verified {r.dest.name} lines={n}")
    m = pd.DataFrame(rows)
    m.to_csv(mp, index=False, encoding="utf-8")
    log(f"manifest {mp} {len(m)} rows; size_match all: {bool(m.size_match.all()) if len(m) else None}")
