using System;
using System.Collections.Generic;
using System.IO;

using PANCAKE_DSLib;

namespace PANCAKE_Read_Map
{

    


    public class Map
    {
        // 物品 → 節點
        public Aquire_List ObjectsAquireList { get; private set; }
        // 所有節點
        public List<Node> Nodes { get; private set; }

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

            // 跳過表頭
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