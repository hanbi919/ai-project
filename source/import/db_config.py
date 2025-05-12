# db_config.py
from neo4j import GraphDatabase

# Neo4j 数据库配置
NEO4J_CONFIG = {
    "uri": "bolt://localhost:7687",
    "auth": ("neo4j", "password"),  # 替换为你的实际密码
    "database": "neo4j"  # 默认数据库，根据需要修改
}


def get_neo4j_driver():
    """获取 Neo4j 数据库驱动"""
    return GraphDatabase.driver(
        NEO4J_CONFIG["uri"],
        auth=NEO4J_CONFIG["auth"]
    )
