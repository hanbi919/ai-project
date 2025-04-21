from neo4j import GraphDatabase
import pandas as pd
from tqdm import tqdm

# Neo4j 连接配置
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "password"  # 替换为您的密码

"""_summary_
    根据全部的区划数据导入neo4j
"""

class DistrictImporter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def import_districts(self, file_path):
        # 读取Excel文件
        df = pd.read_excel(file_path)

        # 创建唯一约束
        # with self.driver.session() as session:
        #     session.run("""
        #     CREATE CONSTRAINT unique_district IF NOT EXISTS
        #     FOR (d:District)
        #     REQUIRE (d.name, d.parent_names) IS NODE KEY
        #     """)

        # 导入数据
        with self.driver.session() as session:
            # 使用tqdm显示进度条
            for _, row in tqdm(df.iterrows(), total=len(df)):
                district_name = row['区划名称']
                level = row['地区层级']
                parent_names = row['上级区划名称']

                # 创建或获取当前区划节点
                session.run("""
                MERGE (d:District {name: $name, parent_names: $parent_names})
                ON CREATE SET d.level = $level
                """, name=district_name, parent_names=parent_names, level=level)

                # 处理上级关系
                parents = [p.strip()
                           for p in parent_names.split(',') if p.strip()]
                for i, parent_name in enumerate(parents):
                    # 上级节点的parent_names是其更上一级的组合
                    parent_parents = ','.join(
                        parents[i+1:]) if i+1 < len(parents) else ''

                    # 创建或获取上级节点
                    session.run("""
                    MERGE (p:District {name: $parent_name, parent_names: $parent_parents})
                    """, parent_name=parent_name, parent_parents=parent_parents)

                    # 如果这是直接上级，则建立关系
                    if i == 0:
                        session.run("""
                        MATCH (d:District {name: $name, parent_names: $parent_names})
                        MATCH (p:District {name: $parent_name, parent_names: $parent_parents})
                        MERGE (d)-[:BELONGS_TO]->(p)
                        """, name=district_name, parent_names=parent_names,
                                    parent_name=parent_name, parent_parents=parent_parents)


if __name__ == "__main__":
    importer = DistrictImporter(URI, USER, PASSWORD)
    try:
        print("开始区划数据导入完成！")
        importer.import_districts("source/create/不重复区划数据.xlsx")
        print("区划数据导入完成！")
    finally:
        importer.close()
