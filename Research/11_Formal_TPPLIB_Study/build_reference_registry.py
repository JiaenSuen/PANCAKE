from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / '01_TPP_Benchmark' / 'official_data' / 'EEuclideo'
OUT = Path(__file__).resolve().parent / 'results' / 'reference_registry.csv'
base = pd.read_csv(DATA / 'Baseline_EEuclideo.csv')

# Literature BKS explicitly reported in Bontoux's TPP chapter, Tables 3.3/3.4.
# These are open instances, so values are BKS rather than proven optima.
bks = {
    'EEuclideo.200.150.4': 2419,
    'EEuclideo.200.200.4': 2344,
    'EEuclideo.250.100.1': 1301,
    'EEuclideo.250.100.4': 1673,
    'EEuclideo.250.100.5': 1641,
    'EEuclideo.250.150.4': 1836,
    'EEuclideo.250.150.5': 1531,
    'EEuclideo.250.200.2': 2785,
    'EEuclideo.250.200.3': 1924,
    'EEuclideo.250.200.4': 2116,
    'EEuclideo.250.200.5': 1797,
}
rows=[]
for _,r in base.iterrows():
    inst=r['Instance']
    timeout_like = float(r['Sec']) >= 17000
    if inst in bks:
        status='literature_bks_open'
        ref=bks[inst]
        ref_m=None
        source='Bontoux thesis Ch.3 Tables 3.3/3.4 (DMD-ATA BKS)'
        note='Open instance; reference is a best-known solution, not a proven optimum.'
    elif timeout_like:
        # In the imported baseline, this row is the remaining long-running instance not
        # covered by the explicitly reported BKS-improvement table.
        status='open_reference_unverified'
        ref=None
        ref_m=None
        source='Imported Baseline_EEuclideo.csv only'
        note='Legacy exact-solver run reached ~5h limit; do not treat its OPT/M* fields as certified.'
    else:
        status='legacy_closed_candidate'
        ref=float(r['OPT'])
        ref_m=int(r['M*'])
        source='Imported Baseline_EEuclideo.csv; solver-completed record'
        note=('Consistent with the historical closed/open split and never beaten by the 3,000-run study. '
              'Retained as a closed-reference candidate, but primary paper claims remain reference-independent until official TPPLIB table is archived.')
    rows.append({
        'instance':inst,'V':int(r['V']),'K':int(r['K']),
        'reference_status':status,'reference_value':ref,'reference_market_count':ref_m,
        'legacy_value':float(r['OPT']),'legacy_market_count':int(r['M*']),
        'legacy_seconds':float(r['Sec']),'reference_source':source,'reference_note':note
    })
out=pd.DataFrame(rows)
out.to_csv(OUT,index=False)
print(out.reference_status.value_counts().to_string())
print('written',OUT)
