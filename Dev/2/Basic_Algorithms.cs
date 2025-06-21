using PANCAKE_Read_Map;
using PANCAKE_DSLib;
using PANCAKE_Evaluation_Utils;







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
                Start_Node = new Node("Origin", 0, 0, new List<SupplyItem>()),
                UnitMoveCost = 0.5
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


    
}




















namespace Exhaustive_PANCAKE
{
    public static class Exhaustive
    {
        public static Recommend_Aquire_Commodities_Path Exhaustive_Method(Map map, List<string> aquireList)
        {
            var bestPath = new Recommend_Aquire_Commodities_Path
            {
                Start_Node = new Node("Origin", 0, 0, new List<SupplyItem>()),
                UnitMoveCost = 0.5
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
                        Start_Node = new Node("Origin", 0, 0, new List<SupplyItem>()),
                        UnitMoveCost = 0.5,
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

