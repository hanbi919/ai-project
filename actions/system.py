from typing import Dict, Text, Any, List
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import Restarted, AllSlotsReset, ConversationPaused
import json

class ActionRestart(Action):
    """重置对话状态和槽位的自定义动作"""

    def name(self) -> Text:
        return "action_restart"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        # 根据需求选择合适的事件组合：

        # 1. 完全重启（重置槽位+对话栈）
        return [Restarted()]

        # 2. 仅重置槽位（保留对话栈）
        # return [AllSlotsReset()]

        # 3. 暂停当前对话（可选）
        # return [ConversationPaused()]


class ActionDebugSlots(Action):
    """仅输出当前所有槽位信息"""

    def name(self) -> Text:
        return "action_debug_entities"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        # 获取所有槽位值
        slots = tracker.slots

        # 构建槽位信息输出
        slot_output = "当前槽位状态：\n"
        # for slot_name, slot_value in slots.items():
        #     slot_output += f"{slot_name}: {slot_value}\n"
        # 你可以把它转为字符串输出
        # 获取所有 slot 的值（返回的是一个字典）
        all_slots = tracker.slots

        # 你可以把它转为字符串输出
        slot_info = "\n".join(
            [f"{key}: {value}" for key, value in all_slots.items() if value is not None])


        # slot_values = "\n".join(
        #     [f"\t{s.name}: {s.value}" for s in slots.values()]
        # )
        
        dispatcher.utter_message(text=slot_info)

        return []


class ActionRestartSession(Action):
    def name(self) -> Text:
        return "action_restart_session"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # 发送确认消息
        dispatcher.utter_message(text="好的，我们将重新开始对话。")

        # 返回Restarted事件来重置对话
        return [Restarted()]
    

class ActionRestarted(Action):
    def name(self):
        return 'action_restarted'

    def run(self, dispatcher, tracker, domain):
        return [Restarted()]


class ActionSlotReset(Action):
    def name(self):
        return 'action_slot_reset'

    def run(self, dispatcher, tracker, domain):
        return [AllSlotsReset()]
