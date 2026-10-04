using PANCAKE_Read_Map;
using PANCAKE_Solution;
using static PANCAKE_ResearchAlgorithms.ResearchOperatorUtils;

namespace PANCAKE_ResearchAlgorithms
{
    /// <summary>
    /// DFOX-Base: a direct discrete mapping of the 2022 FOX optimizer.
    /// It intentionally preserves the original static 50/50 exploration/exploitation split
    /// and is used as an ablation baseline for DFOX-APNS.
    /// </summary>
    public static class DFOX_Base
    {
        public static Recommend_Aquire_Commodities_Path Optimize(
            Map map, List<string> demands, int foxCount = 16, int maxIter = 160, int seed = 77)
        {
            var rng = new Random(seed);
            var population = Enumerable.Range(0, foxCount).Select(_ => RandomPath(map, demands)).ToList();
            var best = ClonePath(population.OrderBy(x => x.Cost).First());

            for (int iter = 0; iter < maxIter; iter++)
            {
                var next = new List<Recommend_Aquire_Commodities_Path>();
                foreach (var current in population)
                {
                    var child = ClonePath(current);
                    double mismatch = Mismatch(current, best);

                    if (rng.NextDouble() < 0.5)
                    {
                        // Exploration: controlled random walk / long discrete jump.
                        if (rng.NextDouble() < 0.5) BlockRelocate(child, rng);
                        else Reverse(child, rng);
                        if (rng.NextDouble() < 0.75) ChangeSource(map, child, rng);
                        if (rng.NextDouble() < 0.25 + 0.25 * mismatch) Swap(child, rng);
                    }
                    else
                    {
                        // Exploitation: prey-guided partial alignment.
                        double jump = Math.Clamp(0.10 + 0.45 * mismatch * rng.NextDouble(),
                            1.0 / Math.Max(1, child.Path.Count), 0.55);
                        AlignToward(child, best, rng, jump);
                        if (rng.NextDouble() < 0.55) Insert(child, rng);
                        if (rng.NextDouble() < 0.65) ChangeSource(map, child, rng);
                    }

                    child.Calculate_Cost();
                    next.Add(child);
                    if (child.Cost < best.Cost) best = ClonePath(child);
                }

                population = next;
                int worst = Enumerable.Range(0, population.Count).OrderByDescending(i => population[i].Cost).First();
                if (best.Cost < population[worst].Cost) population[worst] = ClonePath(best);
            }
            return best;
        }

        internal static double Mismatch(Recommend_Aquire_Commodities_Path a, Recommend_Aquire_Commodities_Path b)
        {
            int n = Math.Min(a.Path.Count, b.Path.Count);
            if (n == 0) return 0.0;
            var targetPos = b.Path.Select((x, i) => (Name: x.Item.Name, Pos: i))
                .GroupBy(x => x.Name).ToDictionary(g => g.Key, g => g.First().Pos);
            double order = 0.0;
            int sourceMismatch = 0;
            for (int i = 0; i < n; i++)
            {
                if (targetPos.TryGetValue(a.Path[i].Item.Name, out int pos)) order += Math.Abs(i - pos);
                var target = b.Path.FirstOrDefault(x => x.Item.Name == a.Path[i].Item.Name);
                if (target != null && !ReferenceEquals(target.Node, a.Path[i].Node)) sourceMismatch++;
            }
            double orderNorm = order / Math.Max(1.0, n * n);
            double sourceNorm = (double)sourceMismatch / n;
            return Math.Min(1.0, 0.62 * orderNorm + 0.38 * sourceNorm);
        }
    }
}
