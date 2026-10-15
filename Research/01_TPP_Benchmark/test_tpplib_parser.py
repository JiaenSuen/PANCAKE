from pathlib import Path
import importlib.util
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('tpplib_parser',HERE/'tpplib_parser.py')
mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)

inst=mod.parse_tpplib(HERE/'fixtures'/'sample_5x3.tpp')
assert inst.dimension==5
assert len(inst.demands)==3
assert len(inst.offers)==5
p=inst.to_pancake_problem()
assert len(p.coords)==4
assert len(p.candidates)==3
assert p.return_to_depot is True
assert p.depot_index==4
assert all(p.candidates)
print('TPPLIB parser fixture: PASS')
