# Results Artifacts

- `main_runs.csv`, `main_summary.csv` — 10-seed / 1,200-FE PANCAKE deepening pilot.
- `main_pairwise_holm.csv`, `main_statistics.json` — paired inferential tests.
- `main_convergence.csv`, `ablation_convergence.csv`, `tpp_style_convergence.csv` — median/IQR best-so-far RPD over fixed FE checkpoints.
- `ablation_runs.csv`, `ablation_summary.csv` — controlled A0–A3 ablation.
- `ablation_pairwise_holm.csv`, `ablation_statistics.json` — ablation inferential tests.
- `operator_telemetry.csv`, `operator_aggregate.csv` — A3 low-level operator behavior.
- `family_algorithm_median_rpd.csv` — landscape-family breakdown.
- `tpp_style_*` — 5-seed / 2,400-FE protocol-regenerated TPP-style transfer pilot.
- `figures/` — automatically generated paper-oriented plots.
- `study_manifest.json` — current protocol/provenance snapshot.

Rerun `Research/experiments/export_materials.py` after experiments to refresh derived tables.
