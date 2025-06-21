import random
import csv

# 設定隨機種子
random.seed(42)

 
goods = [
    # 食材類
    "Rice", "Flour", "Noodles", "Vegetables", "Fruit", "Meat", "Egg", "Milk",
    "Cheese", "Tofu", "CannedFood",

    # 飲料類
    "Water", "SparklingWater", "Soda", "Cola", "OrangeJuice", "AppleJuice", "Milktea", "BlackTea",
    "GreenTea", "Coffee", "Latte", "Cappuccino", "EnergyDrink", "Beer", "CraftBeer", "Wine", "RedWine", "WhiteWine",

    # 熟食類（主食）
    "CheeseBurger", "BeefBurger", "ChickenBurger", "FishBurger", "VeggieBurger", "DoubleBurger",
    "EggSandwich", "HamSandwich", "ClubSandwich", "BLTSandwich", "RiceBall", "TunaRiceBall", "SalmonRiceBall",
    "PorkDumplings", "VegDumplings", "FriedDumplings", "ClassicHotdog", "CheeseHotdog", "SpicyHotdog",

    # 熟食類（其他）
    "InstantSoup", "MisoSoup", "SeafoodSoup", "EnergyBar", "ProteinBar",
    "Chocolate", "DarkChocolate", "WhiteChocolate", "PotatoChips", "CornChips",

    # 熟食類（料理）
    "PepperoniPizza", "MargheritaPizza", "SeafoodPizza", "BBQChickenPizza", "FriedRice", "CurryRice",
    "ChickenSalad", "CaesarSalad", "PastaBolognese", "Carbonara", "Sushi", "SalmonSushi", "EelSushi"
]

price_range = {
    # 食材類
    "Rice": (5, 15), "Flour": (5, 12), "Noodles": (5, 15),
    "Vegetables": (3, 15), "Fruit": (3, 15), "Meat": (30, 80),
    "Egg": (2, 10), "Milk": (10, 25), "Cheese": (15, 40),
    "Tofu": (5, 15), "CannedFood": (15, 40),

    # 飲料類
    "Water": (1, 20), "SparklingWater": (8, 20), "Soda": (5, 15), "Cola": (5, 15),
    "OrangeJuice": (10, 20), "AppleJuice": (10, 20), "Milktea": (15, 40),
    "BlackTea": (10, 25), "GreenTea": (10, 25), "Coffee": (10, 30),
    "Latte": (20, 45), "Cappuccino": (20, 45), "EnergyDrink": (15, 35),
    "Beer": (20, 50), "CraftBeer": (40, 80), "Wine": (60, 200),
    "RedWine": (80, 250), "WhiteWine": (70, 220),

    # 熟食類（主食）
    "CheeseBurger": (30, 60), "BeefBurger": (60, 120), "ChickenBurger": (40, 90),
    "FishBurger": (45, 100), "VeggieBurger": (35, 70), "DoubleBurger": (80, 150),

    "EggSandwich": (20, 40), "HamSandwich": (25, 45), "ClubSandwich": (35, 60),
    "BLTSandwich": (30, 55),

    "RiceBall": (10, 30), "TunaRiceBall": (15, 35), "SalmonRiceBall": (20, 40),

    "PorkDumplings": (30, 60), "VegDumplings": (25, 50), "FriedDumplings": (35, 65),

    "ClassicHotdog": (15, 40), "CheeseHotdog": (20, 45), "SpicyHotdog": (18, 42),

    # 熟食類（其他）
    "InstantSoup": (8, 20), "MisoSoup": (10, 25), "SeafoodSoup": (15, 35),
    "EnergyBar": (10, 25), "ProteinBar": (15, 30),

    "Chocolate": (10, 30), "DarkChocolate": (15, 35), "WhiteChocolate": (12, 28),
    "PotatoChips": (10, 25), "CornChips": (10, 22),

    # 熟食類（料理）
    "PepperoniPizza": (90, 150), "MargheritaPizza": (80, 140), "SeafoodPizza": (100, 160),
    "BBQChickenPizza": (100, 160),

    "FriedRice": (40, 80), "CurryRice": (45, 85),

    "ChickenSalad": (25, 50), "CaesarSalad": (30, 55),

    "PastaBolognese": (45, 90), "Carbonara": (50, 95),

    "Sushi": (60, 150), "SalmonSushi": (70, 160), "EelSushi": (80, 180)
}


# 電腦科學家+商店/餐館名混合命名
cs_names = [
    "Turing", "Einstein", "Newton", "Tesla", "Bohr", "Curie", "Hawking", "Galileo", "Feynman", "Euler",
    "Leibniz", "Maxwell", "Heisenberg", "Fermi", "Dirac", "Pauli", "Planck", "Schrodinger", "Faraday", "Noether",
    "Shannon", "Knuth", "Torvalds", "BernersLee", "AdaLovelace", "Hopper", "Dijkstra", "Liskov", "Papert", "Sutherland",
    "Zuse", "Wilkes", "Backus", "Minsky", "Engelbart", "Kay", "Codd", "McCarthy", "Tanenbaum", "Goldwasser",
    "Diffie", "Hellman", "Rivest", "Shamir", "Adleman", "Karp", "Cook", "Chomsky", "VonNeumann", "Boole",
    "Ko-Wei",
]
store_names = [f"{prefix}{suffix}" for prefix in ["Cafe", "Shop", "Depot", "Market", "Corner", "Resto", "Mart"]
               for suffix in ["X", "Y", "Zone", "Plus", "Square", "Express", "Bay"]]
names = cs_names + store_names
random.shuffle(names)

# 自動生成 N 個節點
num_nodes = 2000
node_data = []
for i in range(num_nodes):
    name = names[i % len(names)] + (str(i) if names.count(names[i % len(names)]) > 1 else "")
    x = random.randint(-1000, 1000)
    y = random.randint(-1000, 1000)
    num_items = random.randint(2, 8)
    items = random.sample(goods, num_items)
    obj_list = [f"{item}:{random.randint(*price_range[item])}" for item in items]
    obj_str = ";".join(obj_list)
    node_data.append([name, x, y, obj_str])

# 輸出為 CSV 檔案
csv_path = "_map.csv"
with open(csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Node_Name", "Location_X", "Location_Y", "Objects"])
    writer.writerows(node_data)

csv_path
