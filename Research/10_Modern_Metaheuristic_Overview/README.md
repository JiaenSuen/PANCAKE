# 10 — Modern Metaheuristic Overview and Mechanism-Level Research Frame

## Why this branch exists

PANCAKE should **not** become a FOX paper. FOX is one substantial experimental branch because it motivated the original discrete transfer and ablation study, but the broader scientific question is:

> **What algorithmic mechanisms from classical and recent metaheuristics remain useful after they are transferred to a structured combinatorial problem, and how do representation, neighborhoods, adaptive control and landscape structure mediate their effectiveness?**

This framing deliberately separates **algorithm name / metaphor** from **search mechanism**. Recent metaheuristics such as CPO, BKA, HO, MGO and IVYA are therefore treated as collections of reusable mechanisms rather than as five independent animals/plants that must all be ranked.

## Mechanism-level taxonomy

| Layer | Examples | Mechanisms to study | PANCAKE role |
|---|---|---|---|
| Trajectory/local search | ILS, VNS, Tabu | perturbation, neighborhood change, intensification | strong discrete baselines |
| Evolutionary | GA, DE | recombination, mutation, selection | established reference family |
| Swarm/leader-guided | PSO, WOA, FOX | elite attraction, population diversity, exploration schedule | historical transfer cases |
| Recent multi-mode | CPO | multi-mode switching, cyclic active-population control | implemented D-CPO |
| Heavy-tail leader-guided | BKA | Cauchy/heavy-tail perturbation, leader guidance | implemented D-BKA |
| Multi-phase | HO | phase-specific update rules | implemented D-HO |
| Memory/diversity/growth | MGO, IVYA | direction estimation, memory, neighbor-guidance, spreading | literature-context / future transfer |
| Meta-level control | AOS, hyper-heuristics | operator credit, online selection, parameter control | APNS and next-stage framework |

## Current empirical picture

The current 100-paired-case PANCAKE study does **not** support a simple “newer is better” narrative. ILS-PA is strongest overall, D-CPO is statistically tied with VNS-PA, D-BKA is competitive but weaker, and D-HO is substantially weaker. DFOX lies between CPO/VNS and BKA in the global ranking but becomes nearly competitive with ILS on shared-hub landscapes.

This suggests three stronger research statements:

1. **Problem-aware search architecture dominates novelty-by-metaphor.** ILS/VNS can outperform newer population methods when neighborhoods encode the coupled procurement-routing structure directly.
2. **Some recent mechanisms survive discretization better than others.** CPO-style mode switching and population control transfer more effectively than the current HO phase mapping; BKA heavy-tail behavior remains useful but not dominant.
3. **Algorithm ranking is conditional on representation and landscape.** FOX improves dramatically when the genotype is changed to a market-tour representation and becomes competitive on shared-hub instances, showing that a single global rank hides important interactions.

## Broader research questions

- **RQ-M1 — Mechanism survival:** Which continuous-population mechanisms retain measurable value after discrete transfer?
- **RQ-M2 — Structure interaction:** Which problem structures favor local intensification, leader guidance, heavy-tailed perturbation, or multi-mode search?
- **RQ-M3 — Representation mediation:** Does an optimizer appear weak because of its update dynamics or because its representation is misaligned with the physical problem?
- **RQ-M4 — Adaptive control:** Can adaptive operator selection learn when each low-level mechanism is useful instead of fixing a single optimizer architecture?
- **RQ-M5 — External validity:** Do these mechanism-level findings persist on true TPPLIB instances with OPT/BKS references?

## Scope control for the current paper

The paper should not implement every recent optimizer. The implemented set **CPO + BKA + HO** is sufficient to provide three distinct contemporary mechanism profiles, while **MGO + IVYA** are used in Related Work to show that recent research increasingly adds explicit diversity, memory, direction estimation and local-refinement mechanisms. If a fourth recent transfer is later required, choose it because it adds a **missing mechanism**, not because it has a newer publication date.

## Literature context

- Sörensen (2015), *Metaheuristics—the metaphor exposed*, argues for analysis of actual optimization mechanisms rather than superficial metaphor novelty.
- Campelo & Aranha et al. (2021), *Metaphor-based metaheuristics, a call for action*, calls for standard optimization terminology, useful novel concepts and fair state-of-the-art benchmarking.
- Pei et al. (2025), *Adaptive Operator Selection for Meta-Heuristics: A Survey*, provides the meta-level framework most directly connected to PANCAKE's APNS direction.
- Abdel-Basset et al. (2024), CPO: multi-mode exploration/exploitation plus cyclic population reduction.
- Wang et al. (2024), BKA: leader strategy plus Cauchy mutation.
- Amiri et al. (2024), HO: three-phase search.
- Moss Growth Optimization (2024): direction estimation, dispersal/propagation and cryptobiosis/diversity mechanisms.
- Ghasemi et al. (2024), IVYA: neighbor-guided growth and spreading/climbing dynamics.

The project uses these papers to motivate **mechanism categories**, not to claim that biological inspiration itself is the source of optimization novelty.
