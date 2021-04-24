import numpy as np
import pandas as pd

def match2(sent_word,lexicon):
    sent_word = sent_word.replace(" ","").lower()
    match_score = 0
    best_score = 0
    best_matches = {}
    for word in lexicon:
        current_word = word.replace(" ","").lower()
        # Phase 1
        if sent_word == current_word:
            match_score = 100
            best_match = word
            best_matches.update({word:match_score})
            break
        # Phase 2
        if sent_word[0] == current_word[0]: 
            match_score+=(1.5/len(current_word))

        if sent_word[-3:] == current_word[-3:]:
            match_score+=(3/len(current_word))

        if sent_word[-2:] == current_word[-2:]:
            match_score+=(3/len(current_word))

        if (len(sent_word)+1 == len(current_word)) or (len(sent_word)-1 == len(current_word)):
            match_score+=(1/len(current_word))
            
        for letter in list(sent_word):
            if letter in current_word:
                match_score+=(1/len(sent_word))/2

        for i in range(min(len(sent_word),len(current_word))):
            if sent_word[i] == current_word[i]:
                match_score+=(1/len(sent_word))

        for i in range(min(len(sent_word),len(current_word))):
            if sent_word[i:i+2] in current_word:
                match_score+=(2/len(sent_word))

        for i in range(min(len(sent_word),len(current_word))):
            if sent_word[i:i+3] in current_word:
                match_score+=(3/len(sent_word))

        best_matches.update({word:match_score})
        if match_score > best_score:
            best_score = match_score
            best_match = word
        match_score = 0
    top_matches = pd.DataFrame(best_matches.values(),best_matches.keys()).sort_values(0,ascending=False).head(3)
    top_matches[0] = top_matches[0]*100/top_matches[0].max()
    return best_match, top_matches