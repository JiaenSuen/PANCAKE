using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;



namespace PANCAKE_Params
{
    using PANCAKE_DSLib;
    internal class Params
    {
        public static Node pStart_Node = new Node("Origin", 0, 0, new List<SupplyItem>());
        public static double  pUnit_Cost = 0.25;
    }
}
