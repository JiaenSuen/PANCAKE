
using Google.OrTools.ConstraintSolver;
using Google.OrTools.Sat;
using PANCAKE_DSLib;
using PANCAKE_Params;
using PANCAKE_Read_Map;
using PANCAKE_Solution;

namespace Basic_Algorithms_PANCAKE
{
     

    class Greedy
    {
        public static Recommend_Aquire_Commodities_Path Greedy_Method(Map map, List<string> Aquire_List)
        {
            Aquire_List = Aquire_List
            .Where(item => map.ObjectsAquireList[item].Any())
            .ToList();

            var path = new Recommend_Aquire_Commodities_Path
            {
                Start_Node = Params.pStart_Node,
                UnitMoveCost = Params.pUnit_Cost,
            };


            while (Aquire_List.Count > 0)
            {
                Node? bestNode = null;
                SupplyItem? bestItem = null;
                string? bestItemName = null;
                double? bestCost = double.MaxValue;


                foreach (var itemName in Aquire_List)
                {


                    var options = map.ObjectsAquireList[itemName];

                    foreach (var (node, price) in options)
                    {
                        // 從 Node.Objects 找到對應的 SupplyItem 實例
                        var supply = node.Objects
                                        .First(si => si.Name.Equals(itemName, StringComparison.OrdinalIgnoreCase));

                        // 計算「從目前位置到 node 的移動成本 + 購買價格」
                        var current = path.Path.Count == 0
                            ? path.Start_Node
                            : path.Path.Last().Node;

                        double moveCost = current.distance_to_next_Node(node) * path.UnitMoveCost;
                        double totalInc = moveCost + supply.Price;

                        if (totalInc < bestCost)
                        {
                            bestCost = totalInc;
                            bestNode = node;
                            bestItem = supply;
                            bestItemName = itemName;
                        }
                    }
                }

                if (bestNode == null || bestItem == null || bestItemName == null)
                {
                    Console.WriteLine("⚠️ 無法再找到任何符合的取購點，提前結束。");
                    break;
                }
                path.Path.Add(new Aquire_Node(bestNode, bestItem));
                // 並從需求清單移除
                Aquire_List.Remove(bestItemName);
            } // End Construct Aquire Commodities Path
            path.Calculate_Cost();
            return path;
        }
    }//End Define Greedy



    /*
     把每個節點當作「供應集合」，元素為它可取得的需求編號。
    Greedy 挑選「成本／新覆蓋數」最小者，直到覆蓋所有需求。
    回建時依序加入購買動作，保證記錄同一地點多項目。   
     */
    // Set Cover 
    public static class SetCover
    {
        public static Recommend_Aquire_Commodities_Path SetCover_Method(Map map, List<string> demands)
        {
            int m = demands.Count;
            var origin = Params.pStart_Node;
            double unitCost = Params.pUnit_Cost;

            // 1. 構建每節點覆蓋需求的集合 Cover[node] = list of demand indices
            var allNodes = map.Nodes;
            var cover = new Dictionary<Node, List<int>>();
            foreach (var node in allNodes)
            {
                var covered = new List<int>();
                for (int i = 0; i < m; i++)
                    if (node.Objects.Any(si => si.Name.Equals(demands[i], StringComparison.OrdinalIgnoreCase)))
                        covered.Add(i);
                if (covered.Any()) cover[node] = covered;
            }

            // 2. 貪婪挑選：不斷選擇「成本效益最高」的節點
            var uncovered = new HashSet<int>(Enumerable.Range(0, m));
            var selected = new List<Node>();
            while (uncovered.Any())
            {
                Node? bestNode = null;
                double bestRatio = double.MaxValue;
                foreach (var kv in cover)
                {
                    var node = kv.Key;
                    var newCover = kv.Value.Count(idx => uncovered.Contains(idx));
                    if (newCover == 0) continue;
                    // 成本 = 移動從上一節點 + 購買所有在此節點的需求價格
                    // 取單筆價格總和 + 移動成本的比例
                    double priceSum = kv.Value.Where(idx => uncovered.Contains(idx))
                                              .Sum(idx => node.Objects.First(si => si.Name == demands[idx]).Price);
                    double moveCost = selected.Any()
                        ? selected.Last().distance_to_next_Node(node) * unitCost
                        : origin.distance_to_next_Node(node) * unitCost;
                    double ratio = (moveCost + priceSum) / newCover;
                    if (ratio < bestRatio)
                    {
                        bestRatio = ratio;
                        bestNode = node;
                    }
                }
                if (bestNode == null) break;
                selected.Add(bestNode);
                foreach (var idx in cover[bestNode])
                    uncovered.Remove(idx);
            }

            // 3. 重建路徑
            var path = new Recommend_Aquire_Commodities_Path
            {
                Start_Node = origin,
                UnitMoveCost = unitCost
            };
            foreach (var node in selected)
            {
                foreach (var idx in cover[node])
                {
                    var item = node.Objects.First(si => si.Name == demands[idx]);
                    path.Path.Add(new Aquire_Node(node, item));
                }
            }
            path.Calculate_Cost();
            return path;
        }
    }

}

namespace Basic_Algorithms_PANCAKE
{
    using PANCAKE_Read_Map;
    using PANCAKE_DSLib;
    using PANCAKE_Solution;
    using PANCAKE_Params;
    
    using System.IO;





    // O ( [2 ^ m ] *  N * m * k )
    // 轉移方程
    // dp[newState, j] = min{ dp[state, lastNode] + 移動成本(lastNode→j) + 購買價格(i 在 j 的售價) }
    public static class DP
    {
        /// 動態規劃(bitmask)解最小成本取貨路徑。
        /// State: (mask, lastNodeIndex) 表示已取物品集合與當前所在節點。
        public static Recommend_Aquire_Commodities_Path DP_Method(Map map, List<string> demands)
        {
            // 過濾無供應物品
            demands = demands.Where(d => map.ObjectsAquireList[d].Any()).ToList();
            int m = demands.Count;
            if (m == 0) return new Recommend_Aquire_Commodities_Path();

            // 對每個需求，列出所有供應選項
            var options = demands
                .Select(d => map.ObjectsAquireList[d]
                    .Select(p => new { Node = p.node, Price = p.price })
                    .ToList()
                ).ToList();

            // 建立全局節點列表以定義索引
            var allNodes = options.SelectMany(o => o.Select(x => x.Node)).Distinct().ToList();
            int N = allNodes.Count;

            // 預計算距離成本矩陣
            double[,] distCost = new double[N + 1, N + 1];
            var origin = Params.pStart_Node;
            for (int i = 0; i < N; i++)
            {
                distCost[N, i] = origin.distance_to_next_Node(allNodes[i]) * Params.pUnit_Cost;
                distCost[i, N] = distCost[N, i];
                for (int j = 0; j < N; j++)
                    distCost[i, j] = allNodes[i].distance_to_next_Node(allNodes[j]) * Params.pUnit_Cost;
            }

            int maxState = 1 << m;
            // DP[state, node]: 最小花費
            var dp = new double[maxState, N + 1];
            var parent = new (int prevState, int prevNode, int chosenOption)[maxState, N + 1];
            for (int s = 0; s < maxState; s++)
                for (int v = 0; v <= N; v++)
                    dp[s, v] = double.MaxValue;

            // 初始：沒取物品，在origin(用索引N)
            dp[0, N] = 0;

            // DP轉移
            for (int s = 0; s < maxState; s++)
            {
                for (int last = 0; last <= N; last++)
                {
                    if (dp[s, last] == double.MaxValue) continue;

                    // 嘗試取下一個需求i
                    for (int i = 0; i < m; i++)
                    {
                        if ((s & (1 << i)) != 0) continue; // 已取
                        // 在options[i]的每個供應點
                        foreach (var opt in options[i])
                        {
                            int ni = allNodes.IndexOf(opt.Node);
                            double cost = dp[s, last] + distCost[last, ni] + opt.Price;
                            int ns = s | (1 << i);
                            if (cost < dp[ns, ni])
                            {
                                dp[ns, ni] = cost;
                                parent[ns, ni] = (s, last, i);
                            }
                        }
                    }
                }
            }

            // 找最終狀態最小cost
            int finalState = maxState - 1;
            double best = double.MaxValue;
            int endNode = -1;
            for (int v = 0; v <= N; v++)
            {
                if (dp[finalState, v] < best)
                {
                    best = dp[finalState, v];
                    endNode = v;
                }
            }

            // 回溯
            var seq = new List<Aquire_Node>();
            int cs = finalState, cv = endNode;
            while (cs != 0)
            {
                var (ps, pv, chosen) = parent[cs, cv];
                // chosen物品對應options[chosen]
                var node = allNodes[cv];
                var price = map.ObjectsAquireList[demands[chosen]]
                               .First(p => p.node == node).price;
                var item = node.Objects.First(si => si.Name.Equals(demands[chosen], StringComparison.OrdinalIgnoreCase));
                seq.Add(new Aquire_Node(node, item));
                cs = ps; cv = pv;
            }
            seq.Reverse();

            // 組結果
            var result = new Recommend_Aquire_Commodities_Path
            {
                Start_Node = origin,
                UnitMoveCost = Params.pUnit_Cost,
                Path = seq
            };
            result.Calculate_Cost();
            return result;
        }
    }
        

}



namespace Basic_Algorithms_PANCAKE
{
    public static class ILP
    {
        /// <summary>
        /// 使用 OR-Tools CpModel 硬約束解最小成本取貨路徑 (ILP/CP-SAT)。
        /// </summary>
        public static Recommend_Aquire_Commodities_Path ILP_Method(Map map, List<string> demands)
        {
            int m = demands.Count;
            var origin = Params.pStart_Node;
            var nodes = new List<Node> { origin };
            var opts = new List<List<int>>();

            // 收集 candidate nodes
            for (int i = 0; i < m; i++)
            {
                var list = new List<int>();
                foreach (var (node, price) in map.ObjectsAquireList[demands[i]])
                {
                    int idx = nodes.IndexOf(node);
                    if (idx == -1)
                    {
                        idx = nodes.Count;
                        nodes.Add(node);
                    }
                    list.Add(idx);
                }
                opts.Add(list);
            }
            int V = nodes.Count;

            // 建模
            var model = new CpModel();
            // x[i,j]: demand i 在節點 j 購買
            var x = new BoolVar[m, V];
            for (int i = 0; i < m; i++)
                for (int j = 0; j < V; j++)
                    x[i, j] = model.NewBoolVar($"x[{i},{j}]");

            // 每件 demand 必須在 exactly one node 買到
            for (int i = 0; i < m; i++)
                model.AddExactlyOne(opts[i].Select(j => x[i, j]).ToArray());

            // y[u,v]: 是否從 u 走到 v
            var y = new BoolVar[V, V];
            for (int u = 0; u < V; u++)
                for (int v = 0; v < V; v++)
                {
                    y[u, v] = model.NewBoolVar($"y[{u},{v}]");
                    if (u == v) model.Add(y[u, v] == 0);
                }

            // visited[j] = OR_i x[i,j]
            var visited = new BoolVar[V];
            for (int j = 0; j < V; j++)
            {
                visited[j] = model.NewBoolVar($"visited[{j}]");
                model.AddMaxEquality(visited[j], Enumerable.Range(0, m).Select(i => x[i, j]).ToArray());
            }

            // 流量守恆 + 環路
            for (int j = 0; j < V; j++)
            {
                var outs = Enumerable.Range(0, V).Select(v => y[j, v]).ToArray();
                var ins = Enumerable.Range(0, V).Select(u => y[u, j]).ToArray();
                if (j == 0)
                {
                    model.Add(LinearExpr.Sum(outs) == 1);
                    model.Add(LinearExpr.Sum(ins) == 1);
                }
                else
                {
                    model.Add(LinearExpr.Sum(outs) == visited[j]);
                    model.Add(LinearExpr.Sum(ins) == visited[j]);
                }
            }

            // MTZ 子迴路消除
            var order = new Google.OrTools.Sat.IntVar[V];
            for (int j = 0; j < V; j++)
                order[j] = model.NewIntVar(0, V, $"order[{j}]");
            for (int u = 1; u < V; u++)
                for (int v = 1; v < V; v++)
                    model.Add(order[u] + 1 <= order[v]).OnlyEnforceIf(y[u, v]);

            // 目標：購買成本 + 移動成本
            var terms = new List<LinearExpr>();
            for (int i = 0; i < m; i++)
                foreach (var j in opts[i])
                    terms.Add(x[i, j] * map.ObjectsAquireList[demands[i]].First(p => p.node == nodes[j]).price * 1000);
            for (int u = 0; u < V; u++)
                for (int v = 0; v < V; v++)
                {
                    long d = (long)(nodes[u].distance_to_next_Node(nodes[v]) * Params.pUnit_Cost * 1000);
                    terms.Add(y[u, v] * d);
                }
            model.Minimize(LinearExpr.Sum(terms));

            // 求解
            var solver = new CpSolver { StringParameters = "max_time_in_seconds:10" };
            var status = solver.Solve(model);
            if (status != CpSolverStatus.Optimal && status != CpSolverStatus.Feasible)
                throw new Exception("No solution found.");

            // 回建最佳路徑，記錄同節點多項目
            var result = new Recommend_Aquire_Commodities_Path
            {
                Start_Node = origin,
                UnitMoveCost = Params.pUnit_Cost
            };
            int cur = 0;
            while (true)
            {
                int next = Enumerable.Range(0, V).FirstOrDefault(v => v != 0 && solver.Value(y[cur, v]) == 1);
                if (next <= 0) break;
                // 若在同一節點有多項需求，全部記錄
                for (int i = 0; i < m; i++)
                {
                    if (solver.Value(x[i, next]) == 1)
                    {
                        var supply = nodes[next].Objects.First(si => si.Name == demands[i]);
                        result.Path.Add(new Aquire_Node(nodes[next], supply));
                    }
                }
                cur = next;
            }
            result.Calculate_Cost();
            return result;
        }
    }
}















namespace Exhaustive_PANCAKE
{
    using PANCAKE_Read_Map;
    using PANCAKE_DSLib;
    using PANCAKE_Solution;
    using PANCAKE_Params;
    public static class Exhaustive
    {
        public static Recommend_Aquire_Commodities_Path Exhaustive_Method(Map map, List<string> aquireList)
        {
            var bestPath = new Recommend_Aquire_Commodities_Path
            {
                Start_Node = Params.pStart_Node,
                UnitMoveCost = Params.pUnit_Cost
            };

            double bestCost = double.MaxValue;

            // 所有物品的排列順序
            foreach (var perm in GetPermutations(aquireList, aquireList.Count))
            {
                // 每個物品 → 可以在哪些 node 拿到
                var supplyOptions = perm.Select(item =>
                    map.ObjectsAquireList[item]
                        .Select(p => new Aquire_Node(p.node, p.node.Objects.First(si => si.Name.Equals(item, StringComparison.OrdinalIgnoreCase))))
                        .ToList()
                ).ToList();

                // 對所有組合做笛卡兒積 (所有節點選擇可能)
                foreach (var combo in CartesianProduct(supplyOptions))
                {
                    // 檢查是否有重複節點
                    var nodesUsed = new HashSet<string>();
                    if (combo.Any(an => !nodesUsed.Add($"{an.Node.Name}:{an.Item.Name}")))
                        continue;

                    var tempPath = new Recommend_Aquire_Commodities_Path
                    {
                        Start_Node = Params.pStart_Node,
                        UnitMoveCost = Params.pUnit_Cost,
                        Path = combo.ToList()
                    };

                    double cost = tempPath.Calculate_Cost();

                    if (cost < bestCost)
                    {
                        bestCost = cost;
                        bestPath = tempPath;
                    }
                }
            }

            return bestPath;
        }

        // 所有排列（遞迴）
        public static IEnumerable<List<T>> GetPermutations<T>(List<T> list, int length)
        {
            if (length == 1)
                return list.Select(t => new List<T> { t });

            return GetPermutations(list, length - 1)
                .SelectMany(t => list.Where(e => !t.Contains(e)),
                            (t1, t2) => new List<T>(t1) { t2 });
        }

        // 笛卡兒積（遞迴）
        public static IEnumerable<List<T>> CartesianProduct<T>(List<List<T>> sequences)
        {
            IEnumerable<List<T>> result = new List<List<T>>() { new List<T>() };
            foreach (var seq in sequences)
            {
                result = from accseq in result
                         from item in seq
                         select new List<T>(accseq) { item };
            }
            return result;
        }
    }
}

