import random
import csv

# 設定隨機種子
random.seed(42)

# 擴大商品種類（含生活、食物、特殊用品）
goods = [
    # 基本需求
    "Water", "Bread", "Egg", "Battery", "Fuel", "FirstAid",

    # 食物類
    "ChessBurger", "BeefBurger", "Milktea", "Noodles", "Fruit", "Juice",
    "Sandwich", "RiceBall", "Dumplings", "Hotdog", "EnergyBar", "InstantSoup",
    "Vegetables", "Soda", "Coffee", "Chocolate", "Chips", "CannedFood",

    # 生活類
    "Toothpaste", "Shampoo", "Soap", "Tissue", "Detergent", "Towel",
    "Toothbrush", "LaundryPowder", "Razor", "Deodorant", "ToiletPaper", "HandSanitizer",

    # 特殊領域
    "Camera", "Laptop", "Drone", "PowerBank", "LanCable", "SolarPanel",
    "Charger", "Smartwatch", "Earphones", "Tablet", "PortableFan", "VRHeadset",

    # 戶外與防災
    "MedKit", "Flashlight", "SleepingBag", "Tent", "Compass", "EmergencyRadio",
    "RainCoat", "FireStarter", "MultiTool", "WaterPurifier", "ThermalBlanket",

    # 醫療類
    "Painkiller", "Antibiotic", "Bandage", "Thermometer", "Gloves", "FaceMask",

    # 嬰幼兒與兒童
    "BabyFood", "Diapers", "ToyCar", "StuffedAnimal", "Crayons", "PictureBook",

    # 車輛與交通
    "Bike", "Scooter", "Helmet", "TirePump", "MotorOil", "ToolKit"
]


# 對應商品價格範圍
price_range = {
    # 基本需求
    "Water": (1, 20), "Bread": (5, 20), "Egg": (2, 10), "Battery": (10, 100),
    "Fuel": (30, 100), "FirstAid": (25, 60),

    # 食物類
    "ChessBurger": (25, 60), "BeefBurger": (60, 120), "Milktea": (15, 40),
    "Noodles": (5, 15), "Fruit": (3, 15), "Juice": (8, 20), "Sandwich": (20, 50),
    "RiceBall": (10, 30), "Dumplings": (30, 60), "Hotdog": (15, 40),
    "EnergyBar": (10, 25), "InstantSoup": (8, 20), "Vegetables": (3, 15),
    "Soda": (5, 15), "Coffee": (10, 30), "Chocolate": (10, 30),
    "Chips": (10, 25), "CannedFood": (15, 40),

    # 生活類
    "Toothpaste": (5, 15), "Shampoo": (10, 30), "Soap": (5, 20),
    "Tissue": (2, 10), "Detergent": (10, 25), "Towel": (8, 25),
    "Toothbrush": (5, 15), "LaundryPowder": (15, 30), "Razor": (10, 25),
    "Deodorant": (15, 30), "ToiletPaper": (5, 15), "HandSanitizer": (10, 30),

    # 特殊領域
    "Camera": (100, 200), "Laptop": (300, 1500), "Drone": (200, 1000),
    "PowerBank": (50, 200), "LanCable": (10, 60), "SolarPanel": (150, 600),
    "Charger": (20, 100), "Smartwatch": (100, 300), "Earphones": (30, 150),
    "Tablet": (150, 800), "PortableFan": (20, 60), "VRHeadset": (300, 1000),

    # 戶外與防災
    "MedKit": (40, 80), "Flashlight": (20, 70), "SleepingBag": (60, 150),
    "Tent": (100, 300), "Compass": (10, 40), "EmergencyRadio": (60, 150),
    "RainCoat": (20, 60), "FireStarter": (10, 50), "MultiTool": (50, 150),
    "WaterPurifier": (100, 250), "ThermalBlanket": (20, 60),

    # 醫療類
    "Painkiller": (10, 30), "Antibiotic": (20, 60), "Bandage": (5, 20),
    "Thermometer": (30, 80), "Gloves": (10, 30), "FaceMask": (10, 25),

    # 嬰幼兒與兒童
    "BabyFood": (15, 40), "Diapers": (30, 80), "ToyCar": (20, 50),
    "StuffedAnimal": (30, 70), "Crayons": (5, 15), "PictureBook": (10, 30),

    # 車輛與交通
    "Bike": (150, 500), "Scooter": (300, 800), "Helmet": (50, 150),
    "TirePump": (20, 50), "MotorOil": (40, 80), "ToolKit": (50, 120)
}

# 電腦科學家+商店/餐館名混合命名
cs_names = [
    "Turing", "Einstein", "Newton", "Tesla", "Bohr", "Curie", "Hawking", "Galileo", "Feynman", "Euler",
    "Leibniz", "Maxwell", "Heisenberg", "Fermi", "Dirac", "Pauli", "Planck", "Schrodinger", "Faraday", "Noether",
    "Shannon", "Knuth", "Torvalds", "BernersLee", "AdaLovelace", "Hopper", "Dijkstra", "Liskov", "Papert", "Sutherland",
    "Zuse", "Wilkes", "Backus", "Minsky", "Engelbart", "Kay", "Codd", "McCarthy", "Tanenbaum", "Goldwasser",
    "Diffie", "Hellman", "Rivest", "Shamir", "Adleman", "Karp", "Cook", "Chomsky", "VonNeumann", "Boole"
]
store_names = [f"{prefix}{suffix}" for prefix in ["Cafe", "Shop", "Depot", "Market", "Corner", "Resto", "Mart"]
               for suffix in ["X", "Y", "Zone", "Plus", "Square", "Express", "Bay"]]
names = cs_names + store_names
random.shuffle(names)

# 自動生成 100 個節點
num_nodes = 500
node_data = []
for i in range(num_nodes):
    name = names[i % len(names)] + (str(i) if names.count(names[i % len(names)]) > 1 else "")
    x = random.randint(-200, 200)
    y = random.randint(-200, 200)
    num_items = random.randint(2, 6)
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
