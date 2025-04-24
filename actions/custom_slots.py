from rasa.shared.core.slots import Slot
from rasa.shared.core.trackers import DialogueStateTracker
from typing import Any, Text, Dict, Optional


class SocialInsuranceSlot(Slot):
    """自定义社保信息校验 Slot"""

    def feature_dimensionality(self) -> int:
        return 1

    def _as_feature(self) -> list:
        return [1.0 if self.value else 0.0]

    @classmethod
    def type_name(cls) -> str:
        return "social_insurance"

    def __init__(self, name, auto_fill=True, **kwargs):
        super().__init__(name, **kwargs)
        self.auto_fill = auto_fill  # 必须调用父类初始化

    def validate(
        self,
        value: Any,
        dispatcher,
        tracker: DialogueStateTracker,
        domain: Dict[Text, Any],
    ) -> Optional[Any]:
        # 校验逻辑
        if not value:
            dispatcher.utter_message(text="请提供社保相关信息！")
            return None

        if "社保" not in value:
            dispatcher.utter_message(text="输入必须包含'社保'关键词！")
            return None

        # 返回标准化后的值（如去除括号等）
        cleaned_value = value.replace("(", "").replace(")", "").strip("'")
        return cleaned_value
