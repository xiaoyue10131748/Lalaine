import pickle,os

import json
from tqdm import tqdm
import pandas as pd
from  collections import defaultdict
from analyzeUtils.getSenInfo import match_ip
import ast

def get_privacy_label_data():
    privacy_label = []
    privacy_label.append("Name")
    privacy_label.append("Email Address")
    privacy_label.append("Phone Number")
    privacy_label.append("Physical Address")
    privacy_label.append("Other User Contact Info")
    privacy_label.append("Health")
    privacy_label.append("Fitness")
    privacy_label.append("Payment Info")
    privacy_label.append("Credit Info")
    privacy_label.append("Other Financial Info")
    privacy_label.append("Precise Location")
    privacy_label.append("Coarse Location")
    privacy_label.append("Sensitive Info")
    privacy_label.append("Contacts")
    privacy_label.append("Emails or Text Messages")
    privacy_label.append("Photos or Videos")
    privacy_label.append("Audio Data")
    privacy_label.append("Gameplay Content")
    privacy_label.append("Customer Support")
    privacy_label.append("Other User Content")
    privacy_label.append("Browsing History")
    privacy_label.append("Search History")
    privacy_label.append("User ID")
    privacy_label.append("Device ID")
    privacy_label.append("Purchase History")
    privacy_label.append("Product Interaction")
    privacy_label.append("Advertising Data")
    privacy_label.append("Other Usage Data")
    privacy_label.append("Crash Data")
    privacy_label.append("Performance Data")
    privacy_label.append("Other Diagnostic Data")
    privacy_label.append("Other Data Types")

    return privacy_label




def get_data_to_Tag_mapping(df):
    data_to_Tag=defaultdict(set)
    API_list=df["API_list"].tolist()
    return_list =df["return_list"].tolist()
    matchRule=df["matchRule"].tolist()
    keyData=df["keyData"].tolist()
    for index, api in enumerate(API_list):
        returnValue = return_list[index]
        if api =="- advertisingIdentifier":
            tag="Device ID"
            data_to_Tag[returnValue].add(tag)

        if api =="- identifierForVendor":
            data_to_Tag[returnValue].add("Device ID")
            data_to_Tag[returnValue].add("User ID")

        if api == "- coordinate":
            if len(str(returnValue).split(".")[1])==3:
                data_to_Tag[returnValue].add("Precise Location")

            else:
                data_to_Tag[returnValue].add("Precise Location")
                data_to_Tag[returnValue].add("Coarse Location")

        if  match_ip(returnValue):
            data_to_Tag[returnValue].add("Device ID")
            data_to_Tag[returnValue].add("Precise Location")
            data_to_Tag[returnValue].add("Coarse Location")
            data_to_Tag[returnValue].add("Other Diagnostic Data")
        if api =="timezoom":
            data_to_Tag[returnValue].add("Precise Location")
            data_to_Tag[returnValue].add("Coarse Location")
        if matchRule[index] =="mappingByKey":
            label_list=keyData[index]
            for l in  ast.literal_eval(label_list):
                data_to_Tag[returnValue].add(l)

    ###load manully label tag given data
    manully_label="../manully/data_to_tag.xlsx"
    if os.path.exists(manully_label):
        df=pd.read_excel(manully_label)
        value=df["manually_set"].tolist()
        tag=df["tag"].tolist()
        for i,v in enumerate(value):
            ## coarse location data if precise location is declare, we ignore
            if "," in str(tag[i]):
                s_t=tag[i].split(",")
                for k in s_t:
                    data_to_Tag[v].add(k.strip())
            else:
                data_to_Tag[v].add(tag[i])
    else:
        ##creat one
        manually_set=set()
        for index, api in enumerate(API_list):
            if api == "- identifierForVendor":
                continue
            value = return_list[index]
            if value not in data_to_Tag.keys():
                manually_set.add(value)

        dic={}
        dic["manually_set"]=list(manually_set)
        manully_df=pd.DataFrame(dic)
        manully_df.to_excel("./data/data_to_tag_omit.xlsx")

    return data_to_Tag


def load(file):
    dbfile = open(file, 'rb')
    df = pickle.load(dbfile)
    dbfile.close()
    return df

def merge_privacy_label_data(label_json):
    merge_data = {}
    for c in tqdm(label_json):
        row = json.loads(c)
        privacy_label = {}
        merge_data[row["bundleid"]] = privacy_label
        for key in row.keys():
            if key in ["Data Linked to You", "Data Not Linked to You", "Data Used to Track You",
                       "Data Not Collected", "url"]:
                privacy_label[key] = row[key]
    return merge_data



def get_privacy_label_data_purpose(privacy_label):
    privacy_label_data_purpose = defaultdict(list)
    for key in privacy_label.keys():
        if key in ["Data Linked to You", "Data Not Linked to You", "Data Used to Track You", "Data Not Collected"]:
            for tag_purpose in privacy_label[key]:
                for category in privacy_label[key][tag_purpose]:
                    if isinstance(category, dict):
                        for use in category:
                            for data_itself in category[use]:
                                    privacy_label_data_purpose[data_itself.lower()].append(tag_purpose)
                    else:
                        privacy_label_data_purpose[category.lower()].append("Data Used to Track You")
    return privacy_label_data_purpose




def is_in(tag,privacy_label_data_purpose,label_set):
    flag=False
    for t in tag:
        if t not in label_set:
            print(t)
            f = open("error.log", "a+")
            f.write(str(t)+'\n')
            f.close()
            flag=True
        if str(t).lower() in privacy_label_data_purpose.keys():
            flag=True

    return flag



def append_privacy_Label_omit(total_file,out_putfile):
    #tofile = "../result/totalv2.pickle"
    #df=load(tofile)
    privacy_label = "./data/20220402_privacy_label_parse.json"
    df=pd.read_excel(total_file)
    data_to_Tag=get_data_to_Tag_mapping(df)



    f = open(privacy_label)
    label_json = f.readlines()
    f.close()
    merge_data=merge_privacy_label_data(label_json)
    label_set=get_privacy_label_data()
    omit_rows = []

    app_url_list=[]
    app_true_label=[]
    omit_data_list=[]

    not_exist_bundle=set()
    for index,row in df.iterrows():
        bundleID=row["bundle_id_list"]
        returnVaule=row["return_list"]
        tag=data_to_Tag[returnVaule]
        if len(tag)==0:
            continue
        if bundleID not in merge_data.keys():
            not_exist_bundle.add(bundleID)
            continue

        privacy_label = merge_data[bundleID]
        url = privacy_label["url"]
        privacy_label_data_purpose = get_privacy_label_data_purpose(privacy_label)
        if not is_in(tag,privacy_label_data_purpose,label_set):
            newrow = row
            omit_rows.append(newrow.values)
            app_url_list.append(url)
            app_true_label.append(privacy_label_data_purpose)
            omit_data_list.append(tag)

    omit_df = pd.DataFrame(omit_rows, columns=df.columns).reset_index()
    omit_df["app_url_list"]=app_url_list
    omit_df["app_true_label"] = app_true_label
    omit_df["omit_data_list"] = omit_data_list


    norepeat_omit_df = omit_df.drop_duplicates(subset=['bundle_id_list'], keep='first')
    norepeat_df = df.drop_duplicates(subset=['bundle_id_list'], keep='first')
    print(len(norepeat_omit_df))
    print(len(norepeat_df))
    print(len(norepeat_omit_df)/len(norepeat_df))

    #omit_df.to_excel()
    writer = pd.ExcelWriter(out_putfile, engine='xlsxwriter', options={'strings_to_urls': False})
    omit_df.to_excel(writer)
    writer.close()
    #print(not_exist_bundle)




if __name__ == '__main__':
    #total_file="../result/zixiaoResult_total.xlsx"
    #omitFile="../result/zixiaoResult_omitDisclosure.xlsx"
    '''
    total_file="../result/appMakerResult_appmaker_total.xlsx"
    omitFile="../result/appMaker_omitDisclosure.xlsx"
    '''

    total_file="../result/omitAppsResult_total.xlsx"
    omitFile="../result/omitAppsResult_total_with_send_data_tag_negelect.xlsx"


    append_privacy_Label_omit(total_file, omitFile,privacy_label)
    '''
    for b in not_exist_bundle:
        f = open("non_exist_bundle.log", "a+")
        f.write(str(b) + '\n')
        f.close()
    '''




