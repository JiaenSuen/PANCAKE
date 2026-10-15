# Literature Map — Recent Metaheuristics and Mechanism-Level Positioning

This document supports the **Related Work / Research Positioning** section. The purpose is not to reproduce every recent optimizer, but to identify reusable search mechanisms and methodological trends relevant to PANCAKE.

## Methodological context

1. **Sörensen, K. (2015).** *Metaheuristics—the metaphor exposed.* International Transactions in Operational Research 22(1):3–18. DOI: `10.1111/itor.12001`.
   - Key role: argues that metaphor alone is not scientific novelty and encourages analysis in standard optimization terminology.

2. **Campelo / Aranha et al. (2021).** *Metaphor-based metaheuristics, a call for action: the elephant in the room.* Swarm Intelligence. DOI: `10.1007/s11721-021-00202-9`.
   - Key role: asks authors to show useful new optimization concepts, fair benchmarking, and metaphor-free descriptions.

3. **Shaikh et al. (2025).** *Applications, classifications, and challenges: a comprehensive evaluation of recently developed metaheuristics for search and analysis.* Artificial Intelligence Review 58:390. DOI: `10.1007/s10462-025-11377-6`.
   - Key role: surveys 162 metaheuristics and highlights algorithm explosion, premature convergence, inconsistent benchmarking, and the need for structural/mechanism-level interpretation.

4. **Pei, Mei, Liu, Zhang, Yao (2025).** *Adaptive Operator Selection for Meta-Heuristics: A Survey.* IEEE Transactions on Artificial Intelligence 6(8):1991–2012. DOI: `10.1109/TAI.2025.3545792`.
   - Key role: provides the most direct theoretical umbrella for PANCAKE's APNS / future hyper-heuristic direction.

## Implemented recent metaheuristics

### CPO — Crested Porcupine Optimizer
- Abdel-Basset, Mohamed, Abouhawwash (2024), Knowledge-Based Systems 284:111257. DOI: `10.1016/j.knosys.2023.111257`.
- Mechanisms extracted for PANCAKE: **multiple exploration/exploitation modes + cyclic population reduction**.
- PANCAKE interpretation: phase switching and active-population scheduling, not the porcupine metaphor.

### BKA — Black-winged Kite Algorithm
- Wang et al. (2024), Artificial Intelligence Review 57:98. DOI: `10.1007/s10462-024-10723-4`.
- Mechanisms: **leader guidance + Cauchy mutation / heavy-tailed migration**.
- PANCAKE interpretation: elite attraction plus heavy-tailed number/strength of discrete moves.

### HO — Hippopotamus Optimization
- Amiri et al. (2024), Scientific Reports 14:5032. DOI: `10.1038/s41598-024-54910-3`.
- Mechanisms: **three-phase positioning, defense/disruption, and escape/exploitation**.
- PANCAKE interpretation: phase-specific neighborhood/recombination schedules.

## Literature-context recent metaheuristics

### MGO — Mountain Gazelle Optimizer
- Abdollahzadeh, Soleimanian Gharehchopogh, Khodadadi, Mirjalili (2022), *Advances in Engineering Software* 174:103282. DOI: `10.1016/j.advengsoft.2022.103282`.
- Mechanisms: **four parallel behavior/update modes, best-guided social hierarchy, stochastic exploration, and an explicit exploration–exploitation schedule**.
- Why currently literature-only: the four-mode idea overlaps CPO/HO phase switching already covered in the implemented suite. Add MGO only if the study tests a specific multi-mode diversity hypothesis rather than increasing the optimizer count.
- Acronym note: some later papers also use “MGO” for other optimizers; in PANCAKE, **MGO always means Mountain Gazelle Optimizer (2022)**.

### IVYA — Ivy Algorithm
- Ghasemi et al. (2024), Knowledge-Based Systems. DOI: `10.1016/j.knosys.2024.111850`.
- Mechanisms: **neighbor-guided growth, spreading/climbing behavior, elite-centered local expansion**.
- Why currently literature-only: useful for discussing neighbor guidance and local refinement, but not required for the current core experiment unless broader recent-method coverage is requested.

## How PANCAKE should cite these methods

Avoid a paragraph of the form “CPO simulates porcupines, BKA simulates birds, HO simulates hippos...” as the main comparison. Prefer:

> Recent population metaheuristics increasingly combine recurring algorithmic primitives such as leader guidance, heavy-tailed perturbation, phase switching, population-size control, diversity preservation and local refinement. PANCAKE therefore compares selected recent methods at the mechanism level and evaluates whether these primitives remain effective after transfer to a structured combinatorial search space.

This wording aligns the work with current criticism of superficial metaphor-based novelty and makes the paper's contribution more defensible.
