# TPPLIB Reference-Semantics Audit

## Why this audit exists

The imported `Baseline_EEuclideo.csv` labels one column `OPT`, but the formal 3,000-run experiment exposed values below that column on several large instances. A paper-grade study cannot silently interpret every row as a proven optimum. This audit records the correction and defines which reference values may be used for which claim.

## What remains valid

The **raw `.tpp` instances, parser semantics, solver outputs, travel/purchase components, evaluation counts, and convergence traces remain valid**. The supplied C++ TPPLIB reader independently confirms the same key objective semantics used by PANCAKE:

- `OFFER_SECTION` triples are `(product_id, price, availability)`;
- the tour starts/ends at the depot and does not duplicate visited markets;
- total objective is `routeCost + purchaseCost`;
- `EEuclideo` coordinate distance is implemented as **truncated Euclidean distance** in the supplied TPP code.

Therefore the canonical 3,000 runs do **not** need to be discarded. The invalid assumption was the interpretation of the legacy reference column, not the objective evaluator.

## External literature check

Historical TPP literature reports that the 140 EEuclideo Class-3 instances were not all closed: **89 had known optimal solutions and 51 remained open** in the cited benchmark study. Later DMD-ATA results improved the best-known solutions for many open cases.

Within the imported 100-instance subset (`V <= 250`), eleven open instances have explicit improved BKS values available in the Bontoux TPP chapter:

| Instance | Literature BKS |
|---|---:|
| EEuclideo.200.150.4 | 2419 |
| EEuclideo.200.200.4 | 2344 |
| EEuclideo.250.100.1 | 1301 |
| EEuclideo.250.100.4 | 1673 |
| EEuclideo.250.100.5 | 1641 |
| EEuclideo.250.150.4 | 1836 |
| EEuclideo.250.150.5 | 1531 |
| EEuclideo.250.200.2 | 2785 |
| EEuclideo.250.200.3 | 1924 |
| EEuclideo.250.200.4 | 2116 |
| EEuclideo.250.200.5 | 1797 |

The imported baseline demonstrably cannot be used as exact OPT for these rows. Example: `EEuclideo.250.100.1` is `2447` in the imported CSV, whereas the literature reports BKS `1301`.

## Current registry policy

`results/reference_registry.csv` assigns every instance one of three statuses:

1. `literature_bks_open` — 11 open instances with explicit published BKS values. These support **BKS-gap**, not exact-optimality-gap, claims.
2. `legacy_closed_candidate` — 88 solver-completed records that did not hit the approximate 5-hour limit. They are retained for secondary consistency/cardinality analysis, but the paper's primary algorithm comparison is deliberately reference-independent until the official TPPLIB optimal-value table is archived with the project.
3. `open_reference_unverified` — `EEuclideo.250.50.5`; the legacy solver record is near the long-run limit and no independently archived BKS is currently attached to PANCAKE.

## Primary metric correction

The formal paper layer now uses **observed RPD** across all 100 instances:

\[
\mathrm{RPD}_{obs}(x)=100\frac{f(x)-f_{best,observed}}{f_{best,observed}},
\]

where `f_best,observed` is the best score reached by any canonical method/seed for that instance. This metric is used for paired algorithm statistics, scaling, density interaction, performance profiles, and anytime convergence. It does **not** claim global optimality.

Published BKS gaps are reported separately on the 11 independently supported open instances. The 88 legacy closed-reference candidates are never mixed with BKS rows under the label “exact OPT” in primary tables.

## Research-integrity consequence

Earlier exploratory README text that said “100 exact OPT values” is superseded by this audit. The correction is intentionally preserved rather than deleted: it documents why the benchmark semantics changed and prevents future authors from reintroducing the same error.
