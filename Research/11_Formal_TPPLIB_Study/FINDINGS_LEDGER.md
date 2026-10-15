# Formal Findings Ledger — 100-Instance TPPLIB Study

**Canonical experiment:** 100 EEuclideo instances × 10 paired seeds × 3 representative mechanisms × 1,200 FE = **3,000 runs**.

**Primary statistical unit:** the median over 10 seeds for each `instance × algorithm` pair (100 paired observations per method). Seed-level runs are used for robustness/anytime analyses, not pseudo-replicated as independent instances.

## F1 — Strong local intensification is the best external baseline under the fixed FE budget

**Evidence.** Per-instance median observed RPD is **3.07% for ILS**, **6.70% for VNS**, and **8.68% for DFOX**. Friedman over 100 paired instances gives `p = 1.14e-34`. Holm-corrected paired Wilcoxon tests are significant for all three pairs. ILS beats DFOX on 96/100 instance medians (3 ties) and VNS on 94/100 (2 ties).

**Safe paper claim.** Under a strict 1,200-objective-evaluation budget and a shared market-tour representation, trajectory-based problem-aware intensification is substantially more sample-efficient than the tested population/prey-guided DFOX transfer.

**Do not claim.** This does not prove ILS is universally superior to population metaheuristics or to all modern metaheuristics; the external layer intentionally tests three representative mechanisms.

---

## F2 — DFOX degradation is associated more with combinatorial product/assortment breadth than with market count alone

**Evidence.** DFOX observed RPD has significant positive association with product count `K` (`Spearman rho = 0.305, p = 0.0020`) and offers per market (`rho = 0.260, p = 0.0089`). Its normalized offer-density association is weaker and not significant. ILS shows no significant association with these descriptors in this suite.

Across scale tiers, DFOX median RPD grows from **7.32% (small)** to **9.21% (medium)** to **10.75% (large)**. The large-minus-small degradation is **+3.43 percentage points**. ILS remains roughly flat (**3.27%, 2.99%, 3.01%**).

**Safe paper claim.** The DFOX transfer exhibits stronger structural sensitivity, especially as the number of products and market-level assortment breadth increase; simple market count alone is an incomplete explanation of difficulty.

**Caveat.** Instance descriptors are correlated by benchmark construction. These are interaction/hypothesis findings, not causal regression claims.

---

## F3 — Market-assortment density exposes a clear mechanism interaction

**Evidence.** From low to high offers-per-market tertiles, median observed RPD changes:

- ILS: **2.93% → 4.12%** (`+1.19 pp`)
- VNS: **5.10% → 7.30%** (`+2.20 pp`)
- DFOX: **5.30% → 12.05%** (`+6.75 pp`)

By contrast, high product-supply density does not harm ILS/VNS and is associated with a modest reduction in their median RPD, while DFOX worsens from **8.05% to 10.64%**.

**Safe paper claim.** Population guidance is much more sensitive to dense market assortments in the present discrete transfer, while problem-aware trajectory methods absorb the same structural breadth more robustly.

---

## F4 — DFOX's large-instance weakness is primarily route-side rather than procurement-side

**Evidence.** Relative to the best tested component median on each instance, DFOX's overall median excess is approximately **4.29% for travel** but only **1.51% for purchase**. On the large tier the contrast becomes **4.83% travel excess vs 0.41% purchase excess**. VNS shows the opposite tendency more often (**1.18% travel vs 3.42% purchase excess overall**).

**Safe paper claim.** The tested DFOX market-selection dynamics often identify competitive procurement sets, but insufficient route intensification leaves a larger residual travel penalty. This independently supports the earlier PANCAKE finding that future population hybrids should add local route polishing rather than more blind restart/exploration.

**Caveat.** These are component comparisons against the best **tested** method, not component-wise optimality gaps.

---

## F5 — The ranking difference is an anytime-efficiency difference, not merely a final-score artifact

**Evidence.** Median observed-RPD AUC: **ILS 5.85**, **VNS 9.60**, **DFOX 12.39**. Coverage of final/anytime RPD ≤10% is **85.8% / 68.7% / 57.1%** for ILS/VNS/DFOX. Among successful runs, the median FE to ≤10% is **240 / 240 / 360**. Coverage of ≤5% is **65.4% / 43.3% / 32.5%**, with median FE **240 / 360 / 480** among hits.

**Safe paper claim.** ILS converts the same evaluation budget into useful solutions earlier and more consistently; DFOX's weakness is visible throughout late-stage convergence rather than only at the final checkpoint.

---

## F6 — Performance-profile coverage makes the robustness gap interpretable

**Evidence.** Using per-instance median score ratios against the best tested median:

- At `tau = 1.00`: ILS is best on **96%** of instances, VNS on 6%, DFOX on 2% (ties permitted).
- At `tau = 1.05`: ILS covers **100%**, VNS **84%**, DFOX **61%**.
- At `tau = 1.10`: ILS **100%**, VNS **95%**, DFOX **86%**.

**Safe paper claim.** DFOX is not catastrophically poor: it lies within 10% of the best tested median on most instances, but it rarely becomes the best method under the current 1,200-FE design.

---

## F7 — Visited-market cardinality alone does not explain performance

**Evidence.** On the 88 solver-completed closed-reference candidate records, all three methods undershoot the legacy reference market count by roughly five markets in median (`ILS -5`, `VNS -5.5`, `DFOX -5`). Yet their objective performance differs strongly.

**Safe paper claim.** Search quality depends on **which** markets are selected and how they are ordered, not merely on recovering the reference market-set cardinality.

**Caveat.** Because the imported `M*` metadata are not yet independently archived from the official TPPLIB reference table, this is a secondary diagnostic, not a primary theorem or exact-cardinality claim.

---

## F8 — Hard open instances remain meaningfully far from literature BKS under 1,200 FE

**Evidence.** On 11 open EEuclideo instances with independently reported literature BKS values, median BKS gap is **20.54% for ILS**, **25.22% for VNS**, and **31.82% for DFOX**.

**Safe paper claim.** The fixed 1,200-FE budget is deliberately stringent and exposes scalability limits; strong performance on PANCAKE/smaller closed cases should not be interpreted as state-of-the-art TPP performance on open large instances.

**Research implication.** Hybrid population + problem-aware local intensification and budget-adaptive control are justified future experiments.
