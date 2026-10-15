using PANCAKE_Read_Map;
using PANCAKE_Solution;
using static PANCAKE_ResearchAlgorithms.ResearchOperatorUtils;

namespace PANCAKE_ResearchAlgorithms
{
    /// <summary>Interactive problem-aware ILS/VNS baselines. Canonical equal-FE results are produced in Python.</summary>
    public static class ProblemAwareLocalSearch
    {
        private static readonly ResearchMove[] Moves =
        {
            ResearchMove.Joint, ResearchMove.Source, ResearchMove.Insert,
            ResearchMove.Reverse, ResearchMove.Swap, ResearchMove.Block
        };

        public static Recommend_Aquire_Commodities_Path ILS(
            Map map, List<string> demands, int maxIter = 220, int seed = 77)
        {
            var rng = new Random(seed);
            var current = RandomPath(map, demands);
            var best = ClonePath(current);
            int stagnation = 0;

            for (int it = 0; it < maxIter; it++)
            {
                var local = ClonePath(current);
                bool changed = true;
                int pass = 0;
                while (changed && pass++ < 3)
                {
                    changed = false;
                    foreach (var move in Moves)
                    {
                        var candidate = ClonePath(local);
                        ApplyMove(map, candidate, rng, move);
                        if (candidate.Cost < local.Cost)
                        {
                            local = candidate;
                            changed = true;
                        }
                    }
                }

                if (local.Cost < best.Cost)
                {
                    best = ClonePath(local);
                    stagnation = 0;
                }
                else stagnation++;

                current = ClonePath(local.Cost <= current.Cost ? local : current);
                int strength = Math.Min(4, 1 + stagnation / 2);
                for (int k = 0; k < strength; k++)
                    ApplyMove(map, current, rng, k == 0 ? ResearchMove.Block : Moves[rng.Next(Moves.Length)]);

                if (stagnation >= 7)
                {
                    current = RandomPath(map, demands);
                    stagnation = 0;
                }
            }
            return best;
        }

        public static Recommend_Aquire_Commodities_Path VNS(
            Map map, List<string> demands, int maxIter = 260, int seed = 77)
        {
            var rng = new Random(seed);
            var current = RandomPath(map, demands);
            var best = ClonePath(current);
            int k = 0;

            for (int it = 0; it < maxIter; it++)
            {
                var shaken = ClonePath(current);
                ApplyMove(map, shaken, rng, Moves[k]);
                if (k >= 4) ApplyMove(map, shaken, rng, Moves[k]);
                var local = LocalBestOf(map, shaken, rng, Moves.Take(Math.Max(3, k + 1)).ToArray(), 5);

                if (local.Cost < current.Cost)
                {
                    current = local;
                    k = 0;
                    if (current.Cost < best.Cost) best = ClonePath(current);
                }
                else
                {
                    k++;
                    if (k >= Moves.Length)
                    {
                        k = 0;
                        current = ClonePath(best);
                        BlockRelocate(current, rng);
                        ChangeSource(map, current, rng);
                    }
                }
            }
            return best;
        }
    }
}
