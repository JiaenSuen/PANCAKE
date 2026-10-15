from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon, spearmanr, rankdata
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
RES=ROOT/'Research'/'results'; OUT=ROOT/'Research'/'08_Mechanism_Analysis'; FIG=RES/'figures'
OUT.mkdir(parents=True,exist_ok=True);FIG.mkdir(parents=True,exist_ok=True)

main=pd.read_csv(RES/'main_runs.csv')
abl=pd.read_csv(RES/'ablation_runs.csv')
rep=pd.read_csv(RES/'representation_runs.csv') if (RES/'representation_runs.csv').exists() else pd.DataFrame()

# ---------- family profiles ----------
family=main.groupby(['family','algorithm']).agg(median_rpd=('rpd_pct','median'),iqr_rpd=('rpd_pct',lambda x:np.percentile(x,75)-np.percentile(x,25)),median_auc=('conv_auc_rpd','median')).reset_index()
family.to_csv(OUT/'family_profile.csv',index=False)

# ---------- robustness / threshold success ----------
def q90(x):return np.percentile(x,90)
def q75(x):return np.percentile(x,75)
rob=main.groupby('algorithm').agg(median_rpd=('rpd_pct','median'),q75_rpd=('rpd_pct',q75),q90_rpd=('rpd_pct',q90),max_rpd=('rpd_pct','max'),std_rpd=('rpd_pct','std'),median_auc=('conv_auc_rpd','median')).reset_index()
for t in (5,10,20):
    s=main.assign(ok=main.rpd_pct<=t).groupby('algorithm').ok.mean().rename(f'success_le_{t}pct').reset_index()
    rob=rob.merge(s,on='algorithm')
rob.to_csv(OUT/'robustness_profile.csv',index=False)

# ---------- pairwise paired superiority ----------
P=main.pivot_table(index=['instance','seed'],columns='algorithm',values='score').dropna()
algs=list(P.columns);win=pd.DataFrame(index=algs,columns=algs,dtype=float);rel=pd.DataFrame(index=algs,columns=algs,dtype=float)
for a in algs:
    for b in algs:
        if a==b:win.loc[a,b]=.5;rel.loc[a,b]=0
        else:
            win.loc[a,b]=float((P[a]<P[b]).mean()+0.5*(P[a]==P[b]).mean())
            rel.loc[a,b]=float(np.median((P[a]-P[b])/P[b]*100))
win.to_csv(OUT/'pairwise_win_probability.csv');rel.to_csv(OUT/'pairwise_median_relative_gap_pct.csv')

# ---------- Dolan-More-like empirical performance profile ----------
best=P.min(axis=1);rat=P.div(best,axis=0)
taus=np.round(np.linspace(1.0,1.40,41),3);rows=[]
for a in algs:
    for tau in taus:rows.append({'algorithm':a,'tau':tau,'fraction_within_tau':float((rat[a]<=tau+1e-12).mean())})
pd.DataFrame(rows).to_csv(OUT/'performance_profile.csv',index=False)

# ---------- ablation paired effects ----------
A=abl.pivot_table(index=['instance','seed'],columns='algorithm',values='score').dropna()
steps=[('DFOX-A0-Generic','DFOX-A1-ProblemAware','problem-aware neighborhood'),('DFOX-A1-ProblemAware','DFOX-A2-Adaptive','adaptive operator control'),('DFOX-A2-Adaptive','DFOX-A3-Full','restart / long jump')]
rows=[]
for a,b,label in steps:
    diff=A[a]-A[b]; relimp=100*(A[a]-A[b])/A[a]
    nz=diff[diff!=0]
    if len(nz):
        w=wilcoxon(A[a],A[b],zero_method='wilcox',alternative='greater')
        ranks=rankdata(np.abs(nz));rplus=float(ranks[nz>0].sum());rminus=float(ranks[nz<0].sum());rbc=(rplus-rminus)/(rplus+rminus)
    else:w=type('X',(object,),{'statistic':0,'pvalue':1})();rbc=0
    rows.append({'from':a,'to':b,'mechanism':label,'median_relative_improvement_pct':float(np.median(relimp)),
                 'paired_win_rate':float((A[b]<A[a]).mean()),'wilcoxon_one_sided_p':float(w.pvalue),'rank_biserial_effect':rbc})
pd.DataFrame(rows).to_csv(OUT/'ablation_effect_sizes.csv',index=False)

# ---------- representation effects ----------
if not rep.empty:
    rows=[]
    for k in ('ILS','VNS','DFOX'):
        c=rep[rep.algorithm==f'C-{k}'].set_index(['instance','seed']);m=rep[rep.algorithm==f'M-{k}'].set_index(['instance','seed']);q=c.join(m,lsuffix='_c',rsuffix='_m')
        improvement=100*(q.score_c-q.score_m)/q.score_c
        w=wilcoxon(q.score_c,q.score_m,alternative='greater')
        rows.append({'search_family':k,'pairs':len(q),'market_tour_win_rate':float((q.score_m<q.score_c).mean()),
                     'median_objective_reduction_pct':float(np.median(improvement)),'mean_objective_reduction_pct':float(np.mean(improvement)),
                     'median_commodity_repeated_market_visits':float(np.median(q.route_market_repeats_c)),
                     'median_market_tour_repeated_market_visits':float(np.median(q.route_market_repeats_m)),
                     'wilcoxon_one_sided_p':float(w.pvalue)})
    pd.DataFrame(rows).to_csv(OUT/'representation_effects.csv',index=False)

# ---------- structural descriptors of PANCAKE instances ----------
def inst_metrics(path):
    d=json.loads(Path(path).read_text());coords=np.array(d['coords'],float);cands=d['candidates'];sets=[set(int(a) for a,_ in x) for x in cands]
    pairs=[]
    for i in range(len(sets)):
        for j in range(i+1,len(sets)):
            u=len(sets[i]|sets[j]);pairs.append(len(sets[i]&sets[j])/u if u else 0)
    cvs=[];conf=[]
    for rows in cands:
        prices=np.array([float(b) for _,b in rows]);cvs.append(float(prices.std()/max(1e-9,prices.mean())))
        ds=np.array([math.hypot(*coords[int(a)]) for a,_ in rows])
        if len(rows)>=3 and np.std(ds)>1e-9 and np.std(prices)>1e-9:
            conf.append(float(spearmanr(prices,ds).statistic))
    return {'instance':d['name'],'family':d['family'],'n_products':len(cands),'n_nodes':len(coords),'avg_candidates':np.mean([len(x) for x in cands]),
            'source_overlap_jaccard':np.mean(pairs) if pairs else 0,'price_cv':np.mean(cvs),'price_distance_spearman':np.nanmean(conf) if conf else np.nan,
            'coord_radius_mean':float(np.mean(np.linalg.norm(coords,axis=1))),'shared_node_ratio':1-len(set().union(*sets))/max(1,sum(len(s) for s in sets))}
metrics=[]
for p in sorted((ROOT/'ResearchBenchmark'/'meta_datasets').glob('*.json')):metrics.append(inst_metrics(p))
met=pd.DataFrame(metrics);met.to_csv(OUT/'instance_structure_metrics.csv',index=False)

# algorithm-vs-ILS structural correlations: exploratory N=10
inst=main.groupby(['instance','family','algorithm'],as_index=False).score.median();wide=inst.pivot(index=['instance','family'],columns='algorithm',values='score').reset_index().merge(met,on=['instance','family'])
corrows=[]
for a in [x for x in algs if x!='ILS-PA']:
    wide[f'{a}_gap']=100*(wide[a]-wide['ILS-PA'])/wide['ILS-PA']
    for metric in ['source_overlap_jaccard','price_cv','price_distance_spearman','coord_radius_mean','shared_node_ratio']:
        z=wide[[f'{a}_gap',metric]].dropna();sp=spearmanr(z[f'{a}_gap'],z[metric])
        corrows.append({'algorithm':a,'metric':metric,'n':len(z),'spearman_rho':float(sp.statistic),'p_value':float(sp.pvalue)})
pd.DataFrame(corrows).to_csv(OUT/'exploratory_structure_correlations.csv',index=False)

# FOX conditional profile
fox=[]
for fam,q0 in main.groupby('family'):
    q=q0[q0.algorithm.isin(['DFOX-APNS','ILS-PA'])].pivot_table(index=['instance','seed'],columns='algorithm',values=['score','rpd_pct','conv_auc_rpd']).dropna()
    fox.append({'family':fam,'dfox_median_rpd':float(q['rpd_pct']['DFOX-APNS'].median()),'ils_median_rpd':float(q['rpd_pct']['ILS-PA'].median()),
                'dfox_win_rate_vs_ils':float((q['score']['DFOX-APNS']<q['score']['ILS-PA']).mean()),
                'median_relative_score_gap_vs_ils_pct':float(np.median((q['score']['DFOX-APNS']-q['score']['ILS-PA'])/q['score']['ILS-PA']*100)),
                'dfox_median_auc':float(q['conv_auc_rpd']['DFOX-APNS'].median()),'ils_median_auc':float(q['conv_auc_rpd']['ILS-PA'].median())})
pd.DataFrame(fox).to_csv(OUT/'fox_conditional_profile.csv',index=False)


# ---------- budget-to-quality from median convergence ----------
conv=pd.read_csv(RES/'main_convergence.csv')
bt=[]
for a,q in conv.groupby('algorithm'):
    row={'algorithm':a}
    for t in (30,20,15,10,5):
        z=q[q.median_rpd_pct<=t]
        row[f'evals_to_median_rpd_le_{t}']=int(z.evals.iloc[0]) if len(z) else np.nan
    bt.append(row)
budget_target=pd.DataFrame(bt)
budget_target.to_csv(OUT/'budget_to_quality.csv',index=False)

# ---------- figures ----------
# family heatmap
mat=family.pivot(index='algorithm',columns='family',values='median_rpd').loc[sorted(algs,key=lambda a:main[main.algorithm==a].rpd_pct.median())]
fig,ax=plt.subplots(figsize=(10,5.6));im=ax.imshow(mat.values,aspect='auto');ax.set_xticks(range(len(mat.columns)),[x.replace('_','\n') for x in mat.columns],fontsize=8);ax.set_yticks(range(len(mat.index)),mat.index,fontsize=8)
for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):ax.text(j,i,f'{mat.iloc[i,j]:.1f}',ha='center',va='center',fontsize=7)
ax.set_title('Conditional performance: median RPD (%) by landscape family');fig.colorbar(im,ax=ax,label='Median RPD (%)');fig.tight_layout();fig.savefig(FIG/'family_interaction_heatmap.png',dpi=220);plt.close(fig)

# win matrix
fig,ax=plt.subplots(figsize=(7.8,6.8));im=ax.imshow(win.values,vmin=0,vmax=1);ax.set_xticks(range(len(algs)),algs,rotation=55,ha='right',fontsize=7);ax.set_yticks(range(len(algs)),algs,fontsize=7)
for i in range(len(algs)):
    for j in range(len(algs)):ax.text(j,i,f'{win.iloc[i,j]:.2f}',ha='center',va='center',fontsize=6)
ax.set_title('Paired probability that row algorithm beats column algorithm');fig.colorbar(im,ax=ax,label='Win probability');fig.tight_layout();fig.savefig(FIG/'pairwise_win_probability.png',dpi=220);plt.close(fig)

# performance profile
prof=pd.read_csv(OUT/'performance_profile.csv');fig,ax=plt.subplots(figsize=(8,5.2))
for a in sorted(algs,key=lambda x:main[main.algorithm==x].rpd_pct.median()):
    q=prof[prof.algorithm==a];ax.plot(q.tau,q.fraction_within_tau,label=a,linewidth=1.6)
ax.set_xlabel(r'Performance ratio $\tau$ to paired best');ax.set_ylabel('Fraction of paired runs');ax.set_ylim(0,1.02);ax.grid(True,alpha=.25);ax.legend(ncol=2,fontsize=7);ax.set_title('Empirical performance profile');fig.tight_layout();fig.savefig(FIG/'performance_profile.png',dpi=220);plt.close(fig)

# robustness median/p90
rr=rob.sort_values('median_rpd');x=np.arange(len(rr));fig,ax=plt.subplots(figsize=(9,4.8));ax.bar(x-.18,rr.median_rpd,width=.36,label='Median RPD');ax.bar(x+.18,rr.q90_rpd,width=.36,label='90th percentile RPD');ax.set_xticks(x,rr.algorithm,rotation=45,ha='right',fontsize=8);ax.set_ylabel('RPD (%)');ax.set_title('Central performance and failure-tail robustness');ax.legend();fig.tight_layout();fig.savefig(FIG/'robustness_tail.png',dpi=220);plt.close(fig)

if not rep.empty:
    re=pd.read_csv(OUT/'representation_effects.csv');fig,ax=plt.subplots(figsize=(7.2,4.5));ax.bar(re.search_family,re.median_objective_reduction_pct);ax.set_ylabel('Median objective reduction (%)');ax.set_title('Benefit of market-tour representation over commodity-centric encoding');
    for i,v in enumerate(re.median_objective_reduction_pct):ax.text(i,v+1,f'{v:.1f}%',ha='center',fontsize=9)
    fig.tight_layout();fig.savefig(FIG/'representation_effect.png',dpi=220);plt.close(fig)


# budget-to-quality figure for 10% and 20% median RPD
bq=budget_target.sort_values('evals_to_median_rpd_le_20');fig,ax=plt.subplots(figsize=(8.5,4.8));x=np.arange(len(bq));
ax.bar(x-.18,bq.evals_to_median_rpd_le_20,width=.36,label='Median RPD <=20%');ax.bar(x+.18,bq.evals_to_median_rpd_le_10.fillna(1250),width=.36,label='Median RPD <=10% (1250 = not reached)');
ax.set_xticks(x,bq.algorithm,rotation=45,ha='right',fontsize=8);ax.set_ylabel('Objective evaluations');ax.set_ylim(0,1300);ax.set_title('Budget-to-quality under a 1,200-FE cap');ax.legend(fontsize=8);fig.tight_layout();fig.savefig(FIG/'budget_to_quality.png',dpi=220);plt.close(fig)

print('wrote mechanism-analysis tables and figures')
