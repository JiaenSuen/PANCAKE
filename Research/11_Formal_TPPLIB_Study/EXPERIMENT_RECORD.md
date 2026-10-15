# Canonical Experiment Record

## Frozen design

| Item | Value |
|---|---|
| Benchmark | EEuclideo Class-3 U-TPP |
| Instance grid | V={50,100,150,200,250} × K={50,100,150,200} × 5 |
| Instances | 100 |
| Methods | TPP-ILS, TPP-VNS, TPP-DFOX |
| Seeds | 10 paired seeds |
| FE budget | 1,200 objective evaluations |
| Total canonical runs | 3,000 |
| Representation | market subset + market order → induced procurement |
| Distance | truncated Euclidean for EEuclideo (validated against supplied TPP parser) |
| Primary statistical unit | per-instance median over 10 seeds |
| Primary comparison metric | observed RPD vs canonical pooled best on same instance |
| External reference layer | 11 literature BKS open instances; 88 legacy closed-reference candidates kept secondary |

## Structural stratification

- `small`: `V <= 100` (40 instances)
- `medium`: `150 <= V <= 200` (40 instances)
- `large`: `V = 250` (20 instances)
- `offers_per_product`: total offers / K
- `offers_per_market`: total offers / (V-1)
- `normalized_offer_density`: total offers / ((V-1)K)
- density categories: global tertiles frozen in `instance_manifest.csv`

## Canonical outputs

- `results/formal_runs.csv` — original raw run export; its historical `OPT/gap_opt_pct` columns are superseded by the reference audit.
- `results/formal_runs_reference_safe.csv` — canonical run table for paper analysis.
- `results/instance_method_medians_reference_safe.csv` — 300 instance×method medians used by Friedman/Wilcoxon.
- `results/pairwise_reference_safe_holm.csv` — paired inference and effect sizes.
- `results/mechanism_scaling_degradation.csv` — scale sensitivity.
- `results/stratified_reference_safe_profiles.csv` — scale and density profiles.
- `results/route_purchase_decomposition.csv` — route/procurement mechanism decomposition.
- `results/market_cardinality_closed_candidate_subset.csv` — secondary M* diagnostic.
- `results/literature_BKS_validation.csv` — external BKS subset.
- `results/budget_efficiency_reference_safe_summary.csv` — anytime sample efficiency.
- `results/performance_profile.csv` — Dolan–Moré style coverage.

## Audit decisions

1. Seeds are never counted as 1,000 independent benchmark problems.
2. All primary algorithm tests use 100 paired instance medians.
3. `Baseline_EEuclideo.csv` is not globally interpreted as exact OPT.
4. Component results do not claim component-optimal gaps.
5. Correlation findings are explicitly exploratory/non-causal.
6. Older pilot tables are preserved for provenance but superseded when inconsistent with the canonical evidence hierarchy.
