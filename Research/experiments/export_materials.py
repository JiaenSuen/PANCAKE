from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Research" / "results"
PAPER = ROOT / "Research" / "07_Paper_Materials"
PAPER.mkdir(parents=True, exist_ok=True)


def main() -> None:
    main_runs = pd.read_csv(OUT / "main_runs.csv")
    family = (main_runs.groupby(["family", "algorithm"], as_index=False)["rpd_pct"]
              .median().rename(columns={"rpd_pct": "median_rpd_pct"}))
    family.to_csv(OUT / "family_algorithm_median_rpd.csv", index=False)

    tele = pd.read_csv(OUT / "operator_telemetry.csv")
    op = tele.groupby("operator", as_index=False).agg(
        calls=("calls", "sum"), success=("success", "sum"),
        total_improvement=("total_improvement", "sum"),
        early=("early", "sum"), mid=("mid", "sum"), late=("late", "sum"))
    op["success_rate"] = op["success"] / op["calls"].clip(lower=1)
    op["improvement_per_call"] = op["total_improvement"] / op["calls"].clip(lower=1)
    op = op.sort_values("success_rate", ascending=False)
    op.to_csv(OUT / "operator_aggregate.csv", index=False)

    snapshot = {
        "status": "research pilot; not a final camera-ready benchmark",
        "protocol": {
            "main": {"instances": 10, "seeds": 10, "objective_evaluations": 1200},
            "ablation": {"instances": 10, "seeds": 10, "objective_evaluations": 1200},
            "tpp_style_transfer": {"instances": 4, "seeds": 5, "objective_evaluations": 2400,
                                   "provenance": "protocol-regenerated EEuclideo-style instances, not official benchmark bytes"}
        },
        "files": {
            "main_summary": "Research/results/main_summary.csv",
            "ablation_summary": "Research/results/ablation_summary.csv",
            "tpp_style_summary": "Research/results/tpp_style_summary.csv",
            "operator_aggregate": "Research/results/operator_aggregate.csv",
            "family_summary": "Research/results/family_algorithm_median_rpd.csv"
        }
    }
    (OUT / "study_manifest.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print("Exported paper-material tables and manifest.")


if __name__ == "__main__":
    main()
