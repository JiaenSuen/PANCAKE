# Formal TPPLIB Class-3 Study

This directory is the **canonical external-validity evidence layer** for the PANCAKE paper. It contains the completed 100-instance / 3,000-run EEuclideo experiment, a frozen protocol, reference-semantics audit, paper-ready analyses, figures, and a claim ledger.

## Canonical experiment

- **Instances:** 100 genuine EEuclideo Class-3 `.tpp` files.
- **Grid:** `V ∈ {50,100,150,200,250}` × `K ∈ {50,100,150,200}` × five replicates.
- **Seeds:** 10 fixed paired seeds per instance and method.
- **Budget:** exactly 1,200 objective evaluations per run.
- **Methods:** `TPP-ILS`, `TPP-VNS`, `TPP-DFOX`.
- **Runs:** **3,000**.
- **Representation:** market subset + market order → induced procurement.
- **Statistical unit:** per-instance median over the 10 seeds. Seeds are not treated as independent benchmark instances.

The external methods are intentionally representative rather than exhaustive. ILS is the trajectory/local-intensification baseline, VNS tests systematic neighborhood change, and DFOX represents population/prey-guided search. The broader CPO/BKA/HO/WOA/GA comparison remains in PANCAKE's mechanism layer.

## Reference policy — read before using any gap column

The imported `Baseline_EEuclideo.csv` cannot be interpreted as 100 exact optima. Historical literature distinguishes **closed** and **open** Class-3 instances, and several long-running legacy rows labeled `OPT` are contradicted by later published BKS values.

Therefore the canonical paper analysis uses:

1. **Observed RPD** relative to the best canonical score reached on the same instance for all 100 instances.
2. **Published BKS gaps** on 11 independently supported open instances.
3. **88 legacy solver-completed closed-reference candidates** only for secondary consistency/cardinality diagnostics until the official optimal-value table is archived with the project.
4. One open row (`EEuclideo.250.50.5`) with no paper-grade external value in the current evidence package.

See `REFERENCE_SEMANTICS_AUDIT.md` and `results/reference_registry.csv`.

## Structural instance descriptors

Each official instance receives descriptors computed from the raw `.tpp` file:

- `scale_tier`: small (`V≤100`), medium (`150≤V≤200`), large (`V=250`).
- `offers_per_product`: total offer entries / number of products.
- `offers_per_market`: total offer entries / purchasable markets.
- `normalized_offer_density`: `offers / ((V-1)K)`.
- `product_market_ratio`: `K/(V-1)`.
- `decision_scale`: `(V-1)K`.

Presentation tiers for product-supply and market-assortment density are global tertiles frozen in `results/instance_manifest.csv`; continuous descriptors are used for correlation analysis.

## Canonical analysis blocks

1. **Reference-safe overall comparison** — observed RPD, paired instance medians, Friedman, Wilcoxon + Holm, win/tie/loss, effect size.
2. **Scaling / mechanism degradation** — small/medium/large profiles, full `V×K` grid, log-scale slope, Spearman association.
3. **Density interaction** — product-supply and market-assortment tertiles plus continuous correlations.
4. **Route / purchase decomposition** — travel and procurement behavior relative to the best tested component on each instance; no component-optimality claim.
5. **Market-cardinality diagnostic** — secondary analysis on the 88 legacy closed-reference candidates only.
6. **Convergence / budget efficiency** — anytime RPD AUC, threshold coverage, FE-to-quality.
7. **Performance profile** — fraction of instances within a multiplicative factor of the best tested median.
8. **External BKS check** — 11 published open-instance BKS values, clearly separated from exact-optimum language.

## Headline canonical results

| Method | Per-instance median observed RPD ↓ | q90 run RPD ↓ | ≤5% coverage ↑ | ≤10% coverage ↑ |
|---|---:|---:|---:|---:|
| **TPP-ILS** | **3.07%** | **12.39%** | **65.4%** | **85.8%** |
| TPP-VNS | 6.70% | 16.44% | 43.3% | 68.7% |
| TPP-DFOX | 8.68% | 19.67% | 32.5% | 57.1% |

Friedman on 100 paired instance medians: **p = 1.14×10⁻³⁴**. All three paired method contrasts remain significant after Holm correction.

The most important mechanism result is not merely the ranking: DFOX's loss grows strongly with **product count / market-assortment breadth**, and its residual error is more route-side than procurement-side. See `FINDINGS_LEDGER.md`.

## Evidence hierarchy

- **Canonical:** this 3,000-run suite and the reference-safe derived tables.
- **External BKS:** 11 published open-instance values stored in the reference registry.
- **Secondary legacy reference:** 88 solver-completed records, never mixed into the primary observed-RPD table as exact OPT.
- **Pilot:** old compact or single-instance infrastructure tests; retained for provenance only.
- **Exploratory:** structure correlations and conditional mechanism findings; useful for hypotheses, not causal claims.

## Reproduction

```bash
python Research/11_Formal_TPPLIB_Study/run_formal_class3.py \
  --seeds 10 --budget 1200 --workers 5

python Research/11_Formal_TPPLIB_Study/build_reference_registry.py
python Research/11_Formal_TPPLIB_Study/analyze_formal_class3_v2.py
```

The original run export `formal_runs.csv` is preserved. Its historical `OPT/gap_opt_pct` columns are **superseded** by `formal_runs_reference_safe.csv`; this preserves traceability without propagating the legacy reference assumption.

## Manuscript artifact index

Start with `MANIFEST.md` when writing the paper. Structural tier definitions are frozen in `INSTANCE_STRATIFICATION.md`. Manuscript-facing LaTeX tables and TikZ figures are under `Research/07_Paper_Materials/formal_tables/` and `Research/07_Paper_Materials/latex_figures/`.

Additional canonical figures now include `formal_market_assortment_interaction.png`, `formal_product_dimension_degradation.png`, and `formal_component_excess_overall.png` to visualize the strongest structure/mechanism interactions.
