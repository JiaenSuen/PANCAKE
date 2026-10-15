# 06 — Emerging Metaheuristic Transfer Study

Rather than adding five recent algorithms as a leaderboard, PANCAKE currently keeps three representatives with visibly different search mechanisms. The implementations are labelled **mechanism-preserving discrete adaptations**, not exact algebraic reproductions of the continuous originals.

## Selected Methods

### D-CPO — Crested Porcupine Optimizer transfer

Preserved ideas: four search modes (two exploration-oriented, two exploitation-oriented) and cyclic active-population reduction/regrowth. Discrete realization uses crossover/block/source moves for broad search and best-guided alignment + joint moves for exploitation.

### D-BKA — Black-winged Kite Algorithm transfer

Preserved ideas: leader-guided attack and heavy-tailed Cauchy mutation/migration. Discrete Cauchy behavior is represented by a heavy-tailed number of neighborhood applications.

### D-HO — Hippopotamus Optimization transfer

Preserved ideas: three phases corresponding to social positioning, defense/disruption, and escape/exploitation. The discrete form maps these phases to recombination, block/reverse/source disruption, and elite-guided joint/insert refinement.

## 10-Seed PANCAKE Pilot

| Emerging transfer | Median RPD ↓ | Mean Rank ↓ |
|---|---:|---:|
| **D-CPO** | **8.30** | **3.23** |
| D-BKA | 12.16 | 4.71 |
| D-HO | 18.77 | 6.36 |

D-CPO is significantly better than D-BKA and D-HO after Holm correction. D-CPO vs VNS-PA is essentially tied in the current paired study (50 wins / 50 losses; Holm-adjusted `p = 1.0`). D-CPO is significantly better than the current DFOX-APNS.

## Finding

The useful question is not whether a newer metaphor wins. CPO's discrete transfer performs well because its **multi-mode search and active-population schedule can be translated into concrete discrete diversification/intensification mechanisms**. BKA's heavy-tail behavior remains moderately competitive; the current HO mapping adds complexity without comparable benefit. This supports mechanism-level comparison rather than novelty-by-animal-name.

## Original method references

- Abdel-Basset, Mohamed, Abouhawwash. *Crested Porcupine Optimizer: A new nature-inspired metaheuristic*. Knowledge-Based Systems 284 (2024), 111257. DOI: 10.1016/j.knosys.2023.111257.
- Wang et al. *Black-winged kite algorithm: a nature-inspired meta-heuristic for solving benchmark functions and engineering problems*. Artificial Intelligence Review 57, 98 (2024). DOI: 10.1007/s10462-024-10723-4.
- Amiri et al. *Hippopotamus optimization algorithm: a novel nature-inspired optimization algorithm*. Scientific Reports 14, 5032 (2024). DOI: 10.1038/s41598-024-54910-3.


## Broader recent-method context

CPO/BKA/HO are the three **implemented** recent transfers because together they already cover distinct mechanism families. The literature review additionally tracks **MGO** and **IVYA**:

- **MGO (2024):** direction estimation, spore dispersal, dual propagation, and cryptobiosis/diversity preservation.
- **IVYA (2024):** neighbor-guided growth, spreading/climbing dynamics, and elite-centered refinement.

They are not added merely to increase the algorithm count. A future implementation is justified only if it contributes a mechanism not already represented by CPO/BKA/HO/FOX/WOA/ILS/VNS. This keeps the paper focused on **mechanism coverage** rather than recent-metaphor coverage.

The cross-family synthesis is maintained in `../10_Modern_Metaheuristic_Overview/`.
