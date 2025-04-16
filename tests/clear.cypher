MATCH ()-[r:BELONGS_TO]->()
DELETE r

MATCH ()-[r:CONTAIN]->()
DELETE r


// 删除所有标签为region的节点及其所有关系
MATCH (r:Region)
DETACH DELETE r