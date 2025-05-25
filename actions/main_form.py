from typing import Text, List, Dict, Any, Union
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from .sys_logger import logger
from rasa_sdk.events import SlotSet, AllSlotsReset

class MainServiceForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_disability_service_form"  # 表单的唯一标识

    # def required_slots(tracker: Tracker) -> List[Text]:
    #     return ["main_item", "business_item", "scenario"]
    async def required_slots(
        self,
        domain_slots: List[Text],  # 来自domain.yml的必需槽位
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Text]:
        # 在这里根据条件返回需要的槽位列表
        # value = tracker.get_slot("business_item")
        # if value:
        #     return ["main_item", "scenario"]

        return ["main_item", "business_item", "scenario"]

    def slot_mappings(self) ->  Dict[Text, Union[Dict, List[Dict]]]:
        return {
            "main_item": [
                # self.from_entity(entity="main_item"),
                self.from_text()  # 捕获用户原始输入（数字或文本）
            ],
            # "business_item": [
            #     self.from_entity(entity="business_item"),
            #     self.from_text()  # 捕获用户原始输入（数字或文本）
            # ],
            # "scenario": [
            #     # self.from_entity(entity="scenario"),
            #     self.from_intent(intent="select_option",
            #                      entity="scenario"),
            #     self.from_text()  # 捕获用户原始输入（数字或文本）
            # ]
        }

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
        """当 main_item 被修改时，清空 business_item 和 name"""
        current_main_item = tracker.get_slot("main_item")
        old_value = tracker.slots.get("main_item")  # 获取未被实体更新的原始值
        # 只有当值真正改变时才重置（避免初始化时的误清空）
        if current_main_item != value:
            return {
                "main_item": value,       # 更新当前值
                "business_item": None,    # 清空子项目
                "scenario": None              # 清空名称
            }
        return {"main_item": value}  # 值未改变时仅更新当前 slot
        

    async def validate_business_item(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """当 business_item 被修改时，清空 name"""
        current_business_item = tracker.get_slot("business_item")

        if current_business_item != value:
            return {
                "business_item": value,  # 更新当前值
                "scenario": None             # 清空名称
            }
        return {"business_item": value}

    async def validate_scenario(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """验证用户输入的数字并映射到实际值"""
        # 定义数字选项映射
        # pass
        return {"scenario": value.strip()}
         
