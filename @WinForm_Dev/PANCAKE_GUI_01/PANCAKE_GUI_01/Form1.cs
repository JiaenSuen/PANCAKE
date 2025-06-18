using PANCAKE_DSLib;
using PANCAKE_Read_Map;
using PANCAKE_Solution;
using Basic_Algorithms_PANCAKE;
using System.Xml.Linq;

using System;
using System.Drawing.Drawing2D;
using System.Reflection;
using System.IO;
using Genetic_Algorithm;
using PANCAKE_GUI_01;
using Tabu_Search;

namespace PANCAKE_GUI_01
{
    public partial class PANCAKE_GUI_Form_1 : Form
    {
        private MapViewer mapViewer;
        Dictionary<string, Delegate> strategyDict;
        public List<string> userDemand = new List<string> {
                "Water", "Bread",  "Battery", "ChessBurger" , "Fuel" , "Tissue",
                "Flashlight","Fruit","Vegetables","FirstAid", "Towel","Juice",
                "Toothpaste","Hotdog","Soda","Coffee","Soap","Chocolate",
                "Compass","BeefBurger","RiceBall","Hotdog"
            };
        Map map = new Map();
        

        public PANCAKE_GUI_Form_1()
        {
            InitializeComponent();
            mapViewer = new MapViewer
            {
                Location = new Point(10, 10),
                Size = new Size(500, 500)
            };
            MapFrame.Controls.Add(mapViewer);

            strategyDict = new Dictionary<string, Delegate>
            {
                { "Greedy Strategy"   , new Action<Map, List<string>, MapViewer, TextBox>(PANCAKE_RACP.PANCAKE_Greedy) },
                { "Genetic Algorithm" , new Action<Map, List<string>, MapViewer, TextBox>(PANCAKE_RACP.PANCAKE_GA ) },
                { "Tabu Search"       , new Action<Map, List<string>, MapViewer, TextBox>(PANCAKE_RACP.PANCAKE_Tabu_Search ) },
            };

            
        }

        private void PANCAKE_GUI_Form_1_Load(object sender, EventArgs e)
        {
            this.map = MapLoader.Read_CSV_From_Map("../../../datasets/map6.csv");
            mapViewer.LoadNodes(this.map.Nodes);

            //userDemand = userDemand.Distinct().ToList();
            var userDemand_counts = userDemand.GroupBy(item => item).ToDictionary(g => g.Key, g => g.Count());

            //map.ObjectsAquireList.show_All_Commidites_on_Map();

        }













        private void btnZoomIn_Click(object sender, EventArgs e)
        {
            mapViewer.Zoom *= 1.2f;
        }

        private void btnZoomOut_Click(object sender, EventArgs e)
        {
            mapViewer.Zoom /= 1.2f;
        }

        private void comboBox1_SelectedIndexChanged(object sender, EventArgs e)
        {
            string selectedStrategy = Algorithm_Selection.SelectedItem.ToString();
            userDemand = GetUserDemandFromTextBox();

            if (strategyDict.ContainsKey(selectedStrategy))
            {
                var func = strategyDict[selectedStrategy] as Action<Map, List<string>, MapViewer, TextBox>;
                func?.Invoke(map, userDemand, mapViewer, RAC_Path_Box); 
            }
            else
                MessageBox.Show("�������w�q�I");
            
        }


        private List<string> GetUserDemandFromTextBox()
        {
            List<string> demands = new List<string>();

            if (Test_Cases.SelectedIndex == 0) {
                demands = txtDemandInput.Text
                    .Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries)
                    .Select(item => item.Trim())
                    .Where(item => !string.IsNullOrEmpty(item))
                    .ToList();
            } else if (Test_Cases.SelectedIndex == 1)
            {
                demands = new List<string> {
                    "Water", "Bread",  "Battery", "ChessBurger" , "Fuel" , "Tissue",
                    "Flashlight","Fruit","Vegetables","FirstAid", "Towel","Juice",
                    "Toothpaste","Hotdog","Soda","Coffee","Soap","Chocolate",
                    "Compass","BeefBurger","RiceBall","Hotdog"
                };
            }
            else if (Test_Cases.SelectedIndex == 2)
            {
                demands = new List<string> {
                    "Water", "Bread",  "Battery", "ChessBurger" , "Fuel" , "Tissue",
                    "Flashlight","Fruit","Vegetables","FirstAid", "Towel","Juice",
                    "Toothpaste","Hotdog","Soda","Coffee","Soap","Chocolate",
                    "Compass","BeefBurger","RiceBall","Hotdog"
                };
            }

            var available = new HashSet<string>(
                map.ObjectsAquireList.AllObjects,
                StringComparer.OrdinalIgnoreCase
            );

            return demands
                .Where(item => available.Contains(item))
                .ToList();
        }



    }




    class PANCAKE_RACP
    {
        public static void PANCAKE_Greedy(Map map, List<string> userDemand, MapViewer mapViewer, TextBox RAC_Path_Box)
        {
            if (userDemand.Count == 0) return;
            var result = Greedy.Greedy_Method(map, userDemand);
            mapViewer.LoadPath(result);
            RAC_Path_Box.Text = result.ToString();
        }

        public static void PANCAKE_GA(Map map, List<string> userDemand, MapViewer mapViewer, TextBox RAC_Path_Box)
        {   
            if(userDemand.Count == 0) return;
            var results = GA.Genetic_Evolution(map, userDemand , populationSize:200);
            mapViewer.LoadPath(results[0]);
            RAC_Path_Box.Text = results[0].ToString();
        }

        public static void PANCAKE_Tabu_Search(Map map, List<string> userDemand, MapViewer mapViewer, TextBox RAC_Path_Box)
        {
            if (userDemand.Count == 0) return;
            var Greedy_result = Greedy.Greedy_Method(map, userDemand);
            var result = TS.Tabu_Search(map, userDemand , Greedy_result , maxIterations:1000,tabuListSize:100,neighborCount:100);
            mapViewer.LoadPath(result);
            RAC_Path_Box.Text = result.ToString();
        }
    };

}




 