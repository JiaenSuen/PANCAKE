# 03 — Controlled DFOX Ablation

All four variants use the **same code path**, population size, seed pairing and 1,200 objective-evaluation budget. This avoids the confound of comparing independently written solvers.

## Variants

- **A0 — Generic:** fixed 50/50 explore/exploit; `swap/reverse/insert/block` only.
- **A1 — ProblemAware:** A0 + `source/joint` moves and problem-aware source perturbation.
- **A2 — Adaptive:** A1 + adaptive exploration probability and reward-based operator selection.
- **A3 — Full:** A2 + stagnation/diversity-triggered restart perturbation.

## 10-Seed Pilot Results

| Variant | Median RPD ↓ | Mean Rank ↓ |
|---|---:|---:|
| A2 Adaptive | **7.65** | **1.80** |
| A3 Full | 8.53 | 1.99 |
| A1 ProblemAware | 9.73 | 2.21 |
| A0 Generic | 33.65 | 4.00 |

Friedman: `p = 7.15e-40` across 100 paired map-seed cases.

### Pairwise evidence

- A0 vs A1: A1 wins **100/100**; Holm `p = 2.34e-17`.
- A0 vs A2: A2 wins **100/100**; Holm `p = 2.34e-17`.
- A1 vs A2: A2 wins 63/100; Holm `p = 5.78e-3`.
- A2 vs A3: the difference is **not significant after Holm correction** in the current pilot.

## Finding

The largest gain comes from making the neighborhood match the coupled problem structure. Adaptive operator control then supplies a smaller additional gain. The current restart mechanism is not validated: adding complexity after A2 does not improve the aggregate result. This negative result is useful because it prevents the paper from attributing every added module to success.
