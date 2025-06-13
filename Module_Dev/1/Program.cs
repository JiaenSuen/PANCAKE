using PANCAKE_Read_Map;
using PANCAKE_DSLib;
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

    }



}



class Evaluation_Utils
{

    class Aquire_Node
    {
        string Target_Aquire_Object = ""; // 獲取目標物品 ， ex. "Bread"
        string Target_AO_Node = "";    // 在哪裡獲取該物品 ， ex. "Shop_Laplcae"
    }

    class Recommend_Aquire_Commodities_Path // Solution
    {
        List<Aquire_Node> Path = new List<Aquire_Node>;
        double Cost;

        
    }

}