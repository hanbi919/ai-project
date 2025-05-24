from typing import Dict, Text, Any, List
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.graph import ExecutionContext, GraphComponent
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.constants import ENTITIES


@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.ENTITY_EXTRACTOR],
    is_trainable=False,
)
class OverlappingEntitiesRemover(GraphComponent):
    """自定义组件用于去除重叠实体"""

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> GraphComponent:
        """创建组件实例"""
        return cls(config, model_storage, resource)

    def __init__(
        self,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
    ) -> None:
        """初始化组件"""
        self._config = config
        self._model_storage = model_storage
        self._resource = resource

    def process(self, messages: List[Message]) -> List[Message]:
        """处理消息，去除重叠实体"""
        for message in messages:
            entities = message.get(ENTITIES, [])
            if not entities:
                continue

            # 按起始位置排序
            sorted_entities = sorted(entities, key=lambda x: x["start"])

            filtered_entities = []
            prev_entity = None
            # print(f"current entity:{sorted_entities}")
            for entity in sorted_entities:
                if prev_entity is None:
                    prev_entity = entity
                    filtered_entities.append(entity)
                    continue

                # 检查是否重叠
                if self._is_overlapping(prev_entity, entity):
                    # 选择更长的实体或根据其他策略选择
                    prev_entity = self._select_entity(prev_entity, entity)
                    # 替换最后一个实体
                    filtered_entities[-1] = prev_entity
                else:
                    filtered_entities.append(entity)
                    prev_entity = entity

            message.set(ENTITIES, filtered_entities)

        return messages

    def _is_overlapping(self, entity1: Dict, entity2: Dict) -> bool:
        """检查两个实体是否位置重叠"""
        return not (entity1["end"] <= entity2["start"] or entity2["end"] <= entity1["start"])

    def _select_entity(self, entity1: Dict, entity2: Dict) -> Dict:
        """选择要保留的实体（默认保留更长的实体）"""
        len1 = entity1["end"] - entity1["start"]
        len2 = entity2["end"] - entity2["start"]

        # 也可以根据实体类型、置信度等做更复杂的决策
        return entity1 if len1 >= len2 else entity2
