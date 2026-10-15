"""Controlled representation study on TPP-style or genuine TPPLIB instances.

Compares the same three search families under two genotypes:
  C = commodity permutation + source assignment (legacy PANCAKE)
  M = market subset/tour + induced cheapest feasible procurement (classical TPP)

The purpose is to test representation effects, not merely algorithm ranking.
"""
from __future__ import annotations
import argparse,csv,json,math,statistics,sys,time
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RB=ROOT/'ResearchBenchmark'
for p in (str(HERE),str(ROOT),str(RB)):
    if p not in sys.path:sys.path.insert(0,p)

from market_tour import TPPProblem
from market_tour_solvers import run_ils as run_m_ils, run_vns as run_m_vns, run_dfox as run_m_dfox
from tpplib_parser import parse_tpplib
from tpplib_bks import lookup,gap_percent
from ResearchBenchmark.meta_study import Problem
from ResearchBenchmark.algorithms.ils_vns import run_ils as run_c_ils, run_vns as run_c_vns
from ResearchBenchmark.algorithms.dfox_apns import run_dfox_apns as run_c_dfox


def load_protocol_json(path:Path):
    d=json.loads(path.read_text())
    m=int(d['markets']); products=int(d['products']); dist=d['distance_matrix']
    legacy=Problem(d['name'],d.get('family','tpp_style'),[tuple(x) for x in d['coords']],
                   [[(int(a),float(b)) for a,b in rows] for rows in d['candidates']],1.0,True,dist,m)
    offers=[[(int(a),float(b)) for a,b in rows] for rows in d['candidates']]
    market=TPPProblem(d['name'],list(range(m)),list(range(products)),dist,m,offers,d.get('family','tpp_style'))
    return legacy,market,None


def load_official(path:Path):
    raw=parse_tpplib(path);return raw.to_pancake_problem(),raw.to_market_tour_problem(),lookup(raw.name)


def commodity_metrics(best):
    nodes=[]
    for item in best.order:
        nodes.append(best._problem.candidates[item][best.src[item]][0] if hasattr(best,'_problem') else None)
    return nodes


def run_one(legacy,market,ref,seed,budget):
    rows=[]
    for name,fn in [('C-ILS',run_c_ils),('C-VNS',run_c_vns),('C-DFOX',run_c_dfox)]:
        t0=time.perf_counter();rr,best=fn(legacy,seed,budget,return_best=True);sec=time.perf_counter()-t0
        nodes=[legacy.candidates[item][best.src[item]][0] for item in best.order]
        unique=len(set(nodes)); repeats=len(nodes)-unique
        rows.append(dict(algorithm=name,representation='commodity',seed=seed,score=best.score,travel=best.dist,
                         purchase=best.purchase,visited_markets=unique,route_market_repeats=repeats,
                         evaluations=rr.evals,seconds=sec,reference_value=ref.value if ref else '',
                         reference_status=ref.status if ref else '',opt_gap_pct=gap_percent(best.score,ref) if ref else ''))
    for name,fn in [('M-ILS',run_m_ils),('M-VNS',run_m_vns),('M-DFOX',run_m_dfox)]:
        r=fn(market,seed,budget)
        rows.append(dict(algorithm=name,representation='market_tour',seed=seed,score=r.score,travel=r.travel,
                         purchase=r.purchase,visited_markets=r.visited_markets,route_market_repeats=0,
                         evaluations=r.evaluations,seconds=r.seconds,reference_value=ref.value if ref else '',
                         reference_status=ref.status if ref else '',opt_gap_pct=gap_percent(r.score,ref) if ref else ''))
    return rows


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',default=str(HERE/'instances'))
    ap.add_argument('--seeds',type=int,default=5);ap.add_argument('--budget',type=int,default=2400)
    ap.add_argument('--official',action='store_true');ap.add_argument('--output',default=str(ROOT/'Research/results/representation_runs.csv'))
    args=ap.parse_args();src=Path(args.input)
    pats='*.tpp' if args.official else 'eeuclideo_style_*.json'
    files=[src] if src.is_file() else sorted(src.rglob(pats))
    if not files:raise SystemExit(f'No {pats} under {src}')
    rows=[]
    for fi,path in enumerate(files,1):
        legacy,market,ref=load_official(path) if args.official else load_protocol_json(path)
        print(f'[{fi}/{len(files)}] {legacy.name}: markets={market.n_markets} products={market.n_products}',flush=True)
        for s in range(args.seeds):
            seed=36011+10007*s
            for r in run_one(legacy,market,ref,seed,args.budget):
                r['instance']=legacy.name;r['markets']=market.n_markets;r['products']=market.n_products;rows.append(r)
    # per-instance pooled BKS for nonofficial stress tests
    if not args.official:
        best={i:min(float(r['score']) for r in rows if r['instance']==i) for i in {r['instance'] for r in rows}}
        for r in rows:r['pooled_rpd_pct']=100*(float(r['score'])-best[r['instance']])/best[r['instance']]
    else:
        for r in rows:r['pooled_rpd_pct']=''
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    fields=list(rows[0]);
    with out.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    # compact summary
    algs=sorted({r['algorithm'] for r in rows});summary=[]
    for a in algs:
        q=[r for r in rows if r['algorithm']==a]
        gaps=[float(r['opt_gap_pct']) for r in q if r['opt_gap_pct']!='']
        rpds=[float(r['pooled_rpd_pct']) for r in q if r['pooled_rpd_pct']!='']
        summary.append(dict(algorithm=a,representation=q[0]['representation'],runs=len(q),median_score=statistics.median(float(x['score']) for x in q),
                            median_pooled_rpd_pct=statistics.median(rpds) if rpds else '',median_opt_gap_pct=statistics.median(gaps) if gaps else '',
                            median_travel=statistics.median(float(x['travel']) for x in q),median_purchase=statistics.median(float(x['purchase']) for x in q),
                            median_visited=statistics.median(int(x['visited_markets']) for x in q),median_repeats=statistics.median(int(x['route_market_repeats']) for x in q),
                            mean_seconds=statistics.mean(float(x['seconds']) for x in q)))
    sout=out.with_name('representation_summary.csv')
    with sout.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    print('wrote',out);print('wrote',sout)

if __name__=='__main__':main()
