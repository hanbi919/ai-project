from db_config import get_neo4j_driver


def create_indexes():
    driver = get_neo4j_driver()
    with driver.session() as session:
        # 为主项名称创建索引
        session.run(
            "CREATE INDEX main_item_name_index IF NOT EXISTS FOR (m:MainItem) ON (m.name)")

        # 为业务办理项名称创建索引
        session.run(
            "CREATE INDEX business_item_name_index IF NOT EXISTS FOR (b:BusinessItem) ON (b.name)")

        # 为情形创建索引
        session.run(
            "CREATE INDEX scenario_name_index IF NOT EXISTS FOR (s:Scenario) ON (s.name)")

        # 为行政区划创建索引
        session.run(
            "CREATE INDEX district_name_index IF NOT EXISTS FOR (d:District) ON (d.name)")

        # 为材料创建索引
        session.run(
            "CREATE INDEX material_name_index IF NOT EXISTS FOR (m:Material) ON (m.name)")

        # 为办理地点创建索引
        session.run(
            "CREATE INDEX location_name_index IF NOT EXISTS FOR (l:Location) ON (l.name)")


if __name__ == "__main__":
    create_indexes()
