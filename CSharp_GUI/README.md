# PANCAKE C# GUI

This folder contains the original WinForms application, revised into an English interactive interface and reintegrated with the research maps and research algorithms.

## Requirements

- Windows 10/11
- .NET 8 SDK or Visual Studio 2022 with .NET Desktop Development workload

## Run

Use `RUN_GUI.bat`, or open `PANCAKE_GUI_01.sln` and run the project from Visual Studio.

Before first use, `VERIFY_GUI.bat` is recommended. It builds the solution and runs a smoke test covering legacy/research map loading, Greedy, Set Cover, DWOA-AVNS, and DFOX-APNS. The log is written to the Release output directory.

## Research integration

The GUI exposes the original methods plus the redesigned study variants. Interactive presets are intentionally smaller than the canonical Python benchmark so the desktop interface remains responsive.

Research algorithms:
- DWOA-AVNS
- DFOX-Base
- DFOX-APNS

Canonical reported results come from `../ResearchBenchmark/`, where each run is controlled by a fixed objective-evaluation budget. The C# versions are interactive ports for route visualization and manual demonstration.

Research source files are in:

```text
PANCAKE_GUI_01/PANCAKE/ResearchAlgorithms/
  DWOA_AVNS.cs
  DFOX_Base.cs
  DFOX_APNS.cs
  ResearchOperatorUtils.cs
```

All ten test maps are also available in the GUI dataset selector with the `research_` prefix.
