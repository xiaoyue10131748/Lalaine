import pickle
#from cv2 import sort
import pandas as pd

def step_two(src='./data/omitAppsResult_total_with_send_data_tag_negelect_with_purpose.xlsx'):
    data_pur2id_cat = {}
    domn2data_id = {}


    #df = pd.read_excel('./data/omit_test.xlsx')
    df = pd.read_excel(src)
    # df = pd.read_excel('./data/zixiao_omit_test.xlsx')
    for i in range(len(df)):
        if i % 100 == 0:
            print('{}/{}'.format(i, len(df)))
        data = df.iloc[i]['omit_data_list']
        if not isinstance(data, str):
            continue
        data = eval(data)
        if not isinstance(data, set):
            continue
        purpose = df.iloc[i]['purpose']
        suffix = df.iloc[i]['suffix']
        domain = df.iloc[i]['domain']
        if domain in ['apple', 'icloud']:
            continue
        if isinstance(suffix, str):
            domain += '.' + suffix

        id = df.iloc[i]['bundle_id']
        category = df.iloc[i]['app_category']
        if domain not in domn2data_id:
            domn2data_id[domain] = {}
        for d in data:
            if (d, purpose) not in data_pur2id_cat:
                data_pur2id_cat[(d, purpose)] = set()
            data_pur2id_cat[(d, purpose)].add((id, category))
            if d not in domn2data_id[domain]:
                domn2data_id[domain][d] = []
            if id not in domn2data_id[domain][d]:
                domn2data_id[domain][d].append(id)

    domn2data_id = sorted(domn2data_id.items(),
                          key=lambda x: len(sum(x[1].values(), [])), reverse=True)

    with open('./pickles/dp2ic.pkl', 'wb') as f:
        pickle.dump(data_pur2id_cat, f)

    with open('./pickles/domn2data_id.pkl', 'wb') as f:
        pickle.dump(domn2data_id, f)
