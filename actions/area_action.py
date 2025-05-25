from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from neo4j import GraphDatabase
from .sys_logger import logger

class QueryAreaAction(Action):
    def name(self) -> Text:
        return "action_area"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        area = tracker.latest_message.get("text")
        return [SlotSet("area",area)]
