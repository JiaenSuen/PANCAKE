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
using Ant_Colony;
using Whale_optimization;
using Discrete_PSO;
using Whale_optimization_TS;


namespace PANCAKE_GUI_01
{


    public partial class PANCAKE_GUI_Form_1 : Form
    {
        public static string Temp_Text = "";
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
                { "Greedy Strategy"          , new Action<Map, List<string>, MapViewer, TextBox>(PANCAKE_RACP.PANCAKE_Greedy) },
                { "SetCover Strategy"          , new Action<Map, List<string>, MapViewer, TextBox>(PANCAKE_RACP.PANCAKE_SetCover) },
                { "Dynamic Programming"      , new Action<Map, List<string>, MapViewer, TextBox>(PANCAKE_RACP.PANCAKE_DP) },

                { "Genetic Algorithm" , new Action<Map, List<string>, MapViewer, TextBox>(PANCAKE_RACP.PANCAKE_GA ) },
                { "Tabu Search"       , new Action<Map, List<string>, MapViewer, TextBox>(PANCAKE_RACP.PANCAKE_Tabu_Search ) },
                { "Genetic Mix TS"    , new Action<Map, List<string>, MapViewer, TextBox>(PANCAKE_RACP.PANCAKE_GA_TS_Mutaion ) },
                { "Ant Colony"        , new Action<Map, List<string>, MapViewer, TextBox>(PANCAKE_RACP.PANCAKE_ACO ) },
                { "Whale Optimization", new Action<Map, List<string>, MapViewer, TextBox>(PANCAKE_RACP.PANCAKE_WOA ) },
                { "Whale Optimization Mix TS" , new Action<Map, List<string>, MapViewer, TextBox>(PANCAKE_RACP.PANCAKE_WOA_TS ) },
                { "Particle Swarm", new Action<Map, List<string>, MapViewer, TextBox>(PANCAKE_RACP.PANCAKE_PSO ) },
            };


        }

        private void PANCAKE_GUI_Form_1_Load(object sender, EventArgs e)
        {
            this.map = MapLoader.Read_CSV_From_Map("../../../datasets/map.csv");
            mapViewer.LoadNodes(this.map.Nodes);

            //userDemand = userDemand.Distinct().ToList();
            var userDemand_counts = userDemand.GroupBy(item => item).ToDictionary(g => g.Key, g => g.Count());
            show_commodites();
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
                MessageBox.Show("策略未定義！");

            MinCost_label.Text = Temp_Text;

        }


        private List<string> GetUserDemandFromTextBox()
        {
            List<string> demands = new List<string>();

            if (Test_Cases.SelectedIndex == 0)
            {
                demands = txtDemandInput.Text
                    .Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries)
                    .Select(item => item.Trim())
                    .Where(item => !string.IsNullOrEmpty(item))
                    .ToList();
            }
            else if (Test_Cases.SelectedIndex == 1)
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
                    "Water", "Bread", "Egg", "Battery", "Fuel", "FirstAid",
                    "ChessBurger", "BeefBurger", "Milktea", "Noodles", "Fruit", "Juice",
                    "Sandwich", "RiceBall", "Dumplings", "Hotdog", "EnergyBar", "InstantSoup",
                    "Vegetables", "Soda", "Coffee", "Chocolate", "Chips", "CannedFood",
                    "Toothpaste", "Shampoo", "Soap", "Tissue", "Detergent", "Towel",
                    "Toothbrush", "LaundryPowder", "Razor", "Deodorant", "ToiletPaper", "HandSanitizer",
                    "Camera", "Laptop", "Drone", "PowerBank", "LanCable", "SolarPanel",
                    "Charger", "Smartwatch", "Earphones", "Tablet", "PortableFan", "VRHeadset",
                    "MedKit", "Flashlight", "SleepingBag", "Tent", "Compass", "EmergencyRadio",
                    "RainCoat", "FireStarter", "MultiTool", "WaterPurifier", "ThermalBlanket",
                    "Painkiller", "Antibiotic", "Bandage", "Thermometer", "Gloves", "FaceMask",
                    "BabyFood", "Diapers", "ToyCar", "StuffedAnimal", "Crayons", "PictureBook",
                    "Bike", "Scooter", "Helmet", "TirePump", "MotorOil", "ToolKit"
                };
            }
            else if (Test_Cases.SelectedIndex == 3)
            {
                demands = new List<string> {
                    "Rice", "Flour", "Noodles", "Vegetables", "Fruit", "Meat", "Egg", "Milk",
                    "Cheese", "Tofu", "CannedFood",
                    "Water", "SparklingWater", "Soda", "Cola", "OrangeJuice", "AppleJuice", "Milktea", "BlackTea",
                    "GreenTea", "Coffee", "Latte", "Cappuccino", "EnergyDrink", "Beer", "CraftBeer", "Wine", "RedWine", "WhiteWine",
                    "CheeseBurger", "BeefBurger", "ChickenBurger", "FishBurger", "VeggieBurger", "DoubleBurger",
                    "EggSandwich", "HamSandwich", "ClubSandwich", "BLTSandwich", "RiceBall", "TunaRiceBall", "SalmonRiceBall",
                    "PorkDumplings", "VegDumplings", "FriedDumplings", "ClassicHotdog", "CheeseHotdog", "SpicyHotdog",
                    "InstantSoup", "MisoSoup", "SeafoodSoup", "EnergyBar", "ProteinBar",
                    "Chocolate", "DarkChocolate", "WhiteChocolate", "PotatoChips", "CornChips",
                    "PepperoniPizza", "MargheritaPizza", "SeafoodPizza", "BBQChickenPizza", "FriedRice", "CurryRice",
                    "ChickenSalad", "CaesarSalad", "PastaBolognese", "Carbonara", "Sushi", "SalmonSushi", "EelSushi"
                };
            }
            else if (Test_Cases.SelectedIndex == 4)
            {
                demands = new List<string> {
                    "Rice", "Flour", "Noodles", "Vegetables", "Fruit", "Meat", "Egg", "Milk",
                    "Cheese", "Tofu", "CannedFood" ,"Water", "SparklingWater", "Soda", "Cola",
                    "OrangeJuice", "AppleJuice", "Milktea", "BlackTea",
                    "GreenTea", "Coffee", "Latte", "Cappuccino",
                };
            }




            var available = new HashSet<string>(
                map.ObjectsAquireList.AllObjects,
                StringComparer.OrdinalIgnoreCase
            );

            show_demands();
            return demands
                .Where(item => available.Contains(item))
                .ToList();
        }

        private void MapSelector_SelectedIndexChanged(object sender, EventArgs e)
        {
            this.map = MapLoader.Read_CSV_From_Map($"../../../datasets/{MapSelector.SelectedItem.ToString()}.csv");
            mapViewer.LoadNodes(this.map.Nodes);
            show_commodites();
            show_demands();
        }


        private void show_commodites()
        {
            ShowCommodities.Text = "";
            foreach (var obj in map.ObjectsAquireList.AllObjects)
            {
                ShowCommodities.Text += obj + "\r\n";
            }
        }

        private void show_demands()
        {
            Demands_Show.Text = "";
            foreach (var item in userDemand)
                Demands_Show.Text += item + "\r\n";

        }

        private void Test_Cases_SelectedIndexChanged(object sender, EventArgs e)
        {
            userDemand = GetUserDemandFromTextBox();
            show_demands();
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
            PANCAKE_GUI_Form_1.Temp_Text = Math.Round(result.Cost, 2).ToString();
        }

        public static void PANCAKE_SetCover(Map map, List<string> userDemand, MapViewer mapViewer, TextBox RAC_Path_Box)
        {
            if (userDemand.Count == 0) return;
            var result = SetCover.SetCover_Method(map, userDemand);
            mapViewer.LoadPath(result);
            RAC_Path_Box.Text = result.ToString();
            PANCAKE_GUI_Form_1.Temp_Text = Math.Round(result.Cost, 2).ToString();
        }

        public static void PANCAKE_DP(Map map, List<string> userDemand, MapViewer mapViewer, TextBox RAC_Path_Box)
        {
            if (userDemand.Count == 0) return;
            var result = DP.DP_Method(map, userDemand);
            mapViewer.LoadPath(result);
            RAC_Path_Box.Text = result.ToString();
            PANCAKE_GUI_Form_1.Temp_Text = Math.Round(result.Cost, 2).ToString();
        }

         

        public static void PANCAKE_GA(Map map, List<string> userDemand, MapViewer mapViewer, TextBox RAC_Path_Box)
        {   
            if(userDemand.Count == 0) return;
            List<Recommend_Aquire_Commodities_Path> init_pop = new List<Recommend_Aquire_Commodities_Path> (){ };
            //init_pop.Add(Greedy.Greedy_Method(map, userDemand));
            var results = GA.Genetic_Evolution(map, userDemand , generations:2000 , populationSize:250 , extra_init_Pop: init_pop);
            mapViewer.LoadPath(results[0]);
            RAC_Path_Box.Text = results[0].ToString();
            PANCAKE_GUI_Form_1.Temp_Text = Math.Round(results[0].Cost, 2).ToString();
        }

        public static void PANCAKE_Tabu_Search(Map map, List<string> userDemand, MapViewer mapViewer, TextBox RAC_Path_Box)
        {
            if (userDemand.Count == 0) return;
            var Greedy_result = Greedy.Greedy_Method(map, userDemand);
            var result = TS.Tabu_Search(map, userDemand , Greedy_result , maxIterations:1000,tabuListSize:100,neighborCount:100);
            mapViewer.LoadPath(result);
            RAC_Path_Box.Text = result.ToString();
            PANCAKE_GUI_Form_1.Temp_Text = Math.Round(result.Cost,2).ToString();
        }

        public static void PANCAKE_GA_TS_Mutaion(Map map, List<string> userDemand, MapViewer mapViewer, TextBox RAC_Path_Box)
        {
            if (userDemand.Count == 0) return;
            List<Recommend_Aquire_Commodities_Path> init_pop = new List<Recommend_Aquire_Commodities_Path>() { };
            //init_pop.Add(Greedy.Greedy_Method(map, userDemand));
            var results = Genetic_Algorithm_TS_Mutaion.GA_ts.Genetic_Evolution(map, userDemand, generations:50 ,populationSize: 100 ,extra_init_Pop:init_pop);
            mapViewer.LoadPath(results[0]);
            RAC_Path_Box.Text = results[0].ToString();
            PANCAKE_GUI_Form_1.Temp_Text = Math.Round(results[0].Cost, 2).ToString();
        }

        public static void PANCAKE_ACO(Map map, List<string> userDemand, MapViewer mapViewer, TextBox RAC_Path_Box)
        {
            if (userDemand.Count == 0) return;
            var result = ACO.ACO_Method(map, userDemand );
            mapViewer.LoadPath(result);
            RAC_Path_Box.Text = result.ToString();
            PANCAKE_GUI_Form_1.Temp_Text = Math.Round(result.Cost, 2).ToString();
        }

        public static void PANCAKE_WOA(Map map, List<string> userDemand, MapViewer mapViewer, TextBox RAC_Path_Box)
        {   // map8 529 比 greedy tabu 好
            if (userDemand.Count == 0) return;
            var result = WOA.Optimize(map, userDemand , maxIter:2500 , numWhales:200);
            mapViewer.LoadPath(result);
            RAC_Path_Box.Text = result.ToString();
            PANCAKE_GUI_Form_1.Temp_Text = Math.Round(result.Cost, 2).ToString();
        }

        public static void PANCAKE_WOA_TS(Map map, List<string> userDemand, MapViewer mapViewer, TextBox RAC_Path_Box)
        {    
            if (userDemand.Count == 0) return;
            var result = WOA_ts.Optimize(map, userDemand, maxIter: 500, numWhales: 75);
            mapViewer.LoadPath(result);
            RAC_Path_Box.Text = result.ToString();
            PANCAKE_GUI_Form_1.Temp_Text = Math.Round(result.Cost, 2).ToString();
        }

        public static void PANCAKE_PSO(Map map, List<string> userDemand, MapViewer mapViewer, TextBox RAC_Path_Box)
        {    
            if (userDemand.Count == 0) return;
            var result = PSO.Optimize(map, userDemand, maxIter: 3000, numParticles: 200);
            mapViewer.LoadPath(result);
            RAC_Path_Box.Text = result.ToString();
            PANCAKE_GUI_Form_1.Temp_Text = Math.Round(result.Cost, 2).ToString();
        }
    };


    
}




 