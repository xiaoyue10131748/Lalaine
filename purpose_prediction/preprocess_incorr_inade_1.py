import os
import sys
import pickle
import pandas as pd


def step_one(src='./data/total_test.xlsx'):
    labels = {}
    actuals = {}
    df = pd.read_excel(src)
    for i in range(len(df)):
        if i % 100 == 0:
            print('{}/{}'.format(i, len(df)))
        bundle_id = df.iloc[i]['bundle_id']
        if not isinstance(bundle_id, str):
            print('bundle_id not str:', bundle_id)
            continue
        domain = df.iloc[i]['domain']
        if domain in ['apple', 'icloud']:
            continue

        label = df.iloc[i]['app_true_label']
        if not isinstance(label, str):
            print('label not str:', label)
            continue
        start = label.find('{')
        end = label.find('}')
        label = label[start:end+1]
        label = eval(label)
        if bundle_id not in labels:
            labels[bundle_id] = label

        # actuals
        data = df.iloc[i]['send_data_tag']
        purpose = df.iloc[i]['purpose']
        if not isinstance(data, str):
            continue
        if data == '{nan}':
            continue
        try:
            data = eval(data)
        except:
            print('data not eval:', data)
            sys.exit(1)
        if not isinstance(data, set):
            continue
        if bundle_id not in actuals:
            actuals[bundle_id] = {}
        for d in data:
            if d not in actuals[bundle_id]:
                actuals[bundle_id][d] = []
            if purpose not in actuals[bundle_id][d]:
                actuals[bundle_id][d].append(purpose)

    '''
    label
    'ai.sugar.january' :
     {'health': ['Analytics', 'Product Personalization', 'App Functionality'], 'physical address': ['Analytics', 'Product Personalization', 'App Functionality'], 'product interaction': ['Analytics', 'Product Personalization'], 'sensitive info': ['Analytics', 'Product Personalization', 'App Functionality'], 'email address': ['App Functionality'], 'name': ['App Functionality'], 'phone number': ['App Functionality'], 'other user contact info': ['App Functionality'], 'photos or videos': ['App Functionality'], 'customer support': ['App Functionality'], 'fitness': ['Analytics', 'Product Personalization', 'App Functionality'], 'crash data': ['App Functionality'], 'performance data': ['App Functionality']}
    '''
    for i in actuals:
        if actuals[i]:
            print(i, actuals[i])
            break

    with open('./pickles/labels.pkl', 'wb') as f:
        pickle.dump(labels, f)

    with open('./pickles/actuals.pkl', 'wb') as f:
        pickle.dump(actuals, f)
