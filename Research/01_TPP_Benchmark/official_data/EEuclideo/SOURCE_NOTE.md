# EEuclideo TPPLIB benchmark subset

This directory contains only the EEuclideo `.tpp` instance files and `Baseline_EEuclideo.csv` extracted from the user-supplied `MyTravelingPurchaser-master.zip`. No solver/source-code files from that project were imported.

- 100 EEuclideo instances: 20 `(markets, products)` size combinations × 5 instances.
- Sizes: markets ∈ {50,100,150,200,250}, products ∈ {50,100,150,200}.
- `Baseline_EEuclideo.csv` fields: Instance, V, K, M*, OPT, Sec.
- TPPLIB convention: market 1 is the depot; benchmark files contain `DEMAND_SECTION` and `OFFER_SECTION`.

## Provenance / redistribution note
The supplied archive did not expose an obvious LICENSE file. Treat these files as research-input data obtained from the user-provided source. Before publicly redistributing the benchmark files in a repository or paper supplement, verify the original TPPLIB/source redistribution terms.

No code from the uploaded repository is used by PANCAKE; PANCAKE uses its own parser and solvers.
