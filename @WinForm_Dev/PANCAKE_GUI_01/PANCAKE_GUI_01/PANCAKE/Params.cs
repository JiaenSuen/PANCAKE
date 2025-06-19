using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using PANCAKE_DSLib;

namespace PANCAKE_Params
{
    internal class Params
    {
        public static Node pStart_Node = new Node("Origin", 0, 0, new List<SupplyItem>());
        public static double  pUnit_Cost = 0.25;
    }
}
