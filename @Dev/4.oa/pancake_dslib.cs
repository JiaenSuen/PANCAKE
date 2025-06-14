namespace PANCAKE_DSLib
{
    public class SupplyItem
    {
        public string Name { get; set; }
        public int Price { get; set; }

        public SupplyItem(string name, int price)
        {
            Name = name;
            Price = price;
        }

        public override string ToString()
            => $"{Name}({Price})";
    }



    public class Node
    {
        public string Name;
        public int Location_X;
        public int Location_Y;
        public List<SupplyItem> Objects;

        public Node(string name, int x, int y, IEnumerable<SupplyItem> objects)
        {
            Name = name;
            Location_X = x;
            Location_Y = y;
            Objects = new List<SupplyItem>(objects);
        }

        public override string ToString()
            => $"{Name} ({Location_X},{Location_Y})";

        public double distance_to_next_Node(Node next_node)
        {
            int deltaX = next_node.Location_X - this.Location_X;
            int deltaY = next_node.Location_Y - this.Location_Y;
            return Math.Sqrt(deltaX * deltaX + deltaY * deltaY);
        }
    }





    // Hash Map - > 由 string 取得該物件可以在哪裡取得
    // 介面設計 :  Aquire_List["Ham"] - > Return List<Node> Shop_A , Shop_C ...
    public class Aquire_List
    {
        // Key = 物品名稱, Value = 各節點中供應該物品的 SupplyItemInfo
        private Dictionary<string, List<(Node node, int price)>> map
            = new Dictionary<string, List<(Node, int)>>(StringComparer.OrdinalIgnoreCase);

        // 索引器：Aquire_List["Water"] → List<(Node, Price)>
        public List<(Node node, int price)> this[string objName]
        {
            get
            {
                if (map.TryGetValue(objName, out var list))
                    return list;
                return new List<(Node, int)>();
            }
        }

        // 新增一筆映射：某 node 賣 objName 這個物品，售價 price
        public void Add(string objName, Node node, int price)
        {
            if (!map.ContainsKey(objName))
                map[objName] = new List<(Node, int)>();
            map[objName].Add((node, price));
        }

        public IEnumerable<string> AllObjects => map.Keys;
    }


}








namespace PANCAKE_Solution
{   
    
    using PANCAKE_DSLib;
    using PANCAKE_Read_Map;
    


    // 增量成本 = 距離(current → node) × 單位距離成本 + 該物品在 node 的售價
    public class Aquire_Node
    {
        public Node Node { get; set; }           // 取貨的節點
        public SupplyItem Item { get; set; }     // 在該節點取得的物品（含價格）

        public Aquire_Node(Node node, SupplyItem item)
        {
            Node = node;
            Item = item;
        }

        public override string ToString()
            => $"{Node.Name} -> {Item.Name}({Item.Price})";
    }

    public class Recommend_Aquire_Commodities_Path {
        public List<Aquire_Node> Path { get; set; } = new List<Aquire_Node>();
        public double Cost { get; private set; } // 累計的總成本（移動距離*單位距離花費價格 + 購買價格）

        public Node Start_Node = new Node("Origin", 0, 0,  new List<SupplyItem>());
        public double UnitMoveCost { get; set; } = 0.5; 

        public double Calculate_Cost()
        {
            double total = 0.0;

            // 購物成本
            foreach (var step in Path)
                total += step.Item.Price;

            // 出發點到第一個取貨點的距離
            if (Start_Node != null && Path.Count > 0)
            {
                double startToFirst = Start_Node.distance_to_next_Node(Path[0].Node);
                total += startToFirst * UnitMoveCost;
            }

            // 每段節點間移動距離
            for (int i = 0; i < Path.Count - 1; i++)
            {
                var from = Path[i].Node;
                var to = Path[i + 1].Node;
                total += from.distance_to_next_Node(to) * UnitMoveCost;
            }

            Cost = total;
            return total;
        }

        public override string ToString()
        {
            var sb = new System.Text.StringBuilder();
            sb.AppendLine("=== 推薦取貨路徑 ===");
            if (Start_Node != null)
                sb.AppendLine($"出發點：{Start_Node.Name}");

            foreach (var step in Path)
                sb.AppendLine($"  {step}");

            sb.AppendLine($"-- 總成本（距離*{UnitMoveCost} + 價格）：{Cost:F2}");
            return sb.ToString();
        }
    }

}









namespace PANCAKE_Read_Map
{

    using PANCAKE_DSLib;


    public class Map
    {

        public Aquire_List ObjectsAquireList { get; private set; }  // 物品名稱 → 節點 List
        public List<Node> Nodes { get; private set; }  // 所有節點

        public Map()
        {
            ObjectsAquireList = new Aquire_List();
            Nodes = new List<Node>();
        }
        
        
    }


    public static class MapLoader
    {
        public static Map Read_CSV_From_Map(string filePath)
        {
            var map = new Map();
            var lines = File.ReadAllLines(filePath);
            if (lines.Length <= 1)
                throw new Exception("CSV 內容不夠。");

             
            for (int i = 1; i < lines.Length; i++)
            {
                var cols = ParseCsvLine(lines[i]);
                if (cols.Count < 4) continue;
                if (cols[0] == "Node_Name") continue;

                string name = cols[0];
                if (!int.TryParse(cols[1], out int x)) continue;
                if (!int.TryParse(cols[2], out int y)) continue;

                // 解析 Objects 欄位：形如 ["Water:15", "Food:10", ...]
                var supplyList = new List<SupplyItem>();
                var items = cols[3]
                    .Split(new[] { ';' }, StringSplitOptions.RemoveEmptyEntries);
                foreach (var it in items)
                {
                    var parts = it.Split(':');
                    if (parts.Length != 2) continue;
                    string itemName = parts[0].Trim();
                    if (!int.TryParse(parts[1], out int price)) continue;
                    supplyList.Add(new SupplyItem(itemName, price));
                }

                // 建立 Node
                var node = new Node(name, x, y, supplyList);
                map.Nodes.Add(node);

                // 註冊到 Aquire_List
                foreach (var si in supplyList)
                {
                    map.ObjectsAquireList.Add(si.Name, node, si.Price);
                }
            }

            return map;
        }

        // 前面相同：支援雙引號的簡易 CSV 解析
        private static List<string> ParseCsvLine(string line)
        {
            var result = new List<string>();
            bool inQuotes = false;
            var cur = "";
            foreach (char ch in line)
            {
                if (ch == '"') { inQuotes = !inQuotes; continue; }
                if (ch == ',' && !inQuotes)
                {
                    result.Add(cur);
                    cur = "";
                }
                else cur += ch;
            }
            result.Add(cur);
            return result;
        }
    }

}