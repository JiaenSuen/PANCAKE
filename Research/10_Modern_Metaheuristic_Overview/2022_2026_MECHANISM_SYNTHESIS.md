# 2022–2026 Mechanism-Oriented Metaheuristic Synthesis

## Research purpose

This artifact formalizes the additional PANCAKE contribution requested for the final revision: recent metaheuristics are not compared as a chronology of biological metaphors. They are decomposed into reusable search primitives and interpreted against controlled PANCAKE evidence. The unit of analysis is therefore the **mechanism**: information source, intensification, diversification, adaptive/memory control, and discrete-transfer interface.

## Taxonomy and evidence

The machine-readable taxonomy is `mechanism_taxonomy_2022_2026.csv`. It spans FOX (2022), DBO (2022/2023), OOA (2023), CPO/BKA/HO/Moss Growth/IVYA (2024), adaptive operator selection (2025), and a 2026 functional-taxonomy review. Only CPO, BKA and HO are implemented as new discrete transfers in the controlled PANCAKE layer; the remaining recent methods are literature-level mechanism coverage. This boundary is intentional: adding an optimizer is justified only when it tests a mechanism not already represented.

## Empirical characterization in PANCAKE

Under 100 paired synthetic cases and 1,200 objective evaluations per run, the regenerated final experiment gives median RPD 5.85% for ILS-PA, 8.14% for VNS-PA, 8.30% for D-CPO, 11.49% for DFOX-APNS, 12.16% for D-BKA, 16.92% for DWOA-AVNS, 18.66% for GA+Tabu, and 18.77% for D-HO. The key result is not that a 2024 method wins: the strongest method is ILS-PA. Instead, CPO-style multi-mode/population control transfers more successfully than the tested HO phase mapping, while BKA heavy-tail diversification is useful but insufficient to replace strong problem-aware intensification.

The DFOX single-code-path ablation gives median RPD 33.65% (A0 generic), 9.73% (A1 problem-aware), 7.65% (A2 adaptive), and 8.53% (A3 full restart). Thus the largest gain comes from problem-aware neighborhood semantics, adaptive operator control adds a second improvement, and the tested restart is not supported. This is direct evidence for the hierarchy `representation -> neighborhood semantics -> adaptive control -> outer/restart mechanism`.

## Contribution claim

The final paper may claim a **mechanism-oriented empirical characterization**, not a universal survey ranking. PANCAKE shows that: (i) recency is not predictive of discrete performance; (ii) transfer success depends on whether a continuous mechanism can be expressed as meaningful combinatorial operators; (iii) local intensification remains highly sample-efficient; (iv) heavy-tail and population diversification become useful mainly when paired with a strong problem-facing interface; and (v) algorithm ranking changes with representation and landscape structure.

## Literature anchors

- Mohammed & Rashid, FOX, Applied Intelligence, DOI 10.1007/s10489-022-03533-0.
- Xue & Shen, Dung Beetle Optimizer, Journal of Supercomputing, DOI 10.1007/s11227-022-04959-6.
- Dehghani & Trojovský, Osprey Optimization Algorithm, Frontiers in Mechanical Engineering, DOI 10.3389/fmech.2022.1126450.
- Abdel-Basset et al., CPO, Knowledge-Based Systems, DOI 10.1016/j.knosys.2023.111257.
- Wang et al., BKA, Artificial Intelligence Review, DOI 10.1007/s10462-024-10723-4.
- Amiri et al., HO, Scientific Reports, DOI 10.1038/s41598-024-54910-3.
- Moss Growth Optimization, Journal of Computational Design and Engineering (2024).
- Ghasemi et al., Ivy Algorithm, Knowledge-Based Systems, DOI 10.1016/j.knosys.2024.111850.
- Pei et al., Adaptive Operator Selection for Meta-Heuristics: A Survey, IEEE TAI (2025), DOI 10.1109/TAI.2025.3545792.
- Suman et al., Metaheuristic algorithms: A benchmark-driven functional taxonomy and performance analysis, Computer Science Review 60 (2026), 100884.
