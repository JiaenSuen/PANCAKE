"""Download the official TPPLIB Class-3 archive from Jorge Riera-Ledesma's site.

Network access is intentionally explicit. The archive is not redistributed in PANCAKE.
Run this script on a machine with Internet access, then point run_market_tour_benchmark.py
at the extracted directory.
"""
from __future__ import annotations
import argparse, hashlib, io, urllib.request, zipfile
from pathlib import Path

URLS=[
    'https://webpages.ull.es/users/jriera/TPPLIB/SymmetricEuclideanLaporteRieraSalazar.zip',
    'https://jriera.webs.ull.es/TPPLIB/SymmetricEuclideanLaporteRieraSalazar.zip',
]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='Research/01_TPP_Benchmark/official_data/class3');args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    data=None; last=None
    for url in URLS:
        try:
            print('Downloading official TPPLIB Class 3 archive from:',url)
            req=urllib.request.Request(url,headers={'User-Agent':'PANCAKE-research/1.0'})
            data=urllib.request.urlopen(req,timeout=60).read(); break
        except Exception as e:
            last=e; print('  failed:',e)
    if data is None:
        raise RuntimeError(f'Could not download official TPPLIB archive from known mirrors: {last}')
    print('bytes:',len(data),'sha256:',hashlib.sha256(data).hexdigest())
    with zipfile.ZipFile(io.BytesIO(data)) as z:z.extractall(out)
    files=list(out.rglob('*.tpp'));print('extracted .tpp files:',len(files),'to',out)

if __name__=='__main__':main()
