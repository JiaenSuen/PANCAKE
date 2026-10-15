# Research Implementation Status

## Completed in this expansion

- [x] Preserve legacy PANCAKE objective and original README benchmark.
- [x] Problem-aware low-level neighborhoods (`source`, coupled `joint`).
- [x] Controlled DFOX A0/A1/A2/A3 ablation on a single code path.
- [x] Adaptive operator-selection telemetry and operator-level success statistics.
- [x] Strong problem-aware ILS and VNS baselines under equal FE budgets.
- [x] Three recent-method mechanism transfers: D-CPO, D-BKA, D-HO.
- [x] 10-seed / 1,200-FE expanded PANCAKE pilot.
- [x] Friedman + paired Wilcoxon + Holm correction + win/tie/loss summaries.
- [x] Median/IQR convergence trajectories and paper-oriented figures.
- [x] TPP-compatible objective bridge (distance matrix, depot return).
- [x] Protocol-regenerated EEuclideo-style transfer instances.
- [x] Conservative TPPLIB `.tpp` parser + fixture test + official-benchmark runner.
- [x] GUI exposure of ILS/VNS, CPO/BKA/HO, A0–A3 and representative TPP-style maps.
- [x] Per-subproblem Research notes, findings bank, results draft and paper outline.
- [x] Classical market-tour + induced procurement representation.
- [x] Equal-FE market-tour ILS/VNS/DFOX solvers.
- [x] Controlled representation study (commodity vs market-tour), 10 seeds × 2 Class-3-style sizes.
- [x] Conditional landscape analysis, failure-tail robustness, paired win matrix and empirical performance profiles.
- [x] Paper-oriented TikZ flowchart/representation/ablation figure fragments.
- [x] Provenance audit of user-supplied routing archive; stored separately as non-TPPLIB auxiliary data.

## High-priority work before submission

- [ ] Acquire/import genuine TPPLIB Class-3 `.tpp` files and run the prepared 50×50 / 50×100 / 100×50 / 100×100 external-validation matrix.
- [ ] Populate official Table 7 with OPT gap, travel/purchase decomposition and visited-market count from genuine benchmark files.
- [ ] Expand independent benchmark instances/scales; do not rely only on more stochastic seeds.
- [ ] Add wall-clock/runtime reporting alongside FE fairness.
- [ ] Revisit or simplify A3 restart; current evidence does not validate it.
- [ ] Add objective-weight sensitivity and problem-size scalability if page/time budget permits.
- [ ] Recompile/run the WinForms self-test on Windows/.NET 8; this container has no `dotnet` toolchain.

## Current strongest manuscript story

The current evidence supports a hierarchy of design importance:

`representation -> problem-aware neighborhoods -> adaptive operator selection -> outer population/restart mechanism`.

This is stronger and more defensible than presenting PANCAKE as another “improved animal optimizer” paper.

## Broader mechanism-study status

- [x] Genuine TPPLIB parser execution on `EEuclideo.350.150.1`.
- [x] BKS-vs-OPT status separation for large/open instances.
- [x] Strict-FE market-tour ILS/VNS/DFOX runner.
- [x] 10-seed genuine external pilot result table.
- [x] Recent-method mechanism taxonomy: CPO/BKA/HO implemented; MGO/IVYA literature-context.
- [x] Adaptive operator-selection / hyper-heuristic research positioning.
- [ ] Multi-instance exact-OPT TPPLIB study (50–250 markets).
- [ ] Additional large-instance BKS cases.
- [ ] Optional fourth recent transfer only if it introduces a missing mechanism.
