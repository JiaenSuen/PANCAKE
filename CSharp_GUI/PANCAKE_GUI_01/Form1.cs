using PANCAKE_Read_Map;
using PANCAKE_Solution;
using System.Diagnostics;
using System.IO;

namespace PANCAKE_GUI_01
{
    public partial class PANCAKE_GUI_Form_1 : Form
    {
        private readonly MapViewer mapViewer;
        private Map map = new();
        private List<string> userDemand = new();
        private bool initializing = true;
        private bool isRunning = false;

        public PANCAKE_GUI_Form_1()
        {
            InitializeComponent();

            mapViewer = new MapViewer
            {
                Dock = DockStyle.Fill,
                Margin = Padding.Empty
            };
            MapFrame.Controls.Add(mapViewer);

            Algorithm_Selection.Items.Clear();
            Algorithm_Selection.Items.AddRange(AlgorithmRunner.AlgorithmNames.Cast<object>().ToArray());
            Algorithm_Selection.DropDownStyle = ComboBoxStyle.DropDownList;
            MapSelector.DropDownStyle = ComboBoxStyle.DropDownList;
            Test_Cases.DropDownStyle = ComboBoxStyle.DropDownList;
        }

        private void PANCAKE_GUI_Form_1_Load(object sender, EventArgs e)
        {
            try
            {
                initializing = true;

                if (MapSelector.Items.Count > 0)
                    MapSelector.SelectedIndex = 0;
                if (Test_Cases.Items.Count > 0)
                    Test_Cases.SelectedIndex = 0;
                if (Algorithm_Selection.Items.Count > 0)
                    Algorithm_Selection.SelectedIndex = 0;

                LoadMap("map");

                txtDemandInput.Text = string.Join(Environment.NewLine, new[]
                {
                    "Water", "Bread", "Battery", "Fuel", "FirstAid", "Fruit"
                });

                UpdateDemandPreview();
                NoteSpace.Text =
                    "Ready.\r\n\r\n" +
                    "1. Select a map.\r\n" +
                    "2. Choose a demand preset or enter one item per line.\r\n" +
                    "3. Select an algorithm.\r\n" +
                    "4. Click Run Optimization.\r\n\r\n" +
                    "DWOA-AVNS and DFOX-APNS use interactive GUI presets; " +
                    "the canonical research benchmark is under ResearchBenchmark/.";
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"The default dataset could not be loaded.\n\n{ex.Message}",
                    "PANCAKE - Dataset Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
            finally
            {
                initializing = false;
            }
        }

        private void btnZoomIn_Click(object sender, EventArgs e)
        {
            mapViewer.Zoom *= 1.2f;
        }

        private void btnZoomOut_Click(object sender, EventArgs e)
        {
            mapViewer.Zoom /= 1.2f;
        }

        // Selecting an algorithm must not start a potentially expensive optimization.
        // Execution is intentionally bound only to the Run Optimization button.
        private void comboBox1_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (initializing || Algorithm_Selection.SelectedItem is null) return;
            NoteSpace.Text =
                $"Selected algorithm: {Algorithm_Selection.SelectedItem}\r\n" +
                "Click Run Optimization to start.";
        }

        private void MapSelector_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (initializing || MapSelector.SelectedItem is null) return;

            try
            {
                string mapName = MapSelector.SelectedItem.ToString()!;
                LoadMap(mapName);

                // Research benchmark maps use Demand01-Demand16.
                if (mapName.StartsWith("research_", StringComparison.OrdinalIgnoreCase))
                {
                    Test_Cases.SelectedIndex = 0;
                    txtDemandInput.Text = string.Join(
                        Environment.NewLine,
                        map.ObjectsAquireList.AllObjects.OrderBy(x => x, StringComparer.OrdinalIgnoreCase));
                }

                UpdateDemandPreview();
                NoteSpace.Text =
                    $"Loaded map: {mapName}\r\n" +
                    $"Nodes: {map.Nodes.Count}\r\n" +
                    $"Available commodities: {map.ObjectsAquireList.AllObjects.Count()}";
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Unable to load the selected map.\n\n{ex.Message}",
                    "PANCAKE - Map Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
        }

        private void Test_Cases_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (initializing) return;
            UpdateDemandPreview();
        }

        private async void exe_button_Click(object sender, EventArgs e)
        {
            if (isRunning) return;

            if (Algorithm_Selection.SelectedItem is not string selectedAlgorithm)
            {
                MessageBox.Show(
                    "Please select an algorithm first.",
                    "PANCAKE",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information);
                return;
            }

            var requested = GetRequestedDemands();
            var available = new HashSet<string>(
                map.ObjectsAquireList.AllObjects,
                StringComparer.OrdinalIgnoreCase);

            userDemand = requested.Where(available.Contains).ToList();
            var missing = requested.Where(x => !available.Contains(x)).Distinct(StringComparer.OrdinalIgnoreCase).ToList();
            ShowDemandList(userDemand);

            if (userDemand.Count == 0)
            {
                string detail = missing.Count > 0
                    ? $"\n\nUnavailable items: {string.Join(", ", missing.Take(12))}"
                    : string.Empty;
                MessageBox.Show(
                    "No valid demand items are available on the selected map." + detail,
                    "PANCAKE - Invalid Demand",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Warning);
                return;
            }

            SetBusy(true);
            RAC_Path_Box.Clear();
            MinCost_label.Text = "Running...";
            NoteSpace.Text =
                $"Running: {selectedAlgorithm}\r\n" +
                $"Map: {MapSelector.SelectedItem}\r\n" +
                $"Demand items: {userDemand.Count}\r\n\r\n" +
                "Optimization is running on a worker thread; the interface will remain responsive.";

            var stopwatch = Stopwatch.StartNew();

            try
            {
                // Use snapshots so controls/maps cannot change while the worker is reading them.
                Map mapSnapshot = map;
                List<string> demandSnapshot = new(userDemand);

                Recommend_Aquire_Commodities_Path result = await Task.Run(
                    () => AlgorithmRunner.Run(selectedAlgorithm, mapSnapshot, demandSnapshot));

                stopwatch.Stop();
                mapViewer.LoadPath(result);
                RAC_Path_Box.Text = result.ToString();
                MinCost_label.Text = result.Cost.ToString("F2");

                string warning = missing.Count > 0
                    ? $"\r\nIgnored unavailable items: {string.Join(", ", missing)}"
                    : string.Empty;

                NoteSpace.Text =
                    "Completed successfully.\r\n\r\n" +
                    $"Algorithm: {selectedAlgorithm}\r\n" +
                    $"Demand items optimized: {userDemand.Count}\r\n" +
                    $"Final cost: {result.Cost:F2}\r\n" +
                    $"GUI elapsed time: {stopwatch.Elapsed.TotalSeconds:F2} s" + warning +
                    "\r\n\r\nElapsed time is shown only for interactive feedback; " +
                    "the research comparison uses objective-evaluation-based metrics.";
            }
            catch (Exception ex)
            {
                stopwatch.Stop();
                MinCost_label.Text = "Error";
                NoteSpace.Text = "Optimization failed.\r\n\r\n" + ex.Message;
                MessageBox.Show(
                    ex.Message,
                    "PANCAKE - Optimization Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
            finally
            {
                SetBusy(false);
            }
        }

        private void LoadMap(string mapName)
        {
            string path = ResolveDatasetPath(mapName);
            map = MapLoader.Read_CSV_From_Map(path);

            if (map.Nodes.Count == 0)
                throw new InvalidDataException($"Dataset '{mapName}' contains no valid nodes.");

            mapViewer.LoadNodes(map.Nodes);
            mapViewer.ClearPath();
            mapViewer.FitToNodes();
            ShowCommoditiesList();
        }

        private static string ResolveDatasetPath(string mapName)
        {
            string fileName = mapName.EndsWith(".csv", StringComparison.OrdinalIgnoreCase)
                ? mapName
                : mapName + ".csv";

            var candidates = new[]
            {
                Path.Combine(AppContext.BaseDirectory, "datasets", fileName),
                Path.Combine(Environment.CurrentDirectory, "datasets", fileName),
                Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "datasets", fileName))
            };

            string? found = candidates.FirstOrDefault(File.Exists);
            if (found is not null) return found;

            throw new FileNotFoundException(
                "Dataset file was not found. Checked:\n" + string.Join("\n", candidates));
        }

        private List<string> GetRequestedDemands()
        {
            if (Test_Cases.SelectedIndex == 0)
            {
                return txtDemandInput.Text
                    .Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries)
                    .Select(item => item.Trim())
                    .Where(item => !string.IsNullOrWhiteSpace(item))
                    .ToList();
            }

            return GetPresetDemands(Test_Cases.SelectedIndex);
        }

        private static List<string> GetPresetDemands(int presetIndex)
        {
            return presetIndex switch
            {
                1 => new List<string>
                {
                    "Water", "Bread", "Battery", "ChessBurger", "Fuel", "Tissue",
                    "Flashlight", "Fruit", "Vegetables", "FirstAid", "Towel", "Juice",
                    "Toothpaste", "Hotdog", "Soda", "Coffee", "Soap", "Chocolate",
                    "Compass", "BeefBurger", "RiceBall", "Hotdog"
                },
                2 => new List<string>
                {
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
                },
                3 => new List<string>
                {
                    "Rice", "Flour", "Noodles", "Vegetables", "Fruit", "Meat", "Egg", "Milk",
                    "Cheese", "Tofu", "CannedFood", "Water", "SparklingWater", "Soda", "Cola",
                    "OrangeJuice", "AppleJuice", "Milktea", "BlackTea", "GreenTea", "Coffee", "Latte",
                    "Cappuccino", "EnergyDrink", "Beer", "CraftBeer", "Wine", "RedWine", "WhiteWine",
                    "CheeseBurger", "BeefBurger", "ChickenBurger", "FishBurger", "VeggieBurger", "DoubleBurger",
                    "EggSandwich", "HamSandwich", "ClubSandwich", "BLTSandwich", "RiceBall", "TunaRiceBall",
                    "SalmonRiceBall", "PorkDumplings", "VegDumplings", "FriedDumplings", "ClassicHotdog",
                    "CheeseHotdog", "SpicyHotdog", "InstantSoup", "MisoSoup", "SeafoodSoup", "EnergyBar",
                    "ProteinBar", "Chocolate", "DarkChocolate", "WhiteChocolate", "PotatoChips", "CornChips",
                    "PepperoniPizza", "MargheritaPizza", "SeafoodPizza", "BBQChickenPizza", "FriedRice",
                    "CurryRice", "ChickenSalad", "CaesarSalad", "PastaBolognese", "Carbonara", "Sushi",
                    "SalmonSushi", "EelSushi"
                },
                4 => new List<string>
                {
                    "Rice", "Flour", "Noodles", "Vegetables", "Fruit", "Meat", "Egg", "Milk",
                    "Cheese", "Tofu", "CannedFood", "Water", "SparklingWater", "Soda", "Cola",
                    "OrangeJuice", "AppleJuice", "Milktea", "BlackTea", "GreenTea", "Coffee", "Latte", "Cappuccino"
                },
                _ => new List<string>()
            };
        }

        private void UpdateDemandPreview()
        {
            var requested = GetRequestedDemands();
            var available = new HashSet<string>(map.ObjectsAquireList.AllObjects, StringComparer.OrdinalIgnoreCase);
            userDemand = requested.Where(available.Contains).ToList();
            ShowDemandList(userDemand);
        }

        private void ShowCommoditiesList()
        {
            ShowCommodities.Text = string.Join(
                Environment.NewLine,
                map.ObjectsAquireList.AllObjects.OrderBy(x => x, StringComparer.OrdinalIgnoreCase));
        }

        private void ShowDemandList(IEnumerable<string> demands)
        {
            Demands_Show.Text = string.Join(Environment.NewLine, demands);
        }

        private void SetBusy(bool busy)
        {
            isRunning = busy;
            exe_button.Enabled = !busy;
            Algorithm_Selection.Enabled = !busy;
            MapSelector.Enabled = !busy;
            Test_Cases.Enabled = !busy;
            txtDemandInput.Enabled = !busy;
            exe_button.Text = busy ? "Running..." : "Run Optimization";
            UseWaitCursor = busy;
        }
    }
}
