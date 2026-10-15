"""Reference values published on the official TPPLIB site.

Current bundled table: Class 3 (EEuclideo) exact OPT values for the 100 official
instances with 50..250 markets and 50/100/150/200 products.  Values are transcribed
from the official `class3.pdf` table linked by Jorge Riera-Ledesma's TPPLIB site.

The table is metadata only; no TPPLIB instance data are redistributed here.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import csv


@dataclass(frozen=True)
class ReferenceValue:
    instance: str
    markets: int
    products: int
    sample: int
    markets_in_opt: int
    value: float
    status: str = "OPT"
    source: str = "TPPLIB official Class 3 table"


# (markets, products): [(|M*|, OPT) x five correlated instances]
_CLASS3 = {
(50,50): [(9,1856),(9,1070),(10,1553),(7,1394),(3,1536)],
(50,100): [(13,2397),(12,2138),(11,1852),(16,3093),(13,2603)],
(50,150): [(16,2784),(12,2137),(15,2308),(15,2524),(17,3150)],
(50,200): [(20,3354),(16,2397),(12,2319),(17,2858),(18,3575)],
(100,50): [(10,1468),(8,971),(11,1623),(11,1718),(12,2494)],
(100,100): [(17,2121),(14,1906),(14,1822),(10,1649),(16,2925)],
(100,150): [(15,2195),(17,2806),(19,2257),(20,2625),(19,3150)],
(100,200): [(11,1883),(25,3077),(24,2791),(20,3409),(19,2732)],
(150,50): [(13,1658),(8,1383),(8,821),(11,1676),(13,1823)],
(150,100): [(18,1717),(12,1798),(17,1959),(15,1609),(15,1585)],
(150,150): [(20,1669),(25,2526),(20,2456),(17,1761),(19,2355)],
(150,200): [(20,1760),(25,2312),(26,2594),(16,1889),(23,2472)],
(200,50): [(14,1102),(7,607),(7,530),(10,908),(12,1067)],
(200,100): [(13,949),(19,2271),(14,1611),(18,1799),(29,3161)],
(200,150): [(17,1730),(28,2745),(21,1861),(24,2460),(19,2079)],
(200,200): [(19,1736),(23,2352),(24,2505),(21,3314),(24,2427)],
(250,50): [(7,533),(11,1103),(13,1295),(14,1553),(6,1142)],
(250,100): [(12,2447),(13,932),(18,1361),(17,1759),(15,1708)],
(250,150): [(16,1168),(23,2205),(16,1582),(19,2636),(16,2121)],
(250,200): [(21,1677),(26,2787),(26,3555),(18,2432),(19,2771)],
}

# Larger/open Class-3 instances require literature BKS rather than an OPT claim.
# The 2018 MAX-MIN Ant System study reports a new best value 1455 for
# EEuclideo.350.150.1; this value is therefore stored explicitly as BKS.
_LARGE_BKS = {
    "EEuclideo.350.150.1": ReferenceValue(
        "EEuclideo.350.150.1", 350, 150, 1, -1, 1455.0,
        status="BKS",
        source="Skinderowicz 2018 MMAS U-TPP study (ICCCI), best-known value 1455",
    ),
}


def all_class3() -> list[ReferenceValue]:
    out=[]
    for (m,k), vals in sorted(_CLASS3.items()):
        for sample, (mstar,opt) in enumerate(vals,1):
            out.append(ReferenceValue(f"EEuclideo.{m}.{k}.{sample}",m,k,sample,mstar,float(opt)))
    return out


def normalize_name(name: str) -> str:
    # TPPLIB instance IDs contain multiple dots (e.g. EEuclideo.350.150.1).
    # pathlib.Path.stem would incorrectly drop the final sample ID as a suffix.
    n=Path(name).name
    return n[:-4] if n.lower().endswith('.tpp') else n


def lookup(name: str) -> ReferenceValue | None:
    target=normalize_name(name).lower()
    for r in all_class3():
        if r.instance.lower()==target:
            return r
    for r in _LARGE_BKS.values():
        if r.instance.lower()==target:
            return r
    return None


def gap_percent(value: float, ref: ReferenceValue) -> float:
    return 100.0*(float(value)-ref.value)/ref.value


def export_csv(path: str|Path) -> None:
    rows=all_class3(); path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['instance','markets','products','sample','markets_in_opt','reference_value','status','source'])
        for r in rows:w.writerow([r.instance,r.markets,r.products,r.sample,r.markets_in_opt,r.value,r.status,r.source])

if __name__=='__main__':
    export_csv(Path(__file__).with_name('class3_reference_values.csv'))
    print(f"Exported {len(all_class3())} official Class-3 exact reference values")
