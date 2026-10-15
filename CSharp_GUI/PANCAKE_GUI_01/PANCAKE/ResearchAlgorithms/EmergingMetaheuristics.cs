using PANCAKE_Read_Map;
using PANCAKE_Solution;
using static PANCAKE_ResearchAlgorithms.ResearchOperatorUtils;

namespace PANCAKE_ResearchAlgorithms
{
    /// <summary>
    /// Interactive mechanism-preserving discrete adaptations of CPO, BKA and HO.
    /// These are research transfer models, not literal equation-level ports.
    /// </summary>
    public static class EmergingDiscreteMetaheuristics
    {
        public static Recommend_Aquire_Commodities_Path DCPO(
            Map map, List<string> demands, int populationSize = 18, int maxIter = 150, int seed = 77)
        {
            var rng = new Random(seed);
            var pop = Enumerable.Range(0, populationSize).Select(_ => RandomPath(map, demands)).ToList();
            var best = ClonePath(pop.OrderBy(x => x.Cost).First());
            int minActive = Math.Max(5, populationSize / 2);

            for (int iter = 0; iter < maxIter; iter++)
            {
                double cyclePhase = (iter % 24) / 24.0;
                int active = Math.Max(minActive, (int)Math.Round(populationSize - (populationSize - minActive) * cyclePhase));
                foreach (int i in Enumerable.Range(0, pop.Count).OrderBy(x => pop[x].Cost).Take(active).ToList())
                {
                    var cur = pop[i];
                    var child = ClonePath(cur);
                    switch (rng.Next(4))
                    {
                        case 0:
                            child = Blend(cur, pop[rng.Next(pop.Count)], rng); BlockRelocate(child, rng); break;
                        case 1:
                            ApplyMove(map, child, rng, rng.NextDouble() < .5 ? ResearchMove.Reverse : ResearchMove.Insert); break;
                        case 2:
                            AlignToward(child, best, rng, .12 + .28 * rng.NextDouble()); JointMove(map, child, rng); break;
                        default:
                            AlignToward(child, best, rng, .28 + .34 * rng.NextDouble()); JointMove(map, child, rng); Insert(child, rng); break;
                    }
                    if (rng.NextDouble() < .55) ChangeSource(map, child, rng);
                    if (child.Cost < cur.Cost) pop[i] = child;
                    if (child.Cost < best.Cost) best = ClonePath(child);
                }
                if (cyclePhase > .90)
                {
                    foreach (int wi in Enumerable.Range(0, pop.Count).OrderByDescending(i => pop[i].Cost).Take(Math.Max(1, populationSize / 6)).ToList())
                        pop[wi] = RandomPath(map, demands);
                }
            }
            return best;
        }

        public static Recommend_Aquire_Commodities_Path DBKA(
            Map map, List<string> demands, int populationSize = 18, int maxIter = 160, int seed = 77)
        {
            var rng = new Random(seed);
            var pop = Enumerable.Range(0, populationSize).Select(_ => RandomPath(map, demands)).ToList();
            var best = ClonePath(pop.OrderBy(x => x.Cost).First());
            for (int iter = 0; iter < maxIter; iter++)
            {
                double progress = (double)iter / Math.Max(1, maxIter - 1);
                for (int i = 0; i < pop.Count; i++)
                {
                    var cur = pop[i]; var child = ClonePath(cur);
                    if (rng.NextDouble() < .35 + .50 * progress)
                    {
                        AlignToward(child, best, rng, .10 + .42 * rng.NextDouble());
                        if (rng.NextDouble() < .60) JointMove(map, child, rng); else Insert(child, rng);
                    }
                    else
                    {
                        child = Blend(cur, pop[rng.Next(pop.Count)], rng);
                        double u = Math.Clamp(rng.NextDouble(), 1e-6, 1 - 1e-6);
                        int steps = Math.Min(5, Math.Max(1, 1 + (int)Math.Abs(Math.Tan(Math.PI * (u - .5)))));
                        for (int s = 0; s < steps; s++)
                            ApplyMove(map, child, rng, (ResearchMove)rng.Next(0, 6));
                    }
                    if (child.Cost < cur.Cost) pop[i] = child;
                    if (child.Cost < best.Cost) best = ClonePath(child);
                }
            }
            return best;
        }

        public static Recommend_Aquire_Commodities_Path DHO(
            Map map, List<string> demands, int populationSize = 18, int maxIter = 150, int seed = 77)
        {
            var rng = new Random(seed);
            var pop = Enumerable.Range(0, populationSize).Select(_ => RandomPath(map, demands)).ToList();
            var best = ClonePath(pop.OrderBy(x => x.Cost).First());
            for (int iter = 0; iter < maxIter; iter++)
            {
                double progress = (double)iter / Math.Max(1, maxIter - 1);
                for (int i = 0; i < pop.Count; i++)
                {
                    var cur = pop[i]; var child = ClonePath(cur); double r = rng.NextDouble();
                    if (r < .40 * (1 - progress) + .15)
                    {
                        child = Blend(cur, pop[rng.Next(pop.Count)], rng);
                        AlignToward(child, best, rng, .08 + .22 * rng.NextDouble());
                    }
                    else if (r < .78)
                    {
                        BlockRelocate(child, rng); if (rng.NextDouble() < .65) Reverse(child, rng); ChangeSource(map, child, rng);
                    }
                    else
                    {
                        AlignToward(child, best, rng, .18 + .35 * progress + .15 * rng.NextDouble());
                        if (rng.NextDouble() < .65) JointMove(map, child, rng); else Insert(child, rng);
                    }
                    if (child.Cost < cur.Cost) pop[i] = child;
                    if (child.Cost < best.Cost) best = ClonePath(child);
                }
            }
            return best;
        }
    }
}
