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


class QueryServiceDetailsAction(Action):
    def name(self) -> Text:
        return "action_query_service_details"

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

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        main_item = tracker.get_slot("main_item")
        business_item = tracker.get_slot("business_item")
        detail_type = tracker.get_slot("detail_type")
        district = tracker.get_slot("area")
        # district = tracker.get_slot("district")
        # 获取所有需要记录的slot值
        slots_to_log = {
            "main_item": tracker.get_slot("main_item"),
            "business_item": tracker.get_slot("business_item"),
            "detail_type": tracker.get_slot("detail_type"),
            "district": tracker.get_slot("area")
            # "district": tracker.get_slot("district")
        }

        # 使用不同日志级别记录信息
        logger.debug(f"当前对话ID: {tracker.sender_id}")  # 调试信息

        for slot_name, slot_value in slots_to_log.items():
            if slot_value is None:
                logger.warning(f"Slot '{slot_name}' 未设置或为None")  # 警告级别
            else:
                logger.info(f"Slot '{slot_name}' = {slot_value}")  # 常规信息

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
                      (d:District {main_item:$main_item,business_item:$business_item})-[:HAS_LOCATION]->(l:Location)-[:HAS_ADDRESS]->(addr:Address)
                WHERE  addr.name CONTAINS $district
                RETURN collect(addr) AS location, d AS district,
                       l.schedule AS schedule, l.phone AS phone,
                       l.fee AS fee, l.deadline AS deadline,l.condition AS condition
                ORDER BY size(location) DESC
                LIMIT 1
            """, main_item=main_item, business_item=business_item, district=district)

            record = result.single()

        driver.close()

        if not record:
            dispatcher.utter_message(text=f"{HIGENT}数据库未找到对应的业务信息")
            return []

        details = ""
        district = record["district"]
        locations = record["location"]
        location_list = []
        import re
        for location in locations:
            loc = location.get("name", "") 
            cleaned_text = re.sub(r"^\(|\)$|'|,$", "", loc)
            location_list.append(cleaned_text)
        numbered_lines = []  # 初始化一个空列表来存储带序号的行
        for idx, line in enumerate(location_list, start=1):  # 从1开始编号
            numbered_lines.append(f"{idx}. {line}")  # 添加到列表中
        location_result = '\n'.join(numbered_lines)
        # if '\n' in location:
        #     lines = location.split('\n')  # 按换行符分割
        #     numbered_lines = []  # 初始化一个空列表来存储带序号的行
        #     for idx, line in enumerate(lines, start=1):  # 从1开始编号
        #         numbered_lines.append(f"{idx}. {line}")  # 添加到列表中
        #     location_result = '\n'.join(numbered_lines)  # 用换行符连接所有行
        # else:
        #     location_result = location  # 重新拼接成字符串
        if detail_type not in ["全部信息", "办理时间", "咨询方式", "是否收费", "承诺办结时限", "办理地点", "受理条件"]:
            detail_type = "全部信息"
        # 处理不同信息类型
        if detail_type == "全部信息":
            details += f"- 办理时间：{record['schedule']}\n"
            details += f"- 咨询方式：{record['phone']}\n"
            details += f"- 是否收费：{record['fee']}\n"
            details += f"- 承诺办结时限：{record['deadline']}个工作日\n"
            details += f"- 受理条件：{record['condition']}\n"
            details += f"- 办理地点：{location_result} \n"
        else:
            if detail_type == "办理时间":
                details += f"- 办理时间：\n{record['schedule']}\n- 办理地点：\n{location_result}"
            elif detail_type == "咨询方式":
                details += f"- 咨询方式：\n{record['phone']}\n- 办理地点：\n{location_result}"
            elif detail_type == "是否收费":
                details += f"- 是否收费：\n{record['fee']}\n- 办理地点：\n{location_result}"
            elif detail_type == "受理条件":
                details += f"- 受理条件：\n{record['condition']}\n- 办理地点：\n{location_result}"
            elif detail_type == "承诺办结时限":
                details += f"- 承诺办结时限：\n{record['deadline']}个工作日\n- 办理地点：\n{location_result}"
            elif detail_type == "办理地点":
                details += f"- 办理地点：\n{location_result}"

        if details:
            # header = f"【{business_item}】业务信息（{district}）"
            # 如果查询的是单个信息类型，不显示header
            if detail_type != "全部信息":
                header = ""
            dispatcher.utter_message(
                text=f"{HIGENT}\n{details}".strip())
        else:
            dispatcher.utter_message(text=f"{HIGENT}未找到对应的详细业务信息")

        return []
