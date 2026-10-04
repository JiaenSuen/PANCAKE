# ResearchBenchmark

This folder contains the canonical Python benchmark used for the reported PANCAKE results.

- `meta_study.py` — generates the 10 reported test maps, runs 10 algorithms with a 1,200-evaluation budget, and exports raw/statistical results.
- `fox_parameter_screen.py` — development-only screen for the DFOX-APNS fox population size using disjoint map indices 3–4.
- `algorithms/dfox_base.py` — direct discrete FOX baseline with the original fixed 50/50 phase logic.
- `algorithms/dfox_apns.py` — DFOX-APNS canonical implementation.
- `algorithms/dwoa_avns.py` — DWOA-AVNS canonical implementation.
- `meta_datasets/` — 10 test maps used for Table 1/2.
- `dev_datasets/` — 10 disjoint FOX development maps.
- `meta_results/` — raw runs, summary statistics, exact-gap results, Table 1/2 CSVs, Friedman result, and FOX setting screen.
- `export_report.py` — rebuilds the compact CSV tables and paper-style Table 1 PNG.

Run `python fox_parameter_screen.py`, then `python meta_study.py`, then `python export_report.py`.
