import json
import numpy as np
import pandas as pd
import requests
from pathlib import Path
from typing import Any, Text, Dict, List


from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.knowledge_base.storage import InMemoryKnowledgeBase
from rasa_sdk.knowledge_base.actions import ActionQueryKnowledgeBase


# class ActionCheckExistence(Action):
#     knowledge = Path("data/pokenames.txt").read_text().split("\n")

#     def name(self) -> Text:
#         return "action_check_existence"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         for blob in tracker.latest_message['entities']:
#             print(tracker.latest_message)
#             if blob['entity'] == 'pokemon_name':
#                 name = blob['value']
#                 if name in self.knowledge:
#                     dispatcher.utter_message(text=f"Yes, {name} is a pokemon.")
#                 else:
#                     dispatcher.utter_message(
#                         text=f"I do not recognize {name}, are you sure it is correctly spelled?")
#         return []

class ActionGetInfo(Action):
    with open("data/pokemondb.json") as f:
            db = json.load(f)

    table = pd.DataFrame(db['pokemon'])
    knowledge = table.set_index('id')

    def name(self) -> Text:
        return "action_get_info"

    @staticmethod
    def determine_site_link(pkmn_id):
        dex = ['-sm','-xy','-bw','-dp','-rs','-dp','']
        pkmn_id = str(pkmn_id)
        if len(pkmn_id) < 3:
            pkmn_id = ('0'*(3-len(pkmn_id))+pkmn_id)

        for gen in dex:
            sitelink = f"https://serebii.net/pokedex{gen}/{pkmn_id}.shtml"
            verify = requests.get(sitelink)
            if verify.status_code < 400:
                    break
        return sitelink

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        for blob in tracker.latest_message['entities']:
            print(tracker.latest_message['entities'])
            if blob['entity'] == 'search_param':
                search = blob['value']

            if blob['entity'] == 'pokemon_name':
                name_capture = blob['value'].split()
                pokemon_name = blob['value'].replace(" ","").lower()
                if len(name_capture) > 1:
                    name = ""
                    name_parts = [parts.capitalize() for parts in name_capture]
                    for x in name_parts:
                        name+=(" "+x)
                    name = name.strip()
                else:
                    name = blob['value'].capitalize()

        if np.any(self.knowledge['name'] == name):
            if search == 'type':
                p_type = list(self.knowledge[search][self.knowledge['name']==name])[0]
                if len(p_type) > 1:
                    dispatcher.utter_message(text=f"{name} is {p_type[0]}/{p_type[1]} type.")
                else:
                    dispatcher.utter_message(text=f"{name} is {p_type[0]} type.")
            if search == "description":
                desc = list(self.knowledge[search][self.knowledge['name']==name])[0]
                species = list(self.knowledge['species'][self.knowledge['name']==name])[0]
                generation = list(self.knowledge['gen'][self.knowledge['name']==name])[0]
                pokemon_id = self.knowledge[self.knowledge['name']==name].index[0]
                # hyperlink_format = '<a href="{link}">{text}</a>'
                # link_text = hyperlink_format.format
                # site_link = link_text(link=f"https://serebii.net/pokedex-swsh/{pokemon_name}/",text='here')
                site_link = f"https://serebii.net/pokedex-swsh/{pokemon_name}/"
                verify = requests.get(site_link)
                if verify.status_code > 400:
                    site_link = self.determine_site_link(pokemon_id)
                
                dispatcher.utter_message(text=f"{name}, The {species}. Originates from Generation {generation}.\n{desc}\nLearn more at {site_link}")
        else:
            dispatcher.utter_message(
                text=f"I do not recognize {name}, are you sure it is correctly spelled?")
        return []

class MyKnowledgeBaseAction(ActionQueryKnowledgeBase):
    def __init__(self):
        knowledge_base = InMemoryKnowledgeBase("data/pokemondb.json")
        super().__init__(knowledge_base)
