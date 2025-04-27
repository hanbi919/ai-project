from neo4j import GraphDatabase
import pandas as pd

driver = GraphDatabase.driver(
    "bolt://localhost:7687", auth=("neo4j", "password"))

with driver.session() as session:
    result = session.run("MATCH (n:Address) RETURN n.name")
    df = pd.DataFrame([dict(record ) for record in result])
    df.to_excel("output.xlsx", index=False)
