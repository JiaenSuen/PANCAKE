"""DWOA-AVNS: Discrete Whale Optimization with Adaptive Variable-Neighborhood Search.

This is the standalone implementation of the study variant reported in the README.
It operates on a coupled representation: permutation (visit order) + source index.
"""

from __future__ import annotations

import random

from .core import (
    RR,
    align,
    block_reloc,
    change_source,
    cross,
    evaluate,
    insert,
    joint_move,
    local_best_of,
    op_apply,
    pop_diversity,
    random_sol,
    reverse,
)


def run_dwoa_avns(p, seed: int, budget: int, npop: int = 20) -> RR:
    rng = random.Random(seed)
    evals = 0
    trace = []
    population = []

    for s in [random_sol(p, rng) for _ in range(npop)][: min(npop, budget)]:
        evaluate(p, s)
        evals += 1
        population.append(s)

    best = min(population, key=lambda s: s.score).clone()
    trace.append((evals, best.score))
    stagnation = 0

    while evals < budget:
        progress = evals / budget
        a = 2.0 * (1.0 - progress)
        improved = False

        for i in range(len(population)):
            if evals >= budget:
                break

            current = population[i]
            A = 2 * a * rng.random() - a
            p_branch = rng.random()

            # Discrete analogues of encircling / exploration / spiral search.
            if p_branch < 0.5 and abs(A) < 1:
                child = cross(current, best, rng)
                align(child, best, rng, 0.18 + 0.52 * (1 - abs(A)))
            elif p_branch < 0.5:
                reference = rng.choice(population)
                child = cross(current, reference, rng)
                block_reloc(child, rng)
            else:
                child = cross(current, best, rng)
                (insert if rng.random() < 0.5 else reverse)(child, rng)

            # Coupled source/order perturbation.
            if rng.random() < 0.72:
                change_source(p, child, rng, 1)
            if rng.random() < 0.28:
                joint_move(p, child, rng)

            evaluate(p, child)
            evals += 1

            # Competitive VNS: intensify only promising offspring.
            local = child
            if evals < budget and child.score <= current.score * 1.08:
                local, used = local_best_of(
                    p,
                    child,
                    rng,
                    ["swap", "insert", "reverse", "source", "joint"],
                    budget - evals,
                    tries=2,
                )
                evals += used

            if local.score < current.score:
                population[i] = local
            if local.score < best.score:
                best = local.clone()
                trace.append((evals, best.score))
                improved = True

        stagnation = 0 if improved else stagnation + 1

        # Trigger stronger VNS / partial restart only when the population stalls.
        if evals < budget and (stagnation >= 3 or pop_diversity(population) < 0.10):
            refined, used = local_best_of(
                p,
                best,
                rng,
                ["insert", "reverse", "joint", "source", "block"],
                budget - evals,
                tries=min(8, budget - evals),
            )
            evals += used
            if refined.score < best.score:
                best = refined.clone()
                trace.append((evals, best.score))
                stagnation = 0

            worst = sorted(
                range(len(population)), key=lambda k: population[k].score, reverse=True
            )[: max(1, len(population) // 5)]
            for wi in worst:
                if evals >= budget:
                    break
                z = best.clone()
                op_apply(p, z, rng, rng.choice(["block", "insert", "source", "joint"]))
                op_apply(p, z, rng, rng.choice(["swap", "source"]))
                evaluate(p, z)
                evals += 1
                population[wi] = z
                if z.score < best.score:
                    best = z.clone()
                    trace.append((evals, best.score))

    return RR("DWOA-AVNS", p.name, p.family, seed, best.score, evals, trace)


# Alias used by external scripts.
optimize = run_dwoa_avns
