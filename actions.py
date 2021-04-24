import json
import numpy as np
import pandas as pd
import requests

from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from pathlib import Path
from typing import Any, Text, Dict, List
import supplement_functions as sp
import scrapy
from scrapy.crawler import CrawlerProcess
from collection.collection.spiders.info_spider import PkmnSpider 

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

        entities = tracker.latest_message['entities']
        print(entities)
        search = tracker.get_slot('search_param')
        names = []
        for blob in entities[1:]:
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
            names.append(name)
        for name in names:
            name = process.extractOne(name, self.knowledge['name'],scorer=fuzz.token_sort_ratio)[0]
            print(name)
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
                    site_link = f"https://serebii.net/pokedex-swsh/{name}/"
                    # verify = requests.get(site_link)
                    # print(verify.status_code)
                    # if verify.status_code > 400:
                    #     site_link = self.determine_site_link(pokemon_id)
                    # print(site_link)
                    # PkmnSpider().start_requests([site_link])
                    dispatcher.utter_message(text=f"{name}, The {species}. Originates from Generation {generation}.\n{desc}\nLearn more at {site_link}\n\n")
            else:
                match, _ = sp.match2(pokemon_name,self.knowledge['name'])
                dispatcher.utter_message(
                    text=f"I do not recognize the pokemon {name}. Did you mean {match}?")
        return []

class MyKnowledgeBaseAction(ActionQueryKnowledgeBase):
    def __init__(self):
        knowledge_base = InMemoryKnowledgeBase("data/pokemondb.json")
        super().__init__(knowledge_base)
