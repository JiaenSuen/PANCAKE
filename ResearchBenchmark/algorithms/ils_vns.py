"""Problem-aware ILS and VNS baselines for PANCAKE.

These methods deliberately use the same low-level operators as the redesigned FOX/WOA
methods.  They therefore answer a critical methodological question: is performance
coming from the population metaphor, or simply from a good problem-aware neighborhood?
All methods obey an explicit objective-evaluation budget.
"""
from __future__ import annotations

import math
import random
from .core import RR, evaluate, op_apply, random_sol


DEFAULT_NEIGHBORHOODS = ["joint", "source", "insert", "reverse", "swap", "block"]


def _seed_best(p, rng: random.Random, budget: int, count: int = 8):
    used = 0
    best = None
    for _ in range(min(count, budget)):
        s = random_sol(p, rng)
        evaluate(p, s)
        used += 1
        if best is None or s.score < best.score:
            best = s.clone()
    return best, used


def _best_sampled_neighbor(p, base, rng, op, remaining: int, samples: int = 5):
    best = base.clone()
    used = 0
    for _ in range(min(samples, remaining)):
        z = base.clone()
        op_apply(p, z, rng, op)
        evaluate(p, z)
        used += 1
        if z.score < best.score:
            best = z
    return best, used


def _vnd(p, start, rng, remaining: int, neighborhoods=None, samples: int = 4):
    neighborhoods = neighborhoods or DEFAULT_NEIGHBORHOODS
    cur = start.clone()
    used = 0
    k = 0
    while used < remaining and k < len(neighborhoods):
        z, n = _best_sampled_neighbor(p, cur, rng, neighborhoods[k], remaining - used, samples)
        used += n
        if z.score < cur.score:
            cur = z
            k = 0
        else:
            k += 1
    return cur, used


def run_ils(p, seed: int, budget: int, init_count: int = 8, return_best: bool = False):
    rng = random.Random(seed)
    best, ev = _seed_best(p, rng, budget, init_count)
    current = best.clone()
    trace = [(ev, best.score)]
    no_improve = 0

    while ev < budget:
        refined, used = _vnd(p, current, rng, budget - ev, samples=3)
        ev += used
        if refined.score < best.score:
            best = refined.clone()
            trace.append((ev, best.score))
            no_improve = 0
        else:
            no_improve += 1

        # ILS perturbation: destroy both route order and source assignment.  The
        # perturbation strength grows during stagnation but remains problem-aware.
        current = refined.clone() if refined.score <= current.score else current.clone()
        strength = min(4, 1 + no_improve // 2)
        for j in range(strength):
            if ev >= budget:
                break
            op = "block" if j == 0 else rng.choice(["joint", "source", "insert", "reverse"])
            z = current.clone()
            op_apply(p, z, rng, op)
            evaluate(p, z)
            ev += 1
            # Keep a mildly non-greedy state transition to escape local optima.
            delta = z.score - current.score
            temp = max(1e-9, 0.015 * best.score * (1.0 - ev / max(1, budget)) + 1e-9)
            if delta <= 0 or rng.random() < math.exp(-max(0.0, delta) / temp):
                current = z
            if z.score < best.score:
                best = z.clone()
                trace.append((ev, best.score))
                no_improve = 0
        if no_improve >= 6 and ev < budget:
            # Restart around a fresh feasible point, while preserving global elite.
            current = random_sol(p, rng)
            evaluate(p, current)
            ev += 1
            no_improve = 0
            if current.score < best.score:
                best = current.clone()
                trace.append((ev, best.score))

    rr=RR("ILS-PA", p.name, p.family, seed, best.score, ev, trace)
    return (rr,best.clone()) if return_best else rr


def run_vns(p, seed: int, budget: int, init_count: int = 8, return_best: bool = False):
    rng = random.Random(seed)
    best, ev = _seed_best(p, rng, budget, init_count)
    current = best.clone()
    trace = [(ev, best.score)]
    neighborhoods = DEFAULT_NEIGHBORHOODS
    k = 0

    while ev < budget:
        op = neighborhoods[k]
        shaken = current.clone()
        # Larger neighborhoods get a slightly stronger shake.
        for _ in range(1 + int(k >= 4)):
            op_apply(p, shaken, rng, op)
        evaluate(p, shaken)
        ev += 1

        local, used = _vnd(p, shaken, rng, budget - ev, neighborhoods[: max(3, k + 1)], samples=2)
        ev += used
        if local.score < current.score:
            current = local
            k = 0
            if current.score < best.score:
                best = current.clone()
                trace.append((ev, best.score))
        else:
            k += 1
            if k >= len(neighborhoods):
                k = 0
                # Shake the current elite more strongly at the end of a full VNS cycle.
                current = best.clone()
                if ev < budget:
                    op_apply(p, current, rng, "block")
                    op_apply(p, current, rng, "source")
                    evaluate(p, current)
                    ev += 1
                    if current.score < best.score:
                        best = current.clone()
                        trace.append((ev, best.score))

    rr=RR("VNS-PA", p.name, p.family, seed, best.score, ev, trace)
    return (rr,best.clone()) if return_best else rr


optimize_ils = run_ils
optimize_vns = run_vns
