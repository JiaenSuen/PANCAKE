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

        public double distance_to_next_Node(Node next_node) {
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