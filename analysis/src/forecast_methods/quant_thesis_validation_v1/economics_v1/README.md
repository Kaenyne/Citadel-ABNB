# Q7 economic bridge

Read-only audit of immutable L4 financial tables and a bounded conditional operating/cash/share bridge. No workbook, forecast, registry or source data is edited. Python standard library only; no fitted parameters.

From the worktree root:

```powershell
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B analysis/src/forecast_methods/quant_thesis_validation_v1/economics_v1/run.py --out data/processed/forecast_methods/quant_thesis_validation_v1/economics_v1/results_v1
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -m unittest discover -s analysis/src/forecast_methods/quant_thesis_validation_v1/economics_v1 -p 'test_*.py' -v
```

Always use a fresh output suffix. The runner refuses existing destinations and locations outside its exclusive data directory. It binds immutable sources, checks all annual identities, and records each sensitivity assumption and horizon. Source assumptions are in the corresponding docs `economics_v1/ASSUMPTIONS_v1.md`; the final result note distinguishes arithmetic verification from investment evidence. Tables are analytical CSV intermediates, not a replacement spreadsheet or a duplicate full financial model.
