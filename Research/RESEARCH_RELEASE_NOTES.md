# Research Release Notes — Mechanism / Representation Expansion

This release deepens PANCAKE from an optimizer leaderboard into a mechanism-oriented discrete optimization study.

## Added in this release

- Exact-FE market-tour ILS, VNS, and DFOX solvers for unit-demand TPP-style search.
- Controlled commodity-centric vs market-tour representation experiment.
- DFOX conditional-strength analysis by landscape family.
- Reliability metrics: q90 RPD, success thresholds, paired win probabilities.
- Empirical performance profiles and budget-to-quality analysis.
- Paired ablation effect sizes (relative objective gain + rank-biserial effect).
- Descriptive instance-structure metrics and clearly-labelled exploratory correlations.
- TPPLIB archive validation/import utility and 20-instance official Class-3 target matrix.
- Provenance audit for the supplied routing-only archive; it is retained but not relabelled as TPPLIB.
- Paper-ready TikZ figure fragments for research framework, representation bridge, ablation path, and experimental layers.

## Current strongest findings

1. **Problem-aware neighborhoods dominate the controlled DFOX gain.** A0→A1 improves paired objective by 17.06% at the median and wins 100/100 pairs.
2. **Adaptive operator control helps second.** A1→A2 adds 1.76% median objective improvement; the restart layer remains unsupported.
3. **Representation is a first-order variable.** Market-tour encoding reduces objective by 47.56% (ILS), 51.07% (VNS), and 67.85% (DFOX) relative to commodity-centric encoding on the controlled Class-3-style stress test.
4. **DFOX is conditional, not uniformly weak.** It nearly ties ILS on shared-hub structure (0.14% median score gap; 45% paired wins) but is much weaker under price–distance conflict.
5. **ILS wins through intensification efficiency and robustness.** It reaches median RPD≤10% at 540 FE and has q90 RPD 12.20%.

## Still pending before an external-validity claim

- Genuine TPPLIB Class-3 `.tpp` files.
- Official 50×50 / 50×100 / 100×50 / 100×100 runs with OPT gaps.
- Larger independent instance count for confirmatory landscape-structure analysis.
- Wall-clock comparison in addition to FE fairness.

## 2026-10-11 — Genuine TPPLIB + broader metaheuristic framing

- Integrated genuine `EEuclideo.350.150.1.tpp` (350 markets, 150 unit-demand products, 26,698 offers).
- Fixed parser support for colon-suffixed section headers and multi-dot TPPLIB instance names.
- Added explicit large-instance BKS handling; `EEuclideo.350.150.1 = 1455` is stored as `BKS`, not `OPT`.
- Added a reproducible strict-FE official market-tour runner and 10-seed/1200-FE pilot materials.
- Reframed PANCAKE from FOX-centered comparison to a broader **modern metaheuristic mechanism study**.
- Added `10_Modern_Metaheuristic_Overview/` covering ILS/VNS, GA, FOX/WOA, CPO/BKA/HO, MGO/IVYA context, and adaptive operator selection.
- Added method-agnostic TikZ figures for mechanism taxonomy and the broader research framework.

## 2026-10-11 — Formal paper evidence package / canonical TPPLIB study

- Completed **100 official EEuclideo Class-3 instances × 10 paired seeds × 3 representative mechanisms × 1,200 FE = 3,000 runs**.
- Added frozen small/medium/large stratification plus product-supply and market-assortment density descriptors computed from each `.tpp` file.
- Added reference-safe overall comparison, paired Friedman/Wilcoxon-Holm statistics, scaling/mechanism degradation, density interaction, route/purchase decomposition, market-cardinality diagnostics, convergence AUC, FE-to-quality thresholds, and performance profiles.
- Canonical external medians: ILS 2.68% observed RPD, VNS 6.33%, DFOX 8.58% at run level; all three paired instance-median contrasts are significant after Holm correction.
- Identified a mechanism-sensitive scaling finding: DFOX RPD is significantly associated with product count (`rho=0.305`) and offers per market (`rho=0.260`), while ILS is comparatively stable.
- Identified a component-level finding: DFOX residual error is predominantly route-side (about 4.29% tested-component travel excess vs 1.51% purchase excess overall), strengthening the case for route polishing rather than blind restart.
- Added a formal reference-semantics audit. The imported legacy `OPT` column is **not** treated as 100 universally exact optima. Primary analysis uses observed RPD; 11 open cases use independently supported published BKS values; 88 solver-completed rows are secondary closed-reference candidates.
- Archived all pre-audit exact-gap derived tables/plots/scripts instead of deleting them, preserving provenance while preventing accidental citation.
- Added manuscript-ready LaTeX result tables, TikZ evidence/semantics/mechanism figures, compiled PDF previews, a paper table/figure traceability map, findings ledger, limitations register, and manuscript-facing results draft.

The external-validity claim is therefore no longer pending. Remaining work is paper synthesis and optional follow-up experiments (budget sensitivity, hybrid route polishing, adaptive mode selection), not benchmark infrastructure.
