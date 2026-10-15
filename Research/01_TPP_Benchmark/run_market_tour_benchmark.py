"""Official TPPLIB market-tour runner with exact objective-evaluation accounting.

Input must be genuine TPPLIB `.tpp` files.  Three market-tour solvers are compared:
problem-aware ILS, VNS, and a FOX transfer using prey-guided market-set/order alignment.
All objective calls, including local pruning/intensification, are counted against the
same FE budget.  When a Class-3 external reference is available, true OPT/BKS gap is
reported together with travel/purchase decomposition and visited-market count.
"""
from __future__ import annotations
import argparse,csv,statistics,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
for x in (HERE,ROOT):
    if str(x) not in sys.path:sys.path.insert(0,str(x))
from tpplib_parser import parse_tpplib
from tpplib_bks import lookup,gap_percent
from market_tour_solvers import run_ils,run_vns,run_dfox


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',required=True,help='Genuine TPPLIB .tpp file or directory')
    ap.add_argument('--seeds',type=int,default=10);ap.add_argument('--budget',type=int,default=5000)
    ap.add_argument('--output',default=str(ROOT/'Research/results/tpplib_market_tour_runs.csv'));args=ap.parse_args()
    src=Path(args.input);files=[src] if src.is_file() else sorted(src.rglob('*.tpp'))
    if not files:raise SystemExit(f'No .tpp files found under {src}')
    rows=[]
    for fi,path in enumerate(files,1):
        raw=parse_tpplib(path);p=raw.to_market_tour_problem();ref=lookup(raw.name)
        print(f'[{fi}/{len(files)}] {raw.name} markets={p.n_markets} products={p.n_products} ref={ref.value if ref else "n/a"}',flush=True)
        for s in range(args.seeds):
            seed=17011+10007*s
            for fn in (run_ils,run_vns,run_dfox):
                r=fn(p,seed,args.budget)
                rows.append({'algorithm':r.algorithm,'instance':raw.name,'seed':seed,'score':r.score,'travel':r.travel,'purchase':r.purchase,
                             'visited_markets':r.visited_markets,'evaluations':r.evaluations,'seconds':r.seconds,
                             'reference_value':ref.value if ref else '','reference_status':ref.status if ref else '',
                             'opt_gap_pct':gap_percent(r.score,ref) if ref else ''})
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary=[]
    for a in sorted({r['algorithm'] for r in rows}):
        q=[r for r in rows if r['algorithm']==a];g=[float(r['opt_gap_pct']) for r in q if r['opt_gap_pct']!='']
        summary.append({'algorithm':a,'runs':len(q),'median_score':statistics.median(float(r['score']) for r in q),'median_opt_gap_pct':statistics.median(g) if g else '',
                        'median_travel':statistics.median(float(r['travel']) for r in q),'median_purchase':statistics.median(float(r['purchase']) for r in q),
                        'median_visited_markets':statistics.median(int(r['visited_markets']) for r in q),'mean_seconds':statistics.mean(float(r['seconds']) for r in q)})
    sout=out.with_name('tpplib_market_tour_summary.csv')
    with sout.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    print('wrote',out);print('wrote',sout)
if __name__=='__main__':main()
