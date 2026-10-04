# Research Algorithms

The standalone files make the redesigned algorithms inspectable independently of the benchmark runner.

- `dwoa_avns.py` — **DWOA-AVNS**, discrete Whale Optimization with coupled order/source moves, adaptive VNS, diversity/stagnation control, and elite restart.
- `dfox_base.py` — **DFOX-Base**, a direct discrete mapping of the 2022 FOX optimizer used as an ablation baseline.
- `dfox_apns.py` — **DFOX-APNS**, discrete FOX with fitness/progress/diversity-aware phase control, prey-guided alignment, problem-specific multi-neighborhood search, and stagnation-triggered long jumps.
- `core.py` — common representation, objective, and discrete operators.

The main reported tables use these Python implementations. The C# GUI contains interactive ports for demonstration rather than the canonical benchmark protocol.
