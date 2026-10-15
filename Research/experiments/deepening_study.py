from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'ResearchBenchmark'))

from meta_study import (  # noqa: E402
    Problem, generate_problem, run_ga_tabu, run_tabu, run_ga,
)
from algorithms import (  # noqa: E402
    run_dfox_apns, run_dwoa_avns, run_ils, run_vns,
    run_dcpo, run_dbka, run_dho, run_dfox_ablation,
)

OUT = ROOT / 'Research' / 'results'
FIG = OUT / 'figures'
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)


def bks_by_instance(rows):
    out = {}
    for r in rows:
        out[r.inst] = min(out.get(r.inst, math.inf), r.score)
    return out


def trace_auc(trace, budget, bks):
    if not trace:
        return math.inf
    tr = sorted(trace)
    prev = 0
    last = tr[0][1]
    area = 0.0
    for e, v in tr:
        e = min(e, budget)
        area += (e - prev) / budget * 100.0 * (last - bks) / bks
        prev = e
        last = min(last, v)
    if prev < budget:
        area += (budget - prev) / budget * 100.0 * (last - bks) / bks
    return area


def write_csv(path, rows):
    if not rows:
        return
    with Path(path).open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)


def export_convergence(rrs, budget, prefix, checkpoints=20):
    """Export pooled median/IQR best-so-far RPD at fixed FE checkpoints."""
    bks = bks_by_instance(rrs)
    algs = sorted({r.alg for r in rrs})
    rows=[]
    for alg in algs:
        subset=[r for r in rrs if r.alg==alg]
        for ci in range(1,checkpoints+1):
            cp=max(1,int(round(budget*ci/checkpoints)))
            vals=[]
            for r in subset:
                tr=sorted(r.trace)
                if not tr:
                    continue
                val=tr[0][1]
                for e,v in tr:
                    if e>cp: break
                    val=min(val,v)
                vals.append(100.0*(val-bks[r.inst])/bks[r.inst])
            if not vals: continue
            vals=sorted(vals); n=len(vals)
            def quant(q):
                if n==1:return vals[0]
                pos=(n-1)*q; lo=int(math.floor(pos)); hi=int(math.ceil(pos))
                if lo==hi:return vals[lo]
                return vals[lo]+(vals[hi]-vals[lo])*(pos-lo)
            rows.append({'algorithm':alg,'evals':cp,'progress':cp/budget,
                         'median_rpd_pct':statistics.median(vals),'q1_rpd_pct':quant(.25),'q3_rpd_pct':quant(.75)})
    write_csv(OUT/f'{prefix}_convergence.csv',rows)
    return rows


def summarize(rrs, budget):
    bks = bks_by_instance(rrs)
    details = []
    for r in rrs:
        rpd = 100 * (r.score - bks[r.inst]) / bks[r.inst]
        details.append({
            'algorithm': r.alg, 'instance': r.inst, 'family': r.family, 'seed': r.seed,
            'score': r.score, 'rpd_pct': rpd,
            'conv_auc_rpd': trace_auc(r.trace, budget, bks[r.inst]),
        })
    algs = sorted({x['algorithm'] for x in details})
    paired_keys = sorted({(x['instance'], x['seed']) for x in details})
    ranks = {a: [] for a in algs}
    try:
        from scipy.stats import rankdata
        for key in paired_keys:
            vals = {a: next(x['score'] for x in details if (x['instance'], x['seed']) == key and x['algorithm'] == a) for a in algs}
            rr = rankdata([vals[a] for a in algs], method='average')
            for a, rank in zip(algs, rr): ranks[a].append(float(rank))
    except Exception:
        for key in paired_keys:
            vals = sorted((x['score'], x['algorithm']) for x in details if (x['instance'], x['seed']) == key)
            for rank, (_, a) in enumerate(vals, 1): ranks[a].append(float(rank))

    summary = []
    for a in algs:
        sub = [x for x in details if x['algorithm'] == a]
        rpds = [x['rpd_pct'] for x in sub]
        q = statistics.quantiles(rpds, n=4) if len(rpds) >= 4 else [min(rpds), statistics.median(rpds), max(rpds)]
        summary.append({
            'algorithm': a,
            'runs': len(sub),
            'median_rpd_pct': statistics.median(rpds),
            'iqr_rpd_pct': q[2] - q[0],
            'mean_rpd_pct': statistics.fmean(rpds),
            'median_auc_rpd': statistics.median(x['conv_auc_rpd'] for x in sub),
            'mean_rank': statistics.fmean(ranks[a]),
            'win_rate_pct': 100 * sum(abs(x['rpd_pct']) < 1e-12 for x in sub) / len(sub),
        })
    summary.sort(key=lambda x: x['mean_rank'])
    return details, summary


def holm_adjust(pairs):
    # Holm step-down adjusted p-values; pairs is list of dicts containing p_value.
    order = sorted(range(len(pairs)), key=lambda i: pairs[i]['p_value'])
    m = len(order); running = 0.0
    for j, idx in enumerate(order):
        adj = min(1.0, (m - j) * pairs[idx]['p_value'])
        running = max(running, adj)
        pairs[idx]['holm_p'] = running
        pairs[idx]['significant_0.05'] = running < 0.05
    return pairs


def statistical_tests(details, prefix):
    algs = sorted({x['algorithm'] for x in details})
    keys = sorted({(x['instance'], x['seed']) for x in details})
    vectors = {a: [next(x['score'] for x in details if x['algorithm'] == a and (x['instance'], x['seed']) == k) for k in keys] for a in algs}
    stat_obj = {'paired_cases': len(keys), 'algorithms': algs}
    try:
        from scipy.stats import friedmanchisquare, wilcoxon
        if len(algs) >= 3:
            stat, p = friedmanchisquare(*[vectors[a] for a in algs])
            stat_obj['friedman_stat'] = float(stat); stat_obj['friedman_p'] = float(p)
        pairs = []
        for i, a in enumerate(algs):
            for b in algs[i+1:]:
                av, bv = vectors[a], vectors[b]
                try:
                    ws, pv = wilcoxon(av, bv, alternative='two-sided', zero_method='wilcox')
                except ValueError:
                    ws, pv = 0.0, 1.0
                impr = [100 * (y - x) / y for x, y in zip(av, bv) if abs(y) > 1e-12]
                wins = sum(x < y for x, y in zip(av, bv)); ties = sum(abs(x-y) < 1e-12 for x,y in zip(av,bv)); losses = len(av)-wins-ties
                pairs.append({'method_a':a,'method_b':b,'wilcoxon_stat':float(ws),'p_value':float(pv),
                              'median_improvement_a_vs_b_pct':statistics.median(impr) if impr else 0.0,
                              'wins_a':wins,'ties':ties,'losses_a':losses})
        holm_adjust(pairs)
        write_csv(OUT / f'{prefix}_pairwise_holm.csv', pairs)
    except Exception as e:
        stat_obj['error'] = repr(e)
    (OUT / f'{prefix}_statistics.json').write_text(json.dumps(stat_obj, indent=2), encoding='utf-8')


def generate_eeuclideo_style(markets, products, idx, seed=20261011):
    """Regenerate the *published Class-3 protocol*, not the original instance bytes.

    Literature describes integer Euclidean market coordinates in [0,1000]^2, product
    availability at a random subset of markets, prices in [0,500], and a return tour.
    This generator is therefore labelled EEuclideo-*style* throughout the project.
    """
    rng = random.Random(seed + markets * 10007 + products * 1009 + idx)
    market_xy = [(rng.randint(0,1000), rng.randint(0,1000)) for _ in range(markets)]
    depot_xy = (rng.randint(0,1000), rng.randint(0,1000))
    all_xy = market_xy + [depot_xy]
    matrix = []
    for ax, ay in all_xy:
        row=[]
        for bx, by in all_xy:
            row.append(float(int(math.hypot(bx-ax, by-ay))))
        matrix.append(row)
    candidates=[]
    for _ in range(products):
        mk=rng.randint(1,max(1,markets-1))
        suppliers=rng.sample(range(markets),mk)
        candidates.append([(m,float(rng.randint(0,500))) for m in suppliers])
    return Problem(
        name=f'EEuclideoStyle_{markets}_{products}_{idx}', family='tpp_eeuclideo_style',
        coords=[(float(x),float(y)) for x,y in market_xy], candidates=candidates,
        unit_cost=1.0, return_to_depot=True, distance_matrix=matrix, depot_index=markets,
    )


def run_main_suite(seeds, budget):
    probs=[generate_problem(fam,i,n=16) for fam in ['uniform','clustered','price_distance_conflict','shared_hubs','deceptive_groups'] for i in (1,2)]
    algs=[run_ga_tabu,run_dfox_apns,run_dwoa_avns,run_ils,run_vns,run_dcpo,run_dbka,run_dho]
    rows=[]
    for pi,p in enumerate(probs,1):
        print(f'[main {pi}/{len(probs)}] {p.name}', flush=True)
        for s in range(seeds):
            sd=77+10007*s
            for fn in algs: rows.append(fn(p,sd,budget))
    details,summary=summarize(rows,budget);write_csv(OUT/'main_runs.csv',details);write_csv(OUT/'main_summary.csv',summary);export_convergence(rows,budget,'main');statistical_tests(details,'main')
    return summary


def run_ablation_suite(seeds,budget):
    probs=[generate_problem(fam,i,n=16) for fam in ['uniform','clustered','price_distance_conflict','shared_hubs','deceptive_groups'] for i in (1,2)]
    rows=[]; telemetry_rows=[]
    for pi,p in enumerate(probs,1):
        print(f'[ablation {pi}/{len(probs)}] {p.name}', flush=True)
        for s in range(seeds):
            sd=177+10007*s
            for level in range(4):
                tel={}
                rr=run_dfox_ablation(p,sd,budget,level=level,telemetry=tel if level==3 else None);rows.append(rr)
                if level==3:
                    for op,d in tel.get('operator',{}).items():
                        telemetry_rows.append({'instance':p.name,'family':p.family,'seed':sd,'operator':op,**d})
    details,summary=summarize(rows,budget);write_csv(OUT/'ablation_runs.csv',details);write_csv(OUT/'ablation_summary.csv',summary);write_csv(OUT/'operator_telemetry.csv',telemetry_rows);export_convergence(rows,budget,'ablation');statistical_tests(details,'ablation')
    return summary,telemetry_rows


def run_tpp_style_suite(seeds,budget):
    specs=[(50,50,1),(50,50,2),(50,100,1),(100,50,1)]
    probs=[generate_eeuclideo_style(*x) for x in specs]
    algs=[run_ga_tabu,run_dfox_apns,run_dwoa_avns,run_ils,run_vns,run_dbka]
    rows=[]
    for pi,p in enumerate(probs,1):
        print(f'[TPP-style {pi}/{len(probs)}] {p.name}',flush=True)
        for s in range(seeds):
            sd=277+10007*s
            for fn in algs:rows.append(fn(p,sd,budget))
    details,summary=summarize(rows,budget);write_csv(OUT/'tpp_style_runs.csv',details);write_csv(OUT/'tpp_style_summary.csv',summary);export_convergence(rows,budget,'tpp_style');statistical_tests(details,'tpp_style')
    return summary


def make_figures():
    import pandas as pd
    import matplotlib.pyplot as plt
    for fname,title,outname in [
        ('main_summary.csv','PANCAKE deepening study: mean paired rank','main_mean_rank.png'),
        ('ablation_summary.csv','Controlled DFOX ablation: median RPD','ablation_median_rpd.png'),
        ('tpp_style_summary.csv','EEuclideo-style TPP transfer: mean paired rank','tpp_style_mean_rank.png'),
    ]:
        p=OUT/fname
        if not p.exists():continue
        df=pd.read_csv(p)
        metric='median_rpd_pct' if fname.startswith('ablation') else 'mean_rank'
        df=df.sort_values(metric)
        fig,ax=plt.subplots(figsize=(9,4.8),dpi=180)
        ax.bar(df['algorithm'],df[metric])
        ax.set_title(title);ax.set_ylabel('Median RPD (%)' if metric=='median_rpd_pct' else 'Mean rank (lower is better)')
        ax.tick_params(axis='x',rotation=35);fig.tight_layout();fig.savefig(FIG/outname,bbox_inches='tight');plt.close(fig)
    for prefix,title in [('main','PANCAKE main: median best-so-far RPD'),('ablation','DFOX ablation: median best-so-far RPD'),('tpp_style','TPP-style transfer: median best-so-far RPD')]:
        cp=OUT/f'{prefix}_convergence.csv'
        if not cp.exists(): continue
        df=pd.read_csv(cp)
        fig,ax=plt.subplots(figsize=(8.5,4.8),dpi=180)
        for alg,g in df.groupby('algorithm'):
            g=g.sort_values('progress');ax.plot(g['progress'],g['median_rpd_pct'],label=alg,linewidth=1.5)
        ax.set_title(title);ax.set_xlabel('Normalized objective-evaluation budget');ax.set_ylabel('Median best-so-far RPD (%)')
        ax.legend(fontsize=7,ncol=2);fig.tight_layout();fig.savefig(FIG/f'{prefix}_convergence.png',bbox_inches='tight');plt.close(fig)

    tele=OUT/'operator_telemetry.csv'
    if tele.exists():
        df=pd.read_csv(tele);g=df.groupby('operator',as_index=False).agg(calls=('calls','sum'),success=('success','sum'),total_improvement=('total_improvement','sum'))
        g['success_rate']=g['success']/g['calls'].clip(lower=1);g=g.sort_values('success_rate',ascending=False)
        fig,ax=plt.subplots(figsize=(8.5,4.8),dpi=180);ax.bar(g['operator'],g['success_rate']);ax.set_title('DFOX-A3 operator success rate');ax.set_ylabel('Successful-improvement rate');ax.tick_params(axis='x',rotation=30);fig.tight_layout();fig.savefig(FIG/'operator_success_rate.png',bbox_inches='tight');plt.close(fig)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--seeds',type=int,default=10)
    ap.add_argument('--budget',type=int,default=1200)
    ap.add_argument('--tpp-budget',type=int,default=2400)
    ap.add_argument('--tpp-seeds',type=int,default=5)
    ap.add_argument('--quick',action='store_true',help='2 seeds and reduced budgets for CI/smoke testing')
    args=ap.parse_args()
    if args.quick:
        args.seeds=2;args.budget=300;args.tpp_seeds=2;args.tpp_budget=500
    main_summary=run_main_suite(args.seeds,args.budget)
    ablation_summary,_=run_ablation_suite(args.seeds,args.budget)
    tpp_summary=run_tpp_style_suite(args.tpp_seeds,args.tpp_budget)
    make_figures()
    payload={'protocol':vars(args),'main_top3':main_summary[:3],'ablation':ablation_summary,'tpp_style_top3':tpp_summary[:3]}
    (OUT/'study_manifest.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    print('DONE',OUT)


if __name__=='__main__':main()
