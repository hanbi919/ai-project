import asyncio
import os
from dotenv import load_dotenv
from neo4j import AsyncGraphDatabase

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


async def get_neo4j_driver():
    """获取异步Neo4j数据库驱动"""
    try:
        driver = AsyncGraphDatabase.driver(
            NEO4J_CONFIG["uri"],
            auth=NEO4J_CONFIG["auth"]
        )
        # 测试连接是否有效
        async with driver.session() as session:
            await session.run("RETURN 1")
        return driver
    except Exception as e:
        raise ConnectionError(f"无法连接到Neo4j数据库: {str(e)}")


async def get_neo4j_session(database=None):
    """获取异步Neo4j会话"""
    driver = await get_neo4j_driver()
    return driver.session(database=database or NEO4J_CONFIG["database"])


# 使用示例
async def example_usage():
    try:
        session = await get_neo4j_session()
        async with session.begin_transaction() as tx:
            result = await tx.run(
                "MATCH (n) RETURN count(n) AS count"
            )
            record = await result.single()
            print(f"数据库中的节点总数: {record['count']}")
    finally:
        if 'session' in locals():
            await session.close()

# 运行示例
# asyncio.run(example_usage())
