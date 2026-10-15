"""Run the PANCAKE research solvers on user-supplied official TPPLIB .tpp files.

No TPPLIB files are redistributed by this project. Point --input at a folder containing
legally obtained .tpp instances. Results are written to Research/results/tpplib_*.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for p in (ROOT, ROOT / "ResearchBenchmark", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from tpplib_parser import parse_tpplib  # noqa: E402
from algorithms import run_dfox_apns, run_dwoa_avns, run_ils, run_vns, run_dcpo, run_dbka  # noqa: E402
from meta_study import run_ga_tabu  # noqa: E402
from Research.experiments.deepening_study import summarize, statistical_tests, write_csv, OUT  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="TPPLIB .tpp file or directory")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--budget", type=int, default=2400)
    args = ap.parse_args()

    src = Path(args.input)
    files = [src] if src.is_file() else sorted(src.glob("*.tpp"))
    if not files:
        raise SystemExit(f"No .tpp files found under {src}")

    methods = [run_ga_tabu, run_dfox_apns, run_dwoa_avns, run_ils, run_vns, run_dcpo, run_dbka]
    rows = []
    for fi, path in enumerate(files, 1):
        inst = parse_tpplib(path)
        problem = inst.to_pancake_problem()
        print(f"[TPPLIB {fi}/{len(files)}] {problem.name}", flush=True)
        for s in range(args.seeds):
            seed = 377 + 10007 * s
            for fn in methods:
                rows.append(fn(problem, seed, args.budget))

    details, summary = summarize(rows, args.budget)
    write_csv(OUT / "tpplib_runs.csv", details)
    write_csv(OUT / "tpplib_summary.csv", summary)
    statistical_tests(details, "tpplib")
    print(f"Wrote {OUT / 'tpplib_summary.csv'}")


if __name__ == "__main__":
    main()
