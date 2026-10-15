# Research Algorithms

The standalone files make the redesigned algorithms inspectable independently of the benchmark runner.

- `dwoa_avns.py` — **DWOA-AVNS**, discrete Whale Optimization with coupled order/source moves, adaptive VNS, diversity/stagnation control, and elite restart.
- `dfox_base.py` — **DFOX-Base**, a direct discrete mapping of the 2022 FOX optimizer used as an ablation baseline.
- `dfox_apns.py` — **DFOX-APNS**, discrete FOX with fitness/progress/diversity-aware phase control, prey-guided alignment, problem-specific multi-neighborhood search, and stagnation-triggered long jumps.
- `core.py` — common representation, objective, and discrete operators.

The main reported tables use these Python implementations. The C# GUI contains interactive ports for demonstration rather than the canonical benchmark protocol.

## Research deepening modules

- `dfox_ablation.py`: A0 generic → A1 problem-aware → A2 adaptive AOS → A3 restart, all on one controlled code path.
- `ils_vns.py`: problem-aware ILS/VNS baselines sharing the same low-level neighborhood semantics.
- `emerging.py`: discrete mechanism-transfer study for CPO, BKA and HO. These are explicitly not claimed to be exact algebraic ports.
- `core.py`: optional TPP-style depot/distance-matrix evaluation while preserving legacy PANCAKE behavior.
