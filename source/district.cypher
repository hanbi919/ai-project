MATCH (d:District {level: "市级"}) RETURN d.name


MATCH (d:District)-[:BELONGS_TO]->(p:District {name: "长春市"}) 
WHERE d.level = "县级"
RETURN d.name


MATCH path = (d:District {name: "东站街道"})-[:BELONGS_TO*]->(top)
WHERE top.name = "二道区"
RETURN [n in nodes(path) | n.name] AS hierarchy


MATCH (n)
DETACH DELETE n


MATCH (city:District {name: '长春市'})<-[:BELONGS_TO]-(county:District)
RETURN county.name, county.level

// 查找特定街道的完整层级路径:
MATCH path = (street:District {name: '二道村'})-[:BELONGS_TO*]->(province)
RETURN [n IN nodes(path) | n.name] AS hierarchy


MATCH (city:District {name: '二道区'})<-[:BELONGS_TO]-(county:District)
RETURN county.name, county.level


CREATE CONSTRAINT unique_district_name_parent 
IF NOT EXISTS 
FOR (d:District) 
REQUIRE (d.name, d.parent_names) IS NODE KEY