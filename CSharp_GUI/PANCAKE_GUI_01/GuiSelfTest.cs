using Basic_Algorithms_PANCAKE;
using PANCAKE_Read_Map;
using PANCAKE_ResearchAlgorithms;
using PANCAKE_Solution;

namespace PANCAKE_GUI_01
{
    internal static class GuiSelfTest
    {
        public static int Run()
        {
            string logPath = Path.Combine(AppContext.BaseDirectory, "gui_self_test.log");
            var log = new List<string>
            {
                $"PANCAKE GUI self-test - {DateTime.Now:yyyy-MM-dd HH:mm:ss}",
                $"Base directory: {AppContext.BaseDirectory}"
            };

            try
            {
                string legacyPath = Dataset("map.csv");
                string researchPath = Dataset("research_uniform_01.csv");

                var legacy = MapLoader.Read_CSV_From_Map(legacyPath);
                Assert(legacy.Nodes.Count > 0, "Legacy map contains nodes.");
                Assert(legacy.ObjectsAquireList.AllObjects.Any(), "Legacy map contains commodities.");
                log.Add($"PASS legacy map: {legacy.Nodes.Count} nodes");

                var basicDemands = new List<string> { "Water", "Bread", "Battery" };
                var greedy = Greedy.Greedy_Method(legacy, basicDemands);
                ValidateSolution(greedy, basicDemands.Count, "Greedy");
                log.Add($"PASS Greedy: cost={greedy.Cost:F2}");

                var setCover = SetCover.SetCover_Method(legacy, basicDemands);
                ValidateSolution(setCover, basicDemands.Count, "Set Cover");
                log.Add($"PASS Set Cover: cost={setCover.Cost:F2}");

                var research = MapLoader.Read_CSV_From_Map(researchPath);
                Assert(research.Nodes.Count > 0, "Research map contains nodes.");
                var researchDemands = research.ObjectsAquireList.AllObjects
                    .OrderBy(x => x, StringComparer.OrdinalIgnoreCase)
                    .Take(8)
                    .ToList();
                Assert(researchDemands.Count == 8, "Research map exposes at least eight demand commodities.");
                log.Add($"PASS research map: {research.Nodes.Count} nodes, {research.ObjectsAquireList.AllObjects.Count()} commodities");

                var dwoa = DWOA_AVNS.Optimize(research, researchDemands, numWhales: 8, maxIter: 12, seed: 7);
                ValidateSolution(dwoa, researchDemands.Count, "DWOA-AVNS");
                log.Add($"PASS DWOA-AVNS smoke run: cost={dwoa.Cost:F2}");

                var dfox = DFOX_APNS.Optimize(research, researchDemands, foxCount: 6, maxIter: 10, seed: 7);
                ValidateSolution(dfox, researchDemands.Count, "DFOX-APNS");
                log.Add($"PASS DFOX-APNS smoke run: cost={dfox.Cost:F2}");

                log.Add("SELF-TEST PASSED");
                File.WriteAllLines(logPath, log);
                return 0;
            }
            catch (Exception ex)
            {
                log.Add("SELF-TEST FAILED");
                log.Add(ex.ToString());
                File.WriteAllLines(logPath, log);
                return 1;
            }
        }

        private static string Dataset(string fileName)
        {
            string path = Path.Combine(AppContext.BaseDirectory, "datasets", fileName);
            if (!File.Exists(path))
                throw new FileNotFoundException($"Self-test dataset not found: {path}");
            return path;
        }

        private static void ValidateSolution(
            Recommend_Aquire_Commodities_Path solution,
            int expectedDemandCount,
            string name)
        {
            Assert(solution.Path.Count == expectedDemandCount,
                $"{name} returned {solution.Path.Count} steps; expected {expectedDemandCount}.");
            Assert(!double.IsNaN(solution.Cost) && !double.IsInfinity(solution.Cost) && solution.Cost > 0,
                $"{name} returned an invalid cost: {solution.Cost}.");
        }

        private static void Assert(bool condition, string message)
        {
            if (!condition) throw new InvalidOperationException(message);
        }
    }
}
