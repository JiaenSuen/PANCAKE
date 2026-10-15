"""Classical U-TPP market-tour + induced procurement representation.

This module deliberately separates the official TPPLIB representation from PANCAKE's
legacy item-order/source genotype.  A solution is a tour over a subset of markets.
For a fixed visited set, the unit-demand uncapacitated procurement plan is derived
exactly by choosing the cheapest visited offer for every product.

This is the natural representation for classical U-TPP and avoids duplicated visits to
the same market that can occur in an item-order genotype.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math
import random
from typing import Dict, Iterable, List, Sequence, Tuple


@dataclass
class TPPProblem:
    name: str
    market_ids: List[int]                  # excludes depot; internal index 0..m-1
    product_ids: List[int]
    distance: List[List[float]]            # market nodes followed by depot at depot_index
    depot_index: int
    # product index -> list[(market_index, price)]
    offers_by_product: List[List[Tuple[int, float]]]
    family: str = "tpplib"

    @property
    def n_markets(self) -> int:
        return len(self.market_ids)

    @property
    def n_products(self) -> int:
        return len(self.product_ids)


@dataclass
class MarketTourSol:
    tour: List[int]                         # distinct internal market indices
    score: float = math.inf
    travel: float = math.inf
    purchase: float = math.inf
    procurement: List[Tuple[int, int, float]] = field(default_factory=list)

    def clone(self) -> "MarketTourSol":
        return MarketTourSol(self.tour.copy(), self.score, self.travel, self.purchase, self.procurement.copy())


def derive_procurement(p: TPPProblem, tour: Sequence[int]) -> Tuple[float, List[Tuple[int, int, float]]]:
    """Return optimal unit-demand purchasing plan conditional on visited markets.

    Returns (purchase_cost, [(product_index, market_index, unit_price), ...]).
    Infeasible visited sets return (inf, []).
    """
    visited = set(tour)
    plan: List[Tuple[int, int, float]] = []
    total = 0.0
    for k, offers in enumerate(p.offers_by_product):
        feasible = [(price, m) for m, price in offers if m in visited]
        if not feasible:
            return math.inf, []
        price, m = min(feasible)
        total += float(price)
        plan.append((k, m, float(price)))
    return total, plan


def travel_cost(p: TPPProblem, tour: Sequence[int]) -> float:
    if not tour:
        return 0.0
    d = p.depot_index
    total = p.distance[d][tour[0]]
    for a, b in zip(tour, tour[1:]):
        total += p.distance[a][b]
    total += p.distance[tour[-1]][d]
    return float(total)


def evaluate(p: TPPProblem, s: MarketTourSol) -> float:
    # Enforce a simple tour: no repeated markets.
    if len(s.tour) != len(set(s.tour)) or any(m < 0 or m >= p.n_markets for m in s.tour):
        s.score = s.travel = s.purchase = math.inf
        s.procurement = []
        return s.score
    buy, plan = derive_procurement(p, s.tour)
    if not math.isfinite(buy):
        s.score = s.travel = s.purchase = math.inf
        s.procurement = []
        return s.score
    tr = travel_cost(p, s.tour)
    s.travel, s.purchase, s.procurement = tr, buy, plan
    s.score = tr + buy
    return s.score


def greedy_cover(p: TPPProblem, rng: random.Random) -> MarketTourSol:
    """Construct a feasible market subset with cost/coverage-aware insertion."""
    uncovered = set(range(p.n_products))
    selected: List[int] = []
    by_market: List[List[Tuple[int, float]]] = [[] for _ in range(p.n_markets)]
    for k, offers in enumerate(p.offers_by_product):
        for m, price in offers:
            by_market[m].append((k, price))

    while uncovered:
        best = None
        for m in range(p.n_markets):
            if m in selected:
                continue
            rows = [(k, pr) for k, pr in by_market[m] if k in uncovered]
            if not rows:
                continue
            # proxy = covered prices + depot access, normalized by newly covered products
            proxy = (sum(pr for _, pr in rows) + 0.35 * (p.distance[p.depot_index][m] + p.distance[m][p.depot_index])) / len(rows)
            proxy *= 1.0 + rng.uniform(-0.03, 0.03)
            if best is None or proxy < best[0]:
                best = (proxy, m, rows)
        if best is None:
            raise ValueError("No feasible cover exists for all products")
        _, m, rows = best
        selected.append(m)
        uncovered.difference_update(k for k, _ in rows)

    # nearest-neighbor route over selected markets
    tour: List[int] = []
    remaining = set(selected)
    cur = p.depot_index
    while remaining:
        nxt = min(remaining, key=lambda m: p.distance[cur][m])
        tour.append(nxt); remaining.remove(nxt); cur = nxt
    s = MarketTourSol(tour)
    evaluate(p, s)
    return s


def remove_redundant_markets(p: TPPProblem, s: MarketTourSol) -> MarketTourSol:
    """Greedy tour reduction: delete markets whose removal remains feasible and improves objective."""
    cur = s.clone(); evaluate(p, cur)
    improved = True
    while improved and len(cur.tour) > 1:
        improved = False
        best = cur
        for i in range(len(cur.tour)):
            cand = MarketTourSol(cur.tour[:i] + cur.tour[i+1:])
            evaluate(p, cand)
            if cand.score < best.score - 1e-12:
                best = cand
        if best is not cur:
            cur = best; improved = True
    return cur


def random_feasible(p: TPPProblem, rng: random.Random) -> MarketTourSol:
    s = greedy_cover(p, rng)
    # diversify with optional covered markets then shuffle
    available = [m for m in range(p.n_markets) if m not in s.tour]
    extra_n = min(len(available), rng.randrange(0, min(4, len(available)) + 1)) if available else 0
    if extra_n:
        s.tour.extend(rng.sample(available, extra_n))
    rng.shuffle(s.tour)
    evaluate(p, s)
    return remove_redundant_markets(p, s)


def op_two_opt(p: TPPProblem, s: MarketTourSol, rng: random.Random) -> None:
    if len(s.tour) >= 3:
        i, j = sorted(rng.sample(range(len(s.tour)), 2))
        s.tour[i:j+1] = reversed(s.tour[i:j+1])


def op_relocate(p: TPPProblem, s: MarketTourSol, rng: random.Random) -> None:
    if len(s.tour) >= 2:
        i, j = rng.sample(range(len(s.tour)), 2)
        x = s.tour.pop(i); s.tour.insert(j, x)


def op_drop(p: TPPProblem, s: MarketTourSol, rng: random.Random) -> None:
    if len(s.tour) > 1:
        del s.tour[rng.randrange(len(s.tour))]


def op_add(p: TPPProblem, s: MarketTourSol, rng: random.Random) -> None:
    rem = [m for m in range(p.n_markets) if m not in s.tour]
    if rem:
        m = rng.choice(rem)
        pos = rng.randrange(len(s.tour) + 1)
        s.tour.insert(pos, m)


def op_swap_market(p: TPPProblem, s: MarketTourSol, rng: random.Random) -> None:
    rem = [m for m in range(p.n_markets) if m not in s.tour]
    if s.tour and rem:
        s.tour[rng.randrange(len(s.tour))] = rng.choice(rem)


OPERATORS = ("two_opt", "relocate", "drop", "add", "swap_market")


def apply_operator(p: TPPProblem, s: MarketTourSol, rng: random.Random, op: str) -> None:
    {"two_opt": op_two_opt, "relocate": op_relocate, "drop": op_drop,
     "add": op_add, "swap_market": op_swap_market}[op](p, s, rng)
