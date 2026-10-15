"""Equal-FE solvers for classical unit-demand TPP market-tour representation.

All objective calls go through ``BudgetedEvaluator`` so local pruning, repair and
intensification cannot silently exceed the declared evaluation budget.  This module
contains problem-aware ILS/VNS and a FOX transfer operating on variable-length
market tours.  It is intended for representation/mechanism studies, not to claim a
new state-of-the-art TPP solver.
"""
from __future__ import annotations
from dataclasses import dataclass
import math, random, time
from typing import List

from market_tour import TPPProblem, MarketTourSol, evaluate, greedy_cover, apply_operator, OPERATORS


@dataclass
class DetailedRun:
    algorithm: str
    score: float
    travel: float
    purchase: float
    visited_markets: int
    evaluations: int
    seconds: float
    best: MarketTourSol
    trace: list[tuple[int,float]]


class BudgetedEvaluator:
    def __init__(self, p:TPPProblem, budget:int):
        self.p=p; self.budget=int(budget); self.used=0
    @property
    def remaining(self): return self.budget-self.used
    def eval(self,s:MarketTourSol)->float:
        if self.used>=self.budget:
            raise RuntimeError('objective evaluation budget exhausted')
        self.used+=1
        return evaluate(self.p,s)


def _missing_products(p:TPPProblem,tour)->set[int]:
    v=set(tour); miss=set()
    for k,offers in enumerate(p.offers_by_product):
        if not any(m in v for m,_ in offers): miss.add(k)
    return miss


def repair_cover(p:TPPProblem,s:MarketTourSol,rng:random.Random)->None:
    """Feasibility repair without objective calls: add markets with high uncovered coverage."""
    miss=_missing_products(p,s.tour)
    selected=set(s.tour)
    while miss:
        cand=[]
        for m in range(p.n_markets):
            if m in selected: continue
            rows=[]
            for k in miss:
                prices=[pr for mm,pr in p.offers_by_product[k] if mm==m]
                if prices: rows.append((k,min(prices)))
            if rows:
                proxy=(sum(pr for _,pr in rows)+0.15*(p.distance[p.depot_index][m]+p.distance[m][p.depot_index]))/len(rows)
                cand.append((proxy*(1+rng.uniform(-0.01,0.01)),m,{k for k,_ in rows}))
        if not cand: return
        _,m,covers=min(cand)
        pos=rng.randrange(len(s.tour)+1)
        s.tour.insert(pos,m); selected.add(m); miss-=covers


def _greedy_seed(p:TPPProblem,rng:random.Random,ev:BudgetedEvaluator)->MarketTourSol:
    # greedy_cover evaluates once internally; account for exactly that call.
    if ev.remaining<=0: raise RuntimeError('no budget for initialization')
    s=greedy_cover(p,rng); ev.used+=1
    return s


def _prune(p,s,rng,ev:BudgetedEvaluator,max_passes=2):
    cur=s.clone()
    for _ in range(max_passes):
        improved=False
        idx=list(range(len(cur.tour))); rng.shuffle(idx)
        for i in idx:
            if ev.remaining<=0 or len(cur.tour)<=1: break
            cand=MarketTourSol(cur.tour[:i]+cur.tour[i+1:])
            repair_cover(p,cand,rng)
            ev.eval(cand)
            if cand.score<cur.score-1e-12:
                cur=cand; improved=True; break
        if not improved: break
    return cur


def _sample_neighbor(p,base,rng,ev,op):
    z=base.clone(); apply_operator(p,z,rng,op); repair_cover(p,z,rng); ev.eval(z); return z


def run_ils(p:TPPProblem,seed:int,budget:int)->DetailedRun:
    rng=random.Random(seed); t0=time.perf_counter(); ev=BudgetedEvaluator(p,budget)
    cur=_greedy_seed(p,rng,ev); cur=_prune(p,cur,rng,ev); best=cur.clone(); trace=[(ev.used,best.score)]; stagn=0
    while ev.remaining>0:
        local=cur.clone(); improved=True
        while improved and ev.remaining>0:
            improved=False; ops=list(OPERATORS); rng.shuffle(ops)
            for op in ops:
                for _ in range(min(4,ev.remaining)):
                    z=_sample_neighbor(p,local,rng,ev,op)
                    if z.score<local.score-1e-12:
                        local=z; improved=True; break
                if improved or ev.remaining<=0: break
        if local.score<best.score:
            best=local.clone(); trace.append((ev.used,best.score)); stagn=0
        else: stagn+=1
        cur=local.clone()
        # problem-aware perturbation with increasing strength
        strength=min(4,1+stagn//2)
        for j in range(strength):
            if ev.remaining<=0: break
            op='swap_market' if j==0 else rng.choice(OPERATORS)
            z=_sample_neighbor(p,cur,rng,ev,op)
            delta=z.score-cur.score
            temp=max(1e-9,0.01*best.score*(1-ev.used/max(1,budget))+1e-9)
            if delta<=0 or rng.random()<math.exp(-max(0,delta)/temp): cur=z
            if z.score<best.score:
                best=z.clone();trace.append((ev.used,best.score));stagn=0
        if stagn>=7 and ev.remaining>0:
            cur=_greedy_seed(p,rng,ev);stagn=0
    return DetailedRun('TPP-ILS',best.score,best.travel,best.purchase,len(best.tour),ev.used,time.perf_counter()-t0,best,trace)


def run_vns(p:TPPProblem,seed:int,budget:int)->DetailedRun:
    rng=random.Random(seed); t0=time.perf_counter(); ev=BudgetedEvaluator(p,budget)
    cur=_greedy_seed(p,rng,ev);cur=_prune(p,cur,rng,ev);best=cur.clone();trace=[(ev.used,best.score)]
    ops=list(OPERATORS);k=0
    while ev.remaining>0:
        op=ops[k%len(ops)];cand=cur.clone();
        for _ in range(1+int(k>=len(ops))): apply_operator(p,cand,rng,op)
        repair_cover(p,cand,rng);ev.eval(cand)
        # bounded local intensification
        for _ in range(min(5,ev.remaining)):
            z=_sample_neighbor(p,cand,rng,ev,rng.choice(('two_opt','relocate','drop','swap_market')))
            if z.score<cand.score: cand=z
        if cand.score<cur.score:
            cur=cand;k=0
            if cur.score<best.score:
                best=cur.clone();trace.append((ev.used,best.score))
        else:k=(k+1)%(len(ops)*2)
    return DetailedRun('TPP-VNS',best.score,best.travel,best.purchase,len(best.tour),ev.used,time.perf_counter()-t0,best,trace)


def _tour_set_distance(a,b):
    A,B=set(a.tour),set(b.tour); union=len(A|B)
    setd=1-(len(A&B)/max(1,union))
    common=A&B
    if len(common)<2:return setd
    pa={m:i for i,m in enumerate(a.tour)};pb={m:i for i,m in enumerate(b.tour)}
    ord_d=sum(abs(pa[m]/max(1,len(a.tour)-1)-pb[m]/max(1,len(b.tour)-1)) for m in common)/len(common)
    return min(1.0,0.65*setd+0.35*ord_d)


def _prey_pull(p,cur,best,rng,progress):
    z=cur.clone(); A=set(z.tour); B=set(best.tour)
    # set alignment: add prey markets, remove non-prey markets only through feasibility repair
    missing=list(B-A); extra=list(A-B)
    if missing and rng.random()<0.75:
        m=rng.choice(missing); z.tour.insert(rng.randrange(len(z.tour)+1),m)
    if extra and len(z.tour)>1 and rng.random()<0.45+0.25*progress:
        z.tour.remove(rng.choice(extra))
    # order alignment on a shared market
    shared=[m for m in z.tour if m in B]
    if shared and rng.random()<0.8:
        m=rng.choice(shared); z.tour.remove(m)
        target=best.tour.index(m)/max(1,len(best.tour)-1)
        pos=min(len(z.tour),round(target*len(z.tour)));z.tour.insert(pos,m)
    if rng.random()<0.65: apply_operator(p,z,rng,rng.choice(('two_opt','relocate','swap_market')))
    repair_cover(p,z,rng);return z


def _fox_jump(p,cur,rng,progress):
    z=cur.clone(); strength=1+int(rng.random()<0.65*(1-progress))+int(rng.random()<0.25)
    for _ in range(strength): apply_operator(p,z,rng,rng.choice(OPERATORS))
    repair_cover(p,z,rng);return z


def run_dfox(p:TPPProblem,seed:int,budget:int,npop:int=10)->DetailedRun:
    """FOX transfer on market tours: prey-guided set/order alignment + long discrete jumps."""
    rng=random.Random(seed);t0=time.perf_counter();ev=BudgetedEvaluator(p,budget);pop=[]
    while len(pop)<npop and ev.remaining>0:
        s=_greedy_seed(p,rng,ev)
        # diversify seeds without hiding objective calls
        if len(pop)>0 and ev.remaining>0:
            for _ in range(rng.randint(1,3)): apply_operator(p,s,rng,rng.choice(OPERATORS))
            repair_cover(p,s,rng);ev.eval(s)
        pop.append(s)
    best=min(pop,key=lambda x:x.score).clone();trace=[(ev.used,best.score)];stagn=0
    while ev.remaining>0:
        progress=ev.used/max(1,budget);new=[];improved=False
        scores=[s.score for s in pop];lo=min(scores);hi=max(scores);span=max(1e-9,hi-lo)
        for cur in pop:
            if ev.remaining<=0:break
            rel=(cur.score-lo)/span; mismatch=_tour_set_distance(cur,best)
            pexplore=min(.88,max(.08,.12+.50*(1-progress)+.20*rel+.15*mismatch))
            cand=_fox_jump(p,cur,rng,progress) if rng.random()<pexplore else _prey_pull(p,cur,best,rng,progress)
            ev.eval(cand)
            # prey-neighborhood intensification
            if ev.remaining>0 and (cand.score<=cur.score*1.05 or progress>.65):
                tries=2 if progress<.7 else 3
                local=cand
                for _ in range(min(tries,ev.remaining)):
                    z=_sample_neighbor(p,local,rng,ev,rng.choice(('two_opt','relocate','drop','swap_market')))
                    if z.score<local.score:local=z
                cand=local
            surv=cand if cand.score<cur.score or rng.random()<0.025*(1-progress)*rel else cur.clone()
            new.append(surv)
            if surv.score<best.score:
                best=surv.clone();trace.append((ev.used,best.score));improved=True
        if new:pop=new
        stagn=0 if improved else stagn+1
        if stagn>=4 and ev.remaining>0:
            # explicit long jump of worst foxes
            for wi in sorted(range(len(pop)),key=lambda i:pop[i].score,reverse=True)[:max(1,len(pop)//5)]:
                if ev.remaining<=0:break
                z=_fox_jump(p,pop[wi],rng,0.0);apply_operator(p,z,rng,'add');repair_cover(p,z,rng);ev.eval(z);pop[wi]=z
                if z.score<best.score:best=z.clone();trace.append((ev.used,best.score));stagn=0
    return DetailedRun('TPP-DFOX',best.score,best.travel,best.purchase,len(best.tour),ev.used,time.perf_counter()-t0,best,trace)
