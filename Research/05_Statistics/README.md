# 05 — Statistical Protocol

## Experimental unit

A paired case is `(instance, seed)`. Every compared algorithm receives the same objective-evaluation budget on that case. Pairing is important because map difficulty and stochastic initialization can otherwise dominate raw objective comparisons.

## Metrics

- **RPD (%):** `100 * (f - BKS) / BKS`; BKS is pooled within the current experiment and is not claimed to be a global optimum.
- **Median / IQR RPD:** robust final-quality summaries.
- **Convergence AUC:** integral of best-so-far RPD over normalized FE budget; lower is better.
- **Mean paired rank:** reduces sensitivity to instance-specific objective scales.
- **Win/tie/loss:** paired interpretability alongside p-values.

## Tests

1. Friedman test over all algorithms using paired cases.
2. Pairwise Wilcoxon signed-rank tests on final scores.
3. Holm step-down correction over the pairwise family.
4. Report adjusted p-value **and** paired effect description (median score improvement + wins/ties/losses).

## Current completed pilots

- Main: 100 paired cases (10 maps × 10 seeds), Friedman `p = 6.48e-58`.
- Ablation: 100 paired cases, Friedman `p = 7.15e-40`.
- TPP-style transfer: 20 paired cases (4 generated instances × 5 seeds), Friedman `p = 3.03e-17`.

## Submission-grade caution

Ten seeds improve stochastic stability, but seeds are not substitutes for independent problem instances. The final paper should preferentially enlarge the number and scale of benchmark instances, add official TPPLIB/BKS comparisons, and consider effect-size confidence intervals or a Bayesian/rank-based robustness analysis if page budget permits.
