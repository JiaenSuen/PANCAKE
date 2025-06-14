using PANCAKE_Read_Map;
using PANCAKE_DSLib;
using PANCAKE_Solution;

using Exhaustive_PANCAKE;
using Basic_Algorithms_PANCAKE;

using Metaheuristic_Interface;
using Tabu_Search;
class Program
{
    static void Main(string[] args)
    {
        var map = MapLoader.Read_CSV_From_Map("datasets/map6.csv");
        var userDemand = new List<string> {
            "Water", "Bread",  "Battery", "ChessBurger","Fuel",
            "Toothpaste", "Shampoo", "Soap",
            "ChessBurger", "BeefBurger", "Milktea",
           
        };

        Console.WriteLine();

        Console.WriteLine("Greedy");
        var Greedy_RAC_Path = Greedy.Greedy_Method(map, userDemand);
        Console.WriteLine(Greedy_RAC_Path);

        Console.WriteLine("Random");
        var Random_RAC_Path = MH_Utils.Generate_Random_RAC_Path(map, userDemand);
        Console.WriteLine(Random_RAC_Path);

        Console.WriteLine("Random + TS");
        var new_path = TS.Tabu_Search(map, userDemand, Random_RAC_Path, 400, 30, 60);
        Console.WriteLine(new_path);
        
        Console.WriteLine("Greedy + TS");
        var new_gts_path = TS.Tabu_Search( map, userDemand ,  Greedy_RAC_Path , 400 , 30 , 60);
        Console.WriteLine(new_gts_path);
    }





    



}


