import json
from haralyzer import HarParser, HarPage
import datetime
import os
import xlsxwriter, pandas as pd
import sys
import pickle
from analyzeUtils.getSenInfo import *

from tqdm import tqdm
from  collections import defaultdict

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


def getDintionary(index, content):
    index += 2
    startPoint = index
    endPoint = startPoint
    while endPoint < len(content) and content[endPoint] != "\n":
        endPoint += 1
    return "".join(content[startPoint:endPoint])


def writeToExcel(df, path):
    workbook = xlsxwriter.Workbook(path)
    worksheet = workbook.add_worksheet()

    # Set up some formats to use.
    bold = workbook.add_format({'bold': True})
    italic = workbook.add_format({'italic': True})
    red = workbook.add_format({'color': 'red'})

    '''
    df = pd.DataFrame({
        'numCol': [1, 50, 327],
        'plainText': ['plain', 'text', 'column'],
        'richText': [
            ['This is ', bold, 'bold'],
            ['This is ', italic, 'italic'],
            ['This is ', red, 'red']
        ]
    }) 
    '''

    headRows = 1

    for colNum in range(len(df.columns)):
        xlColCont = df[df.columns[colNum]].tolist()
        worksheet.write_string(0, colNum, str(df.columns[colNum]), bold)
        for rowNum in range(len(xlColCont)):

            if df.columns[colNum] == 'bundleID_list':
                worksheet.write_string(rowNum + headRows, colNum, xlColCont[rowNum])
            elif df.columns[colNum] == 'sensitve_content_list':
                try:
                    worksheet.write_rich_string(rowNum + headRows, colNum, *xlColCont[rowNum])
                except:
                    #print(*xlColCont[rowNum])
                    pass

    workbook.close()


def count_class_name_method_name(className, MethodName, app_frida_data):
    is_exsit = False
    for line in app_frida_data:
        if "className" in line.keys():
            if line["className"] == className and line["MethodName"] == MethodName:
                line["count"] += 1
                app_frida_data[app_frida_data.index(line)] = line
                is_exsit = True
    return is_exsit, app_frida_data

skip_list=["0","0.0","0.00","0.000","0.0000"]
def parse_frida_output(frida_file, bundle_id, anlyze_output_path,sen_list):
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


            if MethodName=="- advertisingIdentifier":
                if len(returnValue) > 8:
                    sen_list.add(returnValue)
                    sen_list.add(returnValue.replace("-", ""))
                    sen_list.add(returnValue.lower())
                    sen_list.add(returnValue.lower().replace("-",""))

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

    while index1 < len(content):
        if "In buffer" in content[index1]:
            # print(content[index1])
            # print(index1)
            decrypt_body = getDintionary(index1, content)
            # print(decrypt_body)
            if len(decrypt_body) != 0:
                bundleID_list.append(bundle_id)
                sensitve_content_list.append(decrypt_body)

                one_piece__dic_data = {}
                one_piece__dic_data["decrypt_body"] = decrypt_body
                app_frida_data.append(one_piece__dic_data)

        index1 += 1

    dic = {}
    dic["bundleID_list"] = bundleID_list
    dic["sensitve_content_list"] = sensitve_content_list
    df = pd.DataFrame(dic)
    directory = anlyze_output_path + "parse_frida_result/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    tofile = directory + bundle_id + ".xlsx"
    # df.to_excel(tofile)

    # print(len(bundleID_list))
    # print(len(sensitve_content_list))
    #writeToExcel(df, tofile)
    #for item in app_frida_data:
        #print(item)
    return app_frida_data


def parse_network_output(bundle_id, network_output_path):
    file_path = network_output_path + bundle_id + ".txt"

    ## not exist
    if not os.path.exists(file_path):
        return []
    f = open(file_path, "r")
    entries = f.readlines()
    f.close()
    return entries


def writeToMapping(df, path):
    workbook = xlsxwriter.Workbook(path)
    worksheet = workbook.add_worksheet()

    # Set up some formats to use.
    bold = workbook.add_format({'bold': True})
    italic = workbook.add_format({'italic': True})
    red = workbook.add_format({'color': 'red'})
    headRows = 1
    for colNum in range(len(df.columns)):
        xlColCont = df[df.columns[colNum]].tolist()
        #print(xlColCont)
        worksheet.write_string(0, colNum, str(df.columns[colNum]), bold)
        for rowNum in range(len(xlColCont)):
            if df.columns[colNum] == 'bundleID_list':
                worksheet.write_string(rowNum + headRows, colNum, xlColCont[rowNum])
            # elif df.columns[colNum] == 'requestBody_list' or  df.columns[colNum] == 'responseBody_lists':
            # worksheet.write_rich_string(rowNum + headRows, colNum, xlColCont[rowNum])
            else:
                worksheet.write_string(rowNum + headRows, colNum, xlColCont[rowNum])
    workbook.close()




def match(bundle_id, app_frida_data, app_network_data, anlyze_output_path,sen_list, target_precise_location, target_coarse_location,time_zoom):
    bundle_id_list = []
    className_list = []
    API_list = []
    return_list = []
    invoke_list = []

    url_list = []
    request_header_list = []
    requestBody_list = []
    response_header_list = []
    responseBody_list = []
    note_list = []

    for firda_data in app_frida_data:
        ## case 1: extractly match
        if "ReturnValue" in firda_data.keys():
            returnValue_list = firda_data["ReturnValue"]

            for returnValue in returnValue_list:
                if returnValue in skip_list:
                    print("================="+returnValue)
                for piece in app_network_data:
                    entry = json.loads(piece)
                    if returnValue in str(entry["request"]["postData"]):
                        #print(entry["request"]["postData"])
                        bundle_id_list.append(bundle_id)
                        className_list.append(firda_data["className"])
                        API_list.append(firda_data["MethodName"])
                        return_list.append(returnValue)
                        invoke_list.append(str(firda_data["count"]))

                        url_list.append(entry["request"]["url"])
                        request_header_list.append(str(entry["request"]["headers"]))
                        requestBody_list.append(str(entry["request"]["postData"]))
                        try:
                            response_header_list.append(str(entry["response"]["headers"]))
                        except:
                            response_header_list.append("")
                        try:
                            responseBody_list.append(str(entry["response"]["content"]))
                        except:
                            responseBody_list.append("")
                        note_list.append("postData")



                    elif returnValue in str(entry["request"]["url"]):
                        #print(entry["request"]["url"])
                        bundle_id_list.append(bundle_id)
                        className_list.append(firda_data["className"])
                        API_list.append(firda_data["MethodName"])
                        return_list.append(returnValue)
                        invoke_list.append(str(firda_data["count"]))

                        url_list.append(entry["request"]["url"])
                        request_header_list.append(str(entry["request"]["headers"]))
                        requestBody_list.append(str(entry["request"]["postData"]))
                        try:
                            response_header_list.append(str(entry["response"]["headers"]))
                        except:
                            response_header_list.append("")
                        try:
                            responseBody_list.append(str(entry["response"]["content"]))
                        except:
                            responseBody_list.append("")
                        note_list.append("url")

                    elif returnValue in str(entry["request"]["headers"]):
                        #print(entry["request"]["headers"])
                        bundle_id_list.append(bundle_id)
                        className_list.append(firda_data["className"])
                        API_list.append(firda_data["MethodName"])
                        return_list.append(returnValue)
                        invoke_list.append(str(firda_data["count"]))

                        url_list.append(entry["request"]["url"])
                        request_header_list.append(str(entry["request"]["headers"]))
                        requestBody_list.append(str(entry["request"]["postData"]))
                        try:
                            response_header_list.append(str(entry["response"]["headers"]))
                        except:
                            response_header_list.append("")
                        try:
                            responseBody_list.append(str(entry["response"]["content"]))
                        except:
                            responseBody_list.append("")
                        note_list.append("header")

        ## case 2: match encrpyted body
        if "decrypt_body" in firda_data.keys():
            bundle_id_list.append(bundle_id)
            className_list.append("")
            API_list.append("")
            value = ""
            for sen in sen_list:
                if sen in str(firda_data["decrypt_body"]):
                    value = value + "\n" + sen
            return_list.append(value)
            invoke_list.append("")

            url_list.append("")
            request_header_list.append("")
            requestBody_list.append(str(firda_data["decrypt_body"]))
            response_header_list.append("")
            responseBody_list.append("")
            note_list.append("decrypt body")

    ## case 3: app-measurement
    for piece in app_network_data:
        entry = json.loads(piece)
        if str(entry["request"]["url"]) == "https://app-measurement.com/a":
            bundle_id_list.append(bundle_id)
            className_list.append("")
            API_list.append("")
            return_list.append("")
            invoke_list.append("")

            url_list.append("https://app-measurement.com/a")
            request_header_list.append("")
            requestBody_list.append("")
            response_header_list.append("")
            responseBody_list.append("")
            note_list.append("app_measurement")

    ## case frida exception, but network contains sensi-info
    ## case 4.1: match precise location & coarse location:
    for sen in target_precise_location:
        for piece in app_network_data:
            entry = json.loads(piece)
            if sen in str(entry["request"]["postData"]):
                bundle_id_list.append(bundle_id)
                className_list.append("")
                API_list.append("")
                return_list.append(sen)
                invoke_list.append("")

                url_list.append(entry["request"]["url"])
                request_header_list.append(str(entry["request"]["headers"]))
                requestBody_list.append(str(entry["request"]["postData"]))
                try:
                    response_header_list.append(str(entry["response"]["headers"]))
                except:
                    response_header_list.append("")
                try:
                    responseBody_list.append(str(entry["response"]["content"]))
                except:
                    responseBody_list.append("")
                note_list.append("postData")



            elif sen in str(entry["request"]["url"]):
                #print(entry["request"]["url"])
                bundle_id_list.append(bundle_id)
                className_list.append("")
                API_list.append("")
                return_list.append(sen)
                invoke_list.append("")

                url_list.append(entry["request"]["url"])
                request_header_list.append(str(entry["request"]["headers"]))
                requestBody_list.append(str(entry["request"]["postData"]))
                try:
                    response_header_list.append(str(entry["response"]["headers"]))
                except:
                    response_header_list.append("")
                try:
                    responseBody_list.append(str(entry["response"]["content"]))
                except:
                    responseBody_list.append("")
                note_list.append("url")

            elif sen in str(entry["request"]["headers"]):
                #print(entry["request"]["headers"])
                bundle_id_list.append(bundle_id)
                className_list.append("")
                API_list.append("")
                return_list.append(sen)
                invoke_list.append("")

                url_list.append(entry["request"]["url"])
                request_header_list.append(str(entry["request"]["headers"]))
                requestBody_list.append(str(entry["request"]["postData"]))
                try:
                    response_header_list.append(str(entry["response"]["headers"]))
                except:
                    response_header_list.append("")
                try:
                    responseBody_list.append(str(entry["response"]["content"]))
                except:
                    responseBody_list.append("")
                note_list.append("header")

            ##didn't find precise, check if coarse exsit
            else:
                for sen1 in target_coarse_location:
                    if sen1 not in sen:
                        continue
                    if sen1 in str(entry["request"]["postData"]):
                        bundle_id_list.append(bundle_id)
                        className_list.append("")
                        API_list.append("")
                        return_list.append(sen1)
                        invoke_list.append("")

                        url_list.append(entry["request"]["url"])
                        request_header_list.append(str(entry["request"]["headers"]))
                        requestBody_list.append(str(entry["request"]["postData"]))
                        try:
                            response_header_list.append(str(entry["response"]["headers"]))
                        except:
                            response_header_list.append("")
                        try:
                            responseBody_list.append(str(entry["response"]["content"]))
                        except:
                            responseBody_list.append("")
                        note_list.append("postData")



                    elif sen1 in str(entry["request"]["url"]):
                        #print(entry["request"]["url"])
                        bundle_id_list.append(bundle_id)
                        className_list.append("")
                        API_list.append("")
                        return_list.append(sen1)
                        invoke_list.append("")

                        url_list.append(entry["request"]["url"])
                        request_header_list.append(str(entry["request"]["headers"]))
                        requestBody_list.append(str(entry["request"]["postData"]))
                        try:
                            response_header_list.append(str(entry["response"]["headers"]))
                        except:
                            response_header_list.append("")
                        try:
                            responseBody_list.append(str(entry["response"]["content"]))
                        except:
                            responseBody_list.append("")
                        note_list.append("url")

                    elif sen1 in str(entry["request"]["headers"]):
                        #print(entry["request"]["headers"])
                        bundle_id_list.append(bundle_id)
                        className_list.append("")
                        API_list.append("")
                        return_list.append(sen1)
                        invoke_list.append("")

                        url_list.append(entry["request"]["url"])
                        request_header_list.append(str(entry["request"]["headers"]))
                        requestBody_list.append(str(entry["request"]["postData"]))
                        try:
                            response_header_list.append(str(entry["response"]["headers"]))
                        except:
                            response_header_list.append("")
                        try:
                            responseBody_list.append(str(entry["response"]["content"]))
                        except:
                            responseBody_list.append("")
                        note_list.append("header")



    ## case 4.2: match other data:
    for sen in sen_list:
        for piece in app_network_data:
            entry = json.loads(piece)
            if sen in str(entry["request"]["postData"]):
                bundle_id_list.append(bundle_id)
                className_list.append("")
                API_list.append("")
                return_list.append(sen)
                invoke_list.append("")

                url_list.append(entry["request"]["url"])
                request_header_list.append(str(entry["request"]["headers"]))
                requestBody_list.append(str(entry["request"]["postData"]))
                try:
                    response_header_list.append(str(entry["response"]["headers"]))
                except:
                    response_header_list.append("")
                try:
                    responseBody_list.append(str(entry["response"]["content"]))
                except:
                    responseBody_list.append("")
                note_list.append("postData")



            elif sen in str(entry["request"]["url"]):
                #print(entry["request"]["url"])
                bundle_id_list.append(bundle_id)
                className_list.append("")
                API_list.append("")
                return_list.append(sen)
                invoke_list.append("")

                url_list.append(entry["request"]["url"])
                request_header_list.append(str(entry["request"]["headers"]))
                requestBody_list.append(str(entry["request"]["postData"]))
                try:
                    response_header_list.append(str(entry["response"]["headers"]))
                except:
                    response_header_list.append("")
                try:
                    responseBody_list.append(str(entry["response"]["content"]))
                except:
                    responseBody_list.append("")
                note_list.append("url")

            elif sen in str(entry["request"]["headers"]):
                #print(entry["request"]["headers"])
                bundle_id_list.append(bundle_id)
                className_list.append("")
                API_list.append("")
                return_list.append(sen)
                invoke_list.append("")

                url_list.append(entry["request"]["url"])
                request_header_list.append(str(entry["request"]["headers"]))
                requestBody_list.append(str(entry["request"]["postData"]))
                try:
                    response_header_list.append(str(entry["response"]["headers"]))
                except:
                    response_header_list.append("")
                try:
                    responseBody_list.append(str(entry["response"]["content"]))
                except:
                    responseBody_list.append("")
                note_list.append("header")


    ## case 5:time-zoom
    for sen in time_zoom:
        for piece in app_network_data:
            entry = json.loads(piece)
            if sen in str(entry["request"]["postData"]):
                bundle_id_list.append(bundle_id)
                className_list.append("")
                API_list.append("timezoom")
                return_list.append(sen)
                invoke_list.append("")

                url_list.append(entry["request"]["url"])
                request_header_list.append(str(entry["request"]["headers"]))
                requestBody_list.append(str(entry["request"]["postData"]))
                try:
                    response_header_list.append(str(entry["response"]["headers"]))
                except:
                    response_header_list.append("")
                try:
                    responseBody_list.append(str(entry["response"]["content"]))
                except:
                    responseBody_list.append("")
                note_list.append("postData")



            elif sen in str(entry["request"]["url"]):
                #print(entry["request"]["url"])
                bundle_id_list.append(bundle_id)
                className_list.append("")
                API_list.append("timezoom")
                return_list.append(sen)
                invoke_list.append("")

                url_list.append(entry["request"]["url"])
                request_header_list.append(str(entry["request"]["headers"]))
                requestBody_list.append(str(entry["request"]["postData"]))
                try:
                    response_header_list.append(str(entry["response"]["headers"]))
                except:
                    response_header_list.append("")
                try:
                    responseBody_list.append(str(entry["response"]["content"]))
                except:
                    responseBody_list.append("")
                note_list.append("url")

            elif sen in str(entry["request"]["headers"]):
                #print(entry["request"]["headers"])
                bundle_id_list.append(bundle_id)
                className_list.append("")
                API_list.append("timezoom")
                return_list.append(sen)
                invoke_list.append("")

                url_list.append(entry["request"]["url"])
                request_header_list.append(str(entry["request"]["headers"]))
                requestBody_list.append(str(entry["request"]["postData"]))
                try:
                    response_header_list.append(str(entry["response"]["headers"]))
                except:
                    response_header_list.append("")
                try:
                    responseBody_list.append(str(entry["response"]["content"]))
                except:
                    responseBody_list.append("")
                note_list.append("header")


    mapping = {}
    mapping["bundle_id_list"] = bundle_id_list
    mapping["className_list"] = className_list
    mapping["API_list"] = API_list
    mapping["return_list"] = return_list
    mapping["invoke_list"] = invoke_list

    mapping["url_list"] = url_list
    mapping["request_header_list"] = request_header_list
    mapping["requestBody_list"] = requestBody_list
    mapping["response_header_list"] = response_header_list
    mapping["responseBody_list"] = responseBody_list
    mapping["note_list"] = note_list
    mapping["matchRule"] = ["mappingByAPI"]*len(note_list)
    mapping["keyData"] = [""]*len(note_list)
    df = pd.DataFrame(mapping)

    directory = anlyze_output_path + "mapping_result/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    tofile = directory + bundle_id + ".pickle"
    tofile1=directory + bundle_id + ".xlsx"
    writeToMapping(df, tofile1)
    # Its important to use binary mode
    '''
    dbfile = open(tofile, 'ab')
    # source, destination
    pickle.dump(df, dbfile)
    dbfile.close()
    '''




def analyze_one_batch(root,folder,sen_list, target_precise_location, target_coarse_location,time_zoom):
    frida_output_path = root +"/result/"+ str(folder) + "/frida_output/"
    network_output_path = root+"/result/" + str(folder) + "/network_output/"
    anlyze_output_path =root +"/result/"+ str(folder) + "/analyze_output/"

    # 判断 anlyze output folder 是否存在
    if not os.path.exists(anlyze_output_path):
        os.makedirs(anlyze_output_path)

    frida_list = os.listdir(frida_output_path)
    for f in frida_list:
        if f == ".DS_Store":
            continue
        #if "cn.com.ethank.MobileHotelA" not  in f:
            #continue
        #print(f)
        #print("\n")
        #print(f)
        frida_file = frida_output_path + f
        if "_" in f:
            bundle_id = get_bundle_id(f)
        else:
            bundle_id = get_old_bundle_id(f)

        app_frida_data = parse_frida_output(frida_file, bundle_id, anlyze_output_path,sen_list)
        app_network_data = parse_network_output(bundle_id, network_output_path)
        if len(app_network_data) ==0:
            pass
            #print(f)
        match(bundle_id, app_frida_data, app_network_data, anlyze_output_path,sen_list, target_precise_location, target_coarse_location,time_zoom)
        # break



class senInfo:
  def __init__(self, sen_list):
    self.sen_list = sen_list
    self.precise_location_list = set()
    self.coarse_location_list = set()



def match_by_API(root, folder):
    sen_list, time_zoom,target_precise_location, target_coarse_location=getSensiveInfo(root)
    for num in tqdm(range(0,int(folder)+1)):
        path=root +"/result/"+ str(num)
        if not os.path.exists(path):
            continue
        analyze_one_batch(root,num,sen_list, target_precise_location, target_coarse_location,time_zoom)



if __name__ == '__main__':
    '''
    computer="xiaoyue"
    root = "/Volumes/Seagate/Privacy_Label/measurement_study/data/"+computer+"_unzip/"
    sen_list, time_zoom,target_precise_location, target_coarse_location=getSensiveInfo(root)
    for num in tqdm(range(0,84)):
        path=root + str(num)
        if not os.path.exists(path):
            continue
        analyze_one_batch(root,num,sen_list, target_precise_location, target_coarse_location,time_zoom)



    computer="luyixing"
    root = "/Volumes/Seagate/Privacy_Label/measurement_study/data/"+computer+"_unzip/"
    sen_list, time_zoom,target_precise_location, target_coarse_location=getSensiveInfo(root)
    for num in tqdm(range(0,52)):
        path=root + str(num)
        if not os.path.exists(path):
            continue
        analyze_one_batch(root,num,sen_list, target_precise_location, target_coarse_location,time_zoom)   

    
    computer="appMakerResult"
    root = "/Volumes/Seagate/Privacy_Label/measurement_study/data/"+computer+"/"
    sen_list, time_zoom,target_precise_location, target_coarse_location=getSensiveInfo(root)
    for num in tqdm(range(0,13)):
        path=root + str(num)
        if not os.path.exists(path):
            continue
        analyze_one_batch(root,num,sen_list, target_precise_location, target_coarse_location,time_zoom)
    '''

    '''
    computer="minPost"
    root = "/Volumes/Seagate/Privacy_Label/measurement_study/data/"+computer+"/"
    sen_list, time_zoom,target_precise_location, target_coarse_location=getSensiveInfo(root)
    for num in tqdm(range(0,11)):
        path=root + str(num)
        if not os.path.exists(path):
            continue
        analyze_one_batch(root,num,sen_list, target_precise_location, target_coarse_location,time_zoom)


    '''

    '''
    computer="zixiaoResult"
    root = "/Volumes/Seagate/Privacy_Label/measurement_study/data/"+computer+"/"
    sen_list, time_zoom,target_precise_location, target_coarse_location=getSensiveInfo(root)
    for num in tqdm(range(0,29)):
        path=root + str(num)
        if not os.path.exists(path):
            continue
        analyze_one_batch(root,num,sen_list, target_precise_location, target_coarse_location,time_zoom)
    
    '''
    computer="omitAppsResult"
    root = "/Volumes/Seagate/Privacy_Label/measurement_study/data/"+computer+"/"
    sen_list, time_zoom,target_precise_location, target_coarse_location=getSensiveInfo(root)
    for num in tqdm(range(15,22)):
        path=root + str(num)
        if not os.path.exists(path):
            continue
        analyze_one_batch(root,num,sen_list, target_precise_location, target_coarse_location,time_zoom)
