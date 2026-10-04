"""DFOX-APNS: Discrete FOX Optimization with Adaptive Prey-guided Neighborhood Search.

Research design for PANCAKE.  It keeps the FOX hunting metaphor (prey-guided
movement, jump-like exploration and exploitation) but replaces continuous
coordinates with operators that preserve a coupled permutation + source vector.
The static 50/50 phase choice of the original FOX is replaced with a
fitness/progress/diversity-aware policy inspired by the adaptive motivation of
IFOX (Jumaah et al., 2025).  Problem-specific multi-neighborhood search and
stagnation-triggered long jumps provide discrete intensification/diversification.
"""
from __future__ import annotations
import math, random
from .core import (
    RR, align, block_reloc, change_source, cross, evaluate, insert, joint_move,
    local_best_of, op_apply, pop_diversity, random_sol, reverse, swap
)


def _mismatch(a,b):
    n=len(a.order); pos={d:i for i,d in enumerate(b.order)}
    order=sum(abs(i-pos[d]) for i,d in enumerate(a.order))/max(1,n*n)
    source=sum(int(a.src[i]!=b.src[i]) for i in range(n))/max(1,n)
    return min(1.0,0.62*order+0.38*source)


def _source_pull(child,best,rng,prob):
    for d in range(len(child.src)):
        if rng.random()<prob:
            child.src[d]=best.src[d]


def _prey_exploit(p,cur,best,rng,progress):
    child=cur.clone(); mismatch=_mismatch(cur,best)
    # "Jump" becomes a partial precedence/source alignment toward the best prey.
    # Smaller mismatch => a finer jump; later search becomes more exploitative.
    frac=min(0.72,max(1/len(child.order),0.12+0.30*progress+0.34*mismatch*rng.random()))
    align(child,best,rng,frac)
    _source_pull(child,best,rng,0.18+0.38*progress)
    # Local hunting around the estimated prey location.
    if rng.random()<0.58: joint_move(p,child,rng)
    elif rng.random()<0.55: insert(child,rng)
    else: change_source(p,child,rng,1)
    return child


def _fox_explore(p,cur,best,pop,rng,progress,diversity):
    mismatch=_mismatch(cur,best)
    # Controlled random walk: combine information from another fox, then make a
    # long discrete jump.  Larger leaps are more likely early or under low diversity.
    peer=rng.choice(pop)
    child=cross(cur,peer,rng) if rng.random()<0.55 else cur.clone()
    leap_strength=min(1.0,0.35+0.45*(1-progress)+0.35*(0.12-diversity)/0.12+0.25*mismatch)
    n_ops=1 + int(rng.random()<leap_strength) + int(rng.random()<0.35*leap_strength)
    long_ops=['block','reverse','insert','joint','source']
    for _ in range(n_ops):
        op_apply(p,child,rng,rng.choice(long_ops))
    if rng.random()<0.50+0.25*leap_strength:
        change_source(p,child,rng,1+int(rng.random()<0.45))
    # A weak prey cue keeps exploration from becoming unstructured random restart.
    if rng.random()<0.25:
        align(child,best,rng,0.08+0.12*rng.random())
    return child


def run_dfox_apns(p, seed:int, budget:int, npop:int=12) -> RR:
    rng=random.Random(seed); ev=0; trace=[]; pop=[]
    for _ in range(min(npop,budget)):
        s=random_sol(p,rng); evaluate(p,s); ev+=1; pop.append(s)
    best=min(pop,key=lambda s:s.score).clone(); trace.append((ev,best.score))
    stagn=0
    while ev<budget:
        progress=ev/budget
        div=pop_diversity(pop)
        scores=[s.score for s in pop]; lo=min(scores); hi=max(scores); span=max(1e-9,hi-lo)
        improved_global=False; new=[]
        for cur in pop:
            if ev>=budget: break
            # Poor agents explore more; good agents hunt near the prey. Early search
            # explores more, and low diversity triggers additional exploration.
            rel=(cur.score-lo)/span
            p_explore=0.10 + 0.54*(1-progress) + 0.24*rel
            if div<0.10: p_explore += min(0.18,(0.10-div)*1.8)
            p_explore=max(0.08,min(0.88,p_explore))
            if rng.random()<p_explore:
                cand=_fox_explore(p,cur,best,pop,rng,progress,div)
            else:
                cand=_prey_exploit(p,cur,best,rng,progress)
            evaluate(p,cand); ev+=1
            chosen=cand
            # Adaptive prey-neighborhood search: spend extra evaluations only on
            # competitive candidates or during late exploitation.
            if ev<budget and (cand.score <= cur.score*1.06 or progress>0.67):
                ops=['joint','insert','source','reverse'] if progress<0.75 else ['joint','insert','source','swap']
                refined,used=local_best_of(p,cand,rng,ops,budget-ev,tries=2 if progress<0.75 else 3)
                ev+=used
                if refined.score<chosen.score: chosen=refined
            # Greedy survival with a small diversity-preserving exception for poor agents.
            if chosen.score<cur.score:
                survivor=chosen
            elif rng.random() < 0.05*(1-progress)*rel:
                survivor=chosen
            else:
                survivor=cur.clone()
            new.append(survivor)
            if survivor.score<best.score:
                best=survivor.clone(); trace.append((ev,best.score)); improved_global=True
        if new: pop=new
        stagn=0 if improved_global else stagn+1
        # Elite preservation.
        if pop:
            wi=max(range(len(pop)),key=lambda i:pop[i].score)
            if best.score<pop[wi].score: pop[wi]=best.clone()
        # Stagnation-triggered FOX long jump. The worst foxes are relocated around
        # distant discrete regions while keeping a small prey cue.
        if ev<budget and (stagn>=3 or div<0.075):
            count=max(1,len(pop)//5)
            worst=sorted(range(len(pop)),key=lambda i:pop[i].score,reverse=True)[:count]
            for wi in worst:
                if ev>=budget: break
                z=pop[wi].clone()
                block_reloc(z,rng)
                if rng.random()<0.7: reverse(z,rng)
                change_source(p,z,rng,2)
                if rng.random()<0.35: align(z,best,rng,0.08+0.10*rng.random())
                evaluate(p,z); ev+=1
                pop[wi]=z
                if z.score<best.score:
                    best=z.clone(); trace.append((ev,best.score)); stagn=0
    return RR('DFOX-APNS',p.name,p.family,seed,best.score,ev,trace)

optimize=run_dfox_apns
