# Paper Results Draft — Formal TPPLIB Layer

## Overall mechanism comparison

Across 100 EEuclideo instances and 10 paired seeds per instance, ILS provided the strongest performance under the fixed 1,200-evaluation budget. Using the median over seeds as the independent per-instance statistic, its median observed RPD was 3.07%, compared with 6.70% for VNS and 8.68% for DFOX. A Friedman test detected a strong method effect (`p = 1.14e-34`). Holm-corrected paired Wilcoxon tests were significant for ILS–VNS, ILS–DFOX, and VNS–DFOX. These results indicate that problem-aware trajectory intensification remains a particularly strong baseline even when population methods use the same market-tour representation.

## Scale and mechanism degradation

The three search mechanisms do not degrade uniformly. DFOX median observed RPD increases from 7.32% on the small tier to 9.21% on medium and 10.75% on large instances. ILS remains almost unchanged across the same scale partition (3.27%, 2.99%, 3.01%). More importantly, DFOX performance is significantly associated with product count and offers-per-market, whereas ILS shows no corresponding significant correlation. This suggests that the effective source of difficulty is not merely the number of market nodes, but the breadth of coupled procurement alternatives that each population update must resolve.

## Route–procurement decomposition

Component analysis clarifies why DFOX loses ground. Relative to the best tested component median on each instance, DFOX incurs 4.29% median travel excess but only 1.51% purchase excess. On the largest tier this separation widens to 4.83% versus 0.41%, respectively. Thus, the population method often identifies competitive procurement configurations yet fails to polish their tour ordering to the same extent as ILS. VNS displays a complementary pattern, with a smaller travel penalty but larger purchase penalty. The result supports a mechanism-level interpretation: the methods allocate limited evaluations differently between route intensification and procurement-set refinement.

## Anytime budget efficiency

The final ranking is also reflected in convergence dynamics. ILS obtains the lowest median observed-RPD AUC (5.85), followed by VNS (9.60) and DFOX (12.39). ILS reaches the 10% observed-RPD region in 85.8% of all runs, with a median of 240 evaluations among successful runs; DFOX reaches the same region in 57.1% of runs and requires a median of 360 evaluations. At the stricter 5% level the coverage becomes 65.4% versus 32.5%. This supports the interpretation that the remaining population-method gap is primarily an intensification/sample-efficiency issue rather than a complete failure of global exploration.

## External BKS check

The reference audit identifies eleven open instances with independently reported literature BKS values. Under the deliberately small 1,200-FE budget, median BKS gaps remain 20.54% (ILS), 25.22% (VNS), and 31.82% (DFOX). These results prevent overclaiming: PANCAKE's contribution is a controlled study of representation and search mechanisms, not a claim of new TPP state of the art. They also motivate the next hybrid experiment: population exploration followed by problem-aware local route/procurement intensification under adaptive operator control.
