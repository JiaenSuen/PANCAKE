# Experiment Maps

The research benchmark uses **10 synthetic maps**: five landscape families with two instances each.

| Family | Purpose |
|---|---|
| Uniform | Generic random supply topology; a neutral baseline landscape. |
| Clustered | Spatially clustered sources; tests route-order structure. |
| Price–Distance Conflict | Near sources are expensive and distant sources cheaper; forces source/order trade-offs. |
| Shared Hubs | Multiple demands share hub locations; rewards cross-demand coordination. |
| Deceptive Groups | Local choices can look attractive while coordinated group changes give better global solutions. |

- `JSON/` contains the **exact floating-point instances used by the Python benchmark and README tables**.
- `CSV/` contains human-readable / GUI-compatible versions using `Demand01`–`Demand16`. Coordinates and prices are rounded to integers for the legacy C# data model, so these CSV files are for visualization and interactive demonstration, **not** for reproducing the reported benchmark values.
- Copies of the GUI-compatible maps are also placed in `CSharp_GUI/PANCAKE_GUI_01/datasets/` with the prefix `research_`.
- `map_index.csv` summarizes family, node count, number of demands, and candidate links.

The reported test maps remain isolated from the DFOX-APNS population-size screen. Development-only maps are stored under `ResearchBenchmark/dev_datasets/` and are not used in Table 1 or Table 2.
