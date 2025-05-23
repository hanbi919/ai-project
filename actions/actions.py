from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging
from .const import NO_MARTERIAL, NO_FOUND_MARTERIAL, RESP
from .db_config import get_neo4j_session  # 确保这是异步版本的驱动获取方法

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)


class QueryBusinessItemsAction(Action):
    def name(self) -> Text:
        return "action_query_business_items"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        main_item = tracker.get_slot("main_item").rstrip('。')
        if not main_item:
            return []

        try:
            async with await get_neo4j_session() as session:
                result = await session.run("""
                    MATCH (m:MainItem {name: $main_item})-[:HAS_BUSINESS_ITEM]->(b:BusinessItem)
                    RETURN b.name AS business_item
                    ORDER BY b.name
                """, main_item=main_item)

                records = await result.values()
                business_items = [record[0] for record in records]

            if business_items:
                options = "\n- ".join([""] + business_items)
                dispatcher.utter_message(text=f"请选择业务办理项名称：{options}")
            else:
                dispatcher.utter_message(text=f"未找到'{main_item}'下的业务办理项")

        except Exception as e:
            logger.error(f"查询业务办理项时出错: {str(e)}", exc_info=True)
            dispatcher.utter_message(text="查询业务办理项时发生错误")
        finally:
            if 'driver' in locals():
                await driver.close()

        return []


class QueryScenariosAction(Action):
    def name(self) -> Text:
        return "action_query_scenarios"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        main_item = tracker.get_slot("main_item").rstrip('。')
        business_item = tracker.get_slot("business_item").rstrip('。')
        if not business_item:
            return []

        try:
            async with await get_neo4j_session() as session:
                result = await session.run("""
                    MATCH (:MainItem {name: $main_item})-[:HAS_BUSINESS_ITEM]->
                          (b:BusinessItem {name: $business_item})-[:HAS_SCENARIO]->(s:Scenario)
                    RETURN s.name AS scenario
                    ORDER BY s.name
                """, main_item=main_item, business_item=business_item)

                records = await result.values()
                scenarios = [record[0] for record in records]

            if scenarios:
                options = "\n- ".join([""] + scenarios)
                dispatcher.utter_message(text=f"请选择情形：{options}")
            else:
                dispatcher.utter_message(text=f"未找到'{business_item}'下的情形")

        except Exception as e:
            logger.error(f"查询情形时出错: {str(e)}", exc_info=True)
            dispatcher.utter_message(text="查询情形时发生错误")
        finally:
            if 'driver' in locals():
                await driver.close()

        return []


class QueryMaterialsAction(Action):
    def name(self) -> Text:
        return "action_query_materials"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        main_item = tracker.get_slot("main_item")
        if main_item:
            main_item = main_item.rstrip('。')
        business_item = tracker.get_slot("business_item")
        if business_item:
            business_item = business_item.rstrip('。')
        scenario = tracker.get_slot("scenario")
        if scenario:
            scenario = scenario.rstrip('。')
        if not scenario:
            return []

        try:
            async with await get_neo4j_session() as session:
            
                result = await session.run("""
                    MATCH (mi:MainItem {name: $main_item})
                    USING INDEX mi:MainItem(name)
                    MATCH (bi:BusinessItem {name: $business_item})
                    USING INDEX bi:BusinessItem(name)
                    MATCH (s:Scenario {name: $scenario})
                    USING INDEX s:Scenario(name)
                    MATCH (mi)-[:HAS_BUSINESS_ITEM]->(bi)-[:HAS_SCENARIO]->(s)-[:REQUIRES]->(m:Material)
                    RETURN m.name AS material
                    ORDER BY m.name
                """, main_item=main_item, business_item=business_item, scenario=scenario)

                records = await result.values()
                materials = [record[0] for record in records]

            if materials:
                if materials[0] == "无需材料":
                    dispatcher.utter_message(text=NO_MARTERIAL)
                else:
                    materials_list = "\n- " + \
                        "\n- ".join([f"{item}。" for item in materials])
                    dispatcher.utter_message(
                        text=f"{RESP}您需要准备以下材料：{materials_list}")
            else:
                dispatcher.utter_message(text=NO_FOUND_MARTERIAL)

        except Exception as e:
            logger.error(f"查询材料时出错: {str(e)}", exc_info=True)
            dispatcher.utter_message(text="查询材料时发生错误")


        return [SlotSet("scenario", None)]


class ClearSlotAction(Action):
    def name(self) -> Text:
        return "action_reset_main_item"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 无数据库操作，无需修改
        return [SlotSet("business_item", None), SlotSet("scenario", None)]


class OrdinalAction(Action):
    def name(self) -> Text:
        return "action_ordinal_mention"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 无数据库操作，逻辑保持不变
        requested_slot = tracker.get_slot("requested_slot")
        if not requested_slot:
            dispatcher.utter_message(text="系统错误：未找到当前请求的slot")
            return []

        value = tracker.latest_message.get("text", "").strip()
        options = tracker.get_slot("current_options") or {}

        if value.isdigit():
            if value in options:
                selected_value = options[value]
                return [SlotSet(requested_slot, selected_value)]
            else:
                max_option = max(
                    options.keys(), key=lambda x: int(x)) if options else "0"
                dispatcher.utter_message(text=f"请输入1到{max_option}之间的数字！")
        else:
            dispatcher.utter_message(text="请输入有效的数字（如1、2、3）！")
        return []
