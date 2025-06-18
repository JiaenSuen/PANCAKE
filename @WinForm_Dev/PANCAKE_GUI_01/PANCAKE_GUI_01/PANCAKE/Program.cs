using PANCAKE_Read_Map;
using PANCAKE_DSLib;
using PANCAKE_Solution;

using Exhaustive_PANCAKE;
using Basic_Algorithms_PANCAKE;

using Metaheuristic_Interface;
using Tabu_Search;
using Genetic_Algorithm;

using System.Runtime.InteropServices;

/*
class Program
{
    static void Main(string[] args)
    {
        var map = MapLoader.Read_CSV_From_Map("datasets/map6.csv");
        var userDemand = new List<string> {
            "Water", "Bread",  "Battery", "ChessBurger" , "Fuel" , "Tissue",
            "Flashlight","Fruit","Vegetables","FirstAid", "Towel","Juice",
            "Toothpaste","Hotdog","Soda","Coffee","Soap","Chocolate",
            "Compass","BeefBurger","RiceBall","Hotdog"
        };
        //userDemand = userDemand.Distinct().ToList();
        var userDemand_counts = userDemand.GroupBy(item => item).ToDictionary(g => g.Key, g => g.Count());




        map.ObjectsAquireList.show_All_Commidites_on_Map();
        Console.WriteLine("========================================================");
        var greed_result = Greedy.Greedy_Method(map, userDemand);
        Console.WriteLine(greed_result);


        Console.WriteLine("========================================================");
        List<Recommend_Aquire_Commodities_Path> extra_pop = new List<Recommend_Aquire_Commodities_Path>();
        var TS_result = TS.Tabu_Search(map, userDemand, maxIterations: 500);
        Console.WriteLine(TS_result);
        Console.WriteLine("========================================================");
        extra_pop.Add(TS_result);
        var GA_result =  GA.Genetic_Evolution(map, userDemand ,500, extra_init_Pop:extra_pop!);
        Console.WriteLine( GA_result[0] );
        Console.WriteLine("========================================================");
        Console.WriteLine(TS.Tabu_Search(map, userDemand,GA_result[0] , maxIterations:500 , 50 , 60 ));
    }


    

}
 */