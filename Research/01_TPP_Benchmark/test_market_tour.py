from pathlib import Path
import sys,tempfile
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from tpplib_parser import parse_tpplib
from market_tour import MarketTourSol,evaluate
from tpplib_bks import all_class3,lookup

FIX='''NAME: tiny\nTYPE: TPP\nDIMENSION: 4\nEDGE_WEIGHT_TYPE: EXPLICIT\nEDGE_WEIGHT_FORMAT: FULL_MATRIX\nEDGE_WEIGHT_SECTION\n0 2 3 1\n2 0 1 2\n3 1 0 2\n1 2 2 0\nDEMAND_SECTION\n2\n1 1\n2 1\nOFFER_SECTION\n1 0\n2 1 1 10 1\n3 1 2 10 1\n4 2 1 50 1 2 50 1\nEOF\n'''
with tempfile.TemporaryDirectory() as d:
    p=Path(d)/'tiny.tpp';p.write_text(FIX)
    x=parse_tpplib(p);tp=x.to_market_tour_problem()
    # internal markets correspond TPPLIB 2,3,4; tour 2->3 (indices 0,1): buy=20, depot route=1->2->3->1 = 2+1+3=6
    s=MarketTourSol([0,1]);assert evaluate(tp,s)==26
    assert s.purchase==20 and s.travel==6 and len(s.procurement)==2
assert len(all_class3())==100
assert lookup('EEuclideo.50.50.1.tpp').value==1856
print('market-tour representation + official reference metadata: OK')
