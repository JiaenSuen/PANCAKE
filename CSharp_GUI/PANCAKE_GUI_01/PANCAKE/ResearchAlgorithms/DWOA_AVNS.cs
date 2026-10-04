using PANCAKE_Read_Map;
using PANCAKE_Solution;
using static PANCAKE_ResearchAlgorithms.ResearchOperatorUtils;

namespace PANCAKE_ResearchAlgorithms
{
    /// <summary>
    /// DWOA-AVNS: Discrete Whale Optimization with Adaptive Variable-Neighborhood Search.
    /// Interactive C# port of the research design. The README benchmark values are produced
    /// by the Python implementation under ResearchBenchmark/algorithms/.
    /// </summary>
    public static class DWOA_AVNS
    {
        public static Recommend_Aquire_Commodities_Path Optimize(
            Map map,
            List<string> demands,
            int numWhales = 30,
            int maxIter = 350,
            int seed = 77)
        {
            var rng = new Random(seed);
            var pop = Enumerable.Range(0, numWhales)
                .Select(_ => RandomPath(map, demands))
                .ToList();
            var best = ClonePath(pop.OrderBy(x => x.Cost).First());
            int stagnation = 0;

            var competitiveMoves = new[]
            {
                ResearchMove.Swap, ResearchMove.Insert, ResearchMove.Reverse,
                ResearchMove.Source, ResearchMove.Joint
            };
            var escapeMoves = new[]
            {
                ResearchMove.Insert, ResearchMove.Reverse, ResearchMove.Joint,
                ResearchMove.Source, ResearchMove.Block
            };

            for (int iter = 0; iter < maxIter; iter++)
            {
                double progress = (double)iter / Math.Max(1, maxIter - 1);
                double a = 2.0 * (1.0 - progress);
                bool improved = false;

                for (int i = 0; i < pop.Count; i++)
                {
                    var current = pop[i];
                    double A = 2.0 * a * rng.NextDouble() - a;
                    double branch = rng.NextDouble();
                    Recommend_Aquire_Commodities_Path child;

                    if (branch < 0.5 && Math.Abs(A) < 1.0)
                    {
                        child = Blend(current, best, rng);
                        AlignToward(child, best, rng, 0.18 + 0.52 * (1.0 - Math.Abs(A)));
                    }
                    else if (branch < 0.5)
                    {
                        var reference = pop[rng.Next(pop.Count)];
                        child = Blend(current, reference, rng);
                        BlockRelocate(child, rng);
                    }
                    else
                    {
                        child = Blend(current, best, rng);
                        if (rng.NextDouble() < 0.5) Insert(child, rng);
                        else Reverse(child, rng);
                    }

                    if (rng.NextDouble() < 0.72) ChangeSource(map, child, rng);
                    if (rng.NextDouble() < 0.28) JointMove(map, child, rng);

                    if (child.Cost <= current.Cost * 1.08)
                        child = LocalBestOf(map, child, rng, competitiveMoves, 2);

                    if (child.Cost < current.Cost) pop[i] = child;
                    if (child.Cost < best.Cost)
                    {
                        best = ClonePath(child);
                        improved = true;
                    }
                }

                stagnation = improved ? 0 : stagnation + 1;
                if (stagnation >= 3 || Diversity(pop) < 0.10)
                {
                    var refined = LocalBestOf(map, best, rng, escapeMoves, 8);
                    if (refined.Cost < best.Cost)
                    {
                        best = refined;
                        stagnation = 0;
                    }

                    int replace = Math.Max(1, pop.Count / 5);
                    foreach (int idx in pop
                        .Select((s, i) => (s, i))
                        .OrderByDescending(x => x.s.Cost)
                        .Take(replace)
                        .Select(x => x.i))
                    {
                        var z = ClonePath(best);
                        ApplyMove(map, z, rng, escapeMoves[rng.Next(escapeMoves.Length)]);
                        ApplyMove(map, z, rng, rng.NextDouble() < 0.5 ? ResearchMove.Swap : ResearchMove.Source);
                        pop[idx] = z;
                        if (z.Cost < best.Cost) best = ClonePath(z);
                    }
                }
            }

            return best;
        }
    }
}
