
using PANCAKE_Read_Map;
using PANCAKE_DSLib;
using PANCAKE_Solution;
using PANCAKE_Params;

namespace Ant_Colony
{

    /// <summary>
    /// 5. 螞蟻演算法 (Ant Colony Optimization, ACO)
    /// 流程：
    ///  1. 初始化 pheromone (信息素) 矩陣，均設為 tau0
    ///  2. 重複 iter 次：
    ///     a. 每隻螞蟻依概率建構取貨路徑
    ///        Prob(u->v|mask) ∝ [pheromone(u,v)]^α * [heuristic(u,v)]^β
    ///     b. 評估每隻螞蟻總成本
    ///     c. 更新信息素：蒸發 rho，然後依螞蟻路徑加強 Δtau=Q/Cost
    ///  3. 回傳最佳路徑
    /// </summary>
    public static class ACO
    {
        // 參數
        private static int numAnts = 25;
        private static int maxIters = 200;
        private static double alpha = 1.0;   // 信息素重要度
        private static double beta = 2.0;    // 啟發式重要度
        private static double rho = 0.1;     // 蒸發率
        private static double Q = 1.0;       // 信息素強化因子

        public static Recommend_Aquire_Commodities_Path ACO_Method(Map map, List<string> demands)
        {
            int m = demands.Count;
            var origin = Params.pStart_Node;
            double unitCost = Params.pUnit_Cost;
            // 收集所有候選點 (含起點)
            var nodes = new List<Node> { origin };
            var demandOptions = new List<List<int>>();
            for (int i = 0; i < m; i++)
            {
                var opts = map.ObjectsAquireList[demands[i]]
                    .Select(p => p.node)
                    .Distinct().ToList();
                demandOptions.Add(new List<int>());
                foreach (var n in opts)
                {
                    int idx = nodes.IndexOf(n);
                    if (idx < 0)
                    {
                        idx = nodes.Count;
                        nodes.Add(n);
                    }
                    demandOptions[i].Add(idx);
                }
            }
            int V = nodes.Count;
            // 信息素與啟發式
            double[,] pheromone = new double[V, V];
            double[,] heuristic = new double[V, V];
            for (int u = 0; u < V; u++) for (int v = 0; v < V; v++)
                {
                    pheromone[u, v] = 1.0; // tau0
                    double dist = nodes[u].distance_to_next_Node(nodes[v]);
                    int minPrice = int.MaxValue;
                    // 若 v 能提供某需求，啟發式 = 1/(dist*unitCost + price)
                    for (int i = 0; i < m; i++)
                        if (demandOptions[i].Contains(v))
                        {
                            int price = map.ObjectsAquireList[demands[i]].First(p => p.node == nodes[v]).price;
                            minPrice = Math.Min(minPrice, price);
                        }
                    heuristic[u, v] = (minPrice < int.MaxValue)
                        ? 1.0 / (dist * unitCost + minPrice)
                        : 0.0;
                }

            // 最佳解記錄
            Recommend_Aquire_Commodities_Path bestGlobal = null!;
            double bestCost = double.MaxValue;

            // 主迴圈
            var rand = new Random();
            for (int iter = 0; iter < maxIters; iter++)
            {
                var ants = new List<Recommend_Aquire_Commodities_Path>();
                // 每隻螞蟻建構解
                for (int k = 0; k < numAnts; k++)
                {
                    var path = ConstructAntSolution(nodes, demandOptions, pheromone, heuristic, map, demands, origin, unitCost, rand);
                    ants.Add(path);
                    if (path.Cost < bestCost)
                    {
                        bestCost = path.Cost;
                        bestGlobal = path;
                    }
                }
                // 信息素更新
                // 先蒸發
                for (int u = 0; u < V; u++) for (int v = 0; v < V; v++)
                        pheromone[u, v] *= (1 - rho);
                // 再強化
                foreach (var ant in ants)
                {
                    double delta = Q / ant.Cost;
                    var seq = ant.Path.Select(an => nodes.IndexOf(an.Node)).ToList();
                    int cur = 0;
                    foreach (var nxt in seq)
                    {
                        pheromone[cur, nxt] += delta;
                        cur = nxt;
                    }
                }
            }
            return bestGlobal;
        }

        // 單隻螞蟻建構路徑
        private static Recommend_Aquire_Commodities_Path ConstructAntSolution(
            List<Node> nodes,
            List<List<int>> demandOptions,
            double[,] pheromone,
            double[,] heuristic,
            Map map,
            List<string> demands,
            Node origin,
            double unitCost,
            Random rand)
        {
            int m = demands.Count;
            var available = new HashSet<int>(Enumerable.Range(0, m));
            var path = new Recommend_Aquire_Commodities_Path
            {
                Start_Node = origin,
                UnitMoveCost = unitCost
            };
            int cur = 0;
            while (available.Any())
            {
                // 構建下一步選擇列表 (item i, node v)
                var moves = new List<(int item, int v, double prob)>();
                double sumProb = 0;
                foreach (int i in available)
                {
                    foreach (int v in demandOptions[i])
                    {
                        double tau = pheromone[cur, v];
                        double eta = heuristic[cur, v];
                        double p = Math.Pow(tau, alpha) * Math.Pow(eta, beta);
                        moves.Add((i, v, p));
                        sumProb += p;
                    }
                }
                // 隨機選擇
                double r = rand.NextDouble() * sumProb;
                double acc = 0;
                foreach (var (i, v, p) in moves)
                {
                    acc += p;
                    if (acc >= r)
                    {
                        // 選擇 (i,v)
                        var node = nodes[v];
                        int price = map.ObjectsAquireList[demands[i]].First(pu => pu.node == node).price;
                        path.Path.Add(new Aquire_Node(node, new SupplyItem(demands[i], price)));
                        available.Remove(i);
                        cur = v;
                        break;
                    }
                }
            }
            path.Calculate_Cost();
            return path;
        }
    }

}