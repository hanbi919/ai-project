// 各级区划数量统计
 
MATCH (d:District)
RETURN d.level AS 区划级别, COUNT(*) AS 数量
ORDER BY 数量 DESC

// 各市级区划下属区县数量排名
MATCH (city:District {level: '市级'})<-[:BELONGS_TO]-(county:District)
RETURN city.name AS 城市, COUNT(county) AS 下属区县数量
ORDER BY 下属区县数量 DESC


MATCH path = (d:District {name: '长春市'})<-[:BELONGS_TO*0..5]-(child)
WITH d, child, length(path) AS depth
RETURN 
  depth AS 层级深度,
  child.level AS 区划类型,
  COUNT(*) AS 数量
ORDER BY depth

// 4. 区划名称重复统计
MATCH (d:District)
WITH d.name AS name, COUNT(*) AS cnt
WHERE cnt > 1
RETURN name, cnt
ORDER BY cnt DESC

// 8. 统计每个区划的直接下属数量
MATCH (parent)<-[:BELONGS_TO]-(child)
RETURN 
  parent.name AS 上级区划,
  parent.level AS 上级类型,
  COUNT(child) AS 直接下属数量
ORDER BY 直接下属数量 DESC
LIMIT 50
// 区划关系环检测
MATCH (a)-[:BELONGS_TO*1..10]->(a)
RETURN DISTINCT a.name AS 环中的节点

// 最深的行政区划层级
MATCH path = (province:District {level: '市级'})<-[:BELONGS_TO*1..10]-(leaf)
WHERE NOT (leaf)<-[:BELONGS_TO]-()
RETURN 
  [n IN nodes(path) | n.name] AS 完整路径,
  length(path) AS 层级深度
ORDER BY 层级深度 DESC
LIMIT 10