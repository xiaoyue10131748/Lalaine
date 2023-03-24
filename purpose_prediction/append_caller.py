import pandas as pd
from utils.utils_traffic import ParsedURL, ParsedHeader, ParsedBody
from utils.utils_frida import *
from tqdm import tqdm
import pickle
import os
import collections
import copy
#Bundle ID
#1. From firda output: (data -> extract API -> closest caller)
#2. From network traffic: (API data -> domain)


def get_method_name2caller(caller: tuple) -> dict:
    ret = {}
    for i in range(len(caller)):
        if i % 2 == 0:
            class_name = caller[i]
        else:
            method_name = caller[i]
            if class_name not in ret:
                ret[class_name] = [method_name]
            else:
                ret[class_name].append(method_name)
    return ret


def complete_API_list_total(src: str = '/Volumes/Seagate/Privacy_Label/revision/jiale/traffic/total_with_send_data_tag.xlsx'):
    df = pd.read_excel(src, engine='openpyxl')
    returnData_to_api_map={}
    returnData_to_api_map["5B30BC06-9017-4FA0-8A77-3FB3FFBE3D7D"]="- advertisingIdentifier"
    returnData_to_api_map["0F41A05D-B6F8-49FD-AAFF-3D4711371B81"]="- advertisingIdentifier"
    returnData_to_api_map["4CB50870-7A2F-43AE-96E9-390BBECCAFED"] = "- advertisingIdentifier"
    returnData_to_api_map["F270BCAF-13C0-4D1C-B91F-6F446E24A380"] = "- advertisingIdentifier"
    returnData_to_api_map["86E081D1-7B0E-482F-9FF6-0F5059F60B15"] = "- advertisingIdentifier"
    returnData_to_api_map["9F0B31E6-980B-4468-9797-0B1F1A8FA56E"] = "- advertisingIdentifier"
    returnData_to_api_map["366B7AFE-D8E8-4781-858D-0597D0D589BE"] = "- advertisingIdentifier"

    returnData_to_api_map["-86.523"]="- coordinate"
    returnData_to_api_map["39.173"]=" - coordinate"
    returnData_to_api_map["39.17"] = "- coordinate"
    returnData_to_api_map["-86.48"]=" - coordinate"
    returnData_to_api_map["39.13"] = "- coordinate"
    returnData_to_api_map["-86.523"]=" - coordinate"
    returnData_to_api_map["39.173"] = "- coordinate"
    returnData_to_api_map["39.15"]=" - coordinate"
    returnData_to_api_map["-86.52"] = "- coordinate"
    returnData_to_api_map["-86.492"]=" - coordinate"
    returnData_to_api_map["39.154"] = "- coordinate"
    returnData_to_api_map["-86.480"] = " - coordinate"
    returnData_to_api_map["39.136"] = "- coordinate"
    returnData_to_api_map["-86.49"] = " - coordinate"
    returnData_to_api_map["-86.492"] = "- coordinate"
    returnData_to_api_map["39.154"] = " - coordinate"
    returnData_to_api_map["-86.514"] = "- coordinate"
    returnData_to_api_map["39.139"] = " - coordinate"
    returnData_to_api_map["-86.51"] = "- coordinate"
    returnData_to_api_map["37.132"] = " - coordinate"
    returnData_to_api_map["37.13"] = "- coordinate"
    returnData_to_api_map["39.171"] = "- coordinate"
    returnData_to_api_map["-86.526"] = "- coordinate"
    returnData_to_api_map["-122.258"] = "- coordinate"
    returnData_to_api_map["37.552"] = "- coordinate"
    returnData_to_api_map["-122.258"] = "- coordinate"
    returnData_to_api_map["37.552"] = "- coordinate"
    returnData_to_api_map["39.911"] = "- coordinate"


    returnData_to_api_map["battery_level"]="- batteryLevel"
    returnData_to_api_map["batteryLevel"] = "- batteryLevel"
    returnData_to_api_map["device_battery_level"] = "- batteryLevel"
    returnData_to_api_map["device_battery_percent"] = "- batteryLevel"
    returnData_to_api_map["Battery Info"] = "- batteryLevel"
    returnData_to_api_map["battery_status"] = "- batteryState"
    returnData_to_api_map["battery.remaining.start"] = "- batteryState"
    returnData_to_api_map["battery.charging.start"] = "- batteryState"
    returnData_to_api_map["batteryStatus"] = "- batteryState"
    returnData_to_api_map["device_battery_charging"] = "- batteryState"
    returnData_to_api_map["battery"] = "- batteryState"
    returnData_to_api_map["battery_state"] = "- batteryState"
    returnData_to_api_map["battery_saver_enabled"] = "- batteryState"
    returnData_to_api_map["batteryInfo"] = "- batteryState"
    returnData_to_api_map["batteryState"] = "- batteryState"
    returnData_to_api_map["batterySaverEnabled"] = "- batteryState"
    returnData_to_api_map["cur_battery"] = "- batteryState"
    returnData_to_api_map["IsBatteryCharging"] = "- batteryState"

    returnData_to_api_map["149.161.155.113"]="getifaddrs"
    returnData_to_api_map["149.161.248.108"] = "getifaddrs"
    returnData_to_api_map["149.161.155.113"] = "getifaddrs"
    returnData_to_api_map["149.161.248.108"] = "getifaddrs"
    returnData_to_api_map["192.168.0.131"] = "getifaddrs"
    returnData_to_api_map["192.168.0.132"] = "getifaddrs"
    returnData_to_api_map["192.168.0.131"] = "getifaddrs"
    returnData_to_api_map["192.168.0.131"] = "getifaddrs"
    returnData_to_api_map["192.168.0.132"] = "getifaddrs"
    returnData_to_api_map["149.160.147.75"] = "getifaddrs"
    returnData_to_api_map["149.161.156.25"] = "getifaddrs"
    returnData_to_api_map["149.161.156.25"] = "getifaddrs"
    returnData_to_api_map["149.161.156.25"] = "getifaddrs"
    returnData_to_api_map["149.161.221.52"] = "getifaddrs"
    returnData_to_api_map["149.161.221.52"] = "getifaddrs"
    returnData_to_api_map["149.161.138.58"] = "getifaddrs"
    returnData_to_api_map["149.160.179.16"] = "getifaddrs"
    returnData_to_api_map["149.160.137.251"] = "getifaddrs"
    returnData_to_api_map["149.160.137.251"] = "getifaddrs"
    returnData_to_api_map["149.160.164.92"] = "getifaddrs"
    returnData_to_api_map["149.160.137.251"] = "getifaddrs"
    returnData_to_api_map["192.168.0.211"] = "getifaddrs"
    returnData_to_api_map["192.168.0.187"] = "getifaddrs"
    returnData_to_api_map["192.168.0.189"] = "getifaddrs"
    returnData_to_api_map["192.168.0.212"] = "getifaddrs"
    returnData_to_api_map["192.168.0.211"] = "getifaddrs"
    returnData_to_api_map["15.12.0.12"] = "getifaddrs"
    returnData_to_api_map["15.12.15.15"] = "getifaddrs"
    returnData_to_api_map["192.168.0.112"] = "getifaddrs"
    returnData_to_api_map["192.168.0.212"] = "getifaddrs"

    returnData_to_api_map["email"]="- emailAddresses"
    returnData_to_api_map["emailAddress"] = "- emailAddresses"
    returnData_to_api_map["user_email"] = "- emailAddresses"
    returnData_to_api_map["workEmailAddressChangeRequired"] = "- emailAddresses"
    returnData_to_api_map["emails"] = "- emailAddresses"
    returnData_to_api_map["ShowContactEmailAddresses"] = "- emailAddresses"
    returnData_to_api_map["emailid"] = "- emailAddresses"
    returnData_to_api_map["Email_Address"] = "- emailAddresses"
    returnData_to_api_map["userEmail"] = "- emailAddresses"

    returnData_to_api_map["PhoneNumber"] = "- phoneNumbers"
    returnData_to_api_map["Phone_Number"] = "- phoneNumbers"
    returnData_to_api_map["screenAfterPhoneNumberInput"] = "- phoneNumbers"
    returnData_to_api_map["telephoneNumber"] = "- phoneNumbers"
    returnData_to_api_map["postalCode"] = "- postalAddresses"
    returnData_to_api_map["postal_code"]= "- postalAddresses"

    returnData_to_api_map["birthday"] = "- birthday"
    returnData_to_api_map["birthdate"] = "- birthday"
    returnData_to_api_map["dateOfBirth"] = "- birthday"
    returnData_to_api_map["Date_of_Birth"] = "- birthday"
    returnData_to_api_map["lp_yearofbirth"] = "- birthday"
    returnData_to_api_map["yearofbirth"] = "- birthday"
    returnData_to_api_map["yearofbirth_time"] = "- birthday"
    returnData_to_api_map["BirthYear"] = "- birthday"

    for i in tqdm(range(len(df))):
        data = df.loc[i, "return_list"]
        if data in returnData_to_api_map.keys():
            API = returnData_to_api_map[data]
            df.loc[i, "API_list"] = API
    return df







#dic={bundle_id:{api:[domain]}}
def get_dataAPI_domain(df) -> dict:
    dic={}
    for i in tqdm(range(len(df))):
        api= df.loc[i, 'API_list']
        if not isinstance(api, str):
            continue
        api=api.strip()
        url = df.loc[i, 'url_list']
        bundle_id = df.loc[i, 'bundle_id_list']
        domain = ParsedURL(url).domain
        if domain =="apple" or domain =="icloud":
            continue
        if bundle_id not in dic:
            domain_list=set()
            domain_list.add(domain)
            nest_dic = {}
            nest_dic[api]=domain_list
            dic[bundle_id]=nest_dic
        else:
            nest_dic=dic[bundle_id]
            if api in nest_dic.keys():
                nest_dic[api].add(domain)
            else:
                domain_list = set()
                domain_list.add(domain)
                nest_dic[api] = domain_list

    count_single_domain=0
    count_all_API_domain=0
    for bundle_id in dic.keys():
        for API in dic[bundle_id]:
            domain_list = dic[bundle_id][API]
            if len(domain_list)==1:
                count_single_domain+=1
            count_all_API_domain+=1
    print('single API to Single domain {}/{}'.format(count_single_domain, count_all_API_domain))
    with open('./traffic/dataAPI_domain_dic.pickle', 'wb') as in_data:
        pickle.dump(dic, in_data, pickle.HIGHEST_PROTOCOL)
    return dic


def get_dataAPI_caller(dirs: list =['./frida/jiale', './frida/feifan']) -> dict:
    dirs.append("/Volumes/Seagate/Privacy_Label/measurement_study/data/appMakerResult")
    dirs.append("/Volumes/Seagate/Privacy_Label/measurement_study/data/JialePost")
    dirs.append("/Volumes/Seagate/Privacy_Label/measurement_study/data/luyixing_unzip")
    dirs.append("/Volumes/Seagate/Privacy_Label/measurement_study/data/minPost")
    dirs.append("/Volumes/Seagate/Privacy_Label/measurement_study/data/xiaoyue_unzip")
    dirs.append("/Volumes/Seagate/Privacy_Label/measurement_study/data/zixiaoResult")
    api_caller_dics=get_all_api_caller_dic_from_dirs(dirs)

    count_single_caller = 0
    count_all_API_caller = 0
    for bundle_id in api_caller_dics.keys():
        for API in api_caller_dics[bundle_id]:
            caller_list = api_caller_dics[bundle_id][API]
            if len(caller_list) == 1:
                count_single_caller += 1
            count_all_API_caller += 1
    print('single API to Single domain {}/{}'.format(count_single_caller, count_all_API_caller))
    with open('./traffic/dataAPI_caller_dic.pickle', 'wb') as in_data:
        pickle.dump(api_caller_dics, in_data, pickle.HIGHEST_PROTOCOL)
    return api_caller_dics


def unique_match(dataAPI_domain_dic:dict,dataAPI_caller_dic:dict):
    total=0
    unique_match=0
    unique_mapping_dic={}
    for bundle_id in dataAPI_caller_dic.keys():
        if bundle_id in dataAPI_domain_dic.keys():
            for API in dataAPI_caller_dic[bundle_id].keys():
                if API in dataAPI_domain_dic[bundle_id].keys():
                    caller_list=dataAPI_caller_dic[bundle_id][API]
                    domain_list=dataAPI_domain_dic[bundle_id][API]
                    if len(caller_list)==1 and len(domain_list)==1:
                        #print(API + " => "+ str(caller_list) + " <=> " + str(domain_list))
                        unique_match+=1

                        function_call=str(list(caller_list)[0][0])+":"+str(list(caller_list)[0][1])
                        print(bundle_id + " => " + list(domain_list)[0] + " => " + function_call + " => "+ API)
                        unique_mapping_dic[function_call]=list(domain_list)[0]
                    total+=1

    #print('single caller to Single domain {}/{}'.format(unique_match, total))
    return unique_mapping_dic



def calltrace_to_domain(unique_mapping_dic:dict,dataAPI_domain_dic:dict,dataAPI_caller_dic:dict):
    total = 0
    unique_match = 0
    multi_match=0
    leftover_dic=collections.defaultdict(int)
    API_caller={}


    for bundle_id in dataAPI_caller_dic.keys():
        if bundle_id in dataAPI_domain_dic.keys():
            for API in dataAPI_caller_dic[bundle_id].keys():
                if API in dataAPI_domain_dic[bundle_id].keys():
                    caller_list = dataAPI_caller_dic[bundle_id][API]
                    domain_list = dataAPI_domain_dic[bundle_id][API]
                    if len(caller_list) == 1 and len(domain_list) == 1:
                        unique_match+=1
                        total += 1
                    else:
                        for caller in caller_list:
                            for domain in domain_list:
                                function_call=str(caller[0])+":"+str(caller[1])
                                if function_call in unique_mapping_dic.keys() and domain == unique_mapping_dic[function_call]:
                                    multi_match+=1
                                else:
                                    leftover_dic[function_call+"="+domain]+=1
                                    API_caller[function_call+"="+domain]=API
                            total += 1


    df=pd.DataFrame(leftover_dic.items())
    df2=pd.DataFrame(API_caller.items())
    print('single caller to Single domain {}/{}'.format(unique_match, total))
    print('multi caller to Single domain {}/{}'.format(multi_match, total))
    #df.to_excel("./traffic/multi_caller_domain_mapping.xlsx")
    df2.to_excel("./traffic/API_caller_mapping.xlsx")

#{API:{caller:domain}}
def generate_mapping_from_unique_and_multiple_mapping(dataAPI_domain_dic:dict,dataAPI_caller_dic:dict, multi_manual_src="/Volumes/Seagate/Privacy_Label/revision/jiale/traffic/multi_caller_domain_mapping_yue.xlsx"):
    #source 1 from unique ooe to one mapping
    api_caller_domain_map=collections.defaultdict(dict)
    for bundle_id in dataAPI_caller_dic.keys():
        if bundle_id in dataAPI_domain_dic.keys():
            for API in dataAPI_caller_dic[bundle_id].keys():
                if API in dataAPI_domain_dic[bundle_id].keys():
                    caller_list = dataAPI_caller_dic[bundle_id][API]
                    domain_list = dataAPI_domain_dic[bundle_id][API]
                    if len(caller_list) == 1 and len(domain_list) == 1:
                        function_call = str(list(caller_list)[0][0]) + ":" + str(list(caller_list)[0][1])
                        api_caller_domain_map[API][function_call]=domain_list

    #source 2 manully multi-to-multi mapping
    df = pd.read_excel(multi_manual_src, engine='openpyxl')
    for i in tqdm(range(len(df))):
        api= df.loc[i, 'API']
        caller = df.loc[i, 'caller']
        domain = df.loc[i, 'manually_label_domain']
        if str(domain)=="nan":
            continue
        if caller in api_caller_domain_map[api]:
            api_caller_domain_map[api][caller].add(domain)
        else:
            api_caller_domain_map[api][caller]={domain}
    return api_caller_domain_map



def count_API_Caller_Domain_Mapping(api_caller_domain_map:dict):
    num=0
    for api in api_caller_domain_map.keys():
        for caller in api_caller_domain_map[api]:
            for d in api_caller_domain_map[api][caller]:
                print(api + " , " + caller + " , " + d)
                num+=1

    print("the total mapping record is {}".format(str(num)))


def calculate_coverage(api_caller_domain_map):
    dirs=[]
    dirs.append("/Volumes/Seagate/Privacy_Label/measurement_study/data/appMakerResult")
    dirs.append("/Volumes/Seagate/Privacy_Label/measurement_study/data/JialePost")
    dirs.append("/Volumes/Seagate/Privacy_Label/measurement_study/data/luyixing_unzip")
    dirs.append("/Volumes/Seagate/Privacy_Label/measurement_study/data/minPost")
    dirs.append("/Volumes/Seagate/Privacy_Label/measurement_study/data/xiaoyue_unzip")
    dirs.append("/Volumes/Seagate/Privacy_Label/measurement_study/data/zixiaoResult")


    total=0
    matched=0
    for dir in dirs:
        for sub_dir in os.listdir(dir):
            # print(sub_dir)
            if not os.path.isdir(os.path.join(dir, sub_dir)):
                continue
            # frida_dir = dir + sub_dir + '/frida_output/'
            frida_dir = os.path.join(dir, sub_dir, 'frida_output')
            # print(frida_dir)
            if not os.path.exists(frida_dir):
                continue
            for file in os.listdir(frida_dir):
                if file.startswith('.'):
                    continue
                api_caller_dic=count_API_caller_from_file(os.path.join(frida_dir, file))
                for api in api_caller_dic:
                    for caller in api_caller_dic[api]:
                        function_call = str(list(caller)[0]) + ":" + str(list(caller)[1])
                        if function_call in api_caller_domain_map[api].keys():
                            matched+=1
                        else:
                            print(function_call)
                        total+=1
    print("the coverage of call trace mapping is {}".format(str(matched/total)))


def calculate_coverage_calltrace_to_domain(api_caller_domain_map,unique_mapping_dic:dict,dataAPI_domain_dic:dict,dataAPI_caller_dic:dict,c_mapping_file):
    total = 0
    unique_match = 0
    unique_total = 0
    left_match=0
    multi_match=0
    leftover_dic=collections.defaultdict(int)
    API_caller={}

    c_mapping_API=[]
    c_mapping_caller = []
    c_mapping_domain = []
    note=[]

    for bundle_id in dataAPI_caller_dic.keys():
        if bundle_id in dataAPI_domain_dic.keys():
            for API in dataAPI_caller_dic[bundle_id].keys():
                if API in dataAPI_domain_dic[bundle_id].keys():
                    caller_list = dataAPI_caller_dic[bundle_id][API]
                    domain_list = dataAPI_domain_dic[bundle_id][API]
                    caller_list_copy = copy.deepcopy(caller_list)
                    domain_list_copy = copy.deepcopy(domain_list)
                    if len(caller_list) == 1 and len(domain_list) == 1:
                        unique_match+=1
                        total += 1
                        unique_total+=1
                        c_mapping_API.append(API)
                        c_mapping_caller.append(list(caller_list)[0])
                        c_mapping_domain.append(list(domain_list)[0])
                        note.append("1.unique")

                    else:
                        for caller in caller_list:
                            for domain in domain_list:
                                function_call=str(caller[0])+":"+str(caller[1])
                                if function_call in unique_mapping_dic.keys() and domain == unique_mapping_dic[function_call]:
                                    multi_match+=1
                                    c_mapping_API.append(API)
                                    c_mapping_caller.append(caller)
                                    c_mapping_domain.append(domain)
                                    note.append("2.use unique")
                                    caller_list_copy.remove(caller)
                                    if domain in domain_list_copy:
                                        domain_list_copy.remove(domain)
                                elif function_call in api_caller_domain_map[API].keys():
                                    multi_match += 1
                                    for domain in  api_caller_domain_map[API][function_call]:
                                        c_mapping_API.append(API)
                                        c_mapping_caller.append(caller)
                                        c_mapping_domain.append(domain)
                                        note.append("3.use multi")


                                total += 1
                        if len(caller_list_copy) == 1 and len(domain_list_copy) == 1:
                            print(str(caller_list_copy)  + " => " +str(domain_list_copy))
                            left_match+=1
                            multi_match += 1

                            c_mapping_API.append(API)
                            c_mapping_caller.append(list(caller_list_copy)[0])
                            c_mapping_domain.append(list(domain_list_copy)[0])
                            note.append("4.left unique")

                        unique_total+=1
    print('single caller to Single domain {}/{}'.format(unique_match, unique_total))
    print('multi caller to Single domain {}/{}'.format(multi_match, total))
    print('left match is {}'.format(left_match))
    print('total coverage is {}'.format((unique_match+multi_match+left_match)/(total+unique_match)))
    c_map={}
    c_map["c_mapping_API"]=c_mapping_API
    c_map["c_mapping_caller"] = c_mapping_caller
    c_map["c_mapping_domain"] = c_mapping_domain
    c_map["note"] = note
    df=pd.DataFrame(c_map)
    df.to_excel(c_mapping_file)


if __name__ == "__main__":

    if not os.path.exists('./traffic/dataAPI_domain_dic.pickle'):
        df = complete_API_list_total()
        dataAPI_domain_dic=get_dataAPI_domain(df)
        dataAPI_caller_dic=get_dataAPI_caller()
    else:
        with open('./traffic/dataAPI_domain_dic.pickle', 'rb') as out_data:
            dataAPI_domain_dic = pickle.load(out_data)
        with open('./traffic/dataAPI_caller_dic.pickle', 'rb') as out_data:
            dataAPI_caller_dic = pickle.load(out_data)

    unique_mapping_dic=unique_match(dataAPI_domain_dic,dataAPI_caller_dic)
    calltrace_to_domain(unique_mapping_dic, dataAPI_domain_dic, dataAPI_caller_dic)
    api_caller_domain_map=generate_mapping_from_unique_and_multiple_mapping(dataAPI_domain_dic,dataAPI_caller_dic)
    count_API_Caller_Domain_Mapping(api_caller_domain_map)
    #calculate_coverage(api_caller_domain_map)

    #caculate coverage and build mapping
    c_mapping_file="./traffic/cMapping.xlsx"
    calculate_coverage_calltrace_to_domain(api_caller_domain_map,unique_mapping_dic,dataAPI_domain_dic,dataAPI_caller_dic,c_mapping_file)




