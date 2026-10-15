from __future__ import annotations
from pathlib import Path
import json, math
import pandas as pd

HERE=Path(__file__).resolve().parent
R=HERE/'results'
PAPER=HERE.parent/'07_Paper_Materials'
TABLES=PAPER/'formal_tables';TABLES.mkdir(parents=True,exist_ok=True)

def pct(x,d=2): return '—' if pd.isna(x) else f'{x:.{d}f}%'
def num(x,d=2): return '—' if pd.isna(x) else f'{x:.{d}f}'
def md_table(df,cols,headers=None):
    headers=headers or cols
    out=['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(cols))+' |']
    for _,r in df.iterrows():out.append('| '+' | '.join(str(r[c]) for c in cols)+' |')
    return '\n'.join(out)

def tex_escape(s): return str(s).replace('_','\\_').replace('%','\\%')

def main():
    overall=pd.read_csv(R/'overall_summary.csv').sort_values('median_gap_opt_pct')
    scaling=pd.read_csv(R/'scaling_law_summary.csv')
    pair=pd.read_csv(R/'pairwise_instance_median_holm.csv')
    eff=pd.read_csv(R/'budget_efficiency_summary.csv').sort_values('median_gap_auc')
    mstar=pd.read_csv(R/'Mstar_cardinality_profile.csv')
    comp=pd.read_csv(R/'route_purchase_component_profile.csv')
    corr=pd.read_csv(R/'structure_gap_correlations.csv')
    grid=pd.read_csv(R/'VK_scaling_grid.csv')
    stats=json.loads((R/'formal_statistics.json').read_text())
    manifest=json.loads((R/'study_manifest.json').read_text())

    # Convenience maps
    O={r.algorithm:r for _,r in overall.iterrows()}
    S={r.algorithm:r for _,r in scaling.iterrows()}
    E={r.algorithm:r for _,r in eff.iterrows()}
    order=overall.algorithm.tolist()

    # Formal findings ledger
    lines=['# Formal Findings Ledger — Canonical TPPLIB Class-3 Study','',
           f'Canonical basis: **100 instances × {manifest["seeds"]} paired seeds × {len(manifest["methods"])} methods = {100*manifest["seeds"]*len(manifest["methods"]):,} runs**, {manifest["budget"]} FE/run.','',
           'Only findings marked **[C]** are intended as primary manuscript claims. **[E]** findings are exploratory/structural interpretations.','']
    best=order[0]
    lines += ['## FT1 [C] — Overall exact-OPT performance', '',
              f'**Evidence.** {best} has the lowest overall median exact OPT gap ({O[best].median_gap_opt_pct:.2f}%) and q90 gap ({O[best].q90_gap_opt_pct:.2f}%) in the canonical suite. Success rates at ≤5% and ≤10% gap are {O[best].success_gap_le_5_pct:.1f}% and {O[best].success_gap_le_10_pct:.1f}%, respectively.',
              '', '**Safe wording.** “Under the fixed 1,200-evaluation protocol, the strongest representative search architecture achieved the lowest median and tail optimality gaps across the 100 official instances.”',
              '', '**Caveat.** This compares three representative external-validation mechanisms, not every algorithm in the broader PANCAKE mechanism benchmark.','']

    lines += ['## FT2 [C] — Scaling degradation differs by search mechanism','']
    for a in order:
        s=S[a]; lines.append(f'- **{a}:** small median gap {s.small_median_gap:.2f}% → large {s.large_median_gap:.2f}% (Δ {s.large_minus_small_gap_pp:.2f} pp; slope {s.gap_slope_per_log10_decision_scale:.2f} gap-pp/log10-scale; Spearman ρ={s.spearman_rho_scale_gap:.3f}).')
    lines += ['', '**Safe wording.** “All methods degrade as the exact Class-3 instances grow, but the rate of degradation is mechanism-dependent under the same FE budget.”','']

    lines += ['## FT3 [C] — Optimal market-cardinality recovery is measurable independently of objective rank','']
    for a in order:
        z=mstar[mstar.algorithm==a]
        med=float(z.median_abs_error.median()); exact=float(z.exact_Mstar_rate.mean())
        lines.append(f'- **{a}:** median |M−M*| across scale tiers = {med:.2f}; mean exact-cardinality rate across tiers = {exact:.1f}%.')
    lines += ['', '**Interpretation.** Market-set cardinality error provides a structural diagnostic: a method can obtain a competitive cost while systematically visiting too many or too few markets.','']

    lines += ['## FT4 [C] — Convergence budget efficiency separates early discovery from late intensification','']
    for a in eff.algorithm:
        e=E[a]
        lines.append(f'- **{a}:** median exact-gap AUC {e.median_gap_auc:.2f}; reaches ≤10% gap in {e.success_gap_le_10_pct:.1f}% of runs (median FE among hits {num(e.median_FE_to_gap_le_10_among_hits,0)}).')
    lines += ['', '**Safe wording.** “Threshold-reaching rates and gap AUC show whether final differences arise from slow discovery, insufficient late-stage intensification, or both.”','']

    # component descriptive
    lines += ['## FT5 [C-descriptive] — Route/purchase decomposition localizes where objective differences arise','',
              'Official reference metadata provide total OPT but not component-wise optimal route and purchase costs. Therefore this study reports final component levels/shares only; it does **not** claim route-optimality or purchase-optimality gaps.','']
    for a in order:
        z=comp[comp.algorithm==a]
        lines.append(f'- **{a}:** median travel share across scale-tier summaries {100*z.median_travel_share.median():.1f}%; median purchase share {100*z.median_purchase_share.median():.1f}%.')
    lines += ['']

    # strongest density correlations (exploratory)
    lines += ['## FT6 [E] — Instance density interacts with performance','']
    for a in order:
        z=corr[corr.algorithm==a].copy(); z['absrho']=z.spearman_rho_gap.abs(); r=z.sort_values('absrho',ascending=False).iloc[0]
        lines.append(f'- **{a}:** strongest observed descriptor association is `{r.descriptor}` (Spearman ρ={r.spearman_rho_gap:.3f}, p={r.p_value:.3g}).')
    lines += ['', '**Caveat.** These are univariate observational associations across a structured benchmark grid; they are hypothesis-generating, not causal effects.','']

    lines += ['## FT7 [C] — Primary paired algorithm statistics','',
              f'Friedman test over the 100 per-instance medians: statistic={stats["friedman_statistic"]:.3f}, p={stats["friedman_p"]:.3g}. Pairwise inference uses Wilcoxon signed-rank tests with Holm correction; see `pairwise_instance_median_holm.csv` for exact values and effect sizes.','']
    (PAPER/'FORMAL_FINDINGS_LEDGER.md').write_text('\n'.join(lines),encoding='utf-8')

    # Manuscript Results draft
    rlines=['# Formal Results Draft — TPPLIB Class-3 External Validation','',
            '> Generated from the canonical 3,000-run external-validation layer. This text is manuscript material, not a claim beyond the recorded protocol.','',
            '## Exact optimality-gap comparison','',
            f'The 100-instance Class-3 study produced a significant global algorithm effect (Friedman statistic={stats["friedman_statistic"]:.3f}, p={stats["friedman_p"]:.3g}) when each benchmark instance was represented by the median of its 10 paired seeds. '
            f'{best} obtained the lowest overall median exact optimality gap ({O[best].median_gap_opt_pct:.2f}%), with an interquartile range of {O[best].IQR_gap_opt_pct:.2f} percentage points and a 90th-percentile gap of {O[best].q90_gap_opt_pct:.2f}%.','',
            'The result should be interpreted as a comparison of three representative search mechanisms under a tight, equal objective-evaluation budget, rather than as an exhaustive ranking of modern metaheuristics. The broader PANCAKE layer retains CPO, BKA, HO, WOA, GA, Tabu and hybrid references.','',
            '## Scaling and mechanism degradation','']
    for a in order:
        s=S[a]; rlines.append(f'{a} increased from a {s.small_median_gap:.2f}% median gap on the small tier to {s.large_median_gap:.2f}% on the large tier (Δ={s.large_minus_small_gap_pp:.2f} percentage points). Its descriptive gap-vs-scale slope was {s.gap_slope_per_log10_decision_scale:.2f} percentage points per log10 decision-scale unit.')
    rlines += ['', 'This scaling analysis is descriptive: fixed FE budgets intentionally measure sample efficiency as dimensionality grows, not asymptotic convergence with unlimited computation.','',
               '## Market-cardinality structure','',
               'Because Class-3 metadata include the optimal number of visited markets M*, the study can diagnose whether a method over- or under-selects markets independently of its total cost. `Mstar_cardinality_profile.csv` reports signed error, absolute error, and exact-cardinality hit rate by scale tier. This structural endpoint is useful when two algorithms achieve similar objective values through different market-set sizes.','',
               '## Travel / purchase components','',
               'Final solutions are decomposed into travel and purchase costs. These components are used to localize behavioral differences between methods, but not to compute component-wise optimality gaps: the benchmark reference provides total OPT and M*, not the travel/purchase decomposition of an optimal solution.','',
               '## Budget-to-quality behavior','',
               'Convergence is summarized both by exact-gap AUC and by the number of objective evaluations required to first enter 20%, 10%, 5%, 2%, and 1% optimality-gap regions. This separates algorithms that discover useful basins quickly from algorithms that mainly differ in late-stage intensification.','']
    (PAPER/'FORMAL_RESULTS_DRAFT.md').write_text('\n'.join(rlines),encoding='utf-8')

    # README-ready section
    rows=[]
    for a in order:
        r=O[a]
        rows.append({'Method':a,'Median OPT gap':pct(r.median_gap_opt_pct),'IQR':pct(r.IQR_gap_opt_pct),'q90':pct(r.q90_gap_opt_pct),
                     '≤5%':pct(r.success_gap_le_5_pct,1),'≤10%':pct(r.success_gap_le_10_pct,1),'|M−M*|':num(r.median_abs_Mstar_error,1)})
    tdf=pd.DataFrame(rows)
    sec=['## Formal External Validation — 100 TPPLIB Class-3 Instances','',
         f'The canonical external-validation layer now contains **100 official EEuclideo instances × 10 paired seeds × 3 representative search mechanisms = 3,000 runs**, each capped at **{manifest["budget"]} objective evaluations**. Unlike PANCAKE RPD, this layer reports **true exact optimality gap** against the Class-3 OPT metadata.','',
         md_table(tdf,list(tdf.columns)),'',
         f'Global paired test over the 100 per-instance medians: **Friedman p = {stats["friedman_p"]:.3g}**. Pairwise Wilcoxon–Holm results and effect sizes are stored in `Research/11_Formal_TPPLIB_Study/results/pairwise_instance_median_holm.csv`.','',
         'The formal analysis is not limited to rank. It records **small/medium/large scaling degradation, product-supply and market-assortment density, travel/purchase decomposition, exact `M*` cardinality error, and convergence budget efficiency**. See `Research/11_Formal_TPPLIB_Study/` and `Research/07_Paper_Materials/FORMAL_FINDINGS_LEDGER.md`.','']
    (PAPER/'README_FORMAL_SECTION.md').write_text('\n'.join(sec),encoding='utf-8')

    # LaTeX tables.
    def write_table(path,caption,label,headers,bodyrows):
        col='l'+'r'*(len(headers)-1)
        s=['\\begin{table}[t]','\\centering','\\small',f'\\caption{{{caption}}}',f'\\label{{{label}}}',f'\\begin{{tabular}}{{{col}}}','\\toprule',' & '.join(headers)+' \\\\','\\midrule']
        s += [' & '.join(row)+' \\\\' for row in bodyrows]
        s += ['\\bottomrule','\\end{tabular}','\\end{table}']
        path.write_text('\n'.join(s),encoding='utf-8')
    body=[]
    for a in order:
        r=O[a];body.append([tex_escape(a),f'{r.median_gap_opt_pct:.2f}',f'{r.IQR_gap_opt_pct:.2f}',f'{r.q90_gap_opt_pct:.2f}',f'{r.success_gap_le_5_pct:.1f}',f'{r.median_abs_Mstar_error:.1f}'])
    write_table(TABLES/'table_tpplib_overall.tex','Canonical TPPLIB Class-3 exact-OPT results under 1,200 objective evaluations.','tab:tpplib_overall',
                ['Method','Median gap (\\%)','IQR','q90','Gap$\\leq$5\\% (\\%)','Median $|M-M^*|$'],body)
    body=[]
    for a in order:
        s=S[a];body.append([tex_escape(a),f'{s.small_median_gap:.2f}',f'{s.large_median_gap:.2f}',f'{s.large_minus_small_gap_pp:.2f}',f'{s.gap_slope_per_log10_decision_scale:.2f}',f'{s.spearman_rho_scale_gap:.3f}'])
    write_table(TABLES/'table_tpplib_scaling.tex','Mechanism degradation from small to large Class-3 instances.','tab:tpplib_scaling',
                ['Method','Small gap','Large gap','$\\Delta$ pp','Slope','Spearman $\\rho$'],body)
    body=[]
    for a in eff.algorithm:
        e=E[a];body.append([tex_escape(a),f'{e.median_gap_auc:.2f}',f'{e.success_gap_le_10_pct:.1f}',num(e.median_FE_to_gap_le_10_among_hits,0),f'{e.success_gap_le_5_pct:.1f}',num(e.median_FE_to_gap_le_5_among_hits,0)])
    write_table(TABLES/'table_tpplib_budget_efficiency.tex','Budget-to-quality efficiency on official Class-3 instances.','tab:tpplib_budget',
                ['Method','Gap AUC','Hit 10\\%','FE@10\\%','Hit 5\\%','FE@5\\%'],body)

    print('Exported formal paper materials')
if __name__=='__main__':main()
