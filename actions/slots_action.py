from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from .sys_logger import logger
from .const import RESP, HIGENT, FOLLOW_UP, NO_MAIN_ITEM
from .db_config import get_neo4j_session  # 确保这是异步版本的驱动获取方法

def parse_options(options_str: str) -> dict:
    """异步版本保持不变"""
    lines = options_str.split('\n')
    mapping = {}
    for line in lines:
        if '.' in line:
            parts = line.split('.', 1)
            num = parts[0].strip()
            value = parts[1].strip()
            mapping[num] = value
    return mapping


class AskForMainItemSlotAction(Action):
    def name(self) -> Text:
        return "action_ask_main_item"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.debug("Starting async action_ask_main_item execution")
        main_item = tracker.get_slot("main_item")

        if main_item is None:
            dispatcher.utter_message(text=NO_MAIN_ITEM)
            return []

        try:
            async with await get_neo4j_session() as session:
                result = await session.run("""
                    MATCH (m:MainItem)
                    RETURN DISTINCT m.name AS main_item
                    ORDER BY m.name
                    LIMIT 10
                """)
                records = await result.values()
                main_items = [record[0] for record in records]

                if main_items:
                    numbered_items = [
                        f"{idx + 1}. {item}"
                        for idx, item in enumerate(sorted(main_items))
                    ]
                    str = '\n'.join(numbered_items)
                    message = f"{RESP}请选择您要查询的主项名称：\n{str}"
                else:
                    message = f"{HIGENT}当前没有可用的主项服务"

                dispatcher.utter_message(text=message)

        except Exception as e:
            logger.error(f"查询主项时出错：{str(e)}", exc_info=True)
            dispatcher.utter_message(text=f"{HIGENT}查询主项服务时发生错误，请稍后再试")

        return []


class AskForBusinessItemSlotAction(Action):
    def name(self) -> Text:
        return "action_ask_business_item"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.debug("Starting async action_ask_business_item execution")
        main_item = tracker.get_slot("main_item")

        if not main_item:
            dispatcher.utter_message(text="请先选择主项服务")
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

                if len(business_items) == 1:
                    if tracker.active_loop:
                        form_name = tracker.active_loop.get("name")
                    return [SlotSet("business_item", business_items[0]), FollowupAction(form_name)]

                if business_items:
                    numbered_items = [
                        f"{idx + 1}. {item}。"
                        for idx, item in enumerate(sorted(business_items))
                    ]
                    _str = "\n".join(numbered_items)
                    message = f"{FOLLOW_UP}请选择'{main_item}'下的业务办理项: \n{_str}"
                else:
                    message = f"{HIGENT}'{main_item}'下没有可用的业务办理项"

                dispatcher.utter_message(text=message)

        except Exception as e:
            logger.error(f"查询业务办理项时出错：{str(e)}", exc_info=True)
            dispatcher.utter_message(text=f"{HIGENT}查询业务办理项时发生错误，请稍后再试")
        return []


class AskForScenarioSlotAction(Action):
    def name(self) -> Text:
        return "action_ask_scenario"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.debug("Starting async action_ask_scenario execution")
        main_item = tracker.get_slot("main_item").rstrip('。')
        business_item = tracker.get_slot("business_item").rstrip('。')

        if not business_item:
            dispatcher.utter_message(text="请先选择业务办理项")
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

                if scenarios and (scenarios[0] == "无情形" or len(scenarios) == 1):
                    return [SlotSet("scenario", scenarios[0]), SlotSet("current_options", {}), SlotSet("requested_slot", None)]

                if scenarios:
                    scenarios_dict = {
                        str(i+1): scenario for i, scenario in enumerate(scenarios)}
                    options = "\n".join(
                        [f"{i+1}. {item}。" for i, item in enumerate(scenarios)])
                    message = f"{FOLLOW_UP}请选择'{business_item}'下的情形：\n{options}"
                    dispatcher.utter_message(text=message)
                    return [SlotSet("current_options", scenarios_dict)]
                else:
                    message = f"{HIGENT}'{business_item}'下没有可用的情形"
                    dispatcher.utter_message(text=message)

        except Exception as e:
            logger.error(f"查询情形时出错：{str(e)}", exc_info=True)
            dispatcher.utter_message(text=f"{HIGENT}查询情形时发生错误，请稍后再试")
        return []


class AskForDistrictSlotAction(Action):
    def name(self) -> Text:
        return "action_ask_area"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.debug("Starting async action_ask_district execution")
        main_item = tracker.get_slot("main_item").rstrip('。')
        business_item = tracker.get_slot("business_item").rstrip('。')

        if not business_item:
            dispatcher.utter_message(text="请先选择业务办理项")
            return []

        try:
            async with await get_neo4j_session() as session:
                result = await session.run("""
                    MATCH (:MainItem {name: $main_item})-[:HAS_BUSINESS_ITEM]->
                          (b:BusinessItem {name: $business_item})-[:LOCATED_IN]->(s:District)
                    RETURN s.name AS district
                    ORDER BY s.name
                """, main_item=main_item, business_item=business_item)
                records = await result.values()
                districts = [record[0] for record in records]

                if len(districts) == 1:
                    if tracker.active_loop:
                        form_name = tracker.active_loop.get("name")
                    return [SlotSet("area", districts[0]), FollowupAction(form_name)]

                if districts:
                    message = f"{HIGENT}请说出您的地理位置，例如：朝阳区重庆街道，双阳区鹿乡镇"
                else:
                    message = f"{HIGENT}'{business_item}'没有查询到指定的服务区划"

                dispatcher.utter_message(text=message)

        except Exception as e:
            logger.error(f"查询区划时出错：{str(e)}", exc_info=True)
            dispatcher.utter_message(text=f"{HIGENT}查询服务区划时发生错误，请稍后再试")

        return []


class AskForLevelSlotAction(Action):
    def name(self) -> Text:
        return "action_ask_level"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logger.debug("Starting async action_ask_level execution")
        main_item = tracker.get_slot("main_item").rstrip('。')
        business_item = tracker.get_slot("business_item").rstrip('。')

        if not business_item:
            dispatcher.utter_message(text="请先选择业务办理项")
            return []

        try:
            async with await get_neo4j_session() as session:
                
                result = await session.run("""
                    MATCH (:MainItem {name: $main_item})-[:HAS_BUSINESS_ITEM]->
                          (b:BusinessItem {name: $business_item})-[:LOCATED_IN]->(s:District)
                    WITH DISTINCT s.level AS level
                    RETURN level
                    ORDER BY level
                """, main_item=main_item, business_item=business_item)
                records = await result.values()
                levels = [record[0] for record in records]

                if len(levels) == 1:
                    if tracker.active_loop:
                        form_name = tracker.active_loop.get("name")
                    return [SlotSet("level", levels[0]), FollowupAction(form_name)]

                if levels:
                    options = "\n".join(
                        [f"{i+1}. {item}" for i, item in enumerate(levels)])
                    message = f"{FOLLOW_UP}请选择'{business_item}'服务的层级：\n{options}"
                else:
                    message = f"{HIGENT}'{business_item}'没有指定服务层级"

                dispatcher.utter_message(text=message)

        except Exception as e:
            logger.error(f"查询层级时出错：{str(e)}", exc_info=True)
            dispatcher.utter_message(text=f"{HIGENT}查询服务层级时发生错误，请稍后再试")
        return []
