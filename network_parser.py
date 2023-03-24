import json
from haralyzer import HarParser, HarPage
import datetime 
import os,sys
import shutil

def write_json(row, file):
  fp = open(file, 'a')
  fp.write(json.dumps(row)+'\n')
  fp.flush()
  fp.close()


def parser(file):
    with open(file, 'r') as f:
        har_parser = HarParser(json.loads(f.read().encode().decode('utf-8-sig') ))
    data = har_parser.har_data
    entries=data["entries"]
    for entry in entries:
        if 'startedDateTime' in entry.keys():
            print(entry['startedDateTime'])


def read_file(file_path):
    f=open(file_path,"r")
    content=f.readlines()
    f.close()
    return content


def format_time(s_time):
    year, month, date = s_time.split(" ")[0].split("-")
    hour, minute, second =  s_time.split(" ")[1].split(":")
    d = datetime.datetime(int(year), int(month), int(date), int(hour), int(minute), int(second)) 
    return d


def format_network_time(s_time):
    start_time=s_time.split(".")[0]
    year, month, date = start_time.split("T")[0].split("-")
    hour, minute, second =  start_time.split("T")[1].split(":")
    d = datetime.datetime(int(year), int(month), int(date), int(hour), int(minute), int(second)) 
    return d



def get_network_traffic_duration(start_time,end_time,network_file,ipa_network_file):
    with open(network_file, 'r') as f:
        har_parser = HarParser(json.loads(f.read().encode().decode('utf-8-sig') ))
    data = har_parser.har_data
    entries=data["entries"]
    for entry in entries:
        if 'startedDateTime' in entry.keys():
            currentDateTime=format_network_time(entry['startedDateTime'])
            if start_time < currentDateTime < end_time:
                print(str(currentDateTime) + " :: " + entry["request"]["url"])
                write_json(entry, ipa_network_file)


def get_raw_har(network_path,har_path):
    if not os.path.exists(network_path):
        os.makedirs(network_path)

    for filename in os.listdir(har_path):
        f = os.path.join(har_path, filename)
        # checking if it is a file
        if os.path.isfile(f):
            print(f)
            dst = network_path + filename
            shutil.move(f, dst)



def parse_raw_network(root,folder,har_path):
    log_file = root+'/result/' + str(folder) + '/log.txt'
    network_path = root+'/result/' + str(folder) + "/har/"
    network_output_path = root+'/result/'+ str(folder) + "/network_output/"
    if not os.path.exists(network_path):
        get_raw_har(network_path, har_path)
    # 判断 network output folder 是否存在
    if not os.path.exists(network_output_path):
        os.makedirs(network_output_path)

    content = read_file(log_file)
    for line in content:
        data = json.loads(line)
        bundleID = data["bundleID"]
        ipa_network_file = network_output_path + bundleID + ".txt"
        start_time = format_time(data["start_time"])
        end_time = format_time(data["end_time"])
        f_list = os.listdir(network_path)
        for file in f_list:
            if file == ".DS_Store":
                continue
            network_file = network_path + file
            get_network_traffic_duration(start_time, end_time, network_file, ipa_network_file)
            print("========================\n\n")






if __name__ == '__main__':
    folder = 0
    root = "."
    har_path = "/Users/xiaoyue-admin/Documents/Fiddler2/Captures/har"
    parse_raw_network(root, folder, har_path)
