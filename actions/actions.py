from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from neo4j import GraphDatabase
import logging
from .const import HIGENT

# 配置日志格式（带文件名和行号）
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]',
    level=logging.DEBUG
)
# 初始化日志记录器
logger = logging.getLogger(__name__)


class QueryBusinessItemsAction(Action):
    def name(self) -> Text:
        return "action_query_business_items"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        main_item = tracker.get_slot("main_item")

        if not main_item:
            return []

        # 连接Neo4j数据库
        driver = GraphDatabase.driver(
            "bolt://localhost:7687", auth=("neo4j", "password"))

        with driver.session() as session:
            result = session.run("""
                MATCH (m:MainItem {name: $main_item})-[:HAS_BUSINESS_ITEM]->(b:BusinessItem)
                RETURN b.name AS business_item
                ORDER BY b.name
            """, main_item=main_item)

            business_items = [record["business_item"] for record in result]

        driver.close()

        if business_items:
            options = "\n- ".join([""] + business_items)
            dispatcher.utter_message(text=f"请选择业务办理项名称：{options}")
        else:
            dispatcher.utter_message(text=f"未找到'{main_item}'下的业务办理项")

        return []


class QueryScenariosAction(Action):
    def name(self) -> Text:
        return "action_query_scenarios"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        main_item = tracker.get_slot("main_item")
        business_item = tracker.get_slot("business_item")

        if not business_item:
            return []

        # 连接Neo4j数据库
        driver = GraphDatabase.driver(
            "bolt://localhost:7687", auth=("neo4j", "password"))

        with driver.session() as session:
            result = session.run("""
                MATCH (:MainItem {name: $main_item})-[:HAS_BUSINESS_ITEM]->
                      (b:BusinessItem {name: $business_item})-[:HAS_SCENARIO]->(s:Scenario)
                RETURN s.name AS scenario
                ORDER BY s.name
            """, main_item=main_item, business_item=business_item)

            scenarios = [record["scenario"] for record in result]

        driver.close()

        if scenarios:
            options = "\n- ".join([""] + scenarios)
            dispatcher.utter_message(text=f"请选择情形：{options}")
        else:
            dispatcher.utter_message(text=f"未找到'{business_item}'下的情形")

        return []


class QueryMaterialsAction(Action):
    def name(self) -> Text:
        return "action_query_materials"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        main_item = tracker.get_slot("main_item")
        business_item = tracker.get_slot("business_item")
        scenario = tracker.get_slot("scenario")

        if not scenario:
            return []

        # 连接Neo4j数据库
        driver = GraphDatabase.driver(
            "bolt://localhost:7687", auth=("neo4j", "password"))

        with driver.session() as session:
            result = session.run("""
                MATCH (:MainItem {name: $main_item})-[:HAS_BUSINESS_ITEM]->
                      (:BusinessItem {name: $business_item,main_item:$main_item})-[:HAS_SCENARIO]->
                      (s:Scenario {name: $scenario,business_item:$business_item,main_item:$main_item})-[:REQUIRES]->(m:Material)
                RETURN m.name AS material
                ORDER BY m.name
            """, main_item=main_item, business_item=business_item, scenario=scenario)

            materials = [record["material"] for record in result]

        driver.close()
        if materials:
            if materials[0] == "无需材料":
                dispatcher.utter_message(text=f"{HIGENT}办理这个业务，您不需要准备材料。")
            else:
                materials_list = "\n- " + "\n- ".join(materials)
                dispatcher.utter_message(
                    text=f"{HIGENT}您需要准备以下材料：{materials_list}")
        else:
            dispatcher.utter_message(text=f"{HIGENT}未找到对应的材料信息，请确认您的选择是否正确。")

        return [SlotSet("scenario", None),]


class OrdinalAction(Action):
    def name(self) -> Text:
        return "action_ordinal_mention"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        requested_slot = tracker.get_slot("requested_slot")
        if not requested_slot:
            dispatcher.utter_message(text="系统错误：未找到当前请求的slot")
            return []

        # 2. 获取用户输入的数字
        value = tracker.latest_message.get("text", "").strip()

        options = tracker.get_slot("current_options") or {}
        # 检查输入是否是数字且在 options 的范围内
        if value.isdigit():
            # 检查数字是否在 options 的键中
            if value in options:
                selected_value = options[value]
                return [SlotSet(requested_slot, selected_value)]
            else:
                # 数字超出范围（比如 options 只有1-3，但用户输入4）
                max_option = max(
                    options.keys(), key=lambda x: int(x)) if options else "0"
                dispatcher.utter_message(text=f"请输入1到{max_option}之间的数字！"
                                         )
        else:
            # 输入不是数字
            dispatcher.utter_message(text="请输入有效的数字（如1、2、3）！")
