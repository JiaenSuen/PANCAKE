# <font color=#FF0000> **DSLib**
<font color=#FFFF00>

### **SupplyItem**
	{ 物品名稱 , 價格 }
<br><br>

## **Node**
	{
		Node Name,
		Location_X,
		Location_Y,
		List<SupplyItem>

		-  double distance_to_next_Node(Node)
	}
<br><br>

## **Aquire_List**
	{
		Dictionary<string, List<(Node node, int price)>> map ,

		/* Aquire_List["Water"] → List<(Node, Price)> 索引器*/

		IEnumerable<string> AllObjects => map.Keys; 
		// 可以得知地圖有哪些可取物
	}
<br>
<br>

	  
	

# <font color=#00FF> **Map**

<font color=#89CFF0 >

### **Map** 
	{
		[ Aquire_List ] ObjectsAquireList  // 物品名稱 → 節點 List 字典查找
		[ List<Node> ]  Nodes  // 地圖上所有點
	}
<br>
<br>


### **MapLoader**
	@ Map Read_CSV_From_Map(string filePath)  // 讀取 CSV 檔案

<br>
<br>
<br>


# <font color=#FF00FF> **Solution**
<font color=#FFC0CB >

### **Aquire_Node**
	{
		[    Node    ]  Node  	// 取貨的節點
		[ SupplyItem ]  Item 	// 在該節點取得的物品（含價格）
	}
<br>

## **Recommend_Aquire_Commodities_Path**
	{
		[ List<Aquire_Node> ]  Path 
		[ double ] 	Cost // 累計的總成本（移動距離*單位距離花費價格 + 購買價格）

		預設 : Start_Node = (0,0) 、UnitMoveCost = 0.5

		- double Calculate_Cost()
        
	}
<br>
