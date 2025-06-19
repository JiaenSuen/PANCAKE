

namespace Tabu_Search
{
    using PANCAKE_Read_Map;
    using PANCAKE_DSLib;
    using PANCAKE_Solution;

    using Exhaustive_PANCAKE;
    using Basic_Algorithms_PANCAKE;

    using Metaheuristic_Interface;

    class TS
    {


        public enum MoveType
        {
            ReplaceNode,  // 替換同一商品的取貨節點
            SwapNodes     // 交換兩個取貨節點
        }

        public class Move
        {
            public MoveType Type { get; }
            public int IndexA { get; }         // 受影響的第一個位置
            public int IndexB { get; }         // （若為 Swap）受影響的第二個位置
            public Node? OldNode { get; }       // （若為 Replace）原本的取貨節點
            public Node? NewNode { get; }       // （若為 Replace）新的取貨節點

            // Replace 構造
            public Move(int idx, Node oldNode, Node newNode)
            {
                Type = MoveType.ReplaceNode;
                IndexA = idx;
                OldNode = oldNode;
                NewNode = newNode;
            }

            // Swap 構造
            public Move(int idxA, int idxB)
            {
                Type = MoveType.SwapNodes;
                IndexA = idxA;
                IndexB = idxB;
            }

            public override string ToString()
            {
                if (Type == MoveType.ReplaceNode)
                    return $"Replace: Path[{IndexA}] 從 {OldNode!.Name} → {NewNode!.Name}";
                else
                    return $"Swap: Path[{IndexA}] ⇄ Path[{IndexB}]";
            }


            public override bool Equals(object? obj)
            {
                if (obj is not Move other || Type != other.Type) return false;

                return Type switch
                {
                    MoveType.ReplaceNode => IndexA == other.IndexA &&
                                            OldNode?.Name == other.OldNode?.Name &&
                                            NewNode?.Name == other.NewNode?.Name,

                    MoveType.SwapNodes => (IndexA == other.IndexA && IndexB == other.IndexB) ||
                                        (IndexA == other.IndexB && IndexB == other.IndexA), // 無順序
                    _ => false
                };
            }
            public override int GetHashCode()
            {
                return Type switch
                {
                    MoveType.ReplaceNode => HashCode.Combine(Type, IndexA, OldNode?.Name, NewNode?.Name),
                    MoveType.SwapNodes => HashCode.Combine(Type, Math.Min(IndexA, IndexB), Math.Max(IndexA, IndexB)),
                    _ => 0
                };
            }
        }



        public class TabuList
        {
            private readonly int _maxSize;
            private readonly Queue<Move> _tabuQueue = new();

            public TabuList(int maxSize)
            {
                _maxSize = maxSize;
            }

            public void Add(Move move)
            {
                if (_tabuQueue.Count >= _maxSize)
                    _tabuQueue.Dequeue();

                _tabuQueue.Enqueue(move);
            }

            public bool Contains(Move move)
            {
                return _tabuQueue.Any(m => m.Equals(move));
            }
        }




        // Tabu Search 鄰近解搜尋 ， Return Tuple ( Neighbor_Path , Move )
        static public (Recommend_Aquire_Commodities_Path Neighbor, Move? MoveRecord) Generate_A_Neighbor_for_TS(Recommend_Aquire_Commodities_Path thePath, Map map, List<string> Require_List)
        {
            var rand = new Random();

            // Copy Path
            var newPath = new Recommend_Aquire_Commodities_Path { UnitMoveCost = thePath.UnitMoveCost, Start_Node = thePath.Start_Node };
            newPath.Path = thePath.Path.Select(an => new Aquire_Node(an.Node, an.Item)).ToList();

            Move? moveRecord = null;

            int Random_Select = rand.Next(1, 3);
            if (Random_Select == 1) // 選一個物件 換一個節點買
            {

                int idx = rand.Next(newPath.Path.Count);
                var oldAcquire = newPath.Path[idx];
                string commodity = oldAcquire.Item.Name;


                var candidates = map.ObjectsAquireList[commodity].Where(t => t.node != oldAcquire.Node).ToList();

                if (candidates.Count > 0)
                {
                    // 隨機選一個新節點
                    var (newNode, newPrice) = candidates[rand.Next(candidates.Count)];
                    var newItem = new SupplyItem(commodity, newPrice);
                    newPath.Path[idx] = new Aquire_Node(newNode, newItem);

                    moveRecord = new Move(idx, oldAcquire.Node, newNode);
                }
                else
                {
                    // 若沒有候選節點，就當作 swap 處理
                    int i = rand.Next(newPath.Path.Count);
                    int j = (i + rand.Next(1, newPath.Path.Count)) % newPath.Path.Count;
                    (newPath.Path[i], newPath.Path[j]) = (newPath.Path[j], newPath.Path[i]);
                    moveRecord = new Move(i, j);
                }
            }
            else if (Random_Select == 2) // 交換兩購物點順序 
            {
                int i = rand.Next(newPath.Path.Count);
                int j = rand.Next(newPath.Path.Count);
                while (j == i) j = rand.Next(newPath.Path.Count);

                (newPath.Path[i], newPath.Path[j]) = (newPath.Path[j], newPath.Path[i]);
                moveRecord = new Move(i, j);
            }

            newPath.Calculate_Cost();




            return (newPath, moveRecord);
        }


        public static Recommend_Aquire_Commodities_Path Tabu_Search(Map map, List<string> userDemand, Recommend_Aquire_Commodities_Path? initialSolution = null,
          int maxIterations = 100, int tabuListSize = 10, int neighborCount = 30)
        {

            var currentSolution = initialSolution ?? MH_init_Utils.Generate_Random_RAC_Path(map, userDemand);
            var bestSolution = currentSolution;
            double bestCost = currentSolution.Cost;

            var tabuList = new TabuList(tabuListSize);

            for (int iter = 0; iter < maxIterations; iter++)
            {
                List<(Recommend_Aquire_Commodities_Path path, Move move)> neighbors = new();
                for (int k = 0; k < neighborCount; k++)
                {
                    var (neighbor, move) = Generate_A_Neighbor_for_TS(currentSolution, map, userDemand);
                    if (move != null && !tabuList.Contains(move))
                    {
                        neighbors.Add((neighbor, move));
                    }
                }
                if (neighbors.Count == 0) break;



                var bestNeighbor = neighbors.OrderBy(n => n.path.Cost).First();
                currentSolution = bestNeighbor.path;
                tabuList.Add(bestNeighbor.move);

                //Console.WriteLine($"\n[第 {iter + 1} 次] Move: {bestNeighbor.move}, 成本: {bestNeighbor.path.Cost:F2}");


                if (bestNeighbor.path.Cost < bestCost)
                {
                    bestSolution = bestNeighbor.path;
                    bestCost = bestNeighbor.path.Cost;
                }
            }


            return bestSolution;
        }


    }


}