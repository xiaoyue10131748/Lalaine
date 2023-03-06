import json
from haralyzer import HarParser, HarPage
import datetime
import os
import xlsxwriter, pandas as pd
import sys
import pickle
from tqdm import tqdm
from  collections import defaultdict
import re


def match_ip(content):
    pattern = re.compile(r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}')
    if pattern.search(str(content)):
        k=pattern.search(str(content)).group()
        if k not in ["00.0.29.3", "00.0.29.30", "073.5.0.0", "074.0.0.0", "075.1.0.0", "1.9.9.80", "1.3.0.0", "13.4.1.17",
                 "14.7.1.18", "16.0.21.2", "2.0.0.0", "2.2.0.2", "3.1.206.0", "4.5.0.0", "4.7.2.0", "4.6.0.0",
                 "4.6.1.0", "4.8.0.0", "3.1.206.0"]:
            return k


def get_ip_from_nework(bunldid,senObject,app_network_data):
    for piece in app_network_data:
        entry = json.loads(piece)
        ip1=match_ip(entry["request"]["postData"])
        if ip1 is not None:
            senObject.ip_list[ip1].add(bunldid)
        '''
        ip2=match_ip(entry["request"]["url"])
        if ip2 is not None:
            senObject.ip_list[ip2].add(bunldid)
        '''




def count_class_name_method_name(className, MethodName, app_frida_data):
    is_exsit = False
    for line in app_frida_data:
        if "className" in line.keys():
            if line["className"] == className and line["MethodName"] == MethodName:
                line["count"] += 1
                app_frida_data[app_frida_data.index(line)] = line
                is_exsit = True
    return is_exsit, app_frida_data


def getBackTrace(index, content):
    startPoint = None
    endPoint = None
    while index < len(content):
        if content[index].strip().startswith("Backtrace:"):
            startPoint = index
            break
        index += 1

    if startPoint != None:
        endPoint = startPoint
        while endPoint < len(content) and content[endPoint] != "\n":
            endPoint += 1
    if startPoint != None and endPoint != None:
        return "".join(content[startPoint:endPoint])
    else:
        return ""




def get_bundle_id(ipa):
    cells = ipa.split("_")
    bundle_id = cells[0]
    return bundle_id


def get_old_bundle_id(ipa):
    if "-" in ipa:
        cells = ipa.split("-")
        appid = cells[-3]
        bundle_id = ipa.split(appid)[0][:-1]
        return bundle_id
    else:
        return ipa.split(".txt")[0]



skip_list=["0","0.0","0.00","0.000","0.0000"]
def parse_frida_output(frida_file, bundle_id,senObject):
    f = open(frida_file, "r", encoding="utf8")
    content = f.readlines()
    # content=content_clean(old_content)
    # print(content)
    f.close()
    index = 0
    index1 = 0

    bundleID_list = []
    sensitve_content_list = []

    app_frida_data = []

    while index < len(content):
        # print(content[index])

        if content[index].startswith("[*] Class Name: "):
            # print(content[index])

            className = content[index].split("[*] Class Name: ")[1].strip()
            try:
                MethodName = content[index + 2].split("[*] Method Name: ")[1].strip()
            except:
                MethodName=""
            returnValue_list = []
            if index + 6 < len(content) and "[-] Return Value: " in content[index + 6]:
                try:
                    returnValue = content[index + 6].strip().split("[-] Return Value: ")[1].strip()
                except:
                    returnValue =""
                returnValue_list.append(returnValue)
            else:
                returnValue = ""

            if className == "CLLocation" and returnValue.startswith("<+"):
                lng = str(int(float(returnValue.split(">")[0].split(",")[1])*1000)/1000)
                lat = str(int(float(returnValue.split(">")[0].split(",")[0].split("<+")[1])*1000) /1000)

                ### -122.42 -> -122.420
                lng_decimal_len=len(lng.split(".")[1])
                lat_decimal_len=len(lng.split(".")[1])
                if lng_decimal_len==2 and lng+"0" in returnValue:
                    lng=lng+"0"
                if lat_decimal_len==2 and lng+"0" in returnValue:
                    lat=lat+"0"

                if lng not in skip_list and lat not in skip_list:
                    returnValue_list.append(lng)
                    returnValue_list.append(lat)
                    senObject.precise_location_list[lng].add(bundle_id)
                    senObject.precise_location_list[lat].add(bundle_id)
                #print("============="+str(senObject.precise_location_list))

                c_lng = str(int(float(returnValue.split(">")[0].split(",")[1])*100 )/100)
                c_lat = str(int(float(returnValue.split(">")[0].split(",")[0].split("<+")[1])*100) /100)

                #13.7 -> 13.70
                c_lng_decimal_len=len(c_lng.split(".")[1])
                c_lat_decimal_len=len(c_lat.split(".")[1])
                if c_lng_decimal_len==1 and lng+"0" in returnValue:
                    c_lng=lng+"0"
                if c_lat_decimal_len==1 and lng+"0" in returnValue:
                    c_lat=lat+"0"

                if c_lng not in skip_list and c_lat not in skip_list:
                    senObject.coarse_location_list[c_lng].add(bundle_id)
                    senObject.coarse_location_list[c_lat].add(bundle_id)
                # print(returnValue)
                # print(lng)
                # print(lat)
            if MethodName=="- advertisingIdentifier":
                if len(returnValue) > 8:
                    senObject.sen_list.add(returnValue)
                    senObject.sen_list.add(returnValue.replace("-", ""))
                    senObject.sen_list.add(returnValue.lower())
                    senObject.sen_list.add(returnValue.lower().replace("-",""))

            index = index + 7
            backtrace = getBackTrace(index, content)
            sensitive_content = className + " " + MethodName + "\n" + returnValue + "\n\n" + backtrace

            bundleID_list.append(bundle_id)
            sensitve_content_list.append(sensitive_content)

            is_exsit, app_frida_data = count_class_name_method_name(className, MethodName, app_frida_data)
            if not is_exsit:
                one_piece_data = {}
                one_piece_data["className"] = className
                one_piece_data["MethodName"] = MethodName
                one_piece_data["ReturnValue"] = returnValue_list
                one_piece_data["Backtrace"] = backtrace
                one_piece_data["count"] = 1
                app_frida_data.append(one_piece_data)

        index += 1


def parse_network_output(bundle_id, network_output_path):
    file_path = network_output_path + bundle_id + ".txt"

    ## not exist
    if not os.path.exists(file_path):
        return []
    f = open(file_path, "r")
    entries = f.readlines()
    f.close()
    return entries



def analyze_one_batch(root,folder,senObject):
    frida_output_path = root + str(folder) + "/frida_output/"
    network_output_path = root + str(folder) + "/network_output/"
    frida_list = os.listdir(frida_output_path)
    for f in frida_list:
        if f == ".DS_Store":
            continue

        frida_file = frida_output_path + f
        if "_" in f:
            bundle_id = get_bundle_id(f)
        else:
            bundle_id = get_old_bundle_id(f)

        parse_frida_output(frida_file, bundle_id,senObject)
        app_network_data = parse_network_output(bundle_id, network_output_path)
        get_ip_from_nework(bundle_id,senObject,app_network_data)

class senInfo:
  def __init__(self, sen_list):
    self.sen_list = sen_list
    self.precise_location_list = defaultdict(set)
    self.coarse_location_list = defaultdict(set)
    self.ip_list = defaultdict(set)
    self.time_zoom=["America/Indiana/Indianapolis","America/Los_Angeles"]


def getSensiveInfo(root):
    sen_list = ["9F0B31E6-980B-4468-9797-0B1F1A8FA56E", "F270BCAF-13C0-4D1C-B91F-6F446E24A380",
            "0F41A05D-B6F8-49FD-AAFF-3D4711371B81", "0000000-0000-0000-0000-000000000000",
            "4CB50870-7A2F-43AE-96E9-390BBECCAFED", "00000000-0000-0000-0000-000000000000",
            "4CB508707A2F43AE96E9390BBECCAFED"]

    sen_list=set(sen_list)
    senObject = senInfo(sen_list)
    for num in tqdm(range(0,91)):
        path=root + str(num)
        if not os.path.exists(path):
            continue
        analyze_one_batch(root,num,senObject)


    target_precise_location = set()
    target_coarse_location = set()

    for i in senObject.precise_location_list:
        if len(senObject.precise_location_list[i]) >= 2:
            #print(i + " : " + str(len(senObject.precise_location_list[i])))
            target_precise_location.add(i)

    #print("============\n")
    for i in senObject.coarse_location_list:
        if len(senObject.coarse_location_list[i]) >= 3:
            #print(i + " : " + str(len(senObject.coarse_location_list[i])))
            target_coarse_location.add(i)

    for k in senObject.ip_list:
        if len(senObject.ip_list[k]) >=5:
            if len(k) <= 8:
                continue
            if k in ["5.19.0.41","00.0.29.3","00.0.29.30","073.5.0.0","074.0.0.0","075.1.0.0","1.9.9.80","1.3.0.0","13.4.1.17","14.7.1.18","16.0.21.2","2.0.0.0","2.2.0.2","3.1.206.0","4.5.0.0","4.7.2.0","4.6.0.0","4.6.1.0","4.8.0.0","3.1.206.0"]:
                continue
            print(k + " : " + str(len(senObject.ip_list[k])))
            senObject.sen_list.add(k)
    return senObject.sen_list,senObject.time_zoom,target_precise_location,target_coarse_location



if __name__ == '__main__':

    computer="xiaoyue"
    root = "/Volumes/Seagate/Privacy_Label/measurement_study/data/"+computer+"_unzip/"
    sen_list,time_zoom,target_precise_location,target_coarse_location=getSensiveInfo(root)
    print(sen_list,target_precise_location,target_coarse_location)

