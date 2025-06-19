using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Whale_optimization_TS
{
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using PANCAKE_Read_Map;
    using PANCAKE_DSLib;
    using PANCAKE_Solution;
    using PANCAKE_Params;

    using Tabu_Search;
    using System.IO;
    using Basic_Algorithms_PANCAKE;





    /// 離散鯨魚優化演算法 (Discrete Whale Optimization Algorithm) 用於最小成本取貨路徑。
    /// 包含三種行為：Encircle, Spiral, Exploration。

    public class Whale_ts
    {
        public Recommend_Aquire_Commodities_Path Solution { get; private set; }
        public double Cost => Solution.Cost;

        private static Random rng = new Random();
        private List<string> demands;
        private Map map;

        public Whale_ts(Map map, List<string> demands)
        {
            this.map = map;
            this.demands = new List<string>(demands);
            // 初始解: 隨機生成一條路徑
            Solution = Metaheuristic_Interface.MH_init_Utils.Generate_Random_RAC_Path(map, demands);
        }

        /// Encircle: SwapTowardBest — 讓當前解更靠近 global best。
        private void SwapTowardBest(Recommend_Aquire_Commodities_Path best, double A)
        {
            var path = Solution.Path;
            int n = path.Count;
            int m = (int)Math.Ceiling(Math.Abs(A) * n / 2.0);
            for (int k = 0; k < m; k++)
            {
                int i = rng.Next(n);
                // 找 best 上同商品的位置
                string name = path[i].Item.Name;
                int bpos = best.Path.FindIndex(an => an.Item.Name == name);
                if (bpos >= 0 && bpos < n && bpos != i)
                {
                    // 交換位置
                    var tmp = path[i];
                    path[i] = path[bpos];
                    path[bpos] = tmp;
                }
            }
            Solution.Calculate_Cost();
        }

        /// Spiral: TwoOptReverse — 局部子序列反轉。
        private void TwoOptReverse()
        {
            var path = Solution.Path;
            int n = path.Count;
            if (n < 2) return;
            int i = rng.Next(n - 1);
            int j = rng.Next(i + 1, n);
            path.Reverse(i, j - i + 1);
            Solution.Calculate_Cost();
        }

        /// Exploration: BlockShuffle — 隨機切段並重插。
        private void BlockShuffle()
        {
            var path = Solution.Path;
            int n = path.Count;
            if (n < 2) return;
            int i = rng.Next(n);
            int j = rng.Next(n);
            if (i > j) { int t = i; i = j; j = t; }
            var segment = path.GetRange(i, j - i + 1);
            path.RemoveRange(i, j - i + 1);
            int pos = rng.Next(path.Count + 1);
            path.InsertRange(pos, segment);
            Solution.Calculate_Cost();
        }

        /// ChangeSource: 對隨機一項商品，改變其購買節點。
        private void ChangeSource(int strength)
        {
            var path = Solution.Path;
            int n = path.Count;
            for (int k = 0; k < strength; k++)
            {
                int idx = rng.Next(n);
                string commodity = path[idx].Item.Name;
                var candidates = map.ObjectsAquireList[commodity]
                                    .Where(t => !t.node.Equals(path[idx].Node))
                                    .ToList();
                if (candidates.Count > 0)
                {
                    var (node, price) = candidates[rng.Next(candidates.Count)];
                    path[idx] = new Aquire_Node(node, new SupplyItem(commodity, price));
                }
            }
            Solution.Calculate_Cost();
        }

   
        /// 更新操作：根据 A, p 决定三种行为。
        public Whale_ts Update(Whale_ts best, Whale_ts randWhale, double a, double p)
        {
            // 複製自身
            var offspring = new Whale_ts(map, demands) { Solution = ClonePath(this.Solution) };
            double r = rng.NextDouble();
            double A = 2 * a * r - a;

            if (p < 0.5)
            {
                if (Math.Abs(A) < 1.0)
                {
                    // Encircle
                    offspring.SwapTowardBest(best.Solution, A);
                }
                else
                {
                    // Exploration towards random whale + 大跳躍
                    offspring.Solution = ClonePath(randWhale.Solution);
                    offspring.BlockShuffle();
                }
                // change source lightly
                offspring.ChangeSource(1);
            }
            else
            {
                // Spiral
                offspring.TwoOptReverse();
                offspring.ChangeSource(1);
            }

            if (rng.NextDouble() < 0.08) TS.Tabu_Search(this.map, this.demands, this.Solution , maxIterations: 100 , neighborCount:20 ,tabuListSize:30);
            return offspring;
        }

        private Recommend_Aquire_Commodities_Path ClonePath(Recommend_Aquire_Commodities_Path src)
        {
            var clone = new Recommend_Aquire_Commodities_Path
            {
                Start_Node = src.Start_Node,
                UnitMoveCost = src.UnitMoveCost,
                Path = src.Path.Select(an => new Aquire_Node(an.Node, new SupplyItem(an.Item.Name, an.Item.Price))).ToList()
            };
            clone.Calculate_Cost();
            return clone;
        }
    }

    public static class WOA_ts
    {
     
        /// 離散鯨魚優化主函數
        private static Random rng = new Random();
        public static Recommend_Aquire_Commodities_Path Optimize(
            Map map,
            List<string> demands,
            int numWhales = 20,
            int maxIter = 200)
        {
            // 1. 初始化種群
            var pop = new List<Whale_ts>();
            for (int i = 0; i < numWhales; i++)
                pop.Add(new Whale_ts(map, demands));

             

            // 2. 初始最佳
            Whale_ts best = pop.OrderBy(w => w.Cost).First();

            // 3. 迭代
            for (int iter = 1; iter <= maxIter; iter++)
            {
                double a = 2.0 * (1.0 - (double)iter / maxIter);
                for (int i = 0; i < numWhales; i++)
                {
                    int randIdx;
                    do { randIdx = rng.Next(numWhales); } while (randIdx == i);
                    Whale_ts cur = pop[i];
                    Whale_ts randWhale = pop[randIdx];
                    double p = rng.NextDouble();
                    var offspring = cur.Update(best, randWhale, a, p);
                    // 保留更好者
                    if (offspring.Cost < cur.Cost)
                        pop[i] = offspring;
                }
                // 更新全局最佳
                var currentBest = pop.OrderBy(w => w.Cost).First();
                if (currentBest.Cost < best.Cost)
                    best = currentBest;
            }
            return best.Solution;
        }
    }
   

}
