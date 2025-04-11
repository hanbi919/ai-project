from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from neo4j import GraphDatabase


class QueryServiceDetailsAction(Action):
    def name(self) -> Text:
        return "action_query_service_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        main_item = tracker.get_slot("main_item")
        business_item = tracker.get_slot("business_item")
        detail_type = tracker.get_slot("detail_type")
        district = tracker.get_slot("district")

        if not all([main_item, business_item, detail_type]):
            return []

        # 连接Neo4j数据库
        driver = GraphDatabase.driver(
            "bolt://localhost:7687", auth=("neo4j", "password"))

        with driver.session() as session:
            # 查询行政区划和办理地点信息
            result = session.run("""
                MATCH (:MainItem {name: $main_item})-[:HAS_BUSINESS_ITEM]->
                      (b:BusinessItem {name: $business_item})-[:LOCATED_IN]->
                      (d:District {name: $district})-[:HAS_LOCATION]->(l:Location)
                RETURN d.name AS district, l.address AS location, 
                       l.schedule AS schedule, l.phone AS phone,
                       l.fee AS fee, l.deadline AS deadline
                LIMIT 1
            """, main_item=main_item, business_item=business_item, district=district)

            record = result.single()

        driver.close()

        if not record:
            dispatcher.utter_message(text="未找到对应的业务信息")
            return []

        details = ""
        district = record["district"]
        location = record["location"]

        # 处理不同信息类型
        if detail_type == "全部信息":
            details += f"⏰ 办理时间：{record['schedule']}\n"
            details += f"📞 咨询方式：{record['phone']}\n"
            details += f"💰 是否收费：{record['fee']}\n"
            details += f"⏳ 承诺办结时限：{record['deadline']}个工作日\n"
            details += f"📍 办理地点：{location}"
        else:
            if detail_type == "办理时间":
                details += f"⏰ 办理时间：{record['schedule']}\n📍 办理地点：{location}"
            elif detail_type == "咨询方式":
                details += f"📞 咨询方式：{record['phone']}\n📍 办理地点：{location}"
            elif detail_type == "是否收费":
                details += f"💰 是否收费：{record['fee']}\n📍 办理地点：{location}"
            elif detail_type == "承诺办结时限":
                details += f"⏳ 承诺办结时限：{record['deadline']}个工作日\n📍 办理地点：{location}"
            elif detail_type == "办理地点":
                details += f"📍 办理地点：{location}"

        if details:
            header = f"【{business_item}】业务信息（{district}）"
            # 如果查询的是单个信息类型，不显示header
            if detail_type != "全部信息":
                header = ""
            dispatcher.utter_message(text=f"{header}\n{details}".strip())
        else:
            dispatcher.utter_message(text="未找到对应的业务信息")

        return []
