# DFOX-APNS — Discrete FOX Optimization with Adaptive Prey-guided Neighborhood Search

## Design rationale, literature basis, and research hypothesis

DFOX-APNS starts from the **FOX optimizer** proposed by Mohammed and Rashid (2022), which models red-fox hunting through prey detection, exploration, exploitation, and jump-like movement. The original algorithm uses a fixed 50/50 phase choice; Jumaah et al. (2025) later identified this static balance and the original movement equations as limitations and proposed fitness-adaptive exploration/exploitation in IFOX. My design question was how to preserve the FOX search idea when a continuous position no longer exists. I treated the current best solution as the detected prey and redefined a "jump" as partial precedence/source alignment toward that prey. Exploration uses peer information plus long block, reversal, insertion, joint, and source moves. I further introduced a **fitness-, progress-, and diversity-aware exploration probability**, local prey-neighborhood refinement, and stagnation-triggered long jumps. My hypothesis was that FOX becomes useful for combinatorial optimization only when prey-guided motion is expressed as meaningful discrete neighborhoods rather than as a numeric coordinate transform.

## Performance and academic interpretation

Parameters were screened on ten disjoint development maps, after which the selected 12-agent configuration was frozen for the reported test set. Across **30 paired test cases**, DFOX-APNS achieved **6.69% median RPD**, **43.3% Success@5%**, **1.72× GA-relative convergence efficiency**, **2.10 mean rank**, and a **1.47% median exact gap**. The direct DFOX-Base mapping reached **39.83% median RPD**, so the redesign reduced median RPD by **83.2%**; their paired Wilcoxon difference was **p = 1.86×10⁻⁹**. DFOX-APNS was also significantly better than DWOA-AVNS in paired cost (**p = 0.0016**), while its comparison with GA+Tabu was not significant at 0.05 (**p = 0.0606**). Landscape-level behavior was informative: FOX was strongest on representative Clustered, Price–Distance Conflict, and Deceptive maps, whereas GA+Tabu remained stronger on Uniform and ACO on Shared Hubs. The finding therefore supports adaptive landscape-sensitive search rather than a universal-winner claim.

## Pseudocode and textual flowchart

```text
Algorithm: DFOX-APNS
Input: problem P, fox population N, objective-evaluation budget B
1  Initialize foxes as (commodity permutation, source vector)
2  Evaluate all foxes; prey x* <- best solution
3  while evaluations < B:
4      compute search progress, population diversity, and relative fitness
5      for each fox x_i:
6          compute adaptive exploration probability
7          if exploration:
8              combine x_i with a peer and execute a controlled long discrete jump
9              optionally retain a weak prey cue toward x*
10         else exploitation:
11             estimate discrete prey mismatch and jump partially toward x*
12             apply a coupled order/source hunting move
13         evaluate candidate
14         if candidate is competitive or search is late:
15             refine using adaptive prey-neighborhood search
16         update fox with greedy survival plus small early diversity allowance
17         update prey x* if improved
18     preserve elite prey
19     if stagnation or diversity collapse:
20         long-jump the weakest foxes using block/reversal/source moves
21         keep a small prey-guided component to avoid pure random restart
22 return x*
```

**Flow:** initialize fox population → detect best prey → estimate progress/fitness/diversity → adaptive exploration or prey-guided exploitation → discrete jump / coupled neighborhood move → evaluation → local prey refinement → elite update → stagnation/diversity check → long-jump weak foxes → repeat until the evaluation budget is exhausted.

### References
- H. M. Mohammed and T. A. Rashid, *FOX: a FOX-inspired optimization algorithm*, Applied Intelligence, 2022. DOI: 10.1007/s10489-022-03533-0.
- M. A. Jumaah, Y. H. Ali, and T. A. Rashid, *An improved FOX optimization algorithm using adaptive exploration and exploitation for global optimization*, PLOS ONE, 2025. DOI: 10.1371/journal.pone.0331965.
