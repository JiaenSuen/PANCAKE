using PANCAKE_Read_Map;
using PANCAKE_Solution;
using Basic_Algorithms_PANCAKE;
using Genetic_Algorithm;
using Genetic_Algorithm_TS_Mutaion;
using Tabu_Search;
using Ant_Colony;
using Whale_optimization;
using Whale_optimization_TS;
using Discrete_PSO;
using PANCAKE_ResearchAlgorithms;

namespace PANCAKE_GUI_01
{
    /// <summary>
    /// Central execution layer for the interactive GUI.
    /// Parameters below are intentionally lighter than the research benchmark so the
    /// desktop application remains responsive. Canonical benchmark settings/results
    /// are stored under ResearchBenchmark/.
    /// </summary>
    internal static class AlgorithmRunner
    {
        public static readonly string[] AlgorithmNames =
        {
            "Greedy Strategy",
            "Set Cover Strategy",
            "Dynamic Programming (Exact, Small)",
            "Genetic Algorithm (GA)",
            "Tabu Search",
            "GA + Tabu Hybrid",
            "Ant Colony Optimization (ACO)",
            "Discrete Whale Optimization (DWOA Original)",
            "DWOA + Tabu Hybrid",
            "Discrete Particle Swarm Optimization (DPSO)",
            "DWOA-AVNS",
            "DFOX-Base",
            "DFOX-APNS"
        };

        public static Recommend_Aquire_Commodities_Path Run(
            string algorithm,
            Map map,
            List<string> demands)
        {
            if (demands.Count == 0)
                throw new InvalidOperationException("No valid demand items were supplied.");

            return algorithm switch
            {
                "Greedy Strategy" => Greedy.Greedy_Method(map, demands),
                "Set Cover Strategy" => SetCover.SetCover_Method(map, demands),
                "Dynamic Programming (Exact, Small)" => RunDynamicProgramming(map, demands),
                "Genetic Algorithm (GA)" => GA.Genetic_Evolution(
                    map, demands, populationSize: 70, generations: 220,
                    crossoverRate: 0.8, mutationStrength: 3, mutationRate: 0.2)[0],
                "Tabu Search" => TS.Tabu_Search(
                    map, demands, Greedy.Greedy_Method(map, demands),
                    maxIterations: 350, tabuListSize: 80, neighborCount: 45),
                "GA + Tabu Hybrid" => GA_ts.Genetic_Evolution(
                    map, demands, populationSize: 55, generations: 70,
                    crossoverRate: 0.8, mutationStrength: 2, mutationRate: 0.18)[0],
                "Ant Colony Optimization (ACO)" => ACO.ACO_Method(map, demands),
                "Discrete Whale Optimization (DWOA Original)" => WOA.Optimize(
                    map, demands, numWhales: 40, maxIter: 220),
                "DWOA + Tabu Hybrid" => WOA_ts.Optimize(
                    map, demands, numWhales: 24, maxIter: 110),
                "Discrete Particle Swarm Optimization (DPSO)" => PSO.Optimize(
                    map, demands, numParticles: 45, maxIter: 240),
                "DWOA-AVNS" => DWOA_AVNS.Optimize(
                    map, demands, numWhales: 30, maxIter: 220, seed: 77),
                "DFOX-Base" => DFOX_Base.Optimize(
                    map, demands, foxCount: 16, maxIter: 150, seed: 77),
                "DFOX-APNS" => DFOX_APNS.Optimize(
                    map, demands, foxCount: 12, maxIter: 180, seed: 77),
                _ => throw new ArgumentException($"Unknown algorithm: {algorithm}", nameof(algorithm))
            };
        }

        private static Recommend_Aquire_Commodities_Path RunDynamicProgramming(
            Map map,
            List<string> demands)
        {
            // The exact bit-mask DP uses O(2^m * N) memory and should only be used
            // as a small-instance reference method in the GUI.
            if (demands.Count > 14)
            {
                throw new InvalidOperationException(
                    "Dynamic Programming is limited to 14 demand items in the GUI because its state space grows exponentially. " +
                    "Use a metaheuristic for larger cases.");
            }
            return DP.DP_Method(map, demands);
        }
    }
}
