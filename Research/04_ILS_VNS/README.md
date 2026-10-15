# 04 — Problem-Aware ILS / VNS

## Why these baselines were necessary

A paper comparing only FOX, WOA, PSO and other population metaphors cannot determine whether the apparent benefit comes from the global framework or simply from better neighborhoods. ILS and VNS deliberately reuse the same problem-aware low-level operators, providing a strong non-animal control.

## Implementations

- **ILS-PA:** VND refinement + coupled perturbation + mild non-greedy acceptance + restart after persistent stagnation.
- **VNS-PA:** systematic neighborhood escalation (`joint/source/insert/reverse/swap/block`) + shake + VND refinement.
- Both obey the same explicit objective-evaluation budget as the population methods.

## 10-Seed PANCAKE Pilot

| Method | Median RPD ↓ | Mean Rank ↓ |
|---|---:|---:|
| ILS-PA | **5.85** | **2.14** |
| D-CPO | 8.30 | 3.23 |
| VNS-PA | 8.14 | 3.24 |
| DFOX-APNS | 11.49 | 4.26 |
| D-BKA | 12.16 | 4.71 |
| DWOA-AVNS | 16.92 | 5.77 |
| GA+Tabu | 18.66 | 6.29 |
| D-HO | 18.77 | 6.36 |

ILS-PA beats DFOX-APNS in 77/100 paired cases and remains significant after Holm correction. ILS-PA also differs significantly from VNS-PA in the current paired design.

## Finding

This result changes the paper narrative in a productive way. PANCAKE should not argue that “a redesigned FOX is the best optimizer.” The stronger scientific conclusion is that **problem-aware neighborhood semantics and local improvement are first-order design decisions; population dynamics are a second-order layer that must justify their additional complexity.**

This direction is also consistent with modern TPP literature, where a 2025 EJOR paper reports a competitive ILS enhanced by route-configuration search.
