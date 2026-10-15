# Canonical Experimental Protocol

## Purpose

Test how representative search mechanisms transfer from PANCAKE to a standard structured discrete optimization benchmark while separating algorithm behavior from uncertain benchmark-reference semantics.

## Pre-registered questions

**Q1 — Overall mechanism efficiency.** Under a fixed 1,200-FE budget and shared representation, how do trajectory intensification (ILS), systematic neighborhood change (VNS), and population/prey guidance (DFOX) compare?

**Q2 — Scaling / degradation.** Does mechanism performance change with market count `V`, product count `K`, or total decision scale `(V-1)K`?

**Q3 — Structural density.** Is performance associated with offers per product, offers per market, or normalized offer density?

**Q4 — Component behavior.** Are method differences primarily route-side, purchase-side, or both?

**Q5 — Cardinality diagnostic.** On solver-completed closed-reference candidates, how different is the visited-market cardinality from the legacy reference `M*`?

**Q6 — Anytime efficiency.** Which mechanism converts the same objective-evaluation budget into low relative error earliest and most consistently?

**Q7 — External reference check.** On independently reported open-instance BKS values, how large is the remaining fixed-budget gap?

## Fixed factors

- Same 100 genuine EEuclideo Class-3 instances.
- Same 10 paired seeds for each algorithm × instance pair.
- Same 1,200 objective-evaluation budget.
- Same market-tour + induced-procurement representation.
- Same parser/objective semantics, including truncated Euclidean EEuclideo distance.
- No hidden objective calls outside the evaluation budget.

## Primary metric

Because the imported legacy baseline is not exact for every row, the primary reference-safe metric is

\[
\mathrm{RPD}_{obs}=100\frac{f-f_{best,observed}}{f_{best,observed}},
\]

where `f_best,observed` is the best score reached by any canonical method/seed on the same instance. This supports paired method comparison without claiming global optimality.

Published BKS gaps are reported separately on 11 independently supported open cases.

## Statistical policy

1. Compute the median across 10 seeds for every `instance × algorithm` pair.
2. Use Friedman on the 100 paired instance medians.
3. Use paired Wilcoxon signed-rank tests on those same 100 medians, with Holm correction.
4. Report win/tie/loss counts and paired rank-biserial effect size.
5. Retain seed-level runs for robustness and anytime analysis only; do not pseudo-replicate them in primary inference.

## Scaling analysis

Scaling results are descriptive rather than a universal complexity theorem. For every method report:

- observed RPD by small / medium / large market-scale tier;
- full `V×K` grid;
- difference between large and small tiers;
- descriptive slope against `log10((V-1)K)`;
- Spearman associations with `V`, `K`, and decision scale.

## Density analysis

- `offers_per_product = offers/K`
- `offers_per_market = offers/(V-1)`
- `normalized_offer_density = offers/((V-1)K)`

Low/medium/high labels are global tertiles used for presentation. Continuous descriptors remain the primary correlation variables. Association is labeled exploratory because the benchmark descriptors are not orthogonally randomized.

## Component analysis

External metadata do not provide optimal route and purchase components separately. Therefore route/purchase results compare each method with the **best tested component median on the same instance**. No “travel optimality gap” or “purchase optimality gap” is permitted.

## Reference-cardinality analysis

`M*` analysis is restricted to 88 `legacy_closed_candidate` records and explicitly labeled secondary until the official TPPLIB optimal-value table is archived. The metric is a diagnostic of market-set cardinality, not proof that a nonzero error causes the objective gap.

## Claim discipline

A finding enters `FINDINGS_LEDGER.md` only if its exact evidence table is present under `results/`. Primary claims use reference-safe statistics. BKS, legacy closed-reference, pilot, and exploratory evidence are never silently merged.
