"""DFOX-Base: direct discrete mapping of the 2022 FOX optimizer.

The original FOX uses a static 50/50 exploration/exploitation decision.  This
baseline preserves that policy while mapping continuous movement to PANCAKE's
coupled permutation + source-selection representation.  It is intentionally
simple and serves as the ablation baseline for DFOX-APNS.
"""
from __future__ import annotations
import math, random
from .core import RR, align, block_reloc, change_source, evaluate, insert, random_sol, reverse, swap


def _mismatch(a, b):
    n = len(a.order)
    pos_b = {d:i for i,d in enumerate(b.order)}
    order = sum(abs(i-pos_b[d]) for i,d in enumerate(a.order)) / max(1, n*n)
    source = sum(int(a.src[i] != b.src[i]) for i in range(n)) / max(1,n)
    return min(1.0, 0.65*order + 0.35*source)


def run_dfox_base(p, seed:int, budget:int, npop:int=20) -> RR:
    rng=random.Random(seed); ev=0; trace=[]; pop=[]
    for _ in range(min(npop,budget)):
        s=random_sol(p,rng); evaluate(p,s); ev+=1; pop.append(s)
    best=min(pop,key=lambda s:s.score).clone(); trace.append((ev,best.score))
    generation=0
    while ev<budget:
        generation += 1
        next_pop=[]
        for cur in pop:
            if ev>=budget: break
            child=cur.clone()
            # Original FOX uses a fixed 0.5 exploration/exploitation split.
            if rng.random() < 0.5:
                # Exploration: prey-sensing random walk translated to long discrete moves.
                # The jump magnitude grows with distance from the current best prey.
                m=_mismatch(cur,best)
                if rng.random() < 0.5: block_reloc(child,rng)
                else: reverse(child,rng)
                if rng.random() < 0.75: change_source(p,child,rng,1 + int(m*2))
                if rng.random() < 0.25: swap(child,rng)
            else:
                # Exploitation: jump toward the best prey using partial precedence/source alignment.
                m=_mismatch(cur,best)
                jump=max(1/len(child.order), min(0.55, 0.10 + 0.45*m*rng.random()))
                align(child,best,rng,jump)
                if rng.random() < 0.55: insert(child,rng)
                if rng.random() < 0.65: change_source(p,child,rng,1)
            evaluate(p,child); ev+=1
            # FOX agents move; retain a global elite separately.
            next_pop.append(child)
            if child.score < best.score:
                best=child.clone(); trace.append((ev,best.score))
        if next_pop: pop=next_pop
        if pop:
            worst=max(range(len(pop)),key=lambda i:pop[i].score)
            if best.score < pop[worst].score: pop[worst]=best.clone()
    return RR('DFOX-Base',p.name,p.family,seed,best.score,ev,trace)

optimize=run_dfox_base
