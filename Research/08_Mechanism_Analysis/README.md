# Mechanism-oriented analysis

This folder turns the expanded PANCAKE experiment from a global ranking table into a **mechanism study**. All analyses operate on the packaged paired runs; no post-hoc data are silently substituted.

## Questions

1. Is the overall ranking stable across landscape structures?
2. Does DFOX fail uniformly, or only under specific coupling patterns?
3. How reliable are algorithms in their 90th-percentile failure tail?
4. What fraction of runs lies within 2%, 5%, 10%, or 20% of the paired best?
5. How large is each controlled DFOX ablation effect in paired objective space?
6. How much performance is recovered solely by changing the TPP representation?
7. Are any structural metrics associated with algorithm-vs-ILS gaps? The correlation file is explicitly exploratory because `n=10` synthetic instances is too small for strong inferential claims.

## Current findings

- ILS-PA has the strongest reliability: median RPD 5.85%, 90th-percentile RPD 12.20%, and 84% of runs at RPD ≤10%.
- DFOX-APNS is conditional: on `shared_hubs`, its median score gap to ILS is only 0.14% and its paired win rate is 45%; on `price_distance_conflict`, the median gap grows to 11.73%.
- Budget-to-quality reveals an intensification bottleneck: ILS reaches median RPD≤10% at 540 FE; DFOX reaches ≤15% at 840 FE but does not reach ≤10% within 1,200 FE.
- DFOX's A0→A1 problem-aware transition improves paired objective by 17.06% at the median and wins 100/100 pairs. A1→A2 adds a smaller 1.76% median improvement. A2→A3 is unsupported.
- Representation is a first-order factor on the Class-3-style stress test: market-tour reduces median objective by 47.56% (ILS), 51.07% (VNS), and 67.85% (DFOX), while eliminating 45–48.5 repeated market visits from the commodity encoding.

## Outputs

- `family_profile.csv` — median RPD/IQR/AUC by algorithm × family.
- `fox_conditional_profile.csv` — FOX vs ILS conditional comparison.
- `robustness_profile.csv` — median, q75, q90, maximum, and success thresholds.
- `pairwise_win_probability.csv` — paired probability of superiority.
- `performance_profile.csv` — empirical Dolan–Moré-style near-best coverage.
- `budget_to_quality.csv` — FE required for the median trajectory to reach fixed RPD targets.
- `ablation_effect_sizes.csv` — paired mechanism increments and rank-biserial effects.
- `representation_effects.csv` — controlled representation effect and repeated-market diagnostics.
- `instance_structure_metrics.csv` / `exploratory_structure_correlations.csv` — descriptive landscape diagnostics; exploratory only.

PNG figures are exported into `Research/results/figures/`.
