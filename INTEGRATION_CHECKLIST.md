# PANCAKE Integration Checklist

## Application
- [x] Original C# WinForms GUI retained and English-localized
- [x] Legacy maps retained
- [x] Ten research test maps integrated into the GUI
- [x] Background-task execution and dataset-path fixes retained
- [x] GUI smoke test retained

## Research algorithms
- [x] DWOA-AVNS standalone Python implementation
- [x] DFOX-Base standalone Python ablation
- [x] DFOX-APNS standalone Python implementation
- [x] DWOA-AVNS C# interactive port
- [x] DFOX-Base C# interactive port
- [x] DFOX-APNS C# interactive port
- [x] FOX optimizer research line fully integrated across code, GUI, benchmark, and documentation

## Benchmark
- [x] Five landscape families × two reported test maps
- [x] Three paired seeds × ten algorithms = 300 reported runs
- [x] 1,200 objective evaluations per reported run
- [x] Ten disjoint development maps for FOX population-size screening
- [x] Exact-solvable mini-suite
- [x] Table 1 CSV + paper-style PNG
- [x] Table 2 representative-map mean-cost CSV
- [x] Friedman and paired Wilcoxon interpretation

## Documentation
- [x] Main academic README updated for FOX optimizer
- [x] Per-algorithm Academia_Discussion files updated
- [x] DWOA-AVNS and DFOX-APNS pseudocode / textual flowcharts
- [x] Updated CV result
- [x] Updated Chinese admission-portfolio text
- [x] DWOA-AVNS / DFOX-APNS editable Graphviz sources and rendered PNG figures

## FOX integration validation
- [x] Legacy misidentified optimizer line removed from the active project
- [x] DFOX-Base and DFOX-APNS are the active FOX-family methods
- [x] Combined editable Graphviz flowchart stored at `docs/figures/PANCAKE_algorithms.dot`
- [x] Legacy non-FOX optimizer references removed from filenames, source, documentation, figures, and GUI labels
