# Final Validation Record — 2026-10-13

## Executed in this revision

- TPPLIB parser fixture: **PASS**.
- Market-tour representation/reference-metadata test: **PASS**.
- Full controlled PANCAKE deepening study regenerated with 10 seeds and 1,200 FE; TPP-style transfer regenerated with 5 seeds and 2,400 FE.
- Regenerated main synthetic layer: 10 maps × 10 seeds × 8 algorithms = **800 runs**.
- Regenerated DFOX ablation: 10 maps × 10 seeds × 4 variants = **400 runs**.
- Formal external EEuclideo evidence remains the canonical audited 100-instance × 10-seed × 3-method = **3,000-run** study under 1,200 FE. A fresh spot rerun was initiated and reproduced successful instance completion before the interactive execution window; the archived canonical formal result set is retained rather than replacing it with a partial rerun.

## Final regenerated synthetic summary

| Method | Median RPD (%) | Mean rank |
|---|---:|---:|
| ILS-PA | 5.85 | 2.14 |
| VNS-PA | 8.14 | 3.24 |
| D-CPO | 8.30 | 3.23 |
| DFOX-APNS | 11.49 | 4.26 |
| D-BKA | 12.16 | 4.71 |
| DWOA-AVNS | 16.92 | 5.77 |
| GA+Tabu | 18.66 | 6.29 |
| D-HO | 18.77 | 6.36 |

## Final DFOX ablation

| Variant | Median RPD (%) | Interpretation |
|---|---:|---|
| A0 Generic | 33.65 | direct/generic transfer is inadequate |
| A1 Problem-aware | 9.73 | largest mechanism gain |
| A2 Adaptive | 7.65 | adaptive allocation adds value |
| A3 Full restart | 8.53 | restart does not improve A2 |

## Claim boundary

The final package does **not** claim state-of-the-art TPP performance, exact optimality for all Class-3 reference rows, or universal superiority of DFOX. The strongest supported contribution is a controlled study of representation, problem-aware neighborhood semantics, adaptive operator control, and mechanism–landscape interaction, complemented by a 2022–2026 mechanism taxonomy.
