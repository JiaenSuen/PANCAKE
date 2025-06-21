using PANCAKE_Read_Map;
using PANCAKE_DSLib;
using PANCAKE_Evaluation_Utils;

class Program
{
    static void Main(string[] args)
    {
        var map = MapLoader.Read_CSV_From_Map("map.csv");

        // 列出每個節點及其售價清單
        Console.WriteLine("節點 & 可購物品：");
        foreach (var n in map.Nodes)
        {
            Console.WriteLine($"- {n}");
            foreach (var si in n.Objects)
                Console.WriteLine($"    {si}");
        }

        // 列出各物品在哪些節點能買到 & 價格
        Console.WriteLine("\n物品取得地點與價格：");
        foreach (var obj in map.ObjectsAquireList.AllObjects)
        {
            Console.WriteLine($"* {obj}:");
            foreach (var (node, price) in map.ObjectsAquireList[obj])
                Console.WriteLine($"    {node.Name} @({node.Location_X},{node.Location_Y}) → {price}");
        }

        Console.WriteLine("\n\n");
        List<SupplyItem> emptySupplies = new List<SupplyItem>();
        foreach (var node in map.Nodes)
        {
            Node origin = new Node("Origin", 0, 0, emptySupplies);
            Console.WriteLine($"Distance O to {node.Name} , {node.distance_to_next_Node(origin)}");
        }

        Console.WriteLine("\n\n");
        var solution = new Recommend_Aquire_Commodities_Path();
        
        solution.Path.Add(new Aquire_Node(map.Nodes[0], map.Nodes[0].Objects.First(o => o.Name == "Water")));
        solution.Path.Add(new Aquire_Node(map.Nodes[1], map.Nodes[1].Objects.First(o => o.Name == "Battery")));

        solution.Calculate_Cost();
        Console.WriteLine(solution);
    }



}


