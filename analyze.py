import json
from haralyzer import HarParser, HarPage
import datetime
import os
import xlsxwriter
import pandas as pd
import sys


def get_bundle_id(ipa):
    cells = ipa.split("_")
    #appid = cells[-1]
    #bundle_id = ipa.split(appid)[0][:-1]
    bundle_id = cells[0]
    return bundle_id


def get_old_bundle_id(ipa):
    cells = ipa.split("-")
    appid = cells[-3]
    bundle_id = ipa.split(appid)[0][:-1]
    return bundle_id


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
                worksheet.write_string(
                    rowNum+headRows, colNum, xlColCont[rowNum])
            elif df.columns[colNum] == 'sensitve_content_list':
                try:
                    worksheet.write_rich_string(
                        rowNum+headRows, colNum, *xlColCont[rowNum])
                except:
                    print(*xlColCont[rowNum])

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


def parse_frida_output(frida_file, bundle_id, anlyze_output_path):
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
            MethodName = content[index+2].split("[*] Method Name: ")
            if len(MethodName) < 2:
                print("[!]MethodName is empty")
                print(frida_file, className, MethodName, index)
                sys.exit(1)

            MethodName = MethodName[1].strip()
            returnValue_list = []
            if index+6 < len(content) and "[-] Return Value: " in content[index+6]:
                curr_line = content[index +
                                    6].strip().split("[-] Return Value: ")
                if len(curr_line) > 1:
                    returnValue = curr_line[1].strip()
                else:
                    returnValue = ""
                returnValue_list.append(returnValue)
            else:
                returnValue = ""

            if className == "CLLocation" and returnValue.startswith("<+"):
                lng = '%.2f' % float(returnValue.split(">")[0].split(",")[1])
                lat = '%.2f' % float(returnValue.split(
                    ">")[0].split(",")[0].split("<+")[1])
                returnValue_list.append(lng)
                returnValue_list.append(lat)
                # print(returnValue)
                # print(lng)
                # print(lat)

            index = index+7
            backtrace = getBackTrace(index, content)
            sensitive_content = className + " " + MethodName + \
                "\n" + returnValue + "\n\n" + backtrace

            bundleID_list.append(bundle_id)
            sensitve_content_list.append(sensitive_content)

            is_exsit, app_frida_data = count_class_name_method_name(
                className, MethodName, app_frida_data)
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
    tofile = directory+bundle_id + ".xlsx"
    # df.to_excel(tofile)

    # print(len(bundleID_list))
    # print(len(sensitve_content_list))
    writeToExcel(df, tofile)
    for item in app_frida_data:
        print(item)
    return app_frida_data


def parse_network_output(bundle_id, network_output_path):
    file_path = network_output_path+bundle_id+".txt"

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
        print(xlColCont)
        worksheet.write_string(0, colNum, str(df.columns[colNum]), bold)
        for rowNum in range(len(xlColCont)):
            if df.columns[colNum] == 'bundleID_list':
                worksheet.write_string(
                    rowNum + headRows, colNum, xlColCont[rowNum])
            # elif df.columns[colNum] == 'requestBody_list' or  df.columns[colNum] == 'responseBody_lists':
                #worksheet.write_rich_string(rowNum + headRows, colNum, xlColCont[rowNum])
            else:
                worksheet.write_string(
                    rowNum + headRows, colNum, xlColCont[rowNum])
    workbook.close()


sen_list = ['"ip":', '"local_ip":', "149.160.134.156", "149.161.156.25", "149.160.164.92", "700 N Woodlawn Ave", "47408", "86E081D1-7B0E-482F-9FF6-0F5059F60B15", "5B30BC06-9017-4FA0-8A77-3FB3FFBE3D7D", "F270BCAF-13C0-4D1C-B91F-6F446E24A380",
            "0F41A05D-B6F8-49FD-AAFF-3D4711371B81", "0000000-0000-0000-0000-000000000000", "4CB50870-7A2F-43AE-96E9-390BBECCAFED", "39.17", "-86.52", "00000000-0000-0000-0000-000000000000", "4CB508707A2F43AE96E9390BBECCAFED", "A00D5174-762E-41C6-89E9-9CE7E8E35A14", "0000000-0000-0000-0000-000000000000", "20C0350E-CC32-46A7-9175-B42C84C1CFB6",
            "88C59EAC-BCD6-4D83-B5CB-4647EEF71605", "640AD989-A3E8-4D51-A413-407B4266DAD1",
            "39.17", "39.16", "39.15", "-86.52", "-86.51", "-86.50", "-86.49", "68.38.149.171", "00000000-0000-0000-0000-000000000000", "4CB508707A2F43AE96E9390BBECCAFED"]


def match(bundle_id, app_frida_data, app_network_data, anlyze_output_path):
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
        # case 1: extractly match
        if "ReturnValue" in firda_data.keys():
            returnValue_list = firda_data["ReturnValue"]

            for returnValue in returnValue_list:
                for piece in app_network_data:
                    entry = json.loads(piece)

                    if returnValue in str(entry["request"]["postData"]):
                        print(entry["request"]["postData"])
                        bundle_id_list.append(bundle_id)
                        className_list.append(firda_data["className"])
                        API_list.append(firda_data["MethodName"])
                        return_list.append(returnValue)
                        invoke_list.append(str(firda_data["count"]))

                        url_list.append(entry["request"]["url"])
                        request_header_list.append(
                            str(entry["request"]["headers"]))
                        requestBody_list.append(
                            str(entry["request"]["postData"]))
                        try:
                            response_header_list.append(
                                str(entry["response"]["headers"]))
                        except:
                            response_header_list.append("")
                        responseBody_list.append(
                            str(entry["response"]["content"]))
                        note_list.append("postData")

                    elif returnValue in str(entry["request"]["url"]):
                        print(entry["request"]["url"])
                        bundle_id_list.append(bundle_id)
                        className_list.append(firda_data["className"])
                        API_list.append(firda_data["MethodName"])
                        return_list.append(returnValue)
                        invoke_list.append(str(firda_data["count"]))

                        url_list.append(entry["request"]["url"])
                        request_header_list.append(
                            str(entry["request"]["headers"]))
                        requestBody_list.append(
                            str(entry["request"]["postData"]))
                        try:
                            response_header_list.append(
                                str(entry["response"]["headers"]))
                        except:
                            response_header_list.append("")
                        try:
                            responseBody_list.append(
                                str(entry["response"]["content"]))
                        except:
                            responseBody_list.append("")
                        note_list.append("url")

                    elif returnValue in str(entry["request"]["headers"]):
                        print(entry["request"]["headers"])
                        bundle_id_list.append(bundle_id)
                        className_list.append(firda_data["className"])
                        API_list.append(firda_data["MethodName"])
                        return_list.append(returnValue)
                        invoke_list.append(str(firda_data["count"]))

                        url_list.append(entry["request"]["url"])
                        request_header_list.append(
                            str(entry["request"]["headers"]))
                        requestBody_list.append(
                            str(entry["request"]["postData"]))
                        try:
                            response_header_list.append(
                                str(entry["response"]["headers"]))
                        except:
                            response_header_list.append("")
                        responseBody_list.append(
                            str(entry["response"]["content"]))
                        note_list.append("header")

        # case 2: match encrpyted body
        if "decrypt_body" in firda_data.keys():
            bundle_id_list.append(bundle_id)
            className_list.append("")
            API_list.append("")
            value = ""
            for sen in sen_list:
                if sen in str(firda_data["decrypt_body"]):
                    value = value+"\n"+sen
            return_list.append(value)
            invoke_list.append("")

            url_list.append("")
            request_header_list.append("")
            requestBody_list.append(str(firda_data["decrypt_body"]))
            response_header_list.append("")
            responseBody_list.append("")
            note_list.append("decrypt body")

    # case 3: app-measurement
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

    # case 4: frida exception, but network contains sensi-info
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
                    response_header_list.append(
                        str(entry["response"]["headers"]))
                except:
                    response_header_list.append("")
                responseBody_list.append(str(entry["response"]["content"]))
                note_list.append("postData")

            elif sen in str(entry["request"]["url"]):
                print(entry["request"]["url"])
                bundle_id_list.append(bundle_id)
                className_list.append("")
                API_list.append("")
                return_list.append(sen)
                invoke_list.append("")

                url_list.append(entry["request"]["url"])
                request_header_list.append(str(entry["request"]["headers"]))
                requestBody_list.append(str(entry["request"]["postData"]))
                try:
                    response_header_list.append(
                        str(entry["response"]["headers"]))
                except:
                    response_header_list.append("")
                responseBody_list.append(str(entry["response"]["content"]))
                note_list.append("url")

            elif sen in str(entry["request"]["headers"]):
                print(entry["request"]["headers"])
                bundle_id_list.append(bundle_id)
                className_list.append("")
                API_list.append("")
                return_list.append(sen)
                invoke_list.append("")

                url_list.append(entry["request"]["url"])
                request_header_list.append(str(entry["request"]["headers"]))
                requestBody_list.append(str(entry["request"]["postData"]))
                try:
                    response_header_list.append(
                        str(entry["response"]["headers"]))
                except:
                    response_header_list.append("")
                responseBody_list.append(str(entry["response"]["content"]))
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
    df = pd.DataFrame(mapping)

    directory = anlyze_output_path + "mapping_result/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    tofile = directory + bundle_id + ".xlsx"
    writeToMapping(df, tofile)


def analyze_one_batch(folder):
    frida_output_path = '/Users/xiaoyue-admin/Documents/privacy_label/code/batch_test/result/' + \
        str(folder)+"/frida_output/"
    network_output_path = '/Users/xiaoyue-admin/Documents/privacy_label/code/batch_test/result/' + \
        str(folder)+"/network_output/"
    anlyze_output_path = '/Users/xiaoyue-admin/Documents/privacy_label/code/batch_test/result/' + \
        str(folder)+"/analyze_output/"

    # 判断 anlyze output folder 是否存在
    if not os.path.exists(anlyze_output_path):
        os.makedirs(anlyze_output_path)

    frida_list = os.listdir(frida_output_path)
    for f in frida_list:
        if f == ".DS_Store":
            continue

        print(f)
        frida_file = frida_output_path+f
        bundle_id = get_bundle_id(f)
        #bundle_id = get_old_bundle_id(f)

        app_frida_data = parse_frida_output(
            frida_file, bundle_id, anlyze_output_path)
        app_network_data = parse_network_output(bundle_id, network_output_path)
        match(bundle_id, app_frida_data, app_network_data, anlyze_output_path)
        # break


if __name__ == '__main__':
    folder = sys.argv[1]
    analyze_one_batch(folder)
