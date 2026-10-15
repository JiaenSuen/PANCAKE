"""Controlled DFOX component ablation and operator telemetry.

A0: fixed exploration/exploitation + generic permutation operators.
A1: A0 + problem-aware source/joint operators.
A2: A1 + adaptive phase control and adaptive operator selection (AOS).
A3: A2 + stagnation/diversity-triggered restart (controlled APNS branch).

All variants share the same code path and objective-evaluation budget, making the
incremental evidence more interpretable than comparing independently written solvers.
"""
from __future__ import annotations

import random
from collections import defaultdict
from .core import RR, align, change_source, cross, evaluate, op_apply, pop_diversity, random_sol


def _mismatch(a,b):
    n=len(a.order);pos={d:i for i,d in enumerate(b.order)}
    order=sum(abs(i-pos[d]) for i,d in enumerate(a.order))/max(1,n*n)
    src=sum(int(a.src[i]!=b.src[i]) for i in range(n))/max(1,n)
    return min(1.0,.62*order+.38*src)


def _weighted_choice(rng, ops, weights):
    vals=[max(1e-6,weights[o]) for o in ops];total=sum(vals);r=rng.random()*total;acc=0.0
    for o,w in zip(ops,vals):
        acc+=w
        if acc>=r:return o
    return ops[-1]


def _telemetry_init():
    return {
        'operator': defaultdict(lambda:{'calls':0,'success':0,'total_improvement':0.0,'early':0,'mid':0,'late':0}),
        'phase': {'explore':0,'exploit':0,'restart':0},
    }


def _log_op(tel,op,progress,before,after):
    if tel is None:return
    d=tel['operator'][op];d['calls']+=1
    bucket='early' if progress<1/3 else ('mid' if progress<2/3 else 'late');d[bucket]+=1
    if after<before:
        d['success']+=1;d['total_improvement']+=before-after


def _update_weight(weights,op,before,after):
    if after<before:
        reward=1.0+min(4.0,100.0*(before-after)/max(1e-9,before))
        weights[op]=.82*weights[op]+.18*reward
    else:
        weights[op]=.98*weights[op]+.02*.25


def run_dfox_ablation(p, seed:int, budget:int, level:int=3, npop:int=12, telemetry=None) -> RR:
    assert level in (0,1,2,3)
    rng=random.Random(seed);ev=0;trace=[];pop=[]
    tel=telemetry if telemetry is not None else None
    if tel is not None:
        tel.clear();tel.update(_telemetry_init())
    for _ in range(min(npop,budget)):
        s=random_sol(p,rng);evaluate(p,s);ev+=1;pop.append(s)
    best=min(pop,key=lambda s:s.score).clone();trace.append((ev,best.score));stagn=0
    generic=['swap','reverse','insert','block']
    aware=generic+['source','joint']
    weights={o:1.0 for o in aware}

    while ev<budget:
        progress=ev/budget;div=pop_diversity(pop);scores=[x.score for x in pop];lo=min(scores);hi=max(scores);span=max(1e-9,hi-lo)
        improved_global=False;new=[]
        for cur in pop:
            if ev>=budget:break
            rel=(cur.score-lo)/span
            if level>=2:
                p_explore=.10+.54*(1-progress)+.24*rel
                if div<.10:p_explore+=min(.18,(.10-div)*1.8)
                p_explore=max(.08,min(.88,p_explore))
            else:p_explore=.50
            child=cur.clone();before=cur.score
            ops=aware if level>=1 else generic
            op=_weighted_choice(rng,ops,weights) if level>=2 else rng.choice(ops)
            if rng.random()<p_explore:
                if tel is not None:tel['phase']['explore']+=1
                # Information-preserving exploration: peer recombination only in stronger variants.
                if level>=1 and rng.random()<.45:
                    child=cross(cur,rng.choice(pop),rng)
                op_apply(p,child,rng,op)
                if level>=1 and rng.random()<.28:
                    change_source(p,child,rng,1)
            else:
                if tel is not None:tel['phase']['exploit']+=1
                mismatch=_mismatch(cur,best)
                frac=max(1/len(child.order),min(.65,.08+.32*progress+.28*mismatch*rng.random()))
                align(child,best,rng,frac)
                op_apply(p,child,rng,op)
            evaluate(p,child);ev+=1
            _log_op(tel,op,progress,before,child.score)
            if level>=2:_update_weight(weights,op,before,child.score)

            chosen=child
            # Equal-budget local refinement exists at every level; only the operator set changes.
            if ev<budget and child.score<=cur.score*1.05:
                op2=_weighted_choice(rng,ops,weights) if level>=2 else rng.choice(ops)
                z=child.clone();z_before=z.score;op_apply(p,z,rng,op2);evaluate(p,z);ev+=1
                _log_op(tel,op2,progress,z_before,z.score)
                if level>=2:_update_weight(weights,op2,z_before,z.score)
                if z.score<chosen.score:chosen=z
            survivor=chosen if chosen.score<cur.score else cur.clone();new.append(survivor)
            if survivor.score<best.score:
                best=survivor.clone();trace.append((ev,best.score));improved_global=True
        if new:pop=new
        stagn=0 if improved_global else stagn+1
        if pop:
            wi=max(range(len(pop)),key=lambda i:pop[i].score)
            if best.score<pop[wi].score:pop[wi]=best.clone()

        if level>=3 and ev<budget and (stagn>=3 or div<.075):
            if tel is not None:tel['phase']['restart']+=1
            worst=sorted(range(len(pop)),key=lambda i:pop[i].score,reverse=True)[:max(1,len(pop)//5)]
            for wi in worst:
                if ev>=budget:break
                z=best.clone();before=z.score
                for op3 in ('block', rng.choice(['joint','source','reverse','insert'])):
                    op_apply(p,z,rng,op3)
                evaluate(p,z);ev+=1;_log_op(tel,'restart_jump',progress,before,z.score)
                pop[wi]=z
                if z.score<best.score:
                    best=z.clone();trace.append((ev,best.score));stagn=0
    names={0:'DFOX-A0-Generic',1:'DFOX-A1-ProblemAware',2:'DFOX-A2-Adaptive',3:'DFOX-A3-Full'}
    if tel is not None:
        tel['weights_final']={k:float(v) for k,v in weights.items()}
        # Convert defaultdict to ordinary dict for JSON serialization.
        tel['operator']={k:dict(v) for k,v in tel['operator'].items()}
    return RR(names[level],p.name,p.family,seed,best.score,ev,trace)


def run_dfox_a0(p,seed,budget):return run_dfox_ablation(p,seed,budget,0)
def run_dfox_a1(p,seed,budget):return run_dfox_ablation(p,seed,budget,1)
def run_dfox_a2(p,seed,budget):return run_dfox_ablation(p,seed,budget,2)
def run_dfox_a3(p,seed,budget):return run_dfox_ablation(p,seed,budget,3)

__all__=['run_dfox_ablation','run_dfox_a0','run_dfox_a1','run_dfox_a2','run_dfox_a3']
