import pandas as pd
from neo4j import GraphDatabase
from tqdm import tqdm

# Neo4j数据库连接配置
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password")  # 替换为您的用户名和密码


class Neo4jImporter:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)

    def close(self):
        self.driver.close()

    def clear_database(self):
        """清空数据库"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("数据库已清空")

    def create_constraints(self):
        """创建必要的约束"""
        with self.driver.session() as session:
            # 确保MainItem和BusinessItem的组合是唯一的
            session.run("""
            CREATE CONSTRAINT business_item_name IF NOT EXISTS 
            FOR (b:BusinessItem) 
            REQUIRE b.name IS UNIQUE
            """)
            print("已创建MainItem和BusinessItem组合唯一性约束")

    def import_test_data(self, test_data_path):
        """导入测试数据.xlsx"""
        print("开始导入测试数据...")
        df = pd.read_excel(test_data_path, sheet_name="Sheet1")

        with self.driver.session() as session:
            # 导入主项名称和业务办理项名称
            for _, row in tqdm(df.iterrows(), total=len(df), desc="导入主项和业务项"):
                main_item = row["主项名称"]
                business_item = row["业务办理项名称"]
                scenario = row["情形"]
                materials = row["材料"].split(
                    "<br>") if isinstance(row["材料"], str) else []

                # 创建或获取主项节点
                session.run("""
                MERGE (m:MainItem {name: $main_item})
                """, main_item=main_item)

                # 创建或获取业务项节点并建立关系
                # 现在使用关系属性来存储组合键
                session.run("""
                MATCH (m:MainItem {name: $main_item})
                MERGE (b:BusinessItem {name: $business_item})
                MERGE (m)-[r:HAS_BUSINESS_ITEM {
                    main_item: $main_item, 
                    business_item: $business_item
                }]->(b)
                """, main_item=main_item, business_item=business_item)

                # 创建情形节点和关系
                if pd.notna(scenario):
                    session.run("""
                        MERGE (s:Scenario {name: $scenario, business_item: $business_item})
                        WITH s
                        MATCH (m:MainItem {name: $main_item})-[:HAS_BUSINESS_ITEM]->(b:BusinessItem {name: $business_item})
                        MERGE (b)-[:HAS_SCENARIO]->(s)
                                """,
                                scenario=scenario,
                                business_item=business_item,
                                main_item=main_item)

                    # 创建材料节点和关系
                    for material in materials:
                        material = material.strip()
                        if material:
                            session.run("""
                            MERGE (mat:Material {name: $material})
                            WITH mat
                            MATCH (s:Scenario {name: $scenario, business_item: $business_item})
                            MERGE (s)-[:REQUIRES]->(mat)
                            """, material=material, scenario=scenario, business_item=business_item,)

            print("测试数据导入完成")

    def import_business_data(self, business_data_path):
        """导入残疾人证业务.xlsx"""
        print("开始导入业务数据...")
        df = pd.read_excel(business_data_path, sheet_name="Sheet1")

        with self.driver.session() as session:
            for _, row in tqdm(df.iterrows(), total=len(df), desc="导入业务数据"):
                district = row["区划名称"]
                main_item = row["主项名称"]
                business_item = row["业务办理项名称"]
                deadline = row["承诺办结时限"]
                fee = row["是否收费"]
                locations = row["办理地点"].split(
                    "；") if isinstance(row["办理地点"], str) else []
                schedule = row["办理时间"]
                phone = row["咨询方式"]

                # 创建或获取行政区划节点
                session.run("""
                MERGE (d:District {name: $district})
                WITH d
                MATCH (b:BusinessItem {name: $business_item})
                MERGE (b)-[:LOCATED_IN]->(d)
                """, district=district, business_item=business_item)

                # 处理多个办理地点
                for location in locations:
                    location = location.strip()
                    if location:
                        # 创建办理地点节点和关系
                        session.run("""
                        MERGE (l:Location {
                            address: $location,
                            schedule: $schedule,
                            phone: $phone,
                            fee: $fee,
                            deadline: $deadline
                        })
                        WITH l
                        MATCH (d:District {name: $district})
                        MERGE (d)-[:HAS_LOCATION]->(l)
                        """,
                                    location=location,
                                    schedule=schedule,
                                    phone=phone,
                                    fee=fee,
                                    deadline=deadline,
                                    district=district)

            print("业务数据导入完成")


if __name__ == "__main__":
    # 文件路径
    test_data_path = "source/main_item.xlsx"
    business_data_path = "source/detail.xlsx"

    # 创建导入器实例
    importer = Neo4jImporter(URI, AUTH)

    try:
        # 清空数据库（可选）
        importer.clear_database()

        # 创建约束
        # importer.create_constraints()

        # 导入数据
        importer.import_test_data(test_data_path)
        importer.import_business_data(business_data_path)

        print("数据导入成功完成！")
    except Exception as e:
        print(f"导入过程中发生错误: {e}")
    finally:
        importer.close()
