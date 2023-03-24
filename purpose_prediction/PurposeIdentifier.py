
#%%
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import missingno as mso
import warnings
import joblib
import re,os
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import random
# import pycaret
# from pycaret.classification import *
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, f1_score
import lightgbm as lgb
gt_x, gt_y = pd.read_csv('./purpose_prediction/data/gt_x.csv'), pd.read_csv('./purpose_prediction/data/gt_y.csv')
total_data = pd.read_csv('./purpose_prediction/data/corpus.csv')

#gt_x, gt_y = pd.read_csv('./data/gt_x.csv',encoding='utf-8'), pd.read_csv('./data/gt_y.csv',encoding='utf-8')
#total_data = pd.read_csv('./data/corpus.csv')

cat_cols  = ['app','subdomain','domain','suffix','API_method','API_class','company']#,,'API_class','API_method','caller_method']#,'caller_class']#,'caller_class']#,'caller_method']#,]#,'company']
num_cols = ['QB_len','SB_len','API_freq']#'edit_distance']#,'API_freq']
bow_cols = ['path','url_arg_keys','QH_keys','QB_keys','SH_keys','SB_keys']
dom_col = 'domain_category'

cols = cat_cols + bow_cols + num_cols + [dom_col]
bow_feat = total_data[bow_cols].fillna('')
dom_feat = total_data[dom_col].fillna('')
def make_corpus(data):
    if len(data.shape)==1:
        return [x for x in data]
    else:
        corpus = []
        for i, feat in enumerate(data.iterrows()):
            feats =[x for x in data.iloc[i]]
            feats = ','.join(feats)
            corpus.append(feats)
        return corpus

def fit_vectorizor(bow_feat,dom_feat):
    beat_vec = CountVectorizer(tokenizer = lambda x: re.split('/|-|,|',x),stop_words='english',min_df = 0.001,max_df=0.9)
    transformer = TfidfTransformer()
    corpus = []
    for i, feat in enumerate(bow_feat.iterrows()):
        feats =[x for x in bow_feat.iloc[i]]
        feats = ','.join(feats)
        corpus.append(feats)
    # print(corpus)
    transformer.fit(beat_vec.fit_transform(corpus))
    dom_vec = CountVectorizer(tokenizer = lambda x: re.split(' |,',x))
    dom_corpus = [x for x in dom_feat]
    dom_vec.fit(dom_corpus)
    return beat_vec, transformer, dom_vec

def metrix(y_true, y_pred):
    print('Accuracy:',accuracy_score(y_true, y_pred))
    print('Micro F1:',f1_score(y_true, y_pred, average='micro'))
    print('Macro F1:',f1_score(y_true, y_pred, average='macro'))
    print('Weighted F1:',f1_score(y_true, y_pred, average='weighted'))

    # print(confusion_matrix(y_true, y_pred))
    print(classification_report(y_true, y_pred))

def train_model(data,label,transformer,beat_vec,dom_vec):
    # print(data.iloc[:3],label.iloc[:3])
    ignore_cols = [x for x in data.columns if x not in cat_cols and x not in bow_cols and x not in num_cols]
    cat_feat = data[cat_cols].astype(str)
    # print(cat_feat)
    cat_feat = cat_feat.apply(LabelEncoder().fit_transform)
    num_feat = data[num_cols].astype(float)
    dcn = pd.concat([cat_feat,num_feat ], axis=1)
    dcn = dcn.fillna(0)
    # label = data['purpose']
    bow_feat = data[bow_cols].fillna('')
    corpus = []
    for i, feat in enumerate(bow_feat.iterrows()):
        feats =[x for x in bow_feat.iloc[i]]
        feats = ','.join(feats)
        corpus.append(feats)
    bow_feat_encoded = transformer.transform(beat_vec.transform(corpus)).toarray()
    # print("Aggregated BOW Features:",len(vectorizer.vocabulary_.keys()))
    dom_feat = data[dom_col]
    dom_feat = dom_feat.fillna('')
    dom_corpus = [x for x in dom_feat]

    dom_feat_encoded = dom_vec.transform(dom_corpus).toarray()
    # print("Domain Category BOW Features:",len(dom_vec.vocabulary_.keys()))
    # print(dcn.shape,bow_feat_encoded.shape, dom_feat_encoded.shape)
    # full_feat = np.concatenate([np.array(dcn),dom_feat_encoded], axis=1)

    full_feat = np.concatenate([np.array(dcn), bow_feat_encoded,dom_feat_encoded], axis=1)
    X,y = full_feat, label
    y = y.replace('Developer Advertising or Marketing',"Developer's Advertising or Marketing")
    print(y.value_counts())
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, stratify=y, shuffle=1, random_state=8)

    lgbmclf = lgb.LGBMClassifier(colsample_bytree=1.0,
                   importance_type='split', learning_rate=0.1, max_depth=10,
                   min_child_samples=20, min_child_weight=0.001, min_split_gain=0.0,
                   n_estimators=50, n_jobs=-1, num_leaves=50, objective=None,
                   random_state=123, reg_alpha=0.0, reg_lambda=0.0, silent=True,
                   subsample=1.0, subsample_for_bin=200000, subsample_freq=0,saved_feature_importance_type=1)
    lgbmclf.fit(X_train, y_train)
    # print("Train--LightGBM")
    # metrix(y_train, lgbmclf.predict(X_train))
    print("Test - LightGBM")
    metrix(y_test, lgbmclf.predict(X_test))
    return lgbmclf


def evaluate_application(clf, filename, output_filename,beat_vec, transformer, dom_vec):
    raw_data = pd.read_csv(filename, delimiter=',',  error_bad_lines=False)
    # print(raw_data['purpose'].isna().index)
    raw_data.dropna(axis=0,subset =["purpose"],inplace=True)
    print(raw_data.shape)
    ignore_cols = [x for x in raw_data.columns if x not in cat_cols and x not in bow_cols and x not in num_cols]

    cat_feat = raw_data[cat_cols].astype(str)
    cat_feat = cat_feat.apply(LabelEncoder().fit_transform)

    num_feat = raw_data[num_cols]#.astype(float)
    for i, item in num_feat.iterrows():
        try:
            item = item.astype(float)
        except:
            # print(i,item,'--')
            # print( num_feat.loc[i,'QB_len'])
            num_feat.loc[i,'QB_len'] = 21
            # print( '+++',num_feat.loc[i],'+++')
    num_feat = num_feat.astype(float)

    dcn = pd.concat([cat_feat,num_feat ], axis=1)
    dcn = dcn.fillna(0)
    bow_feat = raw_data[bow_cols].fillna('')

    corpus = []
    for i, feat in enumerate(bow_feat.iterrows()):
        feats =[x for x in bow_feat.iloc[i]]
        feats = ','.join(feats)
        corpus.append(feats)
    # print(np.sum(feat.toarray(),axis=1))
    bow_feat_encoded = transformer.transform(beat_vec.transform(corpus)).toarray()

    dom_feat = raw_data[dom_col]
    dom_feat = dom_feat.fillna('')
    dom_corpus = [x for x in dom_feat]

    dom_feat_encoded = dom_vec.transform(dom_corpus).toarray()
    print("Feature Dimension: Categorical:{}, Numerical:{}, BOW:{},BOW Encoded:{}, Domain:{},Domain Encoded:{}".format(cat_feat.shape, num_feat.shape, bow_feat.shape,bow_feat_encoded.shape,dom_feat.shape,dom_feat_encoded.shape)    )

    print("Domain Category BOW Features:",len(dom_vec.vocabulary_.keys()))
    # print(dcn.shape,bow_feat_encoded.shape, dom_feat_encoded.shape)
    full_feat = np.concatenate([np.array(dcn), bow_feat_encoded,dom_feat_encoded], axis=1)
    X = full_feat

    print("Application - LightGBM")
    pred = clf.predict(X)
    max_pred_prob = (clf.predict_proba(X).max(axis=1))
    # print("Prob:",pred_prob[:10])
    # print('Num of unique confidence:',np.unique(max_pred_prob))
    # asc_idx =  np.argsort(max_pred_prob)
    print(pred.shape, raw_data.shape)
    raw_data['purpose'] = pred
    raw_data['Confidence'] = max_pred_prob

    print(raw_data.shape)

    writer = pd.ExcelWriter(output_filename, engine='xlsxwriter', engine_kwargs={
                            'options': {'strings_to_urls': False}})
    raw_data.to_excel(writer, index=False)
    writer.save()

    # df.to_csv(dst+'.csv', index=False)
    # df.to_excel(dst+'.xlsx', index=False)
    print('File {} generated'.format(output_filename))

    # out_data = pd.concat([raw_data,p])
    #sns.distplot(max_pred_prob)
    pred = pred.reshape(-1,1)
    # print('++',pred)
    if 'purpose' in raw_data.columns:
        y = raw_data['purpose']
        y = y.replace('Developer Advertising or Marketing',"Developer's Advertising or Marketing")
        for item in y:
            if type(item)==float: print(item)

    np.savetxt(filename.replace('.csv','')+'.lgbmclf.csv',pred,fmt = '%s')
    return bow_feat_encoded.shape[1],dom_feat_encoded.shape[1]

def evaluate_test(clf, filename, output_filename,beat_vec, transformer, dom_vec):
    raw_data = pd.read_csv(filename, delimiter=',',  error_bad_lines=False)
    # print(raw_data['purpose'].isna().index)
    raw_data.dropna(axis=0,subset =["purpose"],inplace=True)
    print(raw_data.shape)
    ignore_cols = [x for x in raw_data.columns if x not in cat_cols and x not in bow_cols and x not in num_cols]

    cat_feat = raw_data[cat_cols].astype(str)
    cat_feat = cat_feat.apply(LabelEncoder().fit_transform)

    num_feat = raw_data[num_cols]#.astype(float)
    for i, item in num_feat.iterrows():
        try:
            item = item.astype(float)
        except:
            # print(i,item,'--')
            # print( num_feat.loc[i,'QB_len'])
            num_feat.loc[i,'QB_len'] = 21
            # print( '+++',num_feat.loc[i],'+++')
    num_feat = num_feat.astype(float)

    dcn = pd.concat([cat_feat,num_feat ], axis=1)
    dcn = dcn.fillna(0)
    bow_feat = raw_data[bow_cols].fillna('')

    corpus = []
    for i, feat in enumerate(bow_feat.iterrows()):
        feats =[x for x in bow_feat.iloc[i]]
        feats = ','.join(feats)
        corpus.append(feats)
    # print(np.sum(feat.toarray(),axis=1))
    bow_feat_encoded = transformer.transform(beat_vec.transform(corpus)).toarray()

    dom_feat = raw_data[dom_col]
    dom_feat = dom_feat.fillna('')
    dom_corpus = [x for x in dom_feat]

    dom_feat_encoded = dom_vec.transform(dom_corpus).toarray()
    print("Feature Dimension: Categorical:{}, Numerical:{}, BOW:{},BOW Encoded:{}, Domain:{},Domain Encoded:{}".format(cat_feat.shape, num_feat.shape, bow_feat.shape,bow_feat_encoded.shape,dom_feat.shape,dom_feat_encoded.shape)    )

    print("Domain Category BOW Features:",len(dom_vec.vocabulary_.keys()))
    # print(dcn.shape,bow_feat_encoded.shape, dom_feat_encoded.shape)
    full_feat = np.concatenate([np.array(dcn), bow_feat_encoded,dom_feat_encoded], axis=1)
    X = full_feat

    print("Application - LightGBM")
    pred = clf.predict(X)
    max_pred_prob = (clf.predict_proba(X).max(axis=1))
    # print("Prob:",pred_prob[:10])
    # print('Num of unique confidence:',np.unique(max_pred_prob))
    # asc_idx =  np.argsort(max_pred_prob)

    raw_data['Prediction'] = pred
    raw_data['Confidence'] = max_pred_prob
    raw_data.to_csv(output_filename)
    print(raw_data.shape)
    # out_data = pd.concat([raw_data,p])
    #sns.distplot(max_pred_prob)
    pred = pred.reshape(-1,1)
    # print('++',pred)
    if 'purpose' in raw_data.columns:
        y = raw_data['purpose']
        y = y.replace('Developer Advertising or Marketing',"Developer's Advertising or Marketing")
        for item in y:
            if type(item)==float: print(item)
        metrix(y, pred)

    np.savetxt(filename.replace('.csv','')+'.lgbmclf.csv',pred,fmt = '%s')
    return bow_feat_encoded.shape[1],dom_feat_encoded.shape[1]





def load_model(data,label,transformer,beat_vec,dom_vec,model_path):
    if not os.path.exists(model_path):
        # retrained and saved the model
        # print(data.iloc[:3],label.iloc[:3])
        ignore_cols = [x for x in data.columns if x not in cat_cols and x not in bow_cols and x not in num_cols]
        cat_feat = data[cat_cols].astype(str)
        # print(cat_feat)
        cat_feat = cat_feat.apply(LabelEncoder().fit_transform)
        num_feat = data[num_cols].astype(float)
        dcn = pd.concat([cat_feat,num_feat ], axis=1)
        dcn = dcn.fillna(0)
        # label = data['purpose']
        bow_feat = data[bow_cols].fillna('')
        corpus = []
        for i, feat in enumerate(bow_feat.iterrows()):
            feats =[x for x in bow_feat.iloc[i]]
            feats = ','.join(feats)
            corpus.append(feats)
        bow_feat_encoded = transformer.transform(beat_vec.transform(corpus)).toarray()
        # print("Aggregated BOW Features:",len(vectorizer.vocabulary_.keys()))
        dom_feat = data[dom_col]
        dom_feat = dom_feat.fillna('')
        dom_corpus = [x for x in dom_feat]

        dom_feat_encoded = dom_vec.transform(dom_corpus).toarray()
        # print("Domain Category BOW Features:",len(dom_vec.vocabulary_.keys()))
        # print(dcn.shape,bow_feat_encoded.shape, dom_feat_encoded.shape)
        # full_feat = np.concatenate([np.array(dcn),dom_feat_encoded], axis=1)

        full_feat = np.concatenate([np.array(dcn), bow_feat_encoded,dom_feat_encoded], axis=1)
        X,y = full_feat, label
        y = y.replace('Developer Advertising or Marketing',"Developer's Advertising or Marketing")
        print(y.value_counts())
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, stratify=y, shuffle=1, random_state=8)

        lgbmclf = lgb.LGBMClassifier(colsample_bytree=1.0,
                       importance_type='split', learning_rate=0.1, max_depth=10,
                       min_child_samples=20, min_child_weight=0.001, min_split_gain=0.0,
                       n_estimators=50, n_jobs=-1, num_leaves=50, objective=None,
                       random_state=123, reg_alpha=0.0, reg_lambda=0.0, silent=True,
                       subsample=1.0, subsample_for_bin=200000, subsample_freq=0,saved_feature_importance_type=1)
        lgbmclf.fit(X_train, y_train)
        # print("Train--LightGBM")
        # metrix(y_train, lgbmclf.predict(X_train))
        print("Test - LightGBM")
        metrix(y_test, lgbmclf.predict(X_test))
        joblib.dump(lgbmclf, model_path)

    else:
        # load model
        lgbmclf = joblib.load(model_path)
    return lgbmclf




def predict_purpose(src='./data/test.csv', dst='./data/test_results.csv', retrain=False):
    beat_vec, transformer, dom_vec = fit_vectorizor(bow_feat,dom_feat)
    if retrain:
        lgbmclf= train_model(gt_x,gt_y,transformer,beat_vec,dom_vec)
        bow_feat_dim, dom_feat_dim = evaluate_application(lgbmclf, src, dst,beat_vec, transformer, dom_vec)
    else:
        print(os.getcwd())
        model_path="./purpose_prediction/model/lgb.pkl"
        lgbmclf= load_model(gt_x,gt_y,transformer,beat_vec,dom_vec,model_path)
        bow_feat_dim, dom_feat_dim = evaluate_application(lgbmclf, src, dst,beat_vec, transformer, dom_vec)


#predict_purpose()