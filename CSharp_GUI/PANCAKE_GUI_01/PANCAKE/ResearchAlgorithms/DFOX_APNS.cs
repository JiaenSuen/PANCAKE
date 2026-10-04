using PANCAKE_Read_Map;
using PANCAKE_Solution;
using static PANCAKE_ResearchAlgorithms.ResearchOperatorUtils;
using static PANCAKE_ResearchAlgorithms.DFOX_Base;

namespace PANCAKE_ResearchAlgorithms
{
    /// <summary>
    /// DFOX-APNS: Discrete FOX Optimization with Adaptive Prey-guided Neighborhood Search.
    /// Interactive C# port. Canonical reported results come from the equal-evaluation
    /// Python benchmark in ResearchBenchmark/algorithms/dfox_apns.py.
    /// </summary>
    public static class DFOX_APNS
    {
        public static Recommend_Aquire_Commodities_Path Optimize(
            Map map, List<string> demands, int foxCount = 12, int maxIter = 200, int seed = 77)
        {
            var rng = new Random(seed);
            var population = Enumerable.Range(0, foxCount).Select(_ => RandomPath(map, demands)).ToList();
            var best = ClonePath(population.OrderBy(x => x.Cost).First());
            int stagnation = 0;

            var localMoves = new[] { ResearchMove.Joint, ResearchMove.Insert, ResearchMove.Source, ResearchMove.Reverse };
            var lateMoves = new[] { ResearchMove.Joint, ResearchMove.Insert, ResearchMove.Source, ResearchMove.Swap };
            var exploreMoves = new[] { ResearchMove.Block, ResearchMove.Reverse, ResearchMove.Insert, ResearchMove.Joint, ResearchMove.Source };

            for (int iter = 0; iter < maxIter; iter++)
            {
                double progress = (double)iter / Math.Max(1, maxIter - 1);
                double diversity = Diversity(population);
                double lo = population.Min(x => x.Cost);
                double hi = population.Max(x => x.Cost);
                double span = Math.Max(1e-9, hi - lo);
                bool improvedGlobal = false;
                var next = new List<Recommend_Aquire_Commodities_Path>();

                foreach (var current in population)
                {
                    double rel = (current.Cost - lo) / span;
                    double pExplore = 0.10 + 0.54 * (1.0 - progress) + 0.24 * rel;
                    if (diversity < 0.10) pExplore += Math.Min(0.18, (0.10 - diversity) * 1.8);
                    pExplore = Math.Clamp(pExplore, 0.08, 0.88);

                    Recommend_Aquire_Commodities_Path candidate;
                    if (rng.NextDouble() < pExplore)
                    {
                        var peer = population[rng.Next(population.Count)];
                        candidate = rng.NextDouble() < 0.55 ? Blend(current, peer, rng) : ClonePath(current);
                        double mismatch = Mismatch(current, best);
                        double leap = Math.Clamp(0.35 + 0.45 * (1 - progress) +
                            0.35 * (0.12 - diversity) / 0.12 + 0.25 * mismatch, 0.0, 1.0);
                        int moves = 1 + (rng.NextDouble() < leap ? 1 : 0) + (rng.NextDouble() < 0.35 * leap ? 1 : 0);
                        for (int m = 0; m < moves; m++) ApplyMove(map, candidate, rng, exploreMoves[rng.Next(exploreMoves.Length)]);
                        if (rng.NextDouble() < 0.50 + 0.25 * leap) ChangeSource(map, candidate, rng);
                        if (rng.NextDouble() < 0.25) AlignToward(candidate, best, rng, 0.08 + 0.12 * rng.NextDouble());
                    }
                    else
                    {
                        candidate = ClonePath(current);
                        double mismatch = Mismatch(current, best);
                        double jump = Math.Clamp(0.12 + 0.30 * progress + 0.34 * mismatch * rng.NextDouble(),
                            1.0 / Math.Max(1, candidate.Path.Count), 0.72);
                        AlignToward(candidate, best, rng, jump);
                        if (rng.NextDouble() < 0.58) JointMove(map, candidate, rng);
                        else if (rng.NextDouble() < 0.55) Insert(candidate, rng);
                        else ChangeSource(map, candidate, rng);
                    }

                    candidate.Calculate_Cost();
                    var chosen = candidate;
                    if (candidate.Cost <= current.Cost * 1.06 || progress > 0.67)
                    {
                        var refined = LocalBestOf(map, candidate, rng,
                            progress < 0.75 ? localMoves : lateMoves,
                            progress < 0.75 ? 2 : 3);
                        if (refined.Cost < chosen.Cost) chosen = refined;
                    }

                    Recommend_Aquire_Commodities_Path survivor;
                    if (chosen.Cost < current.Cost) survivor = chosen;
                    else if (rng.NextDouble() < 0.05 * (1 - progress) * rel) survivor = chosen;
                    else survivor = ClonePath(current);

                    next.Add(survivor);
                    if (survivor.Cost < best.Cost)
                    {
                        best = ClonePath(survivor);
                        improvedGlobal = true;
                    }
                }

                population = next;
                stagnation = improvedGlobal ? 0 : stagnation + 1;
                int worstIndex = Enumerable.Range(0, population.Count).OrderByDescending(i => population[i].Cost).First();
                if (best.Cost < population[worstIndex].Cost) population[worstIndex] = ClonePath(best);

                if (stagnation >= 3 || diversity < 0.075)
                {
                    int count = Math.Max(1, population.Count / 5);
                    foreach (int wi in Enumerable.Range(0, population.Count)
                        .OrderByDescending(i => population[i].Cost).Take(count).ToList())
                    {
                        var jump = ClonePath(population[wi]);
                        BlockRelocate(jump, rng);
                        if (rng.NextDouble() < 0.70) Reverse(jump, rng);
                        ChangeSource(map, jump, rng);
                        ChangeSource(map, jump, rng);
                        if (rng.NextDouble() < 0.35) AlignToward(jump, best, rng, 0.08 + 0.10 * rng.NextDouble());
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
    }
}
