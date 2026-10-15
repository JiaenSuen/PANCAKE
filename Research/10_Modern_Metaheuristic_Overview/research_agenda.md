# Modern Metaheuristic Research Agenda

## Paper thesis candidate

> In structured discrete optimization, algorithm performance is mediated by representation and problem-aware neighborhoods; recent metaheuristic mechanisms differ in how well they survive discrete transfer, and adaptive operator selection offers a principled way to combine complementary mechanisms.

## Evidence layers

1. **Baseline layer:** ILS/VNS/GA/Tabu establish what strong discrete search can already achieve.
2. **Transfer layer:** D-CPO/D-BKA/D-HO/DFOX/DWOA test whether population mechanisms survive discretization.
3. **Mechanism layer:** ablation and telemetry isolate problem-aware neighborhoods, adaptive operator control and restart.
4. **Interaction layer:** family profiles and representation studies explain conditional strength/failure modes.
5. **External layer:** official TPPLIB cases measure BKS/OPT gap and purchase/travel decomposition.

## What not to do

- Do not make the contribution “we tested many animals.”
- Do not overfit all discussion to FOX.
- Do not interpret one global rank as a universal algorithm hierarchy.
- Do not label a BKS as OPT for open 300/350-market instances.
- Do not add MGO/IVYA unless they provide a genuinely missing mechanism or a reviewer requests a broader contemporary baseline.
