using PANCAKE_Read_Map;
using PANCAKE_Solution;
using static PANCAKE_ResearchAlgorithms.ResearchOperatorUtils;

namespace PANCAKE_ResearchAlgorithms
{
    /// <summary>
    /// Interactive mirror of the controlled A0-A3 DFOX research ablation.
    /// Canonical equal-FE statistics are produced by ResearchBenchmark/algorithms/dfox_ablation.py.
    /// </summary>
    public static class DFOX_Ablation
    {
        private static readonly ResearchMove[] GenericMoves =
        {
            ResearchMove.Swap, ResearchMove.Reverse, ResearchMove.Insert, ResearchMove.Block
        };

        private static readonly ResearchMove[] AwareMoves =
        {
            ResearchMove.Swap, ResearchMove.Reverse, ResearchMove.Insert,
            ResearchMove.Block, ResearchMove.Source, ResearchMove.Joint
        };

        public static Recommend_Aquire_Commodities_Path Optimize(
            Map map,
            List<string> demands,
            int level,
            int populationSize = 12,
            int maxIter = 120,
            int seed = 177)
        {
            if (level < 0 || level > 3)
                throw new ArgumentOutOfRangeException(nameof(level), "Ablation level must be A0..A3 (0..3).");

            var rng = new Random(seed);
            var population = Enumerable.Range(0, populationSize)
                .Select(_ => RandomPath(map, demands))
                .ToList();
            var best = ClonePath(population.OrderBy(x => x.Cost).First());
            int stagnation = 0;

            var weights = AwareMoves.ToDictionary(x => x, _ => 1.0);

            for (int iter = 0; iter < maxIter; iter++)
            {
                double progress = (double)iter / Math.Max(1, maxIter - 1);
                double diversity = Diversity(population);
                double lo = population.Min(x => x.Cost);
                double hi = population.Max(x => x.Cost);
                double span = Math.Max(1e-9, hi - lo);
                bool globalImproved = false;
                var next = new List<Recommend_Aquire_Commodities_Path>(population.Count);

                foreach (var current in population)
                {
                    double relative = (current.Cost - lo) / span;
                    double pExplore = 0.50;
                    if (level >= 2)
                    {
                        pExplore = 0.10 + 0.54 * (1.0 - progress) + 0.24 * relative;
                        if (diversity < 0.10)
                            pExplore += Math.Min(0.18, (0.10 - diversity) * 1.8);
                        pExplore = Math.Clamp(pExplore, 0.08, 0.88);
                    }

                    var moves = level >= 1 ? AwareMoves : GenericMoves;
                    ResearchMove move = level >= 2
                        ? WeightedChoice(rng, moves, weights)
                        : moves[rng.Next(moves.Length)];

                    var child = ClonePath(current);
                    double before = current.Cost;
                    if (rng.NextDouble() < pExplore)
                    {
                        if (level >= 1 && rng.NextDouble() < 0.45)
                            child = Blend(current, population[rng.Next(population.Count)], rng);
                        ApplyMove(map, child, rng, move);
                        if (level >= 1 && rng.NextDouble() < 0.28)
                            ChangeSource(map, child, rng);
                    }
                    else
                    {
                        double fraction = Math.Clamp(0.08 + 0.32 * progress + 0.28 * rng.NextDouble(),
                            1.0 / Math.Max(1, child.Path.Count), 0.65);
                        AlignToward(child, best, rng, fraction);
                        ApplyMove(map, child, rng, move);
                    }

                    if (level >= 2)
                        UpdateWeight(weights, move, before, child.Cost);

                    var survivor = child.Cost < current.Cost ? child : ClonePath(current);
                    next.Add(survivor);
                    if (survivor.Cost < best.Cost)
                    {
                        best = ClonePath(survivor);
                        globalImproved = true;
                    }
                }

                population = next;
                stagnation = globalImproved ? 0 : stagnation + 1;

                if (population.Count > 0)
                {
                    int worst = Enumerable.Range(0, population.Count)
                        .OrderByDescending(i => population[i].Cost).First();
                    if (best.Cost < population[worst].Cost)
                        population[worst] = ClonePath(best);
                }

                if (level >= 3 && (stagnation >= 3 || diversity < 0.075))
                {
                    int count = Math.Max(1, population.Count / 5);
                    foreach (int wi in Enumerable.Range(0, population.Count)
                                 .OrderByDescending(i => population[i].Cost).Take(count).ToList())
                    {
                        var jump = ClonePath(best);
                        BlockRelocate(jump, rng);
                        ApplyMove(map, jump, rng, rng.NextDouble() < 0.50 ? ResearchMove.Joint : ResearchMove.Source);
                        population[wi] = jump;
                        if (jump.Cost < best.Cost)
                        {
                            best = ClonePath(jump);
                            stagnation = 0;
                        }
                    }
                }
            }

            return best;
        }

        private static ResearchMove WeightedChoice(
            Random rng,
            IReadOnlyList<ResearchMove> moves,
            IReadOnlyDictionary<ResearchMove, double> weights)
        {
            double total = moves.Sum(x => Math.Max(1e-6, weights[x]));
            double target = rng.NextDouble() * total;
            double acc = 0.0;
            foreach (var move in moves)
            {
                acc += Math.Max(1e-6, weights[move]);
                if (acc >= target) return move;
            }
            return moves[^1];
        }

        private static void UpdateWeight(
            Dictionary<ResearchMove, double> weights,
            ResearchMove move,
            double before,
            double after)
        {
            if (after < before)
            {
                double reward = 1.0 + Math.Min(4.0, 100.0 * (before - after) / Math.Max(1e-9, before));
                weights[move] = 0.82 * weights[move] + 0.18 * reward;
            }
            else
            {
                weights[move] = 0.98 * weights[move] + 0.02 * 0.25;
            }
        }
    }
}
