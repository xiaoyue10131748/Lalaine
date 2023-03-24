from tqdm import tqdm
from purpose_prediction.append_caller import *
import pickle
import os
import collections
import csv

def get_API_caller_to_domain():
    with open('./purpose_prediction/traffic/dataAPI_domain_dic.pickle', 'rb') as out_data:
        dataAPI_domain_dic = pickle.load(out_data)
    with open('./purpose_prediction/traffic/dataAPI_caller_dic.pickle', 'rb') as out_data:
        dataAPI_caller_dic = pickle.load(out_data)

    #unique_mapping_dic=unique_match(dataAPI_domain_dic,dataAPI_caller_dic)
    #calltrace_to_domain(unique_mapping_dic, dataAPI_domain_dic, dataAPI_caller_dic)
    return generate_mapping_from_unique_and_multiple_mapping(dataAPI_domain_dic,dataAPI_caller_dic)

API_TO_API_MAP={"- horizontalAccuracy":"- coordinate"}


def editDistDP(str1, str2, m, n):
    # Create a table to store results of subproblems
    dp = [[0 for x in range(n + 1)] for x in range(m + 1)]

    # Fill d[][] in bottom up manner
    for i in range(m + 1):
        for j in range(n + 1):

            # If first string is empty, only option is to
            # insert all characters of second string
            if i == 0:
                dp[i][j] = j  # Min. operations = j

            # If second string is empty, only option is to
            # remove all characters of second string
            elif j == 0:
                dp[i][j] = i  # Min. operations = i

            # If last characters are same, ignore last char
            # and recur for remaining string
            elif str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]

            # If last character are different, consider all
            # possibilities and find minimum
            else:
                dp[i][j] = 1 + min(dp[i][j - 1],  # Insert
                                   dp[i - 1][j],  # Remove
                                   dp[i - 1][j - 1])  # Replace

    return dp[m][n]


def split_caller_class_method(caller:str):
    class_name=caller.split(":")[0].strip()
    method_name=caller.split(class_name+":")[1].strip()
    return class_name,method_name


def calculate_edit_distance(appCompany,callerCompany):
    #if appCompany=="Beijing Xiachufang Technology Co.,Ltd.":
        #print(111)
    appCompany_list=str(appCompany).split(" ")
    MIN=100000
    for app in appCompany_list:
        edit_dis=editDistDP(str(app).lower(), str(callerCompany).lower(), len(str(app)), len(str(callerCompany)))
        if edit_dis < MIN:
            MIN=edit_dis
    return MIN


def convert_to_utf8(path: str = '/Volumes/Seagate/Privacy_Label/revision/jiale/train_test_qin/total_test0605.csv'):
    with open(path, 'r', encoding='utf-8', errors='ignore') as infile, open('/Volumes/Seagate/Privacy_Label/revision/jiale/train_test_qin/total_test0605_utf8.csv', 'w') as outfile:
        inputs = csv.reader(infile)
        output = csv.writer(outfile)
        for index, row in enumerate(inputs):
            # Create file with no header
            if index == 0:
                continue
            output.writerow(row)




#def complete_API_list_train(src: str = '/Volumes/Seagate/Privacy_Label/revision/jiale/train_test_qin/total_test0605utf8.csv'):
def complete_API_list_train(df):

    api_caller_domain_map = get_API_caller_to_domain()

    matched_caller_list=[]
    caller_class_list=[]
    caller_method_list=[]
    edit_distance_list=[]
    reason_list=[]
    for i in tqdm(range(len(df))):
        API = df.loc[i, "API_method"]
        domain = df.loc[i, "domain"]
        if API in API_TO_API_MAP.keys():
            API=API_TO_API_MAP[API]
        matched_caller=""
        class_name=""
        method_name=""
        appCompany=str(df.loc[i, "company"])

        for caller in api_caller_domain_map[API].keys():
            domain_list=api_caller_domain_map[API][caller]
            if domain in domain_list:
                print(API + " => " + caller + " => " + domain)
                matched_caller =caller
                break
        matched_caller_list.append(matched_caller)
        if matched_caller!="":
            class_name,method_name=split_caller_class_method(matched_caller)
        caller_class_list.append(class_name)
        caller_method_list.append(method_name)
        if appCompany=="nan":
            appCompany=""
        edit_distance_list.append(calculate_edit_distance(appCompany,domain))
        reason_list.append("model")
    df["edit_distance"] = edit_distance_list
    df["caller_class"] = caller_class_list
    df["caller_method"] = caller_method_list

    return df



if __name__ == "__main__":
    pass
    #convert_to_utf8()
    #complete_API_list_train()
