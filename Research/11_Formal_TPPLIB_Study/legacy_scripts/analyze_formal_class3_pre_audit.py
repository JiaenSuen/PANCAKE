"""Analyze the canonical PANCAKE 100-instance Class-3 experiment.

Outputs paper-ready tables, figures, statistical tests, scaling summaries,
mechanism-degradation profiles, component decomposition, M* cardinality analysis,
and convergence budget-efficiency metrics.
"""
from __future__ import annotations
import csv, json, math, statistics
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, spearmanr, wilcoxon
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RDIR = HERE / "results"
FDIR = HERE / "figures"
FDIR.mkdir(parents=True, exist_ok=True)


def holm(rows):
    order = sorted(range(len(rows)), key=lambda i: rows[i]["p_value"])
    running = 0.0; n=len(rows)
    for rank,i in enumerate(order):
        running=max(running,(n-rank)*rows[i]["p_value"])
        rows[i]["holm_p"] = min(1.0,running)
        rows[i]["significant_0.05"] = rows[i]["holm_p"] < 0.05
    return rows


def rank_biserial_paired(x,y):
    d=np.asarray(x)-np.asarray(y)
    nz=d[d!=0]
    if len(nz)==0:return 0.0
    return float((np.sum(nz<0)-np.sum(nz>0))/len(nz)) # positive => x better (lower)


def auc_gap(g):
    g=g.sort_values('FE')
    x=g.FE.to_numpy(float); y=g.gap_opt_pct.to_numpy(float)
    return float(np.trapezoid(y,x)/(x[-1]-x[0])) if len(x)>1 else float(y[0])


def first_fe(g,threshold):
    z=g[g.gap_opt_pct<=threshold]
    return float(z.FE.min()) if len(z) else math.nan


def save(df,name):
    df.to_csv(RDIR/name,index=False)


def main():
    runs=pd.read_csv(RDIR/'formal_runs.csv')
    conv=pd.read_csv(RDIR/'formal_convergence.csv')
    manifest=pd.read_csv(RDIR/'instance_manifest.csv')
    df=runs.merge(manifest.drop(columns=['V','K','M_star','OPT'], errors='ignore'),on='instance',how='left')

    algs=sorted(df.algorithm.unique())
    # Overall descriptive summary.
    summary=[]
    for a,g in df.groupby('algorithm'):
        gaps=g.gap_opt_pct.to_numpy(float)
        summary.append({
            'algorithm':a,'runs':len(g),'instances':g.instance.nunique(),
            'median_gap_opt_pct':np.median(gaps),'mean_gap_opt_pct':np.mean(gaps),
            'IQR_gap_opt_pct':np.percentile(gaps,75)-np.percentile(gaps,25),
            'q90_gap_opt_pct':np.percentile(gaps,90),'best_gap_opt_pct':np.min(gaps),
            'success_gap_le_1_pct':100*np.mean(gaps<=1),'success_gap_le_5_pct':100*np.mean(gaps<=5),
            'success_gap_le_10_pct':100*np.mean(gaps<=10),
            'median_abs_Mstar_error':np.median(g.abs_market_count_error),
            'median_signed_Mstar_error':np.median(g.market_count_error),
            'median_travel_share':np.median(g.travel_share),'median_purchase_share':np.median(g.purchase_share),
            'median_seconds':np.median(g.seconds),
        })
    overall=pd.DataFrame(summary).sort_values('median_gap_opt_pct')
    save(overall,'overall_summary.csv')

    # Independent unit for algorithm statistics = per-instance median over 10 seeds.
    imed=df.groupby(['instance','algorithm'],as_index=False).agg(
        median_gap=('gap_opt_pct','median'), median_score=('score','median'),
        median_travel=('travel','median'),median_purchase=('purchase','median'),
        median_abs_Mstar_error=('abs_market_count_error','median'),
        median_Mstar_error=('market_count_error','median'),
        V=('V','first'),K=('K','first'),scale_tier=('scale_tier','first'),
        product_supply_density_tier=('product_supply_density_tier','first'),
        market_assortment_density_tier=('market_assortment_density_tier','first'),
        offers_per_product=('offers_per_product','first'),offers_per_market=('offers_per_market','first'),
        normalized_offer_density=('normalized_offer_density','first'),product_market_ratio=('product_market_ratio','first'),decision_scale=('decision_scale','first')
    )
    save(imed,'instance_method_medians.csv')
    pivot=imed.pivot(index='instance',columns='algorithm',values='median_gap')
    fried=friedmanchisquare(*[pivot[a].to_numpy() for a in algs])
    pair=[]
    for i,a in enumerate(algs):
        for b in algs[i+1:]:
            x=pivot[a].to_numpy();y=pivot[b].to_numpy()
            st,p=wilcoxon(x,y,two_sided if False else 'two-sided') if False else wilcoxon(x,y,alternative='two-sided')
            diff=x-y
            pair.append({'method_a':a,'method_b':b,'wilcoxon_stat':st,'p_value':p,
                         'wins_a':int(np.sum(diff<0)),'ties':int(np.sum(diff==0)),'losses_a':int(np.sum(diff>0)),
                         'median_paired_gap_difference_a_minus_b':float(np.median(diff)),
                         'rank_biserial_a_better_positive':rank_biserial_paired(x,y)})
    pair=pd.DataFrame(holm(pair));save(pair,'pairwise_instance_median_holm.csv')

    # Stratified profiles.
    profiles=[]
    for factor in ['scale_tier','product_supply_density_tier','market_assortment_density_tier']:
        for (level,a),g in imed.groupby([factor,'algorithm']):
            profiles.append({'factor':factor,'level':level,'algorithm':a,'instances':len(g),
                             'median_gap_opt_pct':g.median_gap.median(),'mean_gap_opt_pct':g.median_gap.mean(),
                             'median_abs_Mstar_error':g.median_abs_Mstar_error.median(),
                             'median_travel':g.median_travel.median(),'median_purchase':g.median_purchase.median()})
    strat=pd.DataFrame(profiles);save(strat,'stratified_profiles.csv')

    # Exact V x K scaling grid.
    grid=imed.groupby(['V','K','algorithm'],as_index=False).agg(
        instances=('instance','nunique'),median_gap_opt_pct=('median_gap','median'),
        mean_gap_opt_pct=('median_gap','mean'),median_abs_Mstar_error=('median_abs_Mstar_error','median'),
        median_travel=('median_travel','median'),median_purchase=('median_purchase','median'))
    save(grid,'VK_scaling_grid.csv')

    # Scaling law descriptors: robust descriptive slope/correlation, not causal model.
    scales=[]
    for a,g in imed.groupby('algorithm'):
        x=np.log10(g.decision_scale.to_numpy(float)); y=g.median_gap.to_numpy(float)
        slope,intercept=np.polyfit(x,y,1)
        rho,p=spearmanr(g.decision_scale,y)
        small=np.median(g[g.scale_tier=='small'].median_gap)
        large=np.median(g[g.scale_tier=='large'].median_gap)
        scales.append({'algorithm':a,'gap_slope_per_log10_decision_scale':slope,
                       'spearman_rho_scale_gap':rho,'spearman_p':p,
                       'small_median_gap':small,'large_median_gap':large,
                       'large_minus_small_gap_pp':large-small,
                       'large_over_small_gap_ratio':large/max(small,1e-12)})
    scale_df=pd.DataFrame(scales).sort_values('gap_slope_per_log10_decision_scale');save(scale_df,'scaling_law_summary.csv')

    # Density correlations per algorithm.
    dens=[]
    for a,g in imed.groupby('algorithm'):
        for col in ['offers_per_product','offers_per_market','normalized_offer_density','product_market_ratio']:
            rho,p=spearmanr(g[col],g.median_gap)
            dens.append({'algorithm':a,'descriptor':col,'spearman_rho_gap':rho,'p_value':p})
    save(pd.DataFrame(dens),'structure_gap_correlations.csv')

    # Component profile. No optimal component decomposition is claimed.
    comp=[]
    for (tier,a),g in df.groupby(['scale_tier','algorithm']):
        comp.append({'scale_tier':tier,'algorithm':a,'runs':len(g),
                     'median_travel':g.travel.median(),'median_purchase':g.purchase.median(),
                     'median_travel_share':g.travel_share.median(),'median_purchase_share':g.purchase_share.median(),
                     'median_gap_opt_pct':g.gap_opt_pct.median()})
    save(pd.DataFrame(comp),'route_purchase_component_profile.csv')

    # M* error distribution / bias.
    merr=df.groupby(['algorithm','scale_tier'],as_index=False).agg(
        median_signed_error=('market_count_error','median'),mean_signed_error=('market_count_error','mean'),
        median_abs_error=('abs_market_count_error','median'),mean_abs_error=('abs_market_count_error','mean'),
        exact_Mstar_rate=('market_count_error',lambda s:100*np.mean(np.asarray(s)==0)))
    save(merr,'Mstar_cardinality_profile.csv')

    # Convergence/budget efficiency.
    c=conv.merge(manifest[['instance','scale_tier']],on='instance',how='left')
    run_eff=[]
    for (inst,seed,a),g in c.groupby(['instance','seed','algorithm']):
        row={'instance':inst,'seed':seed,'algorithm':a,'gap_auc':auc_gap(g)}
        for t in [20,10,5,2,1]:row[f'FE_to_gap_le_{t}']=first_fe(g,t)
        run_eff.append(row)
    eff=pd.DataFrame(run_eff);save(eff,'budget_efficiency_runs.csv')
    effsum=[]
    for a,g in eff.groupby('algorithm'):
        row={'algorithm':a,'median_gap_auc':g.gap_auc.median()}
        for t in [20,10,5,2,1]:
            col=f'FE_to_gap_le_{t}'; hit=g[col].notna()
            row[f'success_gap_le_{t}_pct']=100*hit.mean()
            row[f'median_FE_to_gap_le_{t}_among_hits']=g.loc[hit,col].median() if hit.any() else math.nan
        effsum.append(row)
    effsum=pd.DataFrame(effsum).sort_values('median_gap_auc');save(effsum,'budget_efficiency_summary.csv')

    # Checkpoint median convergence.
    csum=c.groupby(['algorithm','FE'],as_index=False).agg(median_gap=('gap_opt_pct','median'),q25=('gap_opt_pct',lambda s:np.percentile(s,25)),q75=('gap_opt_pct',lambda s:np.percentile(s,75)))
    save(csum,'convergence_summary.csv')

    # Figures.
    order=overall.algorithm.tolist()
    fig,ax=plt.subplots(figsize=(7.2,4.4))
    data=[imed[imed.algorithm==a].median_gap.to_numpy() for a in order]
    ax.boxplot(data,labels=order,showfliers=False);ax.set_ylabel('Median OPT gap per instance (%)');ax.set_xlabel('Method');ax.grid(axis='y',alpha=.25)
    fig.tight_layout();fig.savefig(FDIR/'fig_opt_gap_distribution.png',dpi=220);plt.close(fig)

    fig,ax=plt.subplots(figsize=(7.2,4.5))
    for a in order:
        g=csum[csum.algorithm==a];ax.plot(g.FE,g.median_gap,label=a)
        ax.fill_between(g.FE,g.q25,g.q75,alpha=.12)
    ax.set_xlabel('Objective evaluations');ax.set_ylabel('OPT gap (%)');ax.legend(frameon=False);ax.grid(alpha=.25)
    fig.tight_layout();fig.savefig(FDIR/'fig_convergence_efficiency.png',dpi=220);plt.close(fig)

    fig,ax=plt.subplots(figsize=(7.2,4.5))
    scale_order=['small','medium','large'];x=np.arange(len(scale_order));w=.22
    for i,a in enumerate(order):
        vals=[]
        for t in scale_order:
            z=strat[(strat.factor=='scale_tier')&(strat.level==t)&(strat.algorithm==a)]
            vals.append(float(z.median_gap_opt_pct.iloc[0]))
        ax.bar(x+(i-(len(order)-1)/2)*w,vals,width=w,label=a)
    ax.set_xticks(x,scale_order);ax.set_ylabel('Median OPT gap (%)');ax.set_xlabel('Market-scale tier');ax.legend(frameon=False);ax.grid(axis='y',alpha=.25)
    fig.tight_layout();fig.savefig(FDIR/'fig_scaling_degradation.png',dpi=220);plt.close(fig)

    fig,ax=plt.subplots(figsize=(7.2,4.5))
    for a in order:
        z=merr[merr.algorithm==a].set_index('scale_tier').reindex(scale_order)
        ax.plot(scale_order,z.median_abs_error,marker='o',label=a)
    ax.set_ylabel('Median |visited markets - M*|');ax.set_xlabel('Market-scale tier');ax.legend(frameon=False);ax.grid(alpha=.25)
    fig.tight_layout();fig.savefig(FDIR/'fig_Mstar_cardinality_error.png',dpi=220);plt.close(fig)

    # Formal findings JSON and research snapshot.
    stats={'friedman_statistic':float(fried.statistic),'friedman_p':float(fried.pvalue),'instances':int(pivot.shape[0]),'methods':algs}
    (RDIR/'formal_statistics.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')

    print(overall.to_string(index=False))
    print('Friedman',stats)

if __name__=='__main__':main()
