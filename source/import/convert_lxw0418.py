from neo4j import GraphDatabase
import pandas as pd
from typing import List, Dict, Optional
import re
from tqdm import tqdm  # 导入进度条库
from actions.db_config import get_neo4j_driver


class Neo4jImporter:
    def __init__(self, uri, auth):
        self.driver = get_neo4j_driver()

    def close(self):
        self.driver.close()

    def clear_database(self):
        """清空数据库"""
        with self.driver.session() as session:
            session.run("""MATCH(n)
                        WHERE NOT n: District
                        DETACH DELETE n
                        """)
            print("除区划外的数据库已清空")

    def import_data(self, file_path: str):
        """导入Excel数据到Neo4j"""
        # 读取Excel文件
        df = pd.read_excel(file_path)

        print(f"开始导入数据，共 {len(df)} 条记录...")

        with self.driver.session() as session:
            # 导入主项和业务项
            print("\n正在导入主项和业务项...")
            self._import_main_and_business_items(session, df)

            # 导入情形和材料
            print("\n正在导入情形和材料...")
            self._import_scenarios_and_materials(session, df)

            # 导入区划和地点信息
            print("\n正在导入区划和地点信息...")
            self._import_districts_and_locations(session, df)

            # 建立业务项与区划的关系
            print("\n正在建立业务项与区划的关系...")
            self._link_business_items_to_districts(session, df)

        print("\n数据导入完成!")

    def _import_main_and_business_items(self, session, df: pd.DataFrame):
        """导入主项和业务项及其关系"""
        # 获取唯一的主项和业务项组合
        unique_items = df[['主项名称', '业务办理项名称']].drop_duplicates()

        # 添加进度条
        for _, row in tqdm(unique_items.iterrows(), total=len(unique_items), desc="处理主项和业务项"):
            main_item = row['主项名称']
            business_item = row['业务办理项名称']

            # 创建或更新主项节点
            session.run("""
                MERGE (m:MainItem {name: $main_item})
                SET m.name = $main_item
            """, main_item=main_item)

            # 创建或更新业务项节点
            session.run("""
                MERGE (b:BusinessItem {name: $business_item})
                SET b.name = $business_item
            """, business_item=business_item)

            # 建立关系
            session.run("""
                MATCH (m:MainItem {name: $main_item})
                MATCH (b:BusinessItem {name: $business_item})
                MERGE (m)-[:HAS_BUSINESS_ITEM]->(b)
            """, main_item=main_item, business_item=business_item)

    def _import_scenarios_and_materials(self, session, df: pd.DataFrame):
        """导入情形和材料及其关系"""
        for _, row in tqdm(df.iterrows(), total=len(df), desc="处理情形和材料"):
            business_item = row['业务办理项名称']
            scenario = row.get('情形', "无情形")  # 可能为空
            materials = row.get('材料名称', "无需材料")  # 可能为空

            # 创建情形节点并关联到业务项
            session.run("""
                MATCH (b:BusinessItem {name: $business_item})
                MERGE (s:Scenario {name: $scenario,business_item:$business_item})
                MERGE (b)-[:HAS_SCENARIO]->(s)
            """, business_item=business_item, scenario=scenario)

            # 创建材料节点
            session.run("""
                MERGE (m:Material {name: $material, scenario:$scenario})
            """, material=materials, scenario=scenario)

            # 关联到情形节点
            session.run("""
                MATCH (s:Scenario {name: $scenario,business_item: $business_item})
                MATCH (m:Material {name: $material, scenario: $scenario})
                MERGE (s)-[:REQUIRES]->(m)
            """, scenario=scenario, material=materials, business_item=business_item)

    def _import_districts_and_locations(self, session, df: pd.DataFrame):
        """导入区划和地点信息"""
        # 获取唯一的区划和地点组合
        unique_locations = df[['区划名称', '办理地点', '办理时间',
                               '咨询方式', '是否收费', '承诺办结时限', '受理条件']].drop_duplicates()

        # 添加进度条
        for _, row in tqdm(unique_locations.iterrows(), total=len(unique_locations), desc="处理区划和地点"):
            district = row['区划名称']
            location = row['办理地点']
            schedule = row['办理时间']
            phone = row['咨询方式']
            fee = row['是否收费']
            deadline = row['承诺办结时限']
            condition = row['受理条件']

            # 创建区划节点
            session.run("""
                MERGE (d:District {name: $district})
            """, district=district)

            # 创建地点节点（带属性）
            session.run("""
                MERGE (l:Location {address: $location})
                SET l.schedule = $schedule,
                    l.phone = $phone,
                    l.fee = $fee,
                    l.deadline = $deadline,
                    l.condition = $condition
            """, location=location, schedule=schedule, phone=phone,
                        fee=fee, deadline=deadline, condition=condition)

            # 建立区划与地点的关系
            session.run("""
                MATCH (d:District {name: $district})
                MATCH (l:Location {address: $location})
                MERGE (d)-[:HAS_LOCATION]->(l)
            """, district=district, location=location)

    def _link_business_items_to_districts(self, session, df: pd.DataFrame):
        """建立业务项与区划的关系"""
        # 添加进度条
        for _, row in tqdm(df.iterrows(), total=len(df), desc="建立业务项与区划关系"):
            business_item = row['业务办理项名称']
            district = row['区划名称']

            session.run("""
                MATCH (b:BusinessItem {name: $business_item})
                MATCH (d:District {name: $district})
                MERGE (b)-[:LOCATED_IN]->(d)
            """, business_item=business_item, district=district)

    def _split_materials(self, materials_str: str) -> List[str]:
        """分割材料字符串"""
        # 使用^或换行符分割
        if '^' in materials_str:
            return [m.strip() for m in materials_str.split('^') if m.strip()]
        elif '\n' in materials_str:
            return [m.strip() for m in materials_str.split('\n') if m.strip()]
        else:
            return [materials_str.strip()] if materials_str.strip() else []


if __name__ == "__main__":
    importer = Neo4jImporter(URI, AUTH)

    try:
        # 清空数据库（可选）
        # importer.clear_database()
        importer.clear_database()
        # 导入数据
        # importer.import_data("source/import/需要修复.xlsx")
        importer.import_data("source/import/清洗后全市数据.xlsx")
    except Exception as e:
        print(f"导入过程中出错: {e}")
    finally:
        importer.close()
