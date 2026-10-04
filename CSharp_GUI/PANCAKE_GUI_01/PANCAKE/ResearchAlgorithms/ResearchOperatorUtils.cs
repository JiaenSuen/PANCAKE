using PANCAKE_DSLib;
using PANCAKE_Read_Map;
using PANCAKE_Solution;

namespace PANCAKE_ResearchAlgorithms
{
    internal enum ResearchMove
    {
        Swap,
        Reverse,
        Insert,
        Source,
        Joint,
        Block
    }

    internal static class ResearchOperatorUtils
    {
        public static Recommend_Aquire_Commodities_Path ClonePath(Recommend_Aquire_Commodities_Path src)
        {
            var clone = new Recommend_Aquire_Commodities_Path
            {
                Start_Node = src.Start_Node,
                UnitMoveCost = src.UnitMoveCost,
                Path = src.Path
                    .Select(an => new Aquire_Node(an.Node, new SupplyItem(an.Item.Name, an.Item.Price)))
                    .ToList()
            };
            clone.Calculate_Cost();
            return clone;
        }

        public static Recommend_Aquire_Commodities_Path RandomPath(Map map, List<string> demands)
        {
            return Metaheuristic_Interface.MH_init_Utils.Generate_Random_RAC_Path(map, demands);
        }

        public static void Swap(Recommend_Aquire_Commodities_Path s, Random rng)
        {
            if (s.Path.Count < 2) return;
            int i = rng.Next(s.Path.Count);
            int j;
            do j = rng.Next(s.Path.Count); while (j == i);
            (s.Path[i], s.Path[j]) = (s.Path[j], s.Path[i]);
            s.Calculate_Cost();
        }

        public static void Reverse(Recommend_Aquire_Commodities_Path s, Random rng)
        {
            if (s.Path.Count < 2) return;
            int i = rng.Next(s.Path.Count);
            int j = rng.Next(s.Path.Count);
            if (i > j) (i, j) = (j, i);
            if (i == j) return;
            s.Path.Reverse(i, j - i + 1);
            s.Calculate_Cost();
        }

        public static void Insert(Recommend_Aquire_Commodities_Path s, Random rng)
        {
            if (s.Path.Count < 3) return;
            int i = rng.Next(s.Path.Count);
            int j = rng.Next(s.Path.Count);
            if (i == j) return;
            var item = s.Path[i];
            s.Path.RemoveAt(i);
            if (j > s.Path.Count) j = s.Path.Count;
            s.Path.Insert(j, item);
            s.Calculate_Cost();
        }

        public static void BlockRelocate(Recommend_Aquire_Commodities_Path s, Random rng)
        {
            int n = s.Path.Count;
            if (n < 4) return;
            int i = rng.Next(n);
            int j = rng.Next(n);
            if (i > j) (i, j) = (j, i);
            if (i == j) return;
            var segment = s.Path.GetRange(i, j - i + 1);
            s.Path.RemoveRange(i, j - i + 1);
            int pos = rng.Next(s.Path.Count + 1);
            s.Path.InsertRange(pos, segment);
            s.Calculate_Cost();
        }

        public static void ChangeSource(Map map, Recommend_Aquire_Commodities_Path s, Random rng)
        {
            if (s.Path.Count == 0) return;
            int idx = rng.Next(s.Path.Count);
            string commodity = s.Path[idx].Item.Name;
            var choices = map.ObjectsAquireList[commodity]
                .Where(x => !ReferenceEquals(x.node, s.Path[idx].Node))
                .ToList();
            if (choices.Count == 0) return;
            var (node, price) = choices[rng.Next(choices.Count)];
            s.Path[idx] = new Aquire_Node(node, new SupplyItem(commodity, price));
            s.Calculate_Cost();
        }

        public static void JointMove(Map map, Recommend_Aquire_Commodities_Path s, Random rng)
        {
            if (s.Path.Count < 2) return;
            int oldPos = rng.Next(s.Path.Count);
            var step = s.Path[oldPos];
            s.Path.RemoveAt(oldPos);
            int newPos = rng.Next(s.Path.Count + 1);
            s.Path.Insert(newPos, step);

            string commodity = step.Item.Name;
            Node? prev = newPos == 0 ? s.Start_Node : s.Path[newPos - 1].Node;
            Node? next = newPos == s.Path.Count - 1 ? null : s.Path[newPos + 1].Node;

            double bestProxy = double.PositiveInfinity;
            Aquire_Node? bestStep = null;
            foreach (var (node, price) in map.ObjectsAquireList[commodity])
            {
                double proxy = price;
                if (prev != null) proxy += prev.distance_to_next_Node(node) * s.UnitMoveCost;
                if (next != null) proxy += node.distance_to_next_Node(next) * s.UnitMoveCost;
                if (proxy < bestProxy)
                {
                    bestProxy = proxy;
                    bestStep = new Aquire_Node(node, new SupplyItem(commodity, price));
                }
            }
            if (bestStep != null) s.Path[newPos] = bestStep;
            s.Calculate_Cost();
        }

        public static void ApplyMove(Map map, Recommend_Aquire_Commodities_Path s, Random rng, ResearchMove move)
        {
            switch (move)
            {
                case ResearchMove.Swap: Swap(s, rng); break;
                case ResearchMove.Reverse: Reverse(s, rng); break;
                case ResearchMove.Insert: Insert(s, rng); break;
                case ResearchMove.Source: ChangeSource(map, s, rng); break;
                case ResearchMove.Joint: JointMove(map, s, rng); break;
                case ResearchMove.Block: BlockRelocate(s, rng); break;
            }
        }

        public static void AlignToward(
            Recommend_Aquire_Commodities_Path child,
            Recommend_Aquire_Commodities_Path target,
            Random rng,
            double fraction)
        {
            int n = child.Path.Count;
            if (n == 0) return;
            int moves = Math.Max(1, Math.Min(n, (int)Math.Round(n * fraction)));

            for (int k = 0; k < moves; k++)
            {
                int targetPos = rng.Next(n);
                string wanted = target.Path[targetPos].Item.Name;
                int currentPos = child.Path.FindIndex(x => x.Item.Name == wanted);
                if (currentPos >= 0 && currentPos != targetPos)
                    (child.Path[targetPos], child.Path[currentPos]) = (child.Path[currentPos], child.Path[targetPos]);

                if (currentPos >= 0 && rng.NextDouble() < 0.70)
                {
                    var src = target.Path[targetPos];
                    int pos = child.Path.FindIndex(x => x.Item.Name == wanted);
                    if (pos >= 0)
                        child.Path[pos] = new Aquire_Node(src.Node, new SupplyItem(src.Item.Name, src.Item.Price));
                }
            }
            child.Calculate_Cost();
        }

        public static Recommend_Aquire_Commodities_Path Blend(
            Recommend_Aquire_Commodities_Path a,
            Recommend_Aquire_Commodities_Path b,
            Random rng)
        {
            var child = ClonePath(a);
            AlignToward(child, b, rng, 0.35 + 0.30 * rng.NextDouble());
            return child;
        }

        public static Recommend_Aquire_Commodities_Path LocalBestOf(
            Map map,
            Recommend_Aquire_Commodities_Path baseSol,
            Random rng,
            IReadOnlyList<ResearchMove> moves,
            int tries)
        {
            var best = ClonePath(baseSol);
            for (int t = 0; t < tries; t++)
            {
                var candidate = ClonePath(baseSol);
                ApplyMove(map, candidate, rng, moves[rng.Next(moves.Count)]);
                if (candidate.Cost < best.Cost) best = candidate;
            }
            return best;
        }

        public static double Diversity(IReadOnlyList<Recommend_Aquire_Commodities_Path> pop)
        {
            if (pop.Count < 2) return 0.0;
            double sum = 0.0;
            int pairs = 0;
            for (int i = 0; i < pop.Count; i++)
            {
                for (int j = i + 1; j < pop.Count; j++)
                {
                    int n = Math.Min(pop[i].Path.Count, pop[j].Path.Count);
                    if (n == 0) continue;
                    int mismatch = 0;
                    for (int k = 0; k < n; k++)
                    {
                        if (pop[i].Path[k].Item.Name != pop[j].Path[k].Item.Name ||
                            !ReferenceEquals(pop[i].Path[k].Node, pop[j].Path[k].Node))
                            mismatch++;
                    }
                    sum += (double)mismatch / n;
                    pairs++;
                }
            }
            return pairs == 0 ? 0.0 : sum / pairs;
        }
    }
}
