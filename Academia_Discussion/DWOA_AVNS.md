# DWOA-AVNS — Discrete Whale Optimization with Adaptive Variable-Neighborhood Search

## Design rationale and literature basis

DWOA-AVNS was designed after analyzing why the initial DWOA lost information when continuous WOA movement was translated too literally into combinatorial operators. Mirjalili and Lewis (2016) define WOA's exploration/exploitation logic; discrete scheduling studies such as Luan et al. (2019) show that crossover and variable-neighborhood mechanisms are useful when the state is a permutation. My design hypothesis was that PANCAKE contains **two coupled layers—visit order and source assignment—so effective moves should sometimes change both simultaneously**. I therefore retained the WOA-inspired change from exploration to exploitation but implemented it through leader-guided discrete recombination, a joint order–source relocation operator, competitive-offspring VNS, diversity/stagnation detection, and partial elite restarts. The intent was to preserve the high-level WOA search behavior while allowing the neighborhood definition, rather than the continuous equation, to encode problem knowledge.

## Performance and interpretation

With the same 1,200 objective evaluations, DWOA-AVNS reduced median RPD from **30.84% to 11.74%**, a **61.9% reduction** relative to DWOA-original. It obtained **1.26× GA-relative convergence efficiency** and a **3.53 mean rank**. The improvement supports the hypothesis that coupled neighborhoods and conditional intensification are more suitable for this representation than direct position-style movement. DWOA-AVNS remained competitive on deceptive and shared-hub landscapes, but DFOX-APNS achieved better aggregate quality and significantly lower paired costs in this pilot. The useful finding is therefore not that WOA is universally superior; it is that a continuous swarm method can become substantially more effective after its operators are redesigned around the actual combinatorial structure.

## Pseudocode and textual flowchart

```text
Algorithm: DWOA-AVNS
Input: problem P, population N, objective-evaluation budget B
1  Initialize double-layer whales: (permutation, source vector)
2  Evaluate population and select global leader x*
3  while evaluations < B:
4      update WOA exploration coefficient from budget progress
5      for each whale x_i:
6          choose leader-guided exploitation or population-guided exploration
7          create offspring by discrete recombination / alignment / relocation
8          optionally apply source mutation and coupled order-source move
9          evaluate offspring
10         if competitive: run a compact variable-neighborhood refinement
11         greedily update x_i and global leader x*
12     if stagnation or low diversity:
13         refine x* using VNS
14         partially restart weak whales around diverse elite perturbations
15 return x*
```

**Flow:** initialize coupled whales → select leader → WOA-inspired phase decision → discrete recombination → coupled route/source move → evaluation → conditional VNS → elite update → stagnation/diversity check → elite refinement and partial restart → repeat.

### References
- S. Mirjalili and A. Lewis, *The Whale Optimization Algorithm*, Advances in Engineering Software, 2016. DOI: 10.1016/j.advengsoft.2016.01.008.
- F. Luan et al., *Optimizing the Low-Carbon Flexible Job Shop Scheduling Problem with Discrete Whale Optimization Algorithm*, Mathematics, 2019. DOI: 10.3390/math7080688.
