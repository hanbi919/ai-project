from typing import Text, List, Dict, Any, Union
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
import logging
from .const import HIGENT

# 配置日志格式（带文件名和行号）
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]',
    level=logging.DEBUG
)
# 初始化日志记录器
logger = logging.getLogger(__name__)

# 主表单验证类


class MainServiceForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_disability_service_form"  # 表单的唯一标识

    # @staticmethod
    async def required_slots(
        self,
        domain_slots: List[Text],  # 来自domain.yml的必需槽位
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Text]:
        # 在这里根据条件返回需要的槽位列表
        value = tracker.get_slot("business_item")
        if value:
            return ["main_item", "scenario"]

        return ["main_item", "business_item", "scenario"]

    # def slot_mappings(self) ->  Dict[Text, Union[Dict, List[Dict]]]:
    #     return {
    #         "main_item": [
    #             self.from_entity(entity="main_item"),
    #             self.from_text()  # 捕获用户原始输入（数字或文本）
    #         ],
    #         "business_item": [
    #             self.from_entity(entity="business_item"),
    #             self.from_text()  # 捕获用户原始输入（数字或文本）
    #         ],
    #         "scenario": [
    #             # self.from_entity(entity="scenario"),
    #             self.from_intent(intent="select_option",
    #                              entity="scenario"),
    #             self.from_text()  # 捕获用户原始输入（数字或文本）
    #         ]
    #     }

    def submit(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict]:
        # 表单提交后的逻辑（可选）
        dispatcher.utter_message("感谢您的选择！")
        return []

    async def validate_main_item(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        # 发现重置了主项，就更新办理子项
        if tracker.get_slot("main_item") != value:
            return {"main_item": value, "business_item": None, "scenario": None}
        # return {"main_item": value.strip()}

    async def validate_business_item(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if tracker.get_slot("business_item") != value:
            return {"business_item": value, "scenario": None}
        return {"business_item": value.strip()}

    async def validate_scenario(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """验证用户输入的数字并映射到实际值"""
        # 定义数字选项映射
        pass

        # options = tracker.get_slot("scenarios_options") or {}
        # # 检查输入是否为有效数字
        # if value.strip() in options:
        #     selected_value = options[value.strip()]
        #     return {"scenario": selected_value}  # 存储映射后的值
        # else:
        #     dispatcher.utter_message("请输入有效的数字（如1、2、3）！")
        #     return {"scenario": None}  # 验证失败
