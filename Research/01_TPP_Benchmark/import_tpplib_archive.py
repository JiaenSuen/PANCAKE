"""Validate and import a user-supplied TPPLIB archive without relabelling unrelated data."""
from __future__ import annotations
import argparse,zipfile
from pathlib import Path
from tpplib_parser import parse_tpplib

def main():
    ap=argparse.ArgumentParser();ap.add_argument('archive');ap.add_argument('--output',default=str(Path(__file__).resolve().parent/'official_data'/'class3'));args=ap.parse_args()
    arc=Path(args.archive);out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(arc) as z:
        names=[n for n in z.namelist() if n.lower().endswith('.tpp')]
        if not names:raise SystemExit('Archive contains no .tpp files; refusing to classify it as TPPLIB.')
        ok=0
        for n in names:
            data=z.read(n);target=out/Path(n).name;target.write_bytes(data)
            try:inst=parse_tpplib(target)
            except Exception:
                target.unlink(missing_ok=True);raise
            print(f'imported {inst.name}: DIMENSION={inst.dimension}, products={len(inst.demands)}');ok+=1
    print(f'imported {ok} validated .tpp files into {out}')
if __name__=='__main__':main()
