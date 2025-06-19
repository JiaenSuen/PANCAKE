


namespace Genetic_Algorithm_TS_Mutaion
{
    using Metaheuristic_Interface;
    using PANCAKE_DSLib;
    using PANCAKE_Solution;
    using PANCAKE_Read_Map;

    using Tabu_Search;


    class Crossover
    {



        // Crossover 交配方法 1  Item-wise Order Crossover (IOX)
        public static Recommend_Aquire_Commodities_Path Item_wise_Order_Crossover(
            Recommend_Aquire_Commodities_Path parent1,
            Recommend_Aquire_Commodities_Path parent2
        )
        {
            int length = parent1.Path.Count;
            var childPath = new List<Aquire_Node>();
            for (int i = 0; i < length; i++)
                childPath.Add(null!);

            // 隨機產生切點
            var rand = new Random();
            int start = rand.Next(0, length);
            int end = rand.Next(start, length);

            // 記錄 parent1 的 segment 及其名稱多重集合
            var nameCounts = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
            for (int i = start; i <= end; i++)
            {
                var node = parent1.Path[i];
                childPath[i] = node;
                string name = node.Item.Name;
                if (!nameCounts.ContainsKey(name))
                    nameCounts[name] = 0;
                nameCounts[name]++;
            }

            // 將 parent2 的剩餘節點依序填入 child
            int fill_Pos = 0;
            foreach (var node in parent2.Path)
            {
                string name = node.Item.Name;
                // 如果該名稱在 segment 中出現過，先扣掉對應計數，不填入
                if (nameCounts.TryGetValue(name, out int cnt) && cnt > 0)
                {
                    nameCounts[name] = cnt - 1;
                    continue;
                }
                // 找下一個空位
                while (fill_Pos < length && childPath[fill_Pos] != null)
                    fill_Pos++;
                if (fill_Pos < length)
                {
                    childPath[fill_Pos] = node;
                    fill_Pos++;
                }
            }

            // 建立子代路徑並計算成本
            var child = new Recommend_Aquire_Commodities_Path() { Start_Node=parent1.Start_Node , UnitMoveCost = parent1.UnitMoveCost };
            child.Path = childPath;
            child.Calculate_Cost();
            return child;
        }



    }


    class GA_ts_Mutaion
    {
         

         
        public Recommend_Aquire_Commodities_Path Execute_Random_Mutation(
        Recommend_Aquire_Commodities_Path path, Map map, List<string> userDemand, int strength = 1, double rate = 0.1)
        {
            var rand = new Random();
            if (rand.NextDouble() < rate) {
                path = TS.Tabu_Search( map , userDemand , path , maxIterations:50);
            }
            return path;
        }

    }




    class Selection_Chromosome
    {

        public static Recommend_Aquire_Commodities_Path Tournament_Selection(List<Recommend_Aquire_Commodities_Path> Population)
        {
            var rand = new Random();
            int i = rand.Next(0, Population.Count);
            int j = rand.Next(0, Population.Count);
            while (i == j) j = rand.Next(0, Population.Count);

            if (Population[i].Cost < Population[j].Cost) return Population[i];
            else return Population[j];
        }




    }




    class GA_ts
    {
        public static List<Recommend_Aquire_Commodities_Path> Genetic_Evolution(
            Map map,
            List<string> userDemand,
            int populationSize = 100,
            int generations = 100,
            double crossoverRate = 0.8,
            int mutationStrength = 3,
            double mutationRate = 0.2,
             List<Recommend_Aquire_Commodities_Path?>? extra_init_Pop = null
            )
        {

            
            
            
            var population = MH_init_Utils.Generate_RACP_Population(map, userDemand, populationSize , extra_init_Pop!);
            var rand = new Random();
            var mutator = new GA_ts_Mutaion();
            var Global_Iteration_Best = population.OrderBy(p => p.Cost).First();


            for (int gen = 0; gen < generations; gen++) // Start Evolution Iteration
            {
                var newPopulation = new List<Recommend_Aquire_Commodities_Path>(populationSize);
                var best = population.OrderBy(p => p.Cost).First();

                while (newPopulation.Count < populationSize)
                {
                    var parent1 = Selection_Chromosome.Tournament_Selection(population);
                    var parent2 = Selection_Chromosome.Tournament_Selection(population);
                    Recommend_Aquire_Commodities_Path child;
                    if (rand.NextDouble() < crossoverRate)
                        child = Crossover.Item_wise_Order_Crossover(parent1, parent2);
                    else
                    {
                        child = new Recommend_Aquire_Commodities_Path
                        {
                            Path = new List<Aquire_Node>(parent1.Path)
                        };// 未交配則複製父1
                        child.Calculate_Cost();
                    }
                    child = mutator.Execute_Random_Mutation(child, map, userDemand , mutationStrength, mutationRate);
                    newPopulation.Add(child);
                }
                var worstIndex = newPopulation
                    .Select((p, idx) => new { p.Cost, idx })
                    .OrderByDescending(x => x.Cost)
                    .First().idx;
                newPopulation[worstIndex] = best;

                // 更新族群
                population = newPopulation;
                var Current_Best = population.OrderBy(p => p.Cost).First();
                if (Current_Best.Cost < Global_Iteration_Best.Cost) Global_Iteration_Best = Current_Best;
            }

            population.Add(Global_Iteration_Best);
            return population.OrderBy(p => p.Cost).ToList();
        }
        

    }




}