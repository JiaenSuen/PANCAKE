# Research GUI Additions

The WinForms application remains an **interactive visualization/demo layer**. Canonical equal-objective-evaluation experiments are produced by the Python research scripts.

## Added selectable methods

- DFOX-A0 / A1 / A2 / A3 controlled ablation variants
- ILS (Problem-Aware)
- VNS (Problem-Aware)
- D-CPO (Research Transfer)
- D-BKA (Research Transfer)
- D-HO (Research Transfer)

The existing DWOA-AVNS, DFOX-Base and DFOX-APNS entries are retained.

## Added research maps

- `research_tpp_eeuclideo_style_50_50_01.csv`
- `research_tpp_eeuclideo_style_50_100_01.csv`

These maps allow GUI visualization of the larger market/product structure. They are generated from the published Euclidean TPP-style protocol and are **not official TPPLIB files**.

### Objective caveat

The GUI continues to use the legacy PANCAKE route-cost implementation so that old behavior is not broken. The canonical TPP-style experiment (explicit depot return and distance matrix) is implemented in `Research/experiments/deepening_study.py`. Therefore GUI costs on the TPP-style CSV should be treated as visualization/demo values, not as the paper's TPP transfer results.
