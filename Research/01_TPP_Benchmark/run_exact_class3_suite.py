"""Run a compact exact-OPT EEuclideo Class-3 suite without importing external solver code.

The default suite uses four small/medium (markets, products) combinations:
50x50, 50x100, 100x50, 100x100; each has five TPPLIB instances.
Only PANCAKE's parser/solvers are used. Reference OPT/M* values are read from the
locally extracted Baseline_EEuclideo.csv and cross-checkable with class3_reference_values.csv.
"""
from __future__ import annotations
import argparse, csv, statistics, time
from collections import defaultdict
from pathlib import Path
from scipy.stats import friedmanchisquare, wilcoxon
from tpplib_parser import parse_tpplib
from market_tour_solvers import run_ils, run_vns, run_dfox

METHODS={"ILS":run_ils,"VNS":run_vns,"DFOX":run_dfox}
DEFAULT_SIZES={(50,50),(50,100),(100,50),(100,100)}

def load_baseline(path:Path):
    out={}
    with path.open(encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f):
            out[r['Instance']]={'V':int(r['V']),'K':int(r['K']),'M*':int(r['M*']),'OPT':float(r['OPT']),'Sec':float(r['Sec'])}
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--instance-dir',default=str(Path(__file__).parent/'official_data'/'EEuclideo'))
    ap.add_argument('--baseline',default=None)
    ap.add_argument('--seeds',type=int,default=3)
    ap.add_argument('--budget',type=int,default=1200)
    ap.add_argument('--methods',default='ILS,VNS,DFOX')
    ap.add_argument('--sizes',default='50x50,50x100,100x50,100x100')
    ap.add_argument('--out',default=str(Path(__file__).resolve().parents[1]/'results'/'class3_exact_suite'))
    args=ap.parse_args()
    idir=Path(args.instance_dir); baseline=Path(args.baseline) if args.baseline else idir/'Baseline_EEuclideo.csv'
    refs=load_baseline(baseline)
    sizes=set()
    for s in args.sizes.split(','):
        a,b=s.lower().split('x'); sizes.add((int(a),int(b)))
    methods=[m.strip().upper() for m in args.methods.split(',') if m.strip()]
    outdir=Path(args.out); outdir.mkdir(parents=True,exist_ok=True)

    targets=[]
    for name,meta in refs.items():
        if (meta['V'],meta['K']) in sizes:
            p=idir/f'{name}.tpp'
            if not p.exists(): raise FileNotFoundError(p)
            targets.append((name,p,meta))
    targets.sort(key=lambda x:(x[2]['V'],x[2]['K'],x[0]))

    rows=[]; started=time.time()
    for idx,(name,path,meta) in enumerate(targets,1):
        inst=parse_tpplib(path); prob=inst.to_market_tour_problem()
        for si in range(args.seeds):
            seed=377+10007*si
            for m in methods:
                r=METHODS[m](prob,seed,args.budget)
                gap=100*(r.score-meta['OPT'])/meta['OPT']
                rows.append({'instance':name,'markets':meta['V'],'products':meta['K'],'sample':name.split('.')[-1],
                             'seed':seed,'algorithm':f'TPP-{m}','score':r.score,'OPT':meta['OPT'],'gap_opt_pct':gap,
                             'travel':r.travel,'purchase':r.purchase,'visited_markets':r.visited_markets,'M_star':meta['M*'],
                             'market_count_error':r.visited_markets-meta['M*'],'evaluations':r.evaluations,'seconds':r.seconds})
        print(f'[{idx}/{len(targets)}] {name} done',flush=True)

    fields=list(rows[0]);
    with (outdir/'runs.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

    summaries=[]
    for m in methods:
        a=f'TPP-{m}'; rr=[r for r in rows if r['algorithm']==a]
        gaps=[r['gap_opt_pct'] for r in rr]; scores=[r['score'] for r in rr]
        summaries.append({'algorithm':a,'runs':len(rr),'instances':len(set(r['instance'] for r in rr)),
                          'median_gap_opt_pct':statistics.median(gaps),'mean_gap_opt_pct':statistics.mean(gaps),
                          'q90_gap_opt_pct':sorted(gaps)[max(0,int(.9*len(gaps))-1)],'best_gap_opt_pct':min(gaps),
                          'median_score':statistics.median(scores),'median_travel':statistics.median(r['travel'] for r in rr),
                          'median_purchase':statistics.median(r['purchase'] for r in rr),
                          'median_visited_markets':statistics.median(r['visited_markets'] for r in rr),
                          'median_abs_market_count_error':statistics.median(abs(r['market_count_error']) for r in rr),
                          'median_seconds':statistics.median(r['seconds'] for r in rr)})
    with (outdir/'summary.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(summaries[0]));w.writeheader();w.writerows(summaries)

    # instance-level medians support paired nonparametric comparison without pseudo-replicating seeds.
    instmed=defaultdict(dict)
    for name,_,meta in targets:
        for m in methods:
            vals=[r['gap_opt_pct'] for r in rows if r['instance']==name and r['algorithm']==f'TPP-{m}']
            instmed[name][m]=statistics.median(vals)
    pair=[]
    for i,a in enumerate(methods):
        for b in methods[i+1:]:
            xa=[instmed[n][a] for n,_,_ in targets]; xb=[instmed[n][b] for n,_,_ in targets]
            stat,p=wilcoxon(xa,xb,alternative='two-sided')
            pair.append({'method_a':a,'method_b':b,'wilcoxon_stat':stat,'p_value':p,
                         'wins_a':sum(x<y for x,y in zip(xa,xb)),'ties':sum(x==y for x,y in zip(xa,xb)),'losses_a':sum(x>y for x,y in zip(xa,xb))})
    order=sorted(range(len(pair)),key=lambda k:pair[k]['p_value']); running=0; n=len(pair)
    for rank,k in enumerate(order):
        running=max(running,(n-rank)*pair[k]['p_value']);pair[k]['holm_p']=min(1,running);pair[k]['significant_0.05']=pair[k]['holm_p']<.05
    with (outdir/'pairwise_instance_medians_holm.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(pair[0]));w.writeheader();w.writerows(pair)

    # size x method medians for interaction reading
    sized=[]
    for v,k in sorted(sizes):
        for m in methods:
            rr=[r for r in rows if r['markets']==v and r['products']==k and r['algorithm']==f'TPP-{m}']
            sized.append({'markets':v,'products':k,'algorithm':f'TPP-{m}','runs':len(rr),
                          'median_gap_opt_pct':statistics.median(r['gap_opt_pct'] for r in rr),
                          'median_travel':statistics.median(r['travel'] for r in rr),'median_purchase':statistics.median(r['purchase'] for r in rr),
                          'median_visited_markets':statistics.median(r['visited_markets'] for r in rr),
                          'median_abs_Mstar_error':statistics.median(abs(r['market_count_error']) for r in rr)})
    with (outdir/'size_profile.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(sized[0]));w.writeheader();w.writerows(sized)

    # Friedman on 20 instance medians
    arrays=[[instmed[n][m] for n,_,_ in targets] for m in methods]
    fr=friedmanchisquare(*arrays) if len(methods)>=3 else None
    with (outdir/'README.md').open('w',encoding='utf-8') as f:
        f.write('# Exact-OPT EEuclideo pilot suite\n\n')
        f.write(f'- Instances: {len(targets)} ({", ".join(f"{a}x{b}" for a,b in sorted(sizes))}; five each)\n')
        f.write(f'- Seeds: {args.seeds}; budget: {args.budget} objective evaluations per run.\n')
        f.write('- Reference: `Baseline_EEuclideo.csv` OPT and M* supplied with the extracted benchmark set.\n')
        if fr: f.write(f'- Friedman over per-instance median OPT gaps: statistic={fr.statistic:.6g}, p={fr.pvalue:.6g}.\n')
        f.write('\nThis directory is an exact-OPT validation layer. It must not be mixed with BKS-only large-instance claims.\n')
    print('Wrote',outdir,'elapsed',round(time.time()-started,1),'s')

if __name__=='__main__': main()
