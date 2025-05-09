from neo4j import GraphDatabase
from actions.db_config import get_neo4j_driver


class LocationAddressQuery:
    def __init__(self, uri, user, password):
        self.driver = get_neo4j_driver()

    def close(self):
        self.driver.close()

    def fuzzy_search(self, keyword):
        """模糊查询address并返回关联的location信息"""
        with self.driver.session() as session:
            query = """
                MATCH (loc:Location)-[:HAS_ADDRESS]->(addr:Address)
                WHERE toLower(addr.name) CONTAINS toLower($keyword)
                RETURN 
                    loc AS location,
                    collect(addr) AS matched_addresses,
                    count(addr) AS match_count
                ORDER BY match_count DESC
            """
            result = session.run(query, keyword=keyword)
            return list(result)

    def format_results(self, records):
        """格式化查询结果"""
        formatted = []
        for record in records:
            location = record["location"]
            addresses = record["matched_addresses"]

            location_info = {
                "id": location.id,
                "name": location.get("name", ""),
                "phone": location.get("phone", "无"),
                "schedule": location.get("schedule", "无"),
                "address_count": record["match_count"],
                "addresses": []
            }

            for addr in addresses:
                location_info["addresses"].append({
                    "id": addr.id,
                    "address": addr.get("name", ""),
                    "created": addr.get("created_at", "")
                })

            formatted.append(location_info)
        return formatted


if __name__ == "__main__":
    # 配置连接
    neo4j_uri = "bolt://localhost:7687"
    neo4j_user = "neo4j"
    neo4j_password = "password"

    searcher = LocationAddressQuery(neo4j_uri, neo4j_user, neo4j_password)

    try:
        while True:
            keyword = input("\n请输入地址关键词(q退出): ").strip()
            if keyword.lower() == 'q':
                break

            print(f"\n搜索 '{keyword}' 的结果：")

            # 执行查询
            raw_results = searcher.fuzzy_search(keyword)
            results = searcher.format_results(raw_results)

            # 显示结果
            for i, loc in enumerate(results, 1):
                print(f"\n{i}. [Location ID: {loc['id']}]")
                print(f"   📞 电话: {loc['phone']}")
                print(f"   🕒 时间: {loc['schedule']}")
                print(f"   🔍 匹配地址数: {loc['address_count']}")

                for j, addr in enumerate(loc["addresses"], 1):
                    print(f"     {j}. [Address ID: {addr['id']}]")
                    print(f"        {addr['address']}")

    finally:
        searcher.close()
