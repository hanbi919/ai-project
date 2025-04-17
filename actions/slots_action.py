from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from neo4j import GraphDatabase
import logging

# 配置日志格式（带文件名和行号）
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]',
    level=logging.DEBUG
)
# 初始化日志记录器
logger = logging.getLogger(__name__)

# Neo4j数据库配置
NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "password")


def parse_options(options_str: str) -> dict:
    """
    解析选项字符串，返回数字到选项的映射字典

    参数:
        options_str: 包含选项的字符串，格式为"1. 选项1\n2. 选项2"

    返回:
        字典，格式如 {"1": "选项1", "2": "选项2"}
    """
    lines = options_str.split('\n')
    mapping = {}

    for line in lines:
        if '.' in line:  # 检测是否是选项行
            parts = line.split('.', 1)  # 只分割第一个点
            num = parts[0].strip()
            value = parts[1].strip()
            mapping[num] = value

    return mapping


class AskForMainItemSlotAction(Action):
    """询问用户选择主项名称的动作"""

    def name(self) -> Text:
        """返回动作名称"""
        return "action_ask_main_item"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        执行动作，查询并展示所有可用的主项名称

        参数:
            dispatcher: 用于发送消息给用户的工具
            tracker: 当前对话状态跟踪器
            domain: 对话领域配置

        返回:
            空的事件列表
        """
        # 记录调试信息
        logger.debug("Starting action_ask_main_item execution")

        # 获取当前slot值
        main_item = tracker.get_slot("main_item")
        logger.debug(f"Current 'main_item' slot value: {main_item}")

        try:
            # 连接Neo4j数据库
            with GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH) as driver:
                with driver.session() as session:
                    # 查询所有不重复的主项名称
                    result = session.run("""
                        MATCH (m:MainItem)
                        RETURN DISTINCT m.name AS main_item
                        ORDER BY m.name
                        LIMIT 10
                    """)
                    # 用于调试
                    # result = session.run("""
                    #     MATCH (m:MainItem {name:"自行招用保安员单位的备案"})
                    #     RETURN DISTINCT m.name AS main_item
                    #     ORDER BY m.name
                    #     LIMIT 10
                    # """)

                    # 提取结果并创建按钮
                    main_items = [record["main_item"] for record in result]
                    logger.debug(
                        f"Found {len(main_items)} main items in database")

                    if main_items:
                        # 创建按钮列表
                        buttons = [
                            {
                                "title": item,
                                "payload": f"/inform_main_item{{\"main_item\":\"{item}\"}}"
                            }
                            for item in main_items
                        ]

                        message = "请选择您要查询的主项名称："
                        logger.debug(
                            f"Prepared message with {len(main_items)} options")
                    else:
                        message = "当前没有可用的主项服务"
                        logger.warning("No main items found in database")

                    # 发送带按钮的回复
                    dispatcher.utter_message(text=message, buttons=buttons)

        except Exception as e:
            logger.error(f"查询主项时出错：{str(e)}")
            dispatcher.utter_message(text="查询主项服务时发生错误，请稍后再试")

        return []


class AskForBusinessItemSlotAction(Action):
    """询问用户选择业务办理项的动作"""

    def name(self) -> Text:
        """返回动作名称"""
        return "action_ask_business_item"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        根据选择的主项查询对应的业务办理项

        参数:
            dispatcher: 用于发送消息给用户的工具
            tracker: 当前对话状态跟踪器
            domain: 对话领域配置

        返回:
            空的事件列表
        """
        logger.debug("Starting action_ask_business_item execution")

        # 获取当前slot值
        main_item = tracker.get_slot("main_item")
        logger.debug(f"Current 'main_item' slot value: {main_item}")

        if not main_item:
            dispatcher.utter_message(text="请先选择主项服务")
            return []

        try:
            # 连接Neo4j数据库
            with GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH) as driver:
                with driver.session() as session:
                    # 查询指定主项下的所有业务办理项
                    result = session.run("""
                        MATCH (m:MainItem {name: $main_item})-[:HAS_BUSINESS_ITEM]->(b:BusinessItem)
                        RETURN b.name AS business_item
                        ORDER BY b.name
                        
                    """, main_item=main_item)

                    # 提取结果并创建按钮
                    business_items = [record["business_item"]
                                      for record in result]
                    logger.debug(
                        f"Found {len(business_items)} business items for {main_item}")

                    if business_items:
                        buttons = [
                            {
                                "title":  item,
                                # "title": f"{idx + 1}. {item}",
                                "payload": f"/inform_business_item{{\"business_item\":\"{item}\"}}"
                            }
                            for item in business_items
                            # for idx, item in enumerate(business_items)
                        ]
                        message = f"请选择'{main_item}'下的业务办理项："
                    else:
                        message = f"'{main_item}'下没有可用的业务办理项"
                        logger.warning(
                            f"No business items found for {main_item}")

                    # 发送带按钮的回复
                    dispatcher.utter_message(text=message, buttons=buttons)

        except Exception as e:
            logger.error(f"查询业务办理项时出错：{str(e)}")
            dispatcher.utter_message(text="查询业务办理项时发生错误，请稍后再试")

        return []


class AskForScenarioSlotAction(Action):
    """询问用户选择情形的动作"""

    def name(self) -> Text:
        """返回动作名称"""
        return "action_ask_scenario"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        根据选择的业务办理项查询对应的情形

        参数:
            dispatcher: 用于发送消息给用户的工具
            tracker: 当前对话状态跟踪器
            domain: 对话领域配置

        返回:
            空的事件列表
        """
        logger.debug("Starting action_ask_scenario execution")

        # 获取相关slot值
        main_item = tracker.get_slot("main_item")
        business_item = tracker.get_slot("business_item")

        if not business_item:
            dispatcher.utter_message(text="请先选择业务办理项")
            return []

        try:
            # 连接Neo4j数据库
            with GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH) as driver:
                with driver.session() as session:
                    # 查询指定业务办理项下的所有情形
                    result = session.run("""
                        MATCH (:MainItem {name: $main_item})-[:HAS_BUSINESS_ITEM]->
                          (b:BusinessItem {name: $business_item})-[:HAS_SCENARIO]->(s:Scenario)
                        RETURN s.name AS scenario
                        ORDER BY s.name
                    """, main_item=main_item, business_item=business_item)

                    # 提取结果并格式化选项
                    scenarios = [record["scenario"] for record in result]
                    logger.debug(
                        f"Found {len(scenarios)} scenarios for {business_item}")
                    # 无情形
                    if scenarios[0] == "无情形":
                        # if len(scenarios) == 1:
                        return [SlotSet("scenario", "无情形"), SlotSet("current_options", {}), SlotSet("requested_slot", None)]
                    if scenarios:
                        # 转换为字典格式：{序号: 情形名称}
                        scenarios_dict = {str(i+1): record
                                          for i, record in enumerate(scenarios)}
                        logger.debug(f"Scenarios dict: {scenarios_dict}")
                        # 1. 保存到current_options，用于用户通过数字选择
                        slot_event = [
                            SlotSet("current_options", scenarios_dict)]
                        options = "\n".join(
                            [f"{i+1}. {item}" for i, item in enumerate(scenarios)])
                        message = f"请选择'{business_item}'下的情形：\n{options}"
                        dispatcher.utter_message(text=message)
                        return slot_event
                    else:
                        message = f"'{business_item}'下没有可用的情形"
                        logger.warning(
                            f"No scenarios found for {business_item}")
                        dispatcher.utter_message(text=message)
                        return []

        except Exception as e:
            logger.error(f"查询情形时出错：{str(e)}")
            dispatcher.utter_message(text="查询情形时发生错误，请稍后再试")

        return []


class AskForDistrictSlotAction(Action):
    """询问用户选区划的动作"""

    def name(self) -> Text:
        """返回动作名称"""
        return "action_ask_district"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        根据选择的业务办理项查询对应的区划

        参数:
            dispatcher: 用于发送消息给用户的工具
            tracker: 当前对话状态跟踪器
            domain: 对话领域配置

        返回:
            空的事件列表
        """
        logger.debug("Starting action_ask_district execution")

        # 获取相关slot值
        main_item = tracker.get_slot("main_item")
        business_item = tracker.get_slot("business_item")

        if not business_item:
            dispatcher.utter_message(text="请先选择业务办理项")
            return []

        try:
            # 连接Neo4j数据库
            with GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH) as driver:
                with driver.session() as session:
                    # 查询指定业务办理项对应的区划
                    result = session.run("""
                        MATCH (:MainItem {name: $main_item})-[:HAS_BUSINESS_ITEM]->
                          (b:BusinessItem {name: $business_item})-[:LOCATED_IN]->(s:District)
                        RETURN s.name AS district
                        ORDER BY s.name
                    """, main_item=main_item, business_item=business_item)

                    # 提取结果并格式化选项
                    districts = [record["district"] for record in result]
                    logger.debug(
                        f"Found {len(districts)} districts for {business_item}")

                    if districts:
                        options = "\n".join(
                            [f"{i+1}. {item}" for i, item in enumerate(districts)])
                        message = f"请选择'{business_item}'服务的区划：\n{options}"
                    else:
                        message = f"'{business_item}'没有指定服务区划"
                        logger.warning(
                            f"No districts found for {business_item}")

                    dispatcher.utter_message(text=message)

        except Exception as e:
            logger.error(f"查询区划时出错：{str(e)}")
            dispatcher.utter_message(text="查询服务区划时发生错误，请稍后再试")

        return []
