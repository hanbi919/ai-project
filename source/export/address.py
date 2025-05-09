from neo4j import GraphDatabase
import pandas as pd
from actions.db_config import get_neo4j_driver  # 导入驱动获取方法

driver = get_neo4j_driver()

with driver.session() as session:
    result = session.run("MATCH (n:Address) RETURN n.name")
    df = pd.DataFrame([dict(record ) for record in result])
    df.to_excel("output.xlsx", index=False)
