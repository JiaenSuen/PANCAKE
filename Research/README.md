# Research Branch — Discrete Metaheuristic Representation and Mechanism Study

This folder extends the original commodity-centric benchmark without replacing the legacy study.  The goal is to turn the project from a solver-comparison demo into a controlled investigation of **how continuous/population metaheuristics should be transferred to a coupled discrete problem**.

## Research Questions

- **RQ1 — Problem-aware search:** Do neighborhoods that jointly respect commodity ordering and source selection matter more than generic permutation moves?
- **RQ2 — Adaptive operator control:** Does adaptive operator/phase selection add value after problem-aware neighborhoods are introduced?
- **RQ3 — Strong classical baselines:** Are FOX/WOA-style population methods still competitive against problem-aware ILS/VNS under the same objective-evaluation budget?
- **RQ4 — Emerging-method transfer:** Which mechanisms from recent continuous metaheuristics survive a discrete transfer, rather than merely retaining the animal metaphor?
- **RQ5 — TPP transfer:** Do the controlled-study findings persist when the objective is moved toward the classical Traveling Purchaser Problem (TPP) setting?
- **RQ6 — Representation:** How much apparent optimizer performance is actually caused by the genotype (commodity-centric vs. market-tour)?
- **RQ7 — Conditional strength:** Which landscape structures make FOX-style population dynamics competitive or weak relative to ILS/VNS?

## Experimental Evidence Stack

| Study | Instances | Seeds | FE budget | Evidence status |
|---|---:|---:|---:|---|
| Main controlled mechanism study | 10 structured PANCAKE maps | 10 | 1,200 | completed mechanism layer |
| Controlled DFOX ablation | 10 structured synthetic maps | 10 | 1,200 | completed controlled layer |
| TPP-style transfer | 4 protocol-regenerated instances | 5 | 2,400 | transfer pilot |
| Representation study | 2 EEuclideo-style stress tests × 2 encodings | 10 | 2,400 | completed controlled representation layer |
| **Official TPPLIB Class 3** | **100 genuine EEuclideo instances** | **10** | **1,200** | **canonical: 3,000 runs complete** |

The project now separates **pilot**, **controlled**, and **canonical external** evidence. The 100-instance TPPLIB suite is the paper's primary external-validity layer; synthetic controlled experiments remain essential for ablation, operator telemetry, and broad modern-metaheuristic mechanism coverage.

RPD is recomputed from the pooled BKS of the algorithms present in each experiment. Consequently, expanded-study RPD values are internally comparable within that study, but should not be read as direct numerical continuations of the original README Table 1 after new stronger methods change the pooled BKS.

## Current Findings Snapshot

1. **Problem-aware local search is a very strong baseline.** On 100 paired synthetic map-seed cases, ILS-PA obtained median RPD **5.85%** and mean rank **2.14**, ahead of the current population methods.
2. **Problem-aware neighborhoods are the largest controlled DFOX gain.** A0 generic operators produced median RPD **33.65%**; A1 problem-aware operators reduced it to **9.73%**. A0→A1 was better in all 100 paired cases and remained significant after Holm correction.
3. **Adaptive operator control adds a smaller but statistically supported gain.** A2 reached median RPD **7.65%** and significantly improved A1 under paired Wilcoxon + Holm testing.
4. **The restart layer is not automatically beneficial.** A3-Full reached median RPD **8.53%**; A2 vs. A3 is not significant after correction. This is useful negative evidence and suggests restart triggering needs redesign rather than being treated as an unconditional contribution.
5. **The coupled `joint` operator is mechanistically important.** In A3 telemetry it improved the incumbent on **24.4%** of calls, over twice the success rate of any other ordinary low-level operator; it also produced the largest improvement per call.
6. **D-CPO is the strongest of the three emerging transfers tested so far.** It achieved median RPD **8.30%** and mean rank **3.23**; D-CPO and VNS-PA are statistically indistinguishable in the present pilot, while D-CPO is significantly better than the current DFOX-APNS.
7. **TPP transfer exposes a representation/search gap.** On protocol-regenerated EEuclideo-style instances, ILS-PA dominates the transferred population methods. This should be interpreted as a stress-test finding, not as a TPPLIB benchmark result.
8. **Representation is now a measured first-order factor.** Across 20 paired cases per search family, market-tour encoding beats commodity-centric encoding in 100% of pairs. Median objective reduction is **47.56% for ILS, 51.07% for VNS, and 67.85% for DFOX**; commodity encoding also creates 45–48.5 repeated market visits at the median, versus zero by construction in market-tour.
9. **FOX is conditionally competitive rather than globally dominant.** On `shared_hubs`, DFOX's median score is only **0.14%** above ILS and it wins **45%** of paired cases; on `price_distance_conflict`, its median gap grows to **11.73%**. This makes landscape × mechanism interaction a central analysis target.
10. **Reliability distinguishes strong methods beyond median rank.** ILS-PA has q90 RPD **12.20%** and reaches RPD≤10% in **84%** of runs. DFOX-APNS has q90 **22.67%** and reaches the same threshold in **43%** of runs.
11. **The canonical TPPLIB layer is complete.** 100 EEuclideo instances × 10 paired seeds × ILS/VNS/DFOX × 1,200 FE yields **3,000 runs**. Per-instance median observed RPD is **3.07% / 6.70% / 8.68%** for ILS/VNS/DFOX, with Friedman **p=1.14×10⁻³⁴** and all paired contrasts significant after Holm correction.
12. **DFOX is structurally sensitive rather than uniformly weak.** Its RPD is significantly associated with product count (`ρ=0.305, p=0.0020`) and offers per market (`ρ=0.260, p=0.0089`); ILS shows no corresponding significant association. DFOX degrades from **7.32% to 10.75%** median RPD between small and large tiers, while ILS remains near 3%.
13. **Route/purchase decomposition identifies the residual mechanism bottleneck.** DFOX's median excess relative to the best tested component is **4.29% travel vs 1.51% purchase**; on the large tier it is **4.83% vs 0.41%**. Its external weakness is therefore primarily route/tour intensification.
14. **Anytime evidence agrees with the final ranking.** Median observed-RPD AUC is **5.85 (ILS), 9.60 (VNS), 12.39 (DFOX)**. Coverage of RPD≤5% is **65.4%, 43.3%, 32.5%**, respectively.
15. **Reference semantics were formally audited.** The imported legacy `OPT` column is not exact for all 100 rows. Primary external statistics now use pooled observed RPD; 11 published open-instance BKS values are analyzed separately, and legacy closed-reference candidates are restricted to secondary diagnostics. This correction is documented rather than silently overwritten.

## Folder Map

- `01_TPP_Benchmark/` — TPP formulation bridge, instance provenance, protocol-regenerated data and future TPPLIB integration.
- `02_ProblemAware_APNS/` — neighborhood semantics, APNS/AOS interpretation and operator telemetry.
- `03_Ablation/` — controlled A0/A1/A2/A3 experiment and incremental causal claims.
- `04_ILS_VNS/` — problem-aware ILS/VNS baselines and why they are methodologically essential.
- `05_Statistics/` — paired experimental design, RPD/AUC/rank metrics, Friedman/Wilcoxon/Holm procedure.
- `06_Emerging_Metaheuristics/` — mechanism-preserving discrete CPO/BKA/HO transfers and findings.
- `07_Paper_Materials/` — findings bank, paper outline, experiment matrix, related-work notes, limitations, and TikZ figure fragments.
- `08_Mechanism_Analysis/` — conditional performance, reliability, performance profiles, representation effects, exploratory structure diagnostics.
- `09_Auxiliary_Routing_Data/` — provenance-audited user upload retained only as routing-only auxiliary data.
- `10_Modern_Metaheuristic_Overview/` — mechanism taxonomy and literature positioning beyond FOX.
- `11_Formal_TPPLIB_Study/` — **canonical 100-instance / 3,000-run paper evidence**, reference audit, findings ledger, tables and figures.
- `experiments/` — reproducible scripts.
- `results/` — raw runs, summaries, tests, telemetry and figures.

## Reproduction

```bash
cd <project-root>
pip install -r ResearchBenchmark/requirements.txt
python Research/experiments/deepening_study.py --seeds 10 --budget 1200 --tpp-seeds 5 --tpp-budget 2400
python Research/experiments/export_materials.py
python Research/01_TPP_Benchmark/run_representation_study.py --seeds 10 --budget 2400
python Research/08_Mechanism_Analysis/mechanism_analysis.py
```

For a fast smoke test:

```bash
python Research/experiments/deepening_study.py --quick
```

The smoke-test output is for software validation only and must not replace the 1,200-FE research protocol.

## Current benchmark-integration milestone

The TPPLIB branch is now a **completed canonical external experiment**, not merely infrastructure. The project contains 100 genuine EEuclideo Class-3 instances (50–250 markets; 50–200 products), a market-tour + induced-procurement representation, strict FE accounting, and a 3,000-run paired benchmark across ILS/VNS/DFOX.

A critical semantics audit corrected an earlier assumption: the imported `Baseline_EEuclideo.csv` does **not** provide 100 universally exact OPT values. Historical literature distinguishes closed and open Class-3 instances. PANCAKE therefore makes the 100-instance comparison reference-safe through pooled observed RPD and uses published BKS only on independently supported open cases. See `11_Formal_TPPLIB_Study/REFERENCE_SEMANTICS_AUDIT.md`.

The current external layer supports three high-level conclusions: (1) problem-aware local intensification is the strongest fixed-budget baseline; (2) DFOX degradation is disproportionately associated with product/assortment breadth; and (3) DFOX's residual error is route-side more than procurement-side, which motivates hybrid route polishing rather than additional blind exploration. The broader paper remains a **modern metaheuristic mechanism study**, with FOX as one deep case study rather than the paper's center.