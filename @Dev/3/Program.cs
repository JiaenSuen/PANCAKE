using PANCAKE_Read_Map;
using PANCAKE_DSLib;
using PANCAKE_Solution;

using Exhaustive_PANCAKE;
using Basic_Algorithms_PANCAKE;

class Program
{
    static void Main(string[] args)
    {
        var map = MapLoader.Read_CSV_From_Map("datasets/map2.csv");
        var userDemand = new List<string> {
            "Water", "Bread",  "Battery", "ChessBurger","Fuel",
            "MilkTea","Burger","BeefBurger","BeefBurger"
        };


        var solution = Greedy_Method(map, userDemand);
        Console.WriteLine(solution);


        //var solution2 = Exhaustive.Exhaustive_Method(map, userDemand);
        //Console.WriteLine(solution2);
    }



    static Recommend_Aquire_Commodities_Path Greedy_Method(Map map, List<string> Aquire_List)
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

            if (bestNode == null || bestItem == null || bestItemName == null){
                Console.WriteLine("[Error] 無法再找到任何符合的取購點，提前結束。");
                break;
            }
            path.Path.Add(new Aquire_Node(bestNode, bestItem));
            // 並從需求清單移除
            Aquire_List.Remove(bestItemName);
        } // End Construct Aquire Commodities Path
        path.Calculate_Cost();
        return path;
    }









}


