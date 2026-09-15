# L3 ADR/hotel independent-review repair — immutable outputs

2026-09-13 · parent reviewed `adr_hotel` implementation independently; author applied the repair. This note supersedes only the original results/README's same-directory reproduction instructions. Original preregistration, results and output files remain intact.

## Finding and repair

The initial runner wrote to its fixed existing package output directory on a repeat run. Although the bytes were deterministic, that behavior violated the user's copy-never-overwrite and immutable bundle requirements. The parent identified this as a material implementation finding.

The CLI now requires `--out NEW_DIRECTORY`. The runner checks `Path.exists()` and raises `FileExistsError` before writing if the destination exists. A new regression creates an existing directory with a sentinel, attempts the run, and proves the sentinel and directory contents are unchanged. The README now explains how to choose a fresh version each time.

## Verification

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/l3_adr_hotel_v1/run.py --out data/processed/forecast_methods/l3_adr_hotel_v1_rebuild
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -m unittest discover -s analysis/src/forecast_methods/l3_adr_hotel_v1 -p 'test_*.py' -v
```

Both commands exited 0. The fresh rebuild retained 14/14 integrity gates and 86 adapter rows; tests passed 13/13 in 0.088 seconds. SHA-256 comparison by filename shows **17/17 output files byte-identical** to the preserved original `l3_adr_hotel_v1/`; zero differing hashes. No numerical rule, criterion, evidence label, source input, original result or model decision changed. The recorded directory now exists, so another reproduction must choose another nonexistent version; reusing this exact path should fail.

## RESUME

The lead can integrate the original immutable v1 outputs because all 17 files match the guarded runner's new-directory reproduction exactly, or use the identical rebuild. Future runs require a fresh output directory. The parent finding is resolved; the research limitations and pending adoption stated in `L3_ADR_HOTEL_RESULTS.md` remain unchanged.
