import json
from haralyzer import HarParser, HarPage
import datetime
import os
import xlsxwriter, pandas as pd
import sys
import pickle
from tqdm import tqdm
from utils import utils_traffic
from  collections import defaultdict

from utils.get_hunp_str import hump2underline
from utils.utils_traffic import ParsedURL, ParsedBody
import collections

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


def is_Device_ID(key):
    if "device_token" in key:
        return True
    if key in ["device_identifier","aaid","idfa","track_id","serial_number","device_fingerprint_id","tracker_token","device_id","hwid","advertiser_id","unique_device_no"] :
        return True
    return False

def is_User_ID(key):
    if key in ["userid","user_id","uid","account_id","google_aid","windows_aid","appsflyer_id","adjust_id","uuid","username","user_name","customer_id","cid","user_ident","anon_id"]:
        return True
    return False

def is_Name(key):
    if key in ["first name","last name","middle_name","lastname","sns_nickname","firstname","nick_name","username","user_name","user_names","name_or_email_for_user","nickname","avatar","full_name","first_name","last_name","mid_name","family_name","middle_name"]:
        return True
    return False

def is_email_address(key):
    if "email_address" in key or "email address" in key:
        return True
    if key in ["user_emails","user_email","name_or_email_for_user","collect_email","idv_preregistered_email","hashed_email","login_email_suffix","mobile number or email","user[email]","email","emailid","emails","email_token","email_name","account_requires_email","login_auth_email","user_send_email","delivery_details_email","customer_email"]:
        return True
    return False

def is_phone_numer(key):
    if "phone_number" in key:
        return True
    if key in ["telephone_mobile","mobile number or email"]:
        return True
    return False

def is_health(key):
    if key in ["heartbeat","heartbeat_interval_in_sec","controller_heartbeat_timeout","controller_heartbeat_interval","heartbeat_time","current_health","last_update_health_value","individuals[0][birthDay]","birthday","yearofbirth_time","birthdate","heart_rate","heart_beat_frequency_ms", "blood_type", "body_weight", "body_height", "blood_pressure", "date_of_birth", "biological_sex", "skin_type", "wheelchair_usage"]:
        return True
    return False

def is_Physical_Address(key):
    if key in ["delivery address","street_name_house_number","home_address", "mailing_address", "postal_address","delivery_address"]:
        return True
    return False

def is_ad(key):
    #fbs_aeid
    if key in ["fbs_aeid","ad_id","ad_load_duration","ad_unit_id","ad_format","ad_info","ad_size","ad_refresh_ms","ad_type","third_party_ad_placement_id","ad_values","ad_expiration_ms","supported_ad_formats"]:
        return True
    return False

def is_Product_Interaction(key):
    if key in ["click_area","time_show", "video.mute", "click_sensor_events", "mousemove","click_event","launch_time"]:
        return True
    return False

def is_Performance_Data(key):
    if "battery" in key:
        return True
    if key in ["total_storage", "battery_state", "battery_level", "storage_bytes_available", "device_battery_percent", "battery_saver_enabled", "battery_info"]:
        return True
    return False

def is_Other_Diagnostic_Data(key):
    if key in ["os_version","screen_size","screen_height","screen_width","device_type","device_brand","operating_system","operating_system_version"]:
        return True
    return False

def is_Crash_Data(key):
    if key in ["crashlog","crash_report","crash_recording","report_all_events_on_crash","crash_data","enable_crash_reporting","report_interval_ms","cache_bust","log_level","device_meta","logstring"]:
        return True
    return False

def is_Contacts(key):
    if "address book" in key:
        return True
    if key in ["user_messenger_contact","upload_contacts","number_of_contacts","contact_email","contact-preferences-partner-email","contact-preferences-promos-email","name_prefix","email_addresses","social_profiles","phonetic_given_name","phone_number","email_address"]:
        return True
    return False


def is_Sensitive_Info(key):
    if key in ["face_id","baby_name","baby_birthday","baby_gender","birth_year","individuals[0][birthDay]","yearofbirth_time","yearofbirth","lp_yearofbirth","date_of_birth","birthdate","account_number","credentials_type","gender","birthday","birth_day","regtype","password","ssn","social_security_number","driver_license"]:
        return True
    return False


def is_coarse_Location(key):
    if key in ["ipv6_list","ipv4_list","ipv6","ipv4","ip","zip_code","latitude","longitude","altitude","ip_address","lat","lng","city","neighborhood","admin_district_code","postal_code","post_code","ipaddress","geo_location","place_id","city_code","geo_lat","geo_lng","location_code","local_ip","dtm_user_ip","long"]:
        return True
    return False



def check_key(key):
    Label_list=[]
    if is_Device_ID(key):
        Label_list.append("Device ID")
    if is_User_ID(key):
        Label_list.append("User ID")
    if is_Name(key):
        Label_list.append("Name")
    if is_email_address(key):
        Label_list.append("Email Address")
    if is_phone_numer(key):
        Label_list.append("Phone Number")
    if is_health(key):
        Label_list.append("Health")
    if is_Physical_Address(key):
        Label_list.append("Physical Address")
    if is_ad(key):
        Label_list.append("Advertising Data")
    if is_Product_Interaction(key):
        Label_list.append("Product Interaction")
    if is_Performance_Data(key):
        Label_list.append("Performance Data")
    if is_Other_Diagnostic_Data(key):
        Label_list.append("Other Diagnostic Data")
        Label_list.append("Other Data Types")
    if is_Crash_Data(key):
        Label_list.append("Crash Data")
    if is_Contacts(key):
        Label_list.append("Contacts")
    if is_Sensitive_Info(key):
        Label_list.append("Sensitive Info")
    if is_coarse_Location(key):
        Label_list.append("Coarse Location")
        ##add preciselocaion
        Label_list.append("Precise Location")
    return Label_list



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



def match(bundle_id, app_network_data, anlyze_output_path):
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
    matchRule=[]
    keyData=[]


    for piece in app_network_data:
        entry = json.loads(piece)
        ## ignore 443 traffic and traffic send to apple
        if "url" in entry["request"].keys() and (":443" in entry["request"]["url"] or "apple.com" in entry["request"]["url"]):
            continue
        raw_url=entry["request"]["url"]  if "url" in entry["request"].keys() else ""
        raw_body=entry["request"]["postData"]["text"] if ("postData" in entry["request"].keys() and "text" in entry["request"]["postData"].keys()) else ""
        raw_header=entry["request"]["headers"] if "headers" in entry["request"].keys() else ""

        raw_response_body=entry["response"]["content"] if "content" in entry["response"].keys() else ""
        raw_response_header = entry["response"]["headers"] if "headers" in entry["response"].keys() else ""
        try:
            p = ParsedURL(raw_url)
        except:
            continue
        for url_key in p.args.keys():
            clean_url_key=hump2underline(url_key)
            url_label_list=check_key(clean_url_key)
            if len(url_label_list) ==0:
                continue
            bundle_id_list.append(bundle_id)
            className_list.append("")
            API_list.append("")
            return_list.append(url_key)
            invoke_list.append("")
            url_list.append(raw_url)
            request_header_list.append(str(raw_header))
            requestBody_list.append(str(entry["request"]["postData"]))
            response_header_list.append(str(raw_response_header))
            responseBody_list.append(str(raw_response_body))
            note_list.append("url")
            matchRule.append("mappingByKey")
            keyData.append(str(url_label_list))

        p = ParsedBody(raw_body)
        for body_key in p.get_keys():
            clean_body_key=hump2underline(body_key)
            body_label_list=check_key(clean_body_key)
            if len(body_label_list) ==0:
                continue
            bundle_id_list.append(bundle_id)
            className_list.append("")
            API_list.append("")
            return_list.append(body_key)
            invoke_list.append("")
            url_list.append(raw_url)
            request_header_list.append(str(raw_header))
            requestBody_list.append(str(entry["request"]["postData"]))
            response_header_list.append(str(raw_response_header))
            responseBody_list.append(str(raw_response_body))
            note_list.append("postData")
            matchRule.append("mappingByKey")
            keyData.append(str(body_label_list))

    mapping = {}
    mapping["bundle_id_list"] = bundle_id_list
    mapping["className_list"] = className_list
    mapping["API_list"] = API_list
    mapping["return_list"] = return_list

    ###caculate the frequency based on how many times the data is being send out
    fre_list=[]
    frequency = collections.Counter(return_list)
    for key in return_list:
        fre_list.append(str(frequency[key]))
    mapping["invoke_list"] = fre_list

    mapping["url_list"] = url_list
    mapping["request_header_list"] = request_header_list
    mapping["requestBody_list"] = requestBody_list
    mapping["response_header_list"] = response_header_list
    mapping["responseBody_list"] = responseBody_list
    mapping["note_list"] = note_list
    ##add two new columns
    mapping["matchRule"] = matchRule
    mapping["keyData"] = keyData

    df = pd.DataFrame(mapping)


    directory = anlyze_output_path + "key_mapping_result/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    tofile1=directory + bundle_id + ".xlsx"
    writeToMapping(df, tofile1)



def parse_network_output(bundle_id, network_output_path):
    file_path = network_output_path + bundle_id + ".txt"

    ## not exist
    if not os.path.exists(file_path):
        return []
    f = open(file_path, "r")
    entries = f.readlines()
    f.close()
    return entries


def analyze_one_batch(root,folder):
    frida_output_path = root +"/result/"+ str(folder) + "/frida_output/"
    network_output_path = root +"/result/" + str(folder) + "/network_output/"
    anlyze_output_path =root +"/result/" + str(folder) + "/analyze_output/"

    # 判断 anlyze output folder 是否存在
    if not os.path.exists(anlyze_output_path):
        os.makedirs(anlyze_output_path)

    frida_list = os.listdir(frida_output_path)
    for f in frida_list:
        if f == ".DS_Store":
            continue
        #if "in.goindigo.IndiGo" not  in f:
            #continue
        #print(f)
        #print("\n")
        #print(f)
        frida_file = frida_output_path + f
        if "_" in f:
            bundle_id = get_bundle_id(f)
        else:
            bundle_id = get_old_bundle_id(f)

        app_network_data = parse_network_output(bundle_id, network_output_path)
        if len(app_network_data) ==0:
            pass
            #print(f)
        match(bundle_id, app_network_data, anlyze_output_path)
        # break

def match_by_KEY(root, folder):
    for num in tqdm(range(int(folder),int(folder)+1)):
        path=root +"/result/"+ str(num)
        if not os.path.exists(path):
            continue
        analyze_one_batch(root,num)


def main():
    '''
    computer="xiaoyue"
    root = "/Volumes/Seagate/Privacy_Label/measurement_study/data/"+computer+"_unzip/"
    for num in tqdm(range(0,84)):
        path=root + str(num)
        if not os.path.exists(path):
            continue
        analyze_one_batch(root,num)



    computer="luyixing"
    root = "/Volumes/Seagate/Privacy_Label/measurement_study/data/"+computer+"_unzip/"
    for num in tqdm(range(0,52)):
        path=root + str(num)
        if not os.path.exists(path):
            continue
        analyze_one_batch(root,num)


    computer="appMakerResult"
    root = "/Volumes/Seagate/Privacy_Label/measurement_study/data/"+computer+"/"
    for num in tqdm(range(0,13)):
        path=root + str(num)
        if not os.path.exists(path):
            continue
        analyze_one_batch(root,num)


    computer="minPost"
    root = "/Volumes/Seagate/Privacy_Label/measurement_study/data/"+computer+"/"
    for num in tqdm(range(0,11)):
        path=root + str(num)
        if not os.path.exists(path):
            continue
        analyze_one_batch(root,num)



    computer="JialePost"
    root = "/Volumes/Seagate/Privacy_Label/measurement_study/data/"+computer+"/"
    for num in tqdm(range(50,110)):
        path=root + str(num)
        if not os.path.exists(path):
            continue
        analyze_one_batch(root,num)
    '''

    '''
    computer="zixiaoResult"
    root = "/Volumes/Seagate/Privacy_Label/measurement_study/data/"+computer+"/"
    for num in tqdm(range(0,30)):
        path=root + str(num)
        if not os.path.exists(path):
            continue
        analyze_one_batch(root,num)
    '''

    computer="omitAppsResult"
    root = "/Volumes/Seagate/Privacy_Label/measurement_study/data/"+computer+"/"
    for num in tqdm(range(15,22)):
        path=root + str(num)
        if not os.path.exists(path):
            continue
        analyze_one_batch(root,num)



if __name__ == '__main__':
    main()