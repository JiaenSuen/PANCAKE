from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Sol:
    """Coupled discrete solution: commodity visit order + source index per commodity."""
    order: List[int]
    src: List[int]
    score: float = math.inf
    dist: float = math.inf
    purchase: float = math.inf

    def clone(self) -> "Sol":
        return Sol(self.order.copy(), self.src.copy(), self.score, self.dist, self.purchase)


@dataclass
class RR:
    alg: str
    inst: str
    family: str
    seed: int
    score: float
    evals: int
    trace: List[Tuple[int, float]]


def evaluate(p, s: Sol) -> float:
    x0 = y0 = 0.0
    distance = 0.0
    purchase = 0.0
    for item in s.order:
        node, price = p.candidates[item][s.src[item]]
        x, y = p.coords[node]
        distance += math.hypot(x - x0, y - y0)
        purchase += price
        x0, y0 = x, y
    s.dist = distance
    s.purchase = purchase
    s.score = purchase + p.unit_cost * distance
    return s.score


def random_sol(p, rng: random.Random) -> Sol:
    order = list(range(len(p.candidates)))
    rng.shuffle(order)
    return Sol(order, [rng.randrange(len(c)) for c in p.candidates])


def swap(s: Sol, rng: random.Random) -> None:
    if len(s.order) > 1:
        i, j = rng.sample(range(len(s.order)), 2)
        s.order[i], s.order[j] = s.order[j], s.order[i]


def reverse(s: Sol, rng: random.Random) -> None:
    if len(s.order) > 1:
        i, j = sorted(rng.sample(range(len(s.order)), 2))
        s.order[i:j + 1] = reversed(s.order[i:j + 1])


def insert(s: Sol, rng: random.Random) -> None:
    if len(s.order) > 2:
        i, j = rng.sample(range(len(s.order)), 2)
        value = s.order.pop(i)
        s.order.insert(j, value)


def block_reloc(s: Sol, rng: random.Random) -> None:
    n = len(s.order)
    if n < 4:
        return
    i, j = sorted(rng.sample(range(n), 2))
    segment = s.order[i:j + 1]
    remaining = s.order[:i] + s.order[j + 1:]
    pos = rng.randrange(len(remaining) + 1)
    s.order = remaining[:pos] + segment + remaining[pos:]


def change_source(p, s: Sol, rng: random.Random, count: int = 1) -> None:
    n = len(s.src)
    for _ in range(count):
        demand = rng.randrange(n)
        m = len(p.candidates[demand])
        if m > 1:
            old = s.src[demand]
            z = rng.randrange(m - 1)
            s.src[demand] = z + (z >= old)


def joint_move(p, s: Sol, rng: random.Random) -> None:
    """Relocate one demand and reselect its source using a predecessor/successor proxy."""
    if len(s.order) < 2:
        return
    demand = rng.choice(s.order)
    old_pos = s.order.index(demand)
    s.order.pop(old_pos)
    new_pos = rng.randrange(len(s.order) + 1)
    s.order.insert(new_pos, demand)

    pos = s.order.index(demand)
    if pos == 0:
        prev = (0.0, 0.0)
    else:
        prev_d = s.order[pos - 1]
        prev_node = p.candidates[prev_d][s.src[prev_d]][0]
        prev = p.coords[prev_node]

    if pos == len(s.order) - 1:
        nxt = None
    else:
        next_d = s.order[pos + 1]
        next_node = p.candidates[next_d][s.src[next_d]][0]
        nxt = p.coords[next_node]

    best = (math.inf, s.src[demand])
    for source_idx, (node, price) in enumerate(p.candidates[demand]):
        x, y = p.coords[node]
        value = price + p.unit_cost * math.hypot(x - prev[0], y - prev[1])
        if nxt is not None:
            value += p.unit_cost * math.hypot(nxt[0] - x, nxt[1] - y)
        if value < best[0]:
            best = (value, source_idx)
    s.src[demand] = best[1]


def ox(a, b, rng: random.Random):
    n = len(a)
    i, j = sorted(rng.sample(range(n), 2))
    child = [None] * n
    child[i:j + 1] = a[i:j + 1]
    used = set(child[i:j + 1])
    fill = [x for x in b if x not in used]
    k = 0
    for t in list(range(i)) + list(range(j + 1, n)):
        child[t] = fill[k]
        k += 1
    return child


def cross(a: Sol, b: Sol, rng: random.Random) -> Sol:
    return Sol(
        ox(a.order, b.order, rng),
        [a.src[i] if rng.random() < 0.5 else b.src[i] for i in range(len(a.src))],
    )


def align(child: Sol, target: Sol, rng: random.Random, fraction: float) -> None:
    n = len(child.order)
    k = max(1, min(n, int(round(n * fraction))))
    loc = {d: i for i, d in enumerate(child.order)}
    for pos in rng.sample(range(n), k):
        want = target.order[pos]
        here = loc[want]
        if here != pos:
            displaced = child.order[pos]
            child.order[pos], child.order[here] = child.order[here], child.order[pos]
            loc[want] = pos
            loc[displaced] = here
        if rng.random() < 0.7:
            child.src[want] = target.src[want]


def op_apply(p, s: Sol, rng: random.Random, op: str) -> None:
    if op == "swap":
        swap(s, rng)
    elif op == "reverse":
        reverse(s, rng)
    elif op == "insert":
        insert(s, rng)
    elif op == "source":
        change_source(p, s, rng, 1)
    elif op == "joint":
        joint_move(p, s, rng)
    elif op == "block":
        block_reloc(s, rng)
    else:
        raise ValueError(f"Unknown operator: {op}")


def pop_diversity(pop) -> float:
    # Position-based diversity used by the packaged benchmark. The cap at 12
    # individuals keeps the diagnostic inexpensive relative to objective calls.
    if len(pop) < 2:
        return 0.0
    n = len(pop[0].order)
    pairs = 0
    acc = 0.0
    for i in range(min(len(pop), 12)):
        for j in range(i + 1, min(len(pop), 12)):
            pos = {d: k for k, d in enumerate(pop[j].order)}
            acc += sum(abs(k - pos[d]) for k, d in enumerate(pop[i].order)) / (n * n)
            pairs += 1
    return acc / max(1, pairs)


def local_best_of(p, base: Sol, rng: random.Random, ops, remaining: int, tries: int = 4):
    best = base.clone()
    used = 0
    for _ in range(min(tries, remaining)):
        candidate = base.clone()
        op_apply(p, candidate, rng, rng.choice(ops))
        evaluate(p, candidate)
        used += 1
        if candidate.score < best.score:
            best = candidate
    return best, used
