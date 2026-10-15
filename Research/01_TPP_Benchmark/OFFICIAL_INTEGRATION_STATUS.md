# Official TPPLIB Integration Status

## Completed

- Official TPPLIB site and Class-3 reference table verified.
- 100 exact Class-3 reference values encoded with explicit `OPT` status.
- `EEuclideo` routing convention corrected to truncated Euclidean distance.
- Classical market-tour representation implemented.
- Procurement is derived optimally conditional on the visited market set for unit-demand U-TPP.
- Market-level add/drop/replace/relocate/2-opt neighborhoods implemented.
- Official benchmark downloader and runner implemented.
- Runner now uses exact FE accounting for ILS/VNS/DFOX, including pruning and local intensification.
- Runner reports purchase/travel decomposition, number of visited markets, and OPT/BKS gap according to reference status.
- Controlled commodity-vs-market representation runner is implemented for both protocol-regenerated and genuine `.tpp` inputs.
- Synthetic representation regression test passes.
- Genuine `EEuclideo.350.150.1.tpp` parses successfully after adding support for colon-suffixed section headers.
- Multi-dot TPPLIB instance-name normalization was fixed; large-instance BKS lookup now works correctly.
- A 10-seed, 1,200-FE genuine market-tour pilot has been recorded for ILS/VNS/DFOX.

## Not yet claimed

- The genuine `EEuclideo.350.150.1` result is a **single-instance external pilot**, not evidence for TPPLIB-wide superiority.
- The earlier uploaded ZIP remains correctly classified as routing-only TSP CSV data and is not relabelled as TPPLIB.
- 300/350-market values are never labelled optimal unless a proof/source explicitly supports `OPT`; `EEuclideo.350.150.1 = 1455` is stored as `BKS`.
- Capacitated TPP is not yet supported by the market-tour evaluator.

## Paper-safe statement

> We implemented a TPPLIB-compatible evaluation path using the classical market-tour representation and an induced procurement plan. Exact Class-3 reference values are retained for the 50--250-market subset, while large open instances use explicit BKS metadata. A first genuine 350×150 TPPLIB pilot validates the full parsing/evaluation pipeline, but broader multi-instance external validation is still required before making general performance claims.
