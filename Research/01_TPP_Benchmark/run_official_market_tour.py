"""Run strict-FE market-tour solvers on genuine TPPLIB instances.

This runner is intentionally small and paper-oriented. It reports purchase/travel
components, visited-market count, runtime, and OPT/BKS gap when a reference is known.
"""
from __future__ import annotations

import argparse, csv, statistics
from pathlib import Path
from scipy.stats import wilcoxon

from tpplib_parser import parse_tpplib
from tpplib_bks import lookup, gap_percent
from market_tour_solvers import run_ils, run_vns, run_dfox

METHODS = {
    "ILS": run_ils,
    "VNS": run_vns,
    "DFOX": run_dfox,
}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("instance")
    ap.add_argument("--seeds",type=int,default=10)
    ap.add_argument("--budget",type=int,default=1200)
    ap.add_argument("--methods",default="ILS,VNS,DFOX")
    ap.add_argument("--out",default=None)
    args=ap.parse_args()

    inst=parse_tpplib(args.instance)
    p=inst.to_market_tour_problem()
    ref=lookup(inst.name)
    methods=[m.strip().upper() for m in args.methods.split(',') if m.strip()]
    unknown=[m for m in methods if m not in METHODS]
    if unknown: raise SystemExit(f"Unknown methods: {unknown}")

    outdir=Path(args.out) if args.out else Path(__file__).resolve().parents[1]/"results"
    outdir.mkdir(parents=True,exist_ok=True)
    slug=inst.name.replace('.','_')
    rows=[]
    for si in range(args.seeds):
        seed=377+10007*si
        for m in methods:
            r=METHODS[m](p,seed,args.budget)
            rows.append({
                'instance':inst.name,'seed':seed,'algorithm':f'TPP-{m}',
                'score':r.score,
                'reference_value':ref.value if ref else '',
                'reference_status':ref.status if ref else '',
                'gap_reference_pct':gap_percent(r.score,ref) if ref else '',
                'travel':r.travel,'purchase':r.purchase,
                'visited_markets':r.visited_markets,
                'evaluations':r.evaluations,'seconds':r.seconds,
            })
            print(inst.name,si,m,r.score,flush=True)

    run_path=outdir/f'tpplib_{slug}_runs.csv'
    with run_path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)

    summary=[]
    for m in methods:
        a=f'TPP-{m}'; rr=[x for x in rows if x['algorithm']==a]
        scores=[float(x['score']) for x in rr]
        summary.append({
            'algorithm':a,'runs':len(rr),'median_score':statistics.median(scores),
            'mean_score':statistics.mean(scores),'best_score':min(scores),
            'median_gap_reference_pct':statistics.median(float(x['gap_reference_pct']) for x in rr) if ref else '',
            'best_gap_reference_pct':min(float(x['gap_reference_pct']) for x in rr) if ref else '',
            'median_travel':statistics.median(float(x['travel']) for x in rr),
            'median_purchase':statistics.median(float(x['purchase']) for x in rr),
            'median_visited_markets':statistics.median(int(x['visited_markets']) for x in rr),
            'median_seconds':statistics.median(float(x['seconds']) for x in rr),
            'reference_status':ref.status if ref else '',
            'reference_value':ref.value if ref else '',
        })
    summary_path=outdir/f'tpplib_{slug}_summary.csv'
    with summary_path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=summary[0].keys()); w.writeheader(); w.writerows(summary)

    if len(methods)>=2:
        pairs=[]
        for i in range(len(methods)):
            for j in range(i+1,len(methods)):
                a,b=f'TPP-{methods[i]}',f'TPP-{methods[j]}'
                xa=[float(x['score']) for x in rows if x['algorithm']==a]
                xb=[float(x['score']) for x in rows if x['algorithm']==b]
                stat,pv=wilcoxon(xa,xb,alternative='two-sided')
                pairs.append({'method_a':a,'method_b':b,'wilcoxon_stat':stat,'p_value':pv,
                              'wins_a':sum(x<y for x,y in zip(xa,xb)),
                              'ties':sum(x==y for x,y in zip(xa,xb)),
                              'losses_a':sum(x>y for x,y in zip(xa,xb))})
        order=sorted(range(len(pairs)),key=lambda k:pairs[k]['p_value']); running=0.0; n=len(pairs)
        for rank,k in enumerate(order):
            running=max(running,(n-rank)*pairs[k]['p_value']); pairs[k]['holm_p']=min(1.0,running)
            pairs[k]['significant_0.05']=pairs[k]['holm_p']<.05
        pair_path=outdir/f'tpplib_{slug}_pairwise_holm.csv'
        with pair_path.open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=pairs[0].keys()); w.writeheader(); w.writerows(pairs)

    print(f'Wrote {run_path}')
    print(f'Wrote {summary_path}')

if __name__=='__main__':
    main()
