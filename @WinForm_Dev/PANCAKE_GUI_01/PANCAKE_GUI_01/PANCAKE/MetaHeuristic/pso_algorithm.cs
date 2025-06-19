 
using System;
using System.Collections.Generic;
using System.Linq;
using PANCAKE_Read_Map;
using PANCAKE_DSLib;
using PANCAKE_Solution;
using PANCAKE_Params;

namespace Discrete_PSO
{ 
    /// 離散粒子群優化 (Discrete PSO) 用於最小成本取貨路徑。
    /// 核心：每隻粒子記錄當前解、個人最優、透過通訊機率獲得全域最優。
    /// 更新：結合慣性、認知、社會三個部分，以離散交換或反轉操作實現。
 
    public class Particle
    {
        public Recommend_Aquire_Commodities_Path Position { get; private set; }
        public Recommend_Aquire_Commodities_Path PersonalBest { get; private set; }
        public double PersonalBestCost { get; private set; }

        private static Random rng = new Random();
        private Map map;
        private List<string> demands;

        public Particle(Map map, List<string> demands)
        {
            this.map = map;
            this.demands = new List<string>(demands);
            // 初始化位置為隨機路徑
            Position = Metaheuristic_Interface.MH_init_Utils.Generate_Random_RAC_Path(map, demands);
            PersonalBest = ClonePath(Position);
            PersonalBestCost = PersonalBest.Cost;
        }

        // Encircle towards a target solution: swap items to match target
        private void MoveToward(Recommend_Aquire_Commodities_Path target, double fraction)
        {
            var path = Position.Path;
            int n = path.Count;
            int m = (int)Math.Ceiling(fraction * n);
            for (int k = 0; k < m; k++)
            {
                int i = rng.Next(n);
                string name = path[i].Item.Name;
                int tpos = target.Path.FindIndex(an => an.Item.Name == name);
                if (tpos >= 0 && tpos < n && tpos != i)
                    path.Swap(i, tpos);
            }
            Position.Calculate_Cost();
        }

        // Spiral: local two-opt reversal
        private void TwoOpt()
        {
            Position.Path.TwoOptReverse(rng);
            Position.Calculate_Cost();
        }

        // Exploration: change source of one random item
        private void ChangeSource()
        {
            Position.Path.ChangeSource(map, rng);
        }

        private Recommend_Aquire_Commodities_Path ClonePath(Recommend_Aquire_Commodities_Path src)
        {
            var clone = new Recommend_Aquire_Commodities_Path
            {
                Start_Node = src.Start_Node,
                UnitMoveCost = src.UnitMoveCost,
                Path = src.Path.Select(an => new Aquire_Node(an.Node, new SupplyItem(an.Item.Name, an.Item.Price))).ToList()
            };
            clone.Calculate_Cost(); return clone;
        }

        /// <summary>
        /// 更新位置
        /// w: 慣性權重, c1: 個人, c2: 社會
        /// gbest: 粒子所看到的全域最優
        /// </summary>
        public void Update(Recommend_Aquire_Commodities_Path gbest, double w, double c1, double c2)
        {
            // 1. 慣性保留部分：small local tweak
            if (rng.NextDouble() < w)
                TwoOpt();

            // 2. 個體學習
            if (rng.NextDouble() < c1)
                MoveToward(PersonalBest, rng.NextDouble());

            // 3. 社會學習
            if (rng.NextDouble() < c2)
                MoveToward(gbest, rng.NextDouble());

            // 4. 隨機探索
            if (rng.NextDouble() < (1 - w))
                ChangeSource();

            // 更新個人最優
            if (Position.Cost < PersonalBestCost)
            {
                PersonalBest = ClonePath(Position);
                PersonalBestCost = Position.Cost;
            }
        }
    }

    public static class PSO
    {
      
        /// 離散PSO主控：
        /// 1. 初始化粒子群
        /// 2. 迭代更新：依通訊機率決定是否傳遞真實全域最優
        /// 3. 更新個體位置、個人最優及全域最優
 
        private static Random rng = new Random();
        public static Recommend_Aquire_Commodities_Path Optimize(
            Map map,
            List<string> demands,
            int numParticles = 30,
            int maxIter = 200,
            double w = 0.5,
            double c1 = 1.0,
            double c2 = 1.5)
        {
            // 1. 初始化
            var particles = new List<Particle>();
            for (int i = 0; i < numParticles; i++)
                particles.Add(new Particle(map, demands));

            // 初始全域最優為族群中最好
            var gbest = particles.Select(p => p.PersonalBest)
                                 .OrderBy(p => p.Cost).First();
            double gbestCost = gbest.Cost;

            // 2. 迭代
            for (int iter = 1; iter <= maxIter; iter++)
            {
                // 通訊機率：隨迭代線性增加
                double commProb = (double)iter / maxIter;

                foreach (var p in particles)
                {
                    // 通訊選擇：以 prob 決定是否告知真實全域最優，否則使用當前 gbest
                    Recommend_Aquire_Commodities_Path infoG;
                    if (rng.NextDouble() < commProb)
                        infoG = gbest;
                    else
                        infoG = particles[rng.Next(particles.Count)].PersonalBest;

                    p.Update(infoG, w, c1, c2);
                }

                // 更新 gbest
                var candidate = particles.Select(p => p.PersonalBest)
                                         .OrderBy(p => p.Cost).First();
                if (candidate.Cost < gbestCost)
                {
                    gbest = candidate;
                    gbestCost = gbest.Cost;
                }
            }

            return gbest;
        }
    }

    // 擴充方法
    public static class Extensions
    {
        public static void Swap(this List<Aquire_Node> list, int i, int j)
        {
            var tmp = list[i]; list[i] = list[j]; list[j] = tmp;
        }
        public static void TwoOptReverse(this List<Aquire_Node> list, Random rng)
        {
            int n = list.Count;
            if (n < 2) return;
            int i = rng.Next(n - 1);
            int j = rng.Next(i + 1, n);
            list.Reverse(i, j - i + 1);
        }
        public static void ChangeSource(this List<Aquire_Node> path, Map map, Random rng)
        {
            int n = path.Count;
            int idx = rng.Next(n);
            string commodity = path[idx].Item.Name;
            var candidates = map.ObjectsAquireList[commodity]
                                .Where(t => !t.node.Equals(path[idx].Node)).ToList();
            if (candidates.Count == 0) return;
            var (node, price) = candidates[rng.Next(candidates.Count)];
            path[idx] = new Aquire_Node(node, new SupplyItem(commodity, price));
        }
    }
}
