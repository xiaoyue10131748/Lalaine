import os
import sys
import time
import argparse
import json

def is_exist(ipa_path,bundleid):

    if not os.path.exists("./downloaded.txt"):
        with open("./downloaded.txt", 'a') as f:
            return False

    with open("./downloaded.txt", 'r') as f:
        bundleids = f.read().splitlines()
    for item in bundleids:
        b_id =item.strip()
        if b_id == bundleid.strip():
            print("exist!!!! skip the bundleid ....")
            return True
    return False



def download(ipa_path,error_log, target_bundleids):
    error_f = open(error_log, 'w')
    for item in target_bundleids:
        bundleid =item.strip()
        print("begin downloading " +str(bundleid) + "\n")


        if is_exist(ipa_path,bundleid):
            continue
        
        out_put=os.system('ipatool download --purchase -b '+bundleid)
       
        if out_put!=0:
            error_f.write(bundleid + '\n')
        else:
            f_haved_download=open("./downloaded.txt","a+")
            f_haved_download.write(item+"\n")
            f_haved_download.close()
        time.sleep(1)
        #break
    error_f.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, default="./app_info.json")
    parser.add_argument('--result_dir', type=str, default="./ipa/")
 
    options = parser.parse_args()
    input_file = options.input_file
    ipa_path = options.result_dir
    fp = open(input_file, 'r')
    data = json.load(fp)
    fp.close()

    ## take which part to download
    target_bundleids=[]
    for item in data:
        target_bundleids.append(item["bundleid"])


    if not os.path.exists(ipa_path):
        os.makedirs(ipa_path)
    os. chdir(ipa_path)
    error_log = './error.log'
    download(ipa_path,error_log,target_bundleids)


if __name__ == "__main__":
    main()