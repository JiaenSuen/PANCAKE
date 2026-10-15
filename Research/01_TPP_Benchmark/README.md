# RQ-B — Official TPPLIB Transfer and Representation Study

This branch now separates **legacy PANCAKE** from a **classical Traveling Purchaser Problem (TPP)** representation instead of forcing TPPLIB data into the original commodity-order genotype.

## Research question

> When procurement and routing are coupled, how much of the observed performance is caused by the optimizer itself, and how much is caused by using a representation aligned with the actual combinatorial structure?

The classical uncapacitated TPP jointly decides:

1. which markets are visited,
2. in what order they are visited,
3. where each demanded product is purchased.

For a fixed visited market set under unit demand, the procurement subproblem is deterministic: each product is bought from the cheapest visited market that offers it. This motivates the new representation

`market subset/order -> induced procurement plan`

rather than the original PANCAKE representation

`product permutation + one source choice per product`.

## What is implemented

| Component | Status | File |
|---|---|---|
| Conservative TPPLIB parser | Complete | `tpplib_parser.py` |
| Legacy product-order adapter | Retained for representation comparison | `to_pancake_problem()` |
| Classical market-tour adapter | Complete | `to_market_tour_problem()` |
| Market-tour evaluator | Complete | `market_tour.py` |
| Induced optimal unit-demand procurement | Complete | `derive_procurement()` |
| Market-aware neighborhoods | Complete | 2-opt, relocate, add, drop, market replacement |
| Official Class-3 reference values | 100 exact OPT values bundled as metadata | `class3_reference_values.csv` |
| OPT-gap calculation | Complete | `tpplib_bks.py` |
| Official Class-3 downloader | Retained as optional fallback | `fetch_official_tpplib.py` |
| Official benchmark runner | Complete; exact FE accounting | `run_market_tour_benchmark.py` |
| Controlled representation runner | Complete | `run_representation_study.py` |
| Archive validator/importer | Complete; refuses non-`.tpp` archives | `import_tpplib_archive.py` |
| Extracted genuine EEuclideo data | **100 `.tpp` files + exact baseline CSV** | `official_data/EEuclideo/` |
| Compact exact-OPT suite | **20 genuine instances; runner + pilot results complete** | `run_exact_class3_suite.py` |
| Representation unit test | Complete | `test_market_tour.py` |

## Official benchmark provenance

The canonical source is Jorge Riera-Ledesma's TPPLIB site:

- `https://jriera.webs.ull.es/TPP.htm`
- official Class-3 archive link: `SymmetricEuclideanLaporteRieraSalazar.zip`
- official Class-3 solution table: `https://jriera.webs.ull.es/TPPLIB/class3.pdf`

The 2017 EJOR survey by Manerba, Mansini, and Riera-Ledesma describes Class 3 as uncapacitated symmetric TPP instances with Euclidean-coordinate markets and **truncated Euclidean routing costs**. The parser therefore uses truncation automatically for `EEuclideo.*` instances.

The current research copy now contains a **minimal benchmark-only extraction** from the user-supplied `MyTravelingPurchaser-master.zip`: 100 `EEuclideo.*.tpp` files plus `Baseline_EEuclideo.csv`. No source code, solver implementation, Gurobi integration, or other project assets were imported. The supplied archive exposed no obvious LICENSE file, so these raw benchmark files should be treated as research-input data; verify original redistribution terms before publishing them in a public repository or supplement.

A consistency audit found that the supplied baseline agrees with PANCAKE's independently prepared Class-3 metadata on **100/100 OPT values and 100/100 M\*** values.

## Official reference-value coverage

`class3_reference_values.csv` currently contains the exact values published in the official Class-3 table for:

- markets: 50, 100, 150, 200, 250;
- products: 50, 100, 150, 200;
- five instances per size pair;
- total: **100 official instances with OPT metadata**.

For these cases the runner reports

`OPT Gap (%) = 100 * (solution - OPT) / OPT`.

Larger 300/350-market cases are deliberately not assigned an `OPT` label from this table because the literature reports unsolved/open Class-3 cases; future work should attach published BKS separately with an explicit `BKS` status.

## Representation difference

| Property | Legacy PANCAKE genotype | Classical market-tour genotype |
|---|---|---|
| Search unit | demanded product | market |
| Route | product sequence induces source-node sequence | one tour over distinct visited markets |
| Same market visited repeatedly | possible in genotype | structurally impossible |
| Procurement | source gene optimized directly | derived from visited set |
| TPP interpretation | useful transfer baseline | canonical U-TPP representation |
| Main scientific use | quantify representation mismatch | official TPPLIB evaluation |

This comparison is important because a strong result on the official benchmark should not depend on an encoding that creates artificial duplicate-market visits.

## Controlled representation result before official execution

A 10-seed × 2,400-FE stress test on the packaged protocol-regenerated `50×50` and `50×100` EEuclideo-style instances compares the **same search families** under commodity-centric and market-tour representations. Market-tour wins all 20 paired cases for ILS, VNS and DFOX. Median objective reduction is **47.56%, 51.07%, and 67.85%**, respectively. The commodity representation also induces 45–48.5 repeated market visits at the median.

This is a mechanism/representation result only. It is intentionally not reported as TPPLIB performance.

## Run the extracted exact-OPT Class-3 suite

The benchmark files are already available under:

`Research/01_TPP_Benchmark/official_data/EEuclideo/`

For the compact 20-instance exact-OPT suite:

```bash
python Research/01_TPP_Benchmark/run_exact_class3_suite.py \
  --seeds 10 --budget 1200
```

Default target sizes are `50×50`, `50×100`, `100×50`, and `100×100`, five instances each. The runner exports raw runs, size profiles, paired Wilcoxon-Holm statistics, and exact OPT gaps.

For a single arbitrary `.tpp` file:

```bash
python Research/01_TPP_Benchmark/run_official_market_tour.py \
  Research/01_TPP_Benchmark/official_data/EEuclideo/EEuclideo.50.50.1.tpp \
  --seeds 10 --budget 1200
```

## Compact exact-OPT pilot finding

A **single-seed**, 20-instance pipeline pilot is included under `Research/results/class3_exact_suite/`. It is intentionally labeled as a pilot rather than a final stochastic comparison. Under 1,200 objective evaluations:

| Method | Median OPT gap | Mean OPT gap | q90 OPT gap | Median |visited markets − M*| |
|---|---:|---:|---:|---:|
| **TPP-ILS** | **8.07%** | **13.58%** | **34.45%** | **2** |
| TPP-DFOX | 11.45% | 16.75% | 35.96% | 3 |
| TPP-VNS | 12.24% | 16.43% | 37.81% | 3 |

Across 20 instance-level gaps, Friedman `p = 8.63e-4`; ILS differs significantly from both VNS and DFOX after Holm correction, while VNS and DFOX do not differ significantly. The size profile is more important than the rank itself: all methods are close to OPT on `50×50`, while the gaps grow sharply on `50×100`, `100×50`, and `100×100`, establishing a clean **problem scale × search mechanism** research axis.

## Current finding status

The official-data bottleneck is now removed for the 50–250-market EEuclideo family: genuine `.tpp` files, exact OPT values, and M* are locally available, while PANCAKE continues to use its **own parser and solver code only**. This enables three cleaner paper analyses: (1) exact-optimality gap instead of pooled BKS/RPD, (2) scale interaction over markets/products, and (3) visited-market cardinality error relative to M*.

The next empirical milestone is to raise the exact suite from the included one-seed pipeline pilot to the paper protocol (≥10 paired seeds), then add decomposition and convergence analyses by size. Larger 300/350-market instances remain a separate BKS-only external layer and must not be mixed with the exact-OPT claims.
