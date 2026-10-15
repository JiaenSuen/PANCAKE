"""Minimal TPPLIB reader for classical uncapacitated Traveling Purchaser instances.

TPPLIB extends TSPLIB with DEMAND_SECTION and OFFER_SECTION.  This parser is designed
as an adapter for PANCAKE research experiments, with explicit provenance and validation.
It supports coordinate-based EUC_2D data and explicit FULL_MATRIX edge weights.

The parser is intentionally conservative: unknown formats fail loudly instead of being
silently misinterpreted.  Market labels and product labels are accepted as 1-based IDs;
market 1 is treated as the depot by TPPLIB convention.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
from typing import Dict, List, Tuple


@dataclass
class TPPLibInstance:
    name: str
    dimension: int
    coords: Dict[int, Tuple[float, float]]
    demands: Dict[int, int]
    # market -> list[(product_id, cost, availability)]
    offers: Dict[int, List[Tuple[int, float, int]]]
    edge_weight_type: str = "EUC_2D"
    edge_weight_format: str = "FULL_MATRIX"
    explicit_weights: List[List[float]] | None = None
    depot_market: int = 1

    def distance_matrix(self) -> List[List[float]]:
        if self.explicit_weights is not None:
            return [row[:] for row in self.explicit_weights]
        if self.edge_weight_type.upper() != "EUC_2D":
            raise ValueError(f"Unsupported EDGE_WEIGHT_TYPE: {self.edge_weight_type}")
        ids = list(range(1, self.dimension + 1))
        missing = [i for i in ids if i not in self.coords]
        if missing:
            raise ValueError(f"Missing coordinates for market IDs: {missing[:5]}")
        # TPPLIB Class 3 (EEuclideo) is documented with truncated Euclidean travel costs.
        # Other generic EUC_2D files retain the TSPLIB nearest-integer convention.
        trunc = self.name.lower().startswith("eeuclideo") or self.edge_weight_type.upper() in {"EUC_2D_TRUNC", "TRUNC_2D"}
        def d(i, j):
            raw = math.hypot(self.coords[i][0]-self.coords[j][0], self.coords[i][1]-self.coords[j][1])
            return float(int(raw) if trunc else int(raw + 0.5))
        return [[d(i,j) for j in ids] for i in ids]

    def to_pancake_problem(self):
        """Convert to ResearchBenchmark.meta_study.Problem.

        Demand quantities >1 are currently rejected because PANCAKE's research genotype
        represents one acquisition decision per product.  This is correct for classical
        unit-demand U-TPP instances and prevents accidental misuse on capacitated variants.
        """
        # meta_study.py historically imports its sibling `algorithms` as a top-level module,
        # so make both the project root and ResearchBenchmark directory visible when
        # this adapter is executed directly from Research/.
        import sys
        project_root = Path(__file__).resolve().parents[2]
        rb_dir = project_root / "ResearchBenchmark"
        for entry in (str(project_root), str(rb_dir)):
            if entry not in sys.path:
                sys.path.insert(0, entry)
        from ResearchBenchmark.meta_study import Problem

        for pid, q in self.demands.items():
            if q != 1:
                raise ValueError(f"Product {pid} has demand {q}; current adapter supports unit-demand U-TPP only.")

        product_ids = sorted(self.demands)
        prod_index = {pid: i for i, pid in enumerate(product_ids)}
        candidates: List[List[Tuple[int, float]]] = [[] for _ in product_ids]
        # PANCAKE node indices exclude the depot. TPPLIB market IDs 2..DIMENSION map to 0..M-1.
        market_ids = [m for m in range(1, self.dimension + 1) if m != self.depot_market]
        node_index = {m: i for i, m in enumerate(market_ids)}

        for market, rows in self.offers.items():
            if market == self.depot_market:
                continue
            if market not in node_index:
                raise ValueError(f"Offer references unknown market {market}")
            for pid, cost, availability in rows:
                if pid not in prod_index or availability <= 0:
                    continue
                candidates[prod_index[pid]].append((node_index[market], float(cost)))

        missing = [product_ids[i] for i, c in enumerate(candidates) if not c]
        if missing:
            raise ValueError(f"Products without a feasible market offer: {missing[:10]}")

        full = self.distance_matrix()
        ordered_full_ids = market_ids + [self.depot_market]
        matrix = [[full[a-1][b-1] for b in ordered_full_ids] for a in ordered_full_ids]
        coords = [self.coords.get(m, (0.0, 0.0)) for m in market_ids]
        return Problem(
            name=self.name,
            family="tpplib",
            coords=coords,
            candidates=candidates,
            unit_cost=1.0,
            return_to_depot=True,
            distance_matrix=matrix,
            depot_index=len(market_ids),
        )

    def to_market_tour_problem(self):
        """Convert an official unit-demand U-TPP instance to the classical market-tour representation.

        Unlike ``to_pancake_problem()``, this representation searches over a subset/order of markets.
        The purchasing plan is induced optimally for a fixed visited set. This is the canonical bridge
        used for TPPLIB experiments in the Research branch.
        """
        import sys
        here = Path(__file__).resolve().parent
        if str(here) not in sys.path:
            sys.path.insert(0, str(here))
        from market_tour import TPPProblem

        for pid, q in self.demands.items():
            if q != 1:
                raise ValueError(f"Product {pid} has demand {q}; market-tour adapter currently supports unit-demand U-TPP only.")

        product_ids = sorted(self.demands)
        prod_index = {pid: i for i, pid in enumerate(product_ids)}
        market_ids = [m for m in range(1, self.dimension + 1) if m != self.depot_market]
        market_index = {m: i for i, m in enumerate(market_ids)}
        offers_by_product = [[] for _ in product_ids]
        for market, rows in self.offers.items():
            if market == self.depot_market:
                continue
            if market not in market_index:
                raise ValueError(f"Offer references unknown market {market}")
            mi = market_index[market]
            for pid, cost, availability in rows:
                if pid in prod_index and availability > 0:
                    offers_by_product[prod_index[pid]].append((mi, float(cost)))
        missing = [product_ids[i] for i, rows in enumerate(offers_by_product) if not rows]
        if missing:
            raise ValueError(f"Products without a feasible market offer: {missing[:10]}")

        full = self.distance_matrix()
        ordered_ids = market_ids + [self.depot_market]
        matrix = [[float(full[a-1][b-1]) for b in ordered_ids] for a in ordered_ids]
        return TPPProblem(
            name=self.name, market_ids=market_ids, product_ids=product_ids,
            distance=matrix, depot_index=len(market_ids), offers_by_product=offers_by_product,
        )


def _header_value(line: str) -> Tuple[str, str] | None:
    if ":" in line:
        k, v = line.split(":", 1)
        return k.strip().upper(), v.strip()
    parts = line.split(None, 1)
    if len(parts) == 2 and parts[0].upper() in {
        "NAME", "TYPE", "DIMENSION", "EDGE_WEIGHT_TYPE", "EDGE_WEIGHT_FORMAT", "COMMENT"
    }:
        return parts[0].upper(), parts[1].strip()
    return None


def parse_tpplib(path: str | Path) -> TPPLibInstance:
    lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    header: Dict[str, str] = {}
    coords: Dict[int, Tuple[float, float]] = {}
    demands: Dict[int, int] = {}
    offers: Dict[int, List[Tuple[int, float, int]]] = {}
    weights_tokens: List[float] = []
    section = "HEADER"

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        upper = line.upper()
        normalized = upper[:-1].strip() if upper.endswith(":") else upper
        if normalized == "EOF":
            break
        if normalized in {"NODE_COORD_SECTION", "EDGE_WEIGHT_SECTION", "DEMAND_SECTION", "OFFER_SECTION"}:
            section = normalized
            continue

        if section == "HEADER":
            kv = _header_value(line)
            if kv:
                header[kv[0]] = kv[1]
            continue

        nums = line.replace(",", " ").split()
        if section == "NODE_COORD_SECTION":
            if len(nums) < 3:
                raise ValueError(f"Invalid NODE_COORD_SECTION row: {line}")
            coords[int(nums[0])] = (float(nums[1]), float(nums[2]))
        elif section == "EDGE_WEIGHT_SECTION":
            weights_tokens.extend(float(x) for x in nums)
        elif section == "DEMAND_SECTION":
            # First line may contain only the number of products.
            if len(nums) == 1:
                continue
            if len(nums) < 2:
                raise ValueError(f"Invalid DEMAND_SECTION row: {line}")
            demands[int(nums[0])] = int(float(nums[1]))
        elif section == "OFFER_SECTION":
            if len(nums) < 2:
                raise ValueError(f"Invalid OFFER_SECTION row: {line}")
            market = int(nums[0]); count = int(nums[1]); rest = nums[2:]
            if len(rest) != 3 * count:
                raise ValueError(f"OFFER_SECTION market {market}: expected {3*count} values, got {len(rest)}")
            rows=[]
            for i in range(count):
                pid = int(rest[3*i]); cost = float(rest[3*i+1]); avail = int(float(rest[3*i+2]))
                rows.append((pid, cost, avail))
            offers[market] = rows

    if "DIMENSION" not in header:
        raise ValueError("TPPLIB file is missing DIMENSION")
    dimension = int(header["DIMENSION"])
    explicit = None
    if weights_tokens:
        fmt = header.get("EDGE_WEIGHT_FORMAT", "FULL_MATRIX").upper()
        if fmt != "FULL_MATRIX":
            raise ValueError(f"Unsupported EDGE_WEIGHT_FORMAT: {fmt}")
        expected = dimension * dimension
        if len(weights_tokens) != expected:
            raise ValueError(f"Expected {expected} edge weights, got {len(weights_tokens)}")
        explicit = [weights_tokens[i*dimension:(i+1)*dimension] for i in range(dimension)]

    if not demands:
        raise ValueError("TPPLIB file has no parsed product demands")
    if not offers:
        raise ValueError("TPPLIB file has no parsed market offers")

    return TPPLibInstance(
        name=(header.get("NAME") or Path(path).stem),
        dimension=dimension,
        coords=coords,
        demands=demands,
        offers=offers,
        edge_weight_type=header.get("EDGE_WEIGHT_TYPE", "EUC_2D"),
        edge_weight_format=header.get("EDGE_WEIGHT_FORMAT", "FULL_MATRIX"),
        explicit_weights=explicit,
    )


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("instance")
    args = ap.parse_args()
    inst = parse_tpplib(args.instance)
    p = inst.to_pancake_problem()
    print(f"{inst.name}: markets={inst.dimension-1}, products={len(inst.demands)}, candidates={sum(map(len,p.candidates))}")
