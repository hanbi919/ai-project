from neo4j import GraphDatabase
from tqdm import tqdm
"""_summary_

查询数据库，对全部的location的address进行拆分
"""

class Neo4jAddressProcessor:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def process_location_addresses(self):
        with self.driver.session() as session:
            # 查询所有Location节点
            locations = session.run(
                "MATCH (l:Location) RETURN ID(l) as id, l.address as address")
            locations = list(locations)  # 转换为列表以便多次使用

            print(f"找到 {len(locations)} 个Location节点需要处理...")

            for record in tqdm(locations, desc="处理Location地址"):
                node_id = record["id"]
                address = record["address"]

                if not address:
                    continue

                # 拆分地址（支持分号和换行符作为分隔符）
                addresses = [addr.strip() for addr in address.replace(
                    "\n", "；").split("；") if addr.strip()]

                # if len(addresses) <= 1:
                #     continue  # 不需要拆分的情况

                # 为每个拆分后的地址创建Address节点并建立关系
                for addr in addresses:
                    session.run("""
                        MATCH (l:Location) WHERE ID(l) = $node_id
                        MERGE (a:Address {name: $address})
                        MERGE (l)-[:HAS_ADDRESS]->(a)
                    """, node_id=node_id, address=addr)

                # 可选：从Location节点中移除address属性
                # session.run("""
                #     MATCH (l:Location) WHERE ID(l) = $node_id
                #     REMOVE l.address
                # """, node_id=node_id)


if __name__ == "__main__":
    # Neo4j数据库连接配置
    URI = "bolt://localhost:7687"
    USER = "neo4j"
    PASSWORD = "password"  # 替换为你的密码

    # 创建处理器实例
    processor = Neo4jAddressProcessor(URI, USER, PASSWORD)

    try:
        # 处理Location地址
        processor.process_location_addresses()
        print("地址处理完成！")
    finally:
        processor.close()
