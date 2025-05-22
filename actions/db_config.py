import asyncio
import os
from dotenv import load_dotenv
from neo4j import AsyncGraphDatabase
from typing import AsyncGenerator
from contextlib import asynccontextmanager

# 加载环境变量
load_dotenv()

# 从环境变量获取配置
NEO4J_CONFIG = {
    "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    "auth": (
        os.getenv("NEO4J_USERNAME", "neo4j"),
        os.getenv("NEO4J_PASSWORD", "password")
    ),
    "database": os.getenv("NEO4J_DATABASE", "neo4j"),
    "max_connection_pool_size": int(os.getenv("NEO4J_MAX_POOL_SIZE", 10))
}


class Neo4jConnectionPool:
    """Neo4j异步连接池"""

    _driver = None
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self):
        """初始化连接池"""
        if self._driver is None:
            try:
                self._driver = AsyncGraphDatabase.driver(
                    NEO4J_CONFIG["uri"],
                    auth=NEO4J_CONFIG["auth"],
                    max_connection_pool_size=NEO4J_CONFIG["max_connection_pool_size"]
                )
                # 测试连接是否有效
                async with self._driver.session() as session:
                    await session.run("RETURN 1")
            except Exception as e:
                raise ConnectionError(f"无法连接到Neo4j数据库: {str(e)}")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator:
        """获取一个数据库会话"""
        if self._driver is None:
            await self.initialize()

        session = self._driver.session(database=NEO4J_CONFIG["database"])
        try:
            yield session
        finally:
            await session.close()

    async def close(self):
        """关闭连接池"""
        if self._driver is not None:
            await self._driver.close()
            self._driver = None


# 全局连接池实例
neo4j_pool = Neo4jConnectionPool()


async def get_neo4j_session():
    """获取Neo4j会话的快捷方式"""
    return neo4j_pool.get_session()


async def close_neo4j_pool():
    """关闭连接池的快捷方式"""
    await neo4j_pool.close()

# 使用示例


async def query_example():
    async with await get_neo4j_session() as session:
        result = await session.run("MATCH (n) RETURN count(n) AS count")
        record = await result.single()
        print(f"Total nodes in database: {record['count']}")


async def main():
    try:
        await query_example()
    finally:
        await close_neo4j_pool()

if __name__ == "__main__":
    asyncio.run(main())
