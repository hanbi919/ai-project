import pandas as pd
from neo4j import GraphDatabase
from tqdm import tqdm
import re


class Neo4jRegionInserter:
    def __init__(self, uri, user, password):
        """初始化Neo4j连接"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.region_cache = {}  # 缓存已创建的区划节点

    def close(self):
        """关闭数据库连接"""
        self.driver.close()

    def clear_database(self):
        """清空现有数据(谨慎使用)"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("数据库已清空")

    def create_indexes(self):
        """创建必要的索引"""
        with self.driver.session() as session:
            session.run(
                "CREATE INDEX region_name_index IF NOT EXISTS FOR (r:Region) ON (r.name)")
            session.run(
                "CREATE INDEX service_name_index IF NOT EXISTS FOR (s:Service) ON (s.name)")
            session.run(
                "CREATE INDEX service_item_index IF NOT EXISTS FOR (si:ServiceItem) ON (si.name)")
            print("索引创建完成")

    def process_excel_data(self, file_path):
        """处理Excel文件数据"""
        df = pd.read_excel(file_path)

        # 预处理数据：去除空值，标准化格式
        df = df.dropna(subset=['区划名称', '地区层级', '上级区划名称'])
        df['上级区划名称'] = df['上级区划名称'].apply(
            lambda x: x.split(',') if pd.notna(x) else [])

        return df

    def create_region_node(self, name, level):
        """创建区划节点并缓存"""
        if name in self.region_cache:
            return

        # 自动识别区划类型
        region_type = self.determine_region_type(name, level)

        with self.driver.session() as session:
            session.run(
                """
                MERGE (r:Region {name: $name})
                SET r.level = $level,
                    r.type = $type
                """,
                name=name, level=level, type=region_type
            )
            self.region_cache[name] = True

    def determine_region_type(self, name, level):
        """根据名称和层级自动确定区划类型"""
        if level == '省级':
            return '省'
        elif level == '市级':
            return '地级市'
        elif level == '县级':
            if '区' in name:
                return '市辖区'
            elif '市' in name:
                return '县级市'
            elif '开发区' in name:
                return '经济技术开发区'
            else:
                return '县'
        elif level == '镇（乡、街道）级':
            if '街道' in name:
                return '街道'
            elif '镇' in name:
                return '镇'
            elif '乡' in name:
                return '乡'
            else:
                return '乡镇级区划'
        elif level == '村（社区）级':
            if '社区' in name:
                return '社区'
            elif '村' in name:
                return '村'
            else:
                return '村级区划'
        return '其他'

    def create_region_hierarchy(self, child_name, parent_names):
        """创建区划层级关系"""
        if not parent_names:
            return

        with self.driver.session() as session:
            for parent_name in parent_names:
                session.run(
                    """
                    MATCH (child:Region {name: $child_name})
                    MATCH (parent:Region {name: $parent_name})
                    MERGE (parent)-[:CONTAINS]->(child)
                    MERGE (child)-[:BELONGS_TO]->(parent)
                    """,
                    child_name=child_name, parent_name=parent_name.strip()
                )

    def create_service_nodes(self, row):
        """创建服务相关节点"""
        if pd.isna(row['主项名称']):
            return

        with self.driver.session() as session:
            # 创建主项服务节点
            session.run(
                """
                MERGE (s:Service {name: $name})
                SET s.category = $category
                """,
                name=row['主项名称'],
                category=self.determine_service_category(row['主项名称'])
            )

            # 关联区划和服务
            session.run(
                """
                MATCH (r:Region {name: $region_name})
                MATCH (s:Service {name: $service_name})
                MERGE (r)-[:PROVIDES]->(s)
                """,
                region_name=row['区划名称'],
                service_name=row['主项名称']
            )

            # 处理子项(业务办理项)
            if pd.notna(row['子项名称']):
                session.run(
                    """
                    MATCH (s:Service {name: $service_name})
                    MERGE (si:ServiceItem {name: $item_name})
                    MERGE (s)-[:HAS_ITEM]->(si)
                    """,
                    service_name=row['主项名称'],
                    item_name=row['子项名称']
                )
            elif pd.notna(row['业务办理项名称']):
                session.run(
                    """
                    MATCH (s:Service {name: $service_name})
                    MERGE (si:ServiceItem {name: $item_name})
                    MERGE (s)-[:HAS_ITEM]->(si)
                    """,
                    service_name=row['主项名称'],
                    item_name=row['业务办理项名称']
                )

            # 处理材料
            if pd.notna(row['材料名称']):
                materials = re.split(r'\^|\|', row['材料名称'])
                for material in materials:
                    if material.strip():
                        session.run(
                            """
                            MATCH (si:ServiceItem {name: $item_name})
                            MERGE (m:Material {name: $material_name})
                            MERGE (si)-[:REQUIRES]->(m)
                            """,
                            item_name=row['子项名称'] if pd.notna(
                                row['子项名称']) else row['业务办理项名称'],
                            material_name=material.strip()
                        )

            # 处理情形
            if pd.notna(row['情形']):
                conditions = re.split(r'\^|\|', row['情形'])
                for condition in conditions:
                    if condition.strip():
                        session.run(
                            """
                            MATCH (si:ServiceItem {name: $item_name})
                            MERGE (c:Condition {name: $condition_name})
                            MERGE (si)-[:APPLIES_TO]->(c)
                            """,
                            item_name=row['子项名称'] if pd.notna(
                                row['子项名称']) else row['业务办理项名称'],
                            condition_name=condition.strip()
                        )

    def determine_service_category(self, service_name):
        """根据服务名称确定分类"""
        categories = {
            '计划生育': '卫生健康',
            '就业': '就业创业',
            '职业介绍': '就业创业',
            '社会保障': '社会保障',
            '养老保险': '社会保障',
            '工伤保险': '社会保障',
            '消防安全': '公共安全',
            '税务': '税务',
            '残疾人': '社会保障',
            '动物检疫': '农业农村'
        }

        for key, value in categories.items():
            if key in service_name:
                return value
        return '其他'

    def import_from_excel(self, file_path):
        """从Excel导入数据主方法"""
        try:
            df = self.process_excel_data(file_path)

            print("开始创建区划节点...")
            for _, row in tqdm(df.iterrows(), total=len(df)):
                self.create_region_node(row['区划名称'], row['地区层级'])
                if isinstance(row['上级区划名称'], list):
                    self.create_region_hierarchy(row['区划名称'], row['上级区划名称'])

            # print("开始创建服务节点...")
            # for _, row in tqdm(df.iterrows(), total=len(df)):
            #     self.create_service_nodes(row)

            print("数据导入完成！")
        except Exception as e:
            print(f"导入过程中发生错误: {str(e)}")
            raise


if __name__ == "__main__":
    # 配置Neo4j连接信息
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "password"

    # Excel文件路径
    # EXCEL_FILE = "source/区划测试数据.xlsx"
    EXCEL_FILE = "source/基本信息整理.xlsx"

    # 创建实例并执行导入
    inserter = Neo4jRegionInserter(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    try:
        # 清空数据库(可选)
        # inserter.clear_database()

        # 创建索引
        # inserter.create_indexes()

        # 导入数据
        inserter.import_from_excel(EXCEL_FILE)
    finally:
        inserter.close()
