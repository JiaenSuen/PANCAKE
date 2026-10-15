"""Generate reproducible EEuclideo-style U-TPP instances from the published Class-3 protocol.

Important: these are protocol-regenerated instances, not byte-identical copies of the
historical benchmark files formerly hosted at the ULL webpage.
"""
from __future__ import annotations
import csv, json, math, random
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Research'/'01_TPP_Benchmark'/'instances'
GUI=ROOT/'CSharp_GUI'/'PANCAKE_GUI_01'/'datasets'
EXP=ROOT/'Experiment_Maps'/'CSV'
OUT.mkdir(parents=True,exist_ok=True)


def generate(markets:int,products:int,idx:int,seed:int=20261011):
    rng=random.Random(seed+markets*10007+products*1009+idx)
    coords=[(rng.randint(0,1000),rng.randint(0,1000)) for _ in range(markets)]
    depot=(rng.randint(0,1000),rng.randint(0,1000))
    candidate=[]
    supplies=[[] for _ in range(markets)]
    for k in range(products):
        mk=rng.randint(1,max(1,markets-1)); ms=rng.sample(range(markets),mk); arr=[]
        for m in ms:
            price=rng.randint(0,500);arr.append((m,price));supplies[m].append((f'TPPItem{k+1:03d}',price))
        candidate.append(arr)
    all_xy=coords+[depot]
    dist=[[int(math.hypot(bx-ax,by-ay)) for bx,by in all_xy] for ax,ay in all_xy]
    name=f'eeuclideo_style_{markets}_{products}_{idx:02d}'
    payload={'name':name,'family':'tpp_eeuclideo_style','markets':markets,'products':products,'depot':depot,
             'coords':coords,'candidates':candidate,'distance_matrix':dist,'return_to_depot':True,
             'unit_cost':1.0,'provenance':'Regenerated from published Laporte et al. Class-3/EEuclideo protocol; not original benchmark bytes.'}
    (OUT/f'{name}.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    gui_name='research_tpp_'+name+'.csv'
    for target in (GUI/gui_name,EXP/gui_name):
        with target.open('w',newline='',encoding='utf-8') as f:
            w=csv.writer(f);w.writerow(['Node_Name','X','Y','Objects'])
            for m,(xy,items) in enumerate(zip(coords,supplies)):
                w.writerow([f'TPPM{m+1:03d}',xy[0],xy[1],';'.join(f'{k}:{v}' for k,v in items)])
    return name,gui_name


if __name__=='__main__':
    rows=[]
    for spec in [(50,50,1),(50,100,1)]:rows.append(generate(*spec))
    print('\n'.join(f'{a} -> {b}' for a,b in rows))
