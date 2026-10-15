"""Validate the minimal EEuclideo benchmark extraction and reference consistency."""
from pathlib import Path
import csv
from tpplib_parser import parse_tpplib

HERE=Path(__file__).resolve().parent
DATA=HERE/'official_data'/'EEuclideo'
BASE=DATA/'Baseline_EEuclideo.csv'
REF=HERE/'class3_reference_values.csv'

def read(path,key):
    with path.open(encoding='utf-8-sig',newline='') as f: return {r[key]:r for r in csv.DictReader(f)}

def main():
    b=read(BASE,'Instance'); r=read(REF,'instance')
    files=sorted(DATA.glob('EEuclideo.*.tpp'))
    parsed=0; errors=[]
    for p in files:
        try:
            x=parse_tpplib(p)
            if x.name not in b: errors.append(f'{p.name}: missing baseline')
            else: parsed+=1
        except Exception as e: errors.append(f'{p.name}: {e}')
    mismatch_opt=[]; mismatch_m=[]
    for name,row in b.items():
        if name not in r: continue
        if float(row['OPT'])!=float(r[name]['reference_value']): mismatch_opt.append(name)
        if int(row['M*'])!=int(r[name]['markets_in_opt']): mismatch_m.append(name)
    print(f'tpp_files={len(files)} parsed={parsed} errors={len(errors)}')
    print(f'baseline={len(b)} registry={len(r)} OPT_mismatch={len(mismatch_opt)} Mstar_mismatch={len(mismatch_m)}')
    if errors or mismatch_opt or mismatch_m: raise SystemExit(1)
if __name__=='__main__': main()
