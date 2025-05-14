import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# 加载环境变量
load_dotenv()

# 从环境变量获取配置
NEO4J_CONFIG = {
    "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    "auth": (
        os.getenv("NEO4J_USERNAME", "neo4j"),
        os.getenv("NEO4J_PASSWORD", "password")
    ),
    "database": os.getenv("NEO4J_DATABASE", "neo4j")
}


def get_neo4j_driver():
    """获取 Neo4j 数据库驱动"""
    try:
        driver = GraphDatabase.driver(
            NEO4J_CONFIG["uri"],
            auth=NEO4J_CONFIG["auth"]
        )
        # 测试连接是否有效
        with driver.session() as session:
            session.run("RETURN 1")
        return driver
    except Exception as e:
        raise ConnectionError(f"无法连接到Neo4j数据库: {str(e)}")


def get_neo4j_session(database=None):
    """获取Neo4j会话"""
    driver = get_neo4j_driver()
    return driver.session(database=database or NEO4J_CONFIG["database"])
