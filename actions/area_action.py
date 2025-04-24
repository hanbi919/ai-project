from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from neo4j import GraphDatabase
import logging

class QueryAreaAction(Action):
    def name(self) -> Text:
        return "action_area"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        main_item = tracker.get_intent_of_latest_message("text")
        return [SlotSet("area",main_item)]
