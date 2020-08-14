
## happy path
* greet
  - utter_greet
* mood_great
  - utter_happy
* query_knowledge_base
  - action_query_knowledge_base

## sad path 1
* greet
  - utter_greet
* mood_unhappy
  - utter_cheer_up
  - utter_did_that_help
* affirm
  - utter_happy

## sad path 2
* greet
  - utter_greet
* mood_unhappy
  - utter_cheer_up
  - utter_did_that_help
* deny
  - utter_goodbye

## say goodbye
* goodbye
  - utter_goodbye

## bot challenge
* bot_challenge
  - utter_iamabot

## bot challenge
* greet
  - utter_greet
* bot_challenge
  - utter_iamabot
* demand_joke
  - utter_joke
* get_info
  - action_get_info
* query_knowledge_base
  - action_query_knowledge_base

## faq
* faq
  - respond_faq

## pokemon_faq
* query_knowledge_base
  - action_query_knowledge_base

## interactive_story_1
* greet
    - utter_greet
* query_knowledge_base
  - action_query_knowledge_base

## interactive_story_2
* get_info{"pokemon_name": "lugia", "search_param": "type"}
    - slot{"pokemon_name": "lugia", "search_param": "type"}
    - action_get_info
* get_info{"pokemon_name": "zekrom", "search_param": "type"}
    - slot{"pokemon_name": "zekrom", "search_param": "type"}
    - action_get_info
* get_info{"pokemon_name": "pikachu", "search_param": "type"}
    - slot{"pokemon_name": "pikachu", "search_param": "type"}
    - action_get_info
