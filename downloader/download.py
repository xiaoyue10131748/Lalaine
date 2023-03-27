import os
import sys
import time


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
        #out_put=os.system('ipatool download  -b '+bundleid +" -e jj7w3pod@icloud.com -p GuanJiale1997 " + "-o " + file_name)
        #out_put=os.system('ipatool download  -b '+bundleid  + " -o " + file_name)
        
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
    root="."
    folder="/ipa/"
    ipa_path=root+folder
    total_bundle_id='/bundleID.txt'

    with open(root+total_bundle_id, 'r') as f:
        bundleids = f.read().splitlines()

    ## take which part to download
    target_bundleids=bundleids

    if not os.path.exists(ipa_path):
        os.makedirs(ipa_path)
    os. chdir(ipa_path)
    error_log = './error.log'
    download(ipa_path,error_log,target_bundleids)


if __name__ == "__main__":
    main()