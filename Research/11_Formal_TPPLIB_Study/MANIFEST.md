# Formal TPPLIB Study — Evidence Manifest

This file is the entry point for the canonical external experiment. It separates **raw execution records**, **reference-safe derived evidence**, **secondary reference diagnostics**, and **archived pre-audit artifacts**.

## A. Frozen protocol / provenance

- `PROTOCOL.md` — experimental contract: instances, seeds, budget, methods, metrics, statistical unit.
- `EXPERIMENT_RECORD.md` — execution record and audit decisions.
- `ENVIRONMENT.txt` — runtime environment snapshot.
- `REFERENCE_HASHES.txt` — input/reference hashes captured for reproducibility.
- `REFERENCE_SEMANTICS_AUDIT.md` — mandatory reference-status correction.
- `INSTANCE_STRATIFICATION.md` — frozen small/medium/large and density definitions.

## B. Raw canonical execution

- `results/formal_runs.csv` — 3,000 raw final-run records. Historical baseline-reference columns are preserved but superseded.
- `results/formal_convergence.csv` — raw convergence checkpoints.
- `results/instance_manifest.csv` — 100 official instance descriptors.
- `results/study_manifest.json` — seeds, FE checkpoints, density thresholds, analysis policy.

## C. Canonical manuscript-facing derived evidence

Use these files for the paper:

- `results/formal_runs_reference_safe.csv`
- `results/formal_convergence_reference_safe.csv`
- `results/overall_reference_safe_summary.csv`
- `results/instance_method_medians_reference_safe.csv`
- `results/pairwise_reference_safe_holm.csv`
- `results/stratified_reference_safe_profiles.csv`
- `results/VK_scaling_grid_reference_safe.csv`
- `results/mechanism_scaling_degradation.csv`
- `results/instance_structure_correlations.csv`
- `results/route_purchase_decomposition.csv`
- `results/budget_efficiency_reference_safe_summary.csv`
- `results/convergence_reference_safe_summary.csv`
- `results/performance_profile.csv`
- `results/formal_statistics_reference_safe.json`

## D. Explicit external-reference layers

- `results/reference_registry.csv` — per-instance status/provenance.
- `results/literature_BKS_validation.csv` — 11 independently supported open-instance BKS checks.
- `results/market_cardinality_closed_candidate_subset.csv` — secondary 88-row market-count diagnostic only.

## E. Instance-stratification support

- `results/instance_stratification_summary.csv`
- `results/scale_by_market_assortment_counts.csv`
- `results/scale_by_product_supply_counts.csv`
- `results/VK_instance_counts.csv`

## F. Manuscript figures

Canonical raster figures are under `figures/formal_*`:

- overall RPD distribution;
- convergence / anytime behavior;
- scaling degradation;
- performance profile;
- instance density map;
- route/purchase decomposition;
- market-assortment interaction;
- product-dimension degradation;
- overall component excess.

TikZ conceptual figures and LaTeX result tables are maintained in `Research/07_Paper_Materials/`.

## G. Archived / superseded artifacts

- `results/archived_legacy_reference_analysis/`
- `figures/archived_legacy_reference/`
- `legacy_scripts/`

These are retained for provenance only. They were produced before the reference-semantics audit and must not be cited as canonical evidence.
