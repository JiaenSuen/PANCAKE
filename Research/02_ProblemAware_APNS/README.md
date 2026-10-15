# 02 — Problem-Aware Neighborhoods and APNS/AOS

## Hypothesis

PANCAKE contains two coupled decision layers: commodity visit order and source selection. Generic permutation moves modify only the route representation, while a source-only move modifies procurement without considering route context. A stronger neighborhood should alter both decisions coherently.

## Low-level operators

- `swap`, `reverse`, `insert`, `block`: generic permutation operators.
- `source`: changes the selected market for one commodity.
- `joint`: relocates one commodity and simultaneously reselects its source using a predecessor/successor purchase-plus-travel proxy.
- `restart_jump`: composite perturbation used only by the full restart layer.

## Adaptive layer

A2/A3 maintain operator weights. Successful moves receive a reward that scales with relative objective improvement; unsuccessful moves decay toward a small prior. Exploration probability depends on normalized search progress, current solution quality and population diversity. This is best described as **adaptive operator selection (AOS) / selection hyper-heuristic behavior over problem-aware low-level heuristics**, rather than as a new animal metaphor.

## Telemetry Finding

Aggregated over the 10-map × 10-seed A3 pilot:

| Operator | Calls | Improvement Success Rate | Improvement / Call |
|---|---:|---:|---:|
| joint | 25,960 | **24.42%** | **13.07** |
| reverse | 18,290 | 11.77% | 5.38 |
| insert | 17,988 | 10.74% | 5.71 |
| swap | 17,011 | 9.52% | 4.78 |
| source | 17,548 | 9.33% | 5.39 |
| block | 16,899 | 8.30% | 5.28 |
| restart_jump | 5,104 | 1.47% | 0.34 |

The `joint` operator is more than twice as likely to improve the incumbent as any other normal operator. This is direct mechanistic evidence that a neighborhood encoding the **order–source interaction** is more productive than generic move semantics.

## Paper-safe interpretation

The evidence supports: “problem-aware coupled neighborhoods are a major performance driver.” It does **not** prove that the particular joint proxy is optimal or universally superior. The low restart success rate also suggests the current long-jump design is too indiscriminate and should not be advertised as a confirmed improvement.
