"""Small development-only screen for DFOX-APNS population size.

The reported test maps are indices 1-2. This script uses disjoint indices 3-4
from the same five landscape generators, so the selected population size is not
chosen by repeatedly looking at the final reported test table.
"""
from __future__ import annotations
import csv, json, statistics
from pathlib import Path
from meta_study import generate_problem
from algorithms.dfox_apns import run_dfox_apns

ROOT=Path(__file__).resolve().parent
DEV=ROOT/'dev_datasets'; OUT=ROOT/'meta_results'
FAMILIES=['uniform','clustered','price_distance_conflict','shared_hubs','deceptive_groups']
POPS=[12,16,18,20,24]

def main():
    DEV.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
    rows={p:[] for p in POPS}
    for fam in FAMILIES:
        for idx in (3,4):
            problem=generate_problem(fam,idx,n=16)
            payload={'name':problem.name,'family':problem.family,'unit_cost':problem.unit_cost,
                     'coords':problem.coords,'candidates':problem.candidates}
            (DEV/f'{problem.name}.json').write_text(json.dumps(payload),encoding='utf-8')
            for k in range(3):
                seed=10007*k+77
                vals={pop:run_dfox_apns(problem,seed,1200,npop=pop).score for pop in POPS}
                case_best=min(vals.values())
                for pop,v in vals.items(): rows[pop].append(100*(v-case_best)/case_best)
    out=[]
    for pop,arr in rows.items():
        out.append({'fox_agents':pop,'median_dev_relative_gap_pct':statistics.median(arr),
                    'mean_dev_relative_gap_pct':statistics.fmean(arr)})
    out.sort(key=lambda x:(x['median_dev_relative_gap_pct'],x['mean_dev_relative_gap_pct']))
    with (OUT/'fox_population_screen.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=out[0].keys());w.writeheader();w.writerows(out)
    print(out)

if __name__=='__main__': main()
