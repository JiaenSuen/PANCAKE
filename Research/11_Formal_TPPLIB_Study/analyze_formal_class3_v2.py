"""Reference-safe analysis of the canonical 100-instance / 3,000-run TPPLIB study.

Primary comparisons are reference-independent: pooled-best RPD, paired instance medians,
performance profiles, scaling/density interactions, component decomposition, and anytime
budget efficiency. External reference gaps are only computed where the reference registry
explicitly carries a usable exact-candidate or literature BKS value.
"""
from __future__ import annotations
from pathlib import Path
import json, math
import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, spearmanr, wilcoxon
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
RDIR=HERE/'results'; FDIR=HERE/'figures'; FDIR.mkdir(exist_ok=True)


def save(df,name):
    df.to_csv(RDIR/name,index=False)


def holm(df):
    df=df.copy().sort_values('p_value').reset_index(drop=True)
    m=len(df); adj=[]; running=0.0
    for i,p in enumerate(df.p_value):
        running=max(running,(m-i)*float(p)); adj.append(min(1.0,running))
    df['holm_p']=adj; df['significant_0.05']=df.holm_p<0.05
    return df.sort_values(['method_a','method_b']).reset_index(drop=True)


def rank_biserial_lower_better(x,y):
    d=np.asarray(x)-np.asarray(y); d=d[d!=0]
    if len(d)==0:return 0.0
    return float((np.sum(d<0)-np.sum(d>0))/len(d))


def main():
    runs=pd.read_csv(RDIR/'formal_runs.csv')
    conv=pd.read_csv(RDIR/'formal_convergence.csv')
    mani=pd.read_csv(RDIR/'instance_manifest.csv')
    refs=pd.read_csv(RDIR/'reference_registry.csv')

    # Reference-safe canonical denominator: best score observed across all methods/seeds on each instance.
    best=runs.groupby('instance',as_index=False).score.min().rename(columns={'score':'best_observed_score'})
    runs=runs.merge(best,on='instance')
    runs['rpd_observed_pct']=100*(runs.score-runs.best_observed_score)/runs.best_observed_score
    runs=runs.merge(mani.drop(columns=['V','K','M_star','OPT'],errors='ignore'),on='instance',how='left')
    runs=runs.merge(refs[['instance','reference_status','reference_value','reference_market_count']],on='instance',how='left')
    runs['reference_gap_pct']=np.where(runs.reference_value.notna(),100*(runs.score-runs.reference_value)/runs.reference_value,np.nan)
    runs['reference_market_error']=np.where(runs.reference_market_count.notna(),runs.visited_markets-runs.reference_market_count,np.nan)
    runs['abs_reference_market_error']=np.abs(runs.reference_market_error)
    save(runs,'formal_runs_reference_safe.csv')

    # Instance-level medians are the independent unit for algorithm tests.
    imed=runs.groupby(['instance','algorithm'],as_index=False).agg(
        median_score=('score','median'), median_rpd=('rpd_observed_pct','median'),
        median_travel=('travel','median'), median_purchase=('purchase','median'),
        median_travel_share=('travel_share','median'), median_purchase_share=('purchase_share','median'),
        median_markets=('visited_markets','median'), median_seconds=('seconds','median'),
        V=('V','first'),K=('K','first'),scale_tier=('scale_tier','first'),
        product_supply_density_tier=('product_supply_density_tier','first'),
        market_assortment_density_tier=('market_assortment_density_tier','first'),
        offers_per_product=('offers_per_product','first'),offers_per_market=('offers_per_market','first'),
        normalized_offer_density=('normalized_offer_density','first'), product_market_ratio=('product_market_ratio','first'),
        decision_scale=('decision_scale','first'), reference_status=('reference_status','first'),
        reference_value=('reference_value','first'), reference_market_count=('reference_market_count','first')
    )
    imed['reference_gap_pct']=np.where(imed.reference_value.notna(),100*(imed.median_score-imed.reference_value)/imed.reference_value,np.nan)
    imed['market_count_error']=np.where(imed.reference_market_count.notna(),imed.median_markets-imed.reference_market_count,np.nan)
    imed['abs_market_count_error']=np.abs(imed.market_count_error)
    save(imed,'instance_method_medians_reference_safe.csv')

    algs=['TPP-ILS','TPP-VNS','TPP-DFOX']
    overall=[]
    for a,g in runs.groupby('algorithm'):
        gi=imed[imed.algorithm==a]
        overall.append({
            'algorithm':a,'runs':len(g),'instances':g.instance.nunique(),
            'median_observed_RPD_pct':g.rpd_observed_pct.median(),
            'IQR_observed_RPD_pct':g.rpd_observed_pct.quantile(.75)-g.rpd_observed_pct.quantile(.25),
            'q90_observed_RPD_pct':g.rpd_observed_pct.quantile(.90),
            'near_best_1pct_rate':100*np.mean(g.rpd_observed_pct<=1),
            'near_best_5pct_rate':100*np.mean(g.rpd_observed_pct<=5),
            'near_best_10pct_rate':100*np.mean(g.rpd_observed_pct<=10),
            'median_instance_RPD_pct':gi.median_rpd.median(),
            'median_travel_share':g.travel_share.median(),'median_purchase_share':g.purchase_share.median(),
            'median_runtime_seconds':g.seconds.median(),
        })
    overall=pd.DataFrame(overall).sort_values('median_instance_RPD_pct');save(overall,'overall_reference_safe_summary.csv')

    # Friedman + paired Wilcoxon/Holm on per-instance median score ratios, not raw seeds.
    piv=imed.pivot(index='instance',columns='algorithm',values='median_rpd').reindex(columns=algs)
    fr=friedmanchisquare(*[piv[a] for a in algs])
    pair=[]
    for i,a in enumerate(algs):
        for b in algs[i+1:]:
            x=piv[a].to_numpy();y=piv[b].to_numpy(); st,p=wilcoxon(x,y,alternative='two-sided')
            d=x-y
            pair.append({'method_a':a,'method_b':b,'wilcoxon_stat':st,'p_value':p,
                         'wins_a':int((d<0).sum()),'ties':int((d==0).sum()),'losses_a':int((d>0).sum()),
                         'median_RPD_difference_a_minus_b_pp':float(np.median(d)),
                         'rank_biserial_a_better_positive':rank_biserial_lower_better(x,y)})
    pair=holm(pd.DataFrame(pair));save(pair,'pairwise_reference_safe_holm.csv')

    # Stratification by scale and density.
    strat=[]
    for factor in ['scale_tier','product_supply_density_tier','market_assortment_density_tier']:
        for (level,a),g in imed.groupby([factor,'algorithm']):
            strat.append({'factor':factor,'level':level,'algorithm':a,'instances':len(g),
                          'median_RPD_pct':g.median_rpd.median(),'mean_RPD_pct':g.median_rpd.mean(),
                          'median_score':g.median_score.median(),'median_markets':g.median_markets.median(),
                          'median_travel_share':g.median_travel_share.median(),'median_purchase_share':g.median_purchase_share.median()})
    strat=pd.DataFrame(strat);save(strat,'stratified_reference_safe_profiles.csv')

    grid=imed.groupby(['V','K','algorithm'],as_index=False).agg(instances=('instance','nunique'),
        median_RPD_pct=('median_rpd','median'),mean_RPD_pct=('median_rpd','mean'),
        median_travel=('median_travel','median'),median_purchase=('median_purchase','median'),
        median_markets=('median_markets','median'))
    save(grid,'VK_scaling_grid_reference_safe.csv')

    # Scaling degradation and structural correlations.
    scaling=[]; corr=[]
    for a,g in imed.groupby('algorithm'):
        x=np.log10(g.decision_scale.to_numpy(float));y=g.median_rpd.to_numpy(float)
        slope,intercept=np.polyfit(x,y,1); rho,p=spearmanr(g.decision_scale,y)
        med={t:g.loc[g.scale_tier==t,'median_rpd'].median() for t in ['small','medium','large']}
        scaling.append({'algorithm':a,'RPD_slope_pp_per_log10_decision_scale':slope,
                        'spearman_rho_scale_RPD':rho,'spearman_p':p,
                        'small_median_RPD':med['small'],'medium_median_RPD':med['medium'],'large_median_RPD':med['large'],
                        'large_minus_small_pp':med['large']-med['small']})
        for c in ['offers_per_product','offers_per_market','normalized_offer_density','product_market_ratio','V','K']:
            rr,pp=spearmanr(g[c],g.median_rpd)
            corr.append({'algorithm':a,'descriptor':c,'spearman_rho_RPD':rr,'p_value':pp})
    scaling=pd.DataFrame(scaling).sort_values('large_minus_small_pp'); save(scaling,'mechanism_scaling_degradation.csv')
    save(pd.DataFrame(corr),'instance_structure_correlations.csv')

    # Route/purchase decomposition: relative to best tested component median on same instance.
    comp=imed.copy()
    comp['best_tested_travel']=comp.groupby('instance').median_travel.transform('min')
    comp['best_tested_purchase']=comp.groupby('instance').median_purchase.transform('min')
    comp['travel_excess_vs_best_tested_pct']=100*(comp.median_travel-comp.best_tested_travel)/comp.best_tested_travel
    comp['purchase_excess_vs_best_tested_pct']=100*(comp.median_purchase-comp.best_tested_purchase)/comp.best_tested_purchase
    csum=comp.groupby(['algorithm','scale_tier'],as_index=False).agg(
        instances=('instance','nunique'),median_travel_excess_pct=('travel_excess_vs_best_tested_pct','median'),
        median_purchase_excess_pct=('purchase_excess_vs_best_tested_pct','median'),
        median_travel_share=('median_travel_share','median'),median_purchase_share=('median_purchase_share','median'))
    save(csum,'route_purchase_decomposition.csv')

    # Market cardinality only on the 88 legacy closed-reference candidates.
    card=imed[imed.reference_status=='legacy_closed_candidate'].copy()
    card_summary=card.groupby(['algorithm','scale_tier'],as_index=False).agg(
        instances=('instance','nunique'),median_signed_market_error=('market_count_error','median'),
        median_abs_market_error=('abs_market_count_error','median'),mean_abs_market_error=('abs_market_count_error','mean'),
        exact_market_count_rate=('market_count_error',lambda s:100*np.mean(np.asarray(s)==0)))
    save(card_summary,'market_cardinality_closed_candidate_subset.csv')

    # External BKS validation on 11 published open cases.
    bks=imed[imed.reference_status=='literature_bks_open'].copy()
    bks_summary=bks.groupby('algorithm',as_index=False).agg(instances=('instance','nunique'),
        median_BKS_gap_pct=('reference_gap_pct','median'),mean_BKS_gap_pct=('reference_gap_pct','mean'),
        best_BKS_gap_pct=('reference_gap_pct','min'),q90_BKS_gap_pct=('reference_gap_pct',lambda s:s.quantile(.9)))
    save(bks_summary,'literature_BKS_validation.csv')

    # Convergence: recompute RPD to pooled final best, ignoring stale gap_opt_pct column.
    conv=conv.merge(best,on='instance',how='left').merge(mani[['instance','scale_tier']],on='instance',how='left')
    conv['rpd_observed_pct']=100*(conv.best_score-conv.best_observed_score)/conv.best_observed_score
    save(conv,'formal_convergence_reference_safe.csv')
    convsum=conv.groupby(['algorithm','FE'],as_index=False).agg(
        median_RPD=('rpd_observed_pct','median'),q25_RPD=('rpd_observed_pct',lambda s:s.quantile(.25)),q75_RPD=('rpd_observed_pct',lambda s:s.quantile(.75)),
        near_best_10pct_rate=('rpd_observed_pct',lambda s:100*np.mean(np.asarray(s)<=10)),near_best_5pct_rate=('rpd_observed_pct',lambda s:100*np.mean(np.asarray(s)<=5)))
    save(convsum,'convergence_reference_safe_summary.csv')

    eff=[]
    checkpoints=sorted(conv.FE.unique())
    for (inst,seed,a),g in conv.groupby(['instance','seed','algorithm']):
        g=g.sort_values('FE'); x=g.FE.to_numpy(float); y=g.rpd_observed_pct.to_numpy(float)
        auc=float(np.trapezoid(y,x)/(x[-1]-x[0]))
        row={'instance':inst,'seed':seed,'algorithm':a,'RPD_AUC':auc}
        for th in [30,20,15,10,5]:
            hit=g[g.rpd_observed_pct<=th]
            row[f'FE_to_RPD_le_{th}']=float(hit.FE.iloc[0]) if len(hit) else np.nan
        eff.append(row)
    eff=pd.DataFrame(eff);save(eff,'budget_efficiency_reference_safe_runs.csv')
    es=[]
    for a,g in eff.groupby('algorithm'):
        row={'algorithm':a,'median_RPD_AUC':g.RPD_AUC.median()}
        for th in [30,20,15,10,5]:
            c=f'FE_to_RPD_le_{th}'; h=g[c].notna();row[f'coverage_RPD_le_{th}_pct']=100*h.mean();row[f'median_FE_to_RPD_le_{th}_among_hits']=g.loc[h,c].median() if h.any() else np.nan
        es.append(row)
    effsum=pd.DataFrame(es).sort_values('median_RPD_AUC');save(effsum,'budget_efficiency_reference_safe_summary.csv')

    # Dolan-More-style performance profile based on per-instance median scores.
    sp=imed.pivot(index='instance',columns='algorithm',values='median_score').reindex(columns=algs)
    ratio=sp.div(sp.min(axis=1),axis=0)
    taus=np.linspace(1,1.5,101); prows=[]
    for a in algs:
        for tau in taus: prows.append({'algorithm':a,'tau':tau,'fraction_instances':float(np.mean(ratio[a]<=tau))})
    perf=pd.DataFrame(prows);save(perf,'performance_profile.csv')

    # Figures (paper drafts).
    order=overall.algorithm.tolist()
    fig,ax=plt.subplots(figsize=(7.2,4.4));data=[imed[imed.algorithm==a].median_rpd for a in order]
    ax.boxplot(data,tick_labels=order,showfliers=False);ax.set_ylabel('Per-instance median observed RPD (%)');ax.grid(axis='y',alpha=.25);fig.tight_layout();fig.savefig(FDIR/'formal_rpd_distribution.png',dpi=240);plt.close(fig)

    fig,ax=plt.subplots(figsize=(7.2,4.5))
    for a in order:
        g=convsum[convsum.algorithm==a];ax.plot(g.FE,g.median_RPD,label=a);ax.fill_between(g.FE,g.q25_RPD,g.q75_RPD,alpha=.12)
    ax.set_xlabel('Objective evaluations');ax.set_ylabel('Observed RPD (%)');ax.legend(frameon=False);ax.grid(alpha=.25);fig.tight_layout();fig.savefig(FDIR/'formal_convergence.png',dpi=240);plt.close(fig)

    fig,ax=plt.subplots(figsize=(7.2,4.5)); tiers=['small','medium','large'];x=np.arange(3);w=.23
    for i,a in enumerate(order):
        vals=[float(strat[(strat.factor=='scale_tier')&(strat.level==t)&(strat.algorithm==a)].median_RPD_pct.iloc[0]) for t in tiers]
        ax.bar(x+(i-1)*w,vals,width=w,label=a)
    ax.set_xticks(x,tiers);ax.set_ylabel('Median observed RPD (%)');ax.set_xlabel('Scale tier');ax.legend(frameon=False);ax.grid(axis='y',alpha=.25);fig.tight_layout();fig.savefig(FDIR/'formal_scaling_degradation.png',dpi=240);plt.close(fig)

    fig,ax=plt.subplots(figsize=(7.2,4.5))
    for a in order:
        g=perf[perf.algorithm==a];ax.plot(g.tau,g.fraction_instances,label=a)
    ax.set_xlabel(r'Performance ratio $\tau$');ax.set_ylabel('Fraction of instances');ax.set_ylim(0,1.02);ax.legend(frameon=False);ax.grid(alpha=.25);fig.tight_layout();fig.savefig(FDIR/'formal_performance_profile.png',dpi=240);plt.close(fig)

    # 2D density map of instance descriptors.
    fig,ax=plt.subplots(figsize=(7.0,4.8));sc=ax.scatter(mani.offers_per_product,mani.offers_per_market,s=30+0.05*mani.decision_scale,alpha=.7)
    ax.set_xlabel('Offers per product');ax.set_ylabel('Offers per purchasable market');ax.grid(alpha=.2);fig.tight_layout();fig.savefig(FDIR/'formal_instance_density_map.png',dpi=240);plt.close(fig)

    # Mechanism component excess.
    fig,ax=plt.subplots(figsize=(7.2,4.5)); cplot=comp.groupby('algorithm',as_index=False).agg(travel=('travel_excess_vs_best_tested_pct','median'),purchase=('purchase_excess_vs_best_tested_pct','median')).set_index('algorithm').loc[order]
    xx=np.arange(len(order));w=.34;ax.bar(xx-w/2,cplot.travel,width=w,label='Travel excess');ax.bar(xx+w/2,cplot.purchase,width=w,label='Purchase excess');ax.set_xticks(xx,order);ax.set_ylabel('Median excess vs best tested component (%)');ax.legend(frameon=False);ax.grid(axis='y',alpha=.25);fig.tight_layout();fig.savefig(FDIR/'formal_route_purchase_decomposition.png',dpi=240);plt.close(fig)

    # Findings JSON
    stats={'instances':100,'runs':3000,'seeds':10,'budget_FE':1200,'friedman_statistic':float(fr.statistic),'friedman_p':float(fr.pvalue),
           'reference_registry_counts':refs.reference_status.value_counts().to_dict()}
    (RDIR/'formal_statistics_reference_safe.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')

    print('\nOVERALL\n',overall.to_string(index=False))
    print('\nSCALING\n',scaling.to_string(index=False))
    print('\nBKS\n',bks_summary.to_string(index=False))
    print('\nBUDGET\n',effsum.to_string(index=False))
    print('\nPAIR\n',pair.to_string(index=False))
    print('\nFriedman',fr)

if __name__=='__main__': main()
