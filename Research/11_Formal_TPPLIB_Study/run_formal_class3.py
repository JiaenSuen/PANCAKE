"""Canonical 100-instance x 10-seed TPPLIB Class-3 experiment runner.

Research role
-------------
This is the external-validity layer for PANCAKE. It uses the 100 EEuclideo
official EEuclideo instances with audited reference metadata, PANCAKE's own parser/solvers, equal
objective-evaluation budgets, fixed paired seeds, and checkpointed output.

The runner intentionally does not import any third-party solver implementation.
"""
from __future__ import annotations

import argparse, csv, json, math, os, statistics, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
TPP_DIR = HERE.parent / "01_TPP_Benchmark"
if str(TPP_DIR) not in sys.path:
    sys.path.insert(0, str(TPP_DIR))

from tpplib_parser import parse_tpplib
from market_tour_solvers import run_ils, run_vns, run_dfox

METHODS = {"ILS": run_ils, "VNS": run_vns, "DFOX": run_dfox}
CHECKPOINTS = (60, 120, 240, 360, 480, 600, 720, 840, 960, 1080, 1200)


def load_baseline(path: Path) -> dict[str, dict]:
    out = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            out[r["Instance"]] = {
                "V": int(r["V"]), "K": int(r["K"]), "M_star": int(r["M*"]),
                "OPT": float(r["OPT"]), "reference_seconds": float(r["Sec"]),
            }
    return out


def instance_descriptors(path: Path, meta: dict) -> dict:
    inst = parse_tpplib(path)
    m = inst.dimension - 1  # purchasable markets, excluding depot
    k = len(inst.demands)
    offers_total = sum(len(rows) for market, rows in inst.offers.items() if market != inst.depot_market)
    offers_per_product = offers_total / max(1, k)
    offers_per_market = offers_total / max(1, m)
    offer_density = offers_total / max(1, m * k)
    return {
        "instance": inst.name,
        "V": meta["V"], "K": meta["K"], "market_choices": m,
        "offers_total": offers_total,
        "offers_per_product": offers_per_product,
        "offers_per_market": offers_per_market,
        "normalized_offer_density": offer_density,
        "product_market_ratio": k / max(1, m),
        "decision_scale": m * k,
        "M_star": meta["M_star"], "OPT": meta["OPT"],
    }


def _trace_at_checkpoints(trace: list[tuple[int, float]], opt: float, checkpoints: tuple[int, ...]):
    trace = sorted(trace)
    rows = []
    best = math.inf
    j = 0
    for cp in checkpoints:
        while j < len(trace) and trace[j][0] <= cp:
            best = min(best, trace[j][1]); j += 1
        # Initialization always happens well before first checkpoint. Fall back to first score if needed.
        if not math.isfinite(best) and trace:
            best = trace[0][1]
        gap = 100.0 * (best - opt) / opt
        rows.append((cp, best, gap))
    return rows


def _run_instance(task):
    path_s, meta, seeds, budget, methods, checkpoints = task
    path = Path(path_s)
    inst = parse_tpplib(path)
    prob = inst.to_market_tour_problem()
    run_rows, conv_rows = [], []
    for seed in seeds:
        for method in methods:
            fn = METHODS[method]
            r = fn(prob, seed, budget)
            gap = 100.0 * (r.score - meta["OPT"]) / meta["OPT"]
            signed_merr = r.visited_markets - meta["M_star"]
            run_rows.append({
                "instance": inst.name, "V": meta["V"], "K": meta["K"],
                "seed": seed, "algorithm": f"TPP-{method}",
                "score": r.score, "OPT": meta["OPT"], "gap_opt_pct": gap,
                "travel": r.travel, "purchase": r.purchase,
                "travel_share": r.travel / r.score if r.score else math.nan,
                "purchase_share": r.purchase / r.score if r.score else math.nan,
                "visited_markets": r.visited_markets, "M_star": meta["M_star"],
                "market_count_error": signed_merr,
                "abs_market_count_error": abs(signed_merr),
                "evaluations": r.evaluations, "seconds": r.seconds,
            })
            for fe, score, cp_gap in _trace_at_checkpoints(r.trace, meta["OPT"], checkpoints):
                conv_rows.append({
                    "instance": inst.name, "V": meta["V"], "K": meta["K"],
                    "seed": seed, "algorithm": f"TPP-{method}", "FE": fe,
                    "best_score": score, "gap_opt_pct": cp_gap,
                })
    return inst.name, run_rows, conv_rows


def write_rows(path: Path, rows: list[dict], append=False):
    if not rows: return
    mode = "a" if append and path.exists() else "w"
    with path.open(mode, newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        if mode == "w": w.writeheader()
        w.writerows(rows)


def assign_tertiles(vals: list[float]):
    s = sorted(vals)
    def q(p):
        if not s: return math.nan
        pos = (len(s)-1)*p; lo=int(math.floor(pos)); hi=int(math.ceil(pos))
        if lo==hi:return s[lo]
        return s[lo]*(hi-pos)+s[hi]*(pos-lo)
    return q(1/3), q(2/3)


def tier(v, q1, q2):
    if v <= q1: return "low"
    if v <= q2: return "medium"
    return "high"


def main():
    ap = argparse.ArgumentParser()
    default_idir = TPP_DIR / "official_data" / "EEuclideo"
    ap.add_argument("--instance-dir", default=str(default_idir))
    ap.add_argument("--baseline", default=None)
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--budget", type=int, default=1200)
    ap.add_argument("--methods", default="ILS,VNS,DFOX")
    ap.add_argument("--workers", type=int, default=min(5, os.cpu_count() or 1))
    ap.add_argument("--out", default=str(HERE / "results"))
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    idir = Path(args.instance_dir)
    baseline = Path(args.baseline) if args.baseline else idir / "Baseline_EEuclideo.csv"
    refs = load_baseline(baseline)
    methods = [m.strip().upper() for m in args.methods.split(",") if m.strip()]
    unknown = [m for m in methods if m not in METHODS]
    if unknown: raise ValueError(f"Unknown methods: {unknown}")
    seeds = [377 + 10007*i for i in range(args.seeds)]
    checkpoints = tuple(x for x in CHECKPOINTS if x <= args.budget)
    if args.budget not in checkpoints: checkpoints += (args.budget,)

    outdir = Path(args.out); outdir.mkdir(parents=True, exist_ok=True)
    runs_path = outdir / "formal_runs.csv"
    conv_path = outdir / "formal_convergence.csv"

    targets = []
    desc = []
    for name, meta in refs.items():
        p = idir / f"{name}.tpp"
        if not p.exists(): raise FileNotFoundError(p)
        targets.append((name, p, meta))
        desc.append(instance_descriptors(p, meta))
    targets.sort(key=lambda x: (x[2]["V"], x[2]["K"], x[0]))

    # Reproducible, descriptor-driven strata.
    pp_q1, pp_q2 = assign_tertiles([d["offers_per_product"] for d in desc])
    pm_q1, pm_q2 = assign_tertiles([d["offers_per_market"] for d in desc])
    for d in desc:
        d["scale_tier"] = "small" if d["V"] <= 100 else ("medium" if d["V"] <= 200 else "large")
        d["product_supply_density_tier"] = tier(d["offers_per_product"], pp_q1, pp_q2)
        d["market_assortment_density_tier"] = tier(d["offers_per_market"], pm_q1, pm_q2)
    write_rows(outdir / "instance_manifest.csv", sorted(desc, key=lambda d:(d["V"],d["K"],d["instance"])))

    completed = set()
    if args.resume and runs_path.exists():
        with runs_path.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                completed.add(r["instance"])
        print(f"Resume: {len(completed)} completed instances detected", flush=True)
    elif not args.resume:
        for p in (runs_path, conv_path):
            if p.exists(): p.unlink()

    pending = [(str(p), meta, seeds, args.budget, methods, checkpoints)
               for name,p,meta in targets if name not in completed]
    t0 = time.time(); done = len(completed)
    manifest = {
        "study": "PANCAKE Formal TPPLIB Class-3 Study",
        "instances": len(targets), "seeds": args.seeds, "budget": args.budget,
        "methods": methods, "paired_seeds": seeds, "checkpoints": checkpoints,
        "workers": args.workers,
        "reference_semantics": "Raw run generation is reference-independent. The imported baseline is provenance metadata only; manuscript analysis must use reference_registry.csv and reference-safe outputs.",
        "scale_tiers": {"small":"V<=100", "medium":"150<=V<=200", "large":"V>=250"},
        "density_definitions": {
            "offers_per_product":"number of feasible market offers / products",
            "offers_per_market":"number of feasible offers / purchasable markets",
            "normalized_offer_density":"offers / (purchasable_markets * products)",
            "product_supply_tertiles":[pp_q1,pp_q2],
            "market_assortment_tertiles":[pm_q1,pm_q2],
        },
    }
    (outdir / "study_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Formal study: {len(targets)} instances x {args.seeds} seeds x {len(methods)} methods = {len(targets)*args.seeds*len(methods)} runs", flush=True)
    print(f"Pending instances: {len(pending)}; workers={args.workers}", flush=True)

    if pending:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs = [ex.submit(_run_instance, t) for t in pending]
            for fut in as_completed(futs):
                name, rr, cc = fut.result()
                write_rows(runs_path, rr, append=True)
                write_rows(conv_path, cc, append=True)
                done += 1
                elapsed = time.time()-t0
                print(f"[{done}/{len(targets)}] {name} complete | elapsed={elapsed:.1f}s", flush=True)

    print(f"Completed formal run in {time.time()-t0:.1f}s", flush=True)

if __name__ == "__main__":
    main()
