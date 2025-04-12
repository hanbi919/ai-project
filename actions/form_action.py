from typing import Dict, Text, Any, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import logging
from rasa_sdk.knowledge_base.actions import ActionQueryKnowledgeBase

# 初始化logger
logger = logging.getLogger(__name__)

class ValidateCityForm(Action):
    def name(self) -> Text:
        return "validate_main_item_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 获取用户输入
        if tracker.get_slot("main_item"):
            return []
        # city_slot = tracker.get_slot("main_item")
        # logger.debug(f"main item is {city_slot}")
        # latest_message = tracker.latest_message
        # logger.debug(f"latest_message item is {latest_message}")
        # return [SlotSet("main_item", "残疾人证办理")]
