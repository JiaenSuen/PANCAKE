using PANCAKE_Read_Map;
using PANCAKE_DSLib;
using PANCAKE_Solution;

using Exhaustive_PANCAKE;
using Basic_Algorithms_PANCAKE;

namespace Metaheuristic_Interface
{

    class MH_init_Utils
    {
        static public Random rand = new Random();


        static public void rand_seed(int seed)
        {
            rand = new Random(seed);
        }

        static public Recommend_Aquire_Commodities_Path Generate_Random_RAC_Path(Map map, List<string> Require_List_input)
        {

            List<string> Require_List = new List<string>(Require_List_input);


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







        static public List<Recommend_Aquire_Commodities_Path> Generate_RACP_Population(Map map, List<string> Require_List_input,
         int Num_of_Population = 10, List<Recommend_Aquire_Commodities_Path>? extra_init_Pop = null)
        {
            List<Recommend_Aquire_Commodities_Path> Population = new List<Recommend_Aquire_Commodities_Path>();
            for (int i = 0; i < Num_of_Population; i++)
                Population.Add(Generate_Random_RAC_Path(map,Require_List_input));

            if (extra_init_Pop != null)
                Population.AddRange(extra_init_Pop);


            return Population;
        }   







    }

}