from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.table import Table

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'meta_results'
FIG=ROOT.parent/'docs'/'figures'
FIG.mkdir(parents=True,exist_ok=True)

runs=pd.read_csv(OUT/'runs.csv')
summary=pd.read_csv(OUT/'summary.csv')
exact_raw=pd.read_csv(OUT/'exact_small.csv')
exact=(exact_raw.groupby('algorithm',as_index=False)['median_exact_gap_pct'].median()
       .sort_values('median_exact_gap_pct'))
exact.to_csv(OUT/'exact_small_summary.csv',index=False)

ga_auc=float(summary.loc[summary.algorithm.eq('GA'),'median_conv_auc'].iloc[0])
summary['convergence_efficiency_vs_GA_x']=ga_auc/summary['median_conv_auc']
t1=(summary.merge(exact,on='algorithm',how='left').sort_values('mean_rank').reset_index(drop=True))
t1out=t1[['algorithm','median_rpd_pct','iqr_rpd_pct','success_5pct_pct','convergence_efficiency_vs_GA_x','mean_rank','median_exact_gap_pct']].copy()
t1out.columns=['Algorithm','Median RPD (%)','IQR RPD (pp)','Success@5% (%)','Conv. Eff. vs GA (×)','Mean Rank','Median Exact Gap (%)']
t1out.to_csv(OUT/'table1_algorithm_comparison.csv',index=False)
# compatibility compact table
compact=t1out[['Algorithm','Median RPD (%)','Success@5% (%)','Conv. Eff. vs GA (×)','Mean Rank']].copy()
compact.columns=['algorithm','median_rpd_pct','success_5pct_pct','convergence_efficiency_vs_GA_x','mean_rank']
compact.to_csv(OUT/'comparison_for_readme.csv',index=False)

reps=['uniform_01','clustered_01','price_distance_conflict_01','shared_hubs_01','deceptive_groups_01']
t2=(runs[runs.instance.isin(reps)].groupby(['algorithm','instance'],as_index=False)['score'].mean()
    .pivot(index='algorithm',columns='instance',values='score').reindex(t1.algorithm.tolist())[reps])
t2.columns=['U-01','C-01','PDC-01','SH-01','DG-01']; t2.index.name='Algorithm'
t2.reset_index().to_csv(OUT/'table2_map_mean_cost.csv',index=False)

# Paper-style PNG table.
d=t1out.copy()
for c in ['Median RPD (%)','IQR RPD (pp)','Median Exact Gap (%)']: d[c]=d[c].map(lambda x:f'{x:.2f}')
d['Success@5% (%)']=d['Success@5% (%)'].map(lambda x:f'{x:.1f}')
d['Conv. Eff. vs GA (×)']=d['Conv. Eff. vs GA (×)'].map(lambda x:f'{x:.2f}×')
d['Mean Rank']=d['Mean Rank'].map(lambda x:f'{x:.2f}')
labels=['Algorithm','Median\nRPD (%)','IQR RPD\n(pp)','Success\n@5% (%)','Conv. Eff.\nvs GA','Mean\nRank','Median Exact\nGap (%)']
fig,ax=plt.subplots(figsize=(13.5,5.8),dpi=220);fig.patch.set_facecolor('white');ax.set_facecolor('white');ax.axis('off')
ax.text(.5,.965,'TABLE I. METAHEURISTIC PERFORMANCE UNDER AN EQUAL OBJECTIVE-EVALUATION BUDGET',ha='center',va='top',fontsize=14,fontweight='bold',family='DejaVu Serif',transform=ax.transAxes)
ax.text(.5,.915,'10 algorithms × 30 paired test cases = 300 runs; equal objective-evaluation budget per run.',ha='center',va='top',fontsize=9.5,family='DejaVu Serif',transform=ax.transAxes)
tab=Table(ax,bbox=[.02,.075,.96,.78]); widths=[.20,.13,.12,.13,.14,.11,.17]
for j,(lab,w) in enumerate(zip(labels,widths)):
    c=tab.add_cell(0,j,w,.105,text=lab,loc='center',facecolor='white',edgecolor='black');c.set_linewidth(1);c.get_text().set_fontfamily('DejaVu Serif');c.get_text().set_fontsize(9);c.get_text().set_fontweight('bold')
for i,row in d.iterrows():
    for j,(val,w) in enumerate(zip(row.tolist(),widths)):
        c=tab.add_cell(i+1,j,w,.073,text=str(val),loc='center',facecolor='white',edgecolor='black');c.set_linewidth(.35);c.get_text().set_fontfamily('DejaVu Serif');c.get_text().set_fontsize(9)
        if row['Algorithm'] in ('DFOX-APNS','DWOA-AVNS') and j==0:c.get_text().set_fontweight('bold')
best={1:t1out['Median RPD (%)'].idxmin(),2:t1out['IQR RPD (pp)'].idxmin(),3:t1out['Success@5% (%)'].idxmax(),4:t1out['Conv. Eff. vs GA (×)'].idxmax(),5:t1out['Mean Rank'].idxmin(),6:t1out['Median Exact Gap (%)'].idxmin()}
for col,idx in best.items():tab[(idx+1,col)].get_text().set_fontweight('bold')
ax.add_table(tab)
ax.text(.02,.025,'RPD: relative percentage deviation from pooled best-known solution; exact gap uses a separate exact-solvable mini-suite.',ha='left',va='bottom',fontsize=8.5,family='DejaVu Serif',transform=ax.transAxes)
plt.savefig(FIG/'table1_algorithm_comparison.png',bbox_inches='tight',facecolor='white');plt.close(fig)
print('Exported report tables and figure.')
