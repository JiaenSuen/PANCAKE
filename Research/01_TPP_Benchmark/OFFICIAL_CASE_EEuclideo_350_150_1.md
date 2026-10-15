# Genuine TPPLIB pilot — EEuclideo.350.150.1

## Instance verification

The user-supplied file is a genuine TPPLIB-style U-TPP instance:

- `TYPE: TPP`
- `DIMENSION: 350`
- 150 unit-demand products
- 350 offer rows including the depot row
- 26,698 parsed market-product offers
- `NODE_COORD_SECTION`, `DEMAND_SECTION`, and `OFFER_SECTION` are present
- market 1 is treated as the depot

The real file exposed two integration bugs that were fixed in this release: section headers may include a trailing colon (for example `DEMAND_SECTION :`), and TPPLIB instance IDs contain multiple dots, so `Path.stem` must not be used to normalize `EEuclideo.350.150.1`.

## Reference value

The literature reports **1455** as a best-known value for `EEuclideo.350.150.1`. This release stores it as **BKS**, not `OPT`, because the larger 300/350-market set historically contained open instances and the cited 2018 MMAS study explicitly reported a new best result for this case.

## 10-seed equal-FE pilot

Budget: **1,200 objective evaluations per run**. Representation: **market subset/order + induced procurement**. Seeds are paired across methods.

| Method | Median objective | Best objective | Median BKS gap | Best BKS gap | Median travel | Median purchase | Median visited markets |
|---|---:|---:|---:|---:|---:|---:|---:|
| **TPP-ILS** | **1847.0** | **1794.0** | **26.94%** | **23.30%** | 1462.5 | 376.5 | 12 |
| TPP-VNS | 1851.0 | 1806.0 | 27.22% | 24.12% | 1497.5 | 353.5 | 12 |
| TPP-DFOX | 1940.5 | 1868.0 | 33.37% | 28.38% | 1582.5 | 352.0 | 12 |

Paired Wilcoxon + Holm results:

- ILS vs VNS: Holm `p = 0.1484` — **not significant** in this 10-seed pilot.
- ILS vs DFOX: Holm `p = 0.00586` — significant.
- VNS vs DFOX: Holm `p = 0.00781` — significant.

## Paper-safe interpretation

This single official case is **pipeline validation and an external pilot**, not enough to claim a TPPLIB-wide ranking. It nevertheless strengthens two existing observations. First, strong problem-aware trajectory search remains highly competitive after moving from synthetic PANCAKE maps to a genuine U-TPP instance. Second, DFOX's gap is largely concentrated in the travel component: its median purchase cost is similar to VNS, while median travel cost is substantially higher. This suggests that the current market-tour FOX transfer requires stronger **tour intensification / route-order refinement**, rather than additional stochastic restarts.

The next external-validation step should add multiple 50/100/150/200-market exact-OPT instances and several large BKS instances before any broad claim is made.
