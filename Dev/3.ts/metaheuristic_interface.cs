using PANCAKE_Read_Map;
using PANCAKE_DSLib;
using PANCAKE_Solution;

using Exhaustive_PANCAKE;
using Basic_Algorithms_PANCAKE;

namespace Metaheuristic_Interface
{

    class MH_Utils
    {
        static public Recommend_Aquire_Commodities_Path Generate_Random_RAC_Path(Map map, List<string> Require_List)
        {
            var rand = new Random();


            var thePath = new Recommend_Aquire_Commodities_Path();

            while (Require_List.Count != 0)
            {
                string current_search_commodite = Require_List[rand.Next(Require_List.Count)];

                var (target_node, _) = map.ObjectsAquireList[current_search_commodite][rand.Next(map.ObjectsAquireList[current_search_commodite].Count)];
                var item = target_node.Objects.FirstOrDefault(obj => obj.Name == current_search_commodite);
                if (item == null) throw new Exception($"在指定節點中找不到名稱為 {current_search_commodite} 的物品");
                var Current_Aquire_Node = new Aquire_Node(target_node, item);
                thePath.Path.Add(Current_Aquire_Node);

                Require_List.Remove(current_search_commodite);
            }
            thePath.Calculate_Cost();
            return thePath;

        }
    }





    




}