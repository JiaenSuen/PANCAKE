"""Discrete research adaptations of recent continuous metaheuristics.

These are *mechanism-preserving discrete adaptations*, not claims of mathematically
identical ports of the authors' continuous update equations.  They are included to
study what survives when recent population-search mechanisms are transferred to a
coupled permutation + source-selection search space.

Included:
- D-CPO: Crested Porcupine Optimizer-inspired four-mode defense + cyclic active size.
- D-BKA: Black-winged Kite Algorithm-inspired leader search + Cauchy-like migration.
- D-HO: Hippopotamus Optimization-inspired social / defense / escape phases.
"""
from __future__ import annotations

import math
import random

from .core import (
    RR, align, block_reloc, change_source, cross, evaluate, insert, joint_move,
    local_best_of, op_apply, random_sol, reverse
)


def _init_pop(p, rng, budget, npop):
    pop=[]; ev=0; trace=[]
    for _ in range(min(npop,budget)):
        s=random_sol(p,rng); evaluate(p,s); ev+=1; pop.append(s)
    best=min(pop,key=lambda s:s.score).clone(); trace.append((ev,best.score))
    return pop,best,ev,trace


def _elite_replace(pop,best):
    if not pop:return
    wi=max(range(len(pop)),key=lambda i:pop[i].score)
    if best.score<pop[wi].score:pop[wi]=best.clone()


def run_dcpo(p, seed:int, budget:int, npop:int=18) -> RR:
    """Discrete CPO: four defensive modes and cyclic active-population reduction."""
    rng=random.Random(seed); pop,best,ev,trace=_init_pop(p,rng,budget,npop)
    min_active=max(5,npop//2); cycle=max(1,npop*3); step=0
    while ev<budget:
        step+=1; phase=(ev % cycle)/cycle
        active_n=max(min_active, int(round(npop-(npop-min_active)*phase)))
        # Preserve the current elite but sample the remaining active agents to retain diversity.
        ranked=sorted(range(len(pop)),key=lambda i:pop[i].score)
        active=[ranked[0]]
        pool=ranked[1:]
        rng.shuffle(pool);active+=pool[:max(0,min(active_n,len(pop))-1)]
        for i in active:
            if ev>=budget:break
            cur=pop[i]; mode=rng.randrange(4); child=cur.clone()
            if mode==0:  # sight: broad exploration
                peer=rng.choice(pop);child=cross(cur,peer,rng);block_reloc(child,rng)
                if rng.random()<.65:change_source(p,child,rng,1)
            elif mode==1:  # sound: stochastic long-range response
                for _ in range(1+rng.randrange(2)):
                    op_apply(p,child,rng,rng.choice(['reverse','insert','block','source']))
            elif mode==2:  # odor: prey/elite-guided exploitation
                align(child,best,rng,0.12+0.28*rng.random())
                if rng.random()<.65:joint_move(p,child,rng)
                else:change_source(p,child,rng,1)
            else:  # physical attack: aggressive local exploitation
                align(child,best,rng,0.28+0.34*rng.random())
                joint_move(p,child,rng)
                if rng.random()<.5:insert(child,rng)
            evaluate(p,child);ev+=1
            if child.score<cur.score:pop[i]=child
            if child.score<best.score:best=child.clone();trace.append((ev,best.score))
        _elite_replace(pop,best)
        # Cyclic regrowth: refresh inactive/worst individuals when a cycle wraps.
        if ev<budget and phase>0.90:
            for wi in sorted(range(len(pop)),key=lambda i:pop[i].score,reverse=True)[:max(1,npop//6)]:
                if ev>=budget:break
                z=random_sol(p,rng);evaluate(p,z);ev+=1;pop[wi]=z
                if z.score<best.score:best=z.clone();trace.append((ev,best.score))
    return RR('D-CPO',p.name,p.family,seed,best.score,ev,trace)


def _cauchy_step(rng,cap=5):
    # Heavy-tailed integer step count: mechanism analogue of Cauchy mutation.
    u=min(.999999,max(.000001,rng.random()))
    return max(1,min(cap,int(1+abs(math.tan(math.pi*(u-.5))))))


def run_dbka(p, seed:int, budget:int, npop:int=18) -> RR:
    """Discrete BKA: leader-guided attack plus Cauchy-like migration."""
    rng=random.Random(seed);pop,best,ev,trace=_init_pop(p,rng,budget,npop)
    while ev<budget:
        progress=ev/budget
        for i,cur in enumerate(list(pop)):
            if ev>=budget:break
            child=cur.clone()
            # Attack probability rises with progress; migration dominates earlier.
            if rng.random()<0.35+0.50*progress:
                align(child,best,rng,0.10+0.42*rng.random())
                if rng.random()<.60:joint_move(p,child,rng)
                else:insert(child,rng)
                if rng.random()<.55:change_source(p,child,rng,1)
            else:
                peer=rng.choice(pop)
                if rng.random()<.55:child=cross(cur,peer,rng)
                for _ in range(_cauchy_step(rng,5)):
                    op_apply(p,child,rng,rng.choice(['block','reverse','insert','source','joint']))
            evaluate(p,child);ev+=1
            # Greedy attack/migration selection, with occasional exploratory replacement early.
            if child.score<cur.score or rng.random()<0.04*(1-progress):pop[i]=child
            if child.score<best.score:best=child.clone();trace.append((ev,best.score))
        _elite_replace(pop,best)
    return RR('D-BKA',p.name,p.family,seed,best.score,ev,trace)


def run_dho(p, seed:int, budget:int, npop:int=18) -> RR:
    """Discrete HO: social movement, predator defense, and local escape phases."""
    rng=random.Random(seed);pop,best,ev,trace=_init_pop(p,rng,budget,npop)
    while ev<budget:
        progress=ev/budget
        for i,cur in enumerate(list(pop)):
            if ev>=budget:break
            child=cur.clone();r=rng.random()
            if r<0.40*(1-progress)+0.15:  # river/pond social positioning
                peer=rng.choice(pop);child=cross(cur,peer,rng)
                align(child,best,rng,0.08+0.22*rng.random())
                if rng.random()<.55:change_source(p,child,rng,1)
            elif r<0.78:  # predator defense: disruptive exploration
                block_reloc(child,rng)
                if rng.random()<.65:reverse(child,rng)
                change_source(p,child,rng,1+rng.randrange(2))
            else:  # escape / exploitation around a safe high-quality region
                align(child,best,rng,0.18+0.35*progress+0.15*rng.random())
                if rng.random()<.65:joint_move(p,child,rng)
                else:insert(child,rng)
            evaluate(p,child);ev+=1
            chosen=child
            if ev<budget and (child.score<cur.score or progress>.65):
                refined,used=local_best_of(p,child,rng,['joint','source','insert','reverse'],budget-ev,tries=2)
                ev+=used
                if refined.score<chosen.score:chosen=refined
            if chosen.score<cur.score:pop[i]=chosen
            if chosen.score<best.score:best=chosen.clone();trace.append((ev,best.score))
        _elite_replace(pop,best)
    return RR('D-HO',p.name,p.family,seed,best.score,ev,trace)


__all__=['run_dcpo','run_dbka','run_dho']
