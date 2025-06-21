
using PANCAKE_DSLib;
using PANCAKE_Read_Map;

namespace PANCAKE_Evaluation_Utils
{
    


    public class Aquire_Node
    {
        public Node Node { get; set; }           // 取貨的節點
        public SupplyItem Item { get; set; }     // 在該節點取得的物品（含價格）

        public Aquire_Node(Node node, SupplyItem item) {
            Node = node;
            Item = item;
        }

        public override string ToString()
            => $"{Node.Name} -> {Item.Name}({Item.Price})";
    }

    public class Recommend_Aquire_Commodities_Path {
        public List<Aquire_Node> Path { get; set; } = new List<Aquire_Node>();
        public double Cost { get; private set; } // 累計的總成本（移動距離*單位距離花費價格 + 購買價格）

        Node Start_Node = new Node("Origin", 0, 0,  new List<SupplyItem>());
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