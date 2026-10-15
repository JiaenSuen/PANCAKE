# Experiment Scripts

## `deepening_study.py`
Runs the main PANCAKE comparison, controlled DFOX ablation, TPP-style transfer study, statistics and figures.

```bash
python Research/experiments/deepening_study.py --seeds 10 --budget 1200 --tpp-seeds 5 --tpp-budget 2400
```

## `export_materials.py`
Derives operator aggregates, family-level result tables and an explicit protocol manifest from current results.

```bash
python Research/experiments/export_materials.py
```
