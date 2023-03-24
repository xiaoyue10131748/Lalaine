import os
import sys
import pickle
import json
import numpy as np
import pandas as pd
from purpose_prediction.utils_purpose import Purpose


def step_three(dst="'./data/problems.xlsx'"):
    labels = pickle.load(open('./pickles/labels.pkl', 'rb'))
    actuals = pickle.load(open('./pickles/actuals.pkl', 'rb'))
    dp2ic = pickle.load(open('./pickles/dp2ic.pkl', 'rb'))
    id2info = json.load(open('./data/id2info.json', 'r'))
    # labels = pickle.load(open('./pickles/labels2.pkl', 'rb'))
    # actuals = pickle.load(open('./pickles/actuals2.pkl', 'rb'))
    # dp2ic = pickle.load(open('./pickles/dp2ic2.pkl', 'rb'))


    # {id: {(data, purpose): 'omit' or 'inadequate' or 'incorrect'}, ...}
    problems = {}
    df = pd.DataFrame(columns=['id', 'category', 'data',
                      'purpose', 'actual', 'type'])
    for d, p in dp2ic:
        for id, cat in dp2ic[(d, p)]:
            if id not in problems:
                problems[id] = {}
            if id not in id2info:
                category = 'No Record'
            else:
                category = id2info[id]['category']
            if (d, p) not in problems[id]:
                problems[id][(d, p)] = 'omit'
                df = pd.concat([df, pd.DataFrame([[id, category,  d, '', p, 'omit']], columns=[
                               'id', 'category', 'data', 'purpose', 'actual', 'type'])])

    for id in actuals:
        if id not in problems:
            problems[id] = {}
        if id not in labels:
            print('id not in labels:', id)
            continue
        if id not in id2info:
            category = 'No Record'
        else:
            category = id2info[id]['category']
        for d in actuals[id]:
            if d.lower() not in labels[id]:
                # omit
                continue
            actual_purpose = Purpose(actuals[id][d])
            label_purpose = Purpose(labels[id][d.lower()])
            actual_minus_label = actual_purpose - label_purpose
            if not actual_minus_label.is_empty():
                label_minus_actual = label_purpose - actual_purpose
                if not label_minus_actual.is_empty():
                    # incorrect
                    for real in actual_minus_label.get_purpose_list():
                        problems[id][(d, real)] = 'incorrect'
                        for false in label_minus_actual.get_purpose_list():
                            df = pd.concat([df, pd.DataFrame([[id, category, d, false, real, 'incorrect']], columns=[
                                           'id', 'category', 'data', 'purpose', 'actual', 'type'])])
                else:
                    # inadequate
                    for purpose in actual_minus_label.get_purpose_list():
                        problems[id][(d, purpose)] = 'inadequate'
                        df = pd.concat([df, pd.DataFrame([[id, category, d,  '', purpose, 'inadequate']], columns=[
                                       'id', 'category', 'data', 'purpose', 'actual', 'type'])])

    # sort df
    df = df.sort_values(by=['id', 'type', 'data', 'purpose', 'actual'])
    df.to_excel(dst, index=False)

    #print('problems:', len(problems))
    with open('./pickles/problems.pkl', 'wb') as f:
        pickle.dump(problems, f)
