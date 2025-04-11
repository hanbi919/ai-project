from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from neo4j import GraphDatabase
import logging

# 初始化logger
logger = logging.getLogger(__name__)

class AskForMainItemSlotAction(Action):
    def name(self) -> Text:
        return "action_ask_main_item"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 获取当前slot值并记录
        main_item = tracker.get_slot("main_item")
        logger.debug(f"Current 'main_item' slot value: {main_item}")
        # 记录开始执行action
        logger.debug("Starting action_ask_main_item execution")

        # if not main_item:
        #     return []

        # 连接Neo4j数据库
        driver = GraphDatabase.driver(
            "bolt://localhost:7687", auth=("neo4j", "password"))

        try:
            # 连接数据库
            with driver.session() as session:
                # 查询所有不重复的主项名称
                result = session.run("""
                    MATCH (m:MainItem)
                    RETURN DISTINCT m.name AS main_item
                    ORDER BY m.name
                """)

                # 提取结果
                main_items = [record["main_item"] for record in result]
                logger.debug(f"Found {len(main_items)} main items in database")
                if main_items:
                    # 格式化输出
                    options = "\n- ".join([""] + main_items)
                    message = f"请选择您要查询的主项名称：{options}"
                    logger.debug(
                        f"Prepared message with {len(main_items)} options")
                else:
                    message = "当前没有可用的主项服务"
                    logger.warning("No main items found in database")

                # 发送回复
                dispatcher.utter_message(text=message)
                logger.debug("Response message sent to user")

        except Exception as e:
            dispatcher.utter_message(text=f"查询主项时出错：{str(e)}")

        finally:
            # 确保关闭连接
            if 'driver' in locals():
                driver.close()

        return []


class AskForBusinessItemSlotAction(Action):
    def name(self) -> Text:
        return "action_ask_business_item"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 获取当前slot值并记录
        main_item = tracker.get_slot("main_item")
        logger.debug(f"Current 'main_item' slot value: {main_item}")
        # 记录开始执行action
        logger.debug("Starting action_ask_business_item execution")

        # if not main_item:
        #     return []

        # 连接Neo4j数据库
        driver = GraphDatabase.driver(
            "bolt://localhost:7687", auth=("neo4j", "password"))

        try:
            # 连接数据库
            with driver.session() as session:
                # 查询所有不重复的主项名称
                result = session.run("""
                    MATCH (m:MainItem {name: $main_item})-[:HAS_BUSINESS_ITEM]->(b:BusinessItem)
                RETURN b.name AS business_item
                ORDER BY b.name
                """, main_item=main_item)

                # 提取结果
                business_items = [record["business_item"] for record in result]
                logger.debug(
                    f"Found {len(business_items)} main items in database")
                if business_items:
                    # 格式化输出
                    options = "\n- ".join([""] + business_items)
                    message = f"请选择业务办理项名称：{options}"
                    logger.debug(
                        f"Prepared message with {len(business_items)} options")
                else:
                    message = "当前没有可用的业务办理项名称"
                    logger.warning("No business items found in database")

                # 发送回复
                dispatcher.utter_message(text=message)
                logger.debug("Response message sent to user")

        except Exception as e:
            dispatcher.utter_message(text=f"查询业务办理项时出错：{str(e)}")

        finally:
            # 确保关闭连接
            if 'driver' in locals():
                driver.close()

        return []


class AskForScenarioSlotAction(Action):
    def name(self) -> Text:
        return "action_ask_scenario"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 获取当前slot值并记录
        main_item = tracker.get_slot("main_item")
        business_item = tracker.get_slot("business_item")
        logger.debug(f"Current 'main_item' slot value: {main_item}")
        # 记录开始执行action
        logger.debug("Starting action_ask_business_item execution")

        if not business_item:
            return []

        # 连接Neo4j数据库
        driver = GraphDatabase.driver(
            "bolt://localhost:7687", auth=("neo4j", "password"))

        try:
            # 连接数据库
            with driver.session() as session:
                # 查询所有不重复的主项名称
                result = session.run("""
                    MATCH (:MainItem {name: $main_item})-[:HAS_BUSINESS_ITEM]->
                      (b:BusinessItem {name: $business_item})-[:HAS_SCENARIO]->(s:Scenario)
                RETURN s.name AS scenario
                ORDER BY s.name
            """, main_item=main_item, business_item=business_item)

                # 提取结果
                scenarios = [record["scenario"] for record in result]
                logger.debug(
                    f"Found {len(scenarios)} main items in database")
                if scenarios:
                    # 格式化输出
                    options = "\n- ".join([""] + scenarios)
                    message = f"请选择情形：{options}"
                    logger.debug(
                        f"Prepared message with {len(scenarios)} options")
                else:
                    message = f"未找到'{business_item}'下的情形"
                    logger.warning("No scenarios items found in database")

                # 发送回复
                dispatcher.utter_message(text=message)
                logger.debug("Response message sent to user")

        except Exception as e:
            dispatcher.utter_message(text=f"查询情形时出错：{str(e)}")

        finally:
            # 确保关闭连接
            if 'driver' in locals():
                driver.close()

        return []


class AskForDistrictSlotAction(Action):
    def name(self) -> Text:
        return "action_ask_district"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 获取当前slot值并记录
        main_item = tracker.get_slot("main_item")
        business_item = tracker.get_slot("business_item")
        logger.debug(f"Current 'main_item' slot value: {main_item}")
        # 记录开始执行action
        logger.debug("Starting action_ask_location execution")

        if not business_item:
            return []

        # 连接Neo4j数据库
        driver = GraphDatabase.driver(
            "bolt://localhost:7687", auth=("neo4j", "password"))

        try:
            # 连接数据库
            with driver.session() as session:
                # 查询所有不重复的主项名称
                result = session.run("""
                    MATCH (:MainItem {name: $main_item})-[:HAS_BUSINESS_ITEM]->
                      (b:BusinessItem {name: $business_item})-[:LOCATED_IN]->(s:District)
                RETURN s.name AS district
                ORDER BY s.name
            """, main_item=main_item, business_item=business_item)

                # 提取结果
                districts = [record["district"] for record in result]
                logger.debug(
                    f"Found {len(districts)} main items in database")
                if districts:
                    # 格式化输出
                    options = "\n- ".join([""] + districts)
                    message = f"请选择区划名称：{options}"
                    logger.debug(
                        f"Prepared message with {len(districts)} options")
                else:
                    message = f"未找到'{business_item}'下的区划名称"
                    logger.warning("No scenarios items found in database")

                # 发送回复
                dispatcher.utter_message(text=message)
                logger.debug("Response message sent to user")

        except Exception as e:
            dispatcher.utter_message(text=f"查询区划名称时出错：{str(e)}")

        finally:
            # 确保关闭连接
            if 'driver' in locals():
                driver.close()

        return []
